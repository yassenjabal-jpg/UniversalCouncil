using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter.Application;

public sealed class ContextCapsuleCompiler : IContextCapsuleCompiler
{
    public ContextCapsuleCompilationResult Compile(
        ContextResolutionResult resolution,
        ContextCapsuleCompileRequest request)
    {
        if (resolution.State != ContextResolutionState.Current)
        {
            return new(
                resolution.State,
                string.IsNullOrWhiteSpace(resolution.ProblemLabel)
                    ? "Context is not current; capsule compilation is blocked."
                    : resolution.ProblemLabel,
                null);
        }

        ValidateResolution(resolution);
        ValidateRequest(request, resolution);

        var ownerDirectives = request.OwnerDirectiveIds
            .OrderBy(item => item, StringComparer.Ordinal)
            .ToArray();

        var allowedScope = request.AllowedScope
            .OrderBy(item => item, StringComparer.Ordinal)
            .ToArray();

        var forbiddenScope = request.ForbiddenScope
            .OrderBy(item => item, StringComparer.Ordinal)
            .ToArray();

        var expectedOutputs = request.ExpectedOutputs
            .OrderBy(item => item, StringComparer.Ordinal)
            .ToArray();

        var acceptanceTests = request.AcceptanceTests
            .OrderBy(item => item, StringComparer.Ordinal)
            .ToArray();

        var sources = resolution.Sources
            .OrderBy(item => AuthorityRank(item.AuthorityClass))
            .ThenBy(item => item.Id, StringComparer.Ordinal)
            .Select(item => new ContextCapsuleSource(
                item.Id,
                item.Path,
                item.BlobSha,
                item.AuthorityClass,
                item.Freshness,
                item.CanGovern))
            .ToArray();

        var domains = resolution.Domains
            .OrderBy(item => item, StringComparer.Ordinal)
            .ToArray();

        var requestedScopes = resolution.RequestedScopes
            .OrderBy(item => item, StringComparer.Ordinal)
            .ToArray();

        var fingerprint = new CapsuleFingerprint(
            resolution.ProjectId,
            request.JobOrChangeId,
            request.CreatedAt,
            resolution.SourceRevision,
            domains,
            requestedScopes,
            ownerDirectives,
            sources,
            allowedScope,
            forbiddenScope,
            request.RequiredSkillVersion,
            request.AuthorityPolicyVersion,
            request.RiskClass,
            expectedOutputs,
            acceptanceTests);

        var options = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
            WriteIndented = false
        };

        var canonicalJson = JsonSerializer.Serialize(fingerprint, options);
        var digest = Convert.ToHexString(
            SHA256.HashData(Encoding.UTF8.GetBytes(canonicalJson)))
            .ToLowerInvariant();

        var capsule = new CompiledContextCapsule(
            $"CTX-{digest[..24]}",
            fingerprint.ProjectId,
            fingerprint.JobOrChangeId,
            fingerprint.CreatedAt,
            fingerprint.SourceRevision,
            fingerprint.Domains,
            fingerprint.RequestedScopes,
            fingerprint.OwnerDirectiveIds,
            fingerprint.Sources,
            fingerprint.AllowedScope,
            fingerprint.ForbiddenScope,
            fingerprint.RequiredSkillVersion,
            fingerprint.AuthorityPolicyVersion,
            fingerprint.RiskClass,
            fingerprint.ExpectedOutputs,
            fingerprint.AcceptanceTests);

        return new(ContextResolutionState.Current, string.Empty, capsule);
    }

    private static void ValidateResolution(ContextResolutionResult resolution)
    {
        if (string.IsNullOrWhiteSpace(resolution.ProjectId) ||
            resolution.SourceRevision.Length != 40)
        {
            throw new ContextCapsuleCompileException(
                "Resolved context identity/source revision is incomplete.");
        }

        if (resolution.Sources.Count == 0)
        {
            throw new ContextCapsuleCompileException(
                "A capsule requires at least one resolved source.");
        }

        if (resolution.Sources.Any(item => item.Freshness != "CURRENT"))
        {
            throw new ContextCapsuleCompileException(
                "A capsule may not compile from stale sources.");
        }

        if (resolution.Conflicts.Count != 0)
        {
            throw new ContextCapsuleCompileException(
                "A capsule may not compile while context conflicts exist.");
        }
    }

    private static void ValidateRequest(
        ContextCapsuleCompileRequest request,
        ContextResolutionResult resolution)
    {
        Require(request.JobOrChangeId, nameof(request.JobOrChangeId));
        Require(request.RequiredSkillVersion, nameof(request.RequiredSkillVersion));
        Require(request.AuthorityPolicyVersion, nameof(request.AuthorityPolicyVersion));
        Require(request.RiskClass, nameof(request.RiskClass));

        if (request.CreatedAt == default)
        {
            throw new ContextCapsuleCompileException(
                "CreatedAt must be explicit.");
        }

        ValidateDistinctNonEmpty(request.OwnerDirectiveIds, "owner directive ids");
        ValidateDistinctNonEmpty(request.AllowedScope, "allowed scope");
        ValidateDistinct(request.ForbiddenScope, "forbidden scope");
        ValidateDistinctNonEmpty(request.ExpectedOutputs, "expected outputs");
        ValidateDistinctNonEmpty(request.AcceptanceTests, "acceptance tests");

        var knownOwnerDirectives = resolution.OwnerDirectiveIds
            .ToHashSet(StringComparer.Ordinal);

        if (request.OwnerDirectiveIds.Any(id => !knownOwnerDirectives.Contains(id)))
        {
            throw new ContextCapsuleCompileException(
                "Capsule requested an Owner directive that was not resolved.");
        }

        if (request.AllowedScope.Intersect(
                request.ForbiddenScope,
                StringComparer.Ordinal).Any())
        {
            throw new ContextCapsuleCompileException(
                "Allowed and forbidden scope may not overlap.");
        }
    }

    private static int AuthorityRank(string authorityClass) =>
        authorityClass switch
        {
            "OWNER_DIRECTIVE_TYPED" => 0,
            "LOCKED_POLICY" => 1,
            "CANONICAL_ARTIFACT" => 2,
            "ACCEPTED_EVIDENCE" => 3,
            "WORKING_DATA" => 4,
            "UNTRUSTED_EXTERNAL_DATA" => 5,
            _ => throw new ContextCapsuleCompileException(
                $"Unsupported authority class: {authorityClass}")
        };

    private static void Require(string value, string name)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            throw new ContextCapsuleCompileException(
                $"Capsule field is required: {name}");
        }
    }

    private static void ValidateDistinctNonEmpty(
        IReadOnlyList<string> values,
        string label)
    {
        if (values.Count == 0)
        {
            throw new ContextCapsuleCompileException(
                $"{label} may not be empty.");
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
            throw new ContextCapsuleCompileException(
                $"{label} must be explicit and unique.");
        }
    }

    private sealed record CapsuleFingerprint(
        string ProjectId,
        string JobOrChangeId,
        DateTimeOffset CreatedAt,
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
}
