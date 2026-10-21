using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter.Application;

public sealed class CapabilityRegistryService : ICapabilityRegistry
{
    private static readonly HashSet<string> AllowedAuthenticationStates =
    [
        "INTERNAL",
        "CONNECTED",
        "NOT_CONNECTED",
        "OWNER_GATED",
        "BLOCKED"
    ];

    private readonly ICapabilityRegistryReader reader;
    private readonly Func<DateTimeOffset> utcNow;

    public CapabilityRegistryService(
        ICapabilityRegistryReader reader,
        Func<DateTimeOffset>? utcNow = null)
    {
        this.reader = reader;
        this.utcNow = utcNow ?? (() => DateTimeOffset.UtcNow);
    }

    public CapabilityRegistrySnapshot GetSnapshot()
    {
        var document = reader.Read();
        ValidateDocument(document);

        return new(
            document.RegistryId,
            document.ObservedAt,
            document.Capabilities
                .OrderBy(item => item.Operation, StringComparer.Ordinal)
                .ThenBy(item => item.ProviderId, StringComparer.Ordinal)
                .Select(Project)
                .ToArray());
    }

    public CapabilityResolutionResult Resolve(CapabilityResolutionRequest request)
    {
        ValidateRequest(request);

        var snapshot = GetSnapshot();
        var candidates = snapshot.Capabilities
            .Where(item =>
                item.Operation == request.Operation &&
                item.Effect == request.Effect)
            .Where(item =>
                string.IsNullOrWhiteSpace(request.ProviderId) ||
                item.ProviderId == request.ProviderId)
            .Where(item =>
                string.IsNullOrWhiteSpace(request.EnvironmentHost) ||
                item.EnvironmentHost == request.EnvironmentHost)
            .ToArray();

        if (candidates.Length == 0)
        {
            return new(
                CapabilityResolutionState.Unavailable,
                "No capability matches the requested operation/effect/provider/host.",
                null);
        }

        if (candidates.Length > 1 && string.IsNullOrWhiteSpace(request.ProviderId))
        {
            return new(
                CapabilityResolutionState.Ambiguous,
                "Multiple providers match; provider selection must be explicit.",
                null);
        }

        var capability = candidates[0];

        if (capability.AuthenticationState == "BLOCKED")
        {
            return new(
                CapabilityResolutionState.Blocked,
                string.IsNullOrWhiteSpace(capability.FailureReason)
                    ? "Capability authentication is blocked."
                    : capability.FailureReason,
                capability);
        }

        if (capability.AuthenticationState == "NOT_CONNECTED")
        {
            return new(
                CapabilityResolutionState.Unavailable,
                string.IsNullOrWhiteSpace(capability.FailureReason)
                    ? "Capability provider is not connected."
                    : capability.FailureReason,
                capability);
        }

        return capability.Health switch
        {
            CapabilityHealth.Healthy => new(
                CapabilityResolutionState.Available,
                "Capability is current and eligible.",
                capability),
            CapabilityHealth.Degraded => new(
                CapabilityResolutionState.Degraded,
                "Capability is current but degraded.",
                capability),
            CapabilityHealth.Stale => new(
                CapabilityResolutionState.Stale,
                "Capability evidence expired; refresh is required.",
                capability),
            CapabilityHealth.InTest => new(
                CapabilityResolutionState.Unavailable,
                "Capability is IN_TEST and not eligible for production use.",
                capability),
            CapabilityHealth.Blocked => new(
                CapabilityResolutionState.Blocked,
                string.IsNullOrWhiteSpace(capability.FailureReason)
                    ? "Capability is blocked."
                    : capability.FailureReason,
                capability),
            CapabilityHealth.Unavailable => new(
                CapabilityResolutionState.Unavailable,
                string.IsNullOrWhiteSpace(capability.FailureReason)
                    ? "Capability is unavailable."
                    : capability.FailureReason,
                capability),
            _ => throw new CapabilityRegistryException(
                "Unsupported effective capability health.")
        };
    }

    private CapabilityProjection Project(CapabilityEntryDocument item)
    {
        var rawHealth = ParseHealth(item.Health);
        var effectiveHealth = rawHealth;

        if (rawHealth is
                CapabilityHealth.Healthy or
                CapabilityHealth.Degraded or
                CapabilityHealth.InTest &&
            utcNow() > item.VerifiedAt.AddSeconds(item.TtlSeconds))
        {
            effectiveHealth = CapabilityHealth.Stale;
        }

        return new(
            item.Id,
            item.ProviderId,
            item.Operation,
            item.VersionHash,
            effectiveHealth,
            item.AuthenticationState,
            ParseEffect(item.Effect),
            item.Risk,
            item.LatencyCost,
            item.VerifiedAt,
            item.TtlSeconds,
            item.EnvironmentHost,
            item.EvidenceLevel,
            item.FallbackEligible,
            item.FailureReason);
    }

