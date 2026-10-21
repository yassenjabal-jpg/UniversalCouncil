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
    private sealed record MotionCapture(string Sha256, byte[] Pixels);
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
        ConfigureMotionEvidenceWindow(window);

        var seconds = reducedMotion ? 20 : 28;
        var frameCount = seconds * MotionFramesPerSecond;
        var steps = BuildMotionSteps(reducedMotion);
        var stepsByFrame = steps
            .GroupBy(step => step.Frame)
            .ToDictionary(group => group.Key, group => group.ToArray());

        var frameEvidence = new List<MotionFrameEvidence>(frameCount);
        byte[]? previousPixels = null;
        var changedFrameCount = 0;
        var currentChangedRun = 0;
        var longestChangedRun = 0;
        var motionRunCount = 0;
        var wasChanged = false;

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

            PumpDispatcher(TimeSpan.FromMilliseconds(1000d / MotionFramesPerSecond));
            var path = Path.Combine(framesDirectory, $"frame-{frame:D4}.png");
            var capture = CaptureMotionFrame(window, path);
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
            frameEvidence.Add(new MotionFrameEvidence(
                frame,
                Path.GetFileName(path),
                capture.Sha256,
                Math.Round(meanDelta, 4),
                Math.Round(changedRatio, 6),
                visiblyChanged));
            previousPixels = capture.Pixels;
        }

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

        if (name.Contains("Decision", StringComparison.Ordinal))
        {
            return "screen:owner-decision-mode";
        }

        if (name.Contains("Fork", StringComparison.Ordinal) || name.Contains("Recovery", StringComparison.Ordinal))
        {
            return "screen:checkpoint-recovery-fork";
        }

        if (name.Contains("Handoff", StringComparison.Ordinal) || name.Contains("Pulse", StringComparison.Ordinal))
        {
            return "screen:pulse-visual-project-story";
        }

        if (name.Contains("Work Receipt", StringComparison.Ordinal))
        {
            return "screen:project-complete-work-receipt";
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
                new(At(3), "Open Evidence role context", window => ClickSecondaryHotspot(window, "evidence", "Evidence")),
                new(At(4.5), "Close role context", CloseMotionDrawer),
                new(At(6), "Navigate Project -> Decision Mode", window => NavigateForEvidence(window, "DecisionMode")),
                new(At(8), "Inspect Decision evidence", window => ClickSecondaryHotspot(window, "inspect-evidence")),
                new(At(9.5), "Close evidence context", CloseMotionDrawer),
                new(At(11), "Navigate Decision -> Recovery/Fork", window => NavigateForEvidence(window, "RecoveryFork")),
                new(At(13), "Exercise non-authoritative Fork intent", window => ClickSecondaryHotspot(window, "fork")),
                new(At(15), "Navigate Recovery -> Work Receipt", window => NavigateForEvidence(window, "WorkReceipt")),
            ];
        }

        return
        [
            new(At(2), "Navigate Home -> Project Workspace", window => NavigateForEvidence(window, "ProjectWorkspace")),
            new(At(4), "Activate Evidence role and open context", window => ClickSecondaryHotspot(window, "evidence", "Evidence")),
            new(At(6), "Close role context", CloseMotionDrawer),
            new(At(7), "Open Evidence reasoning context", window => ClickSecondaryHotspot(window, "evidence", "Reasoning")),
            new(At(9), "Close reasoning context", CloseMotionDrawer),
            new(At(10), "Navigate Project -> Decision Mode", window => NavigateForEvidence(window, "DecisionMode")),
            new(At(12), "Inspect Decision evidence", window => ClickSecondaryHotspot(window, "inspect-evidence")),
            new(At(14), "Close Decision evidence", CloseMotionDrawer),
            new(At(15), "Exercise non-authoritative Request Changes intent", window => ClickSecondaryHotspot(window, "request-changes")),
            new(At(17), "Navigate Decision -> Recovery/Fork", window => NavigateForEvidence(window, "RecoveryFork")),
            new(At(19), "Exercise non-authoritative Fork intent", window => ClickSecondaryHotspot(window, "fork")),
            new(At(21), "Navigate Recovery -> Pulse Story", window => NavigateForEvidence(window, "PulseStory")),
            new(At(22), "Open Handoff Pulse context", window => ClickSecondaryHotspot(window, "handoff")),
            new(At(24), "Close Handoff context", CloseMotionDrawer),
            new(At(25), "Navigate Pulse -> Work Receipt", window => NavigateForEvidence(window, "WorkReceipt")),
        ];
    }

    private static void ConfigureMotionEvidenceWindow(MainWindow window)
    {
        if (window.FindName("ReferenceImage") is UIElement referenceImage)
        {
            referenceImage.Visibility = Visibility.Collapsed;
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

    private static MotionCapture CaptureMotionFrame(MainWindow window, string path)
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

        var encoder = new PngBitmapEncoder();
        encoder.Frames.Add(BitmapFrame.Create(bitmap));

        using (var stream = File.Create(path))
        {
            encoder.Save(stream);
        }

        var bytes = File.ReadAllBytes(path);
        var sha256 = Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
        return new MotionCapture(sha256, pixels);
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
