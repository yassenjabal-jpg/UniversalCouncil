using System.IO;
using System.Diagnostics;
using System.Security.Cryptography;
using System.Text.Json;
using System.Windows;
using System.Windows.Interop;
using System.Windows.Threading;
using UniversalCouncil.CommandCenter;

namespace UniversalCouncil.CommandCenter.UiSmoke;

internal static partial class Program
{
    private sealed record WgcMotionFrameSample(
        int Frame,
        string File,
        string Sha256,
        long SourceFrameSequence,
        bool SourceFresh,
        double MeanSampleDelta,
        double ChangedSampleRatio,
        bool VisiblyChanged);

    private static int RenderWgcMotionEvidence(string output, bool reducedMotion)
    {
        var mode = reducedMotion ? "reduced" : "full";
        var candidateSha =
            Environment.GetEnvironmentVariable("CANDIDATE_SHA")?.Trim().ToLowerInvariant()
            ?? "unknown";

        Environment.SetEnvironmentVariable(
            "UNIVERSALCOUNCIL_MOTION_EVIDENCE",
            reducedMotion ? "reduced" : "full");

        Directory.CreateDirectory(output);
        var framesDirectory = Path.Combine(output, "frames");
        Directory.CreateDirectory(framesDirectory);

        MainWindow? window = null;
        try
        {
            window = App.CreateMainWindow(AppContext.BaseDirectory);
            SynchronizationContext.SetSynchronizationContext(
                new DispatcherSynchronizationContext(window.Dispatcher));
            ConfigureMotionEvidenceWindow(window);

            window.WindowStyle = WindowStyle.None;
            window.ResizeMode = ResizeMode.NoResize;
            window.ShowInTaskbar = true;
            window.WindowStartupLocation = WindowStartupLocation.Manual;
            window.Left = 0;
            window.Top = 0;
            window.Width = MotionWidth;
            window.Height = MotionHeight;
            window.Show();
            PumpDispatcher(TimeSpan.FromMilliseconds(250));

            var hwnd = new WindowInteropHelper(window).Handle;
            if (hwnd == IntPtr.Zero)
            {
                throw new InvalidOperationException(
                    "WGC motion evidence could not obtain the real Command Center HWND.");
            }

            using IMotionEvidenceCaptureSource captureSource =
                new PersistentWgcWindowCaptureSource(hwnd);

            if (!captureSource.WaitForFirstFrame(TimeSpan.FromSeconds(5)))
            {
                throw new InvalidOperationException(
                    "Persistent WGC motion evidence received no first frame within five seconds.");
            }

            var geometryReport = new
            {
                schema_version = "1.0",
                candidate_sha = candidateSha,
                source = captureSource.SourceId,
                hwnd = $"0x{hwnd.ToInt64():X}",
                target_width = MotionWidth,
                target_height = MotionHeight,
                source_width = captureSource.Width,
                source_height = captureSource.Height,
                exact_geometry =
                    captureSource.Width == MotionWidth &&
                    captureSource.Height == MotionHeight,
                first_frame_latency_ms =
                    Math.Round(captureSource.FirstFrameLatencyMs, 3),
                fallback_used = false,
                silent_dxgi_fallback = false,
            };

            File.WriteAllText(
                Path.Combine(output, "wgc-host-geometry.json"),
                JsonSerializer.Serialize(
                    geometryReport,
                    new JsonSerializerOptions { WriteIndented = true }));

            if (!geometryReport.exact_geometry)
            {
                Console.Error.WriteLine(
                    $"WGC host geometry mismatch: {captureSource.Width}x{captureSource.Height} " +
                    $"!= {MotionWidth}x{MotionHeight}.");
                return 2;
            }

            var seconds = reducedMotion ? 28 : 38;
            var frameCount = seconds * MotionFramesPerSecond;
            var steps = BuildMotionSteps(reducedMotion);
            var stepsByFrame = steps
                .GroupBy(step => step.Frame)
                .ToDictionary(group => group.Key, group => group.ToArray());

            var samples = new List<WgcMotionFrameSample>(frameCount);
            byte[]? previousPixels = null;
            long? previousSourceSequence = null;
            var changedFrameCount = 0;
            var currentChangedRun = 0;
            var longestChangedRun = 0;
            var motionRunCount = 0;
            var wasChanged = false;
            var freshSourceSampleCount = 0;
            var staleSourceSampleCount = 0;
            var totalCaptureLatenessMs = 0d;
            var maxCaptureLatenessMs = 0d;
            var lateFrameCount = 0;

            using var frameEncoder =
                new BackgroundPngFrameEncoder(framesDirectory, frameCount);
            var captureClock = Stopwatch.StartNew();

            for (var frameIndex = 0; frameIndex < frameCount; frameIndex++)
            {
                if (stepsByFrame.TryGetValue(frameIndex, out var frameSteps))
                {
                    foreach (var step in frameSteps)
                    {
                        step.Execute(window);
                        Console.WriteLine(
                            $"WGC motion evidence [{mode}] step @{frameIndex}: {step.Name}");
                    }
                }

                var targetCaptureTime = TimeSpan.FromSeconds(
                    (frameIndex + 1d) / MotionFramesPerSecond);
                PaceDispatcherToCaptureTime(captureClock, targetCaptureTime);

                var captureTime = captureClock.Elapsed;
                var latenessMs = Math.Max(
                    0,
                    (captureTime - targetCaptureTime).TotalMilliseconds);
                totalCaptureLatenessMs += latenessMs;
                maxCaptureLatenessMs = Math.Max(maxCaptureLatenessMs, latenessMs);
                if (latenessMs > (1000d / MotionFramesPerSecond))
                {
                    lateFrameCount++;
                }

                var capture = captureSource.CaptureFrame();
                frameEncoder.Queue(capture.Pixels);

                var sourceFresh =
                    previousSourceSequence is null ||
                    capture.SourceFrameSequence != previousSourceSequence.Value;
                if (sourceFresh)
                {
                    freshSourceSampleCount++;
                }
                else
                {
                    staleSourceSampleCount++;
                }

                var (meanDelta, changedRatio) = previousPixels is null
                    ? (0d, 0d)
                    : ComputeFrameDelta(previousPixels, capture.Pixels);
                var visiblyChanged =
                    meanDelta >= 0.20 || changedRatio >= 0.004;

                if (visiblyChanged)
                {
                    changedFrameCount++;
                    currentChangedRun++;
                    longestChangedRun =
                        Math.Max(longestChangedRun, currentChangedRun);
                    if (!wasChanged)
                    {
                        motionRunCount++;
                    }
                }
                else
                {
                    currentChangedRun = 0;
                }

                wasChanged = visiblyChanged;
                samples.Add(new WgcMotionFrameSample(
                    frameIndex,
                    $"frame-{frameIndex:D4}.png",
                    "",
                    capture.SourceFrameSequence,
                    sourceFresh,
                    Math.Round(meanDelta, 4),
                    Math.Round(changedRatio, 6),
                    visiblyChanged));

                previousPixels = capture.Pixels;
                previousSourceSequence = capture.SourceFrameSequence;
            }

            captureClock.Stop();
            var actualCaptureDurationSeconds = captureClock.Elapsed.TotalSeconds;
            var sourceFramesArrived = captureSource.FramesArrived;
            var sourceFrameErrors = captureSource.FrameErrors;
            var firstFrameLatencyMs = captureSource.FirstFrameLatencyMs;
            frameEncoder.CompleteAndVerify();

            var frameEvidence = samples
                .Select(sample =>
                {
                    var path = Path.Combine(framesDirectory, sample.File);
                    return sample with { Sha256 = HashMotionFrame(path) };
                })
                .ToList();

            var manifest = new
            {
                schema_version = "1.1",
                evidence_type = "WPF_P1_CRITICAL_PATH_MOTION",
                candidate_sha = candidateSha,
                source_surface = "ACTUAL_WPF",
                unedited = true,
                optical_flow = false,
                frame_interpolation = false,
                post_produced_animation = false,
                raw_frames_included = true,
                semantic_event_timestamps = true,
                mode,
                reduced_motion = reducedMotion,
                runtime_authority = false,
                stage8_opened = false,
                input_mode =
                    "PROGRAMMATIC_UI_AUTOMATION_AGAINST_REAL_WPF_CONTROLS",
                width = MotionWidth,
                height = MotionHeight,
                frame_rate = MotionFramesPerSecond,
                frame_count = frameCount,
                encoded_duration_seconds =
                    (double)frameCount / MotionFramesPerSecond,
                capture_timing = new
                {
                    clock = "STOPWATCH_REALTIME_WPF",
                    pipeline =
                        "PERSISTENT_WINDOWS_GRAPHICS_CAPTURE_HWND_BGRA_TO_BACKGROUND_FFMPEG_PNG",
                    capture_source = captureSource.SourceId,
                    capture_surface = "ACTUAL_COMMAND_CENTER_HWND",
                    fallback_used = false,
                    silent_dxgi_fallback = false,
                    source_width = captureSource.Width,
                    source_height = captureSource.Height,
                    source_frames_arrived = sourceFramesArrived,
                    source_frame_errors = sourceFrameErrors,
                    first_frame_latency_ms =
                        Math.Round(firstFrameLatencyMs, 3),
                    unique_sampled_source_frames =
                        frameEvidence.Select(item => item.SourceFrameSequence).Distinct().Count(),
                    fresh_source_sample_count = freshSourceSampleCount,
                    stale_source_sample_count = staleSourceSampleCount,
                    target_capture_duration_seconds =
                        (double)frameCount / MotionFramesPerSecond,
                    actual_capture_duration_seconds =
                        Math.Round(actualCaptureDurationSeconds, 3),
                    max_capture_lateness_ms =
                        Math.Round(maxCaptureLatenessMs, 3),
                    mean_capture_lateness_ms =
                        Math.Round(
                            totalCaptureLatenessMs / Math.Max(1, frameCount),
                            3),
                    late_frame_count_over_one_frame = lateFrameCount,
                    background_encoder = "FFMPEG_LOSSLESS_PNG",
                    encoder_queue_capacity_frames =
                        BackgroundPngFrameEncoder.QueueCapacityFrames,
                    png_encoding_on_wpf_capture_thread = false,
                    synchronous_layout_per_frame = false,
                    png_compression_level = 1,
                },
                motion_visibility = new
                {
                    changed_frame_count = changedFrameCount,
                    changed_frame_ratio =
                        Math.Round(
                            (double)changedFrameCount /
                            Math.Max(1, frameCount - 1),
                            4),
                    longest_changed_run = longestChangedRun,
                    motion_run_count = motionRunCount,
                    frame_change_rule =
                        "mean_sample_delta>=0.20 OR changed_sample_ratio>=0.004",
                },
                expected_video_file = reducedMotion
                    ? "p1-critical-path-reduced-motion.mp4"
                    : "p1-critical-path-motion.mp4",
                steps = steps.Select((step, index) => new
                {
                    evidence_step_id = $"step-{index + 1:D2}",
                    frame = step.Frame,
                    second =
                        (double)step.Frame / MotionFramesPerSecond,
                    occurred_at_seconds =
                        (double)step.Frame / MotionFramesPerSecond,
                    event_type = EvidenceEventType(step.Name),
                    semantic_object = EvidenceSemanticObject(step.Name),
                    step.Name,
                }),
                frames = frameEvidence,
            };

            File.WriteAllText(
                Path.Combine(output, "motion-evidence-manifest.json"),
                JsonSerializer.Serialize(
                    manifest,
                    new JsonSerializerOptions { WriteIndented = true }));

            Console.WriteLine(
                $"Command Center P1 {mode} WGC motion evidence frames: PASS " +
                $"({frameCount} frames, {seconds}s, visible={changedFrameCount}, " +
                $"longest-run={longestChangedRun}, runs={motionRunCount}, " +
                $"source-fresh={freshSourceSampleCount})");
            return 0;
        }
        finally
        {
            if (window is not null)
            {
                try
                {
                    window.Close();
                }
                catch
                {
                }
            }
        }
    }
}
