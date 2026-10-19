using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter;

internal sealed class MainWindowViewModel
{
    public MainWindowViewModel(
        ICommandCenterSnapshotProvider snapshotProvider,
        IOperationalStateProvider operationalStateProvider,
        IOrchestrationCatalogProvider orchestrationProvider,
        IExecutionFabricProvider executionFabricProvider,
        IRemoteOwnerGatewayProvider remoteOwnerGatewayProvider,
        IRemoteTransportProjectionProvider remoteTransportProvider,
        IOwnerTailnetProjectionProvider ownerTailnetProvider)
    {
        Snapshot = snapshotProvider.GetSnapshot();
        Operational = operationalStateProvider.GetOperationalState();
        Orchestration = orchestrationProvider.GetCatalog();
        ExecutionFabric = executionFabricProvider.GetFabric();
        RemoteOwner = remoteOwnerGatewayProvider.GetGateway();
        RemoteTransport = remoteTransportProvider.GetTransport();
        OwnerTailnet = ownerTailnetProvider.GetTailnet();
    }

    public CommandCenterSnapshot Snapshot { get; }

    public OperationalStateProjection Operational { get; }

    public OrchestrationCatalogProjection Orchestration { get; }

    public ExecutionFabricProjection ExecutionFabric { get; }

    public RemoteOwnerGatewayProjection RemoteOwner { get; }

    public RemoteTransportProjection RemoteTransport { get; }

    public OwnerTailnetProjection OwnerTailnet { get; }

    public string CouncilCountLabel =>
        $"{Orchestration.Council.CoreRoles.Count} أساسي + {Orchestration.Council.SpecialistRoles.Count} اختصاصي";

    public string StudioDepartmentCountLabel =>
        $"{Orchestration.Studio.Departments.Count} قسم";

    public string MacroPhasesLabel =>
        string.Join("  →  ", Orchestration.Studio.MacroPhases.Select(item => item.ToUpperInvariant()));

    public string SelectionPrecedenceLabel =>
        string.Join("  →  ", Orchestration.ModelControl.SelectionPrecedence);

    public string ModelFallbackLabel =>
        Orchestration.ModelControl.SilentFallbackAllowed
            ? "SILENT FALLBACK ENABLED"
            : "NO SILENT FALLBACK";

    public string ProviderConnectionLabel =>
        Orchestration.ModelControl.ProviderCallsConnected
            ? "PROVIDER CONNECTED"
            : "PROVIDER NOT CONNECTED";

    public string ReturnTicketFieldCountLabel =>
        $"{Orchestration.Studio.ReturnTicketRequiredFields.Count} حقول إلزامية";

    public string ExecutionServiceLabel =>
        $"{ExecutionFabric.ServiceMode} / {ExecutionFabric.TargetHost}";

    public string Phase0SummaryLabel =>
        string.Join(
            "  |  ",
            ExecutionFabric.Phase0Gates.Select(item => $"{item.Id}:{item.Status}"));

    public string ProviderSummaryLabel =>
        $"{ExecutionFabric.Providers.Count} providers / live dispatch disabled";

    public string RemoteOwnerModeLabel =>
        $"{RemoteOwner.Mode} / {RemoteOwner.TargetHost}";

    public string RemoteOwnerTrustLabel =>
        $"G0-C: {RemoteOwner.Phase0RemoteTrustStatus}";

    public string RemoteOwnerConnectionLabel =>
        RemoteOwner.PhoneConnected || RemoteOwner.TailscaleConnected
            ? "REMOTE TRANSPORT CONNECTED"
            : "NO LIVE REMOTE TRANSPORT";

    public string RemoteOwnerRegistryLabel =>
        $"{RemoteOwner.RegisteredDevices} devices / {RemoteOwner.RegisteredSessions} sessions";

    public string RemoteOwnerQueueLabel =>
        $"{RemoteOwner.QueueDepth} queued / execution blocked";

    public string RemoteTransportModeLabel =>
        $"{RemoteTransport.Mode} / {RemoteTransport.ListenerScope}";

    public string RemoteTransportAuthLabel =>
        $"{RemoteTransport.AuthenticationBackend} / bearer required";

    public string RemoteTransportRuntimeLabel =>
        RemoteTransport.RuntimeListenerActive
            ? "LISTENER ACTIVE"
            : "LISTENER CONFIGURED / NOT RUNNING";

    public string RemoteTransportTailnetLabel =>
        RemoteTransport.TailscaleConnected
            ? "TAILSCALE CONNECTED"
            : "TAILSCALE NOT CONNECTED";

    public string RemoteTransportPhoneLabel =>
        RemoteTransport.PhoneConnected
            ? "PHONE CONNECTED"
            : "PHONE NOT CONNECTED";

    public string RemoteTransportExecutionLabel =>
        $"{RemoteTransport.ExecutionState} / live execution disabled";

    public string Stage7ModeLabel =>
        $"{OwnerTailnet.Mode} / {OwnerTailnet.TargetHost}";

    public string Stage7HostAccessLabel =>
        OwnerTailnet.HostControlState == "PAIRED_ONLINE_BUT_TOOL_QUOTA_BLOCKED"
            ? "ONLINE / COMMAND QUOTA BLOCKED"
            : OwnerTailnet.HostControlState;

    public string Stage7TailscaleLabel =>
        $"INSTALL:{OwnerTailnet.TailscaleInstallationState} / CONNECT:{OwnerTailnet.TailscaleConnectionState}";

    public string Stage7ServeLabel =>
        $"SERVE:{OwnerTailnet.TailscaleServeConfigurationState}";

    public string Stage7EnrollmentLabel =>
        OwnerTailnet.OwnerDeviceEnrolled
            ? "OWNER DEVICE ENROLLED"
            : "OWNER DEVICE NOT YET ENROLLED";

    public string Stage7SessionLabel =>
        OwnerTailnet.ActiveSessionIssued
            ? "ACTIVE OWNER SESSION"
            : "NO ACTIVE OWNER SESSION";

    public string Stage7PhoneLabel =>
        OwnerTailnet.PhoneRoundTripProven
            ? "REAL PHONE ROUNDTRIP PROVEN"
            : "REAL PHONE ROUNDTRIP PENDING";

    public string Stage7ExecutionLabel =>
        $"{OwnerTailnet.ExecutionState} / execution remains locked";
}
