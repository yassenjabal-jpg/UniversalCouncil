# YASSIN-ENGINEERING MCP Profile

Status: **deployed on YASSIN / AUDIT verified / awaiting fresh client-session tool exposure**.

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
- Installed EXE SHA-256 on YASSIN:
  `6cd490edcd393c2021f2136860737b92f393c18c9e6a5199d4f2b389085e71cb`
- The installed EXE matched the EXE extracted from the digest-verified official
  ZIP byte-for-byte by SHA-256.

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

The deployed server returned exactly these 15 tools through live MCP
`tools/list`; no forbidden tool leakage was observed.

## QA loop

`Snapshot -> Invoke/Click -> WaitFor -> Assert -> CaptureEvidence`

Prefer `Invoke` over synthetic `Click` whenever a control exposes a Windows UI
Automation pattern.

The YASSIN AUDIT smoke verified:

- `GuardrailStatus`: mode `audit`, `admit=true`
- `DisplayInventory`: 1920x1080, DPI 96, 100% scale
- `Snapshot`: real foreground Notepad UIA tree
- `App switch`: PASS
- `WaitFor active_window`: PASS
- semantic `Invoke` on Notepad Maximize: PASS
- `Assert` after Maximize: PASS
- `CaptureEvidence`: PASS
- semantic Restore: PASS
- `Assert` after Restore: PASS

## Audit destination rule

The audit path **must exist as a directory before the MCP server starts**.

If `audit_destination` points to a nonexistent path, v1.4.0 can create/use it as
a single audit file. Reusing that file across multiple short-lived MCP sessions
creates independent sequence-0 chains in one file and makes strict verification
fail with a sequence gap.

The deployment corrected this by preserving the original diagnostic file as:

`E:\GPT\Tools\DC-Replacement-20261022\logs\windows-mcp-audit.legacy-sequence-gap-20261022`

and creating this path as a directory:

`E:\GPT\Tools\DC-Replacement-20261022\logs\windows-mcp-audit`

After correction:

`windows-mcp-server audit verify <audit-dir> --strict`

returned PASS for a sealed 11-entry session with an intact manifest chain.

## Codex registration

The constrained profile is registered globally as:

`yassin_windows_engineering`

and is enabled.

The prior `yassin_windows` registration remains temporarily as a fallback.
Do not remove it until a **fresh ChatGPT/Codex session** confirms that
`yassin_windows_engineering` is exposed and callable through the client.

Do not depend on MCP hot tool-list refresh. Current Codex issues document stale
in-session MCP schemas after server/config changes.

## Policy rollout

1. Current deployment uses `YASSIN_ENGINEERING_AUDIT_POLICY.json`.
2. Keep the audit path as a pre-existing directory.
3. Start a fresh ChatGPT/Codex session.
4. Confirm the constrained tool surface appears.
5. Repeat a small perception/action/evidence smoke through the client-bound MCP.
6. Only then consider removing the legacy registration.
7. Switch to `YASSIN_ENGINEERING_ENFORCE_POLICY.json` only after the audit run
   and client-bound behavior are reviewed.

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

Deployment evidence is recorded in:

`state/command-center/project-governance/yassin-engineering-mcp-deployment-evidence.json`
