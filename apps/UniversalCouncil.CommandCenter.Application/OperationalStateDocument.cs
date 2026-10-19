namespace UniversalCouncil.CommandCenter.Application;

public sealed record OperationalStateDocument(
    string SchemaVersion,
    string SourceType,
    string SourceLabel,
    string BaselineRevision,
    string ProjectId,
    string ProjectLabel,
    string StageId,
    string StageLabel,
    string StageState,
    bool ExecutionEnabled,
    string PhaseGateLabel,
    IReadOnlyList<EvidenceDocument> Evidence,
    IReadOnlyList<ApprovalDocument> Approvals,
    UsageDocument Usage,
    ExecutionManifestDocument ExecutionManifest);

public sealed record EvidenceDocument(
    string Id,
    string Category,
    string Title,
    string Result,
    string Reference,
    string? Digest,
    string OccurredAt);

public sealed record ApprovalDocument(
    string Id,
    string Title,
    string State,
    string Scope,
    string EvidenceReference);

public sealed record UsageDocument(
    string State,
    string Provider,
    long? RecordedModelCalls,
    decimal? RecordedCostUsd,
    string Note);

public sealed record ExecutionManifestDocument(
    string State,
    string Gate,
    string? LastManifestId,
    string Note);
