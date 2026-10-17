# RevenueSystem 2.0 — Work Environment Audit
Date: 2026-10-17
Status: COUNCIL REVIEW COMPLETE — RECOMMENDATIONS ONLY
RevenueSystem baseline: `6886fbb6398b67b366faf3ca446dbae54eb1ce4f`
UniversalCouncil rebuild branch head at review start: `c3e769df3dbf0773cfad093db13cb54e1ad6fce9`

## Executive verdict

The environment is already strong enough to start the rebuild.

The next quality jump does **not** require buying another UI framework or replacing WPF.

The biggest gains now come from:
1. reproducible toolchain pinning;
2. fail-closed isolated runtime;
3. disk/cache discipline;
4. performance instrumentation;
5. GUI automation hardening;
6. CI decomposition and artifact retention;
7. automated environment inventory;
8. design-system implementation discipline.

Council rating:
- hardware: GOOD, with RAM/disk headroom limits;
- IDE/toolchain: STRONG;
- CI: STRONG but monolithic;
- test coverage mechanism: STRONG legacy gate, weak structured reporting;
- environment reproducibility: MEDIUM;
- GUI automation safety: MEDIUM until bridge v2;
- performance observability: WEAK/MEDIUM;
- visual craft tooling: STRONG;
- source/worktree discipline: GOOD but needs cleanup/registry.

---

# 1. Verified YASSIN baseline

## Hardware

- CPU: Intel Core i5-12400F
- cores/threads: 6 / 12
- RAM: 16 GB DDR4-3200
- physical modules: 2 × 8 GB
- GPU: NVIDIA RTX 4060 Ti
- active display: 1920×1080 @ 143 Hz
- current UI DPI: 96 / 100%

## Disk

- C: ~20.3 GB free
- D: ~148.9 GB free
- E: ~84.4 GB free

Important cache/temp use on C:
- user Temp: ~15.9 GB
- NuGet packages: ~1.55 GB
- local NuGet cache: ~0.43 GB
- Visual Studio local data: ~1.17 GB
- RevenueSystem-related repo worktrees: roughly ~1.2 GB total

Finding:
**C is currently the environment's biggest operational resource risk.**

## Power

Active scheme:
**Power saver**

Finding:
This is inappropriate for sustained local build/profiling/render sessions on a desktop development workstation.

## Development toolchain

- Visual Studio Community 2026: 18.10.3
- Blend: installed
- MSBuild: 18.10
- Windows SDK: 10.0.26100.0
- .NET SDK: 10.0.401 + 10.0.402
- active SDK: 10.0.402
- .NET Windows Desktop runtime: 10.0.13 available
- Managed Desktop Visual Studio workload: present
- Git: 2.55.0
- Python: 3.13.3
- Node: 24.21.0
- FFmpeg/ffprobe: 9.0.2
- long Windows paths: enabled

No .NET workload packs are installed through `dotnet workload`, but this is **not a current WPF blocker** because the Visual Studio Managed Desktop workload and Windows Desktop runtime are present.

---

# 2. Design / creative tooling

Physically present on YASSIN under Adobe 2025:
- Photoshop 2025
- Illustrator 2025
- After Effects 2025
- Premiere Pro 2025
- Audition 2025
- Media Encoder 2025
- Bridge 2025
- other Adobe tools

Finding:
The Council's media capability registry contains stale version/status claims for some Adobe applications.

Recommendation:
Do not maintain tool availability manually.

Create an automated:
`TOOLCHAIN_SNAPSHOT.json`

It should record:
- executable path;
- file/product version;
- last verified date;
- runtime smoke state;
- capability status.

This snapshot becomes evidence; config files consume it rather than inventing availability.

---

# 3. Visual Studio reproducibility

Current gap:
No repository `global.json` was found.

Impact:
- local CLI may silently use a newer SDK feature band;
- GitHub CI currently requests `10.0.x`;
- local and CI builds can drift even when source is identical.

## Recommendation ENV-P0-01

Add repository-level `global.json`.

