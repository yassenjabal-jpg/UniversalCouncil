using System.Diagnostics;
using System.IO;
using System.Security.Cryptography;
using System.Text.Json;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Threading;
using UniversalCouncil.CommandCenter;
using UniversalCouncil.CommandCenter.Core;
using UniversalCouncil.CommandCenter.Host;
internal static class WorkspaceUiChecks
{
    public static void Run(Action<bool,string> check)
    {
        var root=Path.Combine(Path.GetTempPath(),"workspace-ui-"+Guid.NewGuid());
        var repo=Path.Combine(root,"repo");Directory.CreateDirectory(repo);
        var store=Path.Combine(root,"sessions");Directory.CreateDirectory(store);
        var artifact=Path.Combine(root,"artifact.txt");File.WriteAllText(artifact,"fixture");
        var config=Path.Combine(root,"workspace.json");
        var window=new SupervisionInspectorWindow();
        void Pump()=>window.Dispatcher.Invoke(()=>{},DispatcherPriority.ApplicationIdle);
        void Await(Task task) {
            var timer=Stopwatch.StartNew();
            while(!task.IsCompleted) {if(timer.Elapsed>TimeSpan.FromSeconds(30))throw new TimeoutException();Pump();Thread.Sleep(5);}
            task.GetAwaiter().GetResult();Pump();
        }
        T Field<T>(string name) where T:FrameworkElement=>(T)window.FindName(name);
        string Git(params string[] args) {
            var s=new ProcessStartInfo("git"){WorkingDirectory=repo,UseShellExecute=false,RedirectStandardOutput=true,RedirectStandardError=true};
            foreach(var a in args)s.ArgumentList.Add(a);
            using var p=Process.Start(s)!;var output=p.StandardOutput.ReadToEnd();var error=p.StandardError.ReadToEnd();
            if(!p.WaitForExit(10000)||p.ExitCode!=0)throw new Exception(error);return output.Trim();
        }
        try {
            Git("init","-q");Git("config","user.name","UIFixture");Git("config","user.email","fixture@example.invalid");
            File.WriteAllText(Path.Combine(repo,"source.txt"),"fixture");Git("add",".");Git("commit","-qm","fixture");
            var rev=Git("rev-parse","HEAD");var hash=Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(artifact)));
            var service=CommandCenterComposition.CreateLocalReviewSessions(AppContext.BaseDirectory,store);
            var session=service.Create(new("workspace-ui","universal-council-command-center",rev,"minor_reversible_craft",[],[],[]),hash,TimeSpan.FromHours(1));
            var descriptor=new LocalWorkspaceDescriptor(1,session.Request.ProjectId,session.Request.ChangeId,session.Id,store,repo,artifact);
            File.WriteAllText(config,JsonSerializer.Serialize(descriptor));
            window.Show();Pump();
            Await(window.InspectWorkspaceAsync(config));
            check(Field<TextBlock>("WorkspaceLabel").Text.Contains(session.Request.ChangeId)&&
                Field<TextBox>("Revision").Text==rev,"workspace UI binds selected project/session to observed Git");
            check(Field<TextBox>("Details").Text.Contains("\n")&&!Field<TextBox>("Details").Text.Contains(@"\n"),
                "observed workspace metadata uses real line breaks");
            check(Field<TextBox>("Artifact").Text.Equals(hash,StringComparison.OrdinalIgnoreCase)&&
                Field<TextBox>("Artifact").IsReadOnly&&Field<StackPanel>("Inputs").Visibility==Visibility.Collapsed,
                "workspace UI captures bytes without manual freshness entry");
            File.WriteAllText(artifact,"changed");
            Field<Button>("LoadButton").RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
            var timer=Stopwatch.StartNew();
            while(!Field<Button>("LoadButton").IsEnabled){if(timer.Elapsed>TimeSpan.FromSeconds(30))throw new TimeoutException();Pump();Thread.Sleep(5);}
            check(Field<TextBlock>("Status").Text==SupervisionInspectorWindow.StateLabel("INVALIDATED"),"workspace refresh recaptures changed artifact");
            var broken=Path.Combine(root,"broken.json");File.WriteAllText(broken,"{");
            Await(window.InspectWorkspaceAsync(broken));
            check(Field<TextBox>("Details").Text.Length==0&&Field<TextBlock>("WorkspaceLabel").Text.Contains("تعذر"),
                "second workspace failure clears preceding project details");
            Field<Button>("ManualButton").RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
            check(Field<TextBox>("Revision").Text.Length==0&&!Field<TextBox>("Revision").IsReadOnly&&
                Field<StackPanel>("Inputs").Visibility==Visibility.Visible,"manual reset removes workspace binding");
        }
        finally {
            window.Close();
            foreach(var file in Directory.EnumerateFiles(root,"*",SearchOption.AllDirectories))
                File.SetAttributes(file,File.GetAttributes(file)&~FileAttributes.ReadOnly);
            Directory.Delete(root,true);
        }
    }
}
