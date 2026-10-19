namespace UniversalCouncil.CommandCenter.Application;

public sealed record RemoteTransportDocument(
    string SchemaVersion,
    string SourceType,
    IReadOnlyList<RemoteTransportSourceDocument> SourceFiles,
    RemoteTransportRuntimeDocument Transport,
    RemoteTransportAuthenticationDocument Authentication,
    RemoteTransportHttpDocument Http,
    RemoteTransportRoundTripDocument RoundTrip,
    RemoteTransportAuthorityDocument Authority);

public sealed record RemoteTransportSourceDocument(
    string Path,
    string BlobSha);

public sealed record RemoteTransportRuntimeDocument(
    string Mode,
    string TargetHost,
    bool ListenerConfigured,
    bool RuntimeListenerActive,
    string ListenerScope,
    IReadOnlyList<string> AllowedBindAddresses,
    bool PublicBindAllowed,
    bool RouterPortForwardingAllowed,
    bool TailscaleServeCompatible,
    bool TailscaleConnected,
    bool TailscaleServeConfigured,
    bool TailscaleFunnelAllowed,
    bool GithubTransportConnected,
    bool ChatTransportConnected,
    bool PhoneConnected);

public sealed record RemoteTransportAuthenticationDocument(
    string Backend,
    bool BearerTokenRequired,
    bool DeviceHeaderRequired,
    bool SessionHeaderRequired,
    bool TokenPlaintextPersisted,
    int MinimumTokenEntropyBytes,
    bool ShortLivedSessionsRequired,
    int MaxSessionTtlMinutes,
    bool RevocationRequired);

public sealed record RemoteTransportHttpDocument(
    int MaxRequestBodyBytes,
    string CommandEndpoint,
    string ApprovalEndpoint,
    string StatusEndpoint,
    string HealthEndpoint,
    bool CorsEnabled,
    bool AnonymousCommandAllowed,
    bool AnonymousApprovalAllowed);

public sealed record RemoteTransportRoundTripDocument(
    bool RealLoopbackHttpRequired,
    bool SyntheticIdentityFixtureAllowed,
    bool RealPhoneRequiredForStage6Lock,
    bool RealTailscaleRequiredForStage6Lock,
    string SuccessState);

public sealed record RemoteTransportAuthorityDocument(
    bool CommandQueueAcceptanceGrantsExecution,
    bool ApprovalTransportGrantsExecution,
    bool Phase0BypassAllowed,
    bool LiveExecutionAuthorized,
    string ExecutionStateAfterTransportAcceptance);

public interface IRemoteTransportReader
{
    RemoteTransportDocument Read();
}
