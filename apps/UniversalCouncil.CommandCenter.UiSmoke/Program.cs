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

        var statePath = Path.Combine(
            AppContext.BaseDirectory,
            "state",
            "command-center-state.json");

        if (!File.Exists(statePath))
        {
            throw new InvalidOperationException(
                $"Stage 2 UI evidence requires operational state source: {statePath}");
        }

        var stateBytes = File.ReadAllBytes(statePath);
        var stateSha256 = Convert.ToHexString(SHA256.HashData(stateBytes)).ToLowerInvariant();

        var app = new App
        {
            ShutdownMode = ShutdownMode.OnExplicitShutdown,
        };
        app.InitializeComponent();

        var evidence = new[]
        {
            Render(output, 1440, 900, "command-center-stage2-1440x900.png"),
            Render(output, 1180, 720, "command-center-stage2-1180x720.png"),
        };

        var manifestPath = Path.Combine(output, "ui-evidence-manifest.json");
        File.WriteAllText(
            manifestPath,
            JsonSerializer.Serialize(
                new
                {
                    schema_version = "1.0",
                    stage = "COMMAND_CENTER_STAGE2_OPERATIONAL_STATE",
                    generated_at_utc = DateTimeOffset.UtcNow,
                    render_mode = "OFFSCREEN_WPF_CONTENT",
                    operational_state_sha256 = stateSha256,
                    evidence,
                },
                new JsonSerializerOptions { WriteIndented = true }));

        Console.WriteLine($"Command Center Stage 2 UI smoke: PASS ({output})");
        return 0;
    }

    private static object Render(string output, int width, int height, string fileName)
    {
        var window = new MainWindow();

        if (window.Content is not FrameworkElement root)
        {
            throw new InvalidOperationException("MainWindow root content is not a FrameworkElement.");
        }

        root.Width = width;
        root.Height = height;
        root.Measure(new Size(width, height));
        root.Arrange(new Rect(0, 0, width, height));
        root.UpdateLayout();

        if (root.ActualWidth < width - 1 || root.ActualHeight < height - 1)
        {
            throw new InvalidOperationException(
                $"Off-screen layout did not reach requested size: {root.ActualWidth}x{root.ActualHeight}");
        }

        var bitmap = new RenderTargetBitmap(
            width,
            height,
            96,
            96,
            PixelFormats.Pbgra32);

        bitmap.Render(root);

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
            $"Rendered {fileName}: {width}x{height}, {bytes.Length} bytes, sha256:{sha256}");

        return new
        {
            file = fileName,
            requested_width = width,
            requested_height = height,
            pixel_width = bitmap.PixelWidth,
            pixel_height = bitmap.PixelHeight,
            bytes = bytes.Length,
            sha256,
        };
    }
}
