# YASSIN Commander — Secure Remote Execution Design

**Date:** 2026-10-20  
**Status:** DESIGN LOCK CANDIDATE  
**Owner:** Yassen Jabal  
**Purpose:** Replace the monthly-quota dependency on Desktop Commander for controlling the Windows PC named **YASSIN** from ChatGPT conversations, while keeping Android as only the chat interface.

## 1. Goal

The user sends ordinary instructions to ChatGPT from Android. ChatGPT uses the already-connected GitHub plugin as the command transport. A private GitHub control repository dispatches trusted jobs to YASSIN. YASSIN executes the jobs locally and returns structured results, logs, screenshots, and artifacts through GitHub.

There is **no direct Android-to-PC connection** and no inbound port exposed on YASSIN.

## 2. Why this architecture

Custom MCP write/modify actions are not currently available to ChatGPT Plus on mobile. Therefore the control path must use a plugin that already works in the user's ChatGPT surface. GitHub is already connected and supports write actions from ChatGPT.

GitHub self-hosted runners support Windows 10/11 and connect outbound to GitHub over HTTPS. GitHub explicitly recommends using self-hosted runners only with private repositories.

The local Windows automation engine will be `deploymenttheory/windows-mcp-server`, because it provides:
- Windows UI Automation tree access.
- mouse / keyboard and control-pattern invocation.
- screenshots.
- application and window control.
- PowerShell.
- filesystem and process tools.
- policy enforcement and tamper-evident audit features.
- an explicit kill switch and configurable toolsets.

## 3. Architecture

```text
Android ChatGPT
      |
      | natural-language instruction
      v
ChatGPT + GitHub plugin
      |
      | creates a structured yc-job Issue
      v
PRIVATE GitHub control repository
      |
      | issues event -> trusted workflow
      v
GitHub self-hosted runner on YASSIN
(interactive logged-in Windows user session)
      |
      | invokes local bridge
      v
YASSIN Commander Bridge
      |
      | MCP over local stdio only
      v
windows-mcp-server.exe
      |
      v
Windows files / processes / UI / applications
```

Results return through the same private GitHub repository as:
- an issue comment for structured text,
- workflow logs for diagnostics,
- GitHub Actions artifacts for screenshots or files.

## 4. Components

### 4.1 Private control repository

A new private repository named `YASSIN-Commander-Control`.

It contains only:
- the fixed trusted workflow,
- dispatcher/bridge releases or checksums,
- job schema,
- policy configuration,
- audit metadata.

It must never accept public forks or untrusted collaborators.

### 4.2 GitHub self-hosted runner

Runs on YASSIN with labels:

`self-hosted, windows, x64, yassin-commander`

For GUI automation it must run in the interactive user session, not Windows Session 0. Persistence is provided by a Task Scheduler logon task that starts `run.cmd` only when the intended Windows user is logged on.

Shell/file jobs may execute while the runner is active. UI jobs require an unlocked interactive desktop. Windows secure-desktop surfaces such as the lock screen and UAC prompts are intentionally not automatable.

### 4.3 Local Windows MCP engine

Install the latest signed release of `deploymenttheory/windows-mcp-server` into a stable user-local directory.

Initial enabled toolsets:
- `screen`
- `interaction`
- `apps`
- `system`
- `filesystem`
- `shell`

Do **not** enable by default:
- registry mutation,
- scheduled-task mutation,
- services mutation,
- package-management mutation,
- unrestricted network/web tools.

The engine is launched only on loopback/stdin by the local bridge. It is not exposed as a public HTTP server.

### 4.4 YASSIN Commander Bridge

A small compiled Windows executable with one responsibility: convert a validated job payload into one or more calls to the local Windows MCP engine and return normalized results.

The bridge must:
- reject unknown job versions,
- reject unknown actions,
- validate all arguments against JSON Schema,
- canonicalize filesystem paths,
- enforce allowed path roots,
- enforce executable allowlists where applicable,
- block secret-bearing locations by default,
- refuse elevation/UAC bypass,
- enforce timeouts and output limits,
- redact obvious credentials/tokens from returned output,
- write a local append-only audit record.

No arbitrary raw MCP payload supplied through an Issue is forwarded directly.

## 5. Job protocol

ChatGPT creates an Issue labeled `yc-job` with a machine-readable block.

Example:

```json
{
  "version": 1,
  "target": "YASSIN",
  "action": "filesystem.list",
  "args": {
    "path": "C:\\Users\\<user>\\Documents",
    "depth": 2
  },
  "risk": "low",
  "request_id": "yc-..."
}
```

The workflow never evaluates Issue text as PowerShell, YAML, expression syntax, or shell source.

### Initial action families

