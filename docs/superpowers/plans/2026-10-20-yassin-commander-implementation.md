# YASSIN Commander Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a secure, auditable, quota-free control path from ChatGPT to the Windows PC YASSIN using GitHub as the transport, a private self-hosted runner, a compiled local bridge, and windows-mcp-server as the Windows automation engine.

**Architecture:** Public source and tests live in `UniversalCouncil`. The actual control workflow runs only from a dedicated private repository named `YASSIN-Commander-Control`. A self-hosted GitHub runner on YASSIN receives issue-triggered jobs, invokes a compiled Go bridge, and the bridge validates policy before calling `windows-mcp-server.exe` over local stdio MCP.

**Tech Stack:** Go 1.25+, `github.com/modelcontextprotocol/go-sdk v1.8.0`, windows-mcp-server v1.4.0, GitHub Actions self-hosted runner v2.338.0, PowerShell 7/Windows PowerShell for bootstrap only, JSON, GitHub Issues + Actions artifacts.

**Spec:** `docs/superpowers/specs/2026-10-20-yassin-commander-design.md`

## Global Constraints

- Target machine name is exactly `YASSIN`.
- Control transport is GitHub; no custom ChatGPT MCP transport is required for v1.
- The self-hosted runner must be bound only to the dedicated private control repository.
- No inbound port or public listener may be opened on YASSIN.
- The local MCP engine transport is stdio only.
- UI automation must run in the interactive logged-in Windows user session, never Session 0/SYSTEM.
- No UAC bypass, lock-screen bypass, privilege escalation, or SYSTEM execution.
- Issue text is data only; it must never be evaluated as PowerShell, CMD, YAML, template expression, or raw MCP.
- v1 allows only explicitly registered action families; unknown actions fail closed.
- High-risk actions listed in the spec remain disabled in v1.
- Screenshots/generated files use Actions artifacts, not repository history.
- Secrets, PATs, runner registration tokens, credentials, and browser secret stores must never be returned in logs or issue comments.
- `windows-mcp-server` is pinned to v1.4.0 Windows amd64 SHA-256 `6d44fea16d6bac9a17076dd7770970ad0ca93c8cb06bc9b86eaf6aa8b5b77055`.
- GitHub runner is pinned for bootstrap to v2.338.0 Windows x64 SHA-256 `f48e0750a21812bca5f82de5f7f5aeae71abee647fab5a582f1742d07eba455f`.
- MCP Go SDK is pinned to `v1.8.0`.
- The bridge must build as a single Windows amd64 executable with no runtime dependency other than the separately installed Windows MCP binary.
- Local bridge audit records are append-only JSONL with per-entry SHA-256 chaining.

## Review Focus

1. **Path traversal and Windows path aliases:** inputs using `..`, mixed separators, UNC paths, alternate device prefixes, reparse points, and case changes must not escape configured roots. Task 2 owns these tests.
2. **Injection through Issue bodies:** embedded PowerShell, workflow expressions, quotes, newlines, Unicode escapes, and JSON-looking text outside the machine block must remain inert. Tasks 1 and 6 own these tests.
3. **Secret exfiltration through output:** tokens, authorization headers, GitHub tokens, and credential-like values in tool output must be redacted before comments/logs. Task 3 owns these tests.
4. **Locked/non-interactive Windows session:** UI actions must return `INTERACTIVE_SESSION_UNAVAILABLE` without retries that attempt logon/UAC interaction. Task 5 owns this test.
5. **Runner/control-repo trust boundary:** workflows from public repositories, forks, PR refs, or untrusted actors must never dispatch to YASSIN. Task 6 owns these tests.

---

### Task 1: Job Envelope, Issue Parser, and Strict Validation

**Files:**
- Create: `tools/yassin_commander/go.mod`
- Create: `tools/yassin_commander/go.sum`
- Create: `tools/yassin_commander/internal/job/model.go`
- Create: `tools/yassin_commander/internal/job/issue.go`
- Create: `tools/yassin_commander/internal/job/validate.go`
- Test: `tools/yassin_commander/internal/job/job_test.go`

