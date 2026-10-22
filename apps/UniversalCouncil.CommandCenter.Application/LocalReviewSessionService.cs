using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter.Application;

public interface ILocalReviewSessionStore
{
    LocalReviewSession Create(LocalReviewSession session);
    LocalReviewSession Transact(Guid id, int? expectedVersion,
        Func<LocalReviewSession, LocalReviewSession> mutation);
}

public sealed class LocalReviewSessionService(
    ILocalReviewPlanner planner, ILocalReviewSessionStore store, TimeProvider? clock = null)
{
    private readonly TimeProvider time = clock ?? TimeProvider.System;
    private static bool Hex(string? value, int length) =>
        value is not null && value.Length == length && value.All(char.IsAsciiHexDigit);
    public LocalReviewSession Create(LocalReviewRequest request, string artifactSha256, TimeSpan lifetime)
    {
        if (!Hex(artifactSha256, 64) || lifetime <= TimeSpan.Zero || lifetime > TimeSpan.FromDays(7))
            throw new InvalidDataException("Invalid artifact binding or lifetime");
        // Snapshot before planning; no caller-owned mutable arrays survive into the session.
        var copy = request with {
            Routes = request.Routes?.ToArray()!, Surfaces = request.Surfaces?.ToArray()!,
            WorkshopFunctions = request.WorkshopFunctions?.ToArray()!
        };
        var plan = planner.Plan(copy);
        if (plan.Status != "PLANNED") throw new InvalidDataException("Review planning unavailable");
        plan = plan with { Assignments = plan.Assignments.Select(a => a with {
            Reasons = a.Reasons.ToArray() }).ToArray(), Errors = plan.Errors.ToArray() };
        var now = time.GetUtcNow();
        var session = new LocalReviewSession(1, Guid.NewGuid(), 0, copy, plan,
            artifactSha256.ToLowerInvariant(), now, now + lifetime, now, null, []);
        Validate(session);
        return store.Create(session);
    }

    public LocalReviewSession Read(Guid id, string currentRevision, string currentArtifactSha256) =>
        store.Transact(id, null, s => Refresh(s, currentRevision, currentArtifactSha256));

    public LocalReviewSession Record(Guid id, int expectedVersion, string currentRevision,
        string currentArtifactSha256, string roleId, string actor, string outcome,
        string rationale, string[] evidenceRefs)
    {
        return store.Transact(id, expectedVersion, s => {
            var fresh = Refresh(s, currentRevision, currentArtifactSha256);
            // Persist terminal freshness before returning; never record a result for stale work.
            if (fresh.TerminalReason is not null) return fresh;
            if (!s.Plan.Assignments.Any(a => a.RoleId == roleId) ||
                s.Results.Any(r => r.RoleId == roleId) ||
                !new[] { "ACCEPTED_REPORT", "RETURNED_FOR_CHANGES", "BLOCKED",
                    "OWNER_DECISION_REQUIRED" }.Contains(outcome) ||
                string.IsNullOrWhiteSpace(actor) || actor.Length > 256 ||
                string.IsNullOrWhiteSpace(rationale) || rationale.Length > 16000 ||
                evidenceRefs is null || evidenceRefs.Length > 100 ||
                evidenceRefs.Any(v => string.IsNullOrWhiteSpace(v) || v.Length > 2048))
                throw new InvalidDataException("Invalid or duplicate caller-reported result");
            var result = new LocalReviewResult(roleId, actor, outcome, rationale,
                evidenceRefs.ToArray(), fresh.LastObservedAt);
            var updated = fresh with { Version = s.Version + 1, Results = [.. s.Results, result] };
            Validate(updated);
            return updated;
        });
    }

    private LocalReviewSession Refresh(LocalReviewSession s, string revision, string artifact)
    {
        Validate(s);
        if (!Hex(revision, 40) || !Hex(artifact, 64))
            throw new InvalidDataException("Current binding unavailable");
        if (s.TerminalReason is not null) return s;
        var now = time.GetUtcNow();
        var current = planner.Plan(s.Request);
        var reason = now < s.LastObservedAt ? "CLOCK_ROLLBACK" :
            now >= s.ExpiresAt ? "EXPIRED" :
            !string.Equals(revision, s.Plan.SourceRevision, StringComparison.OrdinalIgnoreCase) ||
            !string.Equals(artifact, s.ArtifactSha256, StringComparison.OrdinalIgnoreCase) ||
            current.Status != "PLANNED" || current.PolicyFingerprint != s.Plan.PolicyFingerprint ||
            System.Text.Json.JsonSerializer.Serialize(current) != System.Text.Json.JsonSerializer.Serialize(s.Plan)
                ? "BINDING_CHANGED" : null;
        if (reason is not null)
            return s with { Version = s.Version + 1, LastObservedAt =
                now < s.LastObservedAt ? s.LastObservedAt : now, TerminalReason = reason };
        // Persist time observations to detect clock rollback across process restarts.
        return now == s.LastObservedAt ? s : s with { Version = s.Version + 1, LastObservedAt = now };
    }

    public static void Validate(LocalReviewSession s)
    {
        if (s is null || s.SchemaVersion != 1 || s.Id == Guid.Empty || s.Version < 0 ||
            s.Request is null || s.Plan is null || s.Plan.Status != "PLANNED" ||
            !Hex(s.ArtifactSha256, 64) || !Hex(s.Plan.SourceRevision, 40) ||
            s.Plan.ChangeId != s.Request.ChangeId || s.Plan.ProjectId != s.Request.ProjectId ||
            s.Plan.SourceRevision != s.Request.SourceRevision ||
            string.IsNullOrWhiteSpace(s.Plan.ChangeId) || string.IsNullOrWhiteSpace(s.Plan.ProjectId) ||
            string.IsNullOrWhiteSpace(s.Plan.PolicyFingerprint) ||
            !new[] { "LIGHT", "COUNCIL", "ARENA" }.Contains(s.Plan.Mode) ||
            s.Request.Routes is null || s.Request.Surfaces is null || s.Request.WorkshopFunctions is null ||
            s.Plan.Assignments is null || s.Plan.Assignments.Length == 0 ||
            s.Plan.Errors is null || s.Plan.Errors.Length != 0 || s.Results is null ||
            s.CreatedAt.Offset != TimeSpan.Zero || s.ExpiresAt.Offset != TimeSpan.Zero ||
            s.LastObservedAt.Offset != TimeSpan.Zero || s.CreatedAt >= s.ExpiresAt ||
            s.ExpiresAt - s.CreatedAt > TimeSpan.FromDays(7) || s.LastObservedAt < s.CreatedAt ||
            s.TerminalReason is not null && !new[] { "EXPIRED", "BINDING_CHANGED", "CLOCK_ROLLBACK" }.Contains(s.TerminalReason))
            throw new InvalidDataException("Invalid persisted review session");
        var roles = s.Plan.Assignments.Select(a => a?.RoleId).ToArray();
        if (roles.Distinct(StringComparer.Ordinal).Count() != roles.Length ||
            s.Plan.Assignments.Any(a => a is null || string.IsNullOrWhiteSpace(a.RoleId) ||
                !new[] { "GOVERNANCE", "WORKSHOP" }.Contains(a.Group) || a.Reasons is null ||
                a.Reasons.Length == 0 || a.Reasons.Any(string.IsNullOrWhiteSpace)) ||
            s.Results.Select(r => r?.RoleId).Distinct().Count() != s.Results.Length ||
            s.Results.Length > s.Version ||
            s.Results.Any(r => r is null || !roles.Contains(r.RoleId) || string.IsNullOrWhiteSpace(r.Actor) ||
                r.Actor.Length > 256 || string.IsNullOrWhiteSpace(r.Rationale) || r.Rationale.Length > 16000 ||
                !new[] { "ACCEPTED_REPORT", "RETURNED_FOR_CHANGES", "BLOCKED", "OWNER_DECISION_REQUIRED" }.Contains(r.Outcome) ||
                r.EvidenceRefs is null || r.EvidenceRefs.Length > 100 ||
                r.EvidenceRefs.Any(v => string.IsNullOrWhiteSpace(v) || v.Length > 2048) ||
                r.RecordedAt.Offset != TimeSpan.Zero || r.RecordedAt < s.CreatedAt ||
                r.RecordedAt >= s.ExpiresAt || r.RecordedAt > s.LastObservedAt))
            throw new InvalidDataException("Inconsistent persisted reviewer records");
    }
}
