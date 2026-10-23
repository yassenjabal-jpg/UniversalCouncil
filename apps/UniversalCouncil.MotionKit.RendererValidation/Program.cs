using UniversalCouncil.MotionKit.Core;
using UniversalCouncil.MotionKit.Runtime;
using UniversalCouncil.MotionKit.Testing;

var now = new DateTimeOffset(2026, 10, 23, 2, 0, 0, TimeSpan.Zero);

CheckFullAndReducedProfileResolution();
CheckProfileSnapshotImmutability();
CheckMissingRuleFailsClosed();
CheckInvalidProfileFailsClosed();
CheckRenderCommandTruthFirewall();
await CheckSupportedBeginDuplicateSettleAsync();
await CheckUnsupportedCapabilityAsync();
await CheckCancelAndNotActiveAsync();
await CheckUnknownCapabilityRejectedAsync();
await CheckStaticFallbackRequiresCapabilityAsync();
CheckAdapterVersionValidation();
await CheckConcurrentFakeRendererAsync();
await CheckDisposalCleanupAsync();

Console.WriteLine("MotionKit renderer boundary validation: PASS");

void CheckFullAndReducedProfileResolution()
{
    var resolver = Resolver();
    var full = resolver.Resolve(Lease(
        Guid.Parse("10000000-0000-0000-0000-000000000001"),
        "sigil:chair",
        "ROLE_ACTIVATED",
        MotionAccessibilityMode.Full));
    var reduced = resolver.Resolve(Lease(
        Guid.Parse("10000000-0000-0000-0000-000000000002"),
        "sigil:chair",
        "ROLE_ACTIVATED",
        MotionAccessibilityMode.Reduced));

    var fullCommand = full.Command
        ?? throw new InvalidOperationException("Full profile command should resolve.");
    var reducedCommand = reduced.Command
        ?? throw new InvalidOperationException("Reduced profile command should resolve.");

    Check(full.Status == MotionPreparationStatus.Ready, "Full profile should resolve.");
    Check(fullCommand.ProfileId == "command-center-test", "Render command must carry product Motion Profile identity.");
    Check(fullCommand.VisualToken == "SIGIL_ACTIVE_FULL", "Full profile token drifted.");
    Check(fullCommand.Duration == TimeSpan.FromMilliseconds(180), "Full profile duration drifted.");
    Check(
        fullCommand.RequiredCapabilities
        == (MotionRenderCapability.Opacity | MotionRenderCapability.Scale),
        "Full profile capability requirements drifted.");

    Check(reduced.Status == MotionPreparationStatus.Ready, "Reduced profile should resolve.");
    Check(reducedCommand.VisualToken == "SIGIL_ACTIVE_REDUCED", "Reduced profile token drifted.");
    Check(reducedCommand.Duration == TimeSpan.Zero, "Reduced profile should use explicit static duration.");
    Check(
        reducedCommand.RequiredCapabilities == MotionRenderCapability.StaticSettle,
        "Reduced profile must use its own capability path.");
}

void CheckProfileSnapshotImmutability()
{
    var mutable = Rules();
    var resolver = new MotionProfileResolver(
        new MotionProductProfile("command-center-test", mutable));

    mutable.Clear();
    mutable["BLOCKED"] = new MotionVisualRule(
        "BLOCKED",
        new MotionVisualVariant("MUTATED", TimeSpan.FromSeconds(1), MotionRenderCapability.DynamicDrawing),
        new MotionVisualVariant("MUTATED_REDUCED", TimeSpan.Zero, MotionRenderCapability.StaticSettle));

    var resolved = resolver.Resolve(Lease(
        Guid.Parse("10000000-0000-0000-0000-000000000003"),
        "sigil:chair",
        "ROLE_ACTIVATED",
        MotionAccessibilityMode.Full));

    var command = resolved.Command
        ?? throw new InvalidOperationException("Snapshotted profile should still resolve original rule.");

    Check(command.VisualToken == "SIGIL_ACTIVE_FULL", "External profile mutation must not affect resolver snapshot.");
    Check(resolver.ProfileId == "command-center-test", "Profile identity should remain stable.");
}

