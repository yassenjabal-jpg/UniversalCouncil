using System.Diagnostics;
using System.IO;
using System.Text.Json;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media.Imaging;
using System.Windows.Threading;

namespace UniversalCouncil.MotionKit.SkiaWpfCompileProbe;

internal static class Program
{
    [STAThread]
    private static int Main(string[] args)
    {
        if (args.Length != 1) throw new ArgumentException("Supply evidence output directory.");
        Directory.CreateDirectory(args[0]);
        var samples = new List<double>();
        var image = new Image { Width = 256, Height = 256, Source = SkiaWpfProbe.CreateBitmapSource() };
        var window = new Window {
            Title = "MotionKit MP3 | Skia WPF reference bridge",
            Width = 640, Height = 440, WindowStartupLocation = WindowStartupLocation.CenterScreen,
            Background = System.Windows.Media.Brushes.DarkSlateGray, Content = image
        };
        var timer = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(16) };
        var clock = new Stopwatch();
        var previous = 0d;
        timer.Tick += (_, _) => {
            var now = clock.Elapsed.TotalMilliseconds;
            samples.Add(now - previous);
            previous = now;
            image.Source = SkiaWpfProbe.CreateBitmapSource();
            if (samples.Count != 600) return;
            timer.Stop();
            var bitmap = (BitmapSource)image.Source;
            var encoder = new PngBitmapEncoder();
            encoder.Frames.Add(BitmapFrame.Create(bitmap));
            using (var stream = File.Create(Path.Combine(args[0], "skia-bridge.png"))) encoder.Save(stream);
            samples.Sort();
            File.WriteAllText(Path.Combine(args[0], "skia-window.json"), JsonSerializer.Serialize(new {
                machine = Environment.MachineName, utc = DateTimeOffset.UtcNow,
                interactive = Environment.UserInteractive, process_session = Process.GetCurrentProcess().SessionId,
                visible = window.IsVisible, samples = samples.Count,
                median_dispatch_interval_ms = samples[samples.Count / 2],
                p95_dispatch_interval_ms = samples[(int)(samples.Count * 0.95)],
                measurement = "WPF dispatcher cadence; NOT GPU presentation or product animation",
                gating = false, bridge_pixel_width = bitmap.PixelWidth, bridge_pixel_height = bitmap.PixelHeight
            }, new JsonSerializerOptions { WriteIndented = true }));
            window.Close();
        };
        window.ContentRendered += (_, _) => { clock.Start(); timer.Start(); };
        new Application().Run(window);
        if (samples.Count != 600) throw new InvalidOperationException("Window closed before probe completed.");
        Console.WriteLine("Skia WPF bridge: PASS (600 pixel bridge updates; normal window close)");
        return 0;
    }
}
