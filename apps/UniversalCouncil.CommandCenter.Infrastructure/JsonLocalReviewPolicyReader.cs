using System.Security.Cryptography;
using System.Text.Json;
using UniversalCouncil.CommandCenter.Application;
using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter.Infrastructure;

// Reads local snapshots only. The digest identifies bytes; it is not an approval signature.
public sealed class JsonLocalReviewPolicyReader(string directory) : ILocalReviewPolicyReader
{
    public LocalReviewPolicy Read()
    {
        var councilBytes = File.ReadAllBytes(Path.Combine(directory, "project-council.json"));
        var studioBytes = File.ReadAllBytes(Path.Combine(directory, "product-studio.json"));
        using var council = JsonDocument.Parse(councilBytes);
        using var studio = JsonDocument.Parse(studioBytes);
        var c = council.RootElement;
        var s = studio.RootElement;
        RejectDuplicates(c);
        RejectDuplicates(s);
        Require(c, "schema_version", "1.0");
        Require(s, "schema_version", "1.0");
        Require(c, "profile_id", "al-murtakaz-governance");
        Require(s, "profile_id", "al-murtakaz-workshop");
        Require(c, "status", "ACTIVE_FOR_PROJECT_REVIEW");
        Require(s, "status", "ACTIVE_FOR_PROJECT_DESIGN");
        Require(c, "profile_kind", "PROJECT_LOCAL_COUNCIL_OVERLAY");
        Require(s, "profile_kind", "PROJECT_LOCAL_PRODUCT_STUDIO");
        Require(c.GetProperty("parent"), "inheritance_mode", "READ_ONLY_INHERITANCE");
        Require(s.GetProperty("parent"), "inheritance_mode", "PRINCIPLES_ONLY_READ_ONLY");
        Require(c, "project_id", "universal-council-command-center");
        Require(s, "project_id", Text(c, "project_id"));
        Authority(c, ["may_modify_parent", "may_mutate_authority", "may_execute_tools_by_role_definition", "may_open_stage8"]);
        Authority(s, ["may_modify_parent", "may_mutate_authority", "execution_authority", "live_publish_authority", "may_open_stage8"]);
        foreach (var flag in new[] { "unknown_is_never_success", "recommendation_is_not_authority",
            "role_is_not_independent_agent_without_runtime_evidence" })
            if (!c.GetProperty("truth_rules").GetProperty(flag).GetBoolean())
                throw new InvalidDataException("Unsafe truth policy");
        var roles = Ids(c, "core_roles");
        var functions = Ids(s, "functions");
        foreach (var required in new[] { "cc_project_chair", "cc_product_truth", "cc_red_team",
            "cc_architecture_execution", "cc_security_remote_trust", "cc_owner_experience",
            "cc_durable_autopilot", "cc_cross_platform", "cc_ai_runtime", "cc_synthesis" })
            if (!roles.Contains(required)) throw new InvalidDataException("Missing core role: " + required);
        if (roles.Length != 10 || functions.Length != 13 ||
            functions.Except(new[] { "cc_studio_producer", "cc_experience_architect",
                "cc_interaction_director", "cc_visual_systems", "cc_motion_systems",
                "cc_sigil_iconography", "cc_design_systems_engineer", "cc_windows_experience",
                "cc_android_experience", "cc_prototype_engineer", "cc_accessibility_clearance",
                "cc_visual_qa", "cc_human_assistance" }).Any())
            throw new InvalidDataException("Unsupported reviewer catalog");
        if (roles.Intersect(functions).Any()) throw new InvalidDataException("Ambiguous reviewer identity");
        var routes = Map(c, "mandatory_routes", roles);
        var surfaces = Map(s, "council_clearance_required_for", roles);
        ValidateFloors(routes, new Dictionary<string, string[]> {
            ["autopilot_recovery"] = ["cc_durable_autopilot", "cc_product_truth", "cc_architecture_execution"],
            ["remote_owner"] = ["cc_security_remote_trust", "cc_cross_platform", "cc_product_truth"],
            ["model_reasoning_fallback"] = ["cc_ai_runtime", "cc_owner_experience", "cc_product_truth"],
            ["major_ux"] = ["cc_owner_experience", "cc_product_truth", "cc_red_team"],
            ["cross_platform_state"] = ["cc_cross_platform", "cc_product_truth"],
            ["architecture_boundary"] = ["cc_architecture_execution", "cc_red_team"],
            ["agentic_os_architecture"] = ["cc_architecture_execution", "cc_ai_runtime", "cc_security_remote_trust", "cc_product_truth", "cc_durable_autopilot", "cc_owner_experience", "cc_red_team"],
            ["context_memory_truth"] = ["cc_product_truth", "cc_ai_runtime", "cc_security_remote_trust"],
            ["automation_authority"] = ["cc_durable_autopilot", "cc_security_remote_trust", "cc_product_truth", "cc_architecture_execution", "cc_red_team"],
            ["agentic_ux_state"] = ["cc_owner_experience", "cc_product_truth", "cc_red_team", "cc_cross_platform", "cc_durable_autopilot", "cc_ai_runtime"]
        });
        ValidateFloors(surfaces, new Dictionary<string, string[]> {
            ["truth_bearing_surface"] = ["cc_product_truth"],
            ["remote_authority_surface"] = ["cc_security_remote_trust"],
            ["autopilot_recovery_surface"] = ["cc_durable_autopilot", "cc_product_truth"],
            ["architecture_sensitive_surface"] = ["cc_architecture_execution"],
            ["agentic_ux_state_surface"] = ["cc_owner_experience", "cc_product_truth", "cc_cross_platform"]
        });
        var clearances = Strings(s.GetProperty("mandatory_clearance"));
        if (clearances.Length == 0 || clearances.Any(id => !functions.Contains(id)))
            throw new InvalidDataException("Invalid Workshop clearance");
        foreach (var required in new[] { "cc_studio_producer", "cc_visual_systems",
            "cc_experience_architect", "cc_interaction_director", "cc_accessibility_clearance", "cc_visual_qa" })
            if (!functions.Contains(required)) throw new InvalidDataException("Missing Workshop function");
        if (!clearances.Contains("cc_accessibility_clearance") || !clearances.Contains("cc_visual_qa"))
            throw new InvalidDataException("Mandatory Workshop clearance removed");
        var modes = c.GetProperty("default_modes").EnumerateObject()
            .ToDictionary(p => p.Name, p => p.Value.GetString() ?? "", StringComparer.Ordinal);
        foreach (var (key, value) in new[] { ("minor_reversible_craft", "LIGHT"),
            ("material_product_change", "COUNCIL"), ("authority_security_durability_governance", "ARENA") })
            if (!modes.TryGetValue(key, out var actual) || actual != value)
                throw new InvalidDataException("Unsupported mode policy");
        if (modes.Count != 3) throw new InvalidDataException("Unknown change class");
        // Hash individual exact byte snapshots before combining to avoid boundary ambiguity.
        var hash = Convert.ToHexString(SHA256.HashData(councilBytes)) + ":" +
            Convert.ToHexString(SHA256.HashData(studioBytes));
        return new(Text(c, "project_id"), hash, roles, functions, routes, surfaces, clearances, modes);
    }
    private static string Text(JsonElement e, string key) =>
        e.GetProperty(key).GetString() ?? throw new InvalidDataException("Missing " + key);
    private static void Require(JsonElement e, string key, string value)
    {
        if (Text(e, key) != value) throw new InvalidDataException("Unsupported " + key);
    }
    private static void Authority(JsonElement e, string[] forbidden)
    {
        var a = e.GetProperty("authority");
        if (a.EnumerateObject().Any(p => !forbidden.Contains(p.Name) && p.Name != "owner_final_authority") ||
            forbidden.Any(key => a.GetProperty(key).GetBoolean()) ||
            !a.GetProperty("owner_final_authority").GetBoolean())
            throw new InvalidDataException("Authority inflation");
    }
    private static string[] Strings(JsonElement e)
    {
        var values = e.EnumerateArray().Select(v => v.GetString() ??
            throw new InvalidDataException("Null identifier")).ToArray();
        if (values.Any(string.IsNullOrWhiteSpace) || values.Distinct(StringComparer.Ordinal).Count() != values.Length)
            throw new InvalidDataException("Empty or duplicate identifier");
        return values;
    }
    private static string[] Ids(JsonElement e, string key)
    {
        var ids = e.GetProperty(key).EnumerateArray().Select(v => Text(v, "id")).ToArray();
        if (ids.Length == 0 || ids.Any(id => !id.StartsWith("cc_", StringComparison.Ordinal)) ||
            ids.Distinct(StringComparer.Ordinal).Count() != ids.Length)
            throw new InvalidDataException("Invalid reviewer catalog");
        return ids;
    }
    private static Dictionary<string, string[]> Map(JsonElement e, string key, string[] roles)
    {
        var result = e.GetProperty(key).EnumerateObject().ToDictionary(
            p => p.Name, p => Strings(p.Value), StringComparer.Ordinal);
        if (result.Count == 0 || result.Values.Any(v => v.Length == 0 || v.Any(id => !roles.Contains(id))))
            throw new InvalidDataException("Invalid reviewer reference");
        return result;
    }
    // Version 1.0 is a bounded catalog. Policy additions require reviewed code support.
    private static void ValidateFloors(Dictionary<string, string[]> actual,
        Dictionary<string, string[]> required)
    {
        if (actual.Count != required.Count || required.Any(pair =>
            !actual.TryGetValue(pair.Key, out var roles) || pair.Value.Any(id => !roles.Contains(id))))
            throw new InvalidDataException("Unsupported or weakened mandatory review catalog");
    }
    private static void RejectDuplicates(JsonElement e)
    {
        if (e.ValueKind == JsonValueKind.Object)
        {
            var names = new HashSet<string>(StringComparer.Ordinal);
            foreach (var p in e.EnumerateObject())
            {
                if (!names.Add(p.Name)) throw new InvalidDataException("Duplicate policy property");
                RejectDuplicates(p.Value);
            }
        }
        else if (e.ValueKind == JsonValueKind.Array)
            foreach (var item in e.EnumerateArray()) RejectDuplicates(item);
    }
}
