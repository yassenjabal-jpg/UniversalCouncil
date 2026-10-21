using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter.Application;

public sealed class RoutingCoordinator : IRoutingCoordinator
{
    private static readonly Dictionary<string, int> MaterialityRank = new(StringComparer.Ordinal)
    {
        ["LOW"] = 0,
        ["MATERIAL"] = 1,
        ["HIGH"] = 2,
        ["CRITICAL"] = 3
    };

    private static readonly Dictionary<string, int> UncertaintyRank = new(StringComparer.Ordinal)
    {
        ["LOW"] = 0,
        ["MEDIUM"] = 1,
        ["HIGH"] = 2
    };

    private readonly IGatewayRoutingPolicyReader reader;

    public RoutingCoordinator(IGatewayRoutingPolicyReader reader)
    {
        this.reader = reader;
    }

    public RoutingPlan Coordinate(RoutingRequest request)
    {
        var policy = reader.Read();
        ValidatePolicy(policy);
        ValidateRequest(request, policy);

        var reasons = new List<string>();

        var approvalRequired = RequiresApproval(request);
        if (approvalRequired)
        {
            reasons.Add("Policy requires explicit approval for this effect/risk/consequence.");
        }

        var reasoningPath = SelectReasoningPath(request, policy);
        reasons.Add($"Reasoning path selected deterministically: {reasoningPath}.");

        var stages = new List<RoutingStageDecision>
        {
            new(
                "intent",
                RoutingStageState.Resolved,
                request.Intent.ToString(),
                "Typed intent accepted; free-text inference is disabled."),
            new(
                "project_context",
                RoutingStageState.Resolved,
                request.ContextCapsuleId,
                "Context was resolved and compiled before routing."),
            BuildAuthorityStage(request, approvalRequired),
            BuildSkillStage(request),
            new(
                "reasoning_path",
                RoutingStageState.Resolved,
                reasoningPath.ToString(),
                "Reasoning path is policy-derived; model strength does not change authority."),
            BuildModelStage(reasoningPath, policy),
            BuildExecutionStage(request, policy),
            new(
                "verification",
                RoutingStageState.Resolved,
                VerificationSelection(request.Effect, policy),
                "Verification requirement is selected from effect class.")
        };

        var state = GatewayPlanState.Planned;
        var projectedUxState = "PLANNING";

        if (approvalRequired && !request.OwnerApprovalPresent)
        {
            state = GatewayPlanState.WaitingForApproval;
            projectedUxState = "WAITING_FOR_APPROVAL";
            reasons.Add("Owner approval is required before the route can progress.");
        }
        else if (request.Effect is GatewayEffect.Write or GatewayEffect.Execute)
        {
            state = GatewayPlanState.Blocked;
            projectedUxState = "BLOCKED";
            reasons.Add("Write/execute dispatch remains blocked while live execution is disabled.");
        }
        else if (reasoningPath != GatewayReasoningPath.Deterministic)
        {
            state = GatewayPlanState.Blocked;
            projectedUxState = "BLOCKED";
            reasons.Add("The selected reasoning path needs a Model Broker, which is not implemented yet.");
        }
        else
        {
            reasons.Add("Read-only deterministic shadow planning is allowed; no dispatch occurs.");
        }

        return new(
            state,
            projectedUxState,
            reasoningPath,
            approvalRequired,
            request.OwnerApprovalPresent && approvalRequired,
            false,
            stages,
            reasons);
    }

    private static RoutingStageDecision BuildAuthorityStage(
        RoutingRequest request,
        bool approvalRequired)
    {
        if (approvalRequired && !request.OwnerApprovalPresent)
        {
            return new(
                "authority_risk",
                RoutingStageState.WaitingForApproval,
                "OWNER_APPROVAL_REQUIRED",
                "Effect/risk/consequence exceeds the no-interruption planning envelope.");
        }

        if (approvalRequired)
        {
            return new(
                "authority_risk",
                RoutingStageState.Resolved,
                "OWNER_APPROVAL_PRESENT",
                $"Approval reference accepted for planning: {request.ApprovalRef}");
        }

        return new(
            "authority_risk",
            RoutingStageState.Resolved,
            "NO_OWNER_APPROVAL_REQUIRED_FOR_SHADOW_PLAN",
            "Read-only low-consequence planning does not require Owner interruption.");
    }

