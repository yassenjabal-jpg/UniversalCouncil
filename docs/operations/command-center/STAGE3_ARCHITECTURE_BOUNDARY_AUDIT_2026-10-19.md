# UniversalCouncil Command Center — Stage 3 Architecture Boundary Audit
Date: 2026-10-19
Status: PASS
Method: Architecture Boundary Audit / delta review
Baseline SHA: `448c5b7ce8bff6b9ec3875106922528036695b6c`
Candidate SHA: `2073b0ff5800156e6d908efc43493715c83f22bc`

## Scope

Audit only the boundaries changed by Stage 3.

Baseline:
Stage 2 read-only operational state.

Candidate:
Stage 3 Council + Studio planning/orchestration.

Compare result:
- status: ahead;
- 28 commits ahead;
- 0 behind;
- 21 changed files.

No live LAN/server operation was required.

## Preferred boundary

`App bootstrap -> View -> ViewModel -> Host -> Application -> Infrastructure -> repository projection`

For Stage 3:
- App owns composition/bootstrap.
- View renders only.
- ViewModel exposes read-only projections.
- Host composes services.
- Application owns orchestration validation/routing.
- Infrastructure owns JSON/file access.
- Core owns contracts/projections.

## Findings

### AB-03-01 — MainWindow composition ownership
Initial candidate:
`MainWindow` called `CommandCenterComposition.Create` directly.

Risk:
The View would become a composition root and could accumulate provider, credentials, filesystem or execution wiring in later stages.

Status:
CONFIRMED NEW COUPLING — RESOLVED BEFORE LOCK.

Smallest safe extraction:
Move composition to `App`.

Final evidence:
- `App.xaml` no longer uses StartupUri.
- `App.xaml.cs` owns `CommandCenterComposition.Create(baseDirectory)`.
- `MainWindow.xaml.cs` receives only `MainWindowViewModel`.
- UiSmoke uses the same App composition entrypoint.

Migration path:
Stage 4 provider/execution composition must extend Host/bootstrap, not MainWindow.

### AB-03-02 — Presentation to filesystem
Candidate search:
System.IO, File.Read, Process.Start, Process, HttpClient, PowerShell, cmd, MCP, credential/provider identifiers.

Final status:
DISPROVED / NO NEW MATERIAL VIOLATION.

Evidence:
Stage 3 static architecture gate passes and WPF project references remain exactly:
- CommandCenter.Core
- CommandCenter.Host

Filesystem JSON access remains in Infrastructure.

### AB-03-03 — Application to WPF
Final status:
DISPROVED.

Evidence:
OrchestrationService is in Application and has no WPF dependency.
It accepts repository-projected contracts and returns planning projections/results.

### AB-03-04 — Hidden provider/model dependency
Final status:
DISPROVED.

Evidence:
- provider calls are declared disconnected;
- planner returns `OWNER_SELECTION_REQUIRED / PROVIDER NOT CONNECTED`;
- model selection policy is data/contract only;
- Presentation validator forbids direct provider identifiers and network clients.

### AB-03-05 — Mutable global state
Final status:
DISPROVED.

No newly introduced mutable static runtime state was found.
Static dictionaries in OrchestrationService are immutable ranking tables used for deterministic planning.

### AB-03-06 — Repository truth duplication
Initial risk:
Council/Studio definitions could drift if copied by hand into the product.

Mitigation:
Stage 3 uses `build_command_center_stage3_projection.py` to generate `orchestration-catalog.json` from governing repository files.

The exact-head CI regenerates the projection and runs `git diff --exit-code`.

Source files are pinned by Git blob SHA.

### AB-03-07 — Cross-platform source digest
Initial candidate used working-tree bytes, causing CRLF-dependent Git-blob drift on Windows.

Status:
CONFIRMED EVIDENCE-TOOL DEFECT — RESOLVED.

Fix:
Source digests now use:
`git rev-parse HEAD:<path>`

This makes evidence independent of checkout line-ending normalization.

## Affected verification

Exact-head workflow:
- `Command Center Stage 3`
- run #14
- run ID `39216663102`
- conclusion `SUCCESS`

Relevant passing steps:
- exact candidate SHA;
- canonical projection regeneration;
- Stage 3 architecture/truth boundary;
- WPF build;
- Stage 2 fail-closed regression validation;
- Stage 3 adversarial validation;
- exact UI evidence render;
- published read-model assertion.

CodeQL:
- run #500
- run ID `39216663046`
- conclusion `SUCCESS`

## Architecture debt / follow-up

Not a Stage 3 blocker:
- App references Host as the explicit bootstrap/composition root.
- No DI framework is required merely for style.
- Stage 4 should introduce execution/provider interfaces below Host/Application rather than adding provider logic to WPF.
- Any background service or long-running provider introduced later must have explicit lifetime/cancellation ownership.

## Verdict

`PASS_STAGE3_ARCHITECTURE_BOUNDARY`

No unresolved newly introduced material boundary violation remains at candidate SHA:
`2073b0ff5800156e6d908efc43493715c83f22bc`
