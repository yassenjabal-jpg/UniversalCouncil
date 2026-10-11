# Work Environment Capability Review - 2026-10-11

Status: GO_FOR_SANDBOX_PILOT
Owner: HR & Capability Director
Decision scope: Work Environment Hardening v1 candidate toolchain
Spec: `docs/superpowers/specs/2026-10-11-work-environment-hardening-v1-design.md`
Plan: `docs/superpowers/plans/2026-10-11-work-environment-hardening-v1.md`

## Evidence standard

This review applies the capability-scouting gates in `company/config/capability_scouting.json`:

`HR_DISCOVERY -> SECURITY_REVIEW -> ARCHITECTURE_AND_DUPLICATION_REVIEW -> COUNCIL_REVIEW -> SANDBOX_PILOT -> OWNER_ADOPTION_DECISION`.

Catalog visibility is not capability proof. Unknown facts remain UNKNOWN. Tool installation, authentication, permission change, and external writes remain separately governed.

## Gap summary

The audit identified material gaps rather than a generic desire for more tools:

- CI can be bypassed by direct pushes to unprotected `main`.
- GitHub connector permission is broader than required.
- no branch-coverage measurement or non-regression gate exists;
- no repository lint/format gate exists;
- Python 3.12 CI and Python 3.13 host behavior are not jointly verified;
- Linear is connected but not used as the durable work tracker;
- engineering-tool authority is not represented in the capability registry;
- CodeQL/security feature state is not durable evidence;
- repository branch hygiene is not classified.

These gaps satisfy `RECURRING_TOOL_FAILURE`, `SLOW_OR_HIGH_FRICTION_WORKFLOW`, `SECURITY_OR_COST_REGRESSION`, and `EXTERNAL_CAPABILITY_ADVANCE` triggers.

## Candidate 1 - Ruff 0.17.0

- gap_id: `WEH-RUFF-001`
- candidate_name: `Ruff 0.17.0`
- source_url_or_identifier: `astral-sh/ruff@0.17.0`; official repository and documentation
- capability_added: deterministic Python lint plus changed-file format verification
- existing_capability_overlap: partial; replaces the need for separate Flake8/Black/isort adoption in v1 rather than adding all of them
- maintenance_signal: active; official package metadata reports version 0.17.0 and project status Production/Stable
- license_or_terms: MIT
- install_or_connection_method: pinned pip package inside the isolated `.venv-hardening` environment; CI installs the same exact version
- permissions_required: local read/write access to repository files when format is explicitly invoked; no account authorization
- data_access: local repository source files only
- external_write_capable: false
- cost_model: free/open source; no paid service dependency
- security_risks: Python package supply-chain risk; formatter can modify files when invoked without `--check`
- rollback_plan: remove the dev dependency/config and revert the Ruff gate commit; delete isolated venv
- sandbox_test: run lint and changed-file-only formatter inside feature worktree before PR
- success_metric: deterministic lint passes locally and in CI with no repository-wide formatting churn
- kill_trigger: supply-chain concern, repeated false positives, or materially disruptive formatting churn
- version_or_commit_pin: `0.17.0`

Decision: GO_FOR_SANDBOX_PILOT.

## Candidate 2 - coverage.py 7.16.2

- gap_id: `WEH-COVERAGE-001`
- candidate_name: `coverage.py 7.16.2`
- source_url_or_identifier: `coveragepy/coveragepy@7.16.2`; official 7.16.2 documentation
- capability_added: line and branch-coverage measurement for the existing unittest suite
- existing_capability_overlap: complementary; unittest proves outcomes while coverage reveals unexercised paths
- maintenance_signal: active; official 7.16.2 documentation identifies release 7.16.2 dated 2026-09-27
- license_or_terms: Apache-2.0
- install_or_connection_method: pinned pip package inside isolated venv and CI
- permissions_required: local process execution and read/write of coverage data files
- data_access: local Python code execution and repository source paths
- external_write_capable: false
- cost_model: free/open source
- security_risks: executes the repository test suite under instrumentation; package supply-chain risk
- rollback_plan: remove coverage dependency, baseline file, and gate while preserving raw evidence if useful
- sandbox_test: generate branch coverage in the feature worktree and compare the ratchet against `origin/main`
- success_metric: branch coverage is measurable and touched legacy runtime files cannot regress; new runtime files target 95% line coverage
- kill_trigger: unstable metrics, false blocking caused by measurement artifacts, or incompatible runtime behavior
- version_or_commit_pin: `7.16.2`

Decision: GO_FOR_SANDBOX_PILOT.

## Candidate 3 - GitHub CodeQL Action v4

