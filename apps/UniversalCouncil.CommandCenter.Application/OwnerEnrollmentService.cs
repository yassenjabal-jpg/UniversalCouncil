using System.Security.Cryptography;
using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter.Application;

public sealed class OwnerEnrollmentService : IOwnerEnrollmentService
{
    private static readonly TimeSpan MaxSessionTtl = TimeSpan.FromMinutes(60);
    private readonly IOwnerEnrollmentRegistry registry;
    private readonly Func<DateTimeOffset> utcNow;

    public OwnerEnrollmentService(
        IOwnerEnrollmentRegistry registry,
        Func<DateTimeOffset>? utcNow = null)
    {
        this.registry = registry;
        this.utcNow = utcNow ?? (() => DateTimeOffset.UtcNow);
    }

    public void EnrollDevice(OwnerDeviceEnrollmentRequest request)
    {
        Require(request.OwnerId, nameof(request.OwnerId));
        Require(request.DeviceId, nameof(request.DeviceId));

        if (request.ExpiresAt <= request.ValidFrom)
        {
            throw new RemoteOwnerGatewayException(
                "Owner device expiry must be after valid-from.");
        }

        registry.UpsertDevice(
            request.OwnerId,
            request.DeviceId,
            request.ValidFrom,
            request.ExpiresAt);
    }

    public OwnerSessionCredential IssueSession(OwnerSessionIssueRequest request)
    {
        Require(request.OwnerId, nameof(request.OwnerId));
        Require(request.DeviceId, nameof(request.DeviceId));

        if (request.ExpiresAt <= request.ValidFrom)
        {
            throw new RemoteOwnerGatewayException(
                "Owner session expiry must be after valid-from.");
        }

        var ttl = request.ExpiresAt - request.ValidFrom;
        if (ttl > MaxSessionTtl)
        {
            throw new RemoteOwnerGatewayException(
                "Owner session TTL exceeds the Stage 7 maximum.");
        }

        if (request.AllowedTargets.Count == 0 ||
            request.AllowedTargets.Any(string.IsNullOrWhiteSpace))
        {
            throw new RemoteOwnerGatewayException(
                "Owner session requires at least one target scope.");
        }

        if (request.AllowedEffects.Count == 0 ||
            request.AllowedEffects.Any(string.IsNullOrWhiteSpace))
        {
            throw new RemoteOwnerGatewayException(
                "Owner session requires at least one effect scope.");
        }

        var rawToken = RandomNumberGenerator.GetBytes(32);
        var bearer = Base64Url(rawToken);
        var tokenHash = Convert.ToHexString(
            SHA256.HashData(rawToken)).ToLowerInvariant();
        var sessionId = Guid.NewGuid().ToString("N");

        registry.UpsertSession(
            request.OwnerId,
            request.DeviceId,
            sessionId,
            request.ValidFrom,
            request.ExpiresAt,
            tokenHash,
            request.AllowedTargets.ToArray(),
            request.AllowedEffects.ToArray());

        return new OwnerSessionCredential(
            request.OwnerId,
            request.DeviceId,
            sessionId,
            bearer,
            request.ValidFrom,
            request.ExpiresAt,
            request.AllowedTargets.ToArray(),
            request.AllowedEffects.ToArray());
    }

    public OwnerSessionRevocationReceipt RevokeSession(string sessionId)
    {
        Require(sessionId, nameof(sessionId));
        registry.RevokeSession(sessionId);

        return new OwnerSessionRevocationReceipt(
            sessionId,
            true,
            utcNow());
    }

    public OwnerEnrollmentSnapshot Snapshot() =>
        registry.Snapshot(utcNow());

    private static string Base64Url(byte[] bytes) =>
        Convert.ToBase64String(bytes)
            .TrimEnd('=')
            .Replace('+', '-')
            .Replace('/', '_');

    private static void Require(string value, string name)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            throw new RemoteOwnerGatewayException(
                $"Owner enrollment field is required: {name}");
        }
    }
}
