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
    private string? workspacePath;
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
        if (workspacePath is not null) { await InspectWorkspaceAsync(workspacePath); return; }
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
        Inputs.IsEnabled = LoadButton.IsEnabled = WorkspaceActions.IsEnabled = false;
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
            if (!closed) { Inputs.IsEnabled = LoadButton.IsEnabled = WorkspaceActions.IsEnabled = true; LoadButton.Focus(); }
        }
    }
    private void ResetManual()
    {
        workspacePath = null;
        Inputs.Visibility = Visibility.Visible;
        Details.Clear();
        Storage.Clear(); SessionId.Clear(); Revision.Clear(); Artifact.Clear();
        Storage.IsReadOnly = SessionId.IsReadOnly = Revision.IsReadOnly = Artifact.IsReadOnly = false;
        WorkspaceLabel.Text = "الفحص اليدوي — لم تربط مساحة مشروع.";
        Status.Text = "أدخل بيانات الجلسة ثم افحصها.";
    }
    private void Manual_Click(object sender, RoutedEventArgs e)
    {
        if (!loading && !closed) ResetManual();
    }
    private async void OpenWorkspace_Click(object sender, RoutedEventArgs e)
    {
        if (loading || closed) return;
        ResetManual();
        var dialog = new Microsoft.Win32.OpenFileDialog {
            Title = "فتح مساحة مشروع محلية", Filter = "ملف مساحة مشروع (*.json)|*.json", CheckFileExists = true };
        if (dialog.ShowDialog(this) == true) await InspectWorkspaceAsync(dialog.FileName);
    }
    public async Task InspectWorkspaceAsync(string configurationPath)
    {
        if (loading || closed) return;
        workspacePath = configurationPath;
        Inputs.Visibility = Visibility.Collapsed;
        Details.Clear();
        Storage.Clear(); SessionId.Clear(); Revision.Clear(); Artifact.Clear();
        WorkspaceLabel.Text = "مساحة مشروع محلية محددة — جارٍ التحقق من الربط.";
        Status.Text = "جارٍ قراءة نسخة Git وبصمة المخرج الفعليتين…";
        Storage.IsReadOnly = SessionId.IsReadOnly = Revision.IsReadOnly = Artifact.IsReadOnly = true;
        loading = true;
        Inputs.IsEnabled = LoadButton.IsEnabled = WorkspaceActions.IsEnabled = false;
        try
        {
            var observed = await Task.Run(() => CommandCenterComposition.CreateWorkspaceSupervisionReader(
                AppContext.BaseDirectory).Read(configurationPath));
            if (closed) return;
            var snapshot = observed.Session;
            SessionId.Text = snapshot.Id.ToString();
            Revision.Text = observed.ObservedSourceRevision;
            Artifact.Text = observed.ObservedArtifactSha256;
            WorkspaceLabel.Text = $"المشروع: {snapshot.ProjectId} | التغيير: {snapshot.ChangeId} | الجلسة: {snapshot.Id}";
            Status.Text = StateLabel(snapshot.State);
            Details.Text = $"نسخة Git المقاسة: {observed.ObservedSourceRevision}\nبصمة المخرج المقاسة: {observed.ObservedArtifactSha256}\nملاحظة ملفات محلية عند UTC: {observed.ObservedAt:O}\nالربط إعداد محلي وليس إثبات هوية المشروع. يعاد القياس عند كل فحص.\n\n" + Describe(snapshot);
        }
        catch (Exception error) when (error is InvalidDataException or IOException or
            UnauthorizedAccessException or ArgumentException or System.Text.Json.JsonException or System.ComponentModel.Win32Exception)
        {
            if (!closed)
            {
                WorkspaceLabel.Text = "تعذر ربط مساحة المشروع.";
                Status.Text = "المشروع غير متاح: تحقق من إعداد المساحة ونظافة مستودع Git والمخرج وربط الجلسة.";
            }
        }
        finally
        {
            loading = false;
            if (!closed) { Inputs.IsEnabled = LoadButton.IsEnabled = WorkspaceActions.IsEnabled = true; LoadButton.Focus(); }
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
