using System.Diagnostics;
using UniversalCouncil.MotionKit.Core;
using UniversalCouncil.MotionKit.Runtime;
using UniversalCouncil.MotionKit.SkiaLab;

var now = new DateTimeOffset(2026, 10, 23, 3, 0, 0, TimeSpan.Zero);
var resolver = new MotionProfileResolver(
    new MotionProductProfile(
        "skia-lab-profile",
        new Dictionary<string, MotionVisualRule>(StringComparer.Ordinal)
        {
            ["ROUTE_TRANSFER"] = new(
                "ROUTE_TRANSFER",
                new MotionVisualVariant(
                    "ROUTE_TRANSFER_FULL",
                    TimeSpan.FromMilliseconds(320),
                    MotionRenderCapability.PathGeometry
                    | MotionRenderCapability.DynamicDrawing
                    | MotionRenderCapability.Opacity),
                new MotionVisualVariant(
                    "ROUTE_TRANSFER_REDUCED",
                    TimeSpan.Zero,
                    MotionRenderCapability.StaticSettle))
        }));

await CheckDeterministicFrameAsync();
await CheckReducedVariantAsync();
await CheckUnsupportedStatefulVectorAsync();
await CheckLifecycleAsync();
await ObserveBatchCostAsync();

Console.WriteLine("MotionKit Skia compatibility lab validation: PASS");

async Task CheckDeterministicFrameAsync()
{
    await using var renderer = new SkiaOffscreenLabAdapter();

    var first = Command(
        Guid.Parse("41000000-0000-0000-0000-000000000001"),
        MotionAccessibilityMode.Full);
    var second = Command(
        Guid.Parse("41000000-0000-0000-0000-000000000002"),
        MotionAccessibilityMode.Full);

    var firstStart = await renderer.BeginAsync(first);
    var secondStart = await renderer.BeginAsync(second);

    Check(firstStart.Status == MotionRenderStatus.Started, "first Skia command should start");
    Check(secondStart.Status == MotionRenderStatus.Started, "second Skia command should start");

    Check(renderer.TryGetFrameHash(first.Identity.InstanceId, out var firstHash), "first frame hash missing");
    Check(renderer.TryGetFrameHash(second.Identity.InstanceId, out var secondHash), "second frame hash missing");
    Check(firstHash.Length == 64, "frame hash must be SHA-256 hex");
    Check(firstHash == secondHash, "same visual command must produce deterministic frame bytes");

    _ = await renderer.CancelAsync(first.Identity.InstanceId, "lab cleanup");
    _ = await renderer.CancelAsync(second.Identity.InstanceId, "lab cleanup");
}

async Task CheckReducedVariantAsync()
{
    await using var renderer = new SkiaOffscreenLabAdapter();

    var full = Command(
        Guid.Parse("41000000-0000-0000-0000-000000000003"),
        MotionAccessibilityMode.Full);
    var reduced = Command(
        Guid.Parse("41000000-0000-0000-0000-000000000004"),
        MotionAccessibilityMode.Reduced);

    _ = await renderer.BeginAsync(full);
    _ = await renderer.BeginAsync(reduced);

    Check(renderer.TryGetFrameHash(full.Identity.InstanceId, out var fullHash), "full frame hash missing");
    Check(renderer.TryGetFrameHash(reduced.Identity.InstanceId, out var reducedHash), "reduced frame hash missing");
    Check(fullHash != reducedHash, "Full and Reduced variants must remain distinguishable lab outputs");

    _ = await renderer.SettleAsync(full.Identity.InstanceId, MotionSettleMode.Final);
    _ = await renderer.SettleAsync(reduced.Identity.InstanceId, MotionSettleMode.StaticFallback);
}

async Task CheckUnsupportedStatefulVectorAsync()
{
    await using var renderer = new SkiaOffscreenLabAdapter();

    var command = Command(
        Guid.Parse("41000000-0000-0000-0000-000000000005"),
        MotionAccessibilityMode.Full)
        with
        {
            RequiredCapabilities = MotionRenderCapability.StatefulVector
        };

    var result = await renderer.BeginAsync(command);
    Check(
        result.Status == MotionRenderStatus.NotSupported,
        "Skia lab must not claim STATEFUL_VECTOR without evidence");
}

async Task CheckLifecycleAsync()
{
    await using var renderer = new SkiaOffscreenLabAdapter();

    var command = Command(
        Guid.Parse("41000000-0000-0000-0000-000000000006"),
        MotionAccessibilityMode.Full);

    var started = await renderer.BeginAsync(command);
    Check(started.AdapterVersion == SkiaOffscreenLabAdapter.LabAdapterVersion, "Skia adapter version evidence drifted");

    var duplicate = await renderer.BeginAsync(command);
    Check(duplicate.Status == MotionRenderStatus.DuplicateInstance, "duplicate Skia instance must fail closed");

    var settled = await renderer.SettleAsync(command.Identity.InstanceId, MotionSettleMode.Final);
    Check(settled.Status == MotionRenderStatus.Settled, "Skia lab settle failed");
    Check(!renderer.TryGetFrameHash(command.Identity.InstanceId, out _), "settled frame must be released");

    var diagnostics = renderer.SnapshotDiagnostics();
    Check(diagnostics.ActiveCount == 0, "Skia lab leaked active render state");
    Check(diagnostics.StartedCount == 1, "Skia lab start diagnostics drifted");
    Check(diagnostics.DuplicateCount == 1, "Skia lab duplicate diagnostics drifted");
}

async Task ObserveBatchCostAsync()
{
    await using var renderer = new SkiaOffscreenLabAdapter();
    var stopwatch = Stopwatch.StartNew();

    for (var index = 0; index < 100; index++)
    {
        var command = Command(
            Guid.Parse($"42000000-0000-0000-0000-{index + 1:D12}"),
            MotionAccessibilityMode.Full);
        var started = await renderer.BeginAsync(command);
        Check(started.Status == MotionRenderStatus.Started, $"batch render {index} failed");
        _ = await renderer.SettleAsync(command.Identity.InstanceId, MotionSettleMode.Final);
    }

    stopwatch.Stop();
    Check(renderer.SnapshotDiagnostics().ActiveCount == 0, "batch observation leaked active instances");

    Console.WriteLine(
        $"Skia lab informational timing: 100 offscreen frames in {stopwatch.Elapsed.TotalMilliseconds:F2} ms (shared CI; non-gating)");
}

MotionRenderCommand Command(Guid instanceId, MotionAccessibilityMode mode)
{
    var lease = new MotionLease(
        instanceId,
        $"request:{instanceId:N}",
        "route:lab",
        "ROUTE_TRANSFER",
        "ROUTE_EVENT_EXISTS",
        "lab-state-v1",
        now,
        mode,
        now);

    var prepared = resolver.Resolve(lease);
    return prepared.Command
        ?? throw new InvalidOperationException($"Skia lab command failed to resolve: {prepared.Reason}");
}

void Check(bool condition, string message)
{
    if (!condition)
    {
        throw new InvalidOperationException(message);
    }
}
