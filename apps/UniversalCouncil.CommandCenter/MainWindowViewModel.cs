using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter;

internal sealed class MainWindowViewModel
{
    public MainWindowViewModel(
        ICommandCenterSnapshotProvider snapshotProvider,
        IOperationalStateProvider operationalStateProvider)
    {
        Snapshot = snapshotProvider.GetSnapshot();
        Operational = operationalStateProvider.GetOperationalState();
    }

    public CommandCenterSnapshot Snapshot { get; }

    public OperationalStateProjection Operational { get; }
}
