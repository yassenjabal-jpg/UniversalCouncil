using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter;

internal sealed class MainWindowViewModel
{
    public MainWindowViewModel(
        ICommandCenterSnapshotProvider snapshotProvider,
        IOperationalStateProvider operationalStateProvider,
        IOrchestrationCatalogProvider orchestrationProvider,
        IExecutionFabricProvider executionFabricProvider)
    {
        Snapshot = snapshotProvider.GetSnapshot();
        Operational = operationalStateProvider.GetOperationalState();
        Orchestration = orchestrationProvider.GetCatalog();
        ExecutionFabric = executionFabricProvider.GetFabric();
    }

    public CommandCenterSnapshot Snapshot { get; }

    public OperationalStateProjection Operational { get; }

    public OrchestrationCatalogProjection Orchestration { get; }

    public ExecutionFabricProjection ExecutionFabric { get; }

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
}
