namespace UniversalCouncil.CommandCenter.Core;

public enum ContextResolutionState
{
    Current,
    StaleContext,
    ContextConflict,
    Unavailable
}

public sealed record ContextSourceProjection(
    string Id,
    string Path,
    string BlobSha,
    string AuthorityClass,
    string Freshness,
    IReadOnlyList<string> Domains,
    IReadOnlyList<string> Scopes,
    bool Untrusted,
    bool CanGovern);

public sealed record ContextConflictProjection(
    string Id,
    string Reason,
    IReadOnlyList<string> SourceIds,
    IReadOnlyList<string> Domains,
    bool RequiresOwnerDecision,
    bool ChangeOfTruthRequired);

public sealed record ContextResolutionRequest(
    string ProjectId,
    IReadOnlyList<string> Domains,
    IReadOnlyList<string> RequiredSourceIds,
    IReadOnlyList<string> RequestedScopes,
    bool IncludeUntrustedData,
    int MaxSources);

public sealed record ContextResolutionResult(
    ContextResolutionState State,
    string ProblemLabel,
    string ProjectId,
    string BaselineRevision,
    string SourceRevision,
    IReadOnlyList<string> Domains,
    IReadOnlyList<string> RequestedScopes,
    IReadOnlyList<ContextSourceProjection> Sources,
    IReadOnlyList<ContextConflictProjection> Conflicts,
    bool ChangeOfTruthRequired,
    IReadOnlyList<string> OwnerDirectiveIds,
    IReadOnlyList<string> CanonicalDecisionIds)
{
    public static ContextResolutionResult Unavailable(
        string projectId,
        IReadOnlyList<string> domains,
        IReadOnlyList<string> requestedScopes,
        string problem) =>
        new(
            ContextResolutionState.Unavailable,
            problem,
            projectId,
            "UNKNOWN",
            "UNKNOWN",
            domains,
            requestedScopes,
            [],
            [],
            false,
            [],
            []);
}

public sealed record ContextCapsuleCompileRequest(
    string JobOrChangeId,
    DateTimeOffset CreatedAt,
    IReadOnlyList<string> OwnerDirectiveIds,
    IReadOnlyList<string> AllowedScope,
    IReadOnlyList<string> ForbiddenScope,
    string RequiredSkillVersion,
    string AuthorityPolicyVersion,
    string RiskClass,
    IReadOnlyList<string> ExpectedOutputs,
    IReadOnlyList<string> AcceptanceTests);

public sealed record ContextCapsuleSource(
    string Id,
    string Path,
    string BlobSha,
    string AuthorityClass,
    string Freshness,
    bool CanGovern);

public sealed record CompiledContextCapsule(
    string CapsuleId,
    string ProjectId,
    string JobOrChangeId,
    DateTimeOffset CreatedAt,
    string BaselineRevision,
    string SourceRevision,
    IReadOnlyList<string> Domains,
    IReadOnlyList<string> RequestedScopes,
    IReadOnlyList<string> OwnerDirectiveIds,
    IReadOnlyList<ContextCapsuleSource> Sources,
    IReadOnlyList<string> AllowedScope,
    IReadOnlyList<string> ForbiddenScope,
    string RequiredSkillVersion,
    string AuthorityPolicyVersion,
    string RiskClass,
    IReadOnlyList<string> ExpectedOutputs,
    IReadOnlyList<string> AcceptanceTests);

public sealed record ContextCapsuleCompilationResult(
    ContextResolutionState State,
    string ProblemLabel,
    CompiledContextCapsule? Capsule);

public interface IProjectContextResolver
{
    ContextResolutionResult Resolve(ContextResolutionRequest request);
}

public interface IContextCapsuleCompiler
{
    ContextCapsuleCompilationResult Compile(
        ContextResolutionResult resolution,
        ContextCapsuleCompileRequest request);
}