- gap_id: `WEH-CODEQL-001`
- candidate_name: `GitHub CodeQL Action v4`
- source_url_or_identifier: `github/codeql-action`
- capability_added: GitHub-hosted static security analysis for Python on PRs and `main`
- existing_capability_overlap: complementary to source review/VibeSec; it does not replace human or governance review
- maintenance_signal: active; v4 annotated tag was observed on 2026-10-11 and resolves to commit `24c54180a607b1449ed407dd24f251e4e9147c8d`
- license_or_terms: MIT
- install_or_connection_method: committed GitHub Actions workflow pinned to full commit SHA
- permissions_required: `contents: read`, `security-events: write`; package read only when required by workflow
- data_access: repository source and GitHub code-scanning upload channel
- external_write_capable: true, but only the GitHub security-events result upload is authorized by the workflow permission
- cost_model: repository/account dependent; no new paid tool is approved by this review
- security_risks: action supply-chain risk; workflow permission misconfiguration; provider/account feature availability
- rollback_plan: revert/remove `.github/workflows/codeql.yml`
- sandbox_test: run the pinned workflow on the hardening PR and require an observed successful baseline before treating CodeQL as a merge check
- success_metric: stable `CodeQL Python` result on PR and post-merge `main`
- kill_trigger: provider incompatibility, unstable action behavior, unjustified permission expansion, or repeated false blocking
- version_or_commit_pin: `24c54180a607b1449ed407dd24f251e4e9147c8d`

Decision: GO_FOR_SANDBOX_PILOT. The action is not an enforced security capability until a remote run proves it.

## Candidate 4 - Fullstack Dev Kit activation

- gap_id: `WEH-DEVKIT-001`
- candidate_name: `Fullstack Dev Kit`
- source_url_or_identifier: `skills://plugins/fullstack-dev-kit/`
- capability_added: issue-to-plan-to-tests-to-review-to-PR orchestration
- existing_capability_overlap: orchestration over existing GitHub/Linear capabilities; not a new source of truth
- maintenance_signal: installed skill is callable in the current ChatGPT environment
- license_or_terms: UNKNOWN from the installed skill metadata reviewed in this task
- install_or_connection_method: no new plugin install; repository-local `.claude/dev-kit.json` only
- permissions_required: inherits the separately governed Linear/GitHub connector actions it invokes
- data_access: issue metadata, repository context, and configured tracker/PR host
- external_write_capable: indirect/orchestrated only; no authority expansion is granted by activation
- cost_model: already available in the current environment
- security_risks: orchestration could make writes easier to invoke if connector permissions are too broad; its GitHub PR helper assumes `gh` in some flows
- rollback_plan: remove/revert `.claude/dev-kit.json`
- sandbox_test: use repository config only; GitHub/Linear connectors remain the actual execution channels
- success_metric: work items, PR evidence, and follow-ups become traceable without adding a second tracker
- kill_trigger: repeated unsupported CLI handoffs or duplicated workflow bureaucracy
- version_or_commit_pin: installed plugin skill version is UNKNOWN; repository config is committed and reviewable

Decision: GO_FOR_SANDBOX_PILOT with connector-first adaptation and no `gh` installation in v1.

## Candidate 5 - Linear workflow activation

- gap_id: `WEH-LINEAR-001`
- candidate_name: `Linear connected workspace`
- source_url_or_identifier: connected workspace `yassin`, team `YAS`
- capability_added: durable work intent/status, acceptance criteria, PR linkage, and follow-up tracking
- existing_capability_overlap: replaces chat-only/backlog-memory workflow; does not replace repository technical truth
- maintenance_signal: connected connector and readable workspace observed during this review
- license_or_terms: vendor service terms; no new purchase approved here
- install_or_connection_method: already connected; create one bounded project and work items
- permissions_required: connected-app read/write for work tracker records
- data_access: tracker project/issue metadata supplied for this project
- external_write_capable: true for tracker records
- cost_model: existing connected service; no new spend authorized
- security_risks: accidental tracker mutation or duplication; drift if technical specs are copied into Linear
- rollback_plan: archive/close the project/issues; repository remains canonical
- sandbox_test: create exactly one `Universal Council` project and idempotent hardening issues, then read them back
- success_metric: material engineering work is traceable and no duplicate exact-title hardening issues are created
- kill_trigger: tracker becomes a duplicate source of technical truth or adds more manual overhead than it removes
- version_or_commit_pin: not applicable to SaaS connector; connection state is re-read before writes

Decision: GO_FOR_SANDBOX_PILOT.

## Security Review - VibeSec/tool-trust pass

