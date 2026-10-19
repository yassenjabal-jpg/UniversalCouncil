using System.Text.Json;
using UniversalCouncil.CommandCenter.Application;
using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter.Infrastructure;

public sealed class JsonOwnerEnrollmentRegistry : IOwnerEnrollmentRegistry
{
    private readonly string path;

    public JsonOwnerEnrollmentRegistry(string path)
    {
        this.path = Path.GetFullPath(path);
    }

    public void UpsertDevice(
        string ownerId,
        string deviceId,
        DateTimeOffset validFrom,
        DateTimeOffset expiresAt)
    {
        var document = ReadOrCreate();
        var devices = document.Devices
            .Where(item =>
                !string.Equals(item.OwnerId, ownerId, StringComparison.Ordinal) ||
                !string.Equals(item.DeviceId, deviceId, StringComparison.Ordinal))
            .ToList();

        devices.Add(
            new DeviceRecord(
                ownerId,
                deviceId,
                validFrom,
                expiresAt,
                false));

        Write(document with { Devices = devices });
    }

    public void UpsertSession(
        string ownerId,
        string deviceId,
        string sessionId,
        DateTimeOffset validFrom,
        DateTimeOffset expiresAt,
        string tokenSha256,
        IReadOnlyList<string> allowedTargets,
        IReadOnlyList<string> allowedEffects)
    {
        var document = ReadOrCreate();
        var device = document.Devices.SingleOrDefault(item =>
            string.Equals(item.OwnerId, ownerId, StringComparison.Ordinal) &&
            string.Equals(item.DeviceId, deviceId, StringComparison.Ordinal));

        if (device is null || device.Revoked)
        {
            throw new RemoteOwnerGatewayException(
                "Owner device must be enrolled and non-revoked before session issuance.");
        }

        var sessions = document.Sessions
            .Where(item =>
                !string.Equals(item.SessionId, sessionId, StringComparison.Ordinal))
            .ToList();

        sessions.Add(
            new SessionRecord(
                ownerId,
                deviceId,
                sessionId,
                validFrom,
                expiresAt,
                false,
                tokenSha256,
                allowedTargets.ToArray(),
                allowedEffects.ToArray()));

        Write(document with { Sessions = sessions });
    }

    public void RevokeSession(string sessionId)
    {
        var document = ReadOrCreate();
        var found = false;
        var sessions = document.Sessions
            .Select(item =>
            {
                if (!string.Equals(
                        item.SessionId,
                        sessionId,
                        StringComparison.Ordinal))
                {
                    return item;
                }

                found = true;
                return item with { Revoked = true };
            })
            .ToList();

        if (!found)
        {
            throw new RemoteOwnerGatewayException(
                "Cannot revoke an unknown owner session.");
        }

        Write(document with { Sessions = sessions });
    }

    public OwnerEnrollmentSnapshot Snapshot(DateTimeOffset now)
    {
        var document = ReadOrCreate();
        return new OwnerEnrollmentSnapshot(
            document.Devices.Count,
            document.Devices.Count(item =>
                !item.Revoked &&
                item.ValidFrom <= now &&
                item.ExpiresAt > now),
            document.Sessions.Count,
            document.Sessions.Count(item =>
                !item.Revoked &&
                item.ValidFrom <= now &&
                item.ExpiresAt > now));
    }

    private RegistryDocument ReadOrCreate()
    {
        if (!File.Exists(path))
        {
            return new RegistryDocument("1.0", [], []);
        }

        try
        {
            var options = JsonOptions();
            var document = JsonSerializer.Deserialize<RegistryDocument>(
                File.ReadAllText(path),
                options)
                ?? throw new RemoteOwnerGatewayException(
                    "Owner enrollment registry is empty.");

            if (document.SchemaVersion != "1.0")
            {
                throw new RemoteOwnerGatewayException(
                    "Unsupported owner enrollment registry schema.");
            }

            return document;
        }
        catch (RemoteOwnerGatewayException)
        {
            throw;
        }
        catch (Exception exc) when (
            exc is IOException or
            JsonException or
            UnauthorizedAccessException)
        {
            throw new RemoteOwnerGatewayException(
                $"Cannot read owner enrollment registry: {exc.Message}",
                exc);
        }
    }

    private void Write(RegistryDocument document)
    {
        Directory.CreateDirectory(
            Path.GetDirectoryName(path)
            ?? throw new RemoteOwnerGatewayException(
                "Owner enrollment registry path is invalid."));

        var temp = path + ".tmp";
        var json = JsonSerializer.Serialize(
            document,
            JsonOptions(writeIndented: true));

        File.WriteAllText(temp, json);
        File.Move(temp, path, overwrite: true);
    }

    private static JsonSerializerOptions JsonOptions(bool writeIndented = false) =>
        new()
        {
            PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
            PropertyNameCaseInsensitive = false,
            WriteIndented = writeIndented
        };

    private sealed record RegistryDocument(
        string SchemaVersion,
        IReadOnlyList<DeviceRecord> Devices,
        IReadOnlyList<SessionRecord> Sessions);

    private sealed record DeviceRecord(
        string OwnerId,
        string DeviceId,
        DateTimeOffset ValidFrom,
        DateTimeOffset ExpiresAt,
        bool Revoked);

    private sealed record SessionRecord(
        string OwnerId,
        string DeviceId,
        string SessionId,
        DateTimeOffset ValidFrom,
        DateTimeOffset ExpiresAt,
        bool Revoked,
        string TokenSha256,
        IReadOnlyList<string> AllowedTargets,
        IReadOnlyList<string> AllowedEffects);
}
