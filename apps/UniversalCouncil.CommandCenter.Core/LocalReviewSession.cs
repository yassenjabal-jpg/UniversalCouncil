namespace UniversalCouncil.CommandCenter.Core;

public sealed record LocalReviewResult(string RoleId, string Actor, string Outcome,
    string Rationale, string[] EvidenceRefs, DateTimeOffset RecordedAt)
{
    public string Provenance => "CALLER_REPORTED_UNVERIFIED";
}

public sealed record LocalReviewSession(
    int SchemaVersion, Guid Id, int Version, LocalReviewRequest Request, LocalReviewPlan Plan,
    string ArtifactSha256, DateTimeOffset CreatedAt, DateTimeOffset ExpiresAt,
    DateTimeOffset LastObservedAt, string? TerminalReason, LocalReviewResult[] Results)
{
    public string State => TerminalReason switch {
        "EXPIRED" => "EXPIRED",
        not null => "INVALIDATED",
        _ when Results.Any(r => r.Outcome == "BLOCKED") => "BLOCKED",
        _ when Results.Any(r => r.Outcome == "RETURNED_FOR_CHANGES") => "RETURNED_FOR_CHANGES",
        _ when Results.Any(r => r.Outcome == "OWNER_DECISION_REQUIRED") => "OWNER_DECISION_REQUIRED",
        _ when Results.Length == Plan.Assignments.Length => "RESULTS_RECORDED",
        _ => "REVIEWING"
    };
    public string Provenance => "LOCAL_CALLER_REPORTED_NOT_AUTHENTICATED";
    public bool EvidenceVerified => false;
    public bool ApprovalGranted => false;
    public bool ExecutionAuthority => false;
    public bool LiveExecution => false;
    public bool Stage8Opened => false;
}