Preferred policy:
- pin current validated SDK feature band;
- permit only patch roll-forward inside that band;
- no previews.

Candidate baseline:
`10.0.402`

Do not change SDK feature band during a rebuild slice without a dedicated toolchain update packet.

---

# 4. Visual Studio installation reproducibility

Current gap:
No `.vsconfig` was found.

## Recommendation ENV-P0-02

Export the validated Visual Studio Community 2026 installation configuration into:
`.vsconfig`

Use it to record:
- Managed Desktop workload;
- relevant Windows SDK;
- test/profiling components actually needed;
- extensions that are truly required.

Benefit:
A replacement machine can reproduce the build environment instead of rebuilding it from memory.

Do not include unnecessary workloads.

---

# 5. Package restore / dependency determinism

Current state:
- package versions are declared per project;
- no `Directory.Packages.props`;
- no lock files found;
- no known vulnerable NuGet packages were reported in a fresh local audit on 2026-10-17.

Fresh audit result:
**0 known vulnerable packages** across Product / Validation / Integration / UI test projects.

However updates exist:
- EF Core direct refs 10.0.12 → 10.0.13 available;
- PDFsharp 6.2.4 → 6.5.0 available;
- numerous transitive packages have newer releases.

## Recommendation ENV-P1-01

Introduce Central Package Management only after the first baseline build/runtime metrics are captured.

Add:
`Directory.Packages.props`

Goals:
- one version source;
- easier dependency review;
- no silent project-to-project drift.

## Recommendation ENV-P1-02

Add NuGet lock files and CI locked restore.

Suggested model:
- generate and commit `packages.lock.json`;
- use locked restore in CI;
- dependency update PR deliberately regenerates locks.

Do not bulk-upgrade all transitive packages simply because newer versions exist.

## Recommendation ENV-P1-03

Patch-align the Microsoft 10.0.x stack in one focused dependency packet.

Candidate first update:
EF Core 10.0.12 → 10.0.13.

PDFsharp 6.5.0 should be evaluated separately because reporting output is business-critical and must pass golden report fixtures.

---

# 6. Repository-wide build policy

Current gaps:
- no `.editorconfig` found;
- no root `Directory.Build.props` found.

## Recommendation ENV-P1-04

Create `.editorconfig` covering:
- C# formatting;
- XAML-neutral text rules where practical;
- naming;
- nullable expectations;
- accidental trailing whitespace;
- encoding/newline consistency.

## Recommendation ENV-P1-05

Create `Directory.Build.props` for safe shared build policy.

Candidate settings:
- deterministic builds;
- nullable consistency;
- analyzer policy;
- CI build flag;
- repository-wide NuGet audit policy;
- documentation/build metadata where useful.

Warnings-as-errors should use a **ratchet**:
1. establish current warning baseline;
2. prevent new warnings;
3. reduce legacy warnings gradually.

Do not turn every existing warning into an immediate blocker without baseline review.

---

# 7. CI review

Latest main CI:
- source SHA: current main
- conclusion: PASS
- total job duration: about 4m26s

Observed main steps:
- .NET setup: ~36 s
- restore: ~23 s
- build: ~54 s
- release gate: ~67 s
- other validation/tooling: remainder

Strength:
The Stage10 Release Gate already includes:
- Validation;
- Integration;
- isolated authenticated UI tests;
- static validators;
- SQLite simulations;
- durable/source-sync checks.

This is much stronger than the workflow name alone suggests.

## Problems

### 7.1 Monolithic feedback

Most evidence is hidden inside one long job.

A failure late in the release gate gives slower and less localized feedback.

### 7.2 Duplicate validation

The GitHub workflow runs several validators/simulations before calling the release gate, while the release gate runs a larger overlapping set again.

### 7.3 UI evidence is deleted

The release gate creates a temporary UI artifact folder and deletes it in `finally`.

That is appropriate locally when tests pass, but harmful in CI when a UI test fails because screenshots/logs can disappear before upload.

### 7.4 Runner drift

CI uses `windows-latest`.

That label can move over time.

### 7.5 Action supply-chain pinning

