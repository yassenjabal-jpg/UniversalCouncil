namespace UniversalCouncil.CommandCenter.Core;

public enum RemoteTransportHealth
{
    Healthy,
    Unavailable
}

public sealed record RemoteTransportProjection(
    RemoteTransportHealth Health,
    string ProblemLabel,
    string Mode,
    string TargetHost,
    string ListenerScope,
    bool ListenerConfigured,
    bool RuntimeListenerActive,
    string AuthenticationBackend,
    bool BearerTokenRequired,
    bool DeviceHeaderRequired,
    bool SessionHeaderRequired,
    int MaxRequestBodyBytes,
    bool CorsEnabled,
    bool TailscaleServeCompatible,
    bool TailscaleConnected,
    bool TailscaleServeConfigured,
    bool PhoneConnected,
    bool PublicExposureAllowed,
    bool LiveExecutionAuthorized,
    string ExecutionState)
{
    public static RemoteTransportProjection Unavailable(string problem) =>
        new(
            RemoteTransportHealth.Unavailable,
            problem,
            "UNAVAILABLE",
            "UNKNOWN",
            "UNKNOWN",
            false,
            false,
            "UNAVAILABLE",
            false,
            false,
            false,
            0,
            false,
            false,
            false,
            false,
            false,
            false,
            "BLOCKED");
}

public sealed record RemoteApprovalRequest(
    string ApprovalId,
    IReadOnlyList<string> AllowedTargets,
    IReadOnlyList<string> AllowedEffects,
    DateTimeOffset IssuedAt,
    DateTimeOffset ExpiresAt);

public interface IRemoteTransportProjectionProvider
{
    RemoteTransportProjection GetTransport();
}

public interface IRemoteTransportAuthenticator
{
    OwnerAuthorizationContext Authenticate(
        string bearerToken,
        string deviceId,
        string sessionId,
        DateTimeOffset now);
}
