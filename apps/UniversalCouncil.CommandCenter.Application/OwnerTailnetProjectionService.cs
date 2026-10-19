using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter.Application;

public sealed class OwnerTailnetProjectionService : IOwnerTailnetProjectionProvider
{
    private readonly IOwnerTailnetReader reader;

    public OwnerTailnetProjectionService(IOwnerTailnetReader reader)
    {
        this.reader = reader;
    }

    public OwnerTailnetProjection GetTailnet()
    {
        try
        {
            var document = reader.Read();
            OwnerTailnetPolicyValidator.Validate(document);

            return new OwnerTailnetProjection(
                OwnerTailnetHealth.Healthy,
                string.Empty,
                document.Runtime.Mode,
                document.Runtime.TargetHost,
                document.HostEvidence.RemoteCommandChannelState,
                document.Tailscale.InstallationState,
                document.Tailscale.ConnectionState,
                document.Tailscale.ServeConfigurationState,
                document.Tailscale.ExpectedBackend,
                document.OwnerDevice.DeviceEnrolled,
                document.OwnerDevice.ActiveSessionIssued,
                document.OwnerDevice.PhoneRoundTripProven,
                document.Tailscale.HostProbeProven,
                document.Tailscale.TailnetRoundTripProven,
                !document.Tailscale.FunnelForbidden,
                document.Runtime.PublicBindAllowed,
                document.Runtime.ExecutionAuthorized,
                document.Runtime.ExecutionState);
        }
        catch (RemoteOwnerGatewayException exc)
        {
            return OwnerTailnetProjection.Unavailable(exc.Message);
        }
        catch (Exception exc)
        {
            return OwnerTailnetProjection.Unavailable(
                $"Unexpected Stage 7 tailnet projection failure: {exc.GetType().Name}");
        }
    }
}

internal static class OwnerTailnetPolicyValidator
{
    public static void Validate(OwnerTailnetDocument document)
    {
        if (document.SchemaVersion != "1.0" ||
            document.SourceType != "repository_projection")
        {
            throw new RemoteOwnerGatewayException(
                "Unsupported Stage 7 owner-tailnet schema/source.");
        }

        var runtime = document.Runtime;
        if (runtime.Mode != "OWNER_DEVICE_ENROLLMENT_TAILNET_PILOT" ||
            runtime.TargetHost != "YASSIN" ||
            runtime.RequiredStage6Mode != "LOOPBACK_AUTHENTICATED_PILOT" ||
            runtime.RequiredLocalBind != "127.0.0.1" ||
            runtime.RequiredLocalPort != 47721 ||
            runtime.PublicBindAllowed ||
            runtime.RouterPortForwardingAllowed ||
            runtime.CorsAllowed ||
            runtime.TailscaleFunnelAllowed ||
            runtime.ExecutionAuthorized ||
            runtime.ExecutionState != "BLOCKED_PHASE0")
        {
            throw new RemoteOwnerGatewayException(
                "Stage 7 runtime authority or transport contract drifted.");
        }

        var owner = document.OwnerDevice;
        if (!owner.DeviceEnrollmentRequired ||
            owner.SessionPlaintextPersisted ||
            owner.SessionTokenMinimumEntropyBytes < 32 ||
            owner.SessionTtlMaxMinutes <= 0 ||
            owner.SessionTtlMaxMinutes > 60 ||
            !owner.RevocationRequired)
        {
            throw new RemoteOwnerGatewayException(
                "Stage 7 owner enrollment contract drifted.");
        }

        var tailscale = document.Tailscale;
        if (tailscale.ExpectedBackend != "http://127.0.0.1:47721" ||
            !tailscale.ServePrivateTailnetOnly ||
            !tailscale.FunnelForbidden)
        {
            throw new RemoteOwnerGatewayException(
                "Stage 7 Tailscale contract drifted.");
        }

        if (document.Gates.LiveExecutionAuthorized)
        {
            throw new RemoteOwnerGatewayException(
                "Stage 7 may not authorize live execution.");
        }
    }
}