    private static RoutingStageDecision BuildSkillStage(RoutingRequest request)
    {
        var skillRequired = request.Intent is
            GatewayIntent.Plan or
            GatewayIntent.ModifyProject or
            GatewayIntent.ExecuteHost or
            GatewayIntent.ExternalAction or
            GatewayIntent.Recover;

        return skillRequired
            ? new(
                "skill",
                RoutingStageState.DeferredNotImplemented,
                "SKILL_REGISTRY_NOT_IMPLEMENTED",
                "The route may require a governed Skill, but the Skill Registry is a later roadmap slice.")
            : new(
                "skill",
                RoutingStageState.NotRequired,
                "NO_SKILL_REQUIRED_FOR_CURRENT_SHADOW_ROUTE",
                "This typed request can be planned without resolving a reusable Skill.");
    }

    private static RoutingStageDecision BuildModelStage(
        GatewayReasoningPath reasoningPath,
        GatewayRoutingPolicyDocument policy)
    {
        if (reasoningPath == GatewayReasoningPath.Deterministic)
        {
            return new(
                "model",
                RoutingStageState.NotRequired,
                "NO_MODEL_REQUIRED",
                "Deterministic routing path requires no model.");
        }

        if (policy.FutureDependencies.ModelBroker != "NOT_IMPLEMENTED")
        {
            throw new GatewayRoutingPolicyException(
                "Routing policy unexpectedly claims Model Broker availability.");
        }

        return new(
            "model",
            RoutingStageState.DeferredNotImplemented,
            "OWNER_SELECTION_REQUIRED / MODEL_BROKER_NOT_IMPLEMENTED",
            "Role != Model; no model may be silently selected before Model Broker implementation.");
    }

    private static RoutingStageDecision BuildExecutionStage(
        RoutingRequest request,
        GatewayRoutingPolicyDocument policy)
    {
        if (request.Effect == GatewayEffect.Read)
        {
            return new(
                "execution",
                RoutingStageState.Resolved,
                "SHADOW_READ_ONLY_NO_DISPATCH",
                "This slice produces a route plan only and never dispatches a provider.");
        }

        var selection = request.Effect == GatewayEffect.Write
            ? "WRITE_DISPATCH_DISABLED"
            : "EXECUTE_DISPATCH_DISABLED";

        return new(
            "execution",
            RoutingStageState.Blocked,
            selection,
            policy.LiveDispatchAllowed
                ? "Policy inconsistency: live dispatch must remain disabled in this slice."
                : "Live execution remains disabled by Phase 0 / project governance.");
    }

    private static GatewayReasoningPath SelectReasoningPath(
        RoutingRequest request,
        GatewayRoutingPolicyDocument policy)
    {
        var arenaDomains = policy.ArenaDomains.ToHashSet(StringComparer.Ordinal);
        if (request.RiskTier == GatewayRiskTier.T3HighImpact ||
            request.Domains.Any(arenaDomains.Contains) ||
            request.AuthorityExpansionRequested ||
            request.DestructiveOrIrreversible ||
            request.PrivacySensitive ||
            request.SpendOrSubscription)
        {
            return GatewayReasoningPath.MurtakazArena;
        }

        var governanceDomains = policy.GovernanceDomains.ToHashSet(StringComparer.Ordinal);
        if (request.ChangeOfTruthRequested ||
            Rank(request.Materiality, MaterialityRank, "materiality") >=
                MaterialityRank["HIGH"] ||
            Rank(request.Uncertainty, UncertaintyRank, "uncertainty") >=
                UncertaintyRank["HIGH"] ||
            (
                Rank(request.Materiality, MaterialityRank, "materiality") >=
                    MaterialityRank["MATERIAL"] &&
                request.Domains.Any(governanceDomains.Contains)
            ))
        {
            return GatewayReasoningPath.MurtakazGovernance;
        }

        if (request.Effect == GatewayEffect.Read &&
            request.Intent == GatewayIntent.Observe &&
            request.RiskTier is GatewayRiskTier.T0Observe or GatewayRiskTier.T1Reversible &&
            request.Materiality == "LOW" &&
            request.Uncertainty == "LOW")
        {
            return GatewayReasoningPath.Deterministic;
        }

        return GatewayReasoningPath.SingleAgent;
    }

