namespace UniversalCouncil.CommandCenter.Application;

public sealed record GatewayRoutingPolicyDocument(
    string SchemaVersion,
    string SourceType,
    string PolicyId,
    string Status,
    string ProjectId,
    bool LiveDispatchAllowed,
    bool FreeTextIntentInferenceAllowed,
    bool LlmRouteProposalConnected,
    IReadOnlyList<string> AllowedFrontDoors,
    IReadOnlyList<string> AllowedIntents,
    IReadOnlyList<string> AllowedEffects,
    IReadOnlyList<string> RiskTiers,
    IReadOnlyList<string> MaterialityLevels,
    IReadOnlyList<string> UncertaintyLevels,
    IReadOnlyList<string> ApprovalTriggers,
    IReadOnlyList<string> ArenaDomains,
    IReadOnlyList<string> GovernanceDomains,
    IReadOnlyList<string> DeterministicReadIntents,
    GatewayFutureDependenciesDocument FutureDependencies,
    IReadOnlyList<string> StageOrder,
    GatewayExecutionPolicyDocument ExecutionPolicy,
    GatewayVerificationPolicyDocument VerificationPolicy);

public sealed record GatewayFutureDependenciesDocument(
    string SkillRegistry,
    string ModelBroker,
    string CapabilityRegistry,
    string JobEngine);

public sealed record GatewayExecutionPolicyDocument(
    bool ReadOnlyShadowPlanningAllowed,
    bool WriteDispatchAllowed,
    bool ExecuteDispatchAllowed,
    bool LiveExecutionAuthorized,
    bool Stage8Opened);

public sealed record GatewayVerificationPolicyDocument(
    string Read,
    string Write,
    string Execute);

public interface IGatewayRoutingPolicyReader
{
    GatewayRoutingPolicyDocument Read();
}

public sealed class GatewayRoutingPolicyException : Exception
{
    public GatewayRoutingPolicyException(string message) : base(message) { }

    public GatewayRoutingPolicyException(string message, Exception inner) : base(message, inner) { }
}
