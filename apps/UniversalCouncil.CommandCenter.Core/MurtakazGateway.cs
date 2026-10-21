namespace UniversalCouncil.CommandCenter.Core;

public enum GatewayFrontDoor
{
    Windows,
    Android,
    Web,
    Chat,
    Voice
}

public enum GatewayIntent
{
    Observe,
    Analyze,
    Plan,
    ModifyProject,
    ExecuteHost,
    ExternalAction,
    Recover
}

public enum GatewayEffect
{
    Read,
    Write,
    Execute
}

public enum GatewayRiskTier
{
    T0Observe,
    T1Reversible,
    T2LocalStateChange,
    T3HighImpact
}

public enum GatewayPlanState
{
    Planned,
    WaitingForApproval,
    Blocked,
    StaleContext,
    ContextConflict,
    Unavailable
}

public enum GatewayReasoningPath
{
    Deterministic,
    SingleAgent,
    MurtakazGovernance,
    MurtakazArena
}

public enum RoutingStageState
{
    Resolved,
    DeferredNotImplemented,
    NotRequired,
    Blocked,
    WaitingForApproval
}

public sealed record MurtakazGatewayRequest(
    string RequestId,
    string CorrelationId,
    string ProjectId,
    GatewayFrontDoor FrontDoor,
    string Principal,
    bool Authenticated,
    GatewayIntent Intent,
    GatewayEffect Effect,
    GatewayRiskTier RiskTier,
    string Materiality,
    string Uncertainty,
    IReadOnlyList<string> Domains,
    IReadOnlyList<string> RequiredSourceIds,
    IReadOnlyList<string> RequestedScopes,
    IReadOnlyList<string> OwnerDirectiveIds,
    IReadOnlyList<string> AllowedScope,
    IReadOnlyList<string> ForbiddenScope,
    string Instruction,
    bool OwnerApprovalPresent,
    string ApprovalRef,
    bool ChangeOfTruthRequested,
    bool AuthorityExpansionRequested,
    bool ExternalConsequence,
    bool DestructiveOrIrreversible,
    bool PrivacySensitive,
    bool SpendOrSubscription,
    ModelRoutingPreferences ModelPreferences,
    int MaxContextSources,
    DateTimeOffset RequestedAt);

public sealed record RoutingStageDecision(
    string Stage,
    RoutingStageState State,
    string Selection,
    string Reason);

public sealed record RoutingPlan(
    GatewayPlanState State,
    string ProjectedUxState,
    GatewayReasoningPath ReasoningPath,
    bool ApprovalRequired,
    bool ExecutionAuthorized,
    bool LiveDispatchAllowed,
    IReadOnlyList<RoutingStageDecision> Stages,
    IReadOnlyList<string> Reasons);

public sealed record MurtakazGatewayPlan(
    GatewayPlanState State,
    string ProjectedUxState,
    string RequestId,
    string CorrelationId,
    string ProjectId,
    string ContextCapsuleId,
    string SourceRevision,
    RoutingPlan Routing,
    IReadOnlyList<string> CanonicalSourceIds,
    IReadOnlyList<string> ConflictSourceIds,
    bool ChangeOfTruthRequired,
    string ProblemLabel)
{
    public static MurtakazGatewayPlan ContextFailure(
        MurtakazGatewayRequest request,
        GatewayPlanState state,
        string projectedUxState,
        string sourceRevision,
        IReadOnlyList<string> canonicalSourceIds,
        IReadOnlyList<string> conflictSourceIds,
        bool changeOfTruthRequired,
        string problem) =>
        new(
            state,
            projectedUxState,
            request.RequestId,
            request.CorrelationId,
            request.ProjectId,
            string.Empty,
            sourceRevision,
            new(
                state,
                projectedUxState,
                GatewayReasoningPath.Deterministic,
                false,
                false,
                false,
                [],
                [problem]),
            canonicalSourceIds,
            conflictSourceIds,
            changeOfTruthRequired,
            problem);
}

public sealed record RoutingRequest(
    string ProjectId,
    GatewayFrontDoor FrontDoor,
    GatewayIntent Intent,
    GatewayEffect Effect,
    GatewayRiskTier RiskTier,
    string Materiality,
    string Uncertainty,
    IReadOnlyList<string> Domains,
    bool OwnerApprovalPresent,
    string ApprovalRef,
    bool ChangeOfTruthRequested,
    bool AuthorityExpansionRequested,
    bool ExternalConsequence,
    bool DestructiveOrIrreversible,
    bool PrivacySensitive,
    bool SpendOrSubscription,
    ModelRoutingPreferences ModelPreferences,
    string ContextCapsuleId);

public interface IMurtakazCommandGateway
{
    MurtakazGatewayPlan Plan(MurtakazGatewayRequest request);
}

public interface IRoutingCoordinator
{
    RoutingPlan Coordinate(RoutingRequest request);
}