Actions use moving major tags such as:
- `actions/checkout@v4`
- `actions/setup-dotnet@v4`
- `actions/setup-python@v5`

Permissions are already minimal (`contents: read`), which is good.

## Recommendation ENV-P0-03

Pin the Windows runner to the explicit validated image family:
`windows-2025-vs2026`
after one test PR proves parity.

## Recommendation ENV-P0-04

Add a release-gate switch:
`-KeepUiArtifacts`
or an explicit `-UiOutput <path>`.

CI should upload on `always()`:
- UI screenshots;
- app logs;
- crash/dump metadata when applicable;
- test summary.

## Recommendation ENV-P1-06

Split CI into dependency-aware jobs:

1. `build`
2. `static-validation`
3. `integration-isolated`
4. `ui-smoke-isolated`
5. `release-gate`
6. `publish-artifact`

Reuse the same built artifact instead of rebuilding.

## Recommendation ENV-P1-07

Pin GitHub Actions to reviewed full commit SHAs.

Use Dependabot or a scheduled maintenance packet to update those pins.

## Cleanup

Remove the stray one-byte/empty workflow file:
`.github/workflows/RevenueSystem Windows CI`

Update CI documentation:
current YAML artifact retention is 3 days while documentation still states 14 days.

---

# 8. GitHub governance

Repository rulesets are not available with the current private-repository plan.

Therefore do not design the governance assuming GitHub can enforce required checks.

## Recommendation ENV-P0-05

Use repository-native soft enforcement:
- PR template with gate checklist;
- explicit `RRS_GATE_RESULT.json` artifact;
- release gate command as mandatory Council policy;
- no direct merge without CI pass recorded in handoff.

If stronger server-side branch protection becomes valuable later, evaluate plan upgrade then.

Do not upgrade merely for this rebuild unless the enforcement benefit becomes necessary.

---

# 9. Worktree discipline

Current local worktrees include:
- primary RevenueSystem clone on a non-main governance branch;
- council epistemic worktree;
- detached review worktree at the canonical main SHA;
- skill-pack worktree.

Good:
The project already uses worktrees instead of mixing unrelated changes.

Gap:
The review worktree contains multiple untracked audit scripts.

## Recommendation ENV-P0-06

Never use the canonical source review worktree as scratch storage.

Move analysis scripts to:
`CouncilVideoStudio/analysis/revenuesystem/`
or a dedicated tools branch.

Before every source lock:
`git status --porcelain`
must be empty.

## Recommendation ENV-P0-07

Create a worktree registry artifact:
`RRS_WORKTREE_REGISTRY.json`

Fields:
- path;
- branch;
- SHA;
- purpose;
- owner;
- isolated profile root;
- disposable/retain status.

This reduces branch/path confusion during a long rebuild.

---

# 10. Disk / cache strategy

Current C free space:
~20.3 GB

Current Temp:
~15.9 GB

This is an immediate operational issue.

## Recommendation ENV-P0-08

Perform a safe Temp cleanup before RRS-P0.

Rules:
- delete only stale/unlocked user-temp content;
- do not use aggressive registry/cleaner utilities;
- record before/after free space.

Target:
at least 35–40 GB free on C before sustained VS/Blend/Adobe sessions.

## Recommendation ENV-P0-09

Place the RevenueSystem 2.0 implementation worktree on D:.

Candidate:
`D:\RevenueSystem2\worktrees\...`

D currently has the largest free capacity.

## Recommendation ENV-P0-10

Use development-session-local cache redirection rather than changing all Windows paths globally.

Candidate session variables:
- `NUGET_PACKAGES=D:\DevCache\NuGet\packages`
- optional NuGet HTTP/cache paths on D
- test artifacts on D

Do not globally relocate Windows TEMP solely for RevenueSystem unless later evidence justifies it.

---

# 11. Power / performance workstation policy

Current power scheme:
**Power saver**

## Recommendation ENV-P0-11

Create a development-session power policy.

At session start:
- switch to Balanced or High performance / equivalent available plan.

At session end:
- optionally restore the user's preferred normal plan.

