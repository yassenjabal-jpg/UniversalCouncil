using UniversalCouncil.CommandCenter.Application;
using UniversalCouncil.CommandCenter.Core;
using UniversalCouncil.CommandCenter.Infrastructure;

var stateDirectory = Path.Combine(AppContext.BaseDirectory, "state");
var productionCapabilityPath = Path.Combine(stateDirectory, "capability-registry.json");
var productionModelPath = Path.Combine(stateDirectory, "model-broker-policy.json");

Require(File.Exists(productionCapabilityPath), "Production Capability Registry fixture is missing");
Require(File.Exists(productionModelPath), "Production Model Broker policy fixture is missing");

var productionRegistryReader = new JsonCapabilityRegistryReader(productionCapabilityPath);
var productionModelReader = new JsonModelBrokerPolicyReader(productionModelPath);
var productionRegistry = new CapabilityRegistryService(
    productionRegistryReader,
    () => new DateTimeOffset(2026, 10, 21, 4, 50, 0, TimeSpan.Zero));
var productionBroker = new ModelBroker(productionModelReader, productionRegistry);

var productionSnapshot = productionRegistry.GetSnapshot();
Require(productionSnapshot.Capabilities.Count >= 6, "Production registry must expose operation-specific entries");
Require(
    productionSnapshot.Capabilities.All(item => !string.IsNullOrWhiteSpace(item.Operation)),
    "Every production capability must be operation-scoped");

var productionModelSelection = productionBroker.Select(
    new(
        GatewayReasoningPath.SingleAgent,
        Preferences(
            task: "",
            role: "",
            project: "",
            global: "",
            fallbackMode: ModelFallbackMode.Disabled,
            fallbacks: [])));

Require(
    productionModelSelection.State == ModelSelectionState.OwnerSelectionRequired,
    "Disconnected production broker with no configured preference must require Owner selection");
Require(!productionModelSelection.ProviderInvocationAuthorized, "Production broker may not authorize provider invocation");
Require(!productionModelSelection.ExecutionAuthorityGranted, "Model selection may not grant execution authority");

var now = new DateTimeOffset(2026, 10, 21, 5, 0, 0, TimeSpan.Zero);
var capabilityDocument = SyntheticCapabilities(now);
var modelPolicy = SyntheticModelPolicy();

var registry = new CapabilityRegistryService(
    new StaticCapabilityRegistryReader(capabilityDocument),
    () => now);
var broker = new ModelBroker(
    new StaticModelBrokerPolicyReader(modelPolicy),
    registry);

var taskWins = broker.Select(
    new(
        GatewayReasoningPath.SingleAgent,
        Preferences(
            task: "model-task",
            role: "model-role",
            project: "model-project",
            global: "model-global",
            fallbackMode: ModelFallbackMode.Disabled,
            fallbacks: [])));

Require(taskWins.State == ModelSelectionState.Selected, "Task override must select an eligible model");
Require(taskWins.ModelId == "model-task", "Task override must outrank Role/Project/Global");
Require(taskWins.PreferenceLevel == "TASK_OVERRIDE", "Task preference level drifted");
Require(!taskWins.FallbackUsed, "Primary task override is not a fallback");
Require(taskWins.ProviderInvocationEligible, "Selected synthetic model should be invocation-eligible");
Require(!taskWins.ProviderInvocationAuthorized, "Selection must never authorize provider invocation");
Require(!taskWins.ExecutionAuthorityGranted, "Selection must never grant execution authority");

var roleWins = broker.Select(
    new(
        GatewayReasoningPath.SingleAgent,
        Preferences(
            task: "",
            role: "model-role",
            project: "model-project",
            global: "model-global",
            fallbackMode: ModelFallbackMode.Disabled,
            fallbacks: [])));

Require(roleWins.ModelId == "model-role", "Role override must outrank Project/Global");
Require(roleWins.PreferenceLevel == "ROLE_OVERRIDE", "Role preference level drifted");

var projectWins = broker.Select(
    new(
        GatewayReasoningPath.SingleAgent,
        Preferences(
            task: "",
            role: "",
            project: "model-project",
            global: "model-global",
            fallbackMode: ModelFallbackMode.Disabled,
            fallbacks: [])));

Require(projectWins.ModelId == "model-project", "Project default must outrank Global");
Require(projectWins.PreferenceLevel == "PROJECT_DEFAULT", "Project preference level drifted");

var globalWins = broker.Select(
    new(
        GatewayReasoningPath.SingleAgent,
        Preferences(
            task: "",
            role: "",
            project: "",
            global: "model-global",
            fallbackMode: ModelFallbackMode.Disabled,
            fallbacks: [])));

