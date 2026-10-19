namespace UniversalCouncil.CommandCenter.Core;

public sealed record OwnerDeviceEnrollmentRequest(
    string OwnerId,
    string DeviceId,
    DateTimeOffset ValidFrom,
    DateTimeOffset ExpiresAt);

public sealed record OwnerSessionIssueRequest(
    string OwnerId,
    string DeviceId,
    DateTimeOffset ValidFrom,
    DateTimeOffset ExpiresAt,
    IReadOnlyList<string> AllowedTargets,
    IReadOnlyList<string> AllowedEffects);

public sealed record OwnerSessionCredential(
    string OwnerId,
    string DeviceId,
    string SessionId,
    string BearerToken,
    DateTimeOffset ValidFrom,
    DateTimeOffset ExpiresAt,
    IReadOnlyList<string> AllowedTargets,
    IReadOnlyList<string> AllowedEffects);

public sealed record OwnerSessionRevocationReceipt(
    string SessionId,
    bool Revoked,
    DateTimeOffset RevokedAt);

public sealed record OwnerEnrollmentSnapshot(
    int DeviceCount,
    int ActiveDeviceCount,
    int SessionCount,
    int ActiveSessionCount);

public interface IOwnerEnrollmentRegistry
{
    void UpsertDevice(
        string ownerId,
        string deviceId,
        DateTimeOffset validFrom,
        DateTimeOffset expiresAt);

    void UpsertSession(
        string ownerId,
        string deviceId,
        string sessionId,
        DateTimeOffset validFrom,
        DateTimeOffset expiresAt,
        string tokenSha256,
        IReadOnlyList<string> allowedTargets,
        IReadOnlyList<string> allowedEffects);

    void RevokeSession(string sessionId);

    OwnerEnrollmentSnapshot Snapshot(DateTimeOffset now);
}

public interface IOwnerEnrollmentService
{
    void EnrollDevice(OwnerDeviceEnrollmentRequest request);

    OwnerSessionCredential IssueSession(OwnerSessionIssueRequest request);

    OwnerSessionRevocationReceipt RevokeSession(string sessionId);

    OwnerEnrollmentSnapshot Snapshot();
}
