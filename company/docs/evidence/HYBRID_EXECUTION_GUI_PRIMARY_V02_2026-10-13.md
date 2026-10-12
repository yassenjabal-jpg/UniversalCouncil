# Hybrid Execution GUI-Primary v0.2 — Architecture Decision Evidence

Date: 2026-10-13
Owner directive: redesign Hybrid so GUI is primary and Desktop Commander is secondary.

## Previous state

v0.1 routing priority:
1. native/API
2. Desktop Commander
3. reusable routine
4. semantic GUI
5. visual GUI

This created an execution bias toward controlling interactive applications from outside the application.

## Owner concern

The system should operate real professional applications through their GUI instead of preferring shell/script control simply because it is deterministic or cheaper.

This concern was reinforced during the After Effects pilot:
- the real blocking state was a Crash Repair dialog;
- progress required observing and manipulating the actual application UI;
- host/process evidence alone was insufficient to represent application state.

## Adopted architecture

Primary plane: **GUI**

Secondary plane: **Desktop Commander**

### Interactive application routing

1. semantic GUI/UIA
2. visual GUI assistance
3. DC fallback only when explicitly approved

A valid GUI request always wins over DC/native/routine capabilities.

### Host support routing

DC remains primary for non-interactive host work:
- filesystem
- Git
- processes
- tests
- logs
- artifact checks
- recovery diagnostics

## New fail-closed rule

For an action with:
`interactive_app=true`

the router refuses DC fallback unless:
`allow_dc_fallback=true`

This prevents future code from silently restoring DC-first behavior.

## Preserved controls

The redesign keeps:
- one physical GUI controller lease;
- post-state verification for T2/T3;
- UNKNOWN is never success;
- bounded batching;
- compact result projection;
- routine graduation only after verified clean repeats.

## Automation philosophy

Automation should make GUI interaction deterministic without replacing the GUI as the authoritative control surface.

Preferred graduation target:
`verified_gui_routine_or_app_native_macro`

## Acceptance

Required before merge:
- config validation;
- hybrid unit tests;
- full company test suite;
- Ruff / formatting / compile;
- coverage ratchet;
- GitHub CI;
- real YASSIN GUI + DC-support smoke after merge.

## Expected practical behavior

For After Effects:
- GUI opens/dismisses dialogs and invokes application commands;
- DC stages JSX/assets and verifies renders/logs afterward.

For RevenueSystem:
- GUI is preferred for workflows intended to represent real user interaction;
- DC remains for repo/tests/logs/database-safe diagnostics where appropriate.

## Verdict

**ADOPT — GUI PRIMARY / DC SECONDARY.**