Require(globalWins.ModelId == "model-global", "Global default should be used only when higher preferences are empty");
Require(globalWins.PreferenceLevel == "GLOBAL_DEFAULT", "Global preference level drifted");

var deterministic = broker.Select(
    new(
        GatewayReasoningPath.Deterministic,
        Preferences(
            task: "missing-model",
            role: "",
            project: "",
            global: "",
            fallbackMode: ModelFallbackMode.Disabled,
            fallbacks: [])));

Require(deterministic.State == ModelSelectionState.NotRequired, "Deterministic route must not require a model");

var noFallback = broker.Select(
    new(
        GatewayReasoningPath.SingleAgent,
        Preferences(
            task: "model-unavailable",
            role: "",
            project: "",
            global: "",
            fallbackMode: ModelFallbackMode.Disabled,
            fallbacks: [])));

Require(noFallback.State == ModelSelectionState.Unavailable, "Unavailable primary with disabled fallback must fail closed");
Require(!noFallback.FallbackUsed, "Disabled fallback may not be used");

var explicitFallback = broker.Select(
    new(
        GatewayReasoningPath.SingleAgent,
        Preferences(
            task: "model-unavailable",
            role: "",
            project: "",
            global: "",
            fallbackMode: ModelFallbackMode.ExplicitAllowlist,
            fallbacks: ["model-fallback"])));

Require(explicitFallback.State == ModelSelectionState.Selected, "Explicit allowlisted fallback should be selectable");
Require(explicitFallback.ModelId == "model-fallback", "Broker selected a model outside the explicit fallback");
Require(explicitFallback.FallbackUsed, "Fallback use must be visible in the result");
Require(!explicitFallback.ProviderInvocationAuthorized, "Fallback selection cannot authorize invocation");

var staleRegistry = new CapabilityRegistryService(
    new StaticCapabilityRegistryReader(capabilityDocument),
    () => now.AddHours(2));

var staleCapability = staleRegistry.Resolve(
    new(
        "model.invoke.task",
        CapabilityEffect.Execute,
        "provider-task",
        "EXTERNAL"));

Require(staleCapability.State == CapabilityResolutionState.Stale, "Expired TTL must project STALE capability truth");

var staleBroker = new ModelBroker(
    new StaticModelBrokerPolicyReader(modelPolicy),
    staleRegistry);

var staleModel = staleBroker.Select(
    new(
        GatewayReasoningPath.SingleAgent,
        Preferences(
            task: "model-task",
            role: "",
            project: "",
            global: "",
            fallbackMode: ModelFallbackMode.Disabled,
            fallbacks: [])));

Require(staleModel.State == ModelSelectionState.Unavailable, "Stale invocation capability must block model selection");

var blockedCapability = registry.Resolve(
    new(
        "model.invoke.blocked",
        CapabilityEffect.Execute,
        "provider-blocked",
        "EXTERNAL"));

Require(blockedCapability.State == CapabilityResolutionState.Blocked, "Blocked operation must remain blocked");

var ambiguousDocument = capabilityDocument with
{
    Capabilities = capabilityDocument.Capabilities.Concat(
    [
        new(
            "ambiguous-a",
            "provider-a",
            "shared.operation",
            "v1",
            "HEALTHY",
            "CONNECTED",
            "READ",
            "T0_OBSERVE",
            "LOW",
            now,
            3600,
            "EXTERNAL",
            "SYNTHETIC_TEST",
            true,
            ""),
        new(
            "ambiguous-b",
            "provider-b",
            "shared.operation",
            "v1",
            "HEALTHY",
            "CONNECTED",
            "READ",
            "T0_OBSERVE",
            "LOW",
            now,
            3600,
            "EXTERNAL",
            "SYNTHETIC_TEST",
            true,
            "")
    ]).ToArray()
};

var ambiguousRegistry = new CapabilityRegistryService(
    new StaticCapabilityRegistryReader(ambiguousDocument),
    () => now);

var ambiguous = ambiguousRegistry.Resolve(
    new(
        "shared.operation",
        CapabilityEffect.Read,
        "",
        "EXTERNAL"));

Require(ambiguous.State == CapabilityResolutionState.Ambiguous, "Multiple providers require explicit provider selection");

Console.WriteLine("Command Center Capability Registry/Model Broker validation: PASS");
return 0;

static ModelRoutingPreferences Preferences(
    string task,
    string role,
    string project,
    string global,
    ModelFallbackMode fallbackMode,
    IReadOnlyList<string> fallbacks) =>
    new(
        task,
        role,
        project,
        global,
        fallbackMode,
        fallbacks,
        ["text", "reasoning"],
        32000,
        ["SYNTHETIC", "LOCAL_LOW", "UNKNOWN"],
        "STANDARD",
        "HIGH",
        "EXTERNAL_ALLOWED");