    private static void ValidateDocument(CapabilityRegistryDocument document)
    {
        if (document.SchemaVersion != "1.0" ||
            document.SourceType != "project_local_repository_projection" ||
            document.RegistryId != "murtakaz-capability-registry" ||
            document.Status != "READ_ONLY_OPERATION_TRUTH")
        {
            throw new CapabilityRegistryException(
                "Unsupported Capability Registry identity/status.");
        }

        if (document.ObservedAt == default)
        {
            throw new CapabilityRegistryException(
                "Capability Registry observed_at is required.");
        }

        if (document.Capabilities.Count == 0)
        {
            throw new CapabilityRegistryException(
                "Capability Registry must contain operation-specific entries.");
        }

        var ids = document.Capabilities.Select(item => item.Id).ToArray();
        if (ids.Distinct(StringComparer.Ordinal).Count() != ids.Length)
        {
            throw new CapabilityRegistryException(
                "Capability ids must be unique.");
        }

        var operationProviderPairs = document.Capabilities
            .Select(item => $"{item.Operation}{item.ProviderId}{item.EnvironmentHost}")
            .ToArray();
        if (operationProviderPairs.Distinct(StringComparer.Ordinal).Count() != operationProviderPairs.Length)
        {
            throw new CapabilityRegistryException(
                "Capability operation/provider/host tuples must be unique.");
        }

        foreach (var item in document.Capabilities)
        {
            Require(item.Id, nameof(item.Id));
            Require(item.ProviderId, nameof(item.ProviderId));
            Require(item.Operation, nameof(item.Operation));
            Require(item.VersionHash, nameof(item.VersionHash));
            Require(item.Risk, nameof(item.Risk));
            Require(item.LatencyCost, nameof(item.LatencyCost));
            Require(item.EnvironmentHost, nameof(item.EnvironmentHost));
            Require(item.EvidenceLevel, nameof(item.EvidenceLevel));

            _ = ParseHealth(item.Health);
            _ = ParseEffect(item.Effect);

            if (!AllowedAuthenticationStates.Contains(item.AuthenticationState))
            {
                throw new CapabilityRegistryException(
                    $"Unsupported authentication state: {item.AuthenticationState}");
            }

            if (item.VerifiedAt == default ||
                item.TtlSeconds <= 0 ||
                item.TtlSeconds > 2_592_000)
            {
                throw new CapabilityRegistryException(
                    $"Invalid freshness contract for capability: {item.Id}");
            }

            if (item.Health is "BLOCKED" or "UNAVAILABLE" &&
                string.IsNullOrWhiteSpace(item.FailureReason))
            {
                throw new CapabilityRegistryException(
                    $"Blocked/unavailable capability requires a failure reason: {item.Id}");
            }
        }
    }

    private static void ValidateRequest(CapabilityResolutionRequest request)
    {
        Require(request.Operation, nameof(request.Operation));

        if (request.ProviderId is null ||
            request.EnvironmentHost is null)
        {
            throw new CapabilityRegistryException(
                "ProviderId/EnvironmentHost must be explicit strings; use empty string for no filter.");
        }
    }

    private static CapabilityHealth ParseHealth(string value) =>
        value switch
        {
            "HEALTHY" => CapabilityHealth.Healthy,
            "DEGRADED" => CapabilityHealth.Degraded,
            "STALE" => CapabilityHealth.Stale,
            "IN_TEST" => CapabilityHealth.InTest,
            "UNAVAILABLE" => CapabilityHealth.Unavailable,
            "BLOCKED" => CapabilityHealth.Blocked,
            _ => throw new CapabilityRegistryException(
                $"Unsupported capability health: {value}")
        };

    private static CapabilityEffect ParseEffect(string value) =>
        value switch
        {
            "READ" => CapabilityEffect.Read,
            "WRITE" => CapabilityEffect.Write,
            "EXECUTE" => CapabilityEffect.Execute,
            _ => throw new CapabilityRegistryException(
                $"Unsupported capability effect: {value}")
        };

    private static void Require(string value, string name)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            throw new CapabilityRegistryException(
                $"Capability field is required: {name}");
        }
    }
}
