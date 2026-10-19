using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using UniversalCouncil.CommandCenter.Application;
using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter.Infrastructure;

public sealed class JsonDeviceSessionRegistry : IDeviceSessionRegistry, IRemoteTransportAuthenticator
{
    private readonly string path;

    public JsonDeviceSessionRegistry(string path)
    {
        this.path = path;
    }

    public void AssertTrusted(
        OwnerAuthorizationContext authorization,
        DateTimeOffset now)
    {
        var document = Read();

        var device = document.Devices.SingleOrDefault(item =>
            item.OwnerId == authorization.OwnerId &&
            item.DeviceId == authorization.DeviceId);

        if (device is null ||
            device.Revoked ||
            device.ValidFrom > now ||
            device.ExpiresAt <= now)
        {
            throw new RemoteOwnerGatewayException(
                "Owner device is unregistered, revoked or expired.");
        }

        var session = document.Sessions.SingleOrDefault(item =>
            item.OwnerId == authorization.OwnerId &&
            item.DeviceId == authorization.DeviceId &&
            item.SessionId == authorization.SessionId);

        if (session is null ||
            session.Revoked ||
            session.ValidFrom > now ||
            session.ExpiresAt <= now)
        {
            throw new RemoteOwnerGatewayException(
                "Owner session is unregistered, revoked or expired.");
        }
    }

    public OwnerAuthorizationContext Authenticate(
        string bearerToken,
        string deviceId,
        string sessionId,
        DateTimeOffset now)
    {
        if (string.IsNullOrWhiteSpace(bearerToken) ||
            string.IsNullOrWhiteSpace(deviceId) ||
            string.IsNullOrWhiteSpace(sessionId))
        {
            throw new RemoteOwnerGatewayException(
                "Bearer token, device ID and session ID are required.");
        }

        byte[] tokenBytes;
        try
        {
            tokenBytes = DecodeBase64Url(bearerToken);
        }
        catch (FormatException exc)
        {
            throw new RemoteOwnerGatewayException(
                "Bearer token format is invalid.",
                exc);
        }

        if (tokenBytes.Length < 32)
        {
            throw new RemoteOwnerGatewayException(
                "Bearer token does not meet the Stage 6 entropy floor.");
        }

        var document = Read();
        var session = document.Sessions.SingleOrDefault(item =>
            item.DeviceId == deviceId &&
            item.SessionId == sessionId);

        if (session is null ||
            session.Revoked ||
            session.ValidFrom > now ||
            session.ExpiresAt <= now)
        {
            throw new RemoteOwnerGatewayException(
                "Remote transport session is unknown, revoked or expired.");
        }

        if (session.ExpiresAt - session.ValidFrom > TimeSpan.FromMinutes(60))
        {
            throw new RemoteOwnerGatewayException(
                "Remote transport session exceeds the Stage 6 TTL.");
        }

        if (string.IsNullOrWhiteSpace(session.TokenSha256) ||
            session.AllowedTargets is null ||
            session.AllowedTargets.Count == 0 ||
            session.AllowedEffects is null ||
            session.AllowedEffects.Count == 0)
        {
            throw new RemoteOwnerGatewayException(
                "Remote transport session lacks authentication material or scope.");
        }

        byte[] expected;
        try
        {
            expected = Convert.FromHexString(session.TokenSha256);
        }
        catch (FormatException exc)
        {
            throw new RemoteOwnerGatewayException(
                "Stored transport token hash is invalid.",
                exc);
        }

        var actual = SHA256.HashData(tokenBytes);
        if (expected.Length != actual.Length ||
            !CryptographicOperations.FixedTimeEquals(expected, actual))
        {
            throw new RemoteOwnerGatewayException(
                "Remote transport authentication failed.");
        }

        var device = document.Devices.SingleOrDefault(item =>
            item.OwnerId == session.OwnerId &&
            item.DeviceId == session.DeviceId);

        if (device is null ||
            device.Revoked ||
            device.ValidFrom > now ||
            device.ExpiresAt <= now)
        {
            throw new RemoteOwnerGatewayException(
                "Owner device is unregistered, revoked or expired.");
        }

        return new OwnerAuthorizationContext(
            "OWNER",
            true,
            "stage6-local-session-token",
            session.OwnerId,
            session.DeviceId,
            session.SessionId,
            session.AllowedTargets.ToArray(),
            session.AllowedEffects.ToArray(),
            session.ValidFrom,
            session.ExpiresAt,
            false);
    }

