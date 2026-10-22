using UniversalCouncil.CommandCenter.Application;
using UniversalCouncil.CommandCenter.Core;
using UniversalCouncil.CommandCenter.Infrastructure;

internal sealed class ReviewTestClock : TimeProvider
{
    public DateTimeOffset Now = new(2026, 10, 22, 12, 0, 0, TimeSpan.Zero);
    public override DateTimeOffset GetUtcNow() => Now;
}
internal sealed class DriftPlanner(ILocalReviewPlanner inner) : ILocalReviewPlanner
{
    public LocalReviewPlan Plan(LocalReviewRequest request) =>
        inner.Plan(request) with { PolicyFingerprint = "changed" };
}
internal static class SessionChecks
{
    // Validation fixture: callers must provide an isolated directory; no production path is selected.
    public static int Probe(ILocalReviewPlanner planner, string operation, string directory)
    {
        var service = new LocalReviewSessionService(planner, new JsonLocalReviewSessionStore(directory));
        var revision = new string('a', 40);
        var hash = new string('b', 64);
        var idPath = Path.Combine(directory, "probe-id.txt");
        if (operation == "write")
        {
            var request = new LocalReviewRequest("process-fixture", "universal-council-command-center",
                revision, "material_product_change", ["architecture_boundary"], [], []);
            var session = service.Create(request, hash, TimeSpan.FromHours(1));
            service.Record(session.Id, 0, revision, hash, session.Plan.Assignments[0].RoleId,
                "fixture-process", "BLOCKED", "unverified fixture report", []);
            File.WriteAllText(idPath, session.Id.ToString("D"));
            return 0;
        }
        if (operation != "read") throw new InvalidDataException("Unknown validation probe");
        var saved = service.Read(Guid.Parse(File.ReadAllText(idPath)), revision, hash);
        return saved.State == "BLOCKED" && saved.Results.Length == 1 &&
            saved.Results[0].Actor == "fixture-process" && !saved.ApprovalGranted ? 0 : 1;
    }
    public static void Run(ILocalReviewPlanner planner, Action<bool,string> check)
    {
        var root = Path.Combine(Path.GetTempPath(), "murtakaz-session-" + Guid.NewGuid());
        try
        {
            var probeDirectory = Path.Combine(root, "process-probe");
            foreach (var operation in new[] { "write", "read" })
            {
                var start = new System.Diagnostics.ProcessStartInfo("dotnet") {
                    UseShellExecute = false,
                    ArgumentList = { typeof(SessionChecks).Assembly.Location,
                        "--session-probe", operation, probeDirectory }
                };
                using var child = System.Diagnostics.Process.Start(start)
                    ?? throw new InvalidOperationException("Probe process unavailable");
                if (!child.WaitForExit(30000))
                {
                    child.Kill(true);
                    child.WaitForExit();
                    throw new TimeoutException("Probe process timeout");
                }
                check(child.ExitCode == 0, "separate process durable " + operation);
            }
            var clock = new ReviewTestClock();
            LocalReviewSessionService Service() => new(planner, new JsonLocalReviewSessionStore(root), clock);
            var service = Service();
            var request = new LocalReviewRequest("session-test", "universal-council-command-center",
                new string('a', 40), "material_product_change", ["architecture_boundary"], [], []);
            var hash = new string('b', 64);
            var session = service.Create(request, hash, TimeSpan.FromHours(1));
            void Reject(Action action, string name)
            {
                try { action(); throw new Exception("Expected refusal: " + name); }
                catch (InvalidDataException) { check(true, name); }
                catch (IOException) { check(true, name); }
                catch (UnauthorizedAccessException) { check(true, name); }
            }
            check(Service().Read(session.Id, request.SourceRevision, hash).State == "REVIEWING", "session survives restart");
            request.Routes[0] = "unknown";
            check(Service().Read(session.Id, session.Plan.SourceRevision, hash).Request.Routes[0] == "architecture_boundary",
                "caller request mutation cannot alter durable plan");
            Reject(() => service.Record(session.Id, 0, session.Plan.SourceRevision, hash, "unknown", "actor", "ACCEPTED_REPORT", "report", []), "unassigned role refused");
            Reject(() => service.Record(session.Id, 0, session.Plan.SourceRevision, hash, session.Plan.Assignments[0].RoleId, "actor", "APPROVED", "report", []), "approval outcome refused");
            var role = session.Plan.Assignments[0].RoleId;
            var first = service.Record(session.Id, 0, session.Plan.SourceRevision, hash, role, "caller", "BLOCKED", "unverified blocker", ["evidence-not-verified"]);
            check(first.State == "BLOCKED" && first.Results[0].Provenance == "CALLER_REPORTED_UNVERIFIED", "blocker and honest attribution persisted");
            Reject(() => Service().Record(session.Id, 0, session.Plan.SourceRevision, hash, session.Plan.Assignments[1].RoleId, "actor", "ACCEPTED_REPORT", "report", []), "stale version refused");
            Reject(() => service.Record(session.Id, first.Version, session.Plan.SourceRevision, hash, role, "actor", "ACCEPTED_REPORT", "overwrite dissent", []), "duplicate role cannot erase dissent");
            var negative = first;
            foreach (var assignment in session.Plan.Assignments.Skip(1))
                negative = service.Record(session.Id, negative.Version, session.Plan.SourceRevision, hash,
                    assignment.RoleId, "caller", "ACCEPTED_REPORT", "report", []);
            check(negative.State == "BLOCKED", "all positive summaries cannot erase blocker");
            var inspector = new LocalSupervisionReader(service);
            var overview = inspector.Read(negative.Id, negative.Plan.SourceRevision, hash);
            check(overview.State == "BLOCKED" && overview.PendingRoleIds.Count == 0,
                "supervision preserves blocker after all reports");
            check(overview.Reports.Count == negative.Results.Length &&
                overview.Reports[0].Actor == "caller" && overview.Reports[0].Rationale == "unverified blocker" &&
                overview.Reports[0].EvidenceRefs.SequenceEqual(new[] { "evidence-not-verified" }),
                "supervision retains attributed dissent and references");
            check(!overview.EvidenceVerified && !overview.ApprovalGranted && !overview.ExecutionAuthority &&
                !overview.LiveExecution && !overview.Stage8Opened, "supervision grants no authority");
            try
            {
                ((IList<string>)overview.Reports[0].EvidenceRefs)[0] = "mutated";
                throw new Exception("Expected immutable evidence refs");
            }
            catch (NotSupportedException) { check(true, "supervision evidence references immutable"); }
            try
            {
                ((IList<ReviewerReportView>)overview.Reports).Clear();
                throw new Exception("Expected immutable reports");
            }
            catch (NotSupportedException) { check(true, "supervision report collection immutable"); }
            var pendingSession = service.Create(session.Request, hash, TimeSpan.FromHours(1));
            clock.Now += TimeSpan.FromSeconds(1);
            var pendingView = inspector.Read(pendingSession.Id, pendingSession.Plan.SourceRevision, hash);
            check(pendingView.PendingRoleIds.Count == pendingSession.Plan.Assignments.Length &&
                pendingView.Reports.Count == 0 && pendingView.Version > pendingSession.Version,
                "supervision returns pending roles and persisted observation version");
            check(pendingView.Version == service.Read(pendingSession.Id, pendingSession.Plan.SourceRevision, hash).Version,
                "supervision observation version matches durable record");
            void CliUnavailable(string revision)
            {
                var start = new System.Diagnostics.ProcessStartInfo("dotnet") {
                    UseShellExecute = false, RedirectStandardError = true,
                    ArgumentList = { typeof(SessionChecks).Assembly.Location, "--inspect-session",
                        root, pendingSession.Id.ToString(), revision, hash } };
                using var child = System.Diagnostics.Process.Start(start)!;
                var error = child.StandardError.ReadToEnd();
                if (!child.WaitForExit(10000)) { child.Kill(true); child.WaitForExit(); throw new TimeoutException(); }
                check(child.ExitCode == 1 && error.Trim() == "SESSION_UNAVAILABLE",
                    "inspection CLI fails closed with explicit unavailable result");
            }
            CliUnavailable("unknown");
            var inspectionFile = Path.Combine(root, pendingSession.Id.ToString("N") + ".json");
            var inspectionOriginal = File.ReadAllText(inspectionFile);
            File.WriteAllText(inspectionFile, "{");
            CliUnavailable(pendingSession.Plan.SourceRevision);
            File.WriteAllText(inspectionFile, inspectionOriginal);
            var invalidView = inspector.Read(pendingSession.Id, new string('c',40), hash);
            check(invalidView.State == "INVALIDATED", "supervision rechecks current binding");
            Reject(() => inspector.Read(Guid.NewGuid(), session.Plan.SourceRevision, hash),
                "supervision missing session unavailable");
            Reject(() => inspector.Read(session.Id, "unknown", hash),
                "supervision unknown freshness unavailable");

            var priority = service.Create(session.Request, hash, TimeSpan.FromHours(1));
            var outcomes = new[] { "OWNER_DECISION_REQUIRED", "RETURNED_FOR_CHANGES", "BLOCKED" };
            for (var i = 0; i < outcomes.Length; i++)
            {
                priority = service.Record(priority.Id, priority.Version, priority.Plan.SourceRevision, hash,
                    priority.Plan.Assignments[i].RoleId, "caller", outcomes[i], "reported", []);
                check(priority.State == outcomes[i], "state precedence " + outcomes[i]);
            }
            var positive = service.Create(session.Request, hash, TimeSpan.FromDays(7));
            foreach (var assignment in positive.Plan.Assignments)
                positive = service.Record(positive.Id, positive.Version, positive.Plan.SourceRevision, hash,
                    assignment.RoleId, "caller", "ACCEPTED_REPORT", "reported only", []);
            check(positive.State == "RESULTS_RECORDED" && !positive.ApprovalGranted &&
                !positive.ExecutionAuthority && !positive.EvidenceVerified && !positive.Stage8Opened,
                "complete reports grant no authority or evidence verification");
            Reject(() => service.Create(session.Request, hash, TimeSpan.FromDays(8)), "seven day cap");
            Reject(() => service.Create(session.Request, "unknown", TimeSpan.FromHours(1)), "invalid artifact refused");
            Reject(() => service.Read(session.Id, "unknown", hash), "unknown current revision refused");
            var drift = service.Read(positive.Id, new string('c',40), hash);
            check(drift.State == "INVALIDATED", "revision drift invalidates");
            check(service.Read(positive.Id, positive.Plan.SourceRevision, hash).State == "INVALIDATED", "invalidation cannot revert");
            var artifact = service.Create(session.Request, hash, TimeSpan.FromHours(1));
            check(service.Read(artifact.Id, artifact.Plan.SourceRevision, new string('c',64)).State == "INVALIDATED", "artifact drift invalidates");
            var expiry = service.Create(session.Request, hash, TimeSpan.FromHours(1));
            clock.Now += TimeSpan.FromHours(1);
            check(service.Read(expiry.Id, expiry.Plan.SourceRevision, hash).State == "EXPIRED", "exact expiry boundary");
            clock.Now -= TimeSpan.FromMinutes(1);
            check(service.Read(expiry.Id, expiry.Plan.SourceRevision, hash).State == "EXPIRED", "expiry remains terminal");
            var rollback = service.Create(session.Request, hash, TimeSpan.FromHours(1));
            clock.Now -= TimeSpan.FromMinutes(1);
            check(service.Read(rollback.Id, rollback.Plan.SourceRevision, hash).TerminalReason == "CLOCK_ROLLBACK", "clock rollback invalidates");
            var concurrent = service.Create(session.Request, hash, TimeSpan.FromHours(1));
            var successes = 0;
            Parallel.For(0, 2, index => {
                try {
                    Service().Record(concurrent.Id, 0, concurrent.Plan.SourceRevision, hash,
                        concurrent.Plan.Assignments[index].RoleId, "caller", "ACCEPTED_REPORT", "report", []);
                    Interlocked.Increment(ref successes);
                } catch (IOException) { }
            });
            check(successes == 1 && Service().Read(concurrent.Id, concurrent.Plan.SourceRevision, hash).Results.Length == 1,
                "concurrent writers cannot lose results");
            var remaining = Service().Read(concurrent.Id, concurrent.Plan.SourceRevision, hash);
            var unreported = remaining.Plan.Assignments.First(a => !remaining.Results.Any(v => v.RoleId == a.RoleId)).RoleId;
            var file = Path.Combine(root, concurrent.Id.ToString("N") + ".json");
            var original = File.ReadAllText(file);
            File.WriteAllText(file, "{");
            Reject(() => Service().Read(concurrent.Id, concurrent.Plan.SourceRevision, hash), "truncated record refused");
            File.WriteAllText(file, original.Insert(1, System.Text.Json.JsonSerializer.Serialize("SchemaVersion") + ":1,"));
            Reject(() => Service().Read(concurrent.Id, concurrent.Plan.SourceRevision, hash), "duplicate persisted property refused");
            File.WriteAllText(file, original.Replace("caller", "tamper"));
            Reject(() => Service().Read(concurrent.Id, concurrent.Plan.SourceRevision, hash), "corruption digest refused");
            File.WriteAllText(file, original);
            void RewritePayload(Action<System.Text.Json.Nodes.JsonObject> mutate)
            {
                var envelope = System.Text.Json.Nodes.JsonNode.Parse(original)!.AsObject();
                var payload = System.Text.Json.Nodes.JsonNode.Parse(envelope["Payload"]!.GetValue<string>())!.AsObject();
                mutate(payload);
                var raw = payload.ToJsonString();
                envelope["Payload"] = raw;
                envelope["Sha256"] = Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(
                    System.Text.Encoding.UTF8.GetBytes(raw)));
                File.WriteAllText(file, envelope.ToJsonString());
            }
            RewritePayload(payload => payload["SchemaVersion"] = 99);
            Reject(() => Service().Read(concurrent.Id, concurrent.Plan.SourceRevision, hash), "unsupported persisted schema refused");
            RewritePayload(payload => payload.Remove("Version"));
            Reject(() => Service().Read(concurrent.Id, concurrent.Plan.SourceRevision, hash), "missing required persisted field refused");
            RewritePayload(payload => payload["Plan"]!["Mode"] = "LIGHT");
            check(Service().Read(concurrent.Id, concurrent.Plan.SourceRevision, hash).State == "INVALIDATED",
                "recomputed digest cannot hide inconsistent planned reviewers");
            File.WriteAllText(file, original);
            Reject(() => new JsonLocalReviewSessionStore(root).Create(concurrent), "create cannot overwrite existing session");
            using (var held = new FileStream(file, FileMode.Open, FileAccess.Read, FileShare.Read))
                Reject(() => Service().Record(concurrent.Id, 1, concurrent.Plan.SourceRevision, hash,
                    unreported, "caller", "ACCEPTED_REPORT", "report", []),
                    "failed replacement refused");
            check(File.ReadAllText(file) == original, "failed replacement preserves preceding record");
            var store = new JsonLocalReviewSessionStore(root);
            Reject(() => store.Transact(concurrent.Id, 1, s => s with {
                Version = 2, Results = [] }), "store cannot erase recorded dissent");
            Reject(() => store.Transact(concurrent.Id, 1, s => s with {
                Version = 2, ArtifactSha256 = new string('c',64) }), "store cannot mutate binding");
            Reject(() => store.Transact(concurrent.Id, 1, s => {
                s.Request.Routes[0] = "unknown";
                return s with { Version = 2 };
            }), "in-place request mutation refused");
            Reject(() => store.Transact(concurrent.Id, 1, s => {
                s.Plan.Assignments[0].Reasons[0] = "tampered";
                return s with { Version = 2 };
            }), "in-place plan mutation refused");
            var policyDirectory = Path.Combine(root, "policy");
            Directory.CreateDirectory(policyDirectory);
            foreach (var name in new[] { "project-council.json", "product-studio.json" })
                File.Copy(Path.Combine(AppContext.BaseDirectory, "state", "project-governance", name),
                    Path.Combine(policyDirectory, name));
            var realPlanner = new LocalReviewPlanner(new JsonLocalReviewPolicyReader(policyDirectory));
            var realService = new LocalReviewSessionService(realPlanner, new JsonLocalReviewSessionStore(root), clock);
            var realSession = realService.Create(session.Request, hash, TimeSpan.FromHours(1));
            File.AppendAllText(Path.Combine(policyDirectory, "project-council.json"), " ");
            check(realService.Read(realSession.Id, realSession.Plan.SourceRevision, hash).State == "INVALIDATED",
                "actual profile byte drift invalidates after restart");
            var policySession = service.Create(session.Request, hash, TimeSpan.FromHours(1));
            var changedPolicy = new LocalReviewSessionService(new DriftPlanner(planner),
                new JsonLocalReviewSessionStore(root), clock);
            check(changedPolicy.Read(policySession.Id, policySession.Plan.SourceRevision, hash).State == "INVALIDATED",
                "fresh policy drift invalidates");
            foreach (var outcome in new[] { "RETURNED_FOR_CHANGES", "OWNER_DECISION_REQUIRED" })
            {
                var item = service.Create(session.Request, hash, TimeSpan.FromHours(1));
                item = service.Record(item.Id, 0, item.Plan.SourceRevision, hash,
                    item.Plan.Assignments[0].RoleId, "caller", outcome, "reported", []);
                check(item.State == outcome, "negative outcome " + outcome);
            }
            check(Directory.GetFiles(root, "*.tmp").Length == 0, "failed write temp cleaned");
        }
        finally { if (Directory.Exists(root)) Directory.Delete(root, true); }
    }
}
