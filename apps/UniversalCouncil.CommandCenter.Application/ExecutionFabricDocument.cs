namespace UniversalCouncil.CommandCenter.Application;

public sealed record ExecutionFabricDocument(
    string SchemaVersion,
    string SourceType,
    IReadOnlyList<ExecutionSourceDocument> SourceFiles,
    Phase0Document Phase0,
    ExecutionServiceDocument Service,
    ExecutionContractDocument ExecutionContract,
    ExecutionRouterDocument Router,
    IReadOnlyList<ExecutionProviderDocument> Providers,
    ExecutionRecoveryDocument Recovery,
    IReadOnlyList<string> ReceiptStates);

public sealed record ExecutionSourceDocument(string Path, string BlobSha);

public sealed record Phase0Document(
    string SchemaVersion,
    string SourceBranch,
    string SourceHeadSha,
    string StatusDocument,
    string StatusBlobSha,
    IReadOnlyDictionary<string, Phase0GateDocument> Gates,
    bool LiveExecutionAuthorized,
    string Reason);

public sealed record Phase0GateDocument(string Name, string Status);

public sealed record ExecutionServiceDocument(
    string Mode,
    string TargetHost,
    bool LiveDispatchEnabled,
    IReadOnlyList<string> AllowedCliCommands,
    IReadOnlyList<string> ForbiddenCliCommands);

public sealed record ExecutionContractDocument(
    string Version,
    string Status,
    IReadOnlyList<string> CouncilOwns,
    IReadOnlyList<string> OrchestratorOwns,
    bool OrchestratorIsVotingMember);

public sealed record ExecutionRouterDocument(
    string Version,
    string Status,
    IReadOnlyDictionary<string, object> TaskClasses,
    IReadOnlyList<string> FallbackRestrictions,
    IReadOnlyList<string> RecoveryRequires,
    string HybridPrimaryPlane,
    string HybridSecondaryPlane);

public sealed record ExecutionProviderDocument(
    string Id,
    string DisplayName,
    string Role,
    string State,
    bool CanObserve,
    bool CanExecute,
    string Source,
    string Note);

public sealed record ExecutionRecoveryDocument(
    bool UnknownIsNeverSuccess,
    bool StopOnUnknown,
    bool UnknownRequiresReconciliation,
    bool ReplayCompletedActionDefault,
    bool SinglePhysicalController);

public interface IExecutionFabricReader
{
    ExecutionFabricDocument Read();
}

public sealed class ExecutionFabricReadException : Exception
{
    public ExecutionFabricReadException(string message) : base(message) { }

    public ExecutionFabricReadException(string message, Exception inner) : base(message, inner) { }
}
