using System.Diagnostics;
using System.IO;
using System.Security.Cryptography;
using System.Text.Json;
using System.Windows;
using System.Windows.Interop;
using UniversalCouncil.CommandCenter;

namespace UniversalCouncil.CommandCenter.UiSmoke;

internal static partial class Program
{
    private const int WgcPilotSampleFrames = 60;

    private static int RunWindowsGraphicsCapturePilot(string output)
    {
        Directory.CreateDirectory(output);
        var candidateSha = Environment.GetEnvironmentVariable("CANDIDATE_SHA")?.Trim().ToLowerInvariant() ?? "unknown";
        var reportPath = Path.Combine(output, "wgc-pilot-report.json");
        var sampleCopyDurations = new List<double>();
        var sampleFrameSequences = new List<long>();
        var frameHashes = new List<string>();
        var capturedWidths = new List<int>();
        var capturedHeights = new List<int>();
        var errors = new List<string>();
        var sourceId = "RAW_WGC_PERSISTENT/WKI_CLIPPER_PATTERN";
        var firstFrameLatencyMs = 0d;
        var sourceFramesArrived = 0L;
        var sourceFrameErrors = 0L;
        var sampleClockSeconds = 0d;

        MainWindow? window = null;
        try
        {
            Environment.SetEnvironmentVariable("UNIVERSALCOUNCIL_MOTION_EVIDENCE", "full");
            window = App.CreateMainWindow(AppContext.BaseDirectory);
            ConfigureMotionEvidenceWindow(window);
            window.WindowStyle = WindowStyle.None;
            window.ResizeMode = ResizeMode.NoResize;
            window.ShowInTaskbar = false;
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
                throw new InvalidOperationException("Persistent WGC pilot could not obtain the real Command Center HWND.");
            }

            using IMotionEvidenceCaptureSource source =
                new PersistentWgcWindowCaptureSource(hwnd);
            sourceId = source.SourceId;

            if (!source.WaitForFirstFrame(TimeSpan.FromSeconds(5)))
            {
                throw new InvalidOperationException(
                    "Persistent WGC session delivered no frame within 5 seconds.");
            }

            firstFrameLatencyMs = source.FirstFrameLatencyMs;
            var sampleClock = Stopwatch.StartNew();

            for (var index = 0; index < WgcPilotSampleFrames; index++)
            {
                if (index == 20)
                {
                    NavigateForEvidence(window, "ProjectWorkspace");
                }
                else if (index == 40)
                {
                    NavigateForEvidence(window, "DecisionMode");
                }

                var targetSampleTime = TimeSpan.FromSeconds(
                    (index + 1d) / MotionFramesPerSecond);
                PaceDispatcherToCaptureTime(sampleClock, targetSampleTime);

                var copyClock = Stopwatch.StartNew();
                var frame = source.CaptureFrame();
                copyClock.Stop();

                sampleCopyDurations.Add(copyClock.Elapsed.TotalMilliseconds);
                sampleFrameSequences.Add(frame.SourceFrameSequence);
                capturedWidths.Add(frame.Width);
                capturedHeights.Add(frame.Height);
                frameHashes.Add(
                    Convert.ToHexString(SHA256.HashData(frame.Pixels))
                        .ToLowerInvariant());
            }

            sampleClock.Stop();
            sampleClockSeconds = sampleClock.Elapsed.TotalSeconds;
            sourceFramesArrived = source.FramesArrived;
            sourceFrameErrors = source.FrameErrors;
        }
        catch (Exception ex)
        {
            errors.Add($"{ex.GetType().Name}: {ex.Message}");
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

        var successfulSamples = frameHashes.Count;
        var distinctSourceSequences = sampleFrameSequences.Distinct().Count();
        var distinctPixelHashes = frameHashes.Distinct(StringComparer.Ordinal).Count();
        var freshSourceSamples = 0;
        long? previousSequence = null;
        foreach (var sequence in sampleFrameSequences)
        {
            if (previousSequence is null || sequence != previousSequence.Value)
            {
                freshSourceSamples++;
            }

            previousSequence = sequence;
        }

        var elapsedSeconds = Math.Max(sampleClockSeconds, 0.000001);
        var achievedSampleFps = successfulSamples / elapsedSeconds;
        var sourceArrivalFps = sourceFramesArrived / elapsedSeconds;
        var dimensionsExact = successfulSamples == WgcPilotSampleFrames &&
            capturedWidths.All(width => width == MotionWidth) &&
            capturedHeights.All(height => height == MotionHeight);
        var timingExact =
            Math.Abs(elapsedSeconds - (WgcPilotSampleFrames / (double)MotionFramesPerSecond)) <= 0.25;
        var freshRatio = successfulSamples == 0
            ? 0
            : (double)freshSourceSamples / successfulSamples;
        var sustainedThirtyFps =
            successfulSamples == WgcPilotSampleFrames &&
            achievedSampleFps >= 29.0 &&
            sourceArrivalFps >= 29.0 &&
            freshRatio >= 0.90 &&
            timingExact;

        static double Percentile95(IReadOnlyList<double> values)
        {
            if (values.Count == 0)
            {
                return 0;
            }

            var ordered = values.OrderBy(value => value).ToArray();
            var index = Math.Min(
                ordered.Length - 1,
                (int)Math.Ceiling(ordered.Length * 0.95) - 1);
            return ordered[Math.Max(0, index)];
        }

        var payload = new
        {
            schema_version = "1.1",
            pilot_id = "CC-MOTION-W1-1-PERSISTENT-WGC-PILOT-2026-10-22",
            candidate_sha = candidateSha,
            scope = "EVIDENCE_CAPTURE_ONLY",
            source = sourceId,
            capture_strategy = "PERSISTENT_WGC_ONLY",
            silent_dxgi_fallback = false,
            fallback_used = false,
            architecture_reference = new
            {
                repository = "WKImods/WKI-Clipper",
                upstream_commit = "1b6aff3e9700b5868d252a3f1108b39c5ae773d9",
                pattern = "persistent WgcWindowCapture + latest-frame buffer + D3D11 staging readback",
                license = "MIT",
            },
            dependency = new
            {
                package = "Vortice.Direct3D11",
                version = "3.8.3",
                adoption = "PILOT_ONLY",
            },
            target = new
            {
                width = MotionWidth,
                height = MotionHeight,
                fps = MotionFramesPerSecond,
                sample_frames = WgcPilotSampleFrames,
                target_seconds = WgcPilotSampleFrames / (double)MotionFramesPerSecond,
            },
            result = new
            {
                successful_samples = successfulSamples,
                distinct_source_sequences = distinctSourceSequences,
                distinct_pixel_hashes = distinctPixelHashes,
                fresh_source_samples = freshSourceSamples,
                fresh_source_sample_ratio = Math.Round(freshRatio, 4),
                source_frames_arrived = sourceFramesArrived,
                source_frame_errors = sourceFrameErrors,
                first_frame_latency_ms = Math.Round(firstFrameLatencyMs, 3),
                sample_elapsed_seconds = Math.Round(sampleClockSeconds, 3),
                achieved_sample_fps = Math.Round(achievedSampleFps, 3),
                source_arrival_fps = Math.Round(sourceArrivalFps, 3),
                mean_sample_copy_ms = sampleCopyDurations.Count == 0 ? 0 : Math.Round(sampleCopyDurations.Average(), 3),
                p95_sample_copy_ms = Math.Round(Percentile95(sampleCopyDurations), 3),
                max_sample_copy_ms = sampleCopyDurations.Count == 0 ? 0 : Math.Round(sampleCopyDurations.Max(), 3),
                dimensions_exact_1440x900 = dimensionsExact,
                timing_within_pilot_tolerance = timingExact,
                sustained_30fps = sustainedThirtyFps,
                errors,
            },
            decision = sustainedThirtyFps && dimensionsExact && errors.Count == 0 && sourceFrameErrors == 0
                ? "PASS_PERSISTENT_WGC_CANDIDATE"
                : "FAIL_PERSISTENT_WGC_ON_CURRENT_CI_HOST",
            protected_truth = new
            {
                authoritative_stage = "STAGE_7",
                stage8_opened = false,
                runtime_authority = false,
                live_execution = false,
                motion_dna_changed = false,
                thresholds_changed = false,
                w1_2_started = false,
                merge_authorized = false,
            },
        };

        File.WriteAllText(
            reportPath,
            JsonSerializer.Serialize(
                payload,
                new JsonSerializerOptions { WriteIndented = true }));

        Console.WriteLine(
            $"W1.1 persistent WGC pilot: {payload.decision} " +
            $"({successfulSamples}/{WgcPilotSampleFrames} samples, " +
            $"sample={achievedSampleFps:F2}fps, source={sourceArrivalFps:F2}fps, " +
            $"fresh={freshRatio:P1}, exact={dimensionsExact})");

        // Diagnostic pilot: a negative result is still valid evidence and must
        // remain available for the next governed capture-host decision.
        return 0;
    }
}
