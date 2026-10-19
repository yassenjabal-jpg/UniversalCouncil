using System.Text.Json;
using System.Text.Json.Nodes;
using UniversalCouncil.CommandCenter.Application;
using UniversalCouncil.CommandCenter.Core;
using UniversalCouncil.CommandCenter.Infrastructure;

var now = new DateTimeOffset(2026, 10, 19, 8, 0, 0, TimeSpan.Zero);
var source = Path.Combine(
    AppContext.BaseDirectory,
    "state",
    "execution-fabric.json");

Require(File.Exists(source), "Stage 4 fabric fixture missing");

var reader = new JsonExecutionFabricReader(source);
var service = new ExecutionFabricService(reader, () => now);
var fabric = service.GetFabric();

Require(fabric.Health == ExecutionFabricHealth.Healthy, "canonical fabric must be healthy");
Require(fabric.ServiceMode == "SAFE_DISABLED", "Stage 4 service must be SAFE_DISABLED");
Require(!fabric.LiveDispatchEnabled, "live dispatch must remain disabled");
Require(fabric.TargetHost == "YASSIN", "unexpected execution target");
Require(fabric.Providers.All(item => !item.CanExecute), "no Stage 4 provider may execute");
Require(
    fabric.Providers.Any(item =>
        item.Id == "dc_control_plane" &&
        item.Role == "LEGACY_REFERENCE_PROVIDER" &&
        item.State == "BLOCKED_BY_PROVIDER_LIMIT"),
    "DC must remain legacy/reference and provider-limited");
Require(
    fabric.Providers.Any(item =>
        item.Id == "semantic_uia_bridge" &&
        item.State == "OBSERVE_ONLY_CURRENT"),
    "semantic UIA truth state drifted");
Require(fabric.UnknownIsNeverSuccess, "UNKNOWN != SUCCESS invariant missing");
Require(fabric.SinglePhysicalController, "single controller invariant missing");
Require(!fabric.AllowedCliCommands.Contains("execute"), "execute command leaked into allowlist");

var valid = Manifest(
    now,
    effect: "EXECUTE",
    risk: "T1_REVERSIBLE",
    actionKind: "focus_window");

service.Validate(valid);
var blocked = service.EvaluateForDispatch(valid);
Require(blocked.State == "BLOCKED", "valid manifest must still be blocked in Stage 4");
Require(
    blocked.Reason.Contains("PHASE0_NOT_PASS", StringComparison.Ordinal),
    "dispatch block reason must preserve Phase 0 gate");

ExpectThrows(
    () => service.Validate(valid with { TargetHost = "OTHER" }),
    "wrong host must fail closed");

ExpectThrows(
    () => service.Validate(valid with { ExpiresAt = now }),
    "expired manifest must fail closed");

ExpectThrows(
    () => service.Validate(valid with
    {
        Effect = "EXECUTE",
        RiskTier = "T0_OBSERVE"
    }),
    "caller may not downgrade EXECUTE to T0");

ExpectThrows(
    () => service.Validate(valid with
    {
        Effect = "WRITE",
        RiskTier = "T1_REVERSIBLE"
    }),
    "caller may not downgrade WRITE below T2");

ExpectThrows(
    () => service.Validate(valid with
    {
        ActionKind = "credential_entry"
    }),
    "credential action kinds must be blocked");

using var temp = new TempFabric(source);

temp.Mutate(root =>
{
    root["service"]!["live_dispatch_enabled"] = true;
});
Require(
    NewService(temp.Path, now).GetFabric().Health == ExecutionFabricHealth.Unavailable,
    "live dispatch mutation must fail closed");

temp.Reset();
temp.Mutate(root =>
{
    root["providers"]!.AsArray()[0]!["can_execute"] = true;
});
Require(
    NewService(temp.Path, now).GetFabric().Health == ExecutionFabricHealth.Unavailable,
    "provider execute authority inflation must fail closed");

temp.Reset();
temp.Mutate(root =>
{
    foreach (var gate in root["phase0"]!["gates"]!.AsObject())
    {
        gate.Value!["status"] = "PASS";
    }
});
Require(
    NewService(temp.Path, now).GetFabric().Health == ExecutionFabricHealth.Unavailable,
    "Stage 4 cannot silently become live-ready after Phase 0 mutation");