**Interfaces:**
- Produces: `job.Request`, `job.ParseIssueEvent([]byte) (Request, error)`, `job.Validate(Request, ValidationConfig) error`.
- Consumes: only standard library.

- [ ] **Step 1: Write failing tests for valid v1 requests and fail-closed parsing**
  - Accept exactly one fenced JSON machine block.
  - Require `version == 1`, `target == "YASSIN"`, non-empty `request_id`, registered action, object `args`.
  - Reject duplicate machine blocks, malformed JSON, unknown top-level fields, unknown versions, unknown actions, wrong target, oversized bodies, and trailing executable-looking text that tries to alter the parsed payload.
  - Assert workflow-expression text such as `${{ ... }}` remains plain data.

- [ ] **Step 2: Run**
  - Command: `cd tools/yassin_commander && go test ./internal/job -v`
  - Expected: FAIL because parser/validator do not exist.

- [ ] **Step 3: Implement strict decoding**
  - Use `json.Decoder.DisallowUnknownFields()`.
  - Cap event body bytes before parsing.
  - Parse GitHub issue event metadata separately from the job payload.
  - Expose actor, issue number, labels, repository full name, and body through typed structures; do not pass the raw event to later shell code.

- [ ] **Step 4: Run tests and commit**
  - Expected: PASS.
  - Commit: `feat(yc): add strict job envelope validation`.

---

### Task 2: Local Authorization Policy and Windows Path Guard

**Files:**
- Create: `tools/yassin_commander/internal/policy/config.go`
- Create: `tools/yassin_commander/internal/policy/actions.go`
- Create: `tools/yassin_commander/internal/policy/paths_windows.go`
- Create: `tools/yassin_commander/internal/policy/risk.go`
- Create: `tools/yassin_commander/config/policy.example.json`
- Test: `tools/yassin_commander/internal/policy/policy_test.go`

**Interfaces:**
- Consumes: `job.Request`.
- Produces: `policy.Decision {Allowed bool, Reason string, NormalizedArgs map[string]any}`, `policy.Authorize(Request, Config) Decision`.

- [ ] **Step 1: Write failing policy tests**
  - Allow only the v1 action list from the spec.
  - Deny all paths outside explicit roots.
  - Deny browser profile stores, Windows Credential Manager export/backup locations, SSH private-key locations, DPAPI material, SAM/SECURITY hives, and configured secret globs.
  - Reject UNC/device paths and path traversal.
  - Reject junction/reparse escape when the target exists.
  - Preserve read/write distinction so a root can be read-only.

- [ ] **Step 2: Run**
  - Command: `go test ./internal/policy -v`
  - Expected: FAIL.

- [ ] **Step 3: Implement canonical Windows path authorization**
  - Use Windows path cleaning and volume-aware comparison.
  - Resolve existing paths before authorization; verify resolved target remains under an allowed root.
  - For new files, resolve the nearest existing parent and authorize that parent before creating.
  - Maintain action-to-risk metadata in code, not in Issue input.

- [ ] **Step 4: Run tests and commit**
  - Commit: `feat(yc): enforce local action and path policy`.

---

### Task 3: Redaction and Tamper-Evident Local Audit Chain

**Files:**
- Create: `tools/yassin_commander/internal/redact/redact.go`
- Create: `tools/yassin_commander/internal/audit/record.go`
- Create: `tools/yassin_commander/internal/audit/writer.go`
- Test: `tools/yassin_commander/internal/redact/redact_test.go`
- Test: `tools/yassin_commander/internal/audit/audit_test.go`

**Interfaces:**
- Produces: `redact.Text(string) string`, `audit.Writer.Append(Record) error`, `audit.Verify(path) error`.
- Audit record fields: request id, issue number, actor, action, normalized argument digest, policy verdict, start/end UTC, status, result digest, previous hash, entry hash.

- [ ] **Step 1: Write failing redaction tests**
  - Redact Bearer headers, GitHub classic/fine-grained token shapes, common API-key assignments, authorization/cookie header values, and configured literal secrets.
  - Keep ordinary paths and non-secret IDs readable.

