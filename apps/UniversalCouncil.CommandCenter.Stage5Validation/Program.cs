using System.Text.Json;
using System.Text.Json.Nodes;
using UniversalCouncil.CommandCenter.Application;
using UniversalCouncil.CommandCenter.Core;
using UniversalCouncil.CommandCenter.Infrastructure;

var now = new DateTimeOffset(2026, 10, 19, 8, 0, 0, TimeSpan.Zero);
var source = Path.Combine(
    AppContext.BaseDirectory,
    "state",
    "remote-owner-gateway.json");

Require(File.Exists(source), "Stage 5 gateway fixture missing");

var projectionReader = new JsonRemoteOwnerGatewayReader(source);
var projectionService = new RemoteOwnerProjectionService(projectionReader);
var projection = projectionService.GetGateway();

Require(projection.Health == RemoteOwnerHealth.Healthy, "canonical gateway must be healthy");
Require(projection.Mode == "LOCAL_TRUST_GATE_ONLY", "unexpected Stage 5 gateway mode");
Require(!projection.AuthenticationBackendConnected, "authentication backend must not be fabricated");
Require(!projection.LiveNetworkListenerEnabled, "live network listener must remain disabled");
Require(!projection.PublicInternetExposureAllowed, "public internet exposure must remain forbidden");
Require(!projection.RouterPortForwardingAllowed, "router port forwarding must remain forbidden");
Require(!projection.LiveExecutionAuthorized, "Stage 5 may not authorize execution");
Require(projection.Phase0RemoteTrustStatus == "IN_TEST", "G0-C truth drifted");
Require(!projection.PhoneConnected && !projection.TailscaleConnected, "live remote connection must not be fabricated");

using var temp = new TempRoot();
var registryPath = Path.Combine(temp.Path, "registry.json");
WriteRegistry(registryPath, now);

var ledgerPath = Path.Combine(temp.Path, "replay.jsonl");
var queuePath = Path.Combine(temp.Path, "queue.jsonl");

RemoteCommandTrustService NewTrust() =>
    new(
        projectionReader,
        new JsonDeviceSessionRegistry(registryPath),
        new FileRemoteReplayLedger(ledgerPath),
        new AppendOnlyRemoteCommandQueue(queuePath),
        () => now);

var service = NewTrust();
var envelope = ValidEnvelope(now);
var authorization = ValidAuthorization(now);

service.Validate(envelope, authorization);
var first = service.EnqueueSynthetic(envelope, authorization);
Require(first.TrustState == "QUEUED_TRUSTED", "first accepted command must enter trusted queue");
Require(first.ExecutionState == "BLOCKED_PHASE0", "queue acceptance may not grant execution");

var queue = new AppendOnlyRemoteCommandQueue(queuePath);
Require(queue.ReadAll().Count == 1, "trusted queue must contain exactly one accepted command");

var duplicate = NewTrust().EnqueueSynthetic(envelope, authorization);
Require(duplicate.TrustState == "DUPLICATE_SAME_COMMAND", "same command must dedupe after process restart");
Require(queue.ReadAll().Count == 1, "duplicate command must not append a second queue item");

ExpectThrows(
    () => NewTrust().EnqueueSynthetic(
        envelope with { Instruction = "different instruction" },
        authorization),
    "reused idempotency with changed command must fail closed");

ExpectThrows(
    () => NewTrust().EnqueueSynthetic(
        envelope with
        {
            CommandId = "RC-2",
            IdempotencyKey = "idem-2"
        },
        authorization),
    "nonce replay under a new idempotency key must fail closed");

ExpectThrows(
    () => service.Validate(
        envelope with { ExpiresAt = now.AddSeconds(-1) },
        authorization),
    "expired command must fail closed");

ExpectThrows(
    () => service.Validate(
        envelope with
        {
            IssuedAt = now.AddMinutes(5),
            ExpiresAt = now.AddMinutes(10)
        },
        authorization),
    "future issue time beyond clock skew must fail closed");

ExpectThrows(
    () => service.Validate(
        envelope with
        {
            IssuedAt = now,
            ExpiresAt = now.AddMinutes(20)
        },
        authorization),
    "TTL above Stage 5 maximum must fail closed");

ExpectThrows(
    () => service.Validate(
        envelope with { Target = "system" },
        authorization),
    "target escalation must fail closed");

ExpectThrows(
    () => service.Validate(
        envelope with { Effects = ["DELETE_SYSTEM_FILE"] },
        authorization),
    "effect escalation must fail closed");

ExpectThrows(
    () => service.Validate(
        envelope,
        authorization with { Authenticated = false }),
    "unauthenticated owner context must fail closed");

ExpectThrows(
    () => service.Validate(
        envelope,
        authorization with { Principal = "TECHNICAL_OPERATOR" }),
    "non-owner principal must fail closed");

ExpectThrows(
    () => service.Validate(
        envelope,
        authorization with { DeviceId = "other-device" }),
    "device identity mismatch must fail closed");