using var primitiveRoot = new TempDirectory();
var leasePath = Path.Combine(primitiveRoot.Path, "controller.json");
var lease = new FileControllerLease(
    leasePath,
    TimeSpan.FromMinutes(2),
    () => now);

var first = lease.Acquire("desktop:YASSIN", "technical_operator", "task-a");
lease.AssertCurrent(first);

ExpectThrows(
    () => lease.Acquire("desktop:YASSIN", "other", "task-b"),
    "second controller must be rejected");

lease.Release(first);
var second = lease.Acquire("desktop:YASSIN", "other", "task-b");
Require(second.FencingToken > first.FencingToken, "fencing token must increase");

ExpectThrows(
    () => lease.Release(first),
    "stale holder must not release current lease");

lease.Release(second);

var journal = new AppendOnlyExecutionJournal(
    Path.Combine(primitiveRoot.Path, "journal.jsonl"));
journal.RecordIntent(valid);
Require(
    journal.PendingManifestIds(valid.TaskId).Contains(valid.ManifestId),
    "journal intent must remain pending");

journal.RecordReceipt(new ExecutionReceipt(
    valid.ManifestId,
    valid.TaskId,
    "UNKNOWN",
    "provider interrupted",
    "YASSIN",
    now));

Require(
    journal.PendingManifestIds(valid.TaskId).Contains(valid.ManifestId),
    "UNKNOWN receipt must remain pending");

journal.RecordReceipt(blocked);
Require(
    !journal.PendingManifestIds(valid.TaskId).Contains(valid.ManifestId),
    "terminal BLOCKED receipt must reconcile pending intent");

ExpectThrows(
    () => ExecutionFabricService.ValidateReceipt(new ExecutionReceipt(
        "m",
        "t",
        "POSTCONDITION_VERIFIED",
        "fake",
        "YASSIN",
        now)),
    "Stage 4 cannot originate verified postcondition receipts");

Console.WriteLine("Command Center Stage 4 adversarial validation: PASS");
return 0;

static ExecutionManifest Manifest(
    DateTimeOffset now,
    string effect,
    string risk,
    string actionKind) =>
    new(
        "manifest-1",
        "task-1",
        "technical_operator",
        "YASSIN",
        "desktop_computer_use.control",
        actionKind,
        effect,
        risk,
        "window focus changes to expected target",
        "independent semantic observation",
        "owner-stage4-open",
        now.AddMinutes(10),
        "task-1:manifest-1");

static ExecutionFabricService NewService(
    string path,
    DateTimeOffset now) =>
    new(new JsonExecutionFabricReader(path), () => now);

static void Require(bool condition, string message)
{
    if (!condition)
    {
        throw new InvalidOperationException(message);
    }
}

static void ExpectThrows(Action action, string message)
{
    try
    {
        action();
    }
    catch (Exception)
    {
        return;
    }

    throw new InvalidOperationException(message);
}

sealed class TempFabric : IDisposable
{
    private readonly string original;
    private readonly string directory;

    public TempFabric(string source)
    {
        original = File.ReadAllText(source);
        directory = System.IO.Path.Combine(
            System.IO.Path.GetTempPath(),
            "UniversalCouncil.CommandCenter.Stage4Fabric",
            Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(directory);
        Path = System.IO.Path.Combine(directory, "fabric.json");
        Reset();
    }

    public string Path { get; }

    public void Reset() => File.WriteAllText(Path, original);

    public void Mutate(Action<JsonObject> mutation)
    {
        var root = JsonNode.Parse(original)!.AsObject();
        mutation(root);
        File.WriteAllText(
            Path,
            root.ToJsonString(new JsonSerializerOptions { WriteIndented = true }));
    }

    public void Dispose() => Directory.Delete(directory, recursive: true);
}

sealed class TempDirectory : IDisposable
{
    public TempDirectory()
    {
        Path = System.IO.Path.Combine(
            System.IO.Path.GetTempPath(),
            "UniversalCouncil.CommandCenter.Stage4Primitives",
            Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(Path);
    }

    public string Path { get; }

    public void Dispose() => Directory.Delete(Path, recursive: true);
}
