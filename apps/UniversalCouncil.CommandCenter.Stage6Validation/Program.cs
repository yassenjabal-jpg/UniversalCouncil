using System.Net;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using Microsoft.AspNetCore.Hosting.Server;
using Microsoft.AspNetCore.Hosting.Server.Features;
using Microsoft.Extensions.DependencyInjection;
using UniversalCouncil.CommandCenter.Core;
using UniversalCouncil.CommandCenter.RemoteTransport;

var now = new DateTimeOffset(2026, 10, 19, 8, 45, 0, TimeSpan.Zero);
var stateDirectory = Path.Combine(AppContext.BaseDirectory, "state");
var ownerProjection = Path.Combine(stateDirectory, "remote-owner-gateway.json");
var transportProjection = Path.Combine(stateDirectory, "remote-transport.json");

Require(File.Exists(ownerProjection), "Stage 6 owner projection fixture missing");
Require(File.Exists(transportProjection), "Stage 6 transport projection fixture missing");

using var temp = new TempRoot();
var registry = Path.Combine(temp.Path, "registry.json");
var tokenBytes = RandomNumberGenerator.GetBytes(32);
var token = Base64Url(tokenBytes);
var tokenHash = Convert.ToHexString(SHA256.HashData(tokenBytes)).ToLowerInvariant();
WriteRegistry(registry, now, tokenHash, revoked: false);

var app = RemoteTransportHost.Build(
    new RemoteTransportHostOptions(
        ownerProjection,
        transportProjection,
        registry,
        temp.Path,
        0),
    () => now);

await app.StartAsync();

try
{
    var server = app.Services.GetRequiredService<IServer>();
    var addresses = server.Features.Get<IServerAddressesFeature>()?.Addresses
        ?? throw new InvalidOperationException("Kestrel addresses are unavailable.");
    var address = addresses.Single();

    Require(
        address.StartsWith("http://127.0.0.1:", StringComparison.Ordinal),
        $"Stage 6 listener escaped loopback: {address}");
    Require(
        !address.Contains("0.0.0.0", StringComparison.Ordinal),
        "Stage 6 listener may not bind public wildcard.");

    using var client = new HttpClient
    {
        BaseAddress = new Uri(address)
    };

    var health = await client.GetAsync("/healthz");
    Require(health.StatusCode == HttpStatusCode.OK, "health endpoint must be locally reachable");

    var noAuth = await client.GetAsync("/v1/status");
    Require(noAuth.StatusCode == HttpStatusCode.Unauthorized, "status must require authentication");

    using var wrongToken = AuthorizedRequest(
        HttpMethod.Get,
        "/v1/status",
        Base64Url(RandomNumberGenerator.GetBytes(32)));
    var wrongTokenResponse = await client.SendAsync(wrongToken);
    Require(
        wrongTokenResponse.StatusCode == HttpStatusCode.Unauthorized,
        "wrong token must fail closed");

    using var statusRequest = AuthorizedRequest(HttpMethod.Get, "/v1/status", token);
    var status = await client.SendAsync(statusRequest);
    Require(status.StatusCode == HttpStatusCode.OK, "authenticated status must succeed");
    var statusJson = JsonNode.Parse(await status.Content.ReadAsStringAsync())!.AsObject();
    Require(statusJson["execution_state"]?.GetValue<string>() == "BLOCKED_PHASE0", "status may not imply execution");
    Require(statusJson["tailscale_connected"]?.GetValue<bool>() == false, "Tailscale must remain not connected");
    Require(statusJson["phone_connected"]?.GetValue<bool>() == false, "phone must remain not connected");

    var envelope = new RemoteCommandEnvelope(
        "RC-HTTP-1",
        "nonce-http-1",
        "idem-http-1",
        now.AddMinutes(-1),
        now.AddMinutes(5),
        "owner-1",
        "device-1",
        "session-1",
        "studio",
        ["PROJECT_WRITE"],
        "continue bounded Studio review",
        "OWNER_APPROVAL_REQUIRED_IF_HIGH_IMPACT",
        "corr-http-1");

    using var firstRequest = AuthorizedJsonRequest(
        "/v1/commands",
        token,
        envelope);
    var first = await client.SendAsync(firstRequest);
    Require(first.StatusCode == HttpStatusCode.OK, "authenticated command must enter trust gate");
    var firstJson = JsonNode.Parse(await first.Content.ReadAsStringAsync())!.AsObject();
    Require(firstJson["trust_state"]?.GetValue<string>() == "QUEUED_TRUSTED", "first command must queue as trusted");
    Require(firstJson["execution_state"]?.GetValue<string>() == "BLOCKED_PHASE0", "transport acceptance may not execute");

    var queuePath = Path.Combine(temp.Path, "remote-command-queue.jsonl");
    Require(File.ReadLines(queuePath).Count() == 1, "first command must append exactly one queue record");

    using var duplicateRequest = AuthorizedJsonRequest(
        "/v1/commands",
        token,
        envelope);
    var duplicate = await client.SendAsync(duplicateRequest);
    Require(duplicate.StatusCode == HttpStatusCode.OK, "same command retry must be idempotent");
    var duplicateJson = JsonNode.Parse(await duplicate.Content.ReadAsStringAsync())!.AsObject();
    Require(
        duplicateJson["trust_state"]?.GetValue<string>() == "DUPLICATE_SAME_COMMAND",
        "same command retry must deduplicate");
    Require(File.ReadLines(queuePath).Count() == 1, "duplicate must not append queue record");

    using var changedRequest = AuthorizedJsonRequest(
        "/v1/commands",
        token,
        envelope with { Instruction = "changed under same idempotency" });
    var changed = await client.SendAsync(changedRequest);
    Require(changed.StatusCode == HttpStatusCode.Unauthorized, "changed idempotent command must fail closed");
    Require(File.ReadLines(queuePath).Count() == 1, "rejected conflict must not append queue record");

    var approval = new RemoteApprovalRequest(
        "APR-HTTP-1",
        ["studio"],
        ["PROJECT_WRITE"],
        now.AddMinutes(-1),
        now.AddMinutes(5));
    using var approvalRequest = AuthorizedJsonRequest(
        "/v1/approvals/validate",
        token,
        approval);
    var approvalResponse = await client.SendAsync(approvalRequest);
    Require(approvalResponse.StatusCode == HttpStatusCode.OK, "bounded approval transport must validate");
    var approvalJson = JsonNode.Parse(await approvalResponse.Content.ReadAsStringAsync())!.AsObject();
    Require(
        approvalJson["state"]?.GetValue<string>() == "VALID_NOT_EXECUTION_AUTHORITY",
        "transported approval may not become execution authority");

    var oversized = new string('x', 32769);
    using var oversizedRequest = AuthorizedRequest(HttpMethod.Post, "/v1/commands", token);
    oversizedRequest.Content = new StringContent(
        JsonSerializer.Serialize(new { value = oversized }),
        Encoding.UTF8,
        "application/json");
    var oversizedResponse = await client.SendAsync(oversizedRequest);
    Require(
        oversizedResponse.StatusCode == HttpStatusCode.RequestEntityTooLarge,
        "oversized body must fail closed");

    WriteRegistry(registry, now, tokenHash, revoked: true);
    using var revokedRequest = AuthorizedRequest(HttpMethod.Get, "/v1/status", token);
    var revoked = await client.SendAsync(revokedRequest);
    Require(revoked.StatusCode == HttpStatusCode.Unauthorized, "revoked session must fail closed");

    WriteRegistry(
        registry,
        now.AddHours(-2),
        tokenHash,
        revoked: false,
        expiresAt: now.AddMinutes(-1));
    using var expiredRequest = AuthorizedRequest(HttpMethod.Get, "/v1/status", token);
    var expired = await client.SendAsync(expiredRequest);
    Require(expired.StatusCode == HttpStatusCode.Unauthorized, "expired session must fail closed");

    WriteRegistry(registry, now, tokenHash, revoked: false);
    using var mismatch = AuthorizedRequest(HttpMethod.Get, "/v1/status", token, deviceId: "other-device");
    var mismatchResponse = await client.SendAsync(mismatch);
    Require(mismatchResponse.StatusCode == HttpStatusCode.Unauthorized, "device/session mismatch must fail closed");

    Console.WriteLine($"Stage 6 loopback address: {address}");
    Console.WriteLine("Command Center Stage 6 authenticated HTTP round-trip: PASS");
}
finally
{
    await app.StopAsync();
    await app.DisposeAsync();
}

