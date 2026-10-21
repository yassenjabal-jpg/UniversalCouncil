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
    private const int MotionFramesPerSecond = 6;

    private sealed record MotionStep(int Frame, string Name, Action<MainWindow> Execute);

    private static int RenderMotionEvidence(string output, bool reducedMotion)
    {
        var mode = reducedMotion ? "reduced" : "full";
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

        var frameEvidence = new List<object>(frameCount);
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
            var sha256 = CaptureMotionFrame(window, path);
            frameEvidence.Add(new
            {
                frame,
                file = Path.GetFileName(path),
                sha256,
            });
        }

        var manifestPath = Path.Combine(output, "motion-evidence-manifest.json");
        File.WriteAllText(
            manifestPath,
            JsonSerializer.Serialize(
                new
                {
                    schema_version = "1.0",
                    evidence_type = "WPF_P1_CRITICAL_PATH_MOTION",
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
                    expected_video_file = reducedMotion
                        ? "p1-critical-path-reduced-motion.mp4"
                        : "p1-critical-path-motion.mp4",
                    steps = steps.Select(step => new
                    {
                        frame = step.Frame,
                        second = (double)step.Frame / MotionFramesPerSecond,
                        step.Name,
                    }),
                    frames = frameEvidence,
                },
                new JsonSerializerOptions { WriteIndented = true }));

        Console.WriteLine(
            $"Command Center P1 {mode} motion evidence frames: PASS ({frameCount} frames, {seconds}s)");
        return 0;
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

    private static string CaptureMotionFrame(MainWindow window, string path)
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

        var encoder = new PngBitmapEncoder();
        encoder.Frames.Add(BitmapFrame.Create(bitmap));

        using (var stream = File.Create(path))
        {
            encoder.Save(stream);
        }

        var bytes = File.ReadAllBytes(path);
        return Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
    }
}
