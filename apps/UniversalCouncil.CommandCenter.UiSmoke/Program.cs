using System.IO;
using System.Security.Cryptography;
using System.Text.Json;
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

        var evidence = new[]
        {
            Render(output, 1440, 900, "command-center-stage1-1440x900.png"),
            Render(output, 1180, 720, "command-center-stage1-1180x720.png"),
        };

        var manifestPath = Path.Combine(output, "ui-evidence-manifest.json");
        File.WriteAllText(
            manifestPath,
            JsonSerializer.Serialize(
                new
                {
                    schema_version = "1.0",
                    stage = "COMMAND_CENTER_STAGE1_SHELL",
                    generated_at_utc = DateTimeOffset.UtcNow,
                    evidence,
                },
                new JsonSerializerOptions { WriteIndented = true }));

        Console.WriteLine($"Command Center Stage 1 UI smoke: PASS ({output})");
        return 0;
    }

    private static object Render(string output, int width, int height, string fileName)
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

        if (pixelWidth < 100 || pixelHeight < 100)
        {
            throw new InvalidOperationException(
                $"UI evidence has implausible dimensions: {pixelWidth}x{pixelHeight}");
        }

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

        var bytes = File.ReadAllBytes(path);
        var pngSignature = new byte[] { 137, 80, 78, 71, 13, 10, 26, 10 };
        if (bytes.Length <= pngSignature.Length || !bytes.AsSpan(0, pngSignature.Length).SequenceEqual(pngSignature))
        {
            throw new InvalidOperationException($"UI evidence is not a valid PNG: {path}");
        }

        var sha256 = Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();

        Console.WriteLine(
            $"Rendered {fileName}: {pixelWidth}x{pixelHeight}, {bytes.Length} bytes, sha256:{sha256}");

        window.Close();

        return new
        {
            file = fileName,
            requested_width = width,
            requested_height = height,
            pixel_width = pixelWidth,
            pixel_height = pixelHeight,
            bytes = bytes.Length,
            sha256,
        };
    }
}
