namespace UniversalCouncil.CommandCenter.Core;

public sealed record ReviewerReportView(string RoleId, string Actor, string Outcome,
    string Rationale, IReadOnlyList<string> EvidenceRefs, DateTimeOffset RecordedAt)
{
    public string Provenance => "CALLER_REPORTED_UNVERIFIED";
}
public sealed record LocalSupervisionSnapshot(Guid Id, int Version, string ProjectId,
    string ChangeId, string SourceRevision, string ArtifactSha256, string State,
    DateTimeOffset LastObservedAt, DateTimeOffset ExpiresAt,
    IReadOnlyList<string> PendingRoleIds, IReadOnlyList<ReviewerReportView> Reports)
{
    public string Provenance => "LOCAL_CALLER_REPORTED_NOT_AUTHENTICATED";
    public bool EvidenceVerified => false;
    public bool ApprovalGranted => false;
    public bool ExecutionAuthority => false;
    public bool LiveExecution => false;
    public bool Stage8Opened => false;
}
