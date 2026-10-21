using System.Diagnostics;
using System.Security.Cryptography;
using System.Text.Json;
using System.Windows;
using System.Windows.Interop;

namespace UniversalCouncil.CommandCenter.UiSmoke;

internal static partial class Program
{
    private const int WgcPilotSampleFrames = 30;

    private static int RunWindowsGraphicsCapturePilot(string output)
    {
        Directory.CreateDirectory(output);
        var candidateSha = Environment.GetEnvironmentVariable("CANDIDATE_SHA")?.Trim().ToLowerInvariant() ?? "unknown";
        var reportPath = Path.Combine(output, "wgc-pilot-report.json");
        var callDurations = new List<double>();
        var frameHashes = new List<string>();
        var capturedWidths = new List<int>();
        var capturedHeights = new List<int>();
        var errors = new List<string>();
        var sourceId = "WgcSharp-1.1.1/WGC_ONLY";
        var overallClock = Stopwatch.StartNew();

        Window? window = null;
        try
        {
            Environment.SetEnvironmentVariable("UNIVERSALCOUNCIL_MOTION_EVIDENCE", "full");
            window = App.CreateMainWindow(AppContext.BaseDirectory);
            ConfigureMotionEvidenceWindow(window);
            window.WindowStyle = WindowStyle.None;
            window.ResizeMode = ResizeMode.NoResize;
            window.ShowInTaskbar = false;
            window.WindowStartupLocation = WindowStartupLocation.Manual;
            window.Left = 0;
            window.Top = 0;
            window.Width = MotionWidth;
            window.Height = MotionHeight;
            window.Show();
            PumpDispatcher(TimeSpan.FromMilliseconds(250));

            var hwnd = new WindowInteropHelper(window).Handle;
            if (hwnd == IntPtr.Zero)
            {
                throw new InvalidOperationException("WGC pilot could not obtain the real Command Center HWND.");
            }

            using IMotionEvidenceCaptureSource source = new WgcSharpWindowCaptureSource(hwnd);
            sourceId = source.SourceId;

            for (var index = 0; index < WgcPilotSampleFrames; index++)
            {
                if (index == 10)
                {
                    NavigateForEvidence(window, "ProjectWorkspace");
                    PumpDispatcher(TimeSpan.FromMilliseconds(80));
                }
                else if (index == 20)
                {
                    NavigateForEvidence(window, "DecisionMode");
                    PumpDispatcher(TimeSpan.FromMilliseconds(80));
                }

                var captureClock = Stopwatch.StartNew();
                try
                {
                    var frame = source.CaptureFrame();
                    captureClock.Stop();
                    callDurations.Add(captureClock.Elapsed.TotalMilliseconds);
                    capturedWidths.Add(frame.Width);
                    capturedHeights.Add(frame.Height);
                    frameHashes.Add(Convert.ToHexString(SHA256.HashData(frame.Pixels)).ToLowerInvariant());
                }
                catch (Exception ex)
                {
                    captureClock.Stop();
                    callDurations.Add(captureClock.Elapsed.TotalMilliseconds);
                    errors.Add($"{ex.GetType().Name}: {ex.Message}");
                    break;
                }
            }
        }
        catch (Exception ex)
        {
            errors.Add($"{ex.GetType().Name}: {ex.Message}");
        }
        finally
        {
            overallClock.Stop();
            if (window is not null)
            {
                try
                {
                    window.Close();
                }
                catch
                {
                }
            }
        }

        var successfulFrames = frameHashes.Count;
        var elapsedSeconds = Math.Max(overallClock.Elapsed.TotalSeconds, 0.000001);
        var achievedFps = successfulFrames / elapsedSeconds;
        var dimensionsExact = successfulFrames > 0 &&
            capturedWidths.All(width => width == MotionWidth) &&
            capturedHeights.All(height => height == MotionHeight);
        var sustainedThirtyFps = successfulFrames == WgcPilotSampleFrames && achievedFps >= MotionFramesPerSecond;
        var distinctFrames = frameHashes.Distinct(StringComparer.Ordinal).Count();

        static double Percentile95(IReadOnlyList<double> values)
        {
            if (values.Count == 0)
            {
                return 0;
            }

            var ordered = values.OrderBy(value => value).ToArray();
            var index = Math.Min(
                ordered.Length - 1,
                (int)Math.Ceiling(ordered.Length * 0.95) - 1);
            return ordered[Math.Max(0, index)];
        }

        var payload = new
        {
            schema_version = "1.0",
            pilot_id = "CC-MOTION-W1-1-WGC-PILOT-2026-10-22",
            candidate_sha = candidateSha,
            scope = "EVIDENCE_CAPTURE_ONLY",
            source = sourceId,
            capture_strategy = "WGC_ONLY",
            silent_dxgi_fallback = false,
            dependency = new
            {
                package = "WgcSharp",
                version = "1.1.1",
                upstream_commit = "16450f1fade51ed13bcfaa2555bcb4ddd4019dd3",
                license = "MIT",
                adoption = "PILOT_ONLY",
            },
            source_audit = new
            {
                public_api_shape = "ONE_D3D_DEVICE_AND_WGC_SESSION_PER_CAPTURE_CALL",
                skips_first_frame = true,
                fixed_wait_after_first_frame_ms = 50,
                interpretation = "DIRECT_PER_FRAME_API_MUST_PROVE_30FPS_BEFORE_ADOPTION",
            },
            target = new
            {
                width = MotionWidth,
                height = MotionHeight,
                fps = MotionFramesPerSecond,
                sample_frames = WgcPilotSampleFrames,
            },
            result = new
            {
                successful_frames = successfulFrames,
                distinct_frame_hashes = distinctFrames,
                elapsed_seconds = Math.Round(elapsedSeconds, 3),
                achieved_fps = Math.Round(achievedFps, 3),
                mean_capture_call_ms = callDurations.Count == 0 ? 0 : Math.Round(callDurations.Average(), 3),
                p95_capture_call_ms = Math.Round(Percentile95(callDurations), 3),
                max_capture_call_ms = callDurations.Count == 0 ? 0 : Math.Round(callDurations.Max(), 3),
                dimensions_exact_1440x900 = dimensionsExact,
                sustained_30fps = sustainedThirtyFps,
                errors,
            },
            decision = sustainedThirtyFps && dimensionsExact && errors.Count == 0
                ? "PASS_CANDIDATE_FOR_CONTINUOUS_RECORDER"
                : "FAIL_PUBLIC_API_NOT_SUITABLE_FOR_GOVERNED_30FPS_RECORDER",
            protected_truth = new
            {
                authoritative_stage = "STAGE_7",
                stage8_opened = false,
                runtime_authority = false,
                live_execution = false,
                motion_dna_changed = false,
                thresholds_changed = false,
                w1_2_started = false,
                merge_authorized = false,
            },
        };

        File.WriteAllText(
            reportPath,
            JsonSerializer.Serialize(payload, new JsonSerializerOptions { WriteIndented = true }));

        Console.WriteLine(
            $"W1.1 WGC pilot: {payload.decision} " +
            $"({successfulFrames}/{WgcPilotSampleFrames} frames, {achievedFps:F2} fps, exact={dimensionsExact})");

        // This is a diagnostic pilot. A negative result is evidence for the next
        // governed decision, not a reason to hide or reinterpret the current P1 gate.
        return 0;
    }
}
