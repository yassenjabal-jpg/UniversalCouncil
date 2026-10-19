namespace UniversalCouncil.CommandCenter.Core;

public enum OperationalStateHealth
{
    Healthy,
    Unavailable
}

public sealed record EvidenceReceipt(
    string Id,
    string Category,
    string Title,
    string ResultLabel,
    string Reference,
    string? Digest,
    string OccurredAt);

public sealed record OwnerApprovalItem(
    string Id,
    string Title,
    string StateLabel,
    string ScopeLabel,
    string EvidenceReference);

public sealed record UsageProjection(
    string StateLabel,
    string ProviderLabel,
    long? RecordedModelCalls,
    decimal? RecordedCostUsd,
    string Note);

public sealed record ExecutionManifestProjection(
    string StateLabel,
    string GateLabel,
    string? LastManifestId,
    string Note);

public sealed record OperationalStateProjection(
    OperationalStateHealth Health,
    string SourceLabel,
    string BaselineRevision,
    string ProjectLabel,
    string StageLabel,
    string StageStateLabel,
    string PhaseGateLabel,
    bool ExecutionEnabled,
    string ProblemLabel,
    IReadOnlyList<EvidenceReceipt> Evidence,
    IReadOnlyList<OwnerApprovalItem> Approvals,
    UsageProjection Usage,
    ExecutionManifestProjection ExecutionManifest)
{
    public static OperationalStateProjection Unavailable(string problem) =>
        new(
            OperationalStateHealth.Unavailable,
            "STATE SOURCE UNAVAILABLE",
            "UNKNOWN",
            "UniversalCouncil Command Center",
            "Stage 2 — Operational State",
            "UNAVAILABLE",
            "LOCKED BY PHASE 0",
            false,
            problem,
            [],
            [],
            new(
                "NOT CONNECTED",
                "No usage provider",
                null,
                null,
                "لا توجد بيانات استخدام موصولة؛ لا يتم عرض تكلفة صفرية وهمية."),
            new(
                "NO EXECUTION AUTHORIZED",
                "Phase 0",
                null,
                "لا يوجد تنفيذ مسموح في Stage 2."));
}

public interface IOperationalStateProvider
{
    OperationalStateProjection GetOperationalState();
}
