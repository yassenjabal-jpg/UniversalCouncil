namespace UniversalCouncil.CommandCenter.Application;

public sealed record OwnerTailnetDocument(
    string SchemaVersion,
    string SourceType,
    IReadOnlyList<OwnerTailnetSourceDocument> SourceFiles,
    OwnerTailnetRuntimeDocument Runtime,
    OwnerTailnetDeviceDocument OwnerDevice,
    OwnerTailnetTailscaleDocument Tailscale,
    OwnerTailnetHostEvidenceDocument HostEvidence,
    OwnerTailnetGatesDocument Gates);

public sealed record OwnerTailnetSourceDocument(
    string Path,
    string BlobSha);

public sealed record OwnerTailnetRuntimeDocument(
    string Mode,
    string TargetHost,
    string RequiredStage6Mode,
    string RequiredLocalBind,
    int RequiredLocalPort,
    bool PublicBindAllowed,
    bool RouterPortForwardingAllowed,
    bool CorsAllowed,
    bool TailscaleFunnelAllowed,
    bool ExecutionAuthorized,
    string ExecutionState);

public sealed record OwnerTailnetDeviceDocument(
    bool DeviceEnrollmentRequired,
    bool DeviceEnrolled,
    bool ActiveSessionIssued,
    bool SessionPlaintextPersisted,
    int SessionTokenMinimumEntropyBytes,
    int SessionTtlMaxMinutes,
    bool RevocationRequired,
    bool PhoneRoundTripProven);

public sealed record OwnerTailnetTailscaleDocument(
    string InstallationState,
    string ConnectionState,
    string ServeConfigurationState,
    string ExpectedBackend,
    bool ServePrivateTailnetOnly,
    bool FunnelForbidden,
    bool MagicdnsRequiredForHttpsServe,
    bool HostProbeProven,
    bool TailnetRoundTripProven);

public sealed record OwnerTailnetHostEvidenceDocument(
    bool YassinRemoteAgentSeenOnline,
    string RemoteCommandChannelState,
    bool TailscaleStatusObserved,
    bool RemoteTransportDeployedToYassin,
    bool RemoteTransportRunningOnYassin,
    bool ServeRunningOnYassin);

public sealed record OwnerTailnetGatesDocument(
    bool Stage7CiFoundationPassed,
    bool YassinHostProbePassed,
    bool OwnerDeviceEnrollmentPassed,
    bool TailscalePrivateServePassed,
    bool RealOwnerPhoneRoundTripPassed,
    bool SessionRevocationRoundTripPassed,
    bool LiveExecutionAuthorized);

public interface IOwnerTailnetReader
{
    OwnerTailnetDocument Read();
}
