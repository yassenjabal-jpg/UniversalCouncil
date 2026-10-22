using System.Diagnostics;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using UniversalCouncil.CommandCenter.Core;
using UniversalCouncil.CommandCenter.Host;

internal static class EvidenceChecks
{
    public static void Run(Action<bool,string> check)
    {
        var root = Path.Combine(Path.GetTempPath(), "murtakaz-evidence-" + Guid.NewGuid());
        var repo = Path.Combine(root, "repo");
        var artifacts = Path.Combine(root, "artifacts");
        Directory.CreateDirectory(repo);
        Directory.CreateDirectory(artifacts);
        string Git(params string[] arguments)
        {
            var start = new ProcessStartInfo("git") { WorkingDirectory = repo,
                UseShellExecute = false, RedirectStandardOutput = true, RedirectStandardError = true };
            foreach (var arg in arguments) start.ArgumentList.Add(arg);
            using var process = Process.Start(start)!;
            var output = process.StandardOutput.ReadToEnd();
            var error = process.StandardError.ReadToEnd();
            if (!process.WaitForExit(10000) || process.ExitCode != 0) throw new Exception("Fixture git failed: " + error);
            return output.Trim();
        }
        try
        {
            Git("init", "-q");
            Git("config", "user.name", "Evidence Fixture");
            Git("config", "user.email", "fixture@example.invalid");
            Git("config", "core.autocrlf", "false");
            File.WriteAllText(Path.Combine(repo, "source.txt"), "explicit test fixture");
            Git("add", ".");
            Git("commit", "-qm", "source fixture");
            var source = Git("rev-parse", "HEAD");
            var bytes = Encoding.UTF8.GetBytes("fixture evidence");
            var file = Path.Combine(artifacts, "report.txt");
            File.WriteAllBytes(file, bytes);
            var hash = Convert.ToHexString(SHA256.HashData(bytes));
            var manifest = new EvidenceManifest(1, "project", "change", source, "FIXTURE",
                [new("report.txt", hash, bytes.Length)]);
            string Commit(EvidenceManifest value, Func<string,string>? mutate = null)
            {
                var raw = JsonSerializer.Serialize(value);
                File.WriteAllText(Path.Combine(repo, "evidence.json"), mutate is null ? raw : mutate(raw));
                Git("add", "evidence.json");
                Git("commit", "--allow-empty", "-qm", "manifest fixture");
                return Git("rev-parse", "HEAD");
            }
            var committed = Commit(manifest);
            var request = new EvidenceVerificationRequest("project", "change", source, committed, "evidence.json");
            var verifier = CommandCenterComposition.CreateEvidenceVerifier(repo, artifacts, allowFixtures: true);
            var production = CommandCenterComposition.CreateEvidenceVerifier(repo, artifacts);
            var result = verifier.Verify(request);
            check(result.Status == "FIXTURE_CONTENT_MATCH" && result.ContentMatchesDeclaration,
                "committed fixture bytes match");
            check(!result.CaptureRevisionIndependentlyVerified && !result.SemanticEvidenceAccepted &&
                !result.ApprovalGranted && !result.ExecutionAuthority && !result.Stage8Opened,
                "byte verification grants no truth or authority");
            check(result.ManifestBlobId == Git("rev-parse", committed + ":evidence.json") &&
                result.ManifestSha256 == Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(Path.Combine(repo, "evidence.json")))),
                "exact committed manifest provenance");
            check(!production.Verify(request).ContentMatchesDeclaration, "fixtures refused by default");
            File.WriteAllText(Path.Combine(repo, "evidence.json"), "{dirty working manifest");
            check(verifier.Verify(request).ContentMatchesDeclaration, "working manifest cannot replace committed bytes");
            foreach (var invalid in new[] {
                request with { ProjectId = "other" }, request with { ChangeId = "other" },
                request with { SourceRevision = new string('a',40) },
                request with { ManifestRevision = "HEAD" },
                request with { ManifestRevision = new string('b',40) },
                request with { ManifestPath = "../evidence.json" },
                request with { ManifestPath = "evidence.json:ads" } })
                check(!verifier.Verify(invalid).ContentMatchesDeclaration, "unknown or mismatched request refused");
            File.WriteAllBytes(file, Encoding.UTF8.GetBytes("tampered evidence"));
            check(!verifier.Verify(request).ContentMatchesDeclaration, "tampered bytes refused");
            File.Delete(file);
            check(!verifier.Verify(request).ContentMatchesDeclaration, "missing bytes refused");
            File.WriteAllBytes(file, bytes);
            foreach (var invalid in new[] {
                manifest with { SchemaVersion = 99 }, manifest with { EvidenceKind = "UNKNOWN" },
                manifest with { SourceRevision = new string('b',40) },
                manifest with { Entries = [] },
                manifest with { Entries = [new("REPORT.txt",hash,bytes.Length),new("report.txt",hash,bytes.Length)] },
                manifest with { Entries = [new("report.txt",new string('0',64),bytes.Length)] },
                manifest with { Entries = [new("report.txt",hash,bytes.Length+1)] },
                manifest with { Entries = [new("report.txt",hash,-1)] },
                manifest with { Entries = [new("report.txt",hash,1073741825)] },
                manifest with { Entries = [new("../outside.txt",hash,bytes.Length)] },
                manifest with { Entries = [new("report.txt:stream",hash,bytes.Length)] },
                manifest with { Entries = [new("NUL.txt",hash,bytes.Length)] },
                manifest with { Entries = [new("report.txt.",hash,bytes.Length)] },
                manifest with { Entries = Enumerable.Range(0,101).Select(i=>new EvidenceEntry(i+".txt",hash,0)).ToArray() },
                manifest with { Entries = Enumerable.Range(0,5).Select(i=>new EvidenceEntry(i+".txt",hash,1073741824)).ToArray() } })
            {
                var revision = Commit(invalid);
                check(!verifier.Verify(request with { ManifestRevision = revision }).ContentMatchesDeclaration,
                    "invalid manifest refused");
            }
            foreach (var mutate in new Func<string,string>[] {
                s => "{", s => s.Insert(1, JsonSerializer.Serialize("SchemaVersion")+":1,"),
                s => s.Insert(1, JsonSerializer.Serialize("Unknown")+":true,"),
                s => s.Replace("\"Entries\":", "\"Entries\":null,\"Ignored\":"),
                s => s.Replace("\"Sha256\":", "\"Sha256\":null,\"Ignored\":") })
            {
                var revision = Commit(manifest, mutate);
                check(!verifier.Verify(request with { ManifestRevision = revision }).ContentMatchesDeclaration,
                    "malformed or unknown manifest refused");
            }
            foreach (var mutate in new Action<System.Text.Json.Nodes.JsonObject>[] {
                d => d["Entries"] = null,
                d => d.Remove("Entries"),
                d => d["Entries"]![0]!["Sha256"] = null,
                d => d["Entries"]![0]!.AsObject().Remove("Sha256") })
            {
                var revision = Commit(manifest, raw => {
                    var document = System.Text.Json.Nodes.JsonNode.Parse(raw)!.AsObject();
                    mutate(document);
                    return document.ToJsonString();
                });
                check(!verifier.Verify(request with { ManifestRevision = revision }).ContentMatchesDeclaration,
                    "direct null or missing required field refused");
            }
            var realRevision = Commit(manifest with { EvidenceKind = "REAL" });
            var realResult = production.Verify(request with { ManifestRevision = realRevision });
            check(realResult.Status == "CONTENT_MATCH" && !realResult.SemanticEvidenceAccepted,
                "synthetic REAL-kind branch verifies bytes only");
            var noncommit = Git("rev-parse", source + ":source.txt");
            check(!verifier.Verify(request with { SourceRevision = noncommit }).ContentMatchesDeclaration,
                "blob cannot stand in for source commit");
            Git("checkout", "--orphan", "unrelated");
            Git("rm", "-rf", ".");
            var unrelated = Commit(manifest);
            check(!verifier.Verify(request with { ManifestRevision = unrelated }).ContentMatchesDeclaration,
                "nonancestor source refused");
            Git("checkout", "--detach", committed);
            var target = Path.Combine(root, "outside-directory");
            Directory.CreateDirectory(target);
            File.WriteAllBytes(Path.Combine(target, "report.txt"), bytes);
            var junction = Path.Combine(artifacts, "escape");
            var junctionStart = new ProcessStartInfo("cmd.exe") {
                UseShellExecute = false, CreateNoWindow = true,
                RedirectStandardOutput = true, RedirectStandardError = true,
                ArgumentList = { "/d", "/c", "mklink", "/J", junction, target }
            };
            using (var process = Process.Start(junctionStart)!)
            {
                process.StandardOutput.ReadToEnd();
                process.StandardError.ReadToEnd();
                if (!process.WaitForExit(10000) || process.ExitCode != 0)
                    throw new Exception("Junction fixture creation failed");
            }
            var junctionRevision = Commit(manifest with { Entries = [new("escape/report.txt", hash, bytes.Length)] });
            var reparse = verifier.Verify(request with { ManifestRevision = junctionRevision });
            check(!reparse.ContentMatchesDeclaration && reparse.Errors.Contains("ARTIFACT_REPARSE_PATH"),
                "directory reparse escape refused at content boundary");
            var rootReparse = CommandCenterComposition.CreateEvidenceVerifier(repo, junction, true).Verify(request);
            check(!rootReparse.ContentMatchesDeclaration && rootReparse.Errors.Contains("ARTIFACT_REPARSE_PATH"),
                "reparse artifact root refused");
            Directory.Delete(junction);

        }
        finally
        {
            var allowedPrefix = Path.Combine(Path.GetTempPath(), "murtakaz-evidence-");
            if (!Path.GetFullPath(root).StartsWith(allowedPrefix, StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("Unsafe fixture cleanup target");
            if (Directory.Exists(root))
            {
                var options = new EnumerationOptions { RecurseSubdirectories = true,
                    AttributesToSkip = FileAttributes.ReparsePoint };
                foreach (var entry in Directory.EnumerateFileSystemEntries(root, "*", options))
                {
                    var attributes = File.GetAttributes(entry);
                    if ((attributes & FileAttributes.ReadOnly) != 0)
                        File.SetAttributes(entry, attributes & ~FileAttributes.ReadOnly);
                }
                Directory.Delete(root, true);
            }
        }
        check(!Directory.Exists(root), "temporary Git fixture cleanup completed");
    }
}
