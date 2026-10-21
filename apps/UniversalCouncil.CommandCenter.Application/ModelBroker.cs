using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter.Application;

public sealed class ModelBroker : IModelBroker
{
    private static readonly string[] ExpectedPrecedence =
    [
        "TASK_OVERRIDE",
        "ROLE_OVERRIDE",
        "PROJECT_DEFAULT",
        "GLOBAL_DEFAULT"
    ];

    private readonly IModelBrokerPolicyReader reader;
    private readonly ICapabilityRegistry capabilities;

    public ModelBroker(
        IModelBrokerPolicyReader reader,
        ICapabilityRegistry capabilities)
    {
        this.reader = reader;
        this.capabilities = capabilities;
    }

    public ModelSelectionResult Select(ModelSelectionRequest request)
    {
        if (request.ReasoningPath == GatewayReasoningPath.Deterministic)
        {
            return new(
                ModelSelectionState.NotRequired,
                string.Empty,
                string.Empty,
                "NOT_REQUIRED",
                false,
                "Deterministic reasoning path requires no model.",
                false,
                false,
                false);
        }

        var policy = reader.Read();
        ValidatePolicy(policy);
        ValidatePreferences(request.Preferences, policy);

        var preference = ResolvePreference(request.Preferences);
        if (preference.ModelId.Length == 0)
        {
            return new(
                ModelSelectionState.OwnerSelectionRequired,
                string.Empty,
                string.Empty,
                "OWNER_SELECTION_REQUIRED",
                false,
                "No Task/Role/Project/Global model preference is configured.",
                false,
                false,
                false);
        }

        var primary = EvaluateCandidate(
            preference.ModelId,
            request.Preferences,
            policy);

        if (primary.Eligible)
        {
            return Selected(
                primary.Model!,
                preference.Level,
                fallbackUsed: false,
                "Preferred model is eligible for selection.");
        }

        if (request.Preferences.FallbackMode == ModelFallbackMode.Disabled)
        {
            return new(
                ModelSelectionState.Unavailable,
                string.Empty,
                string.Empty,
                preference.Level,
                false,
                $"Preferred model is unavailable and fallback is disabled: {primary.Reason}",
                false,
                false,
                false);
        }

        foreach (var fallbackId in request.Preferences.AllowedFallbackModelIds)
        {
            if (fallbackId == preference.ModelId)
            {
                continue;
            }

            var fallback = EvaluateCandidate(
                fallbackId,
                request.Preferences,
                policy);

            if (!fallback.Eligible)
            {
                continue;
            }

            return Selected(
                fallback.Model!,
                preference.Level,
                fallbackUsed: true,
                $"Explicitly allowlisted fallback selected because preferred model was unavailable: {primary.Reason}");
        }

        return new(
            ModelSelectionState.Unavailable,
            string.Empty,
            string.Empty,
            preference.Level,
            false,
            $"No explicitly allowlisted fallback is eligible. Preferred failure: {primary.Reason}",
            false,
            false,
            false);
    }

    private ModelEvaluation EvaluateCandidate(
        string modelId,
        ModelRoutingPreferences preferences,
        ModelBrokerPolicyDocument policy)
    {
        var model = policy.Models.SingleOrDefault(item => item.ModelId == modelId);
        if (model is null)
        {
            return new(false, null, $"Model is not present in broker policy: {modelId}");
        }

        if (!model.Enabled)
        {
            return new(false, model, $"Model is disabled: {modelId}");
        }

        if (!policy.ProviderCallsConnected || !model.ProviderConnected)
        {
            return new(false, model, $"Model provider is not connected: {model.ProviderId}");
        }

        var required = preferences.RequiredCapabilities.ToHashSet(StringComparer.Ordinal);
        if (!required.IsSubsetOf(model.Capabilities))
        {
            return new(false, model, $"Model lacks one or more required capabilities: {modelId}");
        }

        if (Rank(model.QualityTier, policy.QualityOrder, "quality") <
            Rank(preferences.MinimumQualityTier, policy.QualityOrder, "minimum quality"))
        {
            return new(false, model, $"Model quality is below the requested floor: {modelId}");
        }

        if (Rank(model.CostTier, policy.CostOrder, "cost") >
            Rank(preferences.MaximumCostTier, policy.CostOrder, "maximum cost"))
        {
            return new(false, model, $"Model cost exceeds the requested ceiling: {modelId}");
        }

        if (Rank(model.PrivacyClass, policy.PrivacyOrder, "privacy") >
            Rank(preferences.RequiredPrivacyClass, policy.PrivacyOrder, "required privacy"))
        {
            return new(false, model, $"Model privacy class is less restrictive than allowed: {modelId}");
        }

        var capability = capabilities.Resolve(
            new(
                model.CapabilityOperation,
                CapabilityEffect.Execute,
                model.ProviderId,
                model.EnvironmentHost));

        if (capability.State is not (
                CapabilityResolutionState.Available or
                CapabilityResolutionState.Degraded))
        {
            return new(
                false,
                model,
                $"Model invocation capability is not eligible: {capability.State} / {capability.Reason}");
        }

        return new(true, model, "eligible");
    }

