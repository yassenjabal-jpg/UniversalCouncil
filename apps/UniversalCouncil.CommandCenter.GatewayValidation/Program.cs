using UniversalCouncil.CommandCenter.Application;
using UniversalCouncil.CommandCenter.Core;
using UniversalCouncil.CommandCenter.Infrastructure;

var stateDirectory = Path.Combine(AppContext.BaseDirectory, "state");
var contextPath = Path.Combine(stateDirectory, "project-context-map.json");
var routingPath = Path.Combine(stateDirectory, "gateway-routing-policy.json");

Require(File.Exists(contextPath), "Project context map fixture is missing");
Require(File.Exists(routingPath), "Gateway routing policy fixture is missing");

var contextReader = new JsonProjectContextMapReader(contextPath);
var routingReader = new JsonGatewayRoutingPolicyReader(routingPath);
var contextDocument = contextReader.Read();

var gateway = BuildGateway(contextReader, routingReader);

var observe = gateway.Plan(
    BuildRequest(
        GatewayIntent.Observe,
        GatewayEffect.Read,
        GatewayRiskTier.T0Observe,
        domains: ["context"],
        materiality: "LOW",
        uncertainty: "LOW"));

Require(observe.State == GatewayPlanState.Planned, "Low-risk Observe should produce a planned shadow route");
Require(observe.ProjectedUxState == "PLANNING", "Observe UX state should be PLANNING");
Require(
    observe.Routing.ReasoningPath == GatewayReasoningPath.Deterministic,
    "Low-risk Observe should use deterministic reasoning");
Require(!observe.Routing.ApprovalRequired, "Low-risk Observe should not require Owner approval");
Require(!observe.Routing.ExecutionAuthorized, "Gateway planning may not authorize execution");
Require(!observe.Routing.LiveDispatchAllowed, "Gateway planning may not enable live dispatch");
Require(observe.ContextCapsuleId.StartsWith("CTX-", StringComparison.Ordinal), "Gateway must compile a Context Capsule");
Require(observe.Routing.Stages.Count == 8, "Routing plan must expose all eight stages");
Require(
    observe.Routing.Stages.Single(item => item.Stage == "model").State ==
        RoutingStageState.NotRequired,
    "Deterministic route should not require a model");

var writeNoApproval = gateway.Plan(
    BuildRequest(
        GatewayIntent.ModifyProject,
        GatewayEffect.Write,
        GatewayRiskTier.T2LocalStateChange,
        domains: ["context"],
        materiality: "MATERIAL",
        uncertainty: "MEDIUM"));

Require(
    writeNoApproval.State == GatewayPlanState.WaitingForApproval,
    "Material WRITE without approval must wait for Owner approval");
Require(
    writeNoApproval.ProjectedUxState == "WAITING_FOR_APPROVAL",
    "WRITE without approval must project WAITING_FOR_APPROVAL");
Require(writeNoApproval.Routing.ApprovalRequired, "WRITE must require approval");
Require(!writeNoApproval.Routing.ExecutionAuthorized, "Waiting approval is not execution authority");

var writeApproved = gateway.Plan(
    BuildRequest(
        GatewayIntent.ModifyProject,
        GatewayEffect.Write,
        GatewayRiskTier.T2LocalStateChange,
        domains: ["context"],
        materiality: "MATERIAL",
        uncertainty: "MEDIUM",
        ownerApprovalPresent: true,
        approvalRef: "OWNER-APPROVAL-VALIDATION-001"));

Require(
    writeApproved.State == GatewayPlanState.Blocked,
    "Approved WRITE must still be blocked while live dispatch is disabled");
Require(
    writeApproved.Routing.Stages.Single(item => item.Stage == "authority_risk").State ==
        RoutingStageState.Resolved,
    "Owner approval should resolve the approval gate for planning");
Require(
    writeApproved.Routing.Stages.Single(item => item.Stage == "execution").State ==
        RoutingStageState.Blocked,
    "Execution stage must remain blocked");
Require(!writeApproved.Routing.ExecutionAuthorized, "Owner approval cannot imply execution authority");
Require(!writeApproved.Routing.LiveDispatchAllowed, "Owner approval cannot enable live dispatch");

var highRiskExecute = gateway.Plan(
    BuildRequest(
        GatewayIntent.ExecuteHost,
        GatewayEffect.Execute,
        GatewayRiskTier.T3HighImpact,
        domains: ["security"],
        materiality: "CRITICAL",
        uncertainty: "HIGH",
        ownerApprovalPresent: true,
        approvalRef: "OWNER-APPROVAL-VALIDATION-002",
        destructiveOrIrreversible: true));

