namespace UniversalCouncil.CommandCenter.Core;

public enum CapabilityHealth
{
    Healthy,
    Degraded,
    Stale,
    InTest,
    Unavailable,
    Blocked
}

public enum CapabilityEffect
{
    Read,
    Write,
    Execute
}

public enum CapabilityResolutionState
{
    Available,
    Degraded,
    Stale,
    Unavailable,
    Blocked,
    Ambiguous
}

public sealed record CapabilityProjection(
    string Id,
    string ProviderId,
    string Operation,
    string VersionHash,
    CapabilityHealth Health,
    string AuthenticationState,
    CapabilityEffect Effect,
    string Risk,
    string LatencyCost,
    DateTimeOffset VerifiedAt,
    int TtlSeconds,
    string EnvironmentHost,
    string EvidenceLevel,
    bool FallbackEligible,
    string FailureReason);

public sealed record CapabilityRegistrySnapshot(
    string RegistryId,
    DateTimeOffset ObservedAt,
    IReadOnlyList<CapabilityProjection> Capabilities);

public sealed record CapabilityResolutionRequest(
    string Operation,
    CapabilityEffect Effect,
    string ProviderId,
    string EnvironmentHost);

public sealed record CapabilityResolutionResult(
    CapabilityResolutionState State,
    string Reason,
    CapabilityProjection? Capability);

public interface ICapabilityRegistry
{
    CapabilityRegistrySnapshot GetSnapshot();

    CapabilityResolutionResult Resolve(CapabilityResolutionRequest request);
}

public enum ModelFallbackMode
{
    Disabled,
    ExplicitAllowlist
}

public enum ModelSelectionState
{
    NotRequired,
    Selected,
    OwnerSelectionRequired,
    Unavailable,
    Blocked
}

public sealed record ModelRoutingPreferences(
    string TaskOverrideModelId,
    string RoleOverrideModelId,
    string ProjectDefaultModelId,
    string GlobalDefaultModelId,
    ModelFallbackMode FallbackMode,
    IReadOnlyList<string> AllowedFallbackModelIds,
    IReadOnlyList<string> RequiredCapabilities,
    string MinimumQualityTier,
    string MaximumCostTier,
    string RequiredPrivacyClass);

public sealed record ModelCandidateProjection(
    string ModelId,
    string ProviderId,
    string CapabilityOperation,
    string EnvironmentHost,
    bool Enabled,
    bool ProviderConnected,
    IReadOnlyList<string> Capabilities,
    string QualityTier,
    string CostTier,
    string PrivacyClass,
    int ContextWindow);

public sealed record ModelSelectionRequest(
    GatewayReasoningPath ReasoningPath,
    ModelRoutingPreferences Preferences);

public sealed record ModelSelectionResult(
    ModelSelectionState State,
    string ModelId,
    string ProviderId,
    string PreferenceLevel,
    bool FallbackUsed,
    string Reason,
    bool ProviderInvocationEligible,
    bool ProviderInvocationAuthorized,
    bool ExecutionAuthorityGranted);

public interface IModelBroker
{
    ModelSelectionResult Select(ModelSelectionRequest request);
}