    private static ModelSelectionResult Selected(
        ModelCandidateDocument model,
        string preferenceLevel,
        bool fallbackUsed,
        string reason) =>
        new(
            ModelSelectionState.Selected,
            model.ModelId,
            model.ProviderId,
            preferenceLevel,
            fallbackUsed,
            reason,
            true,
            false,
            false);

    private static (string ModelId, string Level) ResolvePreference(
        ModelRoutingPreferences preferences)
    {
        if (!string.IsNullOrWhiteSpace(preferences.TaskOverrideModelId))
        {
            return (preferences.TaskOverrideModelId, "TASK_OVERRIDE");
        }

        if (!string.IsNullOrWhiteSpace(preferences.RoleOverrideModelId))
        {
            return (preferences.RoleOverrideModelId, "ROLE_OVERRIDE");
        }

        if (!string.IsNullOrWhiteSpace(preferences.ProjectDefaultModelId))
        {
            return (preferences.ProjectDefaultModelId, "PROJECT_DEFAULT");
        }

        if (!string.IsNullOrWhiteSpace(preferences.GlobalDefaultModelId))
        {
            return (preferences.GlobalDefaultModelId, "GLOBAL_DEFAULT");
        }

        return (string.Empty, "OWNER_SELECTION_REQUIRED");
    }

    private static void ValidatePolicy(ModelBrokerPolicyDocument policy)
    {
        if (policy.SchemaVersion != "1.0" ||
            policy.SourceType != "project_local_repository_projection" ||
            policy.PolicyId != "murtakaz-model-broker" ||
            policy.Status != "SELECTION_ONLY")
        {
            throw new ModelBrokerException(
                "Unsupported Model Broker policy identity/status.");
        }

        if (!policy.OwnerControlled ||
            policy.SilentFallbackAllowed ||
            !policy.SelectionPrecedence.SequenceEqual(ExpectedPrecedence))
        {
            throw new ModelBrokerException(
                "Model Broker owner-control/fallback precedence drifted.");
        }

        if (!policy.AllowedFallbackModes.SequenceEqual(
                new[] { "Disabled", "ExplicitAllowlist" }))
        {
            throw new ModelBrokerException(
                "Model Broker fallback modes drifted.");
        }

        ValidateOrderedUnique(policy.QualityOrder, "quality order");
        ValidateOrderedUnique(policy.CostOrder, "cost order");
        ValidateOrderedUnique(policy.PrivacyOrder, "privacy order");

        var ids = policy.Models.Select(item => item.ModelId).ToArray();
        if (ids.Distinct(StringComparer.Ordinal).Count() != ids.Length)
        {
            throw new ModelBrokerException(
                "Model ids must be unique.");
        }

        foreach (var model in policy.Models)
        {
            Require(model.ModelId, nameof(model.ModelId));
            Require(model.ProviderId, nameof(model.ProviderId));
            Require(model.CapabilityOperation, nameof(model.CapabilityOperation));
            Require(model.EnvironmentHost, nameof(model.EnvironmentHost));
            Require(model.QualityTier, nameof(model.QualityTier));
            Require(model.CostTier, nameof(model.CostTier));
            Require(model.PrivacyClass, nameof(model.PrivacyClass));

            if (model.Capabilities.Count == 0 ||
                model.Capabilities.Any(string.IsNullOrWhiteSpace) ||
                model.Capabilities.Distinct(StringComparer.Ordinal).Count() != model.Capabilities.Count)
            {
                throw new ModelBrokerException(
                    $"Model capabilities must be explicit and unique: {model.ModelId}");
            }

            _ = Rank(model.QualityTier, policy.QualityOrder, "quality");
            _ = Rank(model.CostTier, policy.CostOrder, "cost");
            _ = Rank(model.PrivacyClass, policy.PrivacyOrder, "privacy");

            if (model.ContextWindow <= 0)
            {
                throw new ModelBrokerException(
                    $"Model context window must be positive: {model.ModelId}");
            }

            if (model.ProviderConnected && !policy.ProviderCallsConnected)
            {
                throw new ModelBrokerException(
                    $"Model cannot claim connected provider while provider calls are globally disconnected: {model.ModelId}");
            }
        }
    }