The environment launcher should log which plan was active for performance baselines.

Never compare baseline numbers taken under different power plans without recording that fact.

---

# 12. Hardware headroom

16 GB RAM is enough to begin.

It becomes constrained when combining:
- Visual Studio;
- Blend;
- RevenueSystem runtime;
- browser/reference tools;
- Photoshop/Illustrator;
- Cinetic/Node rendering.

The motherboard reports two populated memory slots:
2 × 8 GB.

## Recommendation ENV-P2-01 — Optional

If the rebuild begins showing memory pressure or paging:
replace with **2 × 16 GB DDR4** for 32 GB total.

This is useful, not mandatory for RRS-P0.

No GPU upgrade is justified for the WPF rebuild.

---

# 13. Performance / diagnostics

Current shell lookup did not find ready commands for:
- dotnet-counters;
- dotnet-trace;
- dotnet-dump;
- WPR/WPA;
- PerfView.

Visual Studio profiling is available through the IDE.

## Recommendation ENV-P0-12

Do not install a large diagnostics stack immediately.

For P0 baseline:
- use Visual Studio Performance Profiler / Application Timeline;
- use one-shot .NET diagnostic tooling where available;
- collect startup, memory, GC, exception and CPU evidence.

## Recommendation ENV-P1-08

Add application-level performance markers.

Use:
- `System.Diagnostics.Metrics`;
- `ActivitySource` or EventSource where appropriate;
- structured scenario timestamps.

Initial named scenarios:
- AppStartup
- WorkspaceOpen
- CashierOpen
- CashierSave
- ReconciliationImport
- ReconciliationApprove
- AccountSearch
- ReportPreview

This lets local and CI evidence compare real operations instead of only wall-clock scripts.

## Recommendation ENV-P1-09

Only install Windows Performance Toolkit if Visual Studio/.NET traces cannot explain a real performance problem.

Avoid tooling inflation.

---

# 14. DPI / display QA

Current physical development display:
1920×1080 at 100% scaling.

This is good for the primary target but insufficient for the approved QA matrix.

## Recommendation ENV-P1-10

Create a display acceptance matrix:

- 1280×720 / 100%
- 1366×768 / 100%
- 1600×900 / 100%
- 1920×1080 / 100%
- 1920×1080 / 125%
- 1920×1080 / 150%

Automate window-size cases.

Run DPI cases on a controlled Windows profile/VM or scheduled local QA pass.

Do not infer 125/150% correctness from a 100% screenshot.

---

# 15. Font strategy

Installed useful Arabic/system fonts include:
- Segoe UI family;
- Arabic Typesetting;
- Traditional Arabic;
- Simplified Arabic;
- DecoType Naskh variants.

Not observed in the system inventory:
- Noto Naskh Arabic;
- IBM Plex Sans Arabic.

The Studio visual bible references Noto Naskh / IBM Plex as fallback candidates.

## Recommendation ENV-P1-11

Select a legally cleared two-font application strategy:

1. operational Arabic sans;
2. restrained editorial Arabic display face.

Prefer packaged, license-reviewed application resources when consistency matters.

Do not depend on a font that exists only on YASSIN.

Financial tabular numbers must be tested in the chosen operational font before lock.

---

# 16. Native WPF / Fluent policy

.NET 10 WPF includes ongoing Fluent theme improvements and RTL fixes.

Recommendation:
Use native Fluent as a **behavior/control baseline**, not as RevenueSystem's final identity.

RevenueSystem styling remains:
Studio Art Direction tokens + custom financial components.

This avoids:
- fighting Windows controls unnecessarily;
- becoming a generic Fluent demo.

---

# 17. Testing architecture

Current Validation and Integration projects are executable custom gates.

They work and should not be deleted during foundation.

Weakness:
CI/test systems get less standard per-test reporting, filtering and code coverage than a conventional test platform.

## Recommendation ENV-P1-12

For **new RevenueSystem 2.0 application/domain tests**, use a standard test framework and Microsoft Testing Platform-compatible design.