void CheckMissingRuleFailsClosed()
{
    var resolved = Resolver().Resolve(Lease(
        Guid.Parse("10000000-0000-0000-0000-000000000004"),
        "status:blocked",
        "BLOCKED",
        MotionAccessibilityMode.Full));

    Check(resolved.Status == MotionPreparationStatus.RuleNotFound, "Missing visual rule must fail closed.");
    Check(resolved.Command is null, "Missing rule must not fabricate a render command.");
}

void CheckInvalidProfileFailsClosed()
{
    var invalidRules = new Dictionary<string, MotionVisualRule>(StringComparer.Ordinal)
    {
        ["ROLE_ACTIVATED"] = new(
            "ROLE_ACTIVATED",
            new MotionVisualVariant(
                "TOO_LONG",
                MotionRendererContractGuard.MaxDuration + TimeSpan.FromMilliseconds(1),
                MotionRenderCapability.Opacity),
            new MotionVisualVariant(
                "STATIC",
                TimeSpan.Zero,
                MotionRenderCapability.StaticSettle))
    };

    var threw = false;
    try
    {
        _ = new MotionProfileResolver(new MotionProductProfile("invalid-profile", invalidRules));
    }
    catch (ArgumentException)
    {
        threw = true;
    }

    Check(threw, "Invalid profile must fail during resolver construction.");
}

void CheckRenderCommandTruthFirewall()
{
    var properties = typeof(MotionRenderCommand)
        .GetProperties()
        .Select(property => property.Name)
        .ToArray();

    Check(
        properties.All(name => !name.Contains("Truth", StringComparison.OrdinalIgnoreCase)),
        "Renderer command must not expose truth fields.");
    Check(
        typeof(MotionRenderCommand)
            .GetProperties()
            .All(property => property.PropertyType != typeof(MotionTruthSnapshot)),
        "Renderer command must not expose MotionTruthSnapshot.");
}

async Task CheckSupportedBeginDuplicateSettleAsync()
{
    await using var renderer = new DeterministicFakeRenderer(
        "fake:full",
        "test-1.0",
        MotionRenderCapability.StaticSettle
        | MotionRenderCapability.Opacity
        | MotionRenderCapability.Scale);

    var command = FullCommand(
        Guid.Parse("20000000-0000-0000-0000-000000000001"));

    var started = await renderer.BeginAsync(command);
    var duplicate = await renderer.BeginAsync(command);
    var settled = await renderer.SettleAsync(
        command.Identity.InstanceId,
        MotionSettleMode.Final);
    var notActive = await renderer.SettleAsync(
        command.Identity.InstanceId,
        MotionSettleMode.Final);

    Check(started.Status == MotionRenderStatus.Started, "Supported command should start.");
    Check(started.AdapterId == "fake:full", "Render result must carry adapter identity.");
    Check(started.AdapterVersion == "test-1.0", "Render result must carry adapter version.");
    Check(duplicate.Status == MotionRenderStatus.DuplicateInstance, "Duplicate active instance must be rejected.");
    Check(settled.Status == MotionRenderStatus.Settled, "Active command should settle.");
    Check(notActive.Status == MotionRenderStatus.NotActive, "Second settle must report not active.");

    var diagnostics = renderer.SnapshotDiagnostics();
    Check(diagnostics.AdapterId == "fake:full", "Diagnostics must carry adapter identity.");
    Check(diagnostics.AdapterVersion == "test-1.0", "Diagnostics must carry adapter version.");
    Check(diagnostics.ActiveCount == 0, "Settled fake renderer must have no active command.");
    Check(diagnostics.StartedCount == 1, "Fake renderer start count drifted.");
    Check(diagnostics.SettledCount == 1, "Fake renderer settle count drifted.");
    Check(diagnostics.DuplicateCount == 1, "Fake renderer duplicate count drifted.");
}