return 0;

HttpRequestMessage AuthorizedRequest(
    HttpMethod method,
    string path,
    string bearer,
    string deviceId = "device-1",
    string sessionId = "session-1")
{
    var request = new HttpRequestMessage(method, path);
    request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", bearer);
    request.Headers.Add("X-UC-Device-ID", deviceId);
    request.Headers.Add("X-UC-Session-ID", sessionId);
    return request;
}

HttpRequestMessage AuthorizedJsonRequest<T>(
    string path,
    string bearer,
    T body)
{
    var request = AuthorizedRequest(HttpMethod.Post, path, bearer);
    request.Content = JsonContent.Create(
        body,
        options: new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower
        });
    return request;
}

static string Base64Url(byte[] bytes) =>
    Convert.ToBase64String(bytes)
        .TrimEnd('=')
        .Replace('+', '-')
        .Replace('/', '_');

static void WriteRegistry(
    string path,
    DateTimeOffset now,
    string tokenHash,
    bool revoked,
    DateTimeOffset? expiresAt = null)
{
    var expiry = expiresAt ?? now.AddMinutes(30);
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
                expires_at = now.AddHours(8),
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
                valid_from = now.AddMinutes(-5),
                expires_at = expiry,
                revoked,
                token_sha256 = tokenHash,
                allowed_targets = new[] { "studio" },
                allowed_effects = new[] { "PROJECT_WRITE" }
            }
        }
    };

    File.WriteAllText(
        path,
        JsonSerializer.Serialize(
            data,
            new JsonSerializerOptions
            {
                WriteIndented = true,
                PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower
            }));
}

static void Require(bool condition, string message)
{
    if (!condition)
    {
        throw new InvalidOperationException(message);
    }
}

sealed class TempRoot : IDisposable
{
    public TempRoot()
    {
        Path = System.IO.Path.Combine(
            System.IO.Path.GetTempPath(),
            "UniversalCouncil.CommandCenter.Stage6",
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