static CapabilityRegistryDocument SyntheticCapabilities(DateTimeOffset now) =>
    new(
        "1.0",
        "project_local_repository_projection",
        "murtakaz-capability-registry",
        "READ_ONLY_OPERATION_TRUTH",
        now,
        [
            Capability(
                "cap-task",
                "provider-task",
                "model.invoke.task",
                "HEALTHY",
                now,
                3600),
            Capability(
                "cap-role",
                "provider-role",
                "model.invoke.role",
                "HEALTHY",
                now,
                3600),
            Capability(
                "cap-project",
                "provider-project",
                "model.invoke.project",
                "HEALTHY",
                now,
                3600),
            Capability(
                "cap-global",
                "provider-global",
                "model.invoke.global",
                "HEALTHY",
                now,
                3600),
            Capability(
                "cap-fallback",
                "provider-fallback",
                "model.invoke.fallback",
                "HEALTHY",
                now,
                3600),
            Capability(
                "cap-unavailable",
                "provider-unavailable",
                "model.invoke.unavailable",
                "UNAVAILABLE",
                now,
                3600,
                failureReason: "SYNTHETIC_PROVIDER_UNAVAILABLE"),
            Capability(
                "cap-blocked",
                "provider-blocked",
                "model.invoke.blocked",
                "BLOCKED",
                now,
                3600,
                failureReason: "SYNTHETIC_PROVIDER_BLOCKED")
        ]);

static CapabilityEntryDocument Capability(
    string id,
    string provider,
    string operation,
    string health,
    DateTimeOffset verifiedAt,
    int ttl,
    string failureReason = "") =>
    new(
        id,
        provider,
        operation,
        "synthetic-v1",
        health,
        "CONNECTED",
        "EXECUTE",
        "T1_REVERSIBLE",
        "SYNTHETIC",
        verifiedAt,
        ttl,
        "EXTERNAL",
        "SYNTHETIC_TEST",
        true,
        failureReason);

static ModelBrokerPolicyDocument SyntheticModelPolicy() =>
    new(
        "1.0",
        "project_local_repository_projection",
        "murtakaz-model-broker",
        "SELECTION_ONLY",
        OwnerControlled: true,
        SilentFallbackAllowed: false,
        ProviderCallsConnected: true,
        SelectionPrecedence:
        [
            "TASK_OVERRIDE",
            "ROLE_OVERRIDE",
            "PROJECT_DEFAULT",
            "GLOBAL_DEFAULT"
        ],
        AllowedFallbackModes: ["Disabled", "ExplicitAllowlist"],
        QualityOrder: ["STANDARD", "HIGH", "MAX"],
        CostOrder: ["FREE", "LOW", "MEDIUM", "HIGH"],
        PrivacyOrder: ["LOCAL_ONLY", "PRIVATE_PROVIDER", "EXTERNAL_ALLOWED"],
        Models:
        [
            Model("model-task", "provider-task", "model.invoke.task"),
            Model("model-role", "provider-role", "model.invoke.role"),
            Model("model-project", "provider-project", "model.invoke.project"),
            Model("model-global", "provider-global", "model.invoke.global"),
            Model("model-fallback", "provider-fallback", "model.invoke.fallback"),
            Model("model-unavailable", "provider-unavailable", "model.invoke.unavailable")
        ]);

static ModelCandidateDocument Model(
    string id,
    string provider,
    string operation) =>
    new(
        id,
        provider,
        operation,
        "EXTERNAL",
        Enabled: true,
        ProviderConnected: true,
        Capabilities: ["text", "reasoning"],
        QualityTier: "HIGH",
        CostTier: "MEDIUM",
        PrivacyClass: "EXTERNAL_ALLOWED",
        ContextWindow: 128000);

static void Require(bool condition, string message)
{
    if (!condition)
    {
        throw new InvalidOperationException(message);
    }
}

sealed class StaticCapabilityRegistryReader : ICapabilityRegistryReader
{
    private readonly CapabilityRegistryDocument document;

    public StaticCapabilityRegistryReader(CapabilityRegistryDocument document)
    {
        this.document = document;
    }

    public CapabilityRegistryDocument Read() => document;
}

sealed class StaticModelBrokerPolicyReader : IModelBrokerPolicyReader
{
    private readonly ModelBrokerPolicyDocument document;

    public StaticModelBrokerPolicyReader(ModelBrokerPolicyDocument document)
    {
        this.document = document;
    }

    public ModelBrokerPolicyDocument Read() => document;
}
