using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter.Application;

// Inspection refreshes durable observations through S2; it is not a zero-write API.
public sealed class LocalSupervisionReader(LocalReviewSessionService sessions)
{
    public LocalSupervisionSnapshot Read(Guid id, string currentRevision, string currentArtifactSha256)
    {
        var session = sessions.Read(id, currentRevision, currentArtifactSha256);
        return Project(session);
    }
    internal static LocalSupervisionSnapshot Project(LocalReviewSession session)
    {
        var reports = session.Results.Select(r => new ReviewerReportView(r.RoleId,
            r.Actor, r.Outcome, r.Rationale, Array.AsReadOnly(r.EvidenceRefs.ToArray()),
            r.RecordedAt)).ToArray();
        var recorded = reports.Select(r => r.RoleId).ToHashSet(StringComparer.Ordinal);
        var pending = session.Plan.Assignments.Select(a => a.RoleId)
            .Where(role => !recorded.Contains(role)).ToArray();
        return new(session.Id, session.Version, session.Request.ProjectId,
            session.Request.ChangeId, session.Plan.SourceRevision, session.ArtifactSha256,
            session.State, session.LastObservedAt, session.ExpiresAt,
            Array.AsReadOnly(pending), Array.AsReadOnly(reports));
    }
}
