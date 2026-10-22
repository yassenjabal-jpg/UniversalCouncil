using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter.Application;

public interface ICommittedEvidenceManifestReader
{
    CommittedEvidenceManifest Read(EvidenceVerificationRequest request);
}
public interface ILocalEvidenceContentReader
{
    EvidenceMeasurement Measure(string relativePath, long expectedSize);
}
public static class EvidenceRules
{
    public const long MaxFileBytes = 1024L * 1024 * 1024;
    public const long MaxBundleBytes = 2L * 1024 * 1024 * 1024;
    public static bool Hex(string? value, int length) =>
        value is not null && value.Length == length && value.All(char.IsAsciiHexDigit);
    public static void RelativePath(string? path)
    {
        if (string.IsNullOrWhiteSpace(path) || path.Length > 512 || path.StartsWith('/') ||
            path.Contains('\\') || path.Any(c => char.IsControl(c) || new[] { ':', '*', '?', '<', '>', '|', (char)34 }.Contains(c)))
            throw new InvalidDataException("UNSAFE_RELATIVE_PATH");
        foreach (var segment in path.Split('/'))
        {
            var device = segment.Split('.')[0].ToUpperInvariant();
            if (segment.Length == 0 || segment is "." or ".." || segment.EndsWith('.') || segment.EndsWith(' ') ||
                device is "CON" or "PRN" or "AUX" or "NUL" or "CLOCK$" or "CONIN$" or "CONOUT$" ||
                device.Length == 4 && (device.StartsWith("COM") || device.StartsWith("LPT")) &&
                    (device[3] is >= '0' and <= '9' or '¹' or '²' or '³'))
                throw new InvalidDataException("AMBIGUOUS_RELATIVE_PATH");
        }
    }
}
public sealed class EvidenceVerifier(ICommittedEvidenceManifestReader manifests,
    ILocalEvidenceContentReader content, bool allowFixtures = false)
{
    public EvidenceVerificationResult Verify(EvidenceVerificationRequest request)
    {
        CommittedEvidenceManifest? snapshot = null;
        var measured = new List<EvidenceMeasurement>();
        try
        {
            if (request is null || string.IsNullOrWhiteSpace(request.ProjectId) || request.ProjectId.Length > 256 ||
                string.IsNullOrWhiteSpace(request.ChangeId) || request.ChangeId.Length > 256 ||
                !EvidenceRules.Hex(request.SourceRevision,40) || !EvidenceRules.Hex(request.ManifestRevision,40))
                throw new InvalidDataException("INVALID_BINDING_REQUEST");
            EvidenceRules.RelativePath(request.ManifestPath);
            snapshot = manifests.Read(request);
            if (snapshot is null || !EvidenceRules.Hex(snapshot.CommitId,40) ||
                !string.Equals(snapshot.CommitId, request.ManifestRevision, StringComparison.OrdinalIgnoreCase) ||
                !EvidenceRules.Hex(snapshot.BlobId,40) || !EvidenceRules.Hex(snapshot.ManifestSha256,64))
                throw new InvalidDataException("INVALID_COMMITTED_MANIFEST_PROVENANCE");
            var m = snapshot.Manifest;
            if (m is null || m.SchemaVersion != 1 || m.ProjectId != request.ProjectId ||
                m.ChangeId != request.ChangeId || !string.Equals(m.SourceRevision, request.SourceRevision,
                    StringComparison.OrdinalIgnoreCase) || !EvidenceRules.Hex(m.SourceRevision,40) ||
                m.EvidenceKind is not ("REAL" or "FIXTURE") || m.Entries is null ||
                m.Entries.Length is < 1 or > 100)
                throw new InvalidDataException("INVALID_MANIFEST_BINDING_OR_SCHEMA");
            if (m.EvidenceKind == "FIXTURE" && !allowFixtures)
                throw new InvalidDataException("FIXTURE_REQUIRES_EXPLICIT_MODE");
            long total = 0;
            var paths = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (var entry in m.Entries)
            {
                if (entry is null || !EvidenceRules.Hex(entry.Sha256,64) || entry.SizeBytes < 0 ||
                    entry.SizeBytes > EvidenceRules.MaxFileBytes)
                    throw new InvalidDataException("INVALID_ENTRY_OR_SIZE_LIMIT");
                EvidenceRules.RelativePath(entry.Path);
                if (!paths.Add(entry.Path)) throw new InvalidDataException("DUPLICATE_ARTIFACT_PATH");
                total += entry.SizeBytes;
                if (total > EvidenceRules.MaxBundleBytes) throw new InvalidDataException("BUNDLE_SIZE_LIMIT");
            }
            foreach (var entry in m.Entries)
            {
                var observed = content.Measure(entry.Path, entry.SizeBytes);
                if (observed.Path != entry.Path || observed.SizeBytes != entry.SizeBytes ||
                    !string.Equals(observed.Sha256, entry.Sha256, StringComparison.OrdinalIgnoreCase))
                    throw new InvalidDataException("ARTIFACT_BYTES_MISMATCH");
                measured.Add(observed);
            }
            return new(m.EvidenceKind == "FIXTURE" ? "FIXTURE_CONTENT_MATCH" : "CONTENT_MATCH",
                request.ProjectId, request.ChangeId, request.SourceRevision.ToLowerInvariant(),
                snapshot.CommitId, snapshot.BlobId, snapshot.ManifestSha256, m.EvidenceKind,
                measured.ToArray(), []);
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or
            InvalidDataException or System.Text.Json.JsonException or ArgumentException or
            InvalidOperationException or NotSupportedException or System.ComponentModel.Win32Exception)
        {
            return new("UNAVAILABLE", request?.ProjectId ?? "", request?.ChangeId ?? "",
                request?.SourceRevision ?? "", snapshot?.CommitId ?? "", snapshot?.BlobId ?? "",
                snapshot?.ManifestSha256 ?? "", snapshot?.Manifest?.EvidenceKind ?? "UNKNOWN",
                measured.ToArray(), [ex is InvalidDataException ? ex.Message : "READ_OR_GIT_FAILURE"]);
        }
    }
}
