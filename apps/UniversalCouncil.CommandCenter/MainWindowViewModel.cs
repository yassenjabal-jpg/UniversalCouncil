using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter;

internal sealed class MainWindowViewModel
{
    public MainWindowViewModel(ICommandCenterSnapshotProvider snapshotProvider)
    {
        Snapshot = snapshotProvider.GetSnapshot();
    }

    public CommandCenterSnapshot Snapshot { get; }
}
