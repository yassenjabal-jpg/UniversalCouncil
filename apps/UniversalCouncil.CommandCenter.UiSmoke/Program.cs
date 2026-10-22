using System.IO;
using System.Reflection;
using System.Security.Cryptography;
using System.Text.Json;
using System.Windows;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using UniversalCouncil.CommandCenter;

namespace UniversalCouncil.CommandCenter.UiSmoke;

internal static partial class Program
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

        var ownerTailnetPath = Path.Combine(
            AppContext.BaseDirectory,
            "state",
            "owner-device-tailnet.json");

        if (!File.Exists(statePath) ||
            !File.Exists(orchestrationPath) ||
            !File.Exists(executionFabricPath) ||
            !File.Exists(remoteOwnerPath) ||
            !File.Exists(remoteTransportPath) ||
            !File.Exists(ownerTailnetPath))
        {
            throw new InvalidOperationException(
                "Stage 7 UI evidence requires operational + orchestration + execution + remote owner + transport + owner-tailnet state.");
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
        var ownerTailnetBytes = File.ReadAllBytes(ownerTailnetPath);
        var ownerTailnetSha256 = Convert.ToHexString(
            SHA256.HashData(ownerTailnetBytes)).ToLowerInvariant();

        var app = new App
        {
            ShutdownMode = ShutdownMode.OnExplicitShutdown,
        };
        app.InitializeComponent();

        if (args.Any(arg => string.Equals(arg, "--wgc-motion-evidence", StringComparison.OrdinalIgnoreCase)))
        {
            var reducedMotion = args.Any(
                arg => string.Equals(arg, "--reduced-motion", StringComparison.OrdinalIgnoreCase));
            return RenderWgcMotionEvidence(output, reducedMotion);
        }

        if (args.Any(arg => string.Equals(arg, "--wgc-pilot", StringComparison.OrdinalIgnoreCase)))
        {
            return RunWindowsGraphicsCapturePilot(output);
        }

        if (args.Any(arg => string.Equals(arg, "--motion-evidence", StringComparison.OrdinalIgnoreCase)))
        {
            var reducedMotion = args.Any(
                arg => string.Equals(arg, "--reduced-motion", StringComparison.OrdinalIgnoreCase));
            return RenderMotionEvidence(output, reducedMotion);
        }

        var evidence = new[]
        {
            Render(output, 1440, 900, "command-center-stage7-1440x900.png", "native"),
            Render(output, 1180, 720, "command-center-stage7-1180x720.png", "native"),
            Render(output, 1440, 900, "home-reference-only-1440x900.png", "reference"),
            Render(output, 1440, 900, "home-native-1440x900.png", "native"),
            Render(output, 1440, 900, "home-native-overlay-1440x900.png", "blend"),
            Render(
                output,
                1440,
                900,
                "project-workspace-reference-1440x900.png",
                "reference",
                "ProjectWorkspace"),
            Render(
                output,
                1440,
                900,
                "project-workspace-native-1440x900.png",
                "native",
                "ProjectWorkspace"),
            Render(
                output,
                1440,
                900,
                "project-workspace-blend-1440x900.png",
                "blend",
                "ProjectWorkspace"),
            Render(
                output,
                1440,
                900,
                "software-autopilot-reference-1440x900.png",
                "reference",
                "SoftwareAutopilot"),
            Render(
                output,
                1440,
                900,
                "software-autopilot-native-1440x900.png",
                "native",
                "SoftwareAutopilot"),
            Render(
                output,
                1440,
                900,
                "software-autopilot-blend-1440x900.png",
                "blend",
                "SoftwareAutopilot"),
            Render(
                output,
                1440,
                900,
                "studio-project-reference-1440x900.png",
                "reference",
                "StudioProject"),
            Render(
                output,
                1440,
                900,
                "studio-project-native-1440x900.png",
                "native",
                "StudioProject"),
            Render(
                output,
                1440,
                900,
                "studio-project-blend-1440x900.png",
                "blend",
                "StudioProject"),
            Render(
                output,
                1440,
                900,
                "owner-decision-reference-1440x900.png",
                "reference",
                "DecisionMode"),
            Render(
                output,
                1440,
                900,
                "owner-decision-native-1440x900.png",
                "native",
                "DecisionMode"),
            Render(
                output,
                1440,
                900,
                "owner-decision-blend-1440x900.png",
                "blend",
                "DecisionMode"),
            Render(
                output,
                1440,
                900,
                "recovery-fork-reference-1440x900.png",
                "reference",
                "RecoveryFork"),
            Render(
                output,
                1440,
                900,
                "recovery-fork-native-1440x900.png",
                "native",
                "RecoveryFork"),
            Render(
                output,
                1440,
                900,
                "recovery-fork-blend-1440x900.png",
                "blend",
                "RecoveryFork"),
            Render(
                output,
                1440,
                900,
                "pulse-story-reference-1440x900.png",
                "reference",
                "PulseStory"),
            Render(
                output,
                1440,
                900,
                "pulse-story-native-1440x900.png",
                "native",
                "PulseStory"),
            Render(
                output,
                1440,
                900,
                "pulse-story-blend-1440x900.png",
                "blend",
                "PulseStory"),
            Render(
                output,
                1440,
                900,
                "work-receipt-reference-1440x900.png",
                "reference",
                "WorkReceipt"),
            Render(
                output,
                1440,
                900,
                "work-receipt-native-1440x900.png",
                "native",
                "WorkReceipt"),
            Render(
                output,
                1440,
                900,
                "work-receipt-blend-1440x900.png",
                "blend",
                "WorkReceipt"),
        };

        var manifestPath = Path.Combine(output, "ui-evidence-manifest.json");
        File.WriteAllText(
            manifestPath,
            JsonSerializer.Serialize(
                new
                {
                    schema_version = "1.0",
                    stage = "COMMAND_CENTER_STAGE7_OWNER_DEVICE_TAILNET",
                    generated_at_utc = DateTimeOffset.UtcNow,
                    render_mode = "OFFSCREEN_WPF_CONTENT",
                    operational_state_sha256 = stateSha256,
                    orchestration_catalog_sha256 = orchestrationSha256,
                    execution_fabric_sha256 = executionFabricSha256,
                    remote_owner_gateway_sha256 = remoteOwnerSha256,
                    remote_transport_sha256 = remoteTransportSha256,
                    owner_device_tailnet_sha256 = ownerTailnetSha256,
                    evidence,
                },
                new JsonSerializerOptions { WriteIndented = true }));

        Console.WriteLine($"Command Center Stage 7 UI smoke: PASS ({output})");
        return 0;
    }

    private static void NavigateForEvidence(MainWindow window, string screenName)
    {
        var windowType = typeof(MainWindow);
        var screenType = windowType.GetNestedType(
            "ScreenKind",
            BindingFlags.NonPublic);
        var navigate = windowType.GetMethod(
            "NavigateTo",
            BindingFlags.Instance | BindingFlags.NonPublic);

        if (screenType is null || navigate is null)
        {
            throw new InvalidOperationException(
                "Unable to locate private screen navigation for UI evidence.");
        }

        var screen = Enum.Parse(screenType, screenName, ignoreCase: false);
        navigate.Invoke(window, new[] { screen });
    }

    private static object Render(
        string output,
        int width,
        int height,
        string fileName,
        string variant,
        string? screen = null)
    {
        var window = App.CreateMainWindow(AppContext.BaseDirectory);

        if (!string.IsNullOrWhiteSpace(screen))
        {
            NavigateForEvidence(window, screen);
        }

        if (window.FindName("ReferenceImage") is UIElement referenceImage)
        {
            referenceImage.Visibility = variant == "native"
                ? Visibility.Collapsed
                : Visibility.Visible;
        }

        if (window.FindName("InteractionCanvas") is UIElement homeInteractionLayer)
        {
            homeInteractionLayer.Visibility = Visibility.Collapsed;
        }

        if (window.FindName("NativeHomeReconstructionRoot") is UIElement nativeHomeLayer)
        {
            if (!string.IsNullOrWhiteSpace(screen))
            {
                nativeHomeLayer.Visibility = Visibility.Collapsed;
            }
            else
            {
                switch (variant)
                {
                    case "reference":
                        nativeHomeLayer.Visibility = Visibility.Collapsed;
                        break;
                    case "blend":
                        nativeHomeLayer.Visibility = Visibility.Visible;
                        nativeHomeLayer.Opacity = 0.46;
                        break;
                    default:
                        nativeHomeLayer.Visibility = Visibility.Visible;
                        nativeHomeLayer.Opacity = 1;
                        break;
                }
            }
        }

        if (window.FindName("SecondaryInteractionCanvas") is UIElement secondaryInteractionLayer)
        {
            secondaryInteractionLayer.Visibility = Visibility.Collapsed;
        }

        if (window.FindName("SecondaryNativeLayer") is UIElement secondaryNativeLayer &&
            !string.IsNullOrWhiteSpace(screen))
        {
            switch (variant)
            {
                case "reference":
                    secondaryNativeLayer.Visibility = Visibility.Collapsed;
                    break;
                case "blend":
                    secondaryNativeLayer.Visibility = Visibility.Visible;
                    secondaryNativeLayer.Opacity = 0.46;
                    break;
                default:
                    secondaryNativeLayer.Visibility = Visibility.Visible;
                    secondaryNativeLayer.Opacity = 1;
                    break;
            }
        }

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
            variant,
        };
    }
}
