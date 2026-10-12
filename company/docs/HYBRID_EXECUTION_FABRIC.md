# Hybrid Execution Fabric — GUI-Primary v0.2

Status: IMPLEMENTED_PROTOTYPE
Governance status: execution substrate; does not replace Council role governance.

## Decision

The Hybrid Execution Fabric is now **GUI-primary / DC-secondary**.

For interactive desktop applications, the application UI is the authoritative control surface. Desktop Commander is a support plane for machine-level work around the application, not the default controller of the application itself.

The governing principle is:

> **Use GUI to operate interactive applications. Use DC to support, inspect, stage, verify and recover the host around them.**

## Why v0.2 exists

v0.1 preferred deterministic DC/native execution before GUI. That reduced token use, but it also created a structural bias toward controlling creative and interactive applications from outside their real UI.

This is unacceptable when:
- application state exists in menus, dialogs, panels, timelines or visual canvases;
- the user expects real interaction with the professional application;
- GUI state determines success;
- a shell/script route can bypass or misrepresent the application's real state.

v0.2 corrects that bias.

## Primary and secondary planes

### Primary — GUI Interaction Plane

The GUI plane owns interactive application work:
- inspect the live application state;
- open menus, dialogs and panels;
- invoke semantic controls;
- enter text and values;
- perform bounded clicks/keyboard actions when semantic controls are unavailable;
- observe visual state;
- verify post-action state.

Routing inside GUI:
1. semantic UI / UI Automation;
2. visual GUI assistance;
3. bounded physical interaction only through the governed bridge.

Raw arbitrary coordinate control remains disabled by default in the Hybrid router.

### Secondary — Desktop Commander Support Plane

DC supports the GUI workflow with:
- filesystem reads/writes;
- Git operations;
- process inspection;
- test execution;
- logs;
- artifact existence/hash/size checks;
- staging files before GUI work;
- collecting outputs after GUI work;
- recovery/diagnostics when the application is unhealthy.

DC **must not bypass an available GUI path for interactive application work**.

For an action marked `interactive_app=true`, DC fallback requires explicit:
`allow_dc_fallback=true`.

That fallback is a recovery decision, not the default route.

## Routing profiles

### Interactive application

Order:
1. `gui_semantic_uia`
2. `gui_visual_assist`
3. `dc_control_plane` only as explicit fallback

If a valid `gui_request` exists, GUI wins even when:
- `dc_capable=true`;
- `native_available=true`;
- `routine_available=true`.

### Host support

For tasks that are not application interaction, DC remains appropriate:
- filesystem;
- Git;
- processes;
- tests;
- logs;
- artifact checks;
- recovery.

Order:
1. `dc_control_plane`
2. `native_api_or_connector`
3. `reusable_routine`

### External service

For non-desktop external services, a true native connector may remain preferable.

Order:
1. `native_api_or_connector`
2. `dc_control_plane`
3. `reusable_routine`

This does not weaken the GUI-primary rule for desktop applications.

## Single-controller rule

Only one state-changing GUI requester may hold the desktop controller lease at a time.

This prevents:
- focus races;
- pointer/keyboard contention;
- interleaved state changes;
- ambiguous action ownership.

GUI observation does not require the control lease. GUI control does.

## Observation before action

Interactive work should begin by observing the current application state rather than assuming a remembered state.

The GUI configuration therefore requires:
- pre-action observation;
- semantic-first interaction;
- visual fallback when semantics are insufficient.

## Verification after state change

Provider success is not enough.

T2/T3 state changes require independent post-state verification.

If the action executes but the expected state cannot be verified, result state is:

`UNKNOWN`

`UNKNOWN` is never silently promoted to `SUCCEEDED`.

## DC support examples

Good DC use around a GUI workflow:
- create a project directory before opening the app;
- confirm a render file appeared after the app rendered it;
- inspect process health after a crash;
- archive evidence/screenshots;
- run Git/tests after edits;
- read logs when the GUI reports a failure.

Bad DC use:
- replacing an available application menu action with a shell hack merely because it is easier;
- declaring success from filesystem/process evidence when the UI state contradicts it;
- bypassing a live interactive application without explicit fallback approval.

## Automation graduation

Repeated work may graduate only after verified clean repetitions.

Preferred graduation target in v0.2:

`verified_gui_routine_or_app_native_macro`

The goal is to make GUI work more deterministic without replacing the application UI as the authoritative interaction surface.

Default threshold: 3 verified repetitions with:
- no UNKNOWN;
- no accidental action.

## Batching

Bounded batches remain supported:
- maximum configured deterministic steps: 6;
- one controller lease across GUI-control batch;
- stop on first non-SUCCEEDED result;
- no lease for pure host-support/DC batches.

## Compact result projection

Model-facing output remains compact by default.

Raw provider output stays local unless explicitly needed.

For GUI observations such as `list_windows`, projection keeps only bounded state summaries needed for reasoning and verification.

## Risk tiers

- T0 Observe: read-only.
- T1 Local reversible: navigation/focus/bounded reversible action.
- T2 Local state change: post-state verification required.
- T3 External consequential: approved task + explicit Owner confirmation.
- T4 Separately governed/blocked: fail closed.

The router maps to existing Tool Authority; it does not create new authority.

## Example: After Effects

Correct v0.2 flow:
1. GUI observes After Effects window/dialog state.
2. GUI dismisses startup/recovery dialogs.
3. GUI invokes File → Scripts → Run Script File or equivalent application UI action.
4. GUI observes project/timeline/render state.
5. DC checks output files, logs and process health after the GUI action.
6. independent verification confirms expected result.

Incorrect v0.1-style flow:
1. assume app state;
2. push a shell command into an already-running interactive app;
3. infer success only from process/file behavior.

## CLI

Plan:

`python tools/hybrid_execute.py action.json`

Execute:

`python tools/hybrid_execute.py action.json --execute --task-approved`

External consequential action:

`--owner-confirmed`

Persist state:

`--state .runtime/hybrid/<task>.json`

## Compatibility

Execution path enum names remain stable:
- `gui_semantic_uia`
- `gui_visual_assist`
- `dc_control_plane`
- `native_api_or_connector`
- `reusable_routine`

The breaking change is **routing priority and policy**, not serialization names.

## Acceptance conditions

v0.2 is accepted only when:
1. config validator passes;
2. GUI beats DC/native/routine when a GUI request exists;
3. interactive app without GUI cannot silently fall back to DC;
4. explicit DC recovery fallback still works;
5. controller lease behavior remains correct;
6. independent post-state verification remains correct;
7. full repository tests and coverage gate pass;
8. real GUI + DC-support smoke is performed on YASSIN.

## Related governing sources

- `company/config/hybrid_execution.json`
- `company/runtime/hybrid_execution.py`
- `company/tests/test_hybrid_execution.py`
- `company/config/tool_authority.json`
- `company/config/evidence_sync.json`
- `CouncilVideoStudio/docs/YASSIN_CONTROL_BRIDGE.md`
