namespace UniversalCouncil.CommandCenter.Core;

public enum RemoteOwnerHealth
{
    Healthy,
    Unavailable
}

public sealed record RemoteOwnerGatewayProjection(
    RemoteOwnerHealth Health,
    string ProblemLabel,
    string Mode,
    string TargetHost,
    bool AuthenticationBackendConnected,
    bool LiveNetworkListenerEnabled,
    bool LocalCliIngressEnabled,
    bool TailscaleCompatibleArchitecture,
    bool PublicInternetExposureAllowed,
    bool RouterPortForwardingAllowed,
    bool GithubQueueTransportEnabled,
    bool ChatTransportEnabled,
    string Phase0RemoteTrustStatus,
    bool LiveExecutionAuthorized,
    int RegisteredDevices,
    int RegisteredSessions,
    int QueueDepth,
    bool PhoneConnected,
    bool TailscaleConnected)
{
    public static RemoteOwnerGatewayProjection Unavailable(string problem) =>
        new(
            RemoteOwnerHealth.Unavailable,
            problem,
            "UNAVAILABLE",
            "UNKNOWN",
            false,
            false,
            false,
            false,
            false,
            false,
            false,
            false,
            "UNKNOWN",
            false,
            0,
            0,
            0,
            false,
            false);
}

public sealed record RemoteCommandEnvelope(
    string CommandId,
    string Nonce,
    string IdempotencyKey,
    DateTimeOffset IssuedAt,
    DateTimeOffset ExpiresAt,
    string OwnerId,
    string DeviceId,
    string SessionId,
    string Target,
    IReadOnlyList<string> Effects,
    string Instruction,
    string ApprovalIntent,
    string CorrelationId);

public sealed record OwnerAuthorizationContext(
    string Principal,
    bool Authenticated,
    string AuthenticationSource,
    string OwnerId,
    string DeviceId,
    string SessionId,
    IReadOnlyList<string> AllowedTargets,
    IReadOnlyList<string> AllowedEffects,
    DateTimeOffset ValidFrom,
    DateTimeOffset ExpiresAt,
    bool Revoked);

public sealed record RemoteApprovalRecord(
    string ApprovalId,
    string OwnerId,
    string DeviceId,
    string SessionId,
    IReadOnlyList<string> AllowedTargets,
    IReadOnlyList<string> AllowedEffects,
    DateTimeOffset IssuedAt,
    DateTimeOffset ExpiresAt,
    bool Authenticated,
    string AuthenticationSource,
    bool Revoked);

public sealed record RemoteCommandReceipt(
    string CommandId,
    string IdempotencyKey,
    string Digest,
    string TrustState,
    string ExecutionState,
    string Reason,
    DateTimeOffset RecordedAt);

public sealed record ReplayLedgerDecision(
    string State,
    string Digest);

public sealed record RemoteCommandQueueRecord(
    string CommandId,
    string IdempotencyKey,
    string Digest,
    string OwnerId,
    string DeviceId,
    string SessionId,
    string Target,
    IReadOnlyList<string> Effects,
    string TrustState,
    string ExecutionState,
    DateTimeOffset QueuedAt);

public interface IRemoteOwnerGatewayProvider
{
    RemoteOwnerGatewayProjection GetGateway();
}

public interface IRemoteCommandTrustService
{
    void Validate(
        RemoteCommandEnvelope envelope,
        OwnerAuthorizationContext authorization);

    RemoteCommandReceipt EnqueueSynthetic(
        RemoteCommandEnvelope envelope,
        OwnerAuthorizationContext authorization);

    RemoteCommandReceipt EnqueueAuthenticatedTransport(
        RemoteCommandEnvelope envelope,
        OwnerAuthorizationContext authorization);

    void ValidateApproval(RemoteApprovalRecord approval);

    RemoteApprovalRecord BuildAndValidateApproval(
        RemoteApprovalRequest request,
        OwnerAuthorizationContext authorization);
}

public interface IRemoteReplayLedger
{
    ReplayLedgerDecision Accept(
        RemoteCommandEnvelope envelope,
        OwnerAuthorizationContext authorization,
        string digest,
        DateTimeOffset acceptedAt);
}

public interface IRemoteCommandQueue
{
    void Append(RemoteCommandQueueRecord record);

    IReadOnlyList<RemoteCommandQueueRecord> ReadAll();
}

public interface IDeviceSessionRegistry
{
    void AssertTrusted(
        OwnerAuthorizationContext authorization,
        DateTimeOffset now);
}
