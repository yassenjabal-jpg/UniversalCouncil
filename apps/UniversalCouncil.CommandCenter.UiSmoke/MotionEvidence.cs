using System.Diagnostics;
using System.IO;
using System.Security.Cryptography;
using System.Text.Json;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Threading;
using UniversalCouncil.CommandCenter;

namespace UniversalCouncil.CommandCenter.UiSmoke;

internal static partial class Program
{
    private const int MotionWidth = 1440;
    private const int MotionHeight = 900;
    private const int MotionFramesPerSecond = 30;

    private sealed record MotionStep(int Frame, string Name, Action<MainWindow> Execute);
    private sealed record MotionCapture(byte[] Pixels);
    private sealed record MotionFrameSample(
        int Frame,
        string File,
        double MeanSampleDelta,
        double ChangedSampleRatio,
        bool VisiblyChanged);
    private sealed record MotionFrameEvidence(
        int Frame,
        string File,
        string Sha256,
        double MeanSampleDelta,
        double ChangedSampleRatio,
        bool VisiblyChanged);

    private static int RenderMotionEvidence(string output, bool reducedMotion)
    {
        var mode = reducedMotion ? "reduced" : "full";
        var candidateSha = Environment.GetEnvironmentVariable("CANDIDATE_SHA")?.Trim().ToLowerInvariant() ?? "unknown";
        Environment.SetEnvironmentVariable(
            "UNIVERSALCOUNCIL_MOTION_EVIDENCE",
            reducedMotion ? "reduced" : "full");

        Directory.CreateDirectory(output);
        var framesDirectory = Path.Combine(output, "frames");
        Directory.CreateDirectory(framesDirectory);

        var window = App.CreateMainWindow(AppContext.BaseDirectory);
        SynchronizationContext.SetSynchronizationContext(
            new DispatcherSynchronizationContext(window.Dispatcher));
        ConfigureMotionEvidenceWindow(window);

        var seconds = reducedMotion ? 28 : 38;
        var frameCount = seconds * MotionFramesPerSecond;
        var steps = BuildMotionSteps(reducedMotion);
        var stepsByFrame = steps
            .GroupBy(step => step.Frame)
            .ToDictionary(group => group.Key, group => group.ToArray());

        var frameSamples = new List<MotionFrameSample>(frameCount);
        byte[]? previousPixels = null;
        var changedFrameCount = 0;
        var currentChangedRun = 0;
        var longestChangedRun = 0;
        var motionRunCount = 0;
        var wasChanged = false;
        var totalCaptureLatenessMs = 0d;
        var maxCaptureLatenessMs = 0d;
        var lateFrameCount = 0;
        var rawCapturePath = Path.Combine(output, $"wpf-{mode}-capture.bgra");
        var captureClock = Stopwatch.StartNew();

        using (var rawCapture = new FileStream(
            rawCapturePath,
            FileMode.Create,
            FileAccess.Write,
            FileShare.None,
            1024 * 1024,
            FileOptions.SequentialScan))
        {
            for (var frame = 0; frame < frameCount; frame++)
            {
                if (stepsByFrame.TryGetValue(frame, out var frameSteps))
                {
                    foreach (var step in frameSteps)
                    {
                        step.Execute(window);
                        Console.WriteLine($"Motion evidence [{mode}] step @{frame}: {step.Name}");
                    }
                }

                var targetCaptureTime = TimeSpan.FromSeconds(
                    (frame + 1d) / MotionFramesPerSecond);
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

                var capture = CaptureMotionFrame(window);
                rawCapture.Write(capture.Pixels, 0, capture.Pixels.Length);

                var (meanDelta, changedRatio) = previousPixels is null
                    ? (0d, 0d)
                    : ComputeFrameDelta(previousPixels, capture.Pixels);
                var visiblyChanged = meanDelta >= 0.20 || changedRatio >= 0.004;

                if (visiblyChanged)
                {
                    changedFrameCount++;
                    currentChangedRun++;
                    longestChangedRun = Math.Max(longestChangedRun, currentChangedRun);
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
                frameSamples.Add(new MotionFrameSample(
                    frame,
                    $"frame-{frame:D4}.png",
                    Math.Round(meanDelta, 4),
                    Math.Round(changedRatio, 6),
                    visiblyChanged));
                previousPixels = capture.Pixels;
            }
        }

        captureClock.Stop();
        var actualCaptureDurationSeconds = captureClock.Elapsed.TotalSeconds;

        try
        {
            ExtractRawFramesWithFfmpeg(rawCapturePath, framesDirectory, frameCount);
        }
        finally
        {
            if (File.Exists(rawCapturePath))
            {
                File.Delete(rawCapturePath);
            }
        }

        var frameEvidence = frameSamples
            .Select(sample =>
            {
                var path = Path.Combine(framesDirectory, sample.File);
                return new MotionFrameEvidence(
                    sample.Frame,
                    sample.File,
                    HashMotionFrame(path),
                    sample.MeanSampleDelta,
                    sample.ChangedSampleRatio,
                    sample.VisiblyChanged);
            })
            .ToList();

        var manifestPath = Path.Combine(output, "motion-evidence-manifest.json");
        File.WriteAllText(
            manifestPath,
            JsonSerializer.Serialize(
                new
                {
                    schema_version = "1.0",
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
                    input_mode = "PROGRAMMATIC_UI_AUTOMATION_AGAINST_REAL_WPF_CONTROLS",
                    width = MotionWidth,
                    height = MotionHeight,
                    frame_rate = MotionFramesPerSecond,
                    frame_count = frameCount,
                    encoded_duration_seconds = (double)frameCount / MotionFramesPerSecond,
                    capture_timing = new
                    {
                        clock = "STOPWATCH_REALTIME_WPF",
                        pipeline = "RENDERTARGETBITMAP_BGRA_STREAM_THEN_POST_CAPTURE_PNG_EXTRACTION",
                        target_capture_duration_seconds = (double)frameCount / MotionFramesPerSecond,
                        actual_capture_duration_seconds = Math.Round(actualCaptureDurationSeconds, 3),
                        max_capture_lateness_ms = Math.Round(maxCaptureLatenessMs, 3),
                        mean_capture_lateness_ms = Math.Round(
                            totalCaptureLatenessMs / Math.Max(1, frameCount),
                            3),
                        late_frame_count_over_one_frame = lateFrameCount,
                        png_encoding_during_capture = false,
                    },
                    motion_visibility = new
                    {
                        changed_frame_count = changedFrameCount,
                        changed_frame_ratio = Math.Round((double)changedFrameCount / Math.Max(1, frameCount - 1), 4),
                        longest_changed_run = longestChangedRun,
                        motion_run_count = motionRunCount,
                        frame_change_rule = "mean_sample_delta>=0.20 OR changed_sample_ratio>=0.004",
                    },
                    expected_video_file = reducedMotion
                        ? "p1-critical-path-reduced-motion.mp4"
                        : "p1-critical-path-motion.mp4",
                    steps = steps.Select((step, index) => new
                    {
                        evidence_step_id = $"step-{index + 1:D2}",
                        frame = step.Frame,
                        second = (double)step.Frame / MotionFramesPerSecond,
                        occurred_at_seconds = (double)step.Frame / MotionFramesPerSecond,
                        event_type = EvidenceEventType(step.Name),
                        semantic_object = EvidenceSemanticObject(step.Name),
                        step.Name,
                    }),
                    frames = frameEvidence,
                },
                new JsonSerializerOptions { WriteIndented = true }));

        Console.WriteLine(
            $"Command Center P1 {mode} motion evidence frames: PASS " +
            $"({frameCount} frames, {seconds}s, visible={changedFrameCount}, " +
            $"longest-run={longestChangedRun}, runs={motionRunCount})");
        return 0;
    }

    private static string EvidenceEventType(string name)
    {
        if (name.Contains("Activate Evidence role", StringComparison.Ordinal))
        {
            return "ROLE_ACTIVATED";
        }

        if (name.Contains("Request Changes intent", StringComparison.Ordinal))
        {
            return "OWNER_INTENT_PREVIEW";
        }

        if (name.Contains("Fork intent", StringComparison.Ordinal))
        {
            return "FORK_INTENT_PREVIEW";
        }

        if (name.Contains("Handoff Pulse context", StringComparison.Ordinal))
        {
            return "HANDOFF_CONTEXT_PREVIEW";
        }

        if (name.StartsWith("Navigate ", StringComparison.Ordinal))
        {
            return "EVIDENCE_NAVIGATION";
        }

        if (name.StartsWith("Close ", StringComparison.Ordinal))
        {
            return "CONTEXT_CLOSED";
        }

        return "EVIDENCE_INSPECTION";
    }

    private static string EvidenceSemanticObject(string name)
    {
        if (name.Contains("Evidence role", StringComparison.Ordinal))
        {
            return "role:evidence";
        }

        if (name.Contains("-> Project Workspace", StringComparison.Ordinal))
        {
            return "screen:living-project-workspace";
        }

        if (name.Contains("-> Software Autopilot", StringComparison.Ordinal))
        {
            return "screen:software-autopilot-project";
        }

        if (name.Contains("-> Studio Project", StringComparison.Ordinal))
        {
            return "screen:studio-project";
        }

        if (name.Contains("-> Decision Mode", StringComparison.Ordinal) ||
            name.Contains("Decision", StringComparison.Ordinal))
        {
            return "screen:owner-decision-mode";
        }

        if (name.Contains("-> Recovery/Fork", StringComparison.Ordinal) ||
            name.Contains("Fork", StringComparison.Ordinal) ||
            name.Contains("Recovery", StringComparison.Ordinal))
        {
            return "screen:checkpoint-recovery-fork";
        }

        if (name.Contains("-> Pulse Story", StringComparison.Ordinal) ||
            name.Contains("Handoff", StringComparison.Ordinal) ||
            name.Contains("Pulse", StringComparison.Ordinal))
        {
            return "screen:pulse-visual-project-story";
        }

        if (name.Contains("-> Work Receipt", StringComparison.Ordinal) ||
            name.Contains("Work Receipt", StringComparison.Ordinal))
        {
            return "screen:project-complete-work-receipt";
        }

        if (name.Contains("-> Home", StringComparison.Ordinal))
        {
            return "screen:home-owner-workspace";
        }

        return "command-center:wpf";
    }

    private static IReadOnlyList<MotionStep> BuildMotionSteps(bool reducedMotion)
    {
        int At(double seconds) => (int)Math.Round(seconds * MotionFramesPerSecond);

        if (reducedMotion)
        {
            return
            [
                new(At(1), "Navigate Home -> Project Workspace", window => NavigateForEvidence(window, "ProjectWorkspace")),
                new(At(4), "Navigate Project -> Software Autopilot", window => NavigateForEvidence(window, "SoftwareAutopilot")),
                new(At(7), "Navigate Autopilot -> Studio Project", window => NavigateForEvidence(window, "StudioProject")),
                new(At(10), "Navigate Studio -> Decision Mode", window => NavigateForEvidence(window, "DecisionMode")),
                new(At(13), "Navigate Decision -> Recovery/Fork", window => NavigateForEvidence(window, "RecoveryFork")),
                new(At(16), "Exercise non-authoritative Fork intent", window => ClickSecondaryHotspot(window, "fork")),
                new(At(18), "Navigate Recovery -> Pulse Story", window => NavigateForEvidence(window, "PulseStory")),
                new(At(21), "Navigate Pulse -> Work Receipt", window => NavigateForEvidence(window, "WorkReceipt")),
                new(At(24), "Navigate Receipt -> Home", window => NavigateForEvidence(window, "Home")),
            ];
        }

        return
        [
            new(At(2), "Navigate Home -> Project Workspace", window => NavigateForEvidence(window, "ProjectWorkspace")),
            new(At(4), "Activate Evidence role and open context", window => ClickSecondaryHotspot(window, "evidence", "Evidence")),
            new(At(5.5), "Close role context", CloseMotionDrawer),
            new(At(7), "Navigate Project -> Software Autopilot", window => NavigateForEvidence(window, "SoftwareAutopilot")),
            new(At(10), "Navigate Autopilot -> Studio Project", window => NavigateForEvidence(window, "StudioProject")),
            new(At(13), "Navigate Studio -> Decision Mode", window => NavigateForEvidence(window, "DecisionMode")),
            new(At(16), "Inspect Decision evidence", window => ClickSecondaryHotspot(window, "inspect-evidence")),
            new(At(17.5), "Close Decision evidence", CloseMotionDrawer),
            new(At(19), "Exercise non-authoritative Request Changes intent", window => ClickSecondaryHotspot(window, "request-changes")),
            new(At(21), "Navigate Decision -> Recovery/Fork", window => NavigateForEvidence(window, "RecoveryFork")),
            new(At(24), "Exercise non-authoritative Fork intent", window => ClickSecondaryHotspot(window, "fork")),
            new(At(26), "Navigate Recovery -> Pulse Story", window => NavigateForEvidence(window, "PulseStory")),
            new(At(29), "Open Handoff Pulse context", window => ClickSecondaryHotspot(window, "handoff")),
            new(At(30.5), "Close Handoff context", CloseMotionDrawer),
            new(At(32), "Navigate Pulse -> Work Receipt", window => NavigateForEvidence(window, "WorkReceipt")),
            new(At(35), "Navigate Receipt -> Home", window => NavigateForEvidence(window, "Home")),
        ];
    }

    private static void ConfigureMotionEvidenceWindow(MainWindow window)
    {
        if (window.FindName("ReferenceImage") is UIElement referenceImage)
        {
            referenceImage.Visibility = Visibility.Visible;
        }

        if (window.Content is not FrameworkElement root)
        {
            throw new InvalidOperationException("MainWindow root content is not a FrameworkElement.");
        }

        root.Width = MotionWidth;
        root.Height = MotionHeight;
        root.Measure(new Size(MotionWidth, MotionHeight));
        root.Arrange(new Rect(0, 0, MotionWidth, MotionHeight));
        root.UpdateLayout();
    }

    private static void ClickSecondaryHotspot(MainWindow window, string tag, string? tooltipContains = null)
    {
        if (window.FindName("SecondaryInteractionCanvas") is not Canvas canvas)
        {
            throw new InvalidOperationException("SecondaryInteractionCanvas is unavailable.");
        }

        var button = canvas.Children
            .OfType<Button>()
            .FirstOrDefault(candidate =>
                string.Equals(candidate.Tag?.ToString(), tag, StringComparison.Ordinal) &&
                (tooltipContains is null ||
                 (candidate.ToolTip?.ToString()?.Contains(
                     tooltipContains,
                     StringComparison.OrdinalIgnoreCase) ?? false)));

        if (button is null)
        {
            throw new InvalidOperationException(
                $"Unable to find interactive WPF hotspot '{tag}' ({tooltipContains ?? "any tooltip"}).");
        }

        button.RaiseEvent(new RoutedEventArgs(Button.ClickEvent, button));
    }

    private static void CloseMotionDrawer(MainWindow window)
    {
        if (window.FindName("CloseDrawerButton") is not Button button)
        {
            throw new InvalidOperationException("CloseDrawerButton is unavailable.");
        }

        button.RaiseEvent(new RoutedEventArgs(Button.ClickEvent, button));
    }

    private static void PumpDispatcher(TimeSpan duration)
    {
        var frame = new DispatcherFrame();
        var timer = new DispatcherTimer(DispatcherPriority.Background)
        {
            Interval = duration,
        };

        timer.Tick += (_, _) =>
        {
            timer.Stop();
            frame.Continue = false;
        };
        timer.Start();
        Dispatcher.PushFrame(frame);
    }

    private static void PaceDispatcherToCaptureTime(
        Stopwatch captureClock,
        TimeSpan targetCaptureTime)
    {
        var remaining = targetCaptureTime - captureClock.Elapsed;
        if (remaining > TimeSpan.Zero)
        {
            PumpDispatcher(remaining);
            return;
        }

        // The capture is already behind its target. Pump one render turn without
        // adding a synthetic delay so WPF animation clocks and queued continuations
        // can advance before the actual RenderTargetBitmap sample.
        PumpDispatcher(TimeSpan.FromMilliseconds(1));
    }

    private static MotionCapture CaptureMotionFrame(MainWindow window)
    {
        if (window.Content is not FrameworkElement root)
        {
            throw new InvalidOperationException("MainWindow root content is not a FrameworkElement.");
        }

        root.UpdateLayout();

        var bitmap = new RenderTargetBitmap(
            MotionWidth,
            MotionHeight,
            96,
            96,
            PixelFormats.Pbgra32);
        bitmap.Render(root);

        var stride = MotionWidth * 4;
        var pixels = new byte[stride * MotionHeight];
        bitmap.CopyPixels(pixels, stride, 0);
        return new MotionCapture(pixels);
    }

    private static void ExtractRawFramesWithFfmpeg(
        string rawCapturePath,
        string framesDirectory,
        int frameCount)
    {
        var outputPattern = Path.Combine(framesDirectory, "frame-%04d.png");
        var startInfo = new ProcessStartInfo
        {
            FileName = "ffmpeg",
            UseShellExecute = false,
            RedirectStandardError = true,
            RedirectStandardOutput = true,
            CreateNoWindow = true,
        };

        foreach (var argument in new[]
        {
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "rawvideo",
            "-pixel_format",
            "bgra",
            "-video_size",
            $"{MotionWidth}x{MotionHeight}",
            "-framerate",
            MotionFramesPerSecond.ToString(),
            "-i",
            rawCapturePath,
            "-start_number",
            "0",
            "-frames:v",
            frameCount.ToString(),
            "-compression_level",
            "6",
            outputPattern,
        })
        {
            startInfo.ArgumentList.Add(argument);
        }

        using var process = Process.Start(startInfo)
            ?? throw new InvalidOperationException("Unable to start ffmpeg for WPF frame extraction.");
        var stdoutTask = process.StandardOutput.ReadToEndAsync();
        var stderrTask = process.StandardError.ReadToEndAsync();
        process.WaitForExit();
        var stdout = stdoutTask.GetAwaiter().GetResult();
        var stderr = stderrTask.GetAwaiter().GetResult();

        if (process.ExitCode != 0)
        {
            throw new InvalidOperationException(
                $"ffmpeg WPF frame extraction failed ({process.ExitCode}). {stderr} {stdout}");
        }

        var extractedFrameCount = Directory.GetFiles(framesDirectory, "frame-*.png").Length;
        if (extractedFrameCount != frameCount)
        {
            throw new InvalidOperationException(
                $"WPF raw-frame extraction mismatch: expected {frameCount}, got {extractedFrameCount}.");
        }
    }

    private static string HashMotionFrame(string path)
    {
        using var stream = File.OpenRead(path);
        return Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
    }

    private static (double MeanSampleDelta, double ChangedSampleRatio) ComputeFrameDelta(
        byte[] previous,
        byte[] current)
    {
        if (previous.Length != current.Length)
        {
            return (255, 1);
        }

        long totalDelta = 0;
        var changedSamples = 0;
        var samples = 0;

        // Sample one BGRA pixel out of every sixteen pixels. This is dense enough to
        // catch region motion while keeping evidence capture affordable in CI.
        for (var index = 0; index + 2 < current.Length; index += 64)
        {
            var blue = Math.Abs(current[index] - previous[index]);
            var green = Math.Abs(current[index + 1] - previous[index + 1]);
            var red = Math.Abs(current[index + 2] - previous[index + 2]);
            var delta = blue + green + red;

            totalDelta += delta;
            if (delta >= 18)
            {
                changedSamples++;
            }

            samples++;
        }

        if (samples == 0)
        {
            return (0, 0);
        }

        return (
            (double)totalDelta / (samples * 3),
            (double)changedSamples / samples);
    }
}
