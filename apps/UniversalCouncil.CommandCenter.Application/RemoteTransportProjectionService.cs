using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter.Application;

public sealed class RemoteTransportProjectionService : IRemoteTransportProjectionProvider
{
    private readonly IRemoteTransportReader reader;

    public RemoteTransportProjectionService(IRemoteTransportReader reader)
    {
        this.reader = reader;
    }

    public RemoteTransportProjection GetTransport()
    {
        try
        {
            var document = reader.Read();
            RemoteTransportPolicyValidator.Validate(document);

            return new RemoteTransportProjection(
                RemoteTransportHealth.Healthy,
                string.Empty,
                document.Transport.Mode,
                document.Transport.TargetHost,
                document.Transport.ListenerScope,
                document.Transport.ListenerConfigured,
                document.Transport.RuntimeListenerActive,
                document.Authentication.Backend,
                document.Authentication.BearerTokenRequired,
                document.Authentication.DeviceHeaderRequired,
                document.Authentication.SessionHeaderRequired,
                document.Http.MaxRequestBodyBytes,
                document.Http.CorsEnabled,
                document.Transport.TailscaleServeCompatible,
                document.Transport.TailscaleConnected,
                document.Transport.TailscaleServeConfigured,
                document.Transport.PhoneConnected,
                document.Transport.PublicBindAllowed,
                document.Authority.LiveExecutionAuthorized,
                document.Authority.ExecutionStateAfterTransportAcceptance);
        }
        catch (RemoteOwnerGatewayException exc)
        {
            return RemoteTransportProjection.Unavailable(exc.Message);
        }
        catch (Exception exc)
        {
            return RemoteTransportProjection.Unavailable(
                $"Unexpected remote transport failure: {exc.GetType().Name}");
        }
    }
}

internal static class RemoteTransportPolicyValidator
{
    public static void Validate(RemoteTransportDocument document)
    {
        if (document.SchemaVersion != "1.0" ||
            document.SourceType != "repository_projection")
        {
            throw new RemoteOwnerGatewayException(
                "Unsupported Remote Transport schema/source.");
        }

        var transport = document.Transport;
        if (transport.Mode != "LOOPBACK_AUTHENTICATED_PILOT" ||
            transport.TargetHost != "YASSIN" ||
            !transport.ListenerConfigured ||
            transport.RuntimeListenerActive ||
            transport.ListenerScope != "LOOPBACK_ONLY" ||
            transport.PublicBindAllowed ||
            transport.RouterPortForwardingAllowed ||
            transport.TailscaleConnected ||
            transport.TailscaleServeConfigured ||
            transport.TailscaleFunnelAllowed ||
            transport.GithubTransportConnected ||
            transport.ChatTransportConnected ||
            transport.PhoneConnected)
        {
            throw new RemoteOwnerGatewayException(
                "Stage 6 transport truth drifted.");
        }

        var allowed = new HashSet<string>(
            transport.AllowedBindAddresses,
            StringComparer.Ordinal);
        if (!allowed.SetEquals(["127.0.0.1", "::1"]))
        {
            throw new RemoteOwnerGatewayException(
                "Stage 6 bind-address allowlist drifted.");
        }

        var auth = document.Authentication;
        if (auth.Backend != "LOCAL_HASHED_SESSION_TOKEN" ||
            !auth.BearerTokenRequired ||
            !auth.DeviceHeaderRequired ||
            !auth.SessionHeaderRequired ||
            auth.TokenPlaintextPersisted ||
            auth.MinimumTokenEntropyBytes < 32 ||
            !auth.ShortLivedSessionsRequired ||
            auth.MaxSessionTtlMinutes <= 0 ||
            auth.MaxSessionTtlMinutes > 60 ||
            !auth.RevocationRequired)
        {
            throw new RemoteOwnerGatewayException(
                "Stage 6 authentication contract drifted.");
        }

        var http = document.Http;
        if (http.MaxRequestBodyBytes <= 0 ||
            http.MaxRequestBodyBytes > 32768 ||
            http.CommandEndpoint != "/v1/commands" ||
            http.ApprovalEndpoint != "/v1/approvals/validate" ||
            http.StatusEndpoint != "/v1/status" ||
            http.HealthEndpoint != "/healthz" ||
            http.CorsEnabled ||
            http.AnonymousCommandAllowed ||
            http.AnonymousApprovalAllowed)
        {
            throw new RemoteOwnerGatewayException(
                "Stage 6 HTTP contract drifted.");
        }

        var authority = document.Authority;
        if (authority.CommandQueueAcceptanceGrantsExecution ||
            authority.ApprovalTransportGrantsExecution ||
            authority.Phase0BypassAllowed ||
            authority.LiveExecutionAuthorized ||
            authority.ExecutionStateAfterTransportAcceptance != "BLOCKED_PHASE0")
        {
            throw new RemoteOwnerGatewayException(
                "Stage 6 transport authority contract drifted.");
        }
    }
}