    private static void ValidatePreferences(
        ModelRoutingPreferences preferences,
        ModelBrokerPolicyDocument policy)
    {
        ValidateDistinct(preferences.AllowedFallbackModelIds, "fallback allowlist");
        ValidateDistinctNonEmpty(preferences.RequiredCapabilities, "required model capabilities");

        if (!policy.AllowedFallbackModes.Contains(
                preferences.FallbackMode.ToString(),
                StringComparer.Ordinal))
        {
            throw new ModelBrokerException(
                $"Unsupported fallback mode: {preferences.FallbackMode}");
        }

        if (preferences.FallbackMode == ModelFallbackMode.Disabled &&
            preferences.AllowedFallbackModelIds.Count != 0)
        {
            throw new ModelBrokerException(
                "Fallback allowlist must be empty when fallback is disabled.");
        }

        if (preferences.FallbackMode == ModelFallbackMode.ExplicitAllowlist &&
            preferences.AllowedFallbackModelIds.Count == 0)
        {
            throw new ModelBrokerException(
                "ExplicitAllowlist mode requires at least one fallback model id.");
        }

        _ = Rank(preferences.MinimumQualityTier, policy.QualityOrder, "minimum quality");
        _ = Rank(preferences.MaximumCostTier, policy.CostOrder, "maximum cost");
        _ = Rank(preferences.RequiredPrivacyClass, policy.PrivacyOrder, "required privacy");
    }

    private static int Rank(
        string value,
        IReadOnlyList<string> order,
        string label)
    {
        var index = order.IndexOf(value);
        if (index < 0)
        {
            throw new ModelBrokerException(
                $"Unknown {label} tier: {value}");
        }

        return index;
    }

    private static void ValidateOrderedUnique(
        IReadOnlyList<string> values,
        string label)
    {
        ValidateDistinctNonEmpty(values, label);
    }

    private static void ValidateDistinctNonEmpty(
        IReadOnlyList<string> values,
        string label)
    {
        if (values.Count == 0)
        {
            throw new ModelBrokerException($"{label} may not be empty.");
        }

        ValidateDistinct(values, label);
    }

    private static void ValidateDistinct(
        IReadOnlyList<string> values,
        string label)
    {
        if (values.Any(string.IsNullOrWhiteSpace) ||
            values.Distinct(StringComparer.Ordinal).Count() != values.Count)
        {
            throw new ModelBrokerException(
                $"{label} must be explicit and unique.");
        }
    }

    private static void Require(string value, string name)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            throw new ModelBrokerException(
                $"Model Broker field is required: {name}");
        }
    }

    private sealed record ModelEvaluation(
        bool Eligible,
        ModelCandidateDocument? Model,
        string Reason);
}

internal static class ReadOnlyListExtensions
{
    public static int IndexOf(
        this IReadOnlyList<string> values,
        string value)
    {
        for (var index = 0; index < values.Count; index++)
        {
            if (string.Equals(values[index], value, StringComparison.Ordinal))
            {
                return index;
            }
        }

        return -1;
    }
}
