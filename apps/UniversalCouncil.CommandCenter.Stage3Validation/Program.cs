using System.Text.Json;
using UniversalCouncil.CommandCenter.Application;
using UniversalCouncil.CommandCenter.Core;
using UniversalCouncil.CommandCenter.Infrastructure;

var source = Path.Combine(
    AppContext.BaseDirectory,
    "state",
    "orchestration-catalog.json");

Require(File.Exists(source), "Stage 3 catalog fixture missing");

var reader = new JsonOrchestrationCatalogReader(source);
var service = new OrchestrationService(reader);

var catalog = service.GetCatalog();
Require(catalog.Health == OrchestrationHealth.Healthy, "canonical catalog must be healthy");
Require(catalog.TaskStateLabel == "NO_LIVE_TASK", "Stage 3 must not fabricate a live task");
Require(catalog.Council.CoreRoles.Count == 8, "expected eight canonical core roles");
Require(catalog.Council.SpecialistRoles.Count == 16, "expected sixteen canonical specialists");
Require(catalog.Studio.Departments.Count == 12, "expected twelve Studio departments");
Require(catalog.ModelControl.RoleModelSeparation, "Role != Model must be locked");
Require(catalog.ModelControl.OwnerControlledSelection, "Owner model control must be locked");
Require(!catalog.ModelControl.SilentFallbackAllowed, "silent fallback must be forbidden");
Require(!catalog.ModelControl.ProviderCallsConnected, "Stage 3 must not connect a model provider");
Require(catalog.Studio.ReturnTicketRequiredFields.Count >= 9, "return-ticket contract incomplete");

var route = service.Plan(
    new CouncilPlanningRequest(
        ["software", "security"],
        Materiality: "HIGH",
        Uncertainty: "HIGH",
        Risk: "HIGH",
        Freshness: "HIGH",
        UserImpact: true,
        ExecutionFeasibility: true,
        CostOrValueTradeoff: true,
        CommercialDecision: false));

foreach (var expected in new[]
{
    "chair",
    "software",
    "security",
    "evidence",
    "redteam",
    "risk",
    "human",
    "execution",
    "value"
})
{
    Require(route.ActivatedRoleIds.Contains(expected), $"routing missed required role: {expected}");
}

Require(!route.ExecutionAuthorized, "planning may never authorize execution");
Require(route.ModelSelectionState.Contains("OWNER_SELECTION_REQUIRED", StringComparison.Ordinal),
    "routing must not silently choose a model");

var commercial = service.Plan(
    new CouncilPlanningRequest(
        ["business"],
        Materiality: "MATERIAL",
        Uncertainty: "MEDIUM",
        Risk: "MEDIUM",
        Freshness: "LOW",
        UserImpact: false,
        ExecutionFeasibility: false,
        CostOrValueTradeoff: true,
        CommercialDecision: true));

Require(commercial.ActivatedRoleIds.Contains("customer_skeptic"),
    "commercial routing requires Customer Skeptic");
Require(commercial.ActivatedRoleIds.Contains("moat_auditor"),
    "commercial routing requires Moat Auditor");

ExpectThrows(
    () => service.Plan(
        new CouncilPlanningRequest(
            ["unknown_domain"],
            "MATERIAL",
            "MEDIUM",
            "LOW",
            "LOW",
            false,
            false,
            false,
            false)),
    "unknown domain must fail closed");

using var temp = new TempCatalog(source);

temp.WriteMutation(root =>
{
    root["model_control"]!["silent_fallback_allowed"] = true;
});
Require(
    NewService(temp.Path).GetCatalog().Health == OrchestrationHealth.Unavailable,
    "silent fallback mutation must fail closed");

temp.Reset();
temp.WriteMutation(root =>
{
    var core = root["council"]!["core_roles"]!.AsArray();
    core[0]!["may_execute_tools"] = true;
});
Require(
    NewService(temp.Path).GetCatalog().Health == OrchestrationHealth.Unavailable,
    "role authority inflation must fail closed");

temp.Reset();
temp.WriteMutation(root =>
{
    root["runtime"]!["active_model"] = "model-x";
});
Require(
    NewService(temp.Path).GetCatalog().Health == OrchestrationHealth.Unavailable,
    "fabricated active model must fail closed");

temp.Reset();
temp.WriteMutation(root =>
{
    root["studio"]!["handoff_contract"]!["downstream_direct_repair_forbidden"] = false;
});
Require(
    NewService(temp.Path).GetCatalog().Health == OrchestrationHealth.Unavailable,
    "Studio cross-edit authority drift must fail closed");

Console.WriteLine("Command Center Stage 3 adversarial validation: PASS");
return 0;

static OrchestrationService NewService(string path) =>
    new(new JsonOrchestrationCatalogReader(path));

static void Require(bool condition, string message)
{
    if (!condition)
    {
        throw new InvalidOperationException(message);
    }
}

static void ExpectThrows(Action action, string message)
{
    try
    {
        action();
    }
    catch (OrchestrationCatalogReadException)
    {
        return;
    }

    throw new InvalidOperationException(message);
}

sealed class TempCatalog : IDisposable
{
    private readonly string original;
    private readonly string directory;

    public TempCatalog(string source)
    {
        original = File.ReadAllText(source);
        directory = System.IO.Path.Combine(
            System.IO.Path.GetTempPath(),
            "UniversalCouncil.CommandCenter.Stage3Validation",
            Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(directory);
        Path = System.IO.Path.Combine(directory, "catalog.json");
        Reset();
    }

    public string Path { get; }

    public void Reset() => File.WriteAllText(Path, original);

    public void WriteMutation(Action<System.Text.Json.Nodes.JsonObject> mutation)
    {
        var root = System.Text.Json.Nodes.JsonNode.Parse(original)!.AsObject();
        mutation(root);
        File.WriteAllText(
            Path,
            root.ToJsonString(new JsonSerializerOptions { WriteIndented = true }));
    }

    public void Dispose() => Directory.Delete(directory, recursive: true);
}
