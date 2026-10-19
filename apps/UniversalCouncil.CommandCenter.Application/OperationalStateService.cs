using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter.Application;

public sealed class OperationalStateService :
    ICommandCenterSnapshotProvider,
    IOperationalStateProvider
{
    private const string SupportedSchemaVersion = "1.0";
    private readonly IOperationalStateReader reader;

    public OperationalStateService(IOperationalStateReader reader)
    {
        this.reader = reader;
    }

    public OperationalStateProjection GetOperationalState()
    {
        try
        {
            var document = reader.Read();
            Validate(document);

            var evidence = document.Evidence
                .Select(item => new EvidenceReceipt(
                    item.Id,
                    item.Category,
                    item.Title,
                    item.Result,
                    item.Reference,
                    item.Digest,
                    item.OccurredAt))
                .ToArray();

            var approvals = document.Approvals
                .Select(item => new OwnerApprovalItem(
                    item.Id,
                    item.Title,
                    item.State,
                    item.Scope,
                    item.EvidenceReference))
                .ToArray();

            return new OperationalStateProjection(
                OperationalStateHealth.Healthy,
                document.SourceLabel,
                document.BaselineRevision,
                document.ProjectLabel,
                document.StageLabel,
                document.StageState,
                document.PhaseGateLabel,
                false,
                string.Empty,
                evidence,
                approvals,
                new UsageProjection(
                    document.Usage.State,
                    document.Usage.Provider,
                    document.Usage.RecordedModelCalls,
                    document.Usage.RecordedCostUsd,
                    document.Usage.Note),
                new ExecutionManifestProjection(
                    document.ExecutionManifest.State,
                    document.ExecutionManifest.Gate,
                    document.ExecutionManifest.LastManifestId,
                    document.ExecutionManifest.Note));
        }
        catch (OperationalStateReadException exc)
        {
            return OperationalStateProjection.Unavailable(exc.Message);
        }
        catch (Exception exc)
        {
            return OperationalStateProjection.Unavailable(
                $"Unexpected state-read failure: {exc.GetType().Name}");
        }
    }

    public CommandCenterSnapshot GetSnapshot()
    {
        var state = GetOperationalState();

        if (state.Health == OperationalStateHealth.Unavailable)
        {
            return new CommandCenterSnapshot(
                ProductName: "UniversalCouncil Command Center",
                StageLabel: "المرحلة 2 — مصدر الحالة غير متاح",
                PhaseGateLabel: "Phase 0 غير مكتملة — التنفيذ الحقيقي مقفول",
                ExecutionEnabled: false,
                ExecutionStateLabel: "LOCKED BY PHASE 0",
                OwnerApprovalLabel: "تعذر تحميل سجل الموافقات؛ لا توجد صلاحية كتابة.",
                Modules:
                [
                    new(
                        "state",
                        "الحالة التشغيلية",
                        state.ProblemLabel,
                        ModuleState.Locked,
                        "غير متاح"),
                    new(
                        "execution",
                        "التنفيذ على YASSIN",
                        "أي Shell/GUI/Provider execution محظور.",
                        ModuleState.Locked,
                        "مقفول")
                ]);
        }

        return new CommandCenterSnapshot(
            ProductName: "UniversalCouncil Command Center",
            StageLabel: state.StageLabel,
            PhaseGateLabel: state.PhaseGateLabel,
            ExecutionEnabled: false,
            ExecutionStateLabel: "LOCKED BY PHASE 0",
            OwnerApprovalLabel: "سجل الموافقات موصول للقراءة فقط؛ لا توجد كتابة في Stage 2.",
            Modules:
            [
                new(
                    "projects",
                    "المشاريع",
                    "موصولة بمصدر Operational State الحقيقي للقراءة.",
                    ModuleState.ReadOnly,
                    "قراءة حقيقية"),
                new(
                    "evidence",
                    "الأدلة",
                    $"{state.Evidence.Count} إيصال دليل محمّل من مصدر الحالة.",
                    ModuleState.ReadOnly,
                    "قراءة حقيقية"),
                new(
                    "approvals",
                    "مكتب المالك",
                    $"{state.Approvals.Count} سجل موافقة محمّل؛ إجراءات الكتابة معطلة.",
                    ModuleState.ReadOnly,
                    "قراءة فقط"),
                new(
                    "council",
                    "المجلس",
                    "تنسيق المجلس غير موصول حتى Stage 3.",
                    ModuleState.NotConnected,
                    "غير متصل"),
                new(
                    "studio",
                    "الاستوديو",
                    "تنسيق الاستوديو غير موصول حتى Stage 3.",
                    ModuleState.NotConnected,
                    "غير متصل"),
                new(
                    "execution",
                    "التنفيذ على YASSIN",
                    "التنفيذ خارج صلاحية Stage 2 ويبقى مقفولًا.",
                    ModuleState.Locked,
                    "مقفول"),
                new(
                    "capabilities",
                    "القدرات والأدوات",
                    "Capability Hub محفوظ لمرحلة لاحقة.",
                    ModuleState.Locked,
                    "مرحلة لاحقة")
            ]);
    }

    private static void Validate(OperationalStateDocument document)
    {
        if (document.SchemaVersion != SupportedSchemaVersion)
        {
            throw new OperationalStateReadException(
                $"Unsupported operational state schema: {document.SchemaVersion}");
        }

        if (!string.Equals(document.SourceType, "repository_projection", StringComparison.Ordinal))
        {
            throw new OperationalStateReadException(
                $"Unsupported operational state source type: {document.SourceType}");
        }

        if (document.ExecutionEnabled)
        {
            throw new OperationalStateReadException(
                "Stage 2 state attempted to enable execution; fail-closed policy applied.");
        }

        if (string.IsNullOrWhiteSpace(document.BaselineRevision) ||
            string.IsNullOrWhiteSpace(document.ProjectLabel) ||
            string.IsNullOrWhiteSpace(document.StageLabel) ||
            string.IsNullOrWhiteSpace(document.PhaseGateLabel))
        {
            throw new OperationalStateReadException(
                "Operational state is missing required identity/gate fields.");
        }

        if (document.Evidence.Select(item => item.Id).Distinct(StringComparer.Ordinal).Count() != document.Evidence.Count)
        {
            throw new OperationalStateReadException("Duplicate evidence receipt id.");
        }

        if (document.Approvals.Select(item => item.Id).Distinct(StringComparer.Ordinal).Count() != document.Approvals.Count)
        {
            throw new OperationalStateReadException("Duplicate owner approval id.");
        }

        if (!string.Equals(document.Usage.State, "NOT_CONNECTED", StringComparison.Ordinal) &&
            document.Usage.RecordedCostUsd is null)
        {
            throw new OperationalStateReadException(
                "Connected usage state must include an explicit recorded cost.");
        }
    }
}
