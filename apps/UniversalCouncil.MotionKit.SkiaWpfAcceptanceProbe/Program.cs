using System.IO;
using System.Diagnostics;
using System.Text.Json;
using System.Windows;

namespace UniversalCouncil.MotionKit.SkiaWpfAcceptanceProbe;

internal static class Program
{
    [STAThread]
    private static int Main(string[] args)
    {
        if (args.Length != 1)
        {
            throw new ArgumentException("Supply evidence output directory.");
        }

        var outputDirectory = Path.GetFullPath(args[0]);
        Directory.CreateDirectory(outputDirectory);
        var previousForeground = NativeMethods.GetForegroundWindow();

        var application = new Application
        {
            ShutdownMode = ShutdownMode.OnLastWindowClose
        };
        var window = new AcceptanceWindow(outputDirectory, previousForeground);
        _ = application.Run(window);

        if (window.Failure is not null)
        {
            throw new InvalidOperationException(
                "MotionKit MP3 reference acceptance failed.",
                window.Failure);
        }

        if (!window.Completed)
        {
            throw new InvalidOperationException(
                "MotionKit MP3 reference acceptance window closed before completion.");
        }

        var results = new List<ScenarioResult>(window.Results)
        {
            new(
                "S2_STATEFUL_SIGIL",
                "ROLE_MATRIX",
                "NOT_APPLICABLE_CURRENT_ACCEPTED_ROLE_SET",
                new Dictionary<string, object?>
                {
                    ["accepted_stateful_vector_renderer"] = false,
                    ["rive_evidence_class"] = "COMPILE_EVIDENCE",
                    ["rive_wpf_runtime"] = false,
                    ["unknown_forward_progress_allowed"] = false,
                    ["decision"] = "Rive remains research-only and unassigned; no custom native wrapper was invented."
                },
                Array.Empty<string>(),
                "S2 becomes mandatory again only if a renderer is assigned STATEFUL_VECTOR runtime responsibility.")
        };

        var process = Process.GetCurrentProcess();
        process.Refresh();
        var report = new
        {
            schema_version = "1.0",
            probe = "MotionKit MP3 reference acceptance",
            candidate = "SkiaSharp 4.153.1 core pixels -> WPF BitmapSource + native WPF input/accessibility surface",
            machine = Environment.MachineName,
            utc = DateTimeOffset.UtcNow,
            interactive = Environment.UserInteractive,
            process_session = process.SessionId,
            os = Environment.OSVersion.VersionString,
            framework = Environment.Version.ToString(),
            processor_count = Environment.ProcessorCount,
            renderer_reentry_count = window.RendererReentryCount,
            s2_policy = "No accepted role claims STATEFUL_VECTOR; Rive remains research-only without a .NET/WPF runtime.",
            performance_policy = "Reference-host measurements are informational until a fixed warmup/sample/threshold policy is approved.",
            owner_visual_acceptance = false,
            production_adoption = false,
            stage8_opened = false,
            results
        };

        var json = JsonSerializer.Serialize(
            report,
            new JsonSerializerOptions { WriteIndented = true });
        File.WriteAllText(
            Path.Combine(outputDirectory, "skia-acceptance.json"),
            json);

        Console.WriteLine(
            "MotionKit MP3 Skia/WPF reference acceptance: PASS "
            + "(S1/S3/S4/S5 Full+Reduced; S2 unassigned research role; normal close/re-entry)");
        return 0;
    }
}