Migration strategy:
- keep existing executable Validation/Integration gates as legacy compatibility gates;
- create standard test projects for new application/domain code;
- migrate legacy test cases only when value exceeds churn.

Do not rewrite all old tests at the beginning.

## Recommendation ENV-P1-13

Add code coverage to new application/domain tests.

Use coverage as a diagnostic/guardrail, not as a vanity target.

Prefer risk-area thresholds over a single repository-wide percentage.

---

# 18. GUI automation bridge review

Strengths:
- semantic UIA first;
- physical fallback;
- before/after screenshots;
- audit log;
- state-changing wrapper;
- telemetry opt-out;
- raw coordinate policy.

Critical gaps:

## 18.1 Deny policy is declarative only

`control_policy.json` contains:
- credential_entry
- password_capture
- security bypass
- purchases
- external publish/message

But `control_bridge.py` currently checks enabled modes, not the `deny` list.

## 18.2 Audit can record sensitive values

Audit records:
- command array;
- stdout;
- stderr.

A `set_value` or `send_keys` request can therefore place entered text in logs unless upstream discipline prevents it.

## 18.3 State changes do not always require semantic verification

`verified_action.py` takes before/after screenshots, but `verify` is optional.

A visually unchanged or failed semantic effect can still complete without a required postcondition query.

## Recommendation ENV-P0-13 — Bridge v2 before broad RevenueSystem automation

Implement:
- JSON schema validation;
- action risk classification;
- code-enforced deny rules;
- sensitive-selector policy;
- value redaction;
- stdout/stderr redaction;
- required verify for consequential state changes;
- per-action timeout;
- correlation/request IDs;
- screenshot + semantic postcondition;
- bounded retry policy;
- log rotation/retention;
- automated bridge tests.

Password/credential fields must be impossible to automate through generic `set_value` / `send_keys`.

---

# 19. Isolated runtime hardening

The rebuild plan already requires isolated runtime.

The Council recommends making that requirement executable rather than documentary.

## Recommendation ENV-P0-14

Create one entry command:
`Enter-RevenueSystemIsolatedDev.ps1`

It should:
1. verify worktree SHA/branch;
2. assert clean/allowed status;
3. create a unique isolated AppData root;
4. create disposable DB path;
5. disable LAN/server discovery;
6. set synthetic-fixture mode;
7. set artifact/log root;
8. record power plan, SDK and machine fingerprint;
9. launch the app/test command;
10. fail closed if any isolation variable is missing.

No test should silently fall back to production AppData.

---

# 20. Environment fingerprint

## Recommendation ENV-P0-15

Generate:
`RRS_ENVIRONMENT_FINGERPRINT.json`

Per run include:
- OS raw build;
- Visual Studio version;
- MSBuild version;
- .NET SDK/runtime;
- Windows SDK;
- Git;
- power plan;
- display/DPI;
- CPU/RAM;
- worktree SHA;
- package lock hash;
- isolated profile ID.

Every performance/runtime handoff references the fingerprint.

This eliminates “it worked on the machine” ambiguity.

---

# 21. CI security / supply-chain

Strength:
workflow token permission is already read-only.

## Recommendation ENV-P1-14

Pin external GitHub Actions to immutable SHAs.

## Recommendation ENV-P1-15

Keep .NET 10 NuGet transitive auditing enabled.

Fresh audit found no known vulnerable packages.

Add an explicit CI security summary so a later vulnerability warning is visible as an artifact/check result.

Do not suppress NU190x globally.

---

# 22. Cinetic

Current:
- pinned source checkout exists;
- source/lint tests pass;
- full HyperFrames runtime render is not yet proven;
- WSL2 is not installed.

Recommendation:
Cinetic is **not** a blocker for RRS-P0.

Complete its runtime gate only when the first motion prototype is due.

Do not install WSL2 merely to make the environment look complete.

---

# 23. Proposed one-command developer session

After the above foundation work, create:

`Start-RevenueSystem2DevSession.ps1`

