using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter;

internal sealed class PrototypeCommandCenterSnapshotProvider : ICommandCenterSnapshotProvider
{
    public CommandCenterSnapshot GetSnapshot()
    {
        return new CommandCenterSnapshot(
            ProductName: "UniversalCouncil Command Center",
            StageLabel: "المرحلة 1 — Shell & Architecture Boundary",
            PhaseGateLabel: "Phase 0 غير مكتملة — التنفيذ الحقيقي مقفول",
            ExecutionEnabled: false,
            ExecutionStateLabel: "LOCKED BY PHASE 0",
            OwnerApprovalLabel: "لا توجد موافقات حقيقية متصلة بعد",
            Modules:
            [
                new(
                    "council",
                    "المجلس",
                    "واجهة الدور والحالة فقط؛ لم يتم توصيل Council Runtime بعد.",
                    ModuleState.NotConnected,
                    "غير متصل"),
                new(
                    "studio",
                    "الاستوديو",
                    "واجهة الإنتاج فقط؛ لم يتم توصيل Studio Runtime بعد.",
                    ModuleState.NotConnected,
                    "غير متصل"),
                new(
                    "projects",
                    "المشاريع",
                    "سيتم توصيلها بمصدر حالة حقيقي في المرحلة 2.",
                    ModuleState.ReadOnly,
                    "نموذج قراءة فقط"),
                new(
                    "execution",
                    "التنفيذ على YASSIN",
                    "أي Shell/GUI/Provider execution محظور في هذه المرحلة.",
                    ModuleState.Locked,
                    "مقفول"),
                new(
                    "evidence",
                    "الأدلة",
                    "لا توجد Evidence Bus متصلة بالواجهة بعد.",
                    ModuleState.NotConnected,
                    "غير متصل"),
                new(
                    "capabilities",
                    "القدرات والأدوات",
                    "Capability Hub سيُبنى بعد تثبيت Runtime وحدود الصلاحيات.",
                    ModuleState.Locked,
                    "مرحلة لاحقة")
            ]);
    }
}
