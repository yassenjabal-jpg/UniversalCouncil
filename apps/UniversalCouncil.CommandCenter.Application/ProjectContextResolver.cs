using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter.Application;

public sealed class ProjectContextResolver : IProjectContextResolver
{
    private static readonly HashSet<string> AllowedAuthorityClasses = new(StringComparer.Ordinal)
    {
        "OWNER_DIRECTIVE_TYPED",
        "LOCKED_POLICY",
        "CANONICAL_ARTIFACT",
        "ACCEPTED_EVIDENCE",
        "WORKING_DATA",
        "UNTRUSTED_EXTERNAL_DATA"
    };

    private static readonly Dictionary<string, int> AuthorityRank = new(StringComparer.Ordinal)
    {
        ["OWNER_DIRECTIVE_TYPED"] = 0,
        ["LOCKED_POLICY"] = 1,
        ["CANONICAL_ARTIFACT"] = 2,
        ["ACCEPTED_EVIDENCE"] = 3,
        ["WORKING_DATA"] = 4,
        ["UNTRUSTED_EXTERNAL_DATA"] = 5
    };

    private readonly IProjectContextMapReader reader;

    public ProjectContextResolver(IProjectContextMapReader reader)
    {
        this.reader = reader;
    }

    public ContextResolutionResult Resolve(ContextResolutionRequest request)
    {
        try
        {
            ValidateRequest(request);

            var document = reader.Read();
            ValidateDocument(document);

            if (!string.Equals(
                    request.ProjectId,
                    document.ProjectId,
                    StringComparison.Ordinal))
            {
                return ContextResolutionResult.Unavailable(
                    request.ProjectId,
                    request.Domains,
                    request.RequestedScopes,
                    "Requested project does not match the project context map.");
            }

            var byId = document.Sources.ToDictionary(item => item.Id, StringComparer.Ordinal);
            foreach (var requiredSourceId in request.RequiredSourceIds)
            {
                if (!byId.ContainsKey(requiredSourceId))
                {
                    return ContextResolutionResult.Unavailable(
                        request.ProjectId,
                        request.Domains,
                        request.RequestedScopes,
                        $"Required context source is missing: {requiredSourceId}");
                }

                if (byId[requiredSourceId].Untrusted &&
                    !request.IncludeUntrustedData)
                {
                    return ContextResolutionResult.Unavailable(
                        request.ProjectId,
                        request.Domains,
                        request.RequestedScopes,
                        $"Required source is untrusted but untrusted data is disabled: {requiredSourceId}");
                }
            }

            var requiredIds = request.RequiredSourceIds.ToHashSet(StringComparer.Ordinal);
            var candidates = document.Sources
                .Where(item =>
                    requiredIds.Contains(item.Id) ||
                    (Overlaps(item.Domains, request.Domains) &&
                     Overlaps(item.Scopes, request.RequestedScopes)))
                .Where(item => request.IncludeUntrustedData || !item.Untrusted)
                .OrderBy(item => AuthorityRank[item.AuthorityClass])
                .ThenBy(item => item.Id, StringComparer.Ordinal)
                .ToArray();

            if (candidates.Length == 0)
            {
                return ContextResolutionResult.Unavailable(
                    request.ProjectId,
                    request.Domains,
                    request.RequestedScopes,
                    "No context sources matched the requested domains/scopes.");
            }

            var conflicts = document.Conflicts
                .Where(item => Overlaps(item.Domains, request.Domains))
                .OrderBy(item => item.Id, StringComparer.Ordinal)
                .ToArray();

            if (conflicts.Length > 0)
            {
                var conflictSourceIds = conflicts
                    .SelectMany(item => item.SourceIds)
                    .Concat(requiredIds)
                    .ToHashSet(StringComparer.Ordinal);

                var conflictSources = document.Sources
                    .Where(item => conflictSourceIds.Contains(item.Id))
                    .OrderBy(item => AuthorityRank[item.AuthorityClass])
                    .ThenBy(item => item.Id, StringComparer.Ordinal)
                    .Select(ProjectSource)
                    .ToArray();

                if (conflictSources.Length > request.MaxSources)
                {
                    return ContextResolutionResult.Unavailable(
                        request.ProjectId,
                        request.Domains,
                        request.RequestedScopes,
                        "MaxSources is too small to preserve conflict provenance.");
                }

                return new(
                    ContextResolutionState.ContextConflict,
                    "Canonical context sources conflict; fail-closed resolution required.",
                    document.ProjectId,
                    document.BaselineRevision,
                    document.SourceRevision,
                    request.Domains.OrderBy(item => item, StringComparer.Ordinal).ToArray(),
                    request.RequestedScopes.OrderBy(item => item, StringComparer.Ordinal).ToArray(),
                    conflictSources,
                    conflicts.Select(ProjectConflict).ToArray(),
                    conflicts.Any(item => item.ChangeOfTruthRequired),
                    document.OwnerDirectives.OrderBy(item => item, StringComparer.Ordinal).ToArray(),
                    document.CanonicalDecisions.OrderBy(item => item, StringComparer.Ordinal).ToArray());
            }

            if (requiredIds.Count > request.MaxSources)
            {
                return ContextResolutionResult.Unavailable(
                    request.ProjectId,
                    request.Domains,
                    request.RequestedScopes,
                    "MaxSources is smaller than the required source set.");
            }

            var selected = candidates
                .Where(item => requiredIds.Contains(item.Id))
                .Concat(candidates.Where(item => !requiredIds.Contains(item.Id)))
                .DistinctBy(item => item.Id, StringComparer.Ordinal)
                .Take(request.MaxSources)
                .Select(ProjectSource)
                .ToArray();

            if (selected.Any(item => item.Freshness == "STALE"))
            {
                return new(
                    ContextResolutionState.StaleContext,
                    "Selected context is stale and requires a new capsule/re-plan.",
                    document.ProjectId,
                    document.BaselineRevision,
                    document.SourceRevision,
                    request.Domains.OrderBy(item => item, StringComparer.Ordinal).ToArray(),
                    request.RequestedScopes.OrderBy(item => item, StringComparer.Ordinal).ToArray(),
                    selected,
                    [],
                    false,
                    document.OwnerDirectives.OrderBy(item => item, StringComparer.Ordinal).ToArray(),
                    document.CanonicalDecisions.OrderBy(item => item, StringComparer.Ordinal).ToArray());
            }

            return new(
                ContextResolutionState.Current,
                string.Empty,
                document.ProjectId,
                document.BaselineRevision,
                document.SourceRevision,
                request.Domains.OrderBy(item => item, StringComparer.Ordinal).ToArray(),
                request.RequestedScopes.OrderBy(item => item, StringComparer.Ordinal).ToArray(),
                selected,
                [],
                false,
                document.OwnerDirectives.OrderBy(item => item, StringComparer.Ordinal).ToArray(),
                document.CanonicalDecisions.OrderBy(item => item, StringComparer.Ordinal).ToArray());
        }
        catch (ProjectContextReadException exc)
        {
            return ContextResolutionResult.Unavailable(
                request.ProjectId,
                request.Domains,
                request.RequestedScopes,
                exc.Message);
        }
        catch (Exception exc)
        {
            return ContextResolutionResult.Unavailable(
                request.ProjectId,
                request.Domains,
                request.RequestedScopes,
                $"Unexpected context-resolution failure: {exc.GetType().Name}");
        }
    }

