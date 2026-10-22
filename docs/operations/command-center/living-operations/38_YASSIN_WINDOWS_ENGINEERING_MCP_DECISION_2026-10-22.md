# YASSIN Windows Engineering MCP — Decision Record

Date: 2026-10-22

## Decision

Adopt a two-boundary local automation architecture instead of extending YASSIN
Verified Files into a monolithic Desktop Commander replacement.

1. **YASSIN Verified Files** remains the verified source-edit/shell boundary.
2. **windows-mcp-server v1.4.0** becomes the constrained Windows GUI/QA boundary.
3. Do not fork upstream merely to create a custom persona. In v1.4.0 personas
   are compiled into the binary; explicit toolset selection and exclusions
   provide a smaller, more auditable surface without fork maintenance.
4. Do not rely on MCP hot tool-list refresh in the active client session.
5. Keep W1.1 motion acceptance independent: operator session recording is not
   governed 30 fps WGC evidence.

## Selected Windows MCP surface

Enabled toolsets:

- screen
- interaction
- apps
- testing

Excluded from the Windows MCP boundary:

- free-form typing and broad keyboard/mouse helpers: Type, Move, Shortcut,
  MultiSelect, MultiEdit
- system helpers: Clipboard, Process, Notification
- administrative/system mutation: Registry, ScheduledTask
- broad execution/data access: PowerShell, FileSystem, Scrape, Package,
  Credentials

This leaves a compact semantic QA surface centered on Snapshot, Invoke,
WaitFor, Assert and CaptureEvidence.

## Rollout

- Phase A — validate the pinned v1.4.0 binary and AUDIT policy on YASSIN.
- Phase B — register the static MCP surface and start a fresh client session.
- Phase C — read-only smoke test: GuardrailStatus, DisplayInventory, Snapshot.
- Phase D — constrained journey test: App, Invoke, WaitFor, Assert,
  CaptureEvidence.
- Phase E — only after audit review, consider switching policy mode to enforce.

## Isolation from Motion remediation

This profile lives on
`infra/yassin-engineering-mcp-profile-20261022`, based directly on canonical
SHA `4b2a7bffe93e1defc93080906f87d7f8d123d66f`.

It is not part of PR #72 and must not alter PR #72 acceptance, Stage 7 truth,
Stage 8 state, runtime authority, or W1.1/W1.2 progression.