    private static byte[] DecodeBase64Url(string value)
    {
        var normalized = value.Replace('-', '+').Replace('_', '/');
        normalized += normalized.Length % 4 switch
        {
            0 => string.Empty,
            2 => "==",
            3 => "=",
            _ => throw new FormatException("Invalid base64url length.")
        };
        return Convert.FromBase64String(normalized);
    }

    private DeviceSessionRegistryDocument Read()
    {
        if (!File.Exists(path))
        {
            throw new RemoteOwnerGatewayException(
                $"Device/session registry is missing: {path}");
        }

        try
        {
            var options = JsonOptions();
            var document = JsonSerializer.Deserialize<DeviceSessionRegistryDocument>(
                File.ReadAllText(path),
                options)
                ?? throw new RemoteOwnerGatewayException(
                    "Device/session registry is empty.");

            if (document.SchemaVersion != "1.0")
            {
                throw new RemoteOwnerGatewayException(
                    "Unsupported device/session registry schema.");
            }

            return document;
        }
        catch (RemoteOwnerGatewayException)
        {
            throw;
        }
        catch (Exception exc) when (
            exc is IOException or JsonException or UnauthorizedAccessException)
        {
            throw new RemoteOwnerGatewayException(
                $"Cannot read device/session registry: {exc.Message}",
                exc);
        }
    }

    private static JsonSerializerOptions JsonOptions() =>
        new()
        {
            PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
            PropertyNameCaseInsensitive = false,
            UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow
        };

    private sealed record DeviceSessionRegistryDocument(
        string SchemaVersion,
        IReadOnlyList<DeviceRegistrationDocument> Devices,
        IReadOnlyList<SessionRegistrationDocument> Sessions);

    private sealed record DeviceRegistrationDocument(
        string OwnerId,
        string DeviceId,
        DateTimeOffset ValidFrom,
        DateTimeOffset ExpiresAt,
        bool Revoked);

    private sealed record SessionRegistrationDocument(
        string OwnerId,
        string DeviceId,
        string SessionId,
        DateTimeOffset ValidFrom,
        DateTimeOffset ExpiresAt,
        bool Revoked,
        string? TokenSha256 = null,
        IReadOnlyList<string>? AllowedTargets = null,
        IReadOnlyList<string>? AllowedEffects = null);
}

public sealed class FileRemoteReplayLedger : IRemoteReplayLedger
{
    private readonly string path;

    public FileRemoteReplayLedger(string path)
    {
        this.path = path;
    }

    public ReplayLedgerDecision Accept(
        RemoteCommandEnvelope envelope,
        OwnerAuthorizationContext authorization,
        string digest,
        DateTimeOffset acceptedAt)
    {
        Directory.CreateDirectory(
            Path.GetDirectoryName(Path.GetFullPath(path))!);

        try
        {
            using var stream = new FileStream(
                path,
                FileMode.OpenOrCreate,
                FileAccess.ReadWrite,
                FileShare.None);

            var records = ReadAll(stream);

            var sameIdempotency = records.SingleOrDefault(item =>
                item.IdempotencyKey == envelope.IdempotencyKey);

            if (sameIdempotency is not null)
            {
                if (!string.Equals(
                        sameIdempotency.Digest,
                        digest,
                        StringComparison.Ordinal))
                {
                    throw new RemoteOwnerGatewayException(
                        "Idempotency key reused with a different command.");
                }

                return new ReplayLedgerDecision(
                    "DUPLICATE_SAME_COMMAND",
                    digest);
            }

            if (records.Any(item => item.Nonce == envelope.Nonce))
            {
                throw new RemoteOwnerGatewayException(
                    "Remote command nonce replay detected.");
            }

            var record = new ReplayRecord(
                envelope.IdempotencyKey,
                envelope.Nonce,
                digest,
                acceptedAt,
                authorization.OwnerId,
                authorization.DeviceId,
                authorization.SessionId,
                envelope.Target,
                envelope.Effects.ToArray());

            stream.Seek(0, SeekOrigin.End);
            using var writer = new StreamWriter(
                stream,
                new UTF8Encoding(encoderShouldEmitUTF8Identifier: false),
                leaveOpen: true);
            writer.WriteLine(JsonSerializer.Serialize(record));
            writer.Flush();
            stream.Flush(flushToDisk: true);

            return new ReplayLedgerDecision("ACCEPTED", digest);
        }
        catch (RemoteOwnerGatewayException)
        {
            throw;
        }
        catch (IOException exc)
        {
            throw new RemoteOwnerGatewayException(
                "Replay ledger is locked or unavailable.",
                exc);
        }
    }

