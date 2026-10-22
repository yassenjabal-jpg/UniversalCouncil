using System.Diagnostics;
using System.Security.Cryptography;
using System.Text.Json;
using UniversalCouncil.CommandCenter.Application;
using UniversalCouncil.CommandCenter.Core;
using UniversalCouncil.CommandCenter.Host;
using UniversalCouncil.CommandCenter.Infrastructure;

internal static class WorkspaceChecks
{
    public static void Run(ILocalReviewPlanner planner, Action<bool,string> check)
    {
        var root = Path.Combine(Path.GetTempPath(),"murtakaz-workspace-"+Guid.NewGuid());
        var repo = Path.Combine(root,"repo"); Directory.CreateDirectory(repo);
        var store = Path.Combine(root,"sessions"); Directory.CreateDirectory(store);
        var artifact = Path.Combine(root,"artifact.txt"); File.WriteAllText(artifact,"fixture");
        var config = Path.Combine(root,"workspace.json");
        string Git(params string[] args) {
            var start = new ProcessStartInfo("git") { WorkingDirectory=repo,UseShellExecute=false,RedirectStandardOutput=true,RedirectStandardError=true };
            foreach(var arg in args) start.ArgumentList.Add(arg);
            using var p=Process.Start(start)!;var output=p.StandardOutput.ReadToEnd();var error=p.StandardError.ReadToEnd();
            if(!p.WaitForExit(10000)||p.ExitCode!=0) throw new Exception(error);return output.Trim();
        }
        try {
            Git("init","-q");Git("config","user.name","Fixture");Git("config","user.email","fixture@example.invalid");
            File.WriteAllText(Path.Combine(repo,"source.txt"),"first");Git("add",".");Git("commit","-qm","first");
            var rev=Git("rev-parse","HEAD");
            var hash=Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(artifact)));
            var service=new LocalReviewSessionService(planner,new JsonLocalReviewSessionStore(store));
            LocalReviewSession Create()=>service.Create(new("workspace-change","universal-council-command-center",rev,"minor_reversible_craft",[],[],[]),hash,TimeSpan.FromHours(1));
            var session=Create();
            var descriptor=new LocalWorkspaceDescriptor(1,session.Request.ProjectId,session.Request.ChangeId,session.Id,store,repo,artifact);
            void Save(LocalWorkspaceDescriptor d)=>File.WriteAllText(config,JsonSerializer.Serialize(d));
            Save(descriptor);
            var inspector=CommandCenterComposition.CreateWorkspaceSupervisionReader(AppContext.BaseDirectory);
            void Reject(string name) { try { inspector.Read(config);throw new Exception("Expected rejection"); }
                catch(Exception e) when(e is InvalidDataException or IOException or JsonException or ArgumentException) {check(true,name);} }
            var first=inspector.Read(config);
            check(first.Session.Id==session.Id && first.ObservedSourceRevision==rev &&
                first.ObservedArtifactSha256.Equals(hash,StringComparison.OrdinalIgnoreCase),"workspace observes actual Git and artifact bytes");
            var record=Path.Combine(store,session.Id.ToString("N")+".json");
            var before=File.ReadAllBytes(record);
            Save(descriptor with { ProjectId="other-project" });Reject("wrong project refused");
            check(before.SequenceEqual(File.ReadAllBytes(record)),"wrong project cannot mutate unrelated session");
            Save(descriptor with { ChangeId="other-change" });Reject("wrong change refused");
            check(before.SequenceEqual(File.ReadAllBytes(record)),"wrong change cannot mutate unrelated session");
            Save(descriptor);
            File.WriteAllText(Path.Combine(repo,"untracked.txt"),"dirty");Reject("untracked work refuses automatic freshness");
            File.Delete(Path.Combine(repo,"untracked.txt"));
            File.WriteAllText(Path.Combine(repo,"source.txt"),"dirty");Reject("tracked changes refuse automatic freshness");Git("checkout","--","source.txt");
            foreach(var flag in new[]{"assume-unchanged","skip-worktree"}) {
                Git("update-index","--"+flag,"source.txt");
                File.WriteAllText(Path.Combine(repo,"source.txt"),"hidden dirty");
                Reject("unsupported index flag refuses freshness: "+flag);
                check(before.SequenceEqual(File.ReadAllBytes(record)),"index flag refusal preserves session");
                Git("update-index","--no-"+flag,"source.txt");Git("checkout","--","source.txt");
            }
            foreach(var raw in new[] {"{",JsonSerializer.Serialize(descriptor).Replace("\"SchemaVersion\":1","\"SchemaVersion\":2"),
                JsonSerializer.Serialize(descriptor).Replace("\"SchemaVersion\":1","\"SchemaVersion\":1,\"SchemaVersion\":1"),
                JsonSerializer.Serialize(descriptor).Replace("{","{\"Unknown\":1,"),
                "{}","null",new string(' ',32769)}) {
                File.WriteAllText(config,raw);Reject("malformed or oversized workspace unavailable");
            }
            foreach(var invalid in new[] {
                descriptor with{ProjectId=null!},descriptor with{ChangeId=null!},
                descriptor with{StorageDirectory=null!},descriptor with{RepositoryDirectory=null!},
                descriptor with{ArtifactPath=null!} }) {
                Save(invalid);Reject("null workspace binding or path refused");
            }
            var link=Path.Combine(root,"repository-link");
            var junction=new ProcessStartInfo("cmd.exe"){UseShellExecute=false,CreateNoWindow=true,
                RedirectStandardOutput=true,RedirectStandardError=true};
            foreach(var arg in new[]{"/c","mklink","/J",link,repo})junction.ArgumentList.Add(arg);
            using(var child=Process.Start(junction)!) {
                var output=child.StandardOutput.ReadToEnd();var error=child.StandardError.ReadToEnd();
                if(!child.WaitForExit(10000)||child.ExitCode!=0)throw new Exception("Fixture junction failed:"+error+output);
            }
            try { Save(descriptor with{RepositoryDirectory=link});Reject("workspace reparse repository refused"); }
            finally { Directory.Delete(link); }
            Save(descriptor with { ArtifactPath="relative.txt" });Reject("relative workspace artifact refused");
            Save(descriptor with { StorageDirectory=@"\\server\share" });Reject("network workspace storage refused");
            Save(descriptor);
            File.WriteAllText(artifact,"changed artifact");
            check(inspector.Read(config).Session.State=="INVALIDATED","workspace artifact drift invalidates bound session");
            File.WriteAllText(artifact,"fixture");session=Create();descriptor=descriptor with{SessionId=session.Id};Save(descriptor);
            File.WriteAllText(Path.Combine(repo,"source.txt"),"second");Git("add",".");Git("commit","-qm","second");
            check(inspector.Read(config).Session.State=="INVALIDATED","workspace committed source drift invalidates bound session");
            File.Delete(artifact);Reject("missing workspace artifact unavailable");
        }
        finally {
            foreach(var file in Directory.EnumerateFiles(root,"*",SearchOption.AllDirectories))
                File.SetAttributes(file,File.GetAttributes(file)&~FileAttributes.ReadOnly);
            Directory.Delete(root,true);
        }
    }
}