    private static bool RequiresApproval(RoutingRequest request) =>
        request.Effect is GatewayEffect.Write or GatewayEffect.Execute ||
        request.ChangeOfTruthRequested ||
        request.AuthorityExpansionRequested ||
        request.ExternalConsequence ||
        request.DestructiveOrIrreversible ||
        request.PrivacySensitive ||
        request.SpendOrSubscription ||
        request.RiskTier == GatewayRiskTier.T3HighImpact;

    private static string VerificationSelection(
        GatewayEffect effect,
        GatewayRoutingPolicyDocument policy) =>
        effect switch
        {
            GatewayEffect.Read => policy.VerificationPolicy.Read,
            GatewayEffect.Write => policy.VerificationPolicy.Write,
            GatewayEffect.Execute => policy.VerificationPolicy.Execute,
            _ => throw new GatewayRoutingPolicyException("Unsupported Gateway effect.")
        };

    private static void ValidateRequest(
        RoutingRequest request,
        GatewayRoutingPolicyDocument policy)
    {
        Require(request.ProjectId, nameof(request.ProjectId));
        Require(request.ContextCapsuleId, nameof(request.ContextCapsuleId));

        ValidateAllowed(request.FrontDoor.ToString(), policy.AllowedFrontDoors, "front door");
        ValidateAllowed(request.Intent.ToString(), policy.AllowedIntents, "intent");
        ValidateAllowed(request.Effect.ToString(), policy.AllowedEffects, "effect");
        ValidateAllowed(request.RiskTier.ToString(), policy.RiskTiers, "risk tier");
        ValidateAllowed(request.Materiality, policy.MaterialityLevels, "materiality");
        ValidateAllowed(request.Uncertainty, policy.UncertaintyLevels, "uncertainty");

        if (request.Domains.Count == 0 ||
            request.Domains.Any(string.IsNullOrWhiteSpace) ||
            request.Domains.Distinct(StringComparer.Ordinal).Count() != request.Domains.Count)
        {
            throw new GatewayRoutingPolicyException(
                "Routing domains must be explicit and unique.");
        }

        if (request.OwnerApprovalPresent && string.IsNullOrWhiteSpace(request.ApprovalRef))
        {
            throw new GatewayRoutingPolicyException(
                "OwnerApprovalPresent requires an explicit ApprovalRef.");
        }

        if (!request.OwnerApprovalPresent && !string.IsNullOrWhiteSpace(request.ApprovalRef))
        {
            throw new GatewayRoutingPolicyException(
                "ApprovalRef cannot be supplied when OwnerApprovalPresent is false.");
        }

        if (request.Intent == GatewayIntent.Observe && request.Effect != GatewayEffect.Read)
        {
            throw new GatewayRoutingPolicyException(
                "Observe intent must remain READ-only.");
        }

        if (request.Intent == GatewayIntent.Analyze && request.Effect != GatewayEffect.Read)
        {
            throw new GatewayRoutingPolicyException(
                "Analyze intent must remain READ-only.");
        }

        if (request.Intent == GatewayIntent.Plan && request.Effect != GatewayEffect.Read)
        {
            throw new GatewayRoutingPolicyException(
                "Plan intent describes planning only and must remain READ-only.");
        }

        if (request.Intent == GatewayIntent.ModifyProject && request.Effect != GatewayEffect.Write)
        {
            throw new GatewayRoutingPolicyException(
                "ModifyProject intent must declare WRITE effect.");
        }

        if (request.Intent == GatewayIntent.ExecuteHost && request.Effect != GatewayEffect.Execute)
        {
            throw new GatewayRoutingPolicyException(
                "ExecuteHost intent must declare EXECUTE effect.");
        }

        if (request.Intent == GatewayIntent.ExternalAction &&
            request.Effect == GatewayEffect.Read)
        {
            throw new GatewayRoutingPolicyException(
                "ExternalAction cannot be disguised as READ.");
        }

        if (request.Intent == GatewayIntent.Recover && request.Effect != GatewayEffect.Execute)
        {
            throw new GatewayRoutingPolicyException(
                "Recover intent must declare EXECUTE effect.");
        }

        if (request.Effect == GatewayEffect.Write &&
            request.RiskTier is GatewayRiskTier.T0Observe or GatewayRiskTier.T1Reversible)
        {
            throw new GatewayRoutingPolicyException(
                "WRITE effect cannot be downgraded below T2LocalStateChange.");
        }

        if (request.Effect == GatewayEffect.Execute &&
            request.RiskTier == GatewayRiskTier.T0Observe)
        {
            throw new GatewayRoutingPolicyException(
                "EXECUTE effect cannot be downgraded to T0Observe.");
        }
    }

