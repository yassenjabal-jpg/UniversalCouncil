namespace UniversalCouncil.CommandCenter.Core;

public enum ExecutionFabricHealth
{
    Healthy,
    Unavailable
}

public sealed record Phase0GateProjection(
    string Id,
    string Name,
    string Status);

public sealed record ExecutionProviderProjection(
    string Id,
    string DisplayName,
    string Role,
    string State,
    bool CanObserve,
    bool CanExecute,
    string Source,
    string Note);

public sealed record ExecutionFabricProjection(
    ExecutionFabricHealth Health,
    string ProblemLabel,
    string ServiceMode,
    string TargetHost,
    bool LiveDispatchEnabled,
    IReadOnlyList<Phase0GateProjection> Phase0Gates,
    IReadOnlyList<ExecutionProviderProjection> Providers,
    IReadOnlyList<string> AllowedCliCommands,
    IReadOnlyList<string> ForbiddenCliCommands,
    bool UnknownIsNeverSuccess,
    bool SinglePhysicalController)
{
    public static ExecutionFabricProjection Unavailable(string problem) =>
        new(
            ExecutionFabricHealth.Unavailable,
            problem,
            "UNAVAILABLE",
            "UNKNOWN",
            false,
            [],
            [],
            [],
            [],
            true,
            true);
}

public sealed record ExecutionManifest(
    string ManifestId,
    string TaskId,
    string Requester,
    string TargetHost,
    string AuthorityOperation,
    string ActionKind,
    string Effect,
    string RiskTier,
    string ExpectedPostcondition,
    string VerificationMethod,
    string ApprovalRef,
    DateTimeOffset ExpiresAt,
    string IdempotencyKey);

public sealed record ExecutionReceipt(
    string ManifestId,
    string TaskId,
    string State,
    string Reason,
    string TargetHost,
    DateTimeOffset RecordedAt);

public sealed record ControllerLeaseToken(
    string Resource,
    string Holder,
    string SessionId,
    long FencingToken,
    DateTimeOffset AcquiredAt);

public interface IExecutionFabricProvider
{
    ExecutionFabricProjection GetFabric();
}

public interface IExecutionManifestValidator
{
    void Validate(ExecutionManifest manifest);

    ExecutionReceipt EvaluateForDispatch(ExecutionManifest manifest);
}

public interface IControllerLease
{
    ControllerLeaseToken Acquire(string resource, string holder, string sessionId);

    void AssertCurrent(ControllerLeaseToken token);

    void Release(ControllerLeaseToken token);
}

public interface IExecutionJournal
{
    void RecordIntent(ExecutionManifest manifest);

    void RecordReceipt(ExecutionReceipt receipt);

    IReadOnlyList<string> PendingManifestIds(string taskId);
}