- [ ] **Step 2: Write failing audit-chain tests**
  - Verify first entry, chained entries, tamper detection, truncation detection where possible from a stored head manifest, and concurrent append serialization.

- [ ] **Step 3: Implement bounded redaction + append-only JSONL chain**
  - Hash normalized JSON bytes with SHA-256.
  - Write through a locked file handle.
  - Never log raw file contents, screenshots, environment dumps, or full shell output.

- [ ] **Step 4: Run and commit**
  - Command: `go test ./internal/redact ./internal/audit -v`
  - Commit: `feat(yc): add redaction and chained audit log`.

---

### Task 4: MCP Client Adapter for windows-mcp-server

**Files:**
- Create: `tools/yassin_commander/internal/mcpclient/client.go`
- Create: `tools/yassin_commander/internal/mcpclient/translate.go`
- Create: `tools/yassin_commander/internal/mcpclient/fake_test.go`
- Test: `tools/yassin_commander/internal/mcpclient/client_test.go`
- Modify: `tools/yassin_commander/go.mod`

**Interfaces:**
- Consumes: authorized action + normalized arguments.
- Produces: `mcpclient.Result {Text string, Files []Artifact, IsError bool, Code string}`.
- Dependency: `github.com/modelcontextprotocol/go-sdk/mcp v1.8.0`.

- [ ] **Step 1: Write a fake MCP child-process test**
  - Test process discovery/connect over `mcp.CommandTransport`.
  - Verify timeout cancels the request and closes the child.
  - Verify an MCP error maps to a bounded bridge error.
  - Verify unknown returned content types do not panic.

- [ ] **Step 2: Run**
  - Command: `go test ./internal/mcpclient -v`
  - Expected: FAIL.

- [ ] **Step 3: Implement local stdio client**
  - Launch exactly the configured `windows-mcp-server.exe`.
  - Arguments: `stdio --policy-config <absolute policy path>`.
  - Set working directory explicitly.
  - Pass only a curated environment; do not inherit GitHub token or unrelated secrets into the MCP child.
  - Enforce per-call timeout and max returned text/file count.

- [ ] **Step 4: Pin SDK and run tests**
  - `go get github.com/modelcontextprotocol/go-sdk@v1.8.0`
  - `go test ./internal/mcpclient -v`
  - Commit: `feat(yc): connect bridge to local Windows MCP over stdio`.

---

### Task 5: Action Registry and Safe v1 Execution Surface

**Files:**
- Create: `tools/yassin_commander/internal/actions/registry.go`
- Create: `tools/yassin_commander/internal/actions/system.go`
- Create: `tools/yassin_commander/internal/actions/filesystem.go`
- Create: `tools/yassin_commander/internal/actions/process.go`
- Create: `tools/yassin_commander/internal/actions/shell.go`
- Create: `tools/yassin_commander/internal/actions/screen.go`
- Create: `tools/yassin_commander/internal/actions/ui.go`
- Create: `tools/yassin_commander/internal/actions/apps.go`
- Test: `tools/yassin_commander/internal/actions/actions_test.go`

**Interfaces:**
- Produces: `actions.Registry.Execute(ctx, Request, policy.Decision) (mcpclient.Result, error)`.
- Registry maps public v1 action names to fixed MCP tool names and fixed argument translations.

- [ ] **Step 1: Write table-driven mapping tests**
  - Every spec v1 action maps to exactly one handler.
  - No Issue input can choose an arbitrary MCP tool name.
  - `shell.powershell` initially accepts only a bounded command policy: explicit executable/script roots and prohibited command families from config; it is not raw unrestricted PowerShell.
  - UI handlers check interactive-session availability first.

- [ ] **Step 2: Add locked-session test**
  - Mock session probe as unavailable.
  - Assert all `ui.*`, `screen.screenshot`, and visible `app.*` actions return `INTERACTIVE_SESSION_UNAVAILABLE` without invoking MCP.

- [ ] **Step 3: Implement mappings**
  - Use Windows MCP tool discovery at startup and fail closed if required tool contracts are missing or changed.
  - Normalize result file paths into the bridge output directory only.

