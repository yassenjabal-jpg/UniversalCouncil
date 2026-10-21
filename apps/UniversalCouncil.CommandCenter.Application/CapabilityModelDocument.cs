namespace UniversalCouncil.CommandCenter.Application;

public sealed record CapabilityRegistryDocument(
    string SchemaVersion,
    string SourceType,
    string RegistryId,
    string Status,
    DateTimeOffset ObservedAt,
    IReadOnlyList<CapabilityEntryDocument> Capabilities);

public sealed record CapabilityEntryDocument(
    string Id,
    string ProviderId,
    string Operation,
    string VersionHash,
    string Health,
    string AuthenticationState,
    string Effect,
    string Risk,
    string LatencyCost,
    DateTimeOffset VerifiedAt,
    int TtlSeconds,
    string EnvironmentHost,
    string EvidenceLevel,
    bool FallbackEligible,
    string FailureReason);

public interface ICapabilityRegistryReader
{
    CapabilityRegistryDocument Read();
}

public sealed record ModelBrokerPolicyDocument(
    string SchemaVersion,
    string SourceType,
    string PolicyId,
    string Status,
    bool OwnerControlled,
    bool SilentFallbackAllowed,
    bool ProviderCallsConnected,
    IReadOnlyList<string> SelectionPrecedence,
    IReadOnlyList<string> AllowedFallbackModes,
    IReadOnlyList<string> QualityOrder,
    IReadOnlyList<string> CostOrder,
    IReadOnlyList<string> PrivacyOrder,
    IReadOnlyList<ModelCandidateDocument> Models);

public sealed record ModelCandidateDocument(
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

public interface IModelBrokerPolicyReader
{
    ModelBrokerPolicyDocument Read();
}

public sealed class CapabilityRegistryException : Exception
{
    public CapabilityRegistryException(string message) : base(message) { }

    public CapabilityRegistryException(string message, Exception inner) : base(message, inner) { }
}

public sealed class ModelBrokerException : Exception
{
    public ModelBrokerException(string message) : base(message) { }

    public ModelBrokerException(string message, Exception inner) : base(message, inner) { }
}
