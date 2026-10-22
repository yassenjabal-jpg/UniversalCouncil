namespace UniversalCouncil.CommandCenter.Core;

// A proposed assignment is never evidence that a reviewer ran or approved anything.
public sealed record LocalReviewRequest(
    string ChangeId, string ProjectId, string SourceRevision, string ChangeClass,
    string[] Routes, string[] Surfaces, string[] WorkshopFunctions);

public sealed record LocalReviewAssignment(string Group, string RoleId, string[] Reasons);

public sealed record LocalReviewPlan(
    string Status, string ChangeId, string ProjectId, string SourceRevision,
    string PolicyFingerprint, string Mode, LocalReviewAssignment[] Assignments, string[] Errors)
{
    public string SourceKind => "LOCAL_FILE_SNAPSHOT";
    public string RevisionBinding => "CALLER_SUPPLIED_NOT_INDEPENDENTLY_VERIFIED";
    public bool ReviewsExecuted => false;
    public bool ApprovalGranted => false;
    public bool ExecutionAuthority => false;
    public bool LiveExecution => false;
    public bool Stage8Opened => false;
    public bool ParentMutationAllowed => false;
}

public sealed record LocalReviewPolicy(
    string ProjectId, string Fingerprint, string[] GovernanceRoles, string[] WorkshopFunctions,
    IReadOnlyDictionary<string, string[]> Routes,
    IReadOnlyDictionary<string, string[]> Surfaces,
    string[] MandatoryWorkshopClearances, IReadOnlyDictionary<string, string> Modes);