var unregisteredAuth = authorization with
{
    DeviceId = "unknown-device",
    SessionId = "unknown-session"
};
var unregisteredEnvelope = envelope with
{
    DeviceId = "unknown-device",
    SessionId = "unknown-session",
    Nonce = "nonce-x",
    IdempotencyKey = "idem-x",
    CommandId = "RC-X"
};
ExpectThrows(
    () => service.Validate(unregisteredEnvelope, unregisteredAuth),
    "unregistered device/session must fail closed");

var approval = new RemoteApprovalRecord(
    "APR-1",
    "owner-1",
    "device-1",
    "session-1",
    ["studio"],
    ["PROJECT_WRITE"],
    now.AddMinutes(-1),
    now.AddMinutes(5),
    true,
    "synthetic-stage5-test",
    false);
service.ValidateApproval(approval);

ExpectThrows(
    () => service.ValidateApproval(
        approval with { ExpiresAt = now.AddSeconds(-1) }),
    "expired approval must fail closed");

ExpectThrows(
    () => service.ValidateApproval(
        approval with { Revoked = true }),
    "revoked approval must fail closed");

using var mutated = new TempProjection(source);

mutated.Mutate(root =>
{
    root["gateway"]!["live_network_listener_enabled"] = true;
});
Require(
    NewProjection(mutated.Path).Health == RemoteOwnerHealth.Unavailable,
    "live listener mutation must fail closed");

mutated.Reset();
mutated.Mutate(root =>
{
    root["gateway"]!["authentication_backend_connected"] = true;
});
Require(
    NewProjection(mutated.Path).Health == RemoteOwnerHealth.Unavailable,
    "fabricated auth backend must fail closed");

mutated.Reset();
mutated.Mutate(root =>
{
    root["queue_contract"]!["live_dispatch_allowed"] = true;
});
Require(
    NewProjection(mutated.Path).Health == RemoteOwnerHealth.Unavailable,
    "queue dispatch authority inflation must fail closed");

mutated.Reset();
mutated.Mutate(root =>
{
    root["runtime_truth"]!["phone_connected"] = true;
});
Require(
    NewProjection(mutated.Path).Health == RemoteOwnerHealth.Unavailable,
    "fabricated phone connection must fail closed");

Console.WriteLine("Command Center Stage 5 adversarial validation: PASS");
return 0;

RemoteOwnerGatewayProjection NewProjection(string path) =>
    new RemoteOwnerProjectionService(
        new JsonRemoteOwnerGatewayReader(path)).GetGateway();

static RemoteCommandEnvelope ValidEnvelope(DateTimeOffset now) =>
    new(
        "RC-1",
        "nonce-1",
        "idem-1",
        now.AddMinutes(-1),
        now.AddMinutes(5),
        "owner-1",
        "device-1",
        "session-1",
        "studio",
        ["PROJECT_WRITE"],
        "continue bounded Studio review",
        "OWNER_APPROVAL_REQUIRED_IF_HIGH_IMPACT",
        "corr-1");

static OwnerAuthorizationContext ValidAuthorization(DateTimeOffset now) =>
    new(
        "OWNER",
        true,
        "synthetic-stage5-test",
        "owner-1",
        "device-1",
        "session-1",
        ["studio"],
        ["PROJECT_WRITE"],
        now.AddMinutes(-10),
        now.AddMinutes(10),
        false);

static void WriteRegistry(string path, DateTimeOffset now)
{
    var data = new
    {
        schema_version = "1.0",
        devices = new[]
        {
            new
            {
                owner_id = "owner-1",
                device_id = "device-1",
                valid_from = now.AddHours(-1),
                expires_at = now.AddHours(1),
                revoked = false
            }
        },
        sessions = new[]
        {
            new
            {
                owner_id = "owner-1",
                device_id = "device-1",
                session_id = "session-1",
                valid_from = now.AddHours(-1),
                expires_at = now.AddHours(1),
                revoked = false
            }
        }
    };

    File.WriteAllText(
        path,
        JsonSerializer.Serialize(
            data,
            new JsonSerializerOptions { WriteIndented = true }));
}

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

sealed class TempRoot : IDisposable
{
    public TempRoot()
    {
        Path = System.IO.Path.Combine(
            System.IO.Path.GetTempPath(),
            "UniversalCouncil.CommandCenter.Stage5",
            Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(Path);
    }

    public string Path { get; }

    public void Dispose() => Directory.Delete(Path, recursive: true);
}

sealed class TempProjection : IDisposable
{
    private readonly string original;
    private readonly string directory;

    public TempProjection(string source)
    {
        original = File.ReadAllText(source);
        directory = System.IO.Path.Combine(
            System.IO.Path.GetTempPath(),
            "UniversalCouncil.CommandCenter.Stage5Projection",
            Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(directory);
        Path = System.IO.Path.Combine(directory, "projection.json");
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
            root.ToJsonString(
                new JsonSerializerOptions { WriteIndented = true }));
    }

    public void Dispose() => Directory.Delete(directory, recursive: true);
}