    private static ContextSourceProjection ProjectSource(ProjectContextSourceDocument item) =>
        new(
            item.Id,
            item.Path,
            item.BlobSha,
            item.AuthorityClass,
            item.Freshness,
            item.Domains.OrderBy(value => value, StringComparer.Ordinal).ToArray(),
            item.Scopes.OrderBy(value => value, StringComparer.Ordinal).ToArray(),
            item.Untrusted,
            CanGovern(item.AuthorityClass, item.Untrusted));

    private static ContextConflictProjection ProjectConflict(ProjectContextConflictDocument item) =>
        new(
            item.Id,
            item.Reason,
            item.SourceIds.OrderBy(value => value, StringComparer.Ordinal).ToArray(),
            item.Domains.OrderBy(value => value, StringComparer.Ordinal).ToArray(),
            item.RequiresOwnerDecision,
            item.ChangeOfTruthRequired);

    private static bool CanGovern(string authorityClass, bool untrusted) =>
        !untrusted &&
        authorityClass is
            "OWNER_DIRECTIVE_TYPED" or
            "LOCKED_POLICY" or
            "CANONICAL_ARTIFACT";

    private static bool Overlaps(
        IReadOnlyList<string> left,
        IReadOnlyList<string> right) =>
        left.Intersect(right, StringComparer.Ordinal).Any();