- [ ] **Step 4: Run and commit**
  - `go test ./internal/actions -v`
  - Commit: `feat(yc): expose bounded v1 action registry`.

---

### Task 6: Bridge CLI, GitHub Event Trust Checks, and Result Contract

**Files:**
- Create: `tools/yassin_commander/cmd/yc-bridge/main.go`
- Create: `tools/yassin_commander/internal/runner/event.go`
- Create: `tools/yassin_commander/internal/result/result.go`
- Create: `tools/yassin_commander/internal/result/files.go`
- Test: `tools/yassin_commander/internal/runner/event_test.go`
- Test: `tools/yassin_commander/internal/result/result_test.go`

**Interfaces:**
- CLI:
  - `yc-bridge execute --event <github-event.json> --config <config.json> --out <dir>`
  - `yc-bridge verify-audit --audit <dir>`
  - `yc-bridge doctor --config <config.json>`
- Output:
  - `result.json` containing request id, status, code, redacted summary, artifact manifest.
  - Binary/text artifacts only inside the supplied output directory.

- [ ] **Step 1: Write actor/repository/label trust tests**
  - Require repository exactly `yassenjabal-jpg/YASSIN-Commander-Control`.
  - Require label `yc-job`.
  - Require configured owner actor allowlist.
  - Reject pull_request events, fork repositories, edited workflow refs, missing event fields, and wrong target.

- [ ] **Step 2: Write result-boundary tests**
  - Cap comment summary length.
  - Redirect oversized text to artifact.
  - Redact before `result.json` is written.
  - Never copy arbitrary source files into artifact output unless the action explicitly returns that file and policy permits it.

- [ ] **Step 3: Implement CLI pipeline**
  - Parse event -> validate -> authorize -> append audit start -> execute -> redact/package -> append audit completion.
  - Exit non-zero for denied/error jobs but always attempt to emit bounded `result.json`.

- [ ] **Step 4: Run and commit**
  - `go test ./... -v`
  - `go build ./cmd/yc-bridge`
  - Commit: `feat(yc): add bridge CLI and GitHub trust boundary`.

---

### Task 7: Windows MCP Policy, Version Lock, and Bootstrap Bundle

**Files:**
- Create: `tools/yassin_commander/config/windows-mcp-policy.json`
- Create: `tools/yassin_commander/config/versions.json`
- Create: `tools/yassin_commander/bootstrap/install.ps1`
- Create: `tools/yassin_commander/bootstrap/register-logon-task.ps1`
- Create: `tools/yassin_commander/bootstrap/uninstall.ps1`
- Create: `tools/yassin_commander/bootstrap/README.md`
- Test: `tools/yassin_commander/bootstrap/tests/Bootstrap.Tests.ps1`

**Interfaces:**
- Install root: `C:\ProgramData\YASSINCommander`.
- Runner root: `C:\actions-runner`.
- Audit root: `C:\ProgramData\YASSINCommander\audit`.
- Artifact scratch root: `C:\ProgramData\YASSINCommander\work`.

- [ ] **Step 1: Add version manifest tests**
  - Assert windows-mcp-server v1.4.0 URL + SHA.
  - Assert actions runner v2.338.0 Windows x64 URL + SHA.
  - Assert install script refuses hash mismatch.

- [ ] **Step 2: Write bootstrap**
  - Create directories with user-only/admin ACLs appropriate to the logged-in owner account.
  - Download pinned Windows MCP zip and verify SHA-256 before extraction.
  - Install bridge EXE from a locally supplied verified build artifact; do not download mutable `main` binaries.
  - Validate Windows MCP policy using `windows-mcp-server.exe policy validate`.
  - Do not accept/store GitHub registration token in files or command history generated by the installer.

- [ ] **Step 3: Register interactive runner startup**
  - Use Task Scheduler **At logon** for the intended Windows user.
  - Start `C:\actions-runner\run.cmd` only in the interactive session.
  - Do not install the runner as SYSTEM/service for GUI mode.
  - Provide a separate stop/kill script.

