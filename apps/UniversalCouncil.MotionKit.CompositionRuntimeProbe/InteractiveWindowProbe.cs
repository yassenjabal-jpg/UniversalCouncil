using System.IO;
using System.Numerics;
using System.Text.Json;
using System.Windows;
using System.Windows.Interop;
using System.Windows.Threading;
using Microsoft.UI.Composition;
using Microsoft.UI.Content;
using Microsoft.UI.Dispatching;

namespace UniversalCouncil.MotionKit.CompositionRuntimeProbe;

internal static class InteractiveWindowProbe
{
    public static int Run(string output)
    {
        Directory.CreateDirectory(output);
        var queue = DispatcherQueueController.CreateOnCurrentThread();
        using var compositor = new Compositor();
        using var root = compositor.CreateContainerVisual();
        using var sprite = compositor.CreateSpriteVisual();
        using var brush = compositor.CreateColorBrush(Windows.UI.Color.FromArgb(255, 0, 190, 220));
        sprite.Size = new Vector2(120, 120);
        sprite.Offset = new Vector3(60, 120, 0);
        sprite.Brush = brush;
        root.Children.InsertAtTop(sprite);
        using var animation = compositor.CreateScalarKeyFrameAnimation();
        animation.InsertKeyFrame(0, 0.15f);
        animation.InsertKeyFrame(0.5f, 1f);
        animation.InsertKeyFrame(1, 0.15f);
        animation.Duration = TimeSpan.FromSeconds(2);
        animation.IterationBehavior = AnimationIterationBehavior.Forever;
        var window = new Window {
            Title = "MotionKit MP3 | Composition WPF interactive",
            Width = 640, Height = 440, WindowStartupLocation = WindowStartupLocation.CenterScreen
        };
        ContentIsland? island = null;
        DesktopChildSiteBridge? bridge = null;
        var ticks = 0;
        var timer = new DispatcherTimer { Interval = TimeSpan.FromSeconds(1) };
        window.SourceInitialized += (_, _) => {
            island = ContentIsland.Create(root);
            bridge = DesktopChildSiteBridge.Create(compositor,
                Microsoft.UI.Win32Interop.GetWindowIdFromWindow(new WindowInteropHelper(window).Handle));
            bridge.ResizePolicy = ContentSizePolicy.ResizeContentToParentWindow;
            bridge.Connect(island);
            bridge.Show();
            sprite.StartAnimation("Opacity", animation);
            timer.Start();
        };
        timer.Tick += (_, _) => {
            ticks++;
            if (ticks == 12) {
                sprite.StopAnimation("Opacity");
                sprite.Opacity = 1;
                window.Title = "MotionKit MP3 | Composition REDUCED static settle";
            }
            if (ticks != 16) return;
            timer.Stop();
            File.WriteAllText(Path.Combine(output, "composition-window.json"),
                JsonSerializer.Serialize(new {
                    machine = Environment.MachineName, utc = DateTimeOffset.UtcNow,
                    interactive = Environment.UserInteractive, visible = window.IsVisible,
                    connected = bridge!.SiteView.IsConnected, timer_ticks = ticks,
                    full = "Composition scalar opacity animation, 2 second repeating timeline",
                    reduced = "StopAnimation then direct opacity=1; four second static dwell",
                    production_adoption = false, gpu_frame_pacing_measured = false
                }, new JsonSerializerOptions { WriteIndented = true }));
            bridge.Dispose();
            island!.Dispose();
            window.Close();
        };
        new Application().Run(window);
        // WPF owns the message pump. All child windows and islands are closed first.
        queue.ShutdownQueue();
        if (ticks != 16) throw new InvalidOperationException("Window closed before probe completed.");
        Console.WriteLine("Composition WPF interactive: PASS (ContentIsland, Full/Reduced, normal close)");
        return 0;
    }
}
