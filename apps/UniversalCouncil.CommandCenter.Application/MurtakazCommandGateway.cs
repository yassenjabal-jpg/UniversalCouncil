using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter.Application;

public sealed class MurtakazCommandGateway : IMurtakazCommandGateway
{
    private readonly IProjectContextResolver contextResolver;
    private readonly IContextCapsuleCompiler capsuleCompiler;
    private readonly IRoutingCoordinator routingCoordinator;

    public MurtakazCommandGateway(
        IProjectContextResolver contextResolver,
        IContextCapsuleCompiler capsuleCompiler,
        IRoutingCoordinator routingCoordinator)
    {
        this.contextResolver = contextResolver;
        this.capsuleCompiler = capsuleCompiler;
        this.routingCoordinator = routingCoordinator;
    }

    public MurtakazGatewayPlan Plan(MurtakazGatewayRequest request)
    {
        try
        {
            ValidateRequest(request);

            var context = contextResolver.Resolve(
                new(
                    request.ProjectId,
                    request.Domains,
                    request.RequiredSourceIds,
                    request.RequestedScopes,
                    IncludeUntrustedData: false,
                    request.MaxContextSources));

            if (context.State == ContextResolutionState.StaleContext)
            {
                return MurtakazGatewayPlan.ContextFailure(
                    request,
                    GatewayPlanState.StaleContext,
                    "STALE_CONTEXT",
                    context.SourceRevision,
                    context.Sources.Select(item => item.Id).ToArray(),
                    [],
                    context.ChangeOfTruthRequired,
                    context.ProblemLabel);
            }

            if (context.State == ContextResolutionState.ContextConflict)
            {
                return MurtakazGatewayPlan.ContextFailure(
                    request,
                    GatewayPlanState.ContextConflict,
                    "CONTEXT_CONFLICT",
                    context.SourceRevision,
                    context.Sources.Select(item => item.Id).ToArray(),
                    context.Conflicts
                        .SelectMany(item => item.SourceIds)
                        .Distinct(StringComparer.Ordinal)
                        .OrderBy(item => item, StringComparer.Ordinal)
                        .ToArray(),
                    context.ChangeOfTruthRequired,
                    context.ProblemLabel);
            }

            if (context.State != ContextResolutionState.Current)
            {
                return MurtakazGatewayPlan.ContextFailure(
                    request,
                    GatewayPlanState.Unavailable,
                    "BLOCKED",
                    context.SourceRevision,
                    context.Sources.Select(item => item.Id).ToArray(),
                    [],
                    context.ChangeOfTruthRequired,
                    string.IsNullOrWhiteSpace(context.ProblemLabel)
                        ? "Project context is unavailable."
                        : context.ProblemLabel);
            }

            var capsule = capsuleCompiler.Compile(
                context,
                new(
                    request.RequestId,
                    request.RequestedAt,
                    request.OwnerDirectiveIds,
                    request.AllowedScope,
                    request.ForbiddenScope,
                    "GATEWAY_ROUTING_CONTRACT_1.0",
                    "al-murtakaz-mandatory-approval:1.0",
                    RiskLabel(request.RiskTier),
                    ["ROUTING_PLAN"],
                    ["TYPED_INTENT", "CONTEXT_CURRENT", "NO_LIVE_DISPATCH"]));

            if (capsule.State != ContextResolutionState.Current ||
                capsule.Capsule is null)
            {
                return MurtakazGatewayPlan.ContextFailure(
                    request,
                    GatewayPlanState.Unavailable,
                    "BLOCKED",
                    context.SourceRevision,
                    context.Sources.Select(item => item.Id).ToArray(),
                    [],
                    context.ChangeOfTruthRequired,
                    string.IsNullOrWhiteSpace(capsule.ProblemLabel)
                        ? "Context Capsule compilation failed."
                        : capsule.ProblemLabel);
            }

            var route = routingCoordinator.Coordinate(
                new(
                    request.ProjectId,
                    request.FrontDoor,
                    request.Intent,
                    request.Effect,
                    request.RiskTier,
                    request.Materiality,
                    request.Uncertainty,
                    request.Domains,
                    request.OwnerApprovalPresent,
                    request.ApprovalRef,
                    request.ChangeOfTruthRequested || context.ChangeOfTruthRequired,
                    request.AuthorityExpansionRequested,
                    request.ExternalConsequence,
                    request.DestructiveOrIrreversible,
                    request.PrivacySensitive,
                    request.SpendOrSubscription,
                    capsule.Capsule.CapsuleId));

            return new(
                route.State,
                route.ProjectedUxState,
                request.RequestId,
                request.CorrelationId,
                request.ProjectId,
                capsule.Capsule.CapsuleId,
                capsule.Capsule.SourceRevision,
                route,
                capsule.Capsule.Sources
                    .Select(item => item.Id)
                    .OrderBy(item => item, StringComparer.Ordinal)
                    .ToArray(),
                [],
                context.ChangeOfTruthRequired,
                string.Empty);
        }
        catch (Exception exc) when (
            exc is ProjectContextReadException or
            ContextCapsuleCompileException or
            GatewayRoutingPolicyException)
        {
            return MurtakazGatewayPlan.ContextFailure(
                request,
                GatewayPlanState.Unavailable,
                "BLOCKED",
                "UNKNOWN",
                [],
                [],
                false,
                exc.Message);
        }
    }