Require(highRiskExecute.State == GatewayPlanState.Blocked, "High-risk EXECUTE must remain blocked");
Require(
    highRiskExecute.Routing.ReasoningPath == GatewayReasoningPath.MurtakazArena,
    "High-risk security/irreversible request must route to Murtakaz Arena");
Require(!highRiskExecute.Routing.ExecutionAuthorized, "Arena planning cannot grant execution authority");

var externalAction = gateway.Plan(
    BuildRequest(
        GatewayIntent.ExternalAction,
        GatewayEffect.Write,
        GatewayRiskTier.T2LocalStateChange,
        domains: ["external_service"],
        materiality: "MATERIAL",
        uncertainty: "MEDIUM",
        ownerApprovalPresent: true,
        approvalRef: "OWNER-APPROVAL-VALIDATION-003",
        externalConsequence: true));

Require(externalAction.State == GatewayPlanState.Blocked, "External WRITE must remain blocked");
Require(
    externalAction.Routing.ReasoningPath == GatewayReasoningPath.MurtakazGovernance,
    "External consequence must not route below Murtakaz Governance");

var recovery = gateway.Plan(
    BuildRequest(
        GatewayIntent.Recover,
        GatewayEffect.Execute,
        GatewayRiskTier.T1Reversible,
        domains: ["host_work"],
        materiality: "MATERIAL",
        uncertainty: "MEDIUM",
        ownerApprovalPresent: true,
        approvalRef: "OWNER-APPROVAL-VALIDATION-004"));

Require(recovery.State == GatewayPlanState.Blocked, "Recovery execution must remain blocked");
Require(
    recovery.Routing.ReasoningPath == GatewayReasoningPath.MurtakazArena,
    "Recovery must always route through Murtakaz Arena");

var analyze = gateway.Plan(
    BuildRequest(
        GatewayIntent.Analyze,
        GatewayEffect.Read,
        GatewayRiskTier.T1Reversible,
        domains: ["analysis"],
        materiality: "MATERIAL",
        uncertainty: "MEDIUM"));

Require(analyze.State == GatewayPlanState.Blocked, "Non-deterministic analysis must block until Model Broker exists");
Require(
    analyze.Routing.ReasoningPath == GatewayReasoningPath.SingleAgent,
    "Ordinary analysis should select SingleAgent reasoning");
Require(
    analyze.Routing.Stages.Single(item => item.Stage == "model").Selection ==
        "OWNER_SELECTION_REQUIRED / MODEL_BROKER_NOT_IMPLEMENTED",
    "No model may be silently selected");

var staleDocument = contextDocument with
{
    Sources = contextDocument.Sources
        .Select(item =>
            item.Id == "context-capsule-contract"
                ? item with { Freshness = "STALE" }
                : item)
        .ToArray()
};

var staleGateway = BuildGateway(
    new StaticProjectContextMapReader(staleDocument),
    routingReader);

var stale = staleGateway.Plan(
    BuildRequest(
        GatewayIntent.Observe,
        GatewayEffect.Read,
        GatewayRiskTier.T0Observe,
        domains: ["context"],
        materiality: "LOW",
        uncertainty: "LOW"));

Require(stale.State == GatewayPlanState.StaleContext, "Stale context must propagate through Gateway");
Require(stale.ProjectedUxState == "STALE_CONTEXT", "Stale context UX state drifted");
Require(string.IsNullOrEmpty(stale.ContextCapsuleId), "Stale context may not compile a capsule");

var conflictDocument = contextDocument with
{
    Conflicts =
    [
        new(
            "gateway-validation-conflict",
            "Two governing context sources disagree.",
            ["agentic-os-policy", "context-capsule-contract"],
            ["context"],
            RequiresOwnerDecision: true,
            ChangeOfTruthRequired: true)
    ]
};

var conflictGateway = BuildGateway(
    new StaticProjectContextMapReader(conflictDocument),
    routingReader);

var conflict = conflictGateway.Plan(
    BuildRequest(
        GatewayIntent.Observe,
        GatewayEffect.Read,
        GatewayRiskTier.T0Observe,
        domains: ["context"],
        materiality: "LOW",
        uncertainty: "LOW"));

