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

        var orchestrationPath = Path.Combine(
            AppContext.BaseDirectory,
            "state",
            "orchestration-catalog.json");

        var executionFabricPath = Path.Combine(
            AppContext.BaseDirectory,
            "state",
            "execution-fabric.json");

        var remoteOwnerPath = Path.Combine(
            AppContext.BaseDirectory,
            "state",
            "remote-owner-gateway.json");

        var remoteTransportPath = Path.Combine(
            AppContext.BaseDirectory,
            "state",
            "remote-transport.json");

        if (!File.Exists(statePath) ||
            !File.Exists(orchestrationPath) ||
            !File.Exists(executionFabricPath) ||
            !File.Exists(remoteOwnerPath) ||
            !File.Exists(remoteTransportPath))
        {
            throw new InvalidOperationException(
                "Stage 6 UI evidence requires operational + orchestration + execution + remote owner + transport state.");
        }

        var stateBytes = File.ReadAllBytes(statePath);
        var stateSha256 = Convert.ToHexString(SHA256.HashData(stateBytes)).ToLowerInvariant();
        var orchestrationBytes = File.ReadAllBytes(orchestrationPath);
        var orchestrationSha256 = Convert.ToHexString(
            SHA256.HashData(orchestrationBytes)).ToLowerInvariant();
        var executionFabricBytes = File.ReadAllBytes(executionFabricPath);
        var executionFabricSha256 = Convert.ToHexString(
            SHA256.HashData(executionFabricBytes)).ToLowerInvariant();
        var remoteOwnerBytes = File.ReadAllBytes(remoteOwnerPath);
        var remoteOwnerSha256 = Convert.ToHexString(
            SHA256.HashData(remoteOwnerBytes)).ToLowerInvariant();
        var remoteTransportBytes = File.ReadAllBytes(remoteTransportPath);
        var remoteTransportSha256 = Convert.ToHexString(
            SHA256.HashData(remoteTransportBytes)).ToLowerInvariant();

        var app = new App
        {
            ShutdownMode = ShutdownMode.OnExplicitShutdown,
        };
        app.InitializeComponent();

        var evidence = new[]
        {
            Render(output, 1440, 900, "command-center-stage6-1440x900.png"),
            Render(output, 1180, 720, "command-center-stage6-1180x720.png"),
        };

        var manifestPath = Path.Combine(output, "ui-evidence-manifest.json");
        File.WriteAllText(
            manifestPath,
            JsonSerializer.Serialize(
                new
                {
                    schema_version = "1.0",
                    stage = "COMMAND_CENTER_STAGE6_AUTHENTICATED_TRANSPORT_PILOT",
                    generated_at_utc = DateTimeOffset.UtcNow,
                    render_mode = "OFFSCREEN_WPF_CONTENT",
                    operational_state_sha256 = stateSha256,
                    orchestration_catalog_sha256 = orchestrationSha256,
                    execution_fabric_sha256 = executionFabricSha256,
                    remote_owner_gateway_sha256 = remoteOwnerSha256,
                    remote_transport_sha256 = remoteTransportSha256,
                    evidence,
                },
                new JsonSerializerOptions { WriteIndented = true }));

        Console.WriteLine($"Command Center Stage 6 UI smoke: PASS ({output})");
        return 0;
    }

    private static object Render(string output, int width, int height, string fileName)
    {
        var window = App.CreateMainWindow(AppContext.BaseDirectory);

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
