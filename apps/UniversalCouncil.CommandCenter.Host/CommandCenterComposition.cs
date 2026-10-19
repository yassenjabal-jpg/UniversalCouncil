using UniversalCouncil.CommandCenter.Application;
using UniversalCouncil.CommandCenter.Core;
using UniversalCouncil.CommandCenter.Infrastructure;

namespace UniversalCouncil.CommandCenter.Host;

public sealed record CommandCenterHostServices(
    ICommandCenterSnapshotProvider Shell,
    IOperationalStateProvider Operational,
    IOrchestrationCatalogProvider Orchestration,
    ICouncilPlanner CouncilPlanner,
    IExecutionFabricProvider ExecutionFabric,
    IExecutionManifestValidator ExecutionManifestValidator);

public static class CommandCenterComposition
{
    public static CommandCenterHostServices Create(string baseDirectory)
    {
        var statePath = Path.Combine(
            baseDirectory,
            "state",
            "command-center-state.json");

        var orchestrationPath = Path.Combine(
            baseDirectory,
            "state",
            "orchestration-catalog.json");

        var executionFabricPath = Path.Combine(
            baseDirectory,
            "state",
            "execution-fabric.json");

        var stateReader = new JsonOperationalStateReader(statePath);
        var stateService = new OperationalStateService(stateReader);

        var orchestrationReader = new JsonOrchestrationCatalogReader(orchestrationPath);
        var orchestrationService = new OrchestrationService(orchestrationReader);

        var executionReader = new JsonExecutionFabricReader(executionFabricPath);
        var executionService = new ExecutionFabricService(executionReader);

        return new CommandCenterHostServices(
            stateService,
            stateService,
            orchestrationService,
            orchestrationService,
            executionService,
            executionService);
    }
}