async Task CheckUnsupportedCapabilityAsync()
{
    await using var renderer = new DeterministicFakeRenderer(
        "fake:static-only",
        "test-1.0",
        MotionRenderCapability.StaticSettle);

    var command = FullCommand(
        Guid.Parse("20000000-0000-0000-0000-000000000002"));

    var result = await renderer.BeginAsync(command);

    Check(result.Status == MotionRenderStatus.NotSupported, "Unsupported capability must be explicit.");
    var diagnostics = renderer.SnapshotDiagnostics();
    Check(diagnostics.ActiveCount == 0, "Unsupported command must not become active.");
    Check(diagnostics.UnsupportedCount == 1, "Unsupported diagnostic count drifted.");
}

async Task CheckCancelAndNotActiveAsync()
{
    await using var renderer = new DeterministicFakeRenderer(
        "fake:cancel",
        "test-1.0",
        MotionRenderCapability.StaticSettle
        | MotionRenderCapability.Opacity
        | MotionRenderCapability.Scale);

    var command = FullCommand(
        Guid.Parse("20000000-0000-0000-0000-000000000003"));

    _ = await renderer.BeginAsync(command);
    var cancelled = await renderer.CancelAsync(command.Identity.InstanceId, "superseded");
    var notActive = await renderer.CancelAsync(command.Identity.InstanceId, "duplicate cancel");

    Check(cancelled.Status == MotionRenderStatus.Cancelled, "Active command should cancel.");
    Check(notActive.Status == MotionRenderStatus.NotActive, "Second cancel must report not active.");
    Check(renderer.SnapshotDiagnostics().CancelledCount == 1, "Cancel diagnostics drifted.");
}

async Task CheckUnknownCapabilityRejectedAsync()
{
    await using var renderer = new DeterministicFakeRenderer(
        "fake:known",
        MotionRendererContractGuard.KnownCapabilities);

    var command = FullCommand(
        Guid.Parse("20000000-0000-0000-0000-000000000004"))
        with
        {
            RequiredCapabilities = (MotionRenderCapability)(1 << 20)
        };

    var result = await renderer.BeginAsync(command);

    Check(result.Status == MotionRenderStatus.RejectedInvalid, "Unknown capability bits must fail closed.");
    Check(renderer.SnapshotDiagnostics().RejectedCount == 1, "Invalid command diagnostic count drifted.");
}


async Task CheckStaticFallbackRequiresCapabilityAsync()
{
    await using var renderer = new DeterministicFakeRenderer(
        "fake:no-static-fallback",
        "test-1.0",
        MotionRenderCapability.Opacity | MotionRenderCapability.Scale);

    var command = FullCommand(
        Guid.Parse("20000000-0000-0000-0000-000000000006"));

    var started = await renderer.BeginAsync(command);
    Check(started.Status == MotionRenderStatus.Started, "Non-static Full command should start without StaticSettle.");

    var unsupported = await renderer.SettleAsync(
        command.Identity.InstanceId,
        MotionSettleMode.StaticFallback);
    Check(
        unsupported.Status == MotionRenderStatus.NotSupported,
        "StaticFallback must fail when adapter lacks StaticSettle capability.");
    Check(
        renderer.SnapshotDiagnostics().ActiveCount == 1,
        "Unsupported StaticFallback must not silently destroy the active instance.");

    var final = await renderer.SettleAsync(
        command.Identity.InstanceId,
        MotionSettleMode.Final);
    Check(final.Status == MotionRenderStatus.Settled, "Caller must remain able to choose an explicit supported settle.");
}

void CheckAdapterVersionValidation()
{
    var threw = false;
    try
    {
        _ = new DeterministicFakeRenderer(
            "fake:bad-version",
            "",
            MotionRenderCapability.StaticSettle);
    }
    catch (ArgumentException)
    {
        threw = true;
    }

    Check(threw, "Adapter version is mandatory evidence identity.");
}

