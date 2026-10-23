using System.Diagnostics;
using System.IO;
using System.Text.Json;
using System.Windows;
using System.Windows.Threading;
using UniversalCouncil.CommandCenter;

namespace UniversalCouncil.CommandCenter.UiSmoke;

internal static partial class Program
{
    private sealed record MotionDriverStepEvidence(
        int Frame,
        string Name,
        double TargetSeconds,
        double ActualSeconds,
        double LatenessMs);

    private static int RunMotionDriver(
        string output,
        bool reducedMotion,
        bool mp4Reference)
    {
        var mode = reducedMotion ? "reduced" : "full";
        var candidateSha = Environment.GetEnvironmentVariable("CANDIDATE_SHA")?.Trim().ToLowerInvariant() ?? "unknown";
        var targetSeconds = mp4Reference ? 12 : reducedMotion ? 28 : 38;
        var steps = mp4Reference ? BuildMp4MotionSteps() : BuildMotionSteps(reducedMotion);

        Environment.SetEnvironmentVariable(
            "UNIVERSALCOUNCIL_MOTION_EVIDENCE",
            reducedMotion ? "reduced" : "full");

        Directory.CreateDirectory(output);
        MainWindow? window = null;

        try
        {
            window = App.CreateMainWindow(AppContext.BaseDirectory);
            SynchronizationContext.SetSynchronizationContext(
                new DispatcherSynchronizationContext(window.Dispatcher));
            ConfigureMotionEvidenceWindow(window);

            window.WindowStyle = WindowStyle.None;
            window.ResizeMode = ResizeMode.NoResize;
            window.ShowInTaskbar = true;
            window.WindowStartupLocation = WindowStartupLocation.Manual;
            window.Left = 0;
            window.Top = 0;
            window.Width = MotionWidth;
            window.Height = MotionHeight;
            window.Topmost = true;
            window.Show();
            PumpDispatcher(TimeSpan.FromMilliseconds(500));

            var readyFile = Environment.GetEnvironmentVariable("MOTION_DRIVER_READY_FILE");
            if (!string.IsNullOrWhiteSpace(readyFile))
            {
                var readyPath = Path.GetFullPath(readyFile);
                var readyDirectory = Path.GetDirectoryName(readyPath);
                if (!string.IsNullOrWhiteSpace(readyDirectory))
                {
                    Directory.CreateDirectory(readyDirectory);
                }

                File.WriteAllText(
                    readyPath,
                    JsonSerializer.Serialize(
                        new
                        {
                            schema_version = "1.0",
                            process_id = Environment.ProcessId,
                            window_title = window.Title,
                            target_seconds = targetSeconds,
                            mode,
                            mp4_reference = mp4Reference,
                            width = MotionWidth,
                            height = MotionHeight,
                        },
                        new JsonSerializerOptions { WriteIndented = true }));
            }

            var goFile = Environment.GetEnvironmentVariable("MOTION_DRIVER_GO_FILE");
            if (!string.IsNullOrWhiteSpace(goFile))
            {
                var goPath = Path.GetFullPath(goFile);
                var waitClock = Stopwatch.StartNew();
                while (!File.Exists(goPath) && waitClock.Elapsed < TimeSpan.FromSeconds(60))
                {
                    PumpDispatcher(TimeSpan.FromMilliseconds(10));
                }

                if (!File.Exists(goPath))
                {
                    throw new TimeoutException(
                        "Motion driver did not receive the external capture GO signal.");
                }
            }

            var clock = Stopwatch.StartNew();
            var evidence = new List<MotionDriverStepEvidence>(steps.Count);
            var targetDuration = TimeSpan.FromSeconds(targetSeconds);
            var scheduler = Task.Factory.StartNew(
                () =>
                {
                    try
                    {
                        Thread.CurrentThread.Priority = ThreadPriority.AboveNormal;
                    }
                    catch
                    {
                        // Timing hardening only; lack of priority elevation is not fatal.
                    }

                    foreach (var step in steps)
                    {
                        var target = TimeSpan.FromSeconds(
                            (double)step.Frame / MotionFramesPerSecond);
                        PaceWorkerToCaptureTime(clock, target);

                        window.Dispatcher.Invoke(
                            DispatcherPriority.Send,
                            new Action(() =>
                            {
                                step.Execute(window);
                                var actualSeconds = clock.Elapsed.TotalSeconds;
                                var targetStepSeconds = target.TotalSeconds;
                                evidence.Add(
                                    new MotionDriverStepEvidence(
                                        step.Frame,
                                        step.Name,
                                        Math.Round(targetStepSeconds, 6),
                                        Math.Round(actualSeconds, 6),
                                        Math.Round(
                                            Math.Max(0, actualSeconds - targetStepSeconds) * 1000,
                                            3)));

                                Console.WriteLine(
                                    $"Motion driver [{mode}] step @{step.Frame}: {step.Name}");
                            }));
                    }

                    PaceWorkerToCaptureTime(clock, targetDuration);
                },
                CancellationToken.None,
                TaskCreationOptions.LongRunning,
                TaskScheduler.Default);

            PumpDispatcherUntilComplete(scheduler);
            clock.Stop();
            var maxLateness = evidence.Count == 0
                ? 0
                : evidence.Max(item => item.LatenessMs);

            File.WriteAllText(
                Path.Combine(output, "motion-driver-timing.json"),
                JsonSerializer.Serialize(
                    new
                    {
                        schema_version = "1.1",
                        evidence_type = "WPF_REALTIME_MOTION_DRIVER_TIMING",
                        candidate_sha = candidateSha,
                        clock = "STOPWATCH_REALTIME_WPF_DRIVER",
                        timing_authority = true,
                        capture_observer = false,
                        scheduler = "DEDICATED_STOPWATCH_WORKER_TO_DISPATCHER_SEND",
                        dispatcher_timer_timing_authority = false,
                        scheduler_thread_priority = "ABOVE_NORMAL_BEST_EFFORT",
                        mode,
                        reduced_motion = reducedMotion,
                        mp4_reference = mp4Reference,
                        target_duration_seconds = targetSeconds,
                        actual_duration_seconds = Math.Round(clock.Elapsed.TotalSeconds, 3),
                        frame_rate = MotionFramesPerSecond,
                        window_title = window.Title,
                        width = MotionWidth,
                        height = MotionHeight,
                        max_step_lateness_ms = Math.Round(maxLateness, 3),
                        steps = evidence,
                    },
                    new JsonSerializerOptions { WriteIndented = true }));

            Console.WriteLine(
                $"Command Center motion driver [{mode}] PASS " +
                $"({targetSeconds}s target, {clock.Elapsed.TotalSeconds:F3}s actual, " +
                $"max-step-late={maxLateness:F3}ms)");
            return 0;
        }
        finally
        {
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
    }
}
