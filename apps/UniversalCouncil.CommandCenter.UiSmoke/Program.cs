using System.IO;
using System.Windows;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using UniversalCouncil.CommandCenter;

namespace UniversalCouncil.CommandCenter.UiSmoke;

internal static class Program
{
    [STAThread]
    private static int Main(string[] args)
    {
        var output = args.Length > 0
            ? Path.GetFullPath(args[0])
            : Path.GetFullPath(Path.Combine("artifacts", "command-center-stage1-ui"));

        Directory.CreateDirectory(output);

        var app = new App();
        app.InitializeComponent();

        Render(output, 1440, 900, "command-center-stage1-1440x900.png");
        Render(output, 1180, 720, "command-center-stage1-1180x720.png");

        Console.WriteLine($"Command Center Stage 1 UI smoke: PASS ({output})");
        return 0;
    }

    private static void Render(string output, int width, int height, string fileName)
    {
        var window = new MainWindow
        {
            Width = width,
            Height = height,
            WindowStartupLocation = WindowStartupLocation.Manual,
            Left = 0,
            Top = 0,
            ShowInTaskbar = false,
        };

        window.Show();
        window.UpdateLayout();

        var dpi = VisualTreeHelper.GetDpi(window);
        var pixelWidth = Math.Max(1, (int)Math.Round(window.ActualWidth * dpi.DpiScaleX));
        var pixelHeight = Math.Max(1, (int)Math.Round(window.ActualHeight * dpi.DpiScaleY));

        var bitmap = new RenderTargetBitmap(
            pixelWidth,
            pixelHeight,
            96 * dpi.DpiScaleX,
            96 * dpi.DpiScaleY,
            PixelFormats.Pbgra32);

        bitmap.Render(window);

        var encoder = new PngBitmapEncoder();
        encoder.Frames.Add(BitmapFrame.Create(bitmap));

        var path = Path.Combine(output, fileName);
        using (var stream = File.Create(path))
        {
            encoder.Save(stream);
        }

        if (!File.Exists(path) || new FileInfo(path).Length < 10_000)
        {
            throw new InvalidOperationException($"UI evidence was not rendered correctly: {path}");
        }

        window.Close();
    }
}