Verdict: PASS_WITH_BOUNDARIES.

- No candidate requires session cookies, browser-debugger access, primary-browser extraction, arbitrary credentials, authenticated social access, payments, publication, or messaging.
- Ruff and coverage are limited to the isolated worktree/venv during pilot.
- CodeQL gets only repository read plus security-event upload permissions required by advanced setup; it receives no repository administration grant from this design.
- Fullstack Dev Kit is coordination logic, not an authorization boundary.
- Linear and GitHub writes remain connector-governed.
- Current GitHub ChatGPT connector state is broader than desired (`Allow all actions`); that is an existing risk and remains a P0 hardening item. It does not authorize any additional candidate permission.
- Moving-branch installs are forbidden; package versions and GitHub Actions are pinned.
- Unknown license/version facts are not promoted to verified.

Security blocker count: 0 for sandbox pilot.
Security condition: GitHub write authority must be reduced before final v1 acceptance.

## Architecture and Duplication Review

Verdict: PASS.

- Ruff is selected as the single v1 lint/format engine. Black, Flake8 and isort are explicitly rejected as duplicate candidates for this scope.
- coverage.py fills a measurement gap and does not replace unittest.
- CodeQL adds static security evidence and does not replace VibeSec, Council challenge, or source review.
- Linear becomes the single work tracker. Jira/ClickUp are rejected for v1.
- Git remains the single canonical technical/governance source. Notion/GitBook mirrors are rejected.
- Fullstack Dev Kit coordinates the existing workflow and is prohibited from becoming an authority source.
- No runtime service or production telemetry need justifies Datadog/Vanta in v1.

Rejected duplicates: `Black`, `Flake8`, `isort`, `Jira`, `ClickUp`, `Notion-as-canonical`, `GitBook-as-canonical`, `Datadog`, `Vanta`.

## Council Review

### Evidence
GO. The gaps are directly observed in repository/connector/host state. Candidate identities are pinned where a pin is meaningful. Remote provider behavior remains unverified until the PR pilot.

### Software / Architecture
GO. The toolchain is small and responsibility-separated: unittest for behavior, coverage for execution visibility, Ruff for lint/format, CodeQL for static security, Linear for work tracking.

### Security
GO_WITH_CONDITION. CodeQL permissions are narrow enough for the pilot and action pins are immutable. Existing GitHub connector `Allow all actions` is unacceptable as a final state.

### Execution
GO. The isolated worktree and staged commits make rollback practical. The suite is small enough that CI should run broadly instead of depending on fragile path filters.

### Risk
GO_WITH_CONDITION. The highest operational risk is enabling main protection before the actual remote check names are proven. Rules must therefore be applied only after successful PR runs.

### Human / User
GO. The proposal reduces repeated manual reconstruction from chat history and makes blocked work visible without adding multiple trackers.

### Value
GO. The package targets verified bottlenecks rather than adding speculative platforms.

### Red Team - protected dissent
DISSENT RETAINED: repository ruleset/security administration may be unavailable through the current connector. If that happens, repository-side hardening can be correct while the external bypass remains open. The system must report `ADMIN_BLOCKED` and must not call v1 fully accepted or create the milestone tag.

### Synthesis
Council decision: GO_FOR_SANDBOX_PILOT. There is no security or architecture blocker to executing the feature-branch pilot. Final adoption remains conditional on test/CI evidence and external enforcement readback.

## Sandbox boundary

The sandbox is the existing isolated branch/worktree `feat/work-environment-hardening-v1` plus its local `.venv-hardening`.

No candidate reaches `main` before:

1. local tests and quality gates pass;
2. PR CI runs remotely;
3. whole-branch review is complete;
4. merge criteria are satisfied.

## Owner adoption decision

Owner instruction: adopt and execute Work Environment Hardening v1 with high precision, using Native execution.

This authorizes the sandbox pilot and the planned repository/connector changes, but it does not waive security blockers, irreversible-operation stops, or truthful `ADMIN_BLOCKED` reporting.

## Gate result

- HR_DISCOVERY: PASS
- SECURITY_REVIEW: PASS_WITH_BOUNDARIES
- ARCHITECTURE_AND_DUPLICATION_REVIEW: PASS
- COUNCIL_REVIEW: GO_FOR_SANDBOX_PILOT
- SANDBOX_PILOT: AUTHORIZED_IN_ISOLATED_WORKTREE
- OWNER_ADOPTION_DECISION: APPROVED, FINAL ACCEPTANCE STILL EVIDENCE-GATED

Overall: **GO_FOR_SANDBOX_PILOT**.