    private static void ValidateRequest(ContextResolutionRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.ProjectId))
        {
            throw new ProjectContextReadException("ProjectId is required.");
        }

        ValidateDistinctNonEmpty(request.Domains, "request domains");
        ValidateDistinctNonEmpty(request.RequestedScopes, "requested scopes");
        ValidateDistinct(request.RequiredSourceIds, "required source ids");

        if (request.MaxSources is < 1 or > 64)
        {
            throw new ProjectContextReadException(
                "MaxSources must be between 1 and 64.");
        }
    }

    private static void ValidateDocument(ProjectContextMapDocument document)
    {
        if (document.SchemaVersion != "2.0" ||
            document.SourceType != "project_local_repository_projection")
        {
            throw new ProjectContextReadException(
                "Unsupported project context map schema/source.");
        }

        if (string.IsNullOrWhiteSpace(document.ProjectId) ||
            string.IsNullOrWhiteSpace(document.BaselineBranch) ||
            !IsLowerHex(document.BaselineRevision, 40) ||
            !IsLowerHex(document.SourceRevision, 64) ||
            document.HeadValidationMode != "BASELINE_ANCESTOR_AND_SOURCE_BLOBS_MATCH_HEAD")
        {
            throw new ProjectContextReadException(
                "Project context identity/baseline/source revision is incomplete.");
        }

        if (document.ProjectManifest.GovernanceSystem != "al-murtakaz" ||
            document.ProjectManifest.OwnerAuthority != "FINAL")
        {
            throw new ProjectContextReadException(
                "Project context governance identity drifted.");
        }

        if (document.CurrentState.LiveExecutionAuthorized ||
            document.CurrentState.Stage8Opened)
        {
            throw new ProjectContextReadException(
                "Context map may not authorize live execution or Stage 8.");
        }

        if (document.Sources.Count == 0)
        {
            throw new ProjectContextReadException(
                "Project context map must contain at least one source.");
        }

        var sourceIds = document.Sources.Select(item => item.Id).ToArray();
        if (sourceIds.Distinct(StringComparer.Ordinal).Count() != sourceIds.Length)
        {
            throw new ProjectContextReadException("Duplicate context source id.");
        }

        foreach (var source in document.Sources)
        {
            if (string.IsNullOrWhiteSpace(source.Id) ||
                string.IsNullOrWhiteSpace(source.Path) ||
                source.BlobSha.Length != 40)
            {
                throw new ProjectContextReadException(
                    $"Context source identity is incomplete: {source.Id}");
            }

            if (!AllowedAuthorityClasses.Contains(source.AuthorityClass))
            {
                throw new ProjectContextReadException(
                    $"Unsupported context authority class: {source.AuthorityClass}");
            }

            if (source.Freshness is not ("CURRENT" or "STALE"))
            {
                throw new ProjectContextReadException(
                    $"Unsupported context freshness: {source.Freshness}");
            }

            if (source.Untrusted !=
                (source.AuthorityClass == "UNTRUSTED_EXTERNAL_DATA"))
            {
                throw new ProjectContextReadException(
                    $"Untrusted flag/authority class mismatch: {source.Id}");
            }

            ValidateDistinctNonEmpty(source.Domains, $"domains for {source.Id}");
            ValidateDistinctNonEmpty(source.Scopes, $"scopes for {source.Id}");
        }

        var knownIds = sourceIds.ToHashSet(StringComparer.Ordinal);
        var conflictIds = document.Conflicts.Select(item => item.Id).ToArray();
        if (conflictIds.Distinct(StringComparer.Ordinal).Count() != conflictIds.Length)
        {
            throw new ProjectContextReadException("Duplicate context conflict id.");
        }

        foreach (var conflict in document.Conflicts)
        {
            if (string.IsNullOrWhiteSpace(conflict.Id) ||
                string.IsNullOrWhiteSpace(conflict.Reason))
            {
                throw new ProjectContextReadException(
                    "Context conflict identity/reason is incomplete.");
            }

            ValidateDistinctNonEmpty(conflict.SourceIds, $"sources for conflict {conflict.Id}");
            ValidateDistinctNonEmpty(conflict.Domains, $"domains for conflict {conflict.Id}");

            if (conflict.SourceIds.Any(id => !knownIds.Contains(id)))
            {
                throw new ProjectContextReadException(
                    $"Context conflict references an unknown source: {conflict.Id}");
            }
        }

        ValidateDistinct(document.CanonicalDecisions, "canonical decisions");
        ValidateDistinct(document.OwnerDirectives, "owner directives");
    }

    private static bool IsLowerHex(string value, int length) =>
        value.Length == length &&
        value.All(character =>
            character is >= '0' and <= '9' or >= 'a' and <= 'f');

    private static void ValidateDistinctNonEmpty(
        IReadOnlyList<string> values,
        string label)
    {
        if (values.Count == 0)
        {
            throw new ProjectContextReadException($"{label} may not be empty.");
        }

        ValidateDistinct(values, label);
    }

    private static void ValidateDistinct(
        IReadOnlyList<string> values,
        string label)
    {
        if (values.Any(string.IsNullOrWhiteSpace) ||
            values.Distinct(StringComparer.Ordinal).Count() != values.Count)
        {
            throw new ProjectContextReadException(
                $"{label} must be explicit and unique.");
        }
    }
}
