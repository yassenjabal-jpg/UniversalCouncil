using System.Text.Json;
using UniversalCouncil.CommandCenter.Core;
using UniversalCouncil.CommandCenter.Host;
using UniversalCouncil.CommandCenter.Infrastructure;
using UniversalCouncil.CommandCenter.Application;

if (args.Length > 0 && args[0] == "--verify-evidence" && args.Length is not (8 or 9))
{
    Console.Error.WriteLine("Invalid evidence verification arguments.");
    return 2;
}
var root = Path.Combine(AppContext.BaseDirectory, "state", "project-governance");
var reader = new JsonLocalReviewPolicyReader(root);
var planner = CommandCenterComposition.Create(AppContext.BaseDirectory).LocalReviewPlanner;
LocalReviewRequest Request(string kind = "minor_reversible_craft", string[]? routes = null,
    string[]? surfaces = null, string[]? functions = null) =>
    new("validation", "universal-council-command-center", new string('a', 40), kind,
        routes ?? [], surfaces ?? [], functions ?? []);
if (args.Length == 2 && args[0] == "--plan")
{
    var request = JsonSerializer.Deserialize<LocalReviewRequest>(File.ReadAllText(args[1]))
        ?? throw new InvalidDataException("Missing request");
    var result = planner.Plan(request);
    Console.WriteLine(JsonSerializer.Serialize(result, new JsonSerializerOptions { WriteIndented = true }));
    return result.Status == "PLANNED" ? 0 : 1;
}
if (args.Length == 3 && args[0] == "--session-probe")
    return SessionChecks.Probe(planner, args[1], args[2]);
if (args.Length is 8 or 9 && args[0] == "--verify-evidence")
{
    if (args.Length == 9 && args[8] != "--allow-fixtures") return 2;
    var verifier = CommandCenterComposition.CreateEvidenceVerifier(args[1], args[2], args.Length == 9);
    var result = verifier.Verify(new EvidenceVerificationRequest(args[6], args[7], args[3], args[4], args[5]));
    Console.WriteLine(JsonSerializer.Serialize(result, new JsonSerializerOptions { WriteIndented = true }));
    return result.ContentMatchesDeclaration ? 0 : 1;
}
if (args.Length != 0)
{
    Console.Error.WriteLine("Unknown or malformed validation command.");
    return 2;
}
var passed = 0;
void Check(bool condition, string name)
{
    if (!condition) throw new InvalidOperationException(name);
    passed++;
    Console.WriteLine("PASS " + name);
}
var light = planner.Plan(Request());
Check(light.Status == "PLANNED" && light.Mode == "LIGHT", "minor craft remains LIGHT");
Check(light.Assignments.Any(a => a.RoleId == "cc_project_chair"), "minimal governance never skipped");
Check(light.Assignments.Any(a => a.RoleId == "cc_visual_systems"), "minor craft has Workshop owner");
Check(!light.ReviewsExecuted && !light.ApprovalGranted && !light.ExecutionAuthority &&
      !light.LiveExecution && !light.Stage8Opened && !light.ParentMutationAllowed, "plan grants no authority");
var policy = reader.Read();
foreach (var route in policy.Routes)
{
    var plan = planner.Plan(Request(routes: [route.Key]));
    Check(plan.Status == "PLANNED" && route.Value.All(role =>
        plan.Assignments.Any(a => a.RoleId == role && a.Reasons.Contains("route:" + route.Key))),
        "actual route " + route.Key);
    Check(plan.Mode != "LIGHT", "route cannot downgrade to LIGHT: " + route.Key);
}
foreach (var surface in policy.Surfaces)
{
    var plan = planner.Plan(Request(surfaces: [surface.Key]));
    Check(surface.Value.All(role => plan.Assignments.Any(a => a.RoleId == role)),
        "actual surface " + surface.Key);
    Check(policy.MandatoryWorkshopClearances.All(role => plan.Assignments.Any(a => a.RoleId == role)),
        "surface Workshop clearances " + surface.Key);
}
Check(planner.Plan(Request(routes: ["automation_authority"])).Mode == "ARENA", "authority risk floor");
Check(planner.Plan(Request(routes: ["autopilot_recovery"])).Mode == "ARENA", "durability risk floor");
var union = planner.Plan(Request(routes: ["remote_owner", "cross_platform_state"]));
Check(union.Assignments.Single(a => a.RoleId == "cc_product_truth").Reasons.Length == 2,
    "union preserves reasons without duplicate reviewers");
foreach (var invalid in new[] {
    Request("unknown"), Request(routes: ["unknown"]), Request(surfaces: ["unknown"]),
    Request(functions: ["unknown"]), Request() with { ProjectId = "other" },
    Request() with { SourceRevision = "unknown" }, Request() with { Routes = null! } })
    Check(planner.Plan(invalid).Status == "UNAVAILABLE", "unknown request fails closed");
