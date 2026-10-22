using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter.Application;

public interface ILocalReviewPolicyReader { LocalReviewPolicy Read(); }
public interface ILocalReviewPlanner { LocalReviewPlan Plan(LocalReviewRequest request); }

public sealed class LocalReviewPlanner(ILocalReviewPolicyReader reader) : ILocalReviewPlanner
{
    private static readonly string[] SensitiveRoles =
        ["cc_security_remote_trust", "cc_durable_autopilot"];
    public LocalReviewPlan Plan(LocalReviewRequest request)
    {
        string fingerprint = "";
        try
        {
            var policy = reader.Read();
            fingerprint = policy.Fingerprint;
            if (request.ProjectId != policy.ProjectId || string.IsNullOrWhiteSpace(request.ChangeId) ||
                request.SourceRevision is null || request.SourceRevision.Length != 40 ||
                request.SourceRevision.Any(c => !char.IsAsciiHexDigit(c)) ||
                request.Routes is null || request.Surfaces is null || request.WorkshopFunctions is null ||
                !policy.Modes.TryGetValue(request.ChangeClass ?? "", out var mode))
                throw new InvalidDataException("Invalid request binding or change class");
            var assignments = new SortedDictionary<string, (string Group, SortedSet<string> Reasons)>(StringComparer.Ordinal);
            void Add(string group, string role, string reason)
            {
                var catalog = group == "GOVERNANCE" ? policy.GovernanceRoles : policy.WorkshopFunctions;
                if (!catalog.Contains(role, StringComparer.Ordinal))
                    throw new InvalidDataException("Unknown reviewer: " + role);
                if (!assignments.TryGetValue(role, out var entry))
                    assignments.Add(role, entry = (group, new(StringComparer.Ordinal)));
                entry.Reasons.Add(reason);
            }
            Add("GOVERNANCE", "cc_project_chair", "minimal_governance");
            Add("WORKSHOP", "cc_studio_producer", "workshop_coordination");
            foreach (var route in request.Routes.Distinct(StringComparer.Ordinal))
            {
                if (route is null || !policy.Routes.TryGetValue(route, out var roles))
                    throw new InvalidDataException("Unknown route");
                foreach (var role in roles) Add("GOVERNANCE", role, "route:" + route);
            }
            foreach (var surface in request.Surfaces.Distinct(StringComparer.Ordinal))
            {
                if (surface is null || !policy.Surfaces.TryGetValue(surface, out var roles))
                    throw new InvalidDataException("Unknown surface");
                foreach (var role in roles) Add("GOVERNANCE", role, "surface:" + surface);
            }
            foreach (var function in request.WorkshopFunctions.Distinct(StringComparer.Ordinal))
                Add("WORKSHOP", function, "requested_craft");
            var craft = request.ChangeClass == "minor_reversible_craft" || request.Surfaces.Length > 0 ||
                request.WorkshopFunctions.Length > 0 ||
                request.Routes.Intersect(["major_ux", "agentic_ux_state", "cross_platform_state"]).Any();
            if (craft)
            {
                if (request.WorkshopFunctions.Length == 0)
                    Add("WORKSHOP", "cc_visual_systems", "default_craft_review");
                foreach (var role in policy.MandatoryWorkshopClearances)
                    Add("WORKSHOP", role, "mandatory_workshop_clearance");
            }
            if (request.Routes.Intersect(["major_ux", "agentic_ux_state"]).Any())
            {
                Add("WORKSHOP", "cc_experience_architect", "experience_scope");
                Add("WORKSHOP", "cc_interaction_director", "interaction_scope");
            }
            if (request.Routes.Length > 0 || request.Surfaces.Length > 0)
                mode = mode == "LIGHT" ? "COUNCIL" : mode;
            if (SensitiveRoles.Any(assignments.ContainsKey) ||
                request.Routes.Contains("context_memory_truth") ||
                request.Routes.Intersect(["model_reasoning_fallback", "automation_authority",
                    "autopilot_recovery", "remote_owner", "agentic_os_architecture"]).Any())
                mode = "ARENA";
            return new("PLANNED", request.ChangeId, request.ProjectId, request.SourceRevision,
                fingerprint, mode, assignments.Select(a => new LocalReviewAssignment(
                    a.Value.Group, a.Key, a.Value.Reasons.ToArray())).ToArray(), []);
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or
            System.Text.Json.JsonException or InvalidDataException or KeyNotFoundException or
            InvalidOperationException or ArgumentException)
        {
            return new("UNAVAILABLE", request.ChangeId, request.ProjectId, request.SourceRevision,
                fingerprint, "UNKNOWN", [], [ex.Message]);
        }
    }
}