Require(conflict.State == GatewayPlanState.ContextConflict, "Context conflict must propagate through Gateway");
Require(conflict.ProjectedUxState == "CONTEXT_CONFLICT", "Conflict UX state drifted");
Require(conflict.ChangeOfTruthRequired, "Change-of-Truth metadata must survive Gateway projection");
Require(conflict.ConflictSourceIds.Count == 2, "Conflict provenance must preserve both sources");
Require(string.IsNullOrEmpty(conflict.ContextCapsuleId), "Conflicting context may not compile a capsule");

var intentEffectMismatch = gateway.Plan(
    BuildRequest(
        GatewayIntent.Observe,
        GatewayEffect.Write,
        GatewayRiskTier.T2LocalStateChange,
        domains: ["context"],
        materiality: "MATERIAL",
        uncertainty: "LOW"));

Require(
    intentEffectMismatch.State == GatewayPlanState.Unavailable,
    "Observe+WRITE mismatch must fail closed");
Require(
    intentEffectMismatch.ProjectedUxState == "BLOCKED",
    "Typed intent/effect mismatch must project BLOCKED");

var unauthenticated = gateway.Plan(
    BuildRequest(
        GatewayIntent.Observe,
        GatewayEffect.Read,
        GatewayRiskTier.T0Observe,
        domains: ["context"],
        materiality: "LOW",
        uncertainty: "LOW") with
    {
        Authenticated = false
    });

Require(unauthenticated.State == GatewayPlanState.Unavailable, "Unauthenticated ingress must fail closed");
Require(!unauthenticated.Routing.ExecutionAuthorized, "Unauthenticated ingress cannot gain execution authority");

Console.WriteLine("Command Center Gateway/Routing validation: PASS");
return 0;

static MurtakazCommandGateway BuildGateway(
    IProjectContextMapReader contextReader,
    IGatewayRoutingPolicyReader routingReader)
{
    var contextResolver = new ProjectContextResolver(contextReader);
    var capsuleCompiler = new ContextCapsuleCompiler();
    var routingCoordinator = new RoutingCoordinator(routingReader);
    return new MurtakazCommandGateway(
        contextResolver,
        capsuleCompiler,
        routingCoordinator);
}

static MurtakazGatewayRequest BuildRequest(
    GatewayIntent intent,
    GatewayEffect effect,
    GatewayRiskTier riskTier,
    IReadOnlyList<string> domains,
    string materiality,
    string uncertainty,
    bool ownerApprovalPresent = false,
    string approvalRef = "",
    bool destructiveOrIrreversible = false,
    bool externalConsequence = false)
{
    return new(
        RequestId: $"VALIDATION-{intent}-{effect}",
        CorrelationId: $"CORR-{intent}-{effect}",
        ProjectId: "universal-council-command-center",
        FrontDoor: GatewayFrontDoor.Windows,
        Principal: "OWNER",
        Authenticated: true,
        Intent: intent,
        Effect: effect,
        RiskTier: riskTier,
        Materiality: materiality,
        Uncertainty: uncertainty,
        Domains: domains,
        RequiredSourceIds:
        [
            "agentic-os-policy",
            "context-capsule-contract",
            "ux-state-contract"
        ],
        RequestedScopes: ["project", "context"],
        OwnerDirectiveIds: ["al-murtakaz-mandatory-approval"],
        AllowedScope: ["READ_CONTEXT", "PLAN_ROUTE"],
        ForbiddenScope: ["LIVE_EXECUTION", "STAGE8"],
        Instruction: "Typed validation request; instruction text is not used for authority routing.",
        OwnerApprovalPresent: ownerApprovalPresent,
        ApprovalRef: approvalRef,
        ChangeOfTruthRequested: false,
        AuthorityExpansionRequested: false,
        ExternalConsequence: externalConsequence,
        DestructiveOrIrreversible: destructiveOrIrreversible,
        PrivacySensitive: false,
        SpendOrSubscription: false,
        MaxContextSources: 7,
        RequestedAt: new DateTimeOffset(2026, 10, 21, 0, 0, 0, TimeSpan.Zero));
}

static void Require(bool condition, string message)
{
    if (!condition)
    {
        throw new InvalidOperationException(message);
    }
}

sealed class StaticProjectContextMapReader : IProjectContextMapReader
{
    private readonly ProjectContextMapDocument document;

    public StaticProjectContextMapReader(ProjectContextMapDocument document)
    {
        this.document = document;
    }

    public ProjectContextMapDocument Read() => document;
}
