using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Threading;
using UniversalCouncil.CommandCenter;
using UniversalCouncil.CommandCenter.Core;
using UniversalCouncil.CommandCenter.Host;

internal static class Program
{
    [STAThread]
    private static int Main(string[] args)
    {
        var app = new App();
        app.InitializeComponent();
        SynchronizationContext.SetSynchronizationContext(new DispatcherSynchronizationContext(app.Dispatcher));
        app.ShutdownMode = ShutdownMode.OnExplicitShutdown;
        var root = Path.Combine(Path.GetTempPath(), "murtakaz-ui-" + Guid.NewGuid());
        Directory.CreateDirectory(root);
        var window = new SupervisionInspectorWindow();
        T Field<T>(string name) where T : FrameworkElement => (T)window.FindName(name);
        var count = 0;
        void Check(bool ok, string label) { if (!ok) throw new Exception(label); Console.WriteLine("PASS " + label); count++; }
        void Pump() => window.Dispatcher.Invoke(() => { }, DispatcherPriority.ApplicationIdle);
        void Load()
        {
            Field<Button>("LoadButton").RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
            var timeout = System.Diagnostics.Stopwatch.StartNew();
            while (!Field<Button>("LoadButton").IsEnabled)
            {
                if (timeout.Elapsed > TimeSpan.FromSeconds(15)) throw new TimeoutException();
                Pump(); Thread.Sleep(5);
            }
            Pump();
        }
        try
        {
            var service = CommandCenterComposition.CreateLocalReviewSessions(AppContext.BaseDirectory, root);
            var revision = new string('a',40); var hash = new string('b',64);
            var session = service.Create(new LocalReviewRequest("UI-FIXTURE", "universal-council-command-center",
                revision, "material_product_change", ["architecture_boundary"], [], []), hash, TimeSpan.FromHours(1));
            session = service.Record(session.Id, session.Version, revision, hash,
                session.Plan.Assignments[0].RoleId, "FIXTURE caller", "BLOCKED", "FIXTURE dissent retained", ["fixture-evidence-not-verified"]);
            window.Show(); Pump();
            Field<TextBox>("Storage").Text = root;
            Field<TextBox>("SessionId").Text = session.Id.ToString();
            Field<TextBox>("Revision").Text = revision;
            Field<TextBox>("Artifact").Text = hash;
            Load();
            var details = Field<TextBox>("Details");
            Check(details.Text.Contains("FIXTURE dissent retained") && details.Text.Contains("fixture-evidence-not-verified"),
                "actual WPF displays full dissent and references");
            Check(Field<TextBlock>("Status").Text == SupervisionInspectorWindow.StateLabel("BLOCKED"),
                "actual WPF state reflects blocker");
            Check(details.Text.Contains(session.Plan.Assignments[1].RoleId), "pending reviewer visible");
            Check(window.FlowDirection == FlowDirection.RightToLeft && Field<TextBox>("Revision").FlowDirection == FlowDirection.LeftToRight,
                "RTL inspector and LTR hashes");
            Check(details.IsReadOnly && Field<Button>("LoadButton").IsEnabled, "selectable readonly reports and controls restored");
            if (args.Length > 0)
            {
                window.UpdateLayout();
                var bitmap = new RenderTargetBitmap((int)window.ActualWidth, (int)window.ActualHeight,96,96,PixelFormats.Pbgra32);
                bitmap.Render(window);
                var png = new PngBitmapEncoder(); png.Frames.Add(BitmapFrame.Create(bitmap));
                using var output = File.Create(args[0]); png.Save(output);
            }
            Field<TextBox>("Revision").Text = "unknown";
            Load();
            Check(details.Text.Length == 0 && Field<TextBlock>("Status").Text.Contains("تعذر"), "failed second load clears previous details");
            Field<TextBox>("Revision").Text = new string('c',40);
            Load();
            Check(Field<TextBlock>("Status").Text == SupervisionInspectorWindow.StateLabel("INVALIDATED"), "actual WPF displays invalidated binding");
            Field<TextBox>("SessionId").Text = Guid.NewGuid().ToString();
            Load();
            Check(details.Text.Length == 0 && Field<TextBlock>("Status").Text.Contains("غير متاحة"), "missing session unavailable without stale details");
            Field<TextBox>("SessionId").Text = session.Id.ToString();
            File.WriteAllText(Path.Combine(root,session.Id.ToString("N")+".json"), "{");
            Load();
            Check(details.Text.Length == 0 && Field<TextBlock>("Status").Text.Contains("غير متاحة"), "corrupt session unavailable");
            var expired = service.Create(new LocalReviewRequest("UI-EXPIRED-FIXTURE", "universal-council-command-center",
                revision, "material_product_change", ["architecture_boundary"], [], []), hash, TimeSpan.FromTicks(1));
            Field<TextBox>("SessionId").Text = expired.Id.ToString();
            Field<TextBox>("Revision").Text = revision;
            Load();
            Check(Field<TextBlock>("Status").Text == SupervisionInspectorWindow.StateLabel("EXPIRED"), "actual WPF displays expiry");
            window.Width = 580; window.Height = 450; Pump(); window.UpdateLayout();
            Check(window.ActualWidth >= 580 && window.ActualHeight >= 450, "inspector supports minimum window geometry");
            Field<Button>("LoadButton").RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
            window.Close();
            for (var i = 0; i < 100; i++) { Pump(); Thread.Sleep(5); }
            Check(!window.IsVisible, "close during asynchronous inspection does not reopen window");
            WorkspaceUiChecks.Run(Check);
            Console.WriteLine($"PASS {count} actual WPF inspector checks (isolated fixtures)");
            return 0;
        }
        finally { window.Close(); app.Shutdown(); Directory.Delete(root,true); }
    }
}
