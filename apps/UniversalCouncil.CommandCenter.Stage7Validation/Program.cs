using System.Security.Cryptography;
using UniversalCouncil.CommandCenter.Application;
using UniversalCouncil.CommandCenter.Core;
using UniversalCouncil.CommandCenter.Infrastructure;

var now = new DateTimeOffset(2026, 10, 19, 9, 20, 0, TimeSpan.Zero);
var source = Path.Combine(
    AppContext.BaseDirectory,
    "state",
    "owner-device-tailnet.json");

Require(File.Exists(source), "Stage 7 owner-tailnet fixture missing");

var projection = new OwnerTailnetProjectionService(
    new JsonOwnerTailnetReader(source)).GetTailnet();

Require(projection.Health == OwnerTailnetHealth.Healthy, "Stage 7 projection must be healthy");
Require(projection.Mode == "OWNER_DEVICE_ENROLLMENT_TAILNET_PILOT", "unexpected Stage 7 mode");
Require(projection.TargetHost == "YASSIN", "Stage 7 target host drifted");
Require(projection.HostControlState == "DEVICE_OFFLINE_AND_TOOL_QUOTA_BLOCKED", "host-control truth drifted");
Require(projection.TailscaleInstallationState == "UNKNOWN", "Tailscale installation must remain unknown without host evidence");
Require(projection.TailscaleConnectionState == "UNKNOWN", "Tailscale connection must remain unknown without host evidence");
Require(projection.TailscaleServeConfigurationState == "NOT_CONFIGURED", "Serve may not be fabricated");
Require(!projection.OwnerDeviceEnrolled, "owner-device success may not be fabricated");
Require(!projection.ActiveSessionIssued, "owner-session success may not be fabricated");
Require(!projection.PhoneRoundTripProven, "phone success may not be fabricated");
Require(!projection.HostProbeProven, "host probe may not be fabricated");
Require(!projection.TailnetRoundTripProven, "tailnet success may not be fabricated");
Require(!projection.FunnelAllowed, "Funnel must remain forbidden");
Require(!projection.PublicBindAllowed, "public bind must remain forbidden");
Require(!projection.LiveExecutionAuthorized, "Stage 7 may not authorize live execution");
Require(projection.ExecutionState == "BLOCKED_PHASE0", "Stage 7 execution gate drifted");

using var temp = new TempRoot();
var registryPath = Path.Combine(temp.Path, "owner-registry.json");
var registry = new JsonOwnerEnrollmentRegistry(registryPath);
var enrollment = new OwnerEnrollmentService(registry, () => now);

enrollment.EnrollDevice(
    new(
        "owner-1",
        "phone-1",
        now.AddMinutes(-1),
        now.AddDays(7)));

var snapshotAfterDevice = enrollment.Snapshot();
Require(snapshotAfterDevice.DeviceCount == 1, "device enrollment must persist one device");
Require(snapshotAfterDevice.ActiveDeviceCount == 1, "enrolled device must be active");

var credential = enrollment.IssueSession(
    new(
        "owner-1",
        "phone-1",
        now.AddMinutes(-1),
        now.AddMinutes(29),
        ["studio"],
        ["PROJECT_WRITE"]));

Require(!string.IsNullOrWhiteSpace(credential.BearerToken), "issued bearer token is missing");
Require(DecodeBase64Url(credential.BearerToken).Length >= 32, "bearer token entropy floor failed");

var persisted = File.ReadAllText(registryPath);
Require(
    !persisted.Contains(credential.BearerToken, StringComparison.Ordinal),
    "plaintext bearer token leaked into enrollment registry");

var rawToken = DecodeBase64Url(credential.BearerToken);
var expectedHash = Convert.ToHexString(
    SHA256.HashData(rawToken)).ToLowerInvariant();
Require(
    persisted.Contains(expectedHash, StringComparison.Ordinal),
    "token SHA-256 is missing from enrollment registry");

var authenticator = new JsonDeviceSessionRegistry(registryPath);
var authorization = authenticator.Authenticate(
    credential.BearerToken,
    "phone-1",
    credential.SessionId,
    now);

Require(authorization.Authenticated, "issued Stage 7 credential must authenticate");
Require(authorization.OwnerId == "owner-1", "owner identity drifted");
Require(authorization.DeviceId == "phone-1", "device identity drifted");
Require(authorization.AllowedTargets.SequenceEqual(["studio"]), "target scope drifted");
Require(authorization.AllowedEffects.SequenceEqual(["PROJECT_WRITE"]), "effect scope drifted");

ExpectThrows(
    () => enrollment.IssueSession(
        new(
            "owner-1",
            "phone-1",
            now,
            now.AddMinutes(61),
            ["studio"],
            ["PROJECT_WRITE"])),
    "session TTL above 60 minutes must fail closed");

ExpectThrows(
    () => enrollment.IssueSession(
        new(
            "owner-1",
            "unknown-phone",
            now,
            now.AddMinutes(10),
            ["studio"],
            ["PROJECT_WRITE"])),
    "unknown device session issuance must fail closed");

var receipt = enrollment.RevokeSession(credential.SessionId);
Require(receipt.Revoked, "revocation receipt must confirm revocation");

ExpectThrows(
    () => authenticator.Authenticate(
        credential.BearerToken,
        "phone-1",
        credential.SessionId,
        now),
    "revoked session must fail authentication");

var finalSnapshot = enrollment.Snapshot();
Require(finalSnapshot.SessionCount == 1, "one issued session should remain auditable");
Require(finalSnapshot.ActiveSessionCount == 0, "revoked session may not remain active");

Console.WriteLine("Command Center Stage 7 enrollment/revocation validation: PASS");
return 0;

static byte[] DecodeBase64Url(string value)
{
    var normalized = value.Replace('-', '+').Replace('_', '/');
    normalized += (normalized.Length % 4) switch
    {
        0 => string.Empty,
        2 => "==",
        3 => "=",
        _ => throw new FormatException("Invalid base64url length.")
    };
    return Convert.FromBase64String(normalized);
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
            "UniversalCouncil.CommandCenter.Stage7",
            Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(Path);
    }

    public string Path { get; }

    public void Dispose()
    {
        if (Directory.Exists(Path))
        {
            Directory.Delete(Path, recursive: true);
        }
    }
}
