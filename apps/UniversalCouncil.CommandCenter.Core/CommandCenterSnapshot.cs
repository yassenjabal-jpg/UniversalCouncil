namespace UniversalCouncil.CommandCenter.Core;

public enum ModuleState
{
    Locked,
    NotConnected,
    ReadOnly,
    ReadyForIntegration
}

public sealed record ModuleStatus(
    string Id,
    string DisplayName,
    string Description,
    ModuleState State,
    string StateLabel);

public sealed record CommandCenterSnapshot(
    string ProductName,
    string StageLabel,
    string PhaseGateLabel,
    bool ExecutionEnabled,
    string ExecutionStateLabel,
    string OwnerApprovalLabel,
    IReadOnlyList<ModuleStatus> Modules);
