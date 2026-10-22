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
- broad execution/data access: PowerShell, LaunchExecutable, FileSystem, Scrape,
  Package, Credentials

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


## Upstream security chronology

The published v1.4.0 pin was checked against the upstream security remediation
history before deployment.

- PR #71 (critical/high security remediation) merged 2026-08-04 at
  `619eae224633bcc22a4601b1850aaa3902bcecf0`.
- PR #73 (medium/low security remediation) merged 2026-08-04 at
  `3642cc3be1e1b80d81d9772c190ca9019fa40da1`.
- PR #75 (security-posture remediation, including destructive annotation coverage
  for Invoke/Click/Scroll) merged 2026-08-04 at
  `7c456f4a8c25e958b34c880bddd75909ad2b95c3`.
- The v1.4.0 tag commit
  `375f40265cb02ae47d2ba0078991b0d4fce3ab31` was cut on 2026-08-13.
- Direct Git ancestry comparison proves v1.4.0 is ahead of all three security
  merge commits with zero commits behind.

The upstream roadmap sentence saying the "newest tag is vulnerable" was committed
at 2026-08-04T13:26:44Z, before the remediation release was cut. It referred to
the tag current at that moment, not v1.4.0.

No newer tagged release exists at this review point. Upstream `main` contains
post-release dependency/refactor/signing-pipeline work and is not adopted
automatically without another review.
