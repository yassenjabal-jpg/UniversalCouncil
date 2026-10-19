namespace UniversalCouncil.CommandCenter.Core;

public enum OwnerTailnetHealth
{
    Healthy,
    Unavailable
}

public sealed record OwnerTailnetProjection(
    OwnerTailnetHealth Health,
    string ProblemLabel,
    string Mode,
    string TargetHost,
    string HostControlState,
    string TailscaleInstallationState,
    string TailscaleConnectionState,
    string TailscaleServeConfigurationState,
    string ExpectedBackend,
    bool OwnerDeviceEnrolled,
    bool ActiveSessionIssued,
    bool PhoneRoundTripProven,
    bool HostProbeProven,
    bool TailnetRoundTripProven,
    bool FunnelAllowed,
    bool PublicBindAllowed,
    bool LiveExecutionAuthorized,
    string ExecutionState)
{
    public static OwnerTailnetProjection Unavailable(string problem) =>
        new(
            OwnerTailnetHealth.Unavailable,
            problem,
            "UNAVAILABLE",
            "UNKNOWN",
            "UNKNOWN",
            "UNKNOWN",
            "UNKNOWN",
            "UNKNOWN",
            "UNKNOWN",
            false,
            false,
            false,
            false,
            false,
            false,
            false,
            false,
            "BLOCKED");
}

public interface IOwnerTailnetProjectionProvider
{
    OwnerTailnetProjection GetTailnet();
}
