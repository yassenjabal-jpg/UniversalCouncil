# YASSIN-ENGINEERING MCP Profile

Status: **prepared / not yet deployed on YASSIN**.

This profile uses the pinned public release
`deploymenttheory/windows-mcp-server v1.4.0` as a **GUI/QA-only** MCP surface.
It deliberately does **not** merge Windows control into YASSIN Verified Files.

## Architecture

- **Windows MCP**: perception, UI Automation, constrained interaction, assertions,
  screenshots, evidence capture and session recording.
- **YASSIN Verified Files**: source/file mutation, shell execution and process
  lifecycle with SHA preconditions, backups and write verification.

This separation prevents a GUI automation server from becoming the authority for
source edits or arbitrary shell/filesystem mutation.

## Pinned upstream

- Repository: `deploymenttheory/windows-mcp-server`
- Release: `v1.4.0`
- Tag commit: `375f40265cb02ae47d2ba0078991b0d4fce3ab31`
- Official Windows amd64 ZIP SHA-256:
  `6d44fea16d6bac9a17076dd7770970ad0ca93c8cb06bc9b86eaf6aa8b5b77055`

## Served surface

Enabled toolsets:

- `screen`
- `interaction`
- `apps`
- `testing`

Explicitly excluded:

- `Type`, `Move`, `Shortcut`, `MultiSelect`, `MultiEdit`
- `Clipboard`, `Process`, `Notification`
- `Registry`, `ScheduledTask`
- `PowerShell`, `LaunchExecutable`, `FileSystem`, `Scrape`, `Package`, `Credentials`

Expected callable tools:

`App, Assert, CaptureEvidence, Click, DisplayInventory, GetText,
GuardrailStatus, Invoke, Kill, Recording, Screenshot, Scroll, Snapshot, Wait,
WaitFor`.

## QA loop

`Snapshot -> Invoke/Click -> WaitFor -> Assert -> CaptureEvidence`

Prefer `Invoke` over synthetic `Click` whenever a control exposes a Windows UI
Automation pattern.

## Policy rollout

1. Begin with `YASSIN_ENGINEERING_AUDIT_POLICY.json`.
2. Review posture decisions, audit output, screenshots and recording behavior.
3. Register the static Codex profile only after local validation.
4. Start a **fresh** ChatGPT/Codex session after MCP registration changes.
5. Smoke-test read-only perception first: `GuardrailStatus`,
   `DisplayInventory`, `Snapshot`.
6. Then test constrained interaction: `App -> Invoke -> WaitFor -> Assert ->
   CaptureEvidence`.
7. Switch to `YASSIN_ENGINEERING_ENFORCE_POLICY.json` only after the audit run
   is understood.

Do not depend on MCP hot tool-list refresh. Current Codex issues document stale
in-session MCP schemas after server/config changes.

## W1.1 boundary

The Windows MCP session recording (4 fps by default) is for operator/audit
review. It is **not** W1.1 acceptance evidence. The governed 30 fps WGC evidence
path remains authoritative.

## Repository isolation

This infrastructure lives on
`infra/yassin-engineering-mcp-profile-20261022`, created directly from the
canonical base SHA
`4b2a7bffe93e1defc93080906f87d7f8d123d66f`.

It is intentionally independent of PR #72. Do not merge this work through the
Motion-remediation PR.
