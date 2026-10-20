namespace UniversalCouncil.CommandCenter.Application;

public sealed record ProjectContextMapDocument(
    string SchemaVersion,
    string SourceType,
    string ProjectId,
    string SourceRevision,
    ProjectManifestDocument ProjectManifest,
    CurrentProjectStateDocument CurrentState,
    IReadOnlyList<string> CanonicalDecisions,
    IReadOnlyList<string> ActiveWork,
    IReadOnlyList<string> RelevantSkills,
    IReadOnlyList<string> RecentEvents,
    IReadOnlyList<string> Blockers,
    IReadOnlyList<string> OwnerDirectives,
    IReadOnlyList<ProjectContextSourceDocument> Sources,
    IReadOnlyList<ProjectContextConflictDocument> Conflicts);

public sealed record ProjectManifestDocument(
    string DisplayName,
    string GovernanceSystem,
    string OwnerAuthority);

public sealed record CurrentProjectStateDocument(
    string DeliveryStage,
    string VisualPhase,
    bool LiveExecutionAuthorized,
    bool Stage8Opened);

public sealed record ProjectContextSourceDocument(
    string Id,
    string Path,
    string BlobSha,
    string AuthorityClass,
    string Freshness,
    IReadOnlyList<string> Domains,
    IReadOnlyList<string> Scopes,
    bool Untrusted);

public sealed record ProjectContextConflictDocument(
    string Id,
    string Reason,
    IReadOnlyList<string> SourceIds,
    IReadOnlyList<string> Domains,
    bool RequiresOwnerDecision);

public interface IProjectContextMapReader
{
    ProjectContextMapDocument Read();
}

public sealed class ProjectContextReadException : Exception
{
    public ProjectContextReadException(string message) : base(message) { }

    public ProjectContextReadException(string message, Exception inner) : base(message, inner) { }
}

public sealed class ContextCapsuleCompileException : Exception
{
    public ContextCapsuleCompileException(string message) : base(message) { }
}
