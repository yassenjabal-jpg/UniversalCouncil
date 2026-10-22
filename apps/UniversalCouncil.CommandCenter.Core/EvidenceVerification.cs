namespace UniversalCouncil.CommandCenter.Core;

public sealed record EvidenceEntry(string Path, string Sha256, long SizeBytes);
public sealed record EvidenceManifest(int SchemaVersion, string ProjectId, string ChangeId,
    string SourceRevision, string EvidenceKind, EvidenceEntry[] Entries);
public sealed record EvidenceVerificationRequest(string ProjectId, string ChangeId,
    string SourceRevision, string ManifestRevision, string ManifestPath);
public sealed record CommittedEvidenceManifest(EvidenceManifest Manifest,
    string CommitId, string BlobId, string ManifestSha256);
public sealed record EvidenceMeasurement(string Path, string Sha256, long SizeBytes);
public sealed record EvidenceVerificationResult(string Status, string ProjectId, string ChangeId,
    string SourceRevision, string ManifestRevision, string ManifestBlobId, string ManifestSha256,
    string EvidenceKind, EvidenceMeasurement[] Files, string[] Errors)
{
    public bool ContentMatchesDeclaration => Status is "CONTENT_MATCH" or "FIXTURE_CONTENT_MATCH";
    public string BindingKind => "COMMITTED_DECLARATION_NOT_CAPTURE_ATTESTATION";
    public bool CaptureRevisionIndependentlyVerified => false;
    public bool SemanticEvidenceAccepted => false;
    public bool ApprovalGranted => false;
    public bool ExecutionAuthority => false;
    public bool Stage8Opened => false;
}