    private static void ValidatePolicy(GatewayRoutingPolicyDocument policy)
    {
        if (policy.SchemaVersion != "1.0" ||
            policy.SourceType != "project_local_repository_projection" ||
            policy.PolicyId != "murtakaz-gateway-routing" ||
            policy.Status != "SHADOW_PLANNING_ONLY" ||
            policy.ProjectId != "universal-council-command-center")
        {
            throw new GatewayRoutingPolicyException(
                "Unsupported Gateway routing policy identity.");
        }

        if (policy.LiveDispatchAllowed ||
            policy.FreeTextIntentInferenceAllowed ||
            policy.LlmRouteProposalConnected ||
            policy.ExecutionPolicy.LiveExecutionAuthorized ||
            policy.ExecutionPolicy.Stage8Opened ||
            policy.ExecutionPolicy.WriteDispatchAllowed ||
            policy.ExecutionPolicy.ExecuteDispatchAllowed ||
            !policy.ExecutionPolicy.ReadOnlyShadowPlanningAllowed)
        {
            throw new GatewayRoutingPolicyException(
                "Gateway routing policy inflated authority or runtime capability.");
        }

        var expectedStages = new[]
        {
            "intent",
            "project_context",
            "authority_risk",
            "skill",
            "reasoning_path",
            "model",
            "execution",
            "verification"
        };

        if (!policy.StageOrder.SequenceEqual(expectedStages))
        {
            throw new GatewayRoutingPolicyException(
                "Gateway routing stage order drifted.");
        }

        if (policy.FutureDependencies.SkillRegistry != "NOT_IMPLEMENTED" ||
            policy.FutureDependencies.ModelBroker != "NOT_IMPLEMENTED" ||
            policy.FutureDependencies.CapabilityRegistry != "NOT_IMPLEMENTED" ||
            policy.FutureDependencies.JobEngine != "NOT_IMPLEMENTED")
        {
            throw new GatewayRoutingPolicyException(
                "Gateway routing policy fabricated a future dependency.");
        }

        if (policy.VerificationPolicy.Read != "SOURCE_PROVENANCE_REQUIRED" ||
            policy.VerificationPolicy.Write != "INDEPENDENT_POSTCONDITION_REQUIRED" ||
            policy.VerificationPolicy.Execute != "INDEPENDENT_POSTCONDITION_REQUIRED")
        {
            throw new GatewayRoutingPolicyException(
                "Gateway verification policy drifted.");
        }
    }

    private static void ValidateAllowed(
        string value,
        IReadOnlyList<string> allowed,
        string label)
    {
        if (!allowed.Contains(value, StringComparer.Ordinal))
        {
            throw new GatewayRoutingPolicyException(
                $"Unsupported {label}: {value}");
        }
    }

    private static int Rank(
        string value,
        IReadOnlyDictionary<string, int> ranks,
        string label)
    {
        if (!ranks.TryGetValue(value, out var rank))
        {
            throw new GatewayRoutingPolicyException(
                $"Unknown {label}: {value}");
        }

        return rank;
    }

    private static void Require(string value, string name)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            throw new GatewayRoutingPolicyException(
                $"Routing field is required: {name}");
        }
    }
}