It should orchestrate, not hide:
- correct worktree;
- SDK pin;
- D: cache paths;
- isolated profile;
- performance power mode;
- logs/artifacts path;
- environment fingerprint;
- optional VS/Blend launch.

At session close:
- flush logs;
- summarize disk/temp growth;
- restore power plan if configured;
- leave source state explicit.

---

# 24. Priority plan

## P0 — Before RRS-P0 implementation

1. Clean stale user Temp safely.
2. Put rebuild worktree on D:.
3. Use non-Power-Saver development session.
4. Add `global.json`.
5. Export/add `.vsconfig`.
6. Clean canonical review worktree / relocate audit scripts.
7. Add worktree registry.
8. Pin CI Windows image after parity check.
9. Preserve failed UI-test artifacts.
10. Upgrade YASSIN Control Bridge to v2 safety.
11. Implement fail-closed isolated runtime launcher.
12. Add environment fingerprint.

## P1 — During Foundation

1. `.editorconfig`
2. `Directory.Build.props`
3. Central Package Management
4. package lock files / locked CI restore
5. patch-align Microsoft 10.0.x packages
6. CI job decomposition
7. pin action SHAs
8. structured performance markers
9. new standard test projects / coverage
10. DPI matrix
11. application font packaging decision
12. automated toolchain inventory

## P2 — Evidence-driven / Optional

1. 32 GB RAM upgrade if paging is observed.
2. Windows Performance Toolkit only if needed.
3. Finish Cinetic Windows runtime when motion work begins.
4. Dedicated disposable Windows QA VM if installer/DPI/destructive testing grows.
5. stronger paid GitHub governance only if manual merge discipline becomes a real bottleneck.

---

# 25. Council decision

The Council recommends **no major new framework and no mandatory new paid software** before rebuild execution.

The environment should be improved by making it:
- reproducible;
- isolated;
- measurable;
- disk-safe;
- automation-safe;
- evidence-driven.

Only after ENV-P0 is closed should RRS-P0 begin product implementation.

This is a work-environment review, not authorization to apply the machine/repository changes automatically.


---

# 26. ENV-P0 execution closure — 2026-10-17

Status: **PASS**

RevenueSystem implementation branch:
`rebuild/rs2-env-p0-hardening`

Draft PR:
`#78`

Validated head:
`01a522a9650dfa6f13ace5338af2ebd8f8abdf1b`

## YASSIN environment actions

- Power saver replaced by Balanced for development session.
- stale user Temp cleanup performed safely.
- C free space improved to approximately 33 GB.
- rebuild worktree placed on D:.
- isolated runtime/cache/artifact roots created on D:.
- SDK pin and VS config added.
- environment fingerprint and worktree registry tooling added.
- YASSIN Control Bridge v2 hardened and smoke-tested.

## Isolation corrections discovered during implementation

The existing test runtime correctly isolated database/settings, but three diagnostic paths still used real LocalAppData:
- StartupTraceService
- TechnicalLogService
- SourceSyncStatusService

They now route through `JsonSettingsStore.Folder`, and validation tests prove the isolation.

A fail-closed `RRS_NO_LAN` guard now prevents isolated runs from adopting SQL/LAN mode.

## Local acceptance evidence

Final run ID:
`41a3ca439f4c4b8d89a7a1aaa31e9774`

- Build: PASS, 0 warnings, 0 errors
- Validation: 94/94 PASS
- Integration: 291/291 PASS
- Authenticated UI smoke: PASS
- UI audit: 137 named elements, 0 layout warnings
- static validators: PASS
- SQLite simulations: PASS
- durable tooling: PASS
- source sync tooling: PASS
- Stage10 Release Gate: PASS [DEVELOPMENT]

## Independent GitHub evidence

Windows CI run:
`#411`

Result:
**SUCCESS**

Runner:
`windows-2025-vs2026`

The workflow also proved UI evidence upload and build artifact publication.

## Closure

ENV-P0 is complete.

The environment is now cleared for:
**RRS-P0 — Foundation Build Packet**

PR #78 remains Draft and unmerged. No RevenueSystem 2.0 product UI implementation has started yet.
