namespace UniversalCouncil.CommandCenter.Application;

public sealed record RemoteOwnerGatewayDocument(
    string SchemaVersion,
    string SourceType,
    IReadOnlyList<RemoteOwnerSourceDocument> SourceFiles,
    Phase0RemoteCommandSourceDocument Phase0RemoteCommandSource,
    GatewayDocument Gateway,
    RemoteTrustContractDocument TrustContract,
    RemoteApprovalContractDocument ApprovalContract,
    DeviceSessionContractDocument DeviceSessionContract,
    RemoteQueueContractDocument QueueContract,
    RemoteGatewayServiceDocument Service,
    RemoteRuntimeTruthDocument RuntimeTruth);

public sealed record RemoteOwnerSourceDocument(
    string Path,
    string BlobSha);

public sealed record Phase0RemoteCommandSourceDocument(
    string Branch,
    string HeadSha,
    IReadOnlyList<RemoteOwnerSourceDocument> Files);

public sealed record GatewayDocument(
    string Mode,
    string OwnerPrincipal,
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
    bool LiveExecutionAuthorized);

public sealed record RemoteTrustContractDocument(
    bool OwnerAuthorizationRequired,
    bool AuthorizationContextMustBeOutOfBand,
    bool DeviceIdRequired,
    bool SessionIdRequired,
    bool NonceRequired,
    bool IdempotencyKeyRequired,
    bool IssuedAtRequired,
    bool ExpiryRequired,
    bool TargetScopeRequired,
    bool EffectScopeRequired,
    bool ApprovalIntentRequired,
    bool PersistentReplayLedgerRequired,
    string ReplayPolicy,
    int MaxClockSkewSeconds,
    int MaxCommandTtlSeconds);

public sealed record RemoteApprovalContractDocument(
    bool DisplayRecordIsAuthority,
    bool OwnerApprovalMustBeOutOfBand,
    bool ApprovalIdRequiredForHighImpact,
    bool ApprovalExpiryRequired,
    bool ApprovalScopeMustCoverCommand);

public sealed record DeviceSessionContractDocument(
    bool RegistrationRequired,
    bool UnregisteredDeviceFailsClosed,
    bool UnregisteredSessionFailsClosed,
    bool RevokedDeviceFailsClosed,
    bool RevokedSessionFailsClosed);

public sealed record RemoteQueueContractDocument(
    bool AppendOnly,
    string AcceptedState,
    string DuplicateState,
    string ExecutionState,
    bool LiveDispatchAllowed,
    bool UnknownIsNeverSuccess);

public sealed record RemoteGatewayServiceDocument(
    IReadOnlyList<string> AllowedCliCommands,
    IReadOnlyList<string> ForbiddenCliCommands);

public sealed record RemoteRuntimeTruthDocument(
    int RegisteredDevices,
    int RegisteredSessions,
    int QueueDepth,
    bool PhoneConnected,
    bool TailscaleConnected,
    bool GithubTransportConnected,
    bool ChatTransportConnected);

public interface IRemoteOwnerGatewayReader
{
    RemoteOwnerGatewayDocument Read();
}

public sealed class RemoteOwnerGatewayException : Exception
{
    public RemoteOwnerGatewayException(string message) : base(message) { }

    public RemoteOwnerGatewayException(string message, Exception inner) : base(message, inner) { }
}
