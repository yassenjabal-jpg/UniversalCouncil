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
    IExecutionManifestValidator ExecutionManifestValidator,
    IRemoteOwnerGatewayProvider RemoteOwnerGateway,
    IRemoteTransportProjectionProvider RemoteTransport);

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

        var remoteOwnerPath = Path.Combine(
            baseDirectory,
            "state",
            "remote-owner-gateway.json");

        var remoteOwnerReader = new JsonRemoteOwnerGatewayReader(remoteOwnerPath);
        var remoteOwnerService = new RemoteOwnerProjectionService(remoteOwnerReader);

        var remoteTransportPath = Path.Combine(
            baseDirectory,
            "state",
            "remote-transport.json");

        var remoteTransportReader = new JsonRemoteTransportReader(remoteTransportPath);
        var remoteTransportService = new RemoteTransportProjectionService(remoteTransportReader);

        return new CommandCenterHostServices(
            stateService,
            stateService,
            orchestrationService,
            orchestrationService,
            executionService,
            executionService,
            remoteOwnerService,
            remoteTransportService);
    }
}
