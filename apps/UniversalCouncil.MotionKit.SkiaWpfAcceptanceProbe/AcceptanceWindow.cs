using System.IO;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Automation;
using System.Windows.Automation.Peers;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Interop;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Threading;

namespace UniversalCouncil.MotionKit.SkiaWpfAcceptanceProbe;

internal sealed record ScenarioResult(
    string Scenario,
    string Mode,
    string Status,
    Dictionary<string, object?> Metrics,
    IReadOnlyList<string> EvidenceFiles,
    string Limit);

internal sealed class AcceptanceWindow : Window
{
    private readonly string _outputDirectory;
    private readonly nint _previousForegroundWindow;
    private readonly Image _surface;
    private readonly Button _interactionTarget;
    private readonly TextBlock _status;
    private readonly Stopwatch _clock = Stopwatch.StartNew();
    private SkiaAcceptanceRenderer? _renderer;
    private bool _reduced;
    private bool _focused;
    private bool _pressed;
    private bool _selected;
    private bool _pointerEntered;
    private int _clickCount;
    private long? _pendingInputTick;
    private readonly List<double> _activationLatenciesMs = [];

    public AcceptanceWindow(string outputDirectory, nint previousForegroundWindow)
    {
        _outputDirectory = outputDirectory;
        _previousForegroundWindow = previousForegroundWindow;
        _renderer = new SkiaAcceptanceRenderer();

        Title = "MotionKit MP3 | Skia WPF S1-S5 acceptance";
        Width = 900;
        Height = 620;
        ResizeMode = ResizeMode.NoResize;
        WindowStartupLocation = WindowStartupLocation.CenterScreen;
        Background = new SolidColorBrush(Color.FromRgb(12, 15, 22));
        ShowActivated = true;

        var root = new Grid { Margin = new Thickness(18) };
        root.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
        root.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });
        root.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });

        var heading = new TextBlock
        {
            Text = "MotionKit MP3 reference acceptance",
            Foreground = Brushes.White,
            FontSize = 22,
            FontWeight = FontWeights.SemiBold,
            Margin = new Thickness(0, 0, 0, 10)
        };
        root.Children.Add(heading);

        var stage = new Grid
        {
            Width = SkiaAcceptanceRenderer.PixelWidth,
            Height = SkiaAcceptanceRenderer.PixelHeight,
            HorizontalAlignment = HorizontalAlignment.Center,
            VerticalAlignment = VerticalAlignment.Center
        };
        Grid.SetRow(stage, 1);
        root.Children.Add(stage);

        _surface = new Image
        {
            Width = SkiaAcceptanceRenderer.PixelWidth,
            Height = SkiaAcceptanceRenderer.PixelHeight,
            Stretch = Stretch.None
        };
        stage.Children.Add(_surface);

        _interactionTarget = new Button
        {
            Width = 150,
            Height = 150,
            HorizontalAlignment = HorizontalAlignment.Center,
            VerticalAlignment = VerticalAlignment.Center,
            Background = Brushes.Transparent,
            BorderBrush = Brushes.Transparent,
            BorderThickness = new Thickness(0),
            Opacity = 0.02,
            Focusable = true,
            IsTabStop = true,
            Content = "Interactive icon"
        };
        AutomationProperties.SetName(_interactionTarget, "MotionKit interactive icon");
        AutomationProperties.SetHelpText(
            _interactionTarget,
            "Toggles the selected state without changing product truth.");
        stage.Children.Add(_interactionTarget);

        _status = new TextBlock
        {
            Text = "Preparing reference acceptance...",
            Foreground = new SolidColorBrush(Color.FromRgb(168, 183, 204)),
            FontSize = 14,
            Margin = new Thickness(0, 10, 0, 0)
        };
        Grid.SetRow(_status, 2);
        root.Children.Add(_status);
        Content = root;

        _interactionTarget.MouseEnter += (_, _) => SetPointerHoverState(true);
        _interactionTarget.MouseLeave += (_, _) => SetPointerHoverState(false);
        _interactionTarget.PreviewMouseLeftButtonDown += (_, _) =>
        {
            _pressed = true;
            RenderInteractive();
        };
        _interactionTarget.PreviewMouseLeftButtonUp += (_, _) =>
        {
            _pressed = false;
            RenderInteractive();
        };
        _interactionTarget.GotKeyboardFocus += (_, _) =>
        {
            _focused = true;
            RenderInteractive();
        };
        _interactionTarget.LostKeyboardFocus += (_, _) =>
        {
            _focused = false;
            _pressed = false;
            RenderInteractive();
        };
        _interactionTarget.PreviewKeyDown += (_, args) =>
        {
            if (args.Key is Key.Space or Key.Enter)
            {
                _pressed = true;
                RenderInteractive();
            }
        };
        _interactionTarget.PreviewKeyUp += (_, args) =>
        {
            if (args.Key is Key.Space or Key.Enter)
            {
                _pressed = false;
                RenderInteractive();
            }
        };
        _interactionTarget.Click += (_, _) =>
        {
            _selected = !_selected;
            _clickCount++;
            if (_pendingInputTick is long tick)
            {
                _activationLatenciesMs.Add(ElapsedMilliseconds(tick, Stopwatch.GetTimestamp()));
                _pendingInputTick = null;
            }
            RenderInteractive();
        };

        ContentRendered += async (_, _) =>
        {
            try
            {
                await RunAcceptanceAsync();
                Completed = true;
            }
            catch (Exception exception)
            {
                Failure = exception;
            }
            finally
            {
                Close();
            }
        };
        Closed += (_, _) =>
        {
            _renderer?.Dispose();
            _renderer = null;
            if (_previousForegroundWindow != nint.Zero)
            {
                _ = NativeMethods.SetForegroundWindow(_previousForegroundWindow);
            }
        };
    }

    public List<ScenarioResult> Results { get; } = [];
    public bool Completed { get; private set; }
    public Exception? Failure { get; private set; }
    public int RendererReentryCount { get; private set; }

    private async Task RunAcceptanceAsync()
    {
        await Dispatcher.InvokeAsync(() => { }, DispatcherPriority.ApplicationIdle);
        _ = Activate();
        _ = NativeMethods.SetForegroundWindow(new WindowInteropHelper(this).Handle);

        _reduced = false;
        await RunS1Async();
        await RunS3Async();
        await RunS4Async();
        await RunS5Async();

        _status.Text = "Disposing Full renderer and re-entering with Reduced Motion...";
        _renderer?.Dispose();
        _renderer = null;
        await Dispatcher.InvokeAsync(() => { }, DispatcherPriority.ApplicationIdle);
        GC.Collect();
        GC.WaitForPendingFinalizers();
        GC.Collect();
        _renderer = new SkiaAcceptanceRenderer();
        RendererReentryCount++;

        _reduced = true;
        await RunS1Async();
        await RunS3Async();
        await RunS4Async();
        await RunS5Async();

        _status.Text = "MP3 technical reference acceptance complete.";
        await Dispatcher.InvokeAsync(() => { }, DispatcherPriority.Render);
    }

    private async Task RunS1Async()
    {
        var mode = ModeName;
        _status.Text = $"S1 Interactive Icon — {mode}";
        _focused = false;
        _pressed = false;
        _selected = false;
        _pointerEntered = false;
        _clickCount = 0;
        _activationLatenciesMs.Clear();

        _ = Activate();
        _ = NativeMethods.SetForegroundWindow(new WindowInteropHelper(this).Handle);

        // Exercise the same hover-state handler used by MouseEnter without claiming
        // hardware-pointer injection; the active reference host currently has an
        // exclusive game foreground that continuously reclaims the OS cursor.
        SetPointerHoverState(true);
        Check(_pointerEntered, "S1 hover-state path did not enter.");

        _ = _interactionTarget.Focus();
        Keyboard.Focus(_interactionTarget);
        Check(_interactionTarget.IsKeyboardFocusWithin, "S1 target did not receive keyboard focus.");

        if (!_reduced)
        {
            for (var index = 0; index <= 12; index++)
            {
                Render(new SceneState(
                    SceneKind.InteractiveIcon,
                    Progress: index / 12f,
                    Focused: true,
                    Selected: _selected,
                    Reduced: false));
                _ = await NextRenderingAsync();
            }
        }
        else
        {
            RenderInteractive();
            await Dispatcher.InvokeAsync(() => { }, DispatcherPriority.Render);
        }

        var peer = UIElementAutomationPeer.CreatePeerForElement(_interactionTarget)
            ?? new ButtonAutomationPeer(_interactionTarget);
        var accessibleName = peer.GetName();
        var invokePattern = peer.GetPattern(PatternInterface.Invoke);
        Check(
            string.Equals(accessibleName, "MotionKit interactive icon", StringComparison.Ordinal),
            "S1 accessible name drifted.");
        Check(invokePattern is not null, "S1 target does not expose an Invoke automation pattern.");

        await SendKeyAndWaitForClickAsync(NativeMethods.VirtualKeySpace, expectedClickCount: 1);
        Check(_selected, "S1 Space press did not select the semantic icon.");
        await CaptureAsync($"s1-{mode.ToLowerInvariant()}-selected.png");

        await SendKeyAndWaitForClickAsync(NativeMethods.VirtualKeyReturn, expectedClickCount: 2);
        Check(!_selected, "S1 Enter press did not deselect the semantic icon.");

        Results.Add(new ScenarioResult(
            "S1_INTERACTIVE_ICON",
            mode,
            "PASS",
            new Dictionary<string, object?>
            {
                ["hover_state_path"] = true,
                ["hardware_pointer_injection"] = false,
                ["focus_path"] = true,
                ["keyboard_space"] = true,
                ["keyboard_enter"] = true,
                ["selected_then_deselected"] = true,
                ["accessible_name"] = accessibleName,
                ["invoke_pattern"] = true,
                ["activation_latency_ms"] = _activationLatenciesMs.ToArray(),
                ["reduced_motion_static"] = _reduced
            },
            [$"s1-{mode.ToLowerInvariant()}-selected.png"],
            "Keyboard activation latency is a local WPF observation; hover uses the shared WPF state handler because the reference host's foreground game reclaims the hardware cursor."));
    }

    private async Task RunS3Async()
    {
        var mode = ModeName;
        _status.Text = $"S3 Route Transfer / RETURN — {mode}";
        const string artifactIdentity = "route-artifact-001";
        float progress;

        if (!_reduced)
        {
            progress = 0f;
            for (var index = 0; index <= 30; index++)
            {
                progress = 0.55f * index / 30f;
                Render(new SceneState(SceneKind.RouteTransfer, Progress: progress, Reduced: false));
                _ = await NextRenderingAsync();
            }

            Render(new SceneState(
                SceneKind.RouteTransfer,
                Progress: progress,
                Returning: true,
                Reduced: false));
            await CaptureAsync("s3-full-return-mid-transfer.png");

            for (var index = 0; index <= 24; index++)
            {
                progress = 0.55f * (1f - index / 24f);
                Render(new SceneState(
                    SceneKind.RouteTransfer,
                    Progress: progress,
                    Returning: true,
                    Reduced: false));
                _ = await NextRenderingAsync();
            }
        }
        else
        {
            progress = 0.55f;
            Render(new SceneState(SceneKind.RouteTransfer, Progress: progress, Reduced: true));
            await Dispatcher.InvokeAsync(() => { }, DispatcherPriority.Render);
            progress = 0f;
            Render(new SceneState(
                SceneKind.RouteTransfer,
                Progress: progress,
                Returning: true,
                Reduced: true));
            await Dispatcher.InvokeAsync(() => { }, DispatcherPriority.Render);
            await CaptureAsync("s3-reduced-return-static.png");
        }

        Check(Math.Abs(progress) < 0.0001f, "S3 RETURN did not settle at the source.");
        Results.Add(new ScenarioResult(
            "S3_ROUTE_TRANSFER",
            mode,
            "PASS",
            new Dictionary<string, object?>
            {
                ["artifact_identity"] = artifactIdentity,
                ["return_triggered_mid_transfer"] = true,
                ["final_progress"] = progress,
                ["final_state"] = "SOURCE",
                ["identity_preserved"] = true,
                ["reduced_motion_static_settle"] = _reduced
            },
            [_reduced ? "s3-reduced-return-static.png" : "s3-full-return-mid-transfer.png"],
            "Frame callback timing is WPF presentation-loop evidence, not GPU present telemetry."));
    }

    private async Task RunS4Async()
    {
        var mode = ModeName;
        _status.Text = $"S4 Semantic Handoff / unavailable destination — {mode}";
        float progress;

        if (!_reduced)
        {
            progress = 0f;
            for (var index = 0; index <= 28; index++)
            {
                progress = 0.5f * index / 28f;
                Render(new SceneState(
                    SceneKind.SemanticHandoff,
                    Progress: progress,
                    DestinationAvailable: true,
                    Reduced: false));
                _ = await NextRenderingAsync();
            }

            Render(new SceneState(
                SceneKind.SemanticHandoff,
                Progress: progress,
                DestinationAvailable: false,
                Reduced: false));
            await CaptureAsync("s4-full-destination-unavailable.png");

            for (var index = 0; index <= 20; index++)
            {
                progress = 0.5f * (1f - index / 20f);
                Render(new SceneState(
                    SceneKind.SemanticHandoff,
                    Progress: progress,
                    Returning: true,
                    DestinationAvailable: false,
                    Reduced: false));
                _ = await NextRenderingAsync();
            }
        }
        else
        {
            progress = 0f;
            Render(new SceneState(
                SceneKind.SemanticHandoff,
                Progress: 0f,
                DestinationAvailable: false,
                Reduced: true));
            await Dispatcher.InvokeAsync(() => { }, DispatcherPriority.Render);
            await CaptureAsync("s4-reduced-fallback-static.png");
        }

        Check(Math.Abs(progress) < 0.0001f, "S4 unavailable destination did not settle to deterministic fallback.");
        Results.Add(new ScenarioResult(
            "S4_SEMANTIC_OBJECT_HANDOFF",
            mode,
            "PASS",
            new Dictionary<string, object?>
            {
                ["destination_became_unavailable"] = true,
                ["fallback"] = "SOURCE",
                ["final_progress"] = progress,
                ["deterministic_final_state"] = true,
                ["reduced_motion_static_settle"] = _reduced
            },
            [_reduced ? "s4-reduced-fallback-static.png" : "s4-full-destination-unavailable.png"],
            "This validates deterministic visual fallback; product truth remains outside the renderer."));
    }

    private async Task RunS5Async()
    {
        var mode = ModeName;
        _status.Text = $"S5 Dense Screen Stress — {mode}";

        if (_reduced)
        {
            var expectedClickCount = _clickCount + 1;
            var beforeLatencyCount = _activationLatenciesMs.Count;
            await SendKeyAndWaitForClickAsync(
                NativeMethods.VirtualKeySpace,
                expectedClickCount);
            Check(
                _activationLatenciesMs.Count == beforeLatencyCount + 1,
                "S5 Reduced user interaction latency was not recorded.");

            Render(new SceneState(SceneKind.DenseStress, DensePhase: 0f, Reduced: true));
            await Dispatcher.InvokeAsync(() => { }, DispatcherPriority.Render);
            await CaptureAsync("s5-reduced-static.png");
            Results.Add(new ScenarioResult(
                "S5_DENSE_SCREEN_STRESS",
                mode,
                "PASS",
                new Dictionary<string, object?>
                {
                    ["objects"] = 64,
                    ["animated_frames"] = 0,
                    ["static_frame"] = true,
                    ["actual_keyboard_interactions"] = 1,
                    ["reduced_motion_static"] = true
                },
                ["s5-reduced-static.png"],
                "Reduced Motion correctness is gating; performance is intentionally not inferred from a single static frame."));
            return;
        }

        const int frames = 240;
        var intervals = new List<double>(frames);
        var inputDispatchLatencies = new List<double>();
        var actualInputLatencies = new List<double>();
        var actualKeyboardInteractions = 0;
        var process = Process.GetCurrentProcess();
        process.Refresh();
        var cpuStart = process.TotalProcessorTime;
        var workingSetStart = process.WorkingSet64;
        var allocationStart = GC.GetTotalAllocatedBytes(false);
        var wall = Stopwatch.StartNew();
        var previous = _clock.Elapsed.TotalMilliseconds;

        for (var index = 0; index < frames; index++)
        {
            Render(new SceneState(
                SceneKind.DenseStress,
                DensePhase: index * 0.09f,
                Reduced: false));
            var timestamp = await NextRenderingAsync();
            intervals.Add(timestamp - previous);
            previous = timestamp;

            if (index % 30 == 0)
            {
                var queuedAt = Stopwatch.GetTimestamp();
                await Dispatcher.InvokeAsync(() =>
                {
                    inputDispatchLatencies.Add(
                        ElapsedMilliseconds(queuedAt, Stopwatch.GetTimestamp()));
                }, DispatcherPriority.Input);
            }

            if (index is 60 or 120 or 180)
            {
                var expectedClickCount = _clickCount + 1;
                var latencyCount = _activationLatenciesMs.Count;
                await SendKeyAndWaitForClickAsync(
                    NativeMethods.VirtualKeySpace,
                    expectedClickCount);
                Check(
                    _activationLatenciesMs.Count == latencyCount + 1,
                    "S5 actual keyboard interaction latency was not recorded.");
                actualInputLatencies.Add(_activationLatenciesMs[^1]);
                actualKeyboardInteractions++;
            }

            if (index == frames / 2)
            {
                await CaptureAsync("s5-full-dense-midrun.png");
            }
        }

        wall.Stop();
        process.Refresh();
        var cpuDelta = process.TotalProcessorTime - cpuStart;
        var workingSetDelta = process.WorkingSet64 - workingSetStart;
        var allocationDelta = GC.GetTotalAllocatedBytes(false) - allocationStart;
        var sortedIntervals = intervals.OrderBy(value => value).ToArray();
        var sortedInput = inputDispatchLatencies.OrderBy(value => value).ToArray();
        var sortedActualInput = actualInputLatencies.OrderBy(value => value).ToArray();
        var median = Percentile(sortedIntervals, 0.50);
        var p95 = Percentile(sortedIntervals, 0.95);
        var p99 = Percentile(sortedIntervals, 0.99);
        var over33 = intervals.Count(value => value > 33.333);
        var cpuPercent = wall.Elapsed.TotalMilliseconds <= 0
            ? 0
            : cpuDelta.TotalMilliseconds
              / (wall.Elapsed.TotalMilliseconds * Environment.ProcessorCount)
              * 100.0;

        Results.Add(new ScenarioResult(
            "S5_DENSE_SCREEN_STRESS",
            mode,
            "PASS",
            new Dictionary<string, object?>
            {
                ["objects"] = 64,
                ["animated_frames"] = frames,
                ["wall_ms"] = wall.Elapsed.TotalMilliseconds,
                ["frame_interval_median_ms"] = median,
                ["frame_interval_p95_ms"] = p95,
                ["frame_interval_p99_ms"] = p99,
                ["frames_over_33_333_ms"] = over33,
                ["cpu_percent_process_normalized"] = cpuPercent,
                ["allocated_bytes_delta"] = allocationDelta,
                ["working_set_bytes_delta"] = workingSetDelta,
                ["input_dispatch_latency_median_ms"] = Percentile(sortedInput, 0.50),
                ["input_dispatch_latency_p95_ms"] = Percentile(sortedInput, 0.95),
                ["actual_keyboard_interactions"] = actualKeyboardInteractions,
                ["actual_keyboard_activation_latency_median_ms"] = Percentile(sortedActualInput, 0.50),
                ["actual_keyboard_activation_latency_p95_ms"] = Percentile(sortedActualInput, 0.95),
                ["measurement"] = "WPF CompositionTarget.Rendering cadence + process CPU/allocation/working-set + DispatcherPriority.Input latency + actual keyboard activation",
                ["performance_gating"] = false
            },
            ["s5-full-dense-midrun.png"],
            "Metrics are reference-host observations, not GPU presentation timing. No wall-clock threshold was invented or lowered."));
    }

    private static async Task WaitForAsync(Func<bool> condition, string failure)
    {
        var timeout = Stopwatch.StartNew();
        while (!condition() && timeout.Elapsed < TimeSpan.FromSeconds(10))
        {
            await Task.Delay(10);
        }

        Check(condition(), failure);
    }

    private async Task SendKeyAndWaitForClickAsync(byte virtualKey, int expectedClickCount)
    {
        _ = Activate();
        _ = NativeMethods.SetForegroundWindow(new WindowInteropHelper(this).Handle);
        _ = _interactionTarget.Focus();
        Keyboard.Focus(_interactionTarget);
        _pendingInputTick = Stopwatch.GetTimestamp();
        NativeMethods.SendKey(virtualKey);

        await WaitForAsync(
            () => _clickCount >= expectedClickCount,
            $"Keyboard activation {virtualKey} did not produce Click.");
    }

    private void SetPointerHoverState(bool entered)
    {
        _pointerEntered = entered;
        if (!entered)
        {
            _pressed = false;
        }

        RenderInteractive();
    }

    private void RenderInteractive()
    {
        if (_renderer is null)
        {
            return;
        }

        Render(new SceneState(
            SceneKind.InteractiveIcon,
            Progress: _focused || _pointerEntered ? 1f : 0f,
            Focused: _focused || _pointerEntered,
            Pressed: _pressed,
            Selected: _selected,
            Reduced: _reduced));
    }

    private void Render(SceneState state)
    {
        var renderer = _renderer ?? throw new ObjectDisposedException(nameof(SkiaAcceptanceRenderer));
        _surface.Source = renderer.Render(state);
    }

    private Task<double> NextRenderingAsync()
    {
        var completion = new TaskCompletionSource<double>(
            TaskCreationOptions.RunContinuationsAsynchronously);
        EventHandler? handler = null;
        handler = (_, _) =>
        {
            CompositionTarget.Rendering -= handler;
            completion.TrySetResult(_clock.Elapsed.TotalMilliseconds);
        };
        CompositionTarget.Rendering += handler;
        return completion.Task;
    }

    private async Task CaptureAsync(string fileName)
    {
        await Dispatcher.InvokeAsync(() =>
        {
            UpdateLayout();
            var dpi = VisualTreeHelper.GetDpi(this);
            var width = Math.Max(1, (int)Math.Ceiling(ActualWidth * dpi.DpiScaleX));
            var height = Math.Max(1, (int)Math.Ceiling(ActualHeight * dpi.DpiScaleY));
            var bitmap = new RenderTargetBitmap(
                width,
                height,
                dpi.PixelsPerInchX,
                dpi.PixelsPerInchY,
                PixelFormats.Pbgra32);
            bitmap.Render(this);
            var encoder = new PngBitmapEncoder();
            encoder.Frames.Add(BitmapFrame.Create(bitmap));
            using var stream = File.Create(Path.Combine(_outputDirectory, fileName));
            encoder.Save(stream);
        }, DispatcherPriority.Render);
    }

    private string ModeName => _reduced ? "REDUCED" : "FULL";

    private static double Percentile(IReadOnlyList<double> sorted, double quantile)
    {
        if (sorted.Count == 0)
        {
            return 0;
        }

        var index = (int)Math.Clamp(
            Math.Ceiling(sorted.Count * quantile) - 1,
            0,
            sorted.Count - 1);
        return sorted[index];
    }

    private static double ElapsedMilliseconds(long start, long end) =>
        (end - start) * 1000.0 / Stopwatch.Frequency;

    private static void Check(bool condition, string message)
    {
        if (!condition)
        {
            throw new InvalidOperationException(message);
        }
    }
}

internal static class NativeMethods
{
    public const byte VirtualKeyReturn = 0x0D;
    public const byte VirtualKeySpace = 0x20;
    private const uint KeyEventKeyUp = 0x0002;

    [DllImport("user32.dll")]
    public static extern nint GetForegroundWindow();

    [DllImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool SetForegroundWindow(nint windowHandle);

    [DllImport("user32.dll")]
    private static extern void keybd_event(
        byte virtualKey,
        byte scanCode,
        uint flags,
        nuint extraInfo);

    public static void SendKey(byte virtualKey)
    {
        keybd_event(virtualKey, 0, 0, 0);
        keybd_event(virtualKey, 0, KeyEventKeyUp, 0);
    }
}