- `system.status`
- `filesystem.list`
- `filesystem.read`
- `filesystem.write`
- `filesystem.copy`
- `filesystem.move`
- `process.list`
- `process.start`
- `process.stop`
- `shell.powershell`
- `screen.screenshot`
- `ui.snapshot`
- `ui.invoke`
- `ui.click`
- `ui.type`
- `ui.shortcut`
- `app.launch`
- `app.switch`

Risky destructive actions are withheld from v1 until the low-risk path is proven.

## 6. Security model

### Network

YASSIN opens outbound HTTPS connections only. No router port forwarding and no inbound listener are required for the control channel.

### Authentication

The self-hosted runner registration token is used only during setup and is not committed.

Repository access is private. The runner uses GitHub's normal runner identity for jobs; the workflow token receives only the minimum permissions needed for issues and artifacts.

### Authorization

The workflow executes only when all are true:
- repository is the dedicated private control repository,
- event is an Issue event from the trusted repository,
- Issue contains the `yc-job` label,
- request target is exactly `YASSIN`,
- payload validates,
- requested action is enabled by local policy,
- actor matches the configured owner allowlist.

### Local policy

Default file roots will be explicit. Sensitive locations such as browser profiles, credential stores, SSH private keys, DPAPI material, password databases, and OS secret stores are denied unless the owner explicitly changes policy.

### High-risk actions

The following require a separate explicit approval gate and are not part of the first release:
- bulk deletion,
- shutdown/restart,
- registry write,
- service changes,
- scheduled-task creation,
- credential operations,
- security-control changes,
- unrestricted PowerShell,
- installing unsigned executables.

### Audit

Every job records:
- request id,
- GitHub issue id,
- actor,
- requested action,
- normalized arguments,
- start/end timestamps,
- result status,
- policy decision,
- output digest.

The Windows MCP audit chain remains enabled as a second independent record.

## 7. Screenshots and files

Screenshots and generated files are never committed to the repository history by default.

They are uploaded as short-lived GitHub Actions artifacts. ChatGPT can fetch the artifact through the GitHub connector when needed.

Text results are capped and summarized before posting to the Issue to avoid leaking large logs or secrets.

## 8. Failure behavior

- Invalid request -> fail closed; comment with validation error.
- Runner offline -> job remains queued; no fallback machine.
- UI locked -> return `INTERACTIVE_SESSION_UNAVAILABLE`; do not attempt login or UAC bypass.
- Windows MCP policy denial -> return the policy reason unchanged.
- Timeout -> terminate the child tool call and return a bounded error.
- Oversized output -> store as artifact and return a digest/reference.
- Tool crash -> bridge survives where possible and records failure.

## 9. Bootstrap constraint

Desktop Commander remote execution is currently paused because its monthly quota is exhausted. Therefore the new agent cannot be installed remotely through DC right now.

All software, policies, workflows, and a one-click bootstrap package can be prepared in advance. The first installation on YASSIN requires one trusted local execution step (or another already-authorized remote-control channel). After that bootstrap succeeds, future administration is performed through YASSIN Commander itself.

## 10. Acceptance criteria

The first usable release is accepted only when all of these are demonstrated on YASSIN:

1. Runner appears online only for the intended private control repository.
2. A ChatGPT-created low-risk job reaches YASSIN without DC.
3. `system.status` returns the expected machine identity.
4. A permitted directory can be listed.
5. A test text file can be written and read in an allowed sandbox directory.
6. A screenshot can be captured and retrieved as an artifact.
7. A visible application can be launched and discovered through UI Automation.
8. A deliberately forbidden path is denied.
9. A malformed Issue payload is denied.
10. Killing the local runner immediately stops remote execution.
11. Reboot/logon restores the runner without exposing an inbound port.
12. No secret, PAT, registration token, or credential appears in repository files, Issue comments, logs, screenshots, or artifacts.

## 11. Deliberate non-goals for v1

- Bypassing the Windows lock screen.
- Automating UAC secure desktop.
- Running as SYSTEM.
- Exposing YASSIN directly to the public internet.
- Replacing AnyDesk as a human remote-viewing product.
- Allowing arbitrary collaborators to submit jobs.
- Automatic privilege escalation.
- General multi-device fleet support.

## 12. Rollout

Phase A — build and offline-test the schema, bridge, policy and workflow.

Phase B — create the dedicated private control repository and prepare the signed/checksummed bootstrap bundle.

Phase C — perform the one-time bootstrap on YASSIN and prove low-risk file/system jobs.

Phase D — enable screenshots and UI Automation and prove one harmless GUI workflow.

Phase E — add higher-risk actions one family at a time only after audit and denial tests pass.

## 13. Source constraints

- OpenAI custom MCP apps with write/modify are not currently available on Plus/mobile, so they are not the control transport for v1.
- GitHub self-hosted runner documentation requires outbound HTTPS and supports Windows 10/11.
- GitHub recommends self-hosted runners only with private repositories.
- windows-mcp-server intentionally has powerful system access; its own policy/audit controls are defense-in-depth and do not replace Windows permissions.