- [ ] **Step 4: Run PowerShell tests on a Windows CI/VM environment and commit**
  - Commit: `feat(yc): add pinned Windows bootstrap and policy`.

---

### Task 8: Private Control Repository Template and Workflow

**Files:**
- Create: `tools/yassin_commander/control-repo-template/.github/workflows/yc-issue-dispatch.yml`
- Create: `tools/yassin_commander/control-repo-template/.github/ISSUE_TEMPLATE/yc-job.yml`
- Create: `tools/yassin_commander/control-repo-template/README.md`
- Create: `tools/yassin_commander/control-repo-template/SECURITY.md`
- Create: `tools/yassin_commander/control-repo-template/scripts/post-result.ps1`
- Test: `tools/yassin_commander/control-repo-template/tests/workflow_contract_test.py`

**Interfaces:**
- Trigger: Issue opened/reopened/labeled.
- Runner selector: `[self-hosted, windows, x64, yassin-commander]`.
- GitHub permissions: `contents: read`, `issues: write`, all others `none` unless Actions artifact upload requires platform-internal scope.
- Workflow invokes only the preinstalled local bridge by absolute path.

- [ ] **Step 1: Write workflow contract tests**
  - No `pull_request` or `pull_request_target` trigger.
  - No checkout of Issue/PR-controlled refs.
  - No `Invoke-Expression`, `iex`, `cmd /c <issue text>`, dynamic YAML generation, or shell interpolation of Issue body.
  - Runs only on the dedicated YASSIN labels.
  - Calls `yc-bridge execute --event $env:GITHUB_EVENT_PATH ...`.
  - Comments back only the bridge-produced redacted summary.
  - Uploads only the bridge output artifact directory.

- [ ] **Step 2: Implement workflow template**
  - Keep issue body out of `run:` expressions entirely.
  - Use environment variables only for fixed local paths and GitHub-provided metadata.
  - Pin official artifact action to an immutable commit SHA selected during implementation.

- [ ] **Step 3: Implement result posting**
  - Parse `result.json` as JSON.
  - POST comment through GitHub REST with `GITHUB_TOKEN`.
  - Never include raw stderr/stdout.
  - Add `yc-done` or `yc-failed` labels only after posting the bounded result.

- [ ] **Step 4: Run tests and commit**
  - Commit: `feat(yc): add private control repository workflow template`.

---

### Task 9: CI, Security Checks, and Reproducible Windows Build

**Files:**
- Create: `.github/workflows/yassin-commander-ci.yml`
- Create: `tools/yassin_commander/Makefile`
- Create: `tools/yassin_commander/SECURITY.md`
- Create: `tools/yassin_commander/README.md`

**Interfaces:**
- Produces: tested Windows amd64 `yc-bridge.exe` artifact + SHA-256 manifest.
- CI never connects to YASSIN.

- [ ] **Step 1: Add CI gates**
  - `go test ./...`
  - `go vet ./...`
  - `go test -race ./...` where supported.
  - `go build -trimpath -ldflags="-s -w" -o dist/yc-bridge.exe ./cmd/yc-bridge`.
  - Generate SHA-256.
  - Scan committed files for token/key patterns.
  - Parse workflow template contract tests.

- [ ] **Step 2: Add dependency/security checks**
  - Verify `go.sum` is clean.
  - Run `govulncheck ./...` in CI.
  - Document that windows-mcp-server itself intentionally has full user-context access and the bridge policy is a guardrail, not a sandbox.

- [ ] **Step 3: Commit**
  - Commit: `ci(yc): add reproducible bridge build and security gates`.

---

### Task 10: One-Time Private Repository + YASSIN Bootstrap

**External state created:** GitHub private repository `yassenjabal-jpg/YASSIN-Commander-Control`; self-hosted runner registration on YASSIN.

**Interfaces:**
- Consumes: release artifact from Task 9 and template from Task 8.
- Produces: online runner labeled `yassin-commander` with no access from public repositories.

