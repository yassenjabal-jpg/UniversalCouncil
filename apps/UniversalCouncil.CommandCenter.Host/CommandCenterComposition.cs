using UniversalCouncil.CommandCenter.Application;
using UniversalCouncil.CommandCenter.Core;
using UniversalCouncil.CommandCenter.Infrastructure;

namespace UniversalCouncil.CommandCenter.Host;

public sealed record CommandCenterHostServices(
    ICommandCenterSnapshotProvider Shell,
    IOperationalStateProvider Operational);

public static class CommandCenterComposition
{
    public static CommandCenterHostServices Create(string baseDirectory)
    {
        var statePath = Path.Combine(
            baseDirectory,
            "state",
            "command-center-state.json");

        var reader = new JsonOperationalStateReader(statePath);
        var service = new OperationalStateService(reader);

        return new CommandCenterHostServices(service, service);
    }
}
