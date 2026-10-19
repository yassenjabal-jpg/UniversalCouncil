using System.Text.Json;
using UniversalCouncil.CommandCenter.Application;
using UniversalCouncil.CommandCenter.Core;
using UniversalCouncil.CommandCenter.Infrastructure;

var jsonOptions = new JsonSerializerOptions
{
    PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
    PropertyNameCaseInsensitive = false,
    WriteIndented = true
};

var projectionPath = Path.Combine(
    AppContext.BaseDirectory,
    "state",
    "remote-owner-gateway.json");

var reader = new JsonRemoteOwnerGatewayReader(projectionPath);
var projection = new RemoteOwnerProjectionService(reader);

var command = args.Length == 0 ? "status" : args[0];

try
{
    switch (command)
    {
        case "status":
        {
            var gateway = projection.GetGateway();
            Console.WriteLine(JsonSerializer.Serialize(new
            {
                health = gateway.Health.ToString().ToUpperInvariant(),
                mode = gateway.Mode,
                target_host = gateway.TargetHost,
                authentication_backend_connected = gateway.AuthenticationBackendConnected,
                live_network_listener_enabled = gateway.LiveNetworkListenerEnabled,
                phase0_remote_trust_status = gateway.Phase0RemoteTrustStatus,
                live_execution_authorized = gateway.LiveExecutionAuthorized,
                phone_connected = gateway.PhoneConnected,
                tailscale_connected = gateway.TailscaleConnected
            }, jsonOptions));
            return gateway.Health == RemoteOwnerHealth.Healthy ? 0 : 3;
        }

        case "validate-envelope":
        {
            RequireCount(args, 4);
            var envelope = Read<RemoteCommandEnvelope>(args[1]);
            var authorization = Read<OwnerAuthorizationContext>(args[2]);
            var service = CreateService(
                reader,
                args[3],
                Path.Combine(Path.GetTempPath(), "UniversalCouncil.Stage5.Validate"));
            service.Validate(envelope, authorization);
            Console.WriteLine("VALID / NOT_QUEUED / NOT_EXECUTABLE");
            return 0;
        }

        case "enqueue-synthetic":
        {
            RequireCount(args, 5);
            var envelope = Read<RemoteCommandEnvelope>(args[1]);
            var authorization = Read<OwnerAuthorizationContext>(args[2]);
            var runtimeRoot = Path.GetFullPath(args[4]);
            Directory.CreateDirectory(runtimeRoot);
            var service = CreateService(reader, args[3], runtimeRoot);
            var receipt = service.EnqueueSynthetic(envelope, authorization);
            Console.WriteLine(JsonSerializer.Serialize(receipt, jsonOptions));
            return 0;
        }

        case "inspect-queue":
        {
            RequireCount(args, 2);
            var queue = new AppendOnlyRemoteCommandQueue(
                Path.GetFullPath(args[1]));
            Console.WriteLine(
                JsonSerializer.Serialize(queue.ReadAll(), jsonOptions));
            return 0;
        }

        case "validate-approval":
        {
            RequireCount(args, 3);
            var approval = Read<RemoteApprovalRecord>(args[1]);
            var runtimeRoot = Path.Combine(
                Path.GetTempPath(),
                "UniversalCouncil.Stage5.Approval");
            var service = CreateService(reader, args[2], runtimeRoot);
            service.ValidateApproval(approval);
            Console.WriteLine("VALID / NOT_EXECUTION_AUTHORITY");
            return 0;
        }

        default:
            Console.Error.WriteLine(
                "Unsupported command. Allowed: status, validate-envelope, enqueue-synthetic, inspect-queue, validate-approval");
            return 2;
    }
}
catch (Exception exc)
{
    Console.Error.WriteLine($"{exc.GetType().Name}: {exc.Message}");
    return 4;
}

RemoteCommandTrustService CreateService(
    IRemoteOwnerGatewayReader gatewayReader,
    string registryPath,
    string runtimeRoot)
{
    var registry = new JsonDeviceSessionRegistry(
        Path.GetFullPath(registryPath));
    var ledger = new FileRemoteReplayLedger(
        Path.Combine(runtimeRoot, "remote-command-replay.jsonl"));
    var queue = new AppendOnlyRemoteCommandQueue(
        Path.Combine(runtimeRoot, "remote-command-queue.jsonl"));

    return new RemoteCommandTrustService(
        gatewayReader,
        registry,
        ledger,
        queue);
}

T Read<T>(string path)
{
    var fullPath = Path.GetFullPath(path);
    if (!File.Exists(fullPath))
    {
        throw new InvalidOperationException(
            $"Required JSON input is missing: {fullPath}");
    }

    return JsonSerializer.Deserialize<T>(
        File.ReadAllText(fullPath),
        jsonOptions)
        ?? throw new InvalidOperationException(
            $"JSON input is empty: {fullPath}");
}

static void RequireCount(string[] arguments, int expected)
{
    if (arguments.Length != expected)
    {
        throw new InvalidOperationException(
            $"Expected {expected - 1} arguments after the command.");
    }
}
