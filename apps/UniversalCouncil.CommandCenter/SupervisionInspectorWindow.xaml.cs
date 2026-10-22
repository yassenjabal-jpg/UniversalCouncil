using System.IO;
using System.Text;
using System.Windows;
using System.Windows.Input;
using UniversalCouncil.CommandCenter.Core;
using UniversalCouncil.CommandCenter.Host;

namespace UniversalCouncil.CommandCenter;

public partial class SupervisionInspectorWindow : Window
{
    private bool loading;
    private bool closed;
    public SupervisionInspectorWindow()
    {
        InitializeComponent();
        Closed += (_, _) => closed = true;
        Loaded += (_, _) => Storage.Focus();
        PreviewKeyDown += (_, e) => { if (e.Key == Key.Escape) { Close(); e.Handled = true; } };
    }
    private async void Load_Click(object sender, RoutedEventArgs e)
    {
        if (loading || closed) return;
        Details.Clear();
        Status.Text = "جارٍ فحص الجلسة…";
        var storage = Storage.Text.Trim();
        var idText = SessionId.Text.Trim();
        var revision = Revision.Text.Trim();
        var artifact = Artifact.Text.Trim();
        if (!Path.IsPathFullyQualified(storage) || !Guid.TryParse(idText, out var id) ||
            revision.Length != 40 || !revision.All(char.IsAsciiHexDigit) ||
            artifact.Length != 64 || !artifact.All(char.IsAsciiHexDigit))
        {
            Status.Text = "تعذر الفحص: تحقق من المجلد والمعرّف وبصمتي النسخة والمخرج.";
            return;
        }
        loading = true;
        Inputs.IsEnabled = LoadButton.IsEnabled = false;
        try
        {
            var snapshot = await Task.Run(() => CommandCenterComposition.CreateLocalSupervisionReader(
                AppContext.BaseDirectory, storage).Read(id, revision, artifact));
            if (closed) return;
            Status.Text = StateLabel(snapshot.State);
            Details.Text = Describe(snapshot);
        }
        catch (Exception error) when (error is InvalidDataException or IOException or
            UnauthorizedAccessException or ArgumentException or System.Text.Json.JsonException)
        {
            if (!closed) Status.Text = "الجلسة غير متاحة: بيانات غير صالحة أو ملف مفقود أو تعذر الوصول. لم تعرض نتيجة سابقة.";
        }
        finally
        {
            loading = false;
            if (!closed) { Inputs.IsEnabled = LoadButton.IsEnabled = true; LoadButton.Focus(); }
        }
    }
    public static string StateLabel(string state) => state switch {
        "INVALIDATED" => "الجلسة مبطلة — تغيّر الربط أو السياسة أو تسلسل الوقت.",
        "EXPIRED" => "انتهت صلاحية الجلسة.",
        "BLOCKED" => "يوجد مانع مسجّل.",
        "RETURNED_FOR_CHANGES" => "أعيد العمل للتعديل.",
        "OWNER_DECISION_REQUIRED" => "يوجد طلب مسجّل لقرار المالك.",
        "RESULTS_RECORDED" => "سُجلت جميع التقارير — ليست موافقة.",
        "REVIEWING" => "الجلسة تنتظر بقية التقارير.",
        _ => "حالة غير معروفة."
    };
    public static string Describe(LocalSupervisionSnapshot snapshot)
    {
        var text = new StringBuilder();
        text.AppendLine($"المشروع: {snapshot.ProjectId}\nالتغيير: {snapshot.ChangeId}\nالحالة: {snapshot.State}");
        text.AppendLine($"إصدار السجل: {snapshot.Version}\nالمصدر: {snapshot.SourceRevision}\nالمخرج: {snapshot.ArtifactSha256}");
        text.AppendLine($"آخر ملاحظة UTC: {snapshot.LastObservedAt:O}\nتنتهي UTC: {snapshot.ExpiresAt:O}");
        text.AppendLine("\nأدوار لم يسجل لها تقرير:");
        foreach (var role in snapshot.PendingRoleIds) text.AppendLine(role);
        if (snapshot.PendingRoleIds.Count == 0) text.AppendLine("لا توجد أدوار منتظرة؛ هذا لا يعني القبول.");
        foreach (var report in snapshot.Reports)
        {
            text.AppendLine($"\nالدور: {report.RoleId}\nصاحب التقرير (غير موثق): {report.Actor}\nالنتيجة المبلغة: {report.Outcome}\nالسبب: {report.Rationale}\nالوقت UTC: {report.RecordedAt:O}\nمراجع غير متحقق منها:");
            foreach (var reference in report.EvidenceRefs) text.AppendLine(reference);
        }
        text.AppendLine("\nالهوية والمراجع والنتائج تقارير من المتصل. لم يتحقق هذا الفحص من بايتات الأدلة أو معناها. لا موافقة، لا تنفيذ حي، Stage 8 مغلقة.");
        return text.ToString();
    }
    private void Close_Click(object sender, RoutedEventArgs e) => Close();
}