- [ ] **Step 1: Create the private repository**
  - Visibility: Private.
  - No outside collaborators.
  - Disable repository forking where account settings permit.
  - Copy only the reviewed control-repo template files.
  - Create label `yc-job`.

- [ ] **Step 2: Run one-time bootstrap on YASSIN**
  - Execute the reviewed `install.ps1` locally or through another already-authorized human remote session.
  - Verify all pinned hashes before installation.

- [ ] **Step 3: Register runner using GitHub's repository-specific one-hour token**
  - Use the exact commands GitHub shows under **Settings -> Actions -> Runners -> New self-hosted runner** for that private repository.
  - Add custom label `yassin-commander`.
  - Do not paste/store the registration token in repository files or chat.

- [ ] **Step 4: Install interactive logon startup**
  - Register scheduled task.
  - Log off/on once.
  - Verify GitHub reports the runner Online.

- [ ] **Step 5: Run `yc-bridge doctor` locally**
  - Expected: config valid, Windows MCP binary hash/version accepted, policy valid, MCP discovery succeeds, audit directory writable.

---

### Task 11: Acceptance Test Sequence on YASSIN

**Files:**
- Create: `tools/yassin_commander/tests/acceptance/ACCEPTANCE.md`
- Create: `tools/yassin_commander/tests/acceptance/jobs/*.json`

**Interfaces:**
- Uses only the private control repository after bootstrap.
- Each test gets a unique `request_id`.

- [ ] **Step 1: System status**
  - Submit `system.status`.
  - Expect machine identity = YASSIN.

- [ ] **Step 2: Allowed filesystem sandbox**
  - List configured sandbox.
  - Write a test text file.
  - Read it back and compare exact contents.

- [ ] **Step 3: Denied filesystem path**
  - Request a forbidden credential/browser/SSH-secret path.
  - Expect policy denial and no artifact.

- [ ] **Step 4: Screenshot**
  - With desktop unlocked, capture screenshot.
  - Expect Actions artifact; no repository commit.

- [ ] **Step 5: GUI action**
  - Launch a harmless app such as Notepad.
  - Snapshot accessibility tree.
  - Type fixed test text.
  - Verify expected control/text.
  - Close the app.

- [ ] **Step 6: Locked-session denial**
  - Lock desktop.
  - Submit UI action.
  - Expect `INTERACTIVE_SESSION_UNAVAILABLE`.

- [ ] **Step 7: Malformed/injection payload**
  - Submit payload containing PowerShell/workflow expression strings and malformed variants.
  - Expect fail-closed validation; no shell invocation.

- [ ] **Step 8: Kill switch / runner stop**
  - Stop local runner.
  - Verify remote jobs cannot execute.
  - Restart at logon and verify recovery.

- [ ] **Step 9: Audit verification**
  - Run `yc-bridge verify-audit`.
  - Verify chain.
  - Tamper with a copy and confirm verification fails.

- [ ] **Step 10: Final security review**
  - Search Issue comments, workflow logs, artifacts, local audit, and repository history for tokens/secrets.
  - Acceptance requires zero secret leakage.

- [ ] **Step 11: Commit acceptance evidence**
  - Commit only sanitized acceptance summary to `UniversalCouncil`; never commit screenshots, secrets, runner tokens, or machine-private paths beyond approved generic roots.
  - Commit: `test(yc): record YASSIN Commander acceptance evidence`.

## Execution Order

Tasks 1-3 establish the trust boundary and must complete first. Task 4 adds MCP transport only after validation/audit exist. Tasks 5-6 expose the bounded execution surface. Tasks 7-9 create installation and transport packaging. Task 10 is the one-time machine bootstrap. Task 11 is the only point where the system is declared usable.

## Stop Conditions

Stop implementation and do not proceed to YASSIN bootstrap if any of these occur:
- The bridge requires an inbound listener.
- The private control repository cannot be restricted to YASSIN's runner.
- Any workflow path allows Issue/PR text to become executable shell text.
- Required Windows MCP actions cannot be constrained by bridge policy.
- A test shows credential/token leakage.
- GUI execution requires SYSTEM/service mode.
- The pinned upstream binary hash cannot be verified.