    private static void ValidateRequest(MurtakazGatewayRequest request)
    {
        Require(request.RequestId, nameof(request.RequestId));
        Require(request.CorrelationId, nameof(request.CorrelationId));
        Require(request.ProjectId, nameof(request.ProjectId));
        Require(request.Principal, nameof(request.Principal));
        Require(request.Instruction, nameof(request.Instruction));

        if (!request.Authenticated ||
            request.Principal != "OWNER")
        {
            throw new GatewayRoutingPolicyException(
                "Gateway requires an authenticated OWNER principal supplied by a trusted ingress adapter.");
        }

        if (request.Instruction.Length > 8000)
        {
            throw new GatewayRoutingPolicyException(
                "Gateway instruction exceeds the bounded request size.");
        }

        if (request.RequestedAt == default)
        {
            throw new GatewayRoutingPolicyException(
                "Gateway request timestamp is required.");
        }

        ValidateDistinctNonEmpty(request.Domains, "domains");
        ValidateDistinctNonEmpty(request.RequiredSourceIds, "required source ids");
        ValidateDistinctNonEmpty(request.RequestedScopes, "requested scopes");
        ValidateDistinctNonEmpty(request.OwnerDirectiveIds, "owner directive ids");
        ValidateDistinctNonEmpty(request.AllowedScope, "allowed scope");
        ValidateDistinct(request.ForbiddenScope, "forbidden scope");

        if (request.AllowedScope.Intersect(
                request.ForbiddenScope,
                StringComparer.Ordinal).Any())
        {
            throw new GatewayRoutingPolicyException(
                "Gateway allowed/forbidden scope may not overlap.");
        }

        if (request.MaxContextSources is < 1 or > 64)
        {
            throw new GatewayRoutingPolicyException(
                "MaxContextSources must be between 1 and 64.");
        }

        if (request.OwnerApprovalPresent &&
            string.IsNullOrWhiteSpace(request.ApprovalRef))
        {
            throw new GatewayRoutingPolicyException(
                "OwnerApprovalPresent requires ApprovalRef.");
        }

        if (!request.OwnerApprovalPresent &&
            !string.IsNullOrWhiteSpace(request.ApprovalRef))
        {
            throw new GatewayRoutingPolicyException(
                "ApprovalRef cannot be supplied without OwnerApprovalPresent.");
        }
    }

    private static string RiskLabel(GatewayRiskTier risk) =>
        risk switch
        {
            GatewayRiskTier.T0Observe => "T0_OBSERVE",
            GatewayRiskTier.T1Reversible => "T1_REVERSIBLE",
            GatewayRiskTier.T2LocalStateChange => "T2_LOCAL_STATE_CHANGE",
            GatewayRiskTier.T3HighImpact => "T3_HIGH_IMPACT",
            _ => throw new GatewayRoutingPolicyException("Unsupported risk tier.")
        };

    private static void ValidateDistinctNonEmpty(
        IReadOnlyList<string> values,
        string label)
    {
        if (values.Count == 0)
        {
            throw new GatewayRoutingPolicyException(
                $"{label} may not be empty.");
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
            throw new GatewayRoutingPolicyException(
                $"{label} must be explicit and unique.");
        }
    }

    private static void Require(string value, string name)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            throw new GatewayRoutingPolicyException(
                $"Gateway field is required: {name}");
        }
    }
}