var nonvisual = planner.Plan(Request(functions: ["cc_windows_experience"]));
Check(!nonvisual.Assignments.Any(a => a.RoleId == "cc_visual_systems"), "requested craft does not get unrelated visual owner");
var multi = planner.Plan(Request(functions: ["cc_windows_experience", "cc_android_experience"]));
Check(multi.Assignments.Count(a => a.Reasons.Contains("requested_craft")) == 2,
    "multiple craft reviewers do not assert authoritative ownership");
var temp = Path.Combine(Path.GetTempPath(), "murtakaz-validation-" + Guid.NewGuid());
Directory.CreateDirectory(temp);
try
{
    void Fixture(string source, Func<string,string> mutate)
    {
        foreach (var name in new[] { "project-council.json", "product-studio.json" })
            File.WriteAllText(Path.Combine(temp, name), File.ReadAllText(Path.Combine(root, name)));
        var path = Path.Combine(temp, source);
        File.WriteAllText(path, mutate(File.ReadAllText(path)));
    }
    foreach (var mutation in new Func<string,string>[] {
        s => s.Replace("\"may_open_stage8\": false", "\"may_open_stage8\": true"),
        s => s.Replace("\"cc_red_team\"", "\"missing_role\"", StringComparison.Ordinal),
        s => s.Replace("\"schema_version\": \"1.0\"", "\"schema_version\": \"99\""),
        s => s.Replace("\"LIGHT\"", "\"INVALID\""),
        s => s.Replace("\"project_id\":", "\"project_id\": \"duplicate\", \"project_id\":"),
        s => "{" })
    {
        Fixture("project-council.json", mutation);
        // Removing all references to a required role must also fail.
        var bad = new LocalReviewPlanner(new JsonLocalReviewPolicyReader(temp)).Plan(Request());
        Check(bad.Status == "UNAVAILABLE", "malformed or inflated policy fails closed");
    }
    Fixture("product-studio.json", s => s.Replace("\"execution_authority\": false", "\"execution_authority\": true"));
    Check(new LocalReviewPlanner(new JsonLocalReviewPolicyReader(temp)).Plan(Request()).Status == "UNAVAILABLE",
        "Workshop authority inflation fails closed");
    foreach (var item in new[] {
        ("project-council.json", "mandatory_routes", "automation_authority", "remove_key"),
        ("project-council.json", "mandatory_routes", "automation_authority", "remove_role"),
        ("project-council.json", "mandatory_routes", "unknown", "add"),
        ("product-studio.json", "council_clearance_required_for", "truth_bearing_surface", "remove_role"),
        ("product-studio.json", "council_clearance_required_for", "unknown", "add") })
    {
        Fixture(item.Item1, text => {
            var doc = System.Text.Json.Nodes.JsonNode.Parse(text)!;
            var map = doc[item.Item2]!.AsObject();
            if (item.Item4 == "remove_key") map.Remove(item.Item3);
            else if (item.Item4 == "remove_role") map[item.Item3]!.AsArray().RemoveAt(0);
            else map[item.Item3] = new System.Text.Json.Nodes.JsonArray("cc_product_truth");
            return doc.ToJsonString();
        });
        Check(new LocalReviewPlanner(new JsonLocalReviewPolicyReader(temp)).Plan(Request()).Status == "UNAVAILABLE",
            "catalog floor rejects " + item);
    }
    foreach (var name in new[] { "project-council.json", "product-studio.json" })
    {
        Fixture(name, text => {
            var doc = System.Text.Json.Nodes.JsonNode.Parse(text)!;
            doc[name == "project-council.json" ? "core_roles" : "functions"]!.AsArray()
                .Add(new System.Text.Json.Nodes.JsonObject { ["id"] = "cc_fake" });
            if (name == "project-council.json")
                doc["mandatory_routes"]!["automation_authority"]!.AsArray().Add("cc_fake");
            return doc.ToJsonString();
        });
        Check(new LocalReviewPlanner(new JsonLocalReviewPolicyReader(temp)).Plan(
            Request(functions: name == "product-studio.json" ? ["cc_fake"] : [],
                routes: name == "project-council.json" ? ["automation_authority"] : [])).Status == "UNAVAILABLE",
            "unknown reviewer definition rejected " + name);
    }
    File.Delete(Path.Combine(temp, "product-studio.json"));
    Check(new LocalReviewPlanner(new JsonLocalReviewPolicyReader(temp)).Plan(Request()).Status == "UNAVAILABLE",
        "missing policy fails closed");
}
finally { Directory.Delete(temp, true); }
SessionChecks.Run(planner, Check);
EvidenceChecks.Run(Check);
Console.WriteLine($"PASS {passed} supervision behavioral checks");
return 0;