async Task CheckConcurrentFakeRendererAsync()
{
    await using var renderer = new DeterministicFakeRenderer(
        "fake:parallel",
        "test-1.0",
        MotionRenderCapability.Opacity | MotionRenderCapability.Scale);

    var instanceIds = Enumerable.Range(1, 32)
        .Select(index => Guid.Parse($"30000000-0000-0000-0000-{index:D12}"))
        .ToArray();

    Parallel.ForEach(instanceIds, instanceId =>
    {
        var result = renderer.BeginAsync(FullCommand(instanceId))
            .GetAwaiter()
            .GetResult();

        if (result.Status != MotionRenderStatus.Started)
        {
            throw new InvalidOperationException($"Concurrent fake begin failed for {instanceId}.");
        }
    });

    Check(renderer.SnapshotDiagnostics().ActiveCount == 32, "Concurrent fake renderer must retain every active instance.");

    Parallel.ForEach(instanceIds, instanceId =>
    {
        var result = renderer.CancelAsync(instanceId, "parallel cleanup")
            .GetAwaiter()
            .GetResult();

        if (result.Status != MotionRenderStatus.Cancelled)
        {
            throw new InvalidOperationException($"Concurrent fake cancel failed for {instanceId}.");
        }
    });

    var diagnostics = renderer.SnapshotDiagnostics();
    Check(diagnostics.ActiveCount == 0, "Concurrent cleanup must leave no active render instance.");
    Check(diagnostics.StartedCount == 32, "Concurrent started count drifted.");
    Check(diagnostics.CancelledCount == 32, "Concurrent cancelled count drifted.");
}

async Task CheckDisposalCleanupAsync()
{
    var renderer = new DeterministicFakeRenderer(
        "fake:dispose",
        "test-1.0",
        MotionRenderCapability.Opacity | MotionRenderCapability.Scale);

    _ = await renderer.BeginAsync(FullCommand(
        Guid.Parse("20000000-0000-0000-0000-000000000005")));

    await renderer.DisposeAsync();

    var threw = false;
    try
    {
        _ = renderer.SnapshotDiagnostics();
    }
    catch (ObjectDisposedException)
    {
        threw = true;
    }

    Check(threw, "Disposed renderer must reject further use.");
}

MotionRenderCommand FullCommand(Guid instanceId)
{
    var resolved = Resolver().Resolve(Lease(
        instanceId,
        "sigil:chair",
        "ROLE_ACTIVATED",
        MotionAccessibilityMode.Full));

    return resolved.Command
        ?? throw new InvalidOperationException("Expected Full command.");
}

MotionProfileResolver Resolver() =>
    new(new MotionProductProfile("command-center-test", Rules()));

Dictionary<string, MotionVisualRule> Rules() =>
    new(StringComparer.Ordinal)
    {
        ["ROLE_ACTIVATED"] = new(
            "ROLE_ACTIVATED",
            new MotionVisualVariant(
                "SIGIL_ACTIVE_FULL",
                TimeSpan.FromMilliseconds(180),
                MotionRenderCapability.Opacity | MotionRenderCapability.Scale),
            new MotionVisualVariant(
                "SIGIL_ACTIVE_REDUCED",
                TimeSpan.Zero,
                MotionRenderCapability.StaticSettle))
    };

MotionLease Lease(
    Guid instanceId,
    string targetId,
    string semanticEventId,
    MotionAccessibilityMode accessibilityMode) =>
    new(
        instanceId,
        $"request:{instanceId:N}",
        targetId,
        semanticEventId,
        "TEST_TRUTH_REQUIREMENT",
        "state-v1",
        now,
        accessibilityMode,
        now);

void Check(bool condition, string message)
{
    if (!condition)
    {
        throw new InvalidOperationException(message);
    }
}