    private static IReadOnlyList<ReplayRecord> ReadAll(FileStream stream)
    {
        stream.Seek(0, SeekOrigin.Begin);
        using var reader = new StreamReader(
            stream,
            Encoding.UTF8,
            detectEncodingFromByteOrderMarks: true,
            leaveOpen: true);

        var result = new List<ReplayRecord>();
        string? line;
        while ((line = reader.ReadLine()) is not null)
        {
            if (string.IsNullOrWhiteSpace(line))
            {
                continue;
            }

            try
            {
                result.Add(
                    JsonSerializer.Deserialize<ReplayRecord>(line)
                    ?? throw new RemoteOwnerGatewayException(
                        "Replay ledger contains an empty record."));
            }
            catch (JsonException exc)
            {
                throw new RemoteOwnerGatewayException(
                    "Replay ledger contains invalid JSON.",
                    exc);
            }
        }

        return result;
    }

    private sealed record ReplayRecord(
        string IdempotencyKey,
        string Nonce,
        string Digest,
        DateTimeOffset AcceptedAt,
        string OwnerId,
        string DeviceId,
        string SessionId,
        string Target,
        IReadOnlyList<string> Effects);
}

public sealed class AppendOnlyRemoteCommandQueue : IRemoteCommandQueue
{
    private readonly string path;

    public AppendOnlyRemoteCommandQueue(string path)
    {
        this.path = path;
    }

    public void Append(RemoteCommandQueueRecord record)
    {
        Directory.CreateDirectory(
            Path.GetDirectoryName(Path.GetFullPath(path))!);

        try
        {
            using var stream = new FileStream(
                path,
                FileMode.Append,
                FileAccess.Write,
                FileShare.Read);
            using var writer = new StreamWriter(
                stream,
                new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
            writer.WriteLine(JsonSerializer.Serialize(record));
            writer.Flush();
            stream.Flush(flushToDisk: true);
        }
        catch (IOException exc)
        {
            throw new RemoteOwnerGatewayException(
                "Remote command queue is unavailable.",
                exc);
        }
    }

    public IReadOnlyList<RemoteCommandQueueRecord> ReadAll()
    {
        if (!File.Exists(path))
        {
            return [];
        }

        try
        {
            var result = new List<RemoteCommandQueueRecord>();
            foreach (var line in File.ReadLines(path))
            {
                if (string.IsNullOrWhiteSpace(line))
                {
                    continue;
                }

                result.Add(
                    JsonSerializer.Deserialize<RemoteCommandQueueRecord>(line)
                    ?? throw new RemoteOwnerGatewayException(
                        "Remote command queue contains an empty record."));
            }

            return result;
        }
        catch (RemoteOwnerGatewayException)
        {
            throw;
        }
        catch (Exception exc) when (
            exc is IOException or JsonException or UnauthorizedAccessException)
        {
            throw new RemoteOwnerGatewayException(
                $"Cannot read Remote Owner queue: {exc.Message}",
                exc);
        }
    }
}
