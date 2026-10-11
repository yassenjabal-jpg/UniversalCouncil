# Work Environment Hardening v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert Universal Council's development environment into a repository-governed, traceable, measurable engineering control plane with enforced CI, quality/security gates, Linear work tracking, and explicit tool authority boundaries.

**Architecture:** The repository remains canonical for code, governance, configuration, quality policy, and durable evidence. Linear tracks work intent/status, GitHub delivers branches/PR/CI, and ChatGPT/host tools operate under explicit read/write/execute authority records. The implementation is staged so every repository commit remains independently testable and external settings are changed only after the repository-side controls that justify them exist.

**Tech Stack:** Python 3.12/3.13, unittest, Ruff 0.17.0, coverage.py 7.16.2, GitHub Actions, GitHub CodeQL, Linear, JSON/TOML, native Git, existing ChatGPT connectors.

**Spec:** `docs/superpowers/specs/2026-10-11-work-environment-hardening-v1-design.md`

## Global Constraints

- Baseline is `main@bfc08b5ea98f352f595029f62fcefe6cc93395fb`.
- Repository state outranks conversation memory.
- Keep `unittest`; do not migrate to pytest in v1.
- Supported Python versions are exactly 3.12 and 3.13 for v1.
- Add only Ruff and coverage.py as new Python development dependencies.
- Pin Ruff to `0.17.0` and coverage.py to `7.16.2`.
- Pin GitHub Actions to full commit SHAs, retaining release comments.
- `actions/checkout@v7` commit: `3d3c42e5aac5ba805825da76410c181273ba90b1`.
- `actions/setup-python@v7` commit: `5fda3b95a4ea91299a34e894583c3862153e4b97`.
- `github/codeql-action@v4` commit: `24c54180a607b1449ed407dd24f251e4e9147c8d`.
- No authenticated-social, OpenCLI, cookie, browser-debugger, or credential expansion for Agent Reach.
- No Jira, ClickUp, Datadog, Vanta, Coda, Dropbox Dash, MongoDB Atlas, pytest, mypy, pre-commit, uv, Black, Flake8, or isort adoption in v1.
- No secret, token, cookie, browser-session material, or credential may be committed to the repository.
- GitHub plugin target permission is `ask_before_writes`, not `full_access`.
- Remote shell execution is high-impact authority and must never be described as backend-enforced when it is only policy-governed.
- A provider/admin limitation is recorded as `ADMIN_BLOCKED` or `UNAVAILABLE`; it is never reported as PASS.
- All behavioral/runtime implementation changes use RED -> GREEN tests.
- Do not delete a remote branch until ancestry/equivalence evidence classifies it as safe to remove.
- Do not merge until local verification, PR CI, and code review are green.
- Do not create the milestone tag until the integrated main branch passes its post-merge workflow.

## File Structure

**Create**
- `pyproject.toml` - Python support, pinned development dependencies, Ruff and coverage configuration.
- `.claude/dev-kit.json` - Fullstack Dev Kit adapter configuration for Linear/GitHub/Python.
- `.github/workflows/codeql.yml` - repository-controlled CodeQL scan.
- `tools/change_scope.py` - cross-platform changed-file discovery for format and coverage gates.
- `tools/coverage_gate.py` - branch-coverage baseline/ratchet evaluator.
- `company/config/coverage_baseline.json` - measured production coverage baseline.
- `company/config/tool_authority.json` - engineering tool authority registry.
- `company/runtime/tool_authority.py` - deterministic validation/query helpers for tool authority.
- `company/tests/test_work_environment_hardening.py` - CI, dependency, Dev Kit, action-pin, and CodeQL contract tests.
- `company/tests/test_change_scope.py` - changed-file scope unit tests.
- `company/tests/test_coverage_gate.py` - coverage ratchet unit tests.
- `company/tests/test_tool_authority.py` - authority registry and fail-closed policy tests.
- `company/docs/WORK_ENVIRONMENT_CAPABILITY_REVIEW_2026-10-11.md` - HR, Security, Architecture/Duplication, and Council adoption-gate record for the v1 toolchain.
- `company/docs/WORK_ENVIRONMENT_HARDENING_ACCEPTANCE.md` - acceptance contract and evidence checklist.
- `company/docs/evidence/tool_permissions_2026-10-11.json` - structured before/after plugin-permission receipt.
- `company/docs/BRANCH_HYGIENE_2026-10-11.md` - branch classification evidence.

**Modify**
- `.github/workflows/company-stage0.yml` - main/PR triggers, immutable action pins, stable jobs, quality/coverage gates.
- `tools/validate_config.py` - validate tool authority and hardening invariants.
- `company/README.md` - document the engineering control plane and source-of-truth boundaries.
- `company/PEOPLE_AND_CAPABILITY.md` - record engineering-tool authority as an HR capability concern without expanding HR authority.
- `skills/universal-council/SKILL.md` - compact rule for engineering capability evidence and no metadata-only PASS.

**External state**
- Linear project and backlog.
- GitHub ChatGPT plugin permission.
- GitHub branch/ruleset state.
- GitHub repository security feature state.
- Remote branches proven safe to delete.
- Final PR/merge and optional milestone tag.

## Review Focus

1. **A workflow edit reintroduces direct-main bypass or a stale branch trigger.** Expected: contract tests fail unless PR plus push-to-main triggers remain present; Task 2 owns this test.
2. **A workflow/action reference drifts back to a mutable tag.** Expected: contract tests reject any `uses:` line for checkout/setup-python/CodeQL that is not the approved 40-character SHA; Tasks 2 and 6 own these tests.
3. **Coverage ratchet sees a changed legacy file below 95% but not below its baseline.** Expected: PASS because v1 requires non-regression for legacy files; a new production file below 95% must FAIL; Task 5 owns both tests.
4. **A tool authority record claims write/execute capability without an explicit approval boundary or enforcement truth.** Expected: registry validation rejects it; Task 7 owns this test.
5. **An external setting cannot be changed because the connector lacks admin authority.** Expected: record `ADMIN_BLOCKED` with readback evidence and continue all independent tasks; never mark the acceptance item PASS; Tasks 10 and 14 own this behavior.

## Rollback Map

- CI trigger/action-pin change: revert Task 2 commit; no runtime data migration exists.
- Ruff/pyproject adoption: revert Task 3; remove only the isolated `.venv-hardening` environment locally.
- Changed-file formatter scope: revert Task 4; no repository-wide formatting is performed.
- Coverage ratchet: revert Task 5 gate/config while retaining raw baseline evidence if useful.
- CodeQL: revert/remove `.github/workflows/codeql.yml`; no runtime code depends on it.
- Tool authority registry: revert Task 7 files/validator changes; this does not alter connector permissions by itself.
- Dev Kit config: remove/revert `.claude/dev-kit.json`; tracker data remains intact.
- GitHub plugin permission: restore only by a fresh explicit Owner decision; rollback is not automatic.
- Linear project/issues: archive or close them; never delete technical truth from Git to make tracker state look clean.
- GitHub ruleset/security settings: revert only through an authorized admin-capable channel if they block legitimate recovery.
- Remote branch deletion: prevention is the rollback strategy; only branches classified `DELETE_SAFE` may be deleted.
- Agent Reach: no authority change is planned, so any observed drift blocks completion rather than being normalized.

---

### Task 0: Close HR, Security, Architecture/Duplication, and Council adoption gates

**Files:**
- Create: `company/docs/WORK_ENVIRONMENT_CAPABILITY_REVIEW_2026-10-11.md`

**Interfaces:**
- Consumes: approved spec, HR audit findings, pinned candidate identities, and the existing VibeSec tool-trust contract.
- Produces: a durable GO/NO-GO record that must be GO before Task 3 installs Ruff/coverage or Task 6 activates CodeQL.

- [ ] **Step 1: Build candidate dossiers from authoritative sources**

Create dossiers for:
- Ruff 0.17.0;
- coverage.py 7.16.2;
- GitHub CodeQL Action v4 at commit `24c54180a607b1449ed407dd24f251e4e9147c8d`;
- Fullstack Dev Kit activation using the already-installed plugin;
- Linear workflow activation using the already-connected workspace.

For each dossier record the fields required by `company/config/capability_scouting.json`: gap id, authoritative source, capability added, overlap, maintenance signal, license/terms, install/connection method, permissions, data access, write capability, cost, security risks, rollback, sandbox test, success metric, kill trigger, and version/commit pin where applicable.

Unknown fields stay `UNKNOWN`; do not invent them.

- [ ] **Step 2: Run VibeSec/tool-trust Security Review**

Review supply-chain and permission risk.

Required conclusions:
- Ruff and coverage execute local repository code/files only within the test environment;
- CodeQL workflow receives repository contents and GitHub security-event write permission only for scan upload;
- Dev Kit is orchestration, not new authorization;
- Linear/GitHub connector writes remain separately governed;
- no candidate requires cookies, browser debugger, arbitrary credentials, or authenticated social access.

Record any blocker as `SECURITY_BLOCKED`.

- [ ] **Step 3: Run Architecture and Duplication Review**

Prove:
- Ruff replaces the need for separate Black/Flake8/isort in v1 instead of duplicating them;
- coverage.py supplies a missing metric rather than duplicating unittest;
- CodeQL complements source/security review rather than being represented as a replacement for it;
- Linear is the single work tracker; no Jira/ClickUp parallel tracker;
- Git repository remains canonical; no Notion/GitBook mirror is introduced;
- Fullstack Dev Kit coordinates existing connectors and does not become a new source of truth.

Record `DUPLICATE_REJECTED` for rejected alternatives.

- [ ] **Step 4: Run Council review on the bounded candidate set**

Use relevant voices only: Security, Software/Architecture, Execution, Risk, Human/User, Value, Evidence, Red Team.

Decision must explicitly cover:
- benefit vs added complexity;
- rollback;
- capability overlap;
- likely failure mode;
- whether each candidate changes a material bottleneck.

Protected dissent is preserved in the record.

- [ ] **Step 5: Record Owner decision already supplied in this conversation**

Owner decision: adopt the approved Work Environment Hardening v1 package, subject to the written spec/plan and verification gates.

This does not waive any security blocker discovered in Steps 1-4.

The isolated worktree plus `.venv-hardening` in Tasks 3-8 is the sandbox pilot. No candidate from this gate reaches `main` before local verification, PR CI, and merge review.

- [ ] **Step 6: Commit the gate record**

Only if no candidate needed for the next tasks is blocked.

`git add company/docs/WORK_ENVIRONMENT_CAPABILITY_REVIEW_2026-10-11.md`

`git commit -m "docs: close work environment capability adoption gates"`

---

### Task 1: Establish the tracked hardening workstream in Linear

**Files:**
- No repository file change in this task.
- External: Linear workspace `yassin`, team `YAS`.

**Interfaces:**
- Consumes: approved spec and this plan.
- Produces: one Linear project named `Universal Council` plus traceable issues used by later tasks.

- [ ] **Step 1: Read existing Linear state before writing**

Use Linear connector to list exact project name `Universal Council` and search issues by the titles below.

Expected: reuse matching records if they already exist; do not duplicate.

- [ ] **Step 2: Create or reuse project `Universal Council`**

Project summary: `Repository-governed engineering, capability, and work-environment hardening for Universal Council.`

Associate it with team `YAS`.

- [ ] **Step 3: Create the hardening issues idempotently**

Create or reuse these exact titles, all attached to `Universal Council`:

1. `P0 - Close main branch and CI bypass` - priority Urgent.
2. `P0 - Reduce GitHub connector write authority` - priority Urgent.
3. `P1 - Standardize Python 3.12 and 3.13 development environment` - priority High.
4. `P1 - Add Ruff lint and changed-file format gate` - priority High.
5. `P1 - Add branch coverage baseline and non-regression ratchet` - priority High.
6. `P1 - Add CodeQL and repository security evidence` - priority High.
7. `P1 - Bootstrap Fullstack Dev Kit for Linear and GitHub` - priority High.
8. `P1 - Add engineering tool authority registry` - priority High.
9. `P2 - Classify and clean historical remote branches` - priority Medium.
10. `P2 - Resolve Codex Security callable capability state` - priority Medium.
11. `P2 - Establish milestone tag discipline` - priority Medium.

Each description links the spec path and records the relevant acceptance criterion(s).

- [ ] **Step 4: Read back project and issue count**

Expected: exactly one `Universal Council` project and at least the 11 hardening issues above, with no duplicate exact-title issues created by this run.

- [ ] **Step 5: Record tracker identifiers in the execution log**

No repository commit yet; identifiers are carried forward for PR links and final status updates.

---

### Task 2: Repair core CI triggers, immutable action pins, and stable compatibility jobs

**Files:**
- Create: `company/tests/test_work_environment_hardening.py`
- Modify: `.github/workflows/company-stage0.yml`

**Interfaces:**
- Consumes: approved checkout/setup-python SHAs from Global Constraints.
- Produces: stable jobs named `Quality Gate` and `Python 3.12 Compatibility`, both triggered for PRs and pushes to `main`.

- [ ] **Step 1: Write failing CI contract tests**

In `company/tests/test_work_environment_hardening.py`, add tests with these assertions:

`test_company_workflow_targets_pull_requests_and_main_pushes`
- workflow contains `pull_request:`;
- workflow contains `push:`;
- workflow contains branch `main`;
- workflow does not contain `codex/venture-operating-system-v1`;
- workflow does not contain a `paths:` filter in the core workflow.

`test_company_workflow_uses_immutable_action_pins`
- checkout line contains `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1`;
- setup-python line contains `actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97`;
- no `actions/checkout@v` or `actions/setup-python@v` reference remains.

`test_company_workflow_has_stable_python_jobs`
- text contains `name: Quality Gate`;
- text contains `name: Python 3.12 Compatibility`;
- quality job configures Python `3.13`;
- compatibility job configures Python `3.12`.

- [ ] **Step 2: Run the new tests and verify RED**

Run:
`python -m unittest company.tests.test_work_environment_hardening -v`

Expected: failures for stale push branch, path filters, mutable action refs, and missing stable job names.

- [ ] **Step 3: Modify `.github/workflows/company-stage0.yml` minimally**

Required shape:

- `pull_request:` with no path filter.
- `push: branches: [main]` with no path filter.
- `Quality Gate` on Python 3.13.
- `Python 3.12 Compatibility` on Python 3.12.
- checkout/setup-python use exact pinned SHAs with comments `# v7`.
- For this task only, both jobs run compile, `tools/validate_config.py`, and existing unittest suite. Quality tooling is added in later tasks.

- [ ] **Step 4: Run CI contract plus full baseline locally**

Run:
- `python -m unittest company.tests.test_work_environment_hardening -v`
- `python tools/validate_config.py`
- `python -m compileall -q company tools`
- `python -m unittest discover -s company/tests -v`

Expected: PASS with existing expected integration skip only.

- [ ] **Step 5: Commit**

`git add .github/workflows/company-stage0.yml company/tests/test_work_environment_hardening.py`

`git commit -m "ci: enforce main and pull request verification"`

---

### Task 3: Add deterministic Python metadata and Ruff staged adoption

**Files:**
- Create: `pyproject.toml`
- Modify: `company/tests/test_work_environment_hardening.py`
- Modify: `.github/workflows/company-stage0.yml`

**Interfaces:**
- Consumes: Python support and pinned tool versions from Global Constraints.
- Produces: installable development extras and repository lint configuration.

- [ ] **Step 1: Add failing pyproject contract test**

Add `test_pyproject_pins_supported_python_and_dev_tools`:

Parse with `tomllib` and assert:
- `project.requires-python == ">=3.12,<3.14"`;
- dev extra contains exactly `ruff==0.17.0` and `coverage==7.16.2`;
- Ruff target version is `py312`;
- Ruff lint selection is the conservative set `["E4", "E7", "E9", "F"]`;
- coverage branch mode is true.

- [ ] **Step 2: Run test and verify RED**

Expected: failure because `pyproject.toml` does not exist.

- [ ] **Step 3: Create `pyproject.toml`**

Use:
- project name `universal-council`;
- version `0.3.0`;
- `requires-python = ">=3.12,<3.14"`;
- no runtime dependencies;
- optional `dev` dependencies pinned exactly to Ruff 0.17.0 and coverage 7.16.2;
- Ruff line length 120, target `py312`;
- conservative lint set `E4,E7,E9,F`;
- coverage `branch = true`, source `company/runtime`, omit tests and cache/worktree paths.

- [ ] **Step 4: Create an isolated local verification environment**

In the hardening worktree:

`python -m venv .venv-hardening`

`.venv-hardening\Scripts\python -m pip install --upgrade pip`

Install only the dev dependency list declared in `pyproject.toml`, without packaging/installing the repository itself:

`.venv-hardening\Scripts\python -c "import subprocess,sys,tomllib; d=tomllib.load(open('pyproject.toml','rb'))['project']['optional-dependencies']['dev']; subprocess.check_call([sys.executable,'-m','pip','install',*d])"`

Do not commit the virtual environment; confirm `.gitignore` excludes `.venv*` or add a narrow ignore entry if needed.

- [ ] **Step 5: Run Ruff baseline and fix only high-confidence failures**

Run:
- `.venv-hardening\Scripts\python -m ruff check company tools`

Expected: if violations exist, fix only selected E4/E7/E9/F findings with no broad formatting churn.

Run again until clean.

- [ ] **Step 6: Add Ruff lint to `Quality Gate`**

After setup-python, install the exact dev dependency list by parsing `pyproject.toml` with the same stdlib `tomllib` command used locally, then add:
`python -m ruff check company tools`

Compatibility job installs no quality tools unless its own commands need them; it runs compile/validator/tests only and does not duplicate the lint pass.

- [ ] **Step 7: Run full local verification**

Run with venv Python:
- `python -m ruff check company tools`
- `python -m unittest discover -s company/tests -v`
- `python tools/validate_config.py`

Expected: PASS.

- [ ] **Step 8: Commit**

`git add pyproject.toml .gitignore .github/workflows/company-stage0.yml company tools`

`git commit -m "build: add pinned Python quality tooling"`

---

### Task 4: Add cross-platform changed-file scope for format and coverage gates

**Files:**
- Create: `tools/change_scope.py`
- Create: `company/tests/test_change_scope.py`
- Modify: `.github/workflows/company-stage0.yml`

**Interfaces:**
- Produces:
  - `normalize_paths(paths: list[str]) -> list[str]`
  - `filter_python_files(paths: list[str]) -> list[str]`
  - `git_changed_files(base: str, head: str = "HEAD") -> list[str]`
  - CLI: `python tools/change_scope.py --base <ref> [--python] [--production]`

- [ ] **Step 1: Write failing unit tests**

Cover:
- slash normalization from Windows to repository paths;
- filtering only existing `.py` files;
- `--production` includes only `company/runtime/**/*.py`;
- duplicate paths are removed while preserving sorted deterministic output;
- invalid/missing base ref exits non-zero rather than silently returning no changes.

Use dependency injection/patching for the subprocess call; tests must not require a real temporary git remote.

- [ ] **Step 2: Run tests and verify RED**

`python -m unittest company.tests.test_change_scope -v`

Expected: import failure because module does not exist.

- [ ] **Step 3: Implement `tools/change_scope.py`**

Use `git diff --name-only <base>...<head>` via `subprocess.run(..., shell=False, check=True, text=True)`.

No arbitrary command input is executed; base/head are passed as argv elements.

- [ ] **Step 4: Add changed-file Ruff format verification to `Quality Gate`**

Determine base:
- PR: `origin/${GITHUB_BASE_REF}` after checkout with `fetch-depth: 0`;
- push: event `before` SHA when valid, otherwise `HEAD^1`.

Use `change_scope.py --python` and invoke `python -m ruff format --check` only when the list is non-empty.

Do not run repository-wide format in v1.

- [ ] **Step 5: Format only the changed Python files, inspect, then verify against `origin/main`**

Run:
- `python tools/change_scope.py --base origin/main --python`;
- `python -m ruff format <changed-files>` only for that returned set;
- inspect the diff to confirm formatting-only changes;
- `python -m ruff format --check <changed-files>`.

Expected: only hardening-changed Python files are modified/checked; no repository-wide formatting churn.

- [ ] **Step 6: Commit**

`git add tools/change_scope.py company/tests/test_change_scope.py .github/workflows/company-stage0.yml`

`git commit -m "ci: scope formatting checks to changed Python files"`

---

### Task 5: Measure branch coverage and enforce the non-regression ratchet

**Files:**
- Create: `tools/coverage_gate.py`
- Create: `company/tests/test_coverage_gate.py`
- Create: `company/config/coverage_baseline.json`
- Modify: `.github/workflows/company-stage0.yml`
- Modify: `company/tests/test_work_environment_hardening.py`

**Interfaces:**
- Produces:
  - `file_metrics(coverage_file: dict) -> dict[str, float | None]` with line and branch percentages.
  - `evaluate_coverage(current: dict, baseline: dict, changed_files: list[str], new_file_min: float = 95.0) -> list[str]` returning failure messages.
  - CLI: `python tools/coverage_gate.py --coverage <coverage.json> --baseline <baseline.json> --base <ref>`.

- [ ] **Step 1: Write RED tests for the ratchet**

Tests must prove:
- changed legacy file at 70% with 70% baseline passes even though below 95%;
- changed legacy file at 69.9% with 70% baseline fails;
- new production file at 94.9% line coverage fails;
- new production file at 95% line coverage passes if branch metric does not regress from an applicable baseline;
- a file with branches reports branch percentage separately;
- missing current coverage for a changed production file fails closed;
- malformed baseline fails closed.

- [ ] **Step 2: Run and verify RED**

`python -m unittest company.tests.test_coverage_gate -v`

Expected: import failure.

- [ ] **Step 3: Implement `tools/coverage_gate.py`**

Read coverage.py JSON only; do not shell out from metric functions.

For legacy files:
- required line percentage = stored baseline line percentage;
- required branch percentage = stored baseline branch percentage when branches exist.

For new `company/runtime/**/*.py` files:
- line minimum = 95.0;
- branch percentage must be reported but v1 does not impose a fabricated percentage when the file has zero branches.

Use a numerical tolerance of 0.01 percentage points to avoid representation noise.

- [ ] **Step 4: Generate the baseline from current runtime behavior**

With the venv:
- `python -m coverage erase`
- `python -m coverage run --branch -m unittest discover -s company/tests`
- `python -m coverage json -o build/coverage-baseline-raw.json`

Generate `company/config/coverage_baseline.json` only for `company/runtime/**/*.py`, with:
- source commit `bfc08b5ea98f352f595029f62fcefe6cc93395fb`;
- generated date `2026-10-11`;
- per-file line percentage;
- per-file branch percentage or null when no branches.

Because Tasks 2-4 do not change `company/runtime`, this baseline remains semantically the baseline runtime.

- [ ] **Step 5: Add coverage commands to `Quality Gate`**

Run:
- `python -m coverage erase`
- `python -m coverage run --branch -m unittest discover -s company/tests`
- `python -m coverage json -o build/coverage.json`
- `python tools/coverage_gate.py --coverage build/coverage.json --baseline company/config/coverage_baseline.json --base "$BASE_REF"`

- [ ] **Step 6: Extend hardening contract test**

Assert workflow invokes `coverage run --branch` and `tools/coverage_gate.py`.

- [ ] **Step 7: Run local gate against `origin/main`**

Expected: PASS; no production runtime regression has been introduced yet.

- [ ] **Step 8: Commit**

`git add tools/coverage_gate.py company/tests/test_coverage_gate.py company/config/coverage_baseline.json .github/workflows/company-stage0.yml company/tests/test_work_environment_hardening.py`

`git commit -m "test: add branch coverage non-regression gate"`

---

### Task 6: Add repository-controlled CodeQL with immutable pins

**Files:**
- Create: `.github/workflows/codeql.yml`
- Modify: `company/tests/test_work_environment_hardening.py`

**Interfaces:**
- Produces: stable CodeQL job named `CodeQL Python`.

- [ ] **Step 1: Add RED CodeQL contract test**

`test_codeql_workflow_is_python_scoped_and_immutably_pinned` asserts:
- workflow exists;
- triggers include PR and push to `main`;
- language is `python`;
- checkout uses approved checkout SHA;
- every `github/codeql-action/*` reference uses commit `24c54180a607b1449ed407dd24f251e4e9147c8d`;
- job name is `CodeQL Python`;
- no `@v4` action reference remains.

- [ ] **Step 2: Run and verify RED**

Expected: missing CodeQL workflow.

- [ ] **Step 3: Create `.github/workflows/codeql.yml`**

Use:
- `pull_request`;
- `push: branches: [main]`;
- weekly schedule;
- `permissions: security-events: write, packages: read, contents: read`;
- checkout pinned SHA;
- CodeQL init/analyze pinned SHA with `languages: python`;
- stable job name `CodeQL Python`.

- [ ] **Step 4: Run contract tests**

Expected: PASS locally. Remote CodeQL status is not claimed until PR execution.

- [ ] **Step 5: Commit**

`git add .github/workflows/codeql.yml company/tests/test_work_environment_hardening.py`

`git commit -m "security: add pinned CodeQL workflow"`

---

### Task 7: Add engineering tool authority registry and deterministic validation

**Files:**
- Create: `company/config/tool_authority.json`
- Create: `company/runtime/tool_authority.py`
- Create: `company/tests/test_tool_authority.py`
- Modify: `tools/validate_config.py`
- Modify: `company/README.md`
- Modify: `company/PEOPLE_AND_CAPABILITY.md`
- Modify: `skills/universal-council/SKILL.md`

**Interfaces:**
- Produces:
  - `validate_registry(cfg: dict) -> bool`, raising `ToolAuthorityError` on invalid state.
  - `get_capability(cfg: dict, operation: str) -> dict`.
  - `requires_explicit_approval(record: dict) -> bool`.
  - `ToolAuthorityError(ValueError)`.

- [ ] **Step 1: Write RED authority tests**

Registry must contain exactly these minimum operations:
- `github.read`
- `github.write`
- `github.merge`
- `linear.read`
- `linear.write`
- `remote_shell.read`
- `remote_shell.execute`
- `agent_reach.public_read`
- `browser.authenticated`
- `external.publish`

Every record requires:
`id, provider, operation, classification, evidence_level, authentication_class, effect, approval_policy, allowed_scope, prohibited_scope, last_verified_at, review_trigger, source_or_pin, enforcement`.

Allowed evidence levels:
`ADVERTISED, METADATA_OBSERVED, BYTES_VERIFIED, SCRIPT_TESTED, HOST_INVOKED, BOUNDARY_ENFORCED`.

Tests reject:
- duplicate operations;
- WRITE or EXECUTE effect with `READ_ALLOWED`;
- WRITE/EXECUTE record missing prohibited scope;
- `POLICY_ENFORCED_ONLY` record represented as `BOUNDARY_ENFORCED` by an `enforcement_evidence` claim;
- authenticated browser operation not classified `BLOCKED` in v1;
- `external.publish` not owner-gated/blocked;
- Agent Reach public-read record with authenticated scope.

- [ ] **Step 2: Run tests and verify RED**

Expected: missing module/config.

- [ ] **Step 3: Implement `company/runtime/tool_authority.py`**

Fail closed on unknown enum values, duplicate IDs/operations, missing fields, and unsafe effect/approval combinations.

Do not implement connector interception; this module validates governance evidence only.

- [ ] **Step 4: Create `company/config/tool_authority.json`**

Required state:
- GitHub read: AVAILABLE, CONNECTED_APP, READ, READ_ALLOWED, enforcement CONNECTOR_POLICY.
- GitHub write/merge: AVAILABLE, CONNECTED_APP, WRITE, ASK_BEFORE_WRITE, enforcement CONNECTOR_POLICY.
- Linear read: AVAILABLE, CONNECTED_APP, READ, READ_ALLOWED.
- Linear write: AVAILABLE, CONNECTED_APP, WRITE, ASK_BEFORE_WRITE.
- Remote shell read: AVAILABLE, HOST_SESSION, READ, OWNER_EXPLICIT, enforcement POLICY_ENFORCED_ONLY.
- Remote shell execute: OWNER_GATED, HOST_SESSION, EXECUTE, OWNER_EXPLICIT, enforcement POLICY_ENFORCED_ONLY.
- Agent Reach public read: AVAILABLE, PUBLIC_ONLY, READ, READ_ALLOWED, source pin `94f06c1969dfc1834001269d79d3ad0972d9dee6`, enforcement GATEWAY_ENFORCED.
- Authenticated browser: BLOCKED.
- External publish: BLOCKED unless separately owner-granted by another governed subsystem.

Use `2026-10-11` observed time and explicit review triggers rather than pretending permissions never expire.

- [ ] **Step 5: Extend `tools/validate_config.py`**

Load registry and invoke `validate_registry`.

Also assert Agent Reach pin/blocked-authenticated-social invariants remain exactly as before.

Update final validator output to include `tool authority registry enforced`.

- [ ] **Step 6: Update governance docs**

Document:
- catalog visibility is not capability proof;
- write/execute authority must have explicit boundaries;
- remote shell is high-impact;
- no HR authority expansion;
- no metadata-only security PASS.

- [ ] **Step 7: Run tests and validators**

Run:
- `python -m unittest company.tests.test_tool_authority -v`
- `python tools/validate_config.py`
- full suite.

Expected: PASS.

- [ ] **Step 8: Commit**

`git add company/config/tool_authority.json company/runtime/tool_authority.py company/tests/test_tool_authority.py tools/validate_config.py company/README.md company/PEOPLE_AND_CAPABILITY.md skills/universal-council/SKILL.md`

`git commit -m "feat: govern engineering tool authority"`

---

### Task 8: Bootstrap Fullstack Dev Kit from measured coverage and existing Linear/GitHub connectors

**Files:**
- Create: `.claude/dev-kit.json`
- Modify: `company/tests/test_work_environment_hardening.py`

**Interfaces:**
- Consumes: Task 5 coverage baseline, Linear team `YAS`.
- Produces: deterministic Dev Kit adapter configuration.

- [ ] **Step 1: Compute the Dev Kit coverage floor from baseline**

From `company/config/coverage_baseline.json`, compute the minimum integer floor of line coverage among runtime files with at least one statement, capped at 95 and floored at 0.

This value is only the Dev Kit compatibility floor; `tools/coverage_gate.py` remains the authoritative non-regression/new-file gate.

- [ ] **Step 2: Add RED Dev Kit config test**

Assert:
- tracker type `linear`;
- teamKey `YAS`;
- prHost `github`;
- stacks `["python"]`;
- coverage mode `auto`;
- coverage min equals the computed baseline-derived floor;
- e2e mode `off`;
- no telemetry key exists;
- no credential/token fields exist.

- [ ] **Step 3: Run and verify RED**

Expected: missing `.claude/dev-kit.json`.

- [ ] **Step 4: Create `.claude/dev-kit.json`**

Do not install `gh`.

Connector policy for execution remains:
- Linear connector for issue/project operations;
- GitHub connector/native Git for repository operations;
- `gh` becomes a future HR gap only after two material repeated handoffs that cannot be adapted.

- [ ] **Step 5: Run test and full validator**

Expected: PASS.

- [ ] **Step 6: Commit**

`git add .claude/dev-kit.json company/tests/test_work_environment_hardening.py`

`git commit -m "chore: bootstrap Linear GitHub development workflow"`

---

### Task 9: Reduce GitHub ChatGPT plugin authority and record a structured receipt

**Files:**
- Create: `company/docs/evidence/tool_permissions_2026-10-11.json`
- Modify: `company/tests/test_work_environment_hardening.py`

**Interfaces:**
- Consumes: Plugin Management permission read/write capability.
- Produces: GitHub plugin setting `ask_before_writes` and a non-secret structured receipt.

- [ ] **Step 1: Read current GitHub plugin permission**

Expected baseline from audit: app-specific `full_access` / UI label `Allow all actions`.

If already safer, do not widen it; record actual state.

- [ ] **Step 2: Change GitHub app-specific permission to `ask_before_writes`**

Use Plugin Management permission update with explicit reason:
`Work Environment Hardening v1: allow reads, require confirmation before writes.`

Do not change global permissions.

- [ ] **Step 3: Read permission back**

Expected: GitHub app-specific permission corresponds to `ask_before_writes`.

If the provider refuses the setting, record `UNAVAILABLE`/actual result and do not claim success.

- [ ] **Step 4: Write receipt JSON**

Fields:
- provider `GitHub`;
- action_family `ChatGPT plugin permission`;
- observed_at `2026-10-11`;
- before;
- requested;
- after;
- changed boolean;
- evidence_source `Plugin Management get_app_permissions/update_app_permissions`;
- enforcement_claim `provider-reported setting, not backend resource proof`.

No account token, user secret, or OAuth material.

- [ ] **Step 5: Add receipt contract test**

Assert receipt does not contain `full_access` in the `after` field and contains `changed` plus evidence source.

- [ ] **Step 6: Commit**

`git add company/docs/evidence/tool_permissions_2026-10-11.json company/tests/test_work_environment_hardening.py`

`git commit -m "security: reduce GitHub connector write authority"`

---

### Task 10: Record repository security feature state and resolve Codex Security capability truthfully

**Files:**
- Create/Modify: `company/docs/WORK_ENVIRONMENT_HARDENING_ACCEPTANCE.md`
- Modify: `company/tests/test_work_environment_hardening.py`

**Interfaces:**
- Produces: explicit evidence states for CodeQL, secret scanning, push protection, Dependabot, and Codex Security.

- [ ] **Step 1: Write acceptance document skeleton with non-PASS initial states**

Include all 22 acceptance criteria from spec section 22 as explicit `PENDING`, `PASS`, `FAILED`, `UNAVAILABLE`, or `ADMIN_BLOCKED` records, plus the reopen triggers from spec section 24.

Initialize security/external fields as:
- CodeQL: `PENDING_REMOTE_RUN`;
- secret scanning: `UNKNOWN`;
- push protection: `UNKNOWN`;
- Dependabot alerts: `UNKNOWN`;
- Codex Security callable capability: `UNKNOWN`;
- main ruleset: `UNPROTECTED_BASELINE`.

- [ ] **Step 2: Inspect repository security endpoints/settings through available GitHub read capability**

Read only supported endpoints. Do not treat 403 as disabled; classify it `ADMIN_READ_BLOCKED`.

- [ ] **Step 3: Inspect callable tool/skill inventory for Codex Security**

If a callable Codex Security tool/skill exists, record `CALLABLE_UNTESTED` and schedule a bounded repository pilot before calling it enforced.

If no callable capability exists, record `UNAVAILABLE_IN_CURRENT_SESSION`.

Metadata-only installation remains `METADATA_OBSERVED`.

- [ ] **Step 4: Update acceptance evidence**

Record provider, timestamp/date, result, and limitation. No secret material.

- [ ] **Step 5: Add acceptance contract test**

Assert acceptance document contains no false phrase indicating Codex Security PASS when state is unavailable, and every security feature has an explicit state.

- [ ] **Step 6: Commit**

`git add company/docs/WORK_ENVIRONMENT_HARDENING_ACCEPTANCE.md company/tests/test_work_environment_hardening.py`

`git commit -m "docs: record hardening security evidence states"`

---

### Task 11: Classify historical remote branches before cleanup

**Files:**
- Create: `company/docs/BRANCH_HYGIENE_2026-10-11.md`

**Interfaces:**
- Produces: one classification per remote branch excluding `origin/main`.

- [ ] **Step 1: Refresh remote refs without mutation**

`git fetch origin --prune`

- [ ] **Step 2: Classify every remote branch**

For each branch:
1. If `git merge-base --is-ancestor <branch> origin/main` succeeds -> `MERGED_EQUIVALENT`.
2. Else if `git diff --quiet origin/main <branch> --` succeeds -> `SUPERSEDED` with identical tree evidence.
3. Else -> `UNMERGED_REQUIRES_REVIEW`.

Record:
- branch name;
- head SHA;
- classification;
- ancestry result;
- changed-file count against main;
- unique commit count;
- action `DELETE_SAFE`, `KEEP`, or `REVIEW`.

- [ ] **Step 3: Review non-ancestor branches for already-landed semantic equivalents**

Use commit messages/diff paths only to explain status; do not silently promote a branch to safe deletion without tree/patch evidence.

- [ ] **Step 4: Delete only `DELETE_SAFE` branches**

Use native Git remote delete.

Never delete `UNMERGED_REQUIRES_REVIEW`.

After deletion, `git fetch origin --prune` and read back remote branch list.

- [ ] **Step 5: Commit evidence document**

`git add company/docs/BRANCH_HYGIENE_2026-10-11.md`

`git commit -m "docs: classify historical remote branches"`

---

### Task 12: Run complete local verification and open the hardening PR

**Files:**
- All changed files in branch.

**Interfaces:**
- Produces: remote feature branch and pull request with local verification evidence.

- [ ] **Step 1: Run verification-before-completion locally**

Required commands using `.venv-hardening`:
- `python -m ruff check company tools`;
- changed-file `ruff format --check`;
- `python -m coverage erase`;
- `python -m coverage run --branch -m unittest discover -s company/tests -v`;
- `python -m coverage json -o build/coverage.json`;
- `python tools/coverage_gate.py --coverage build/coverage.json --baseline company/config/coverage_baseline.json --base origin/main`;
- `python tools/validate_config.py`;
- `python -m compileall -q company tools`;
- `git diff --check origin/main...HEAD`.

Expected: all PASS, only documented expected test skip.

- [ ] **Step 2: Run structured self-review**

Use Fullstack Dev Kit `pr-review` and VibeSec/source review on the whole diff.

Blocking findings must be fixed with tests and full re-verification before proceeding.

- [ ] **Step 3: Push feature branch**

First fetch origin and verify `origin/main` has not diverged unexpectedly from the baseline/integration assumption.

Push:
`git push -u origin feat/work-environment-hardening-v1`

No force push.

- [ ] **Step 4: Open PR with GitHub connector**

Title:
`Work Environment Hardening v1`

Body includes:
- spec and plan paths;
- Linear project/issues;
- local commands/results;
- security boundary summary;
- explicit external settings still pending/admin-blocked;
- rollback notes.

- [ ] **Step 5: Link PR to Linear hardening issues**

Update issue descriptions/comments with PR link. Do not mark completed yet.

---

### Task 13: Observe PR CI, establish remote CodeQL baseline, and fix all blocking failures

**Files:**
- As required by verified failures only.

**Interfaces:**
- Produces: a green remote PR or explicit provider blockers.

- [ ] **Step 1: Read PR workflow runs**

Require successful:
- `Quality Gate`;
- `Python 3.12 Compatibility`;
- `CodeQL Python`.

If CodeQL cannot start because repository/account security capability blocks it, record exact provider result in acceptance document and classify `ADMIN_BLOCKED`; do not fake green.

- [ ] **Step 2: Inspect failed job steps/logs exactly**

Use GitHub workflow job/step/log tools.

Apply systematic debugging; no speculative fixes.

- [ ] **Step 3: Fix, test, commit, and push each blocking issue**

Every behavioral fix uses RED -> GREEN.

Re-run local gates before each push when relevant.

- [ ] **Step 4: Update acceptance document with remote evidence**

Store workflow run identifiers/URLs or canonical GitHub references, status, and observation date.

- [ ] **Step 5: Commit evidence update if changed**

`git commit -m "docs: record remote hardening verification"`

Push normally.

---

### Task 14: Enforce main repository rules and inspect security settings

**Files:**
- Modify: `company/docs/WORK_ENVIRONMENT_HARDENING_ACCEPTANCE.md` only for evidence/status.

**Interfaces:**
- Consumes: actual green check names from Task 13.
- Produces: protected `main` if an authorized repository-admin channel exists; otherwise exact `ADMIN_BLOCKED` evidence.

- [ ] **Step 1: Re-read repository rulesets/protection capability**

Do not assume the connector gained admin authority.

- [ ] **Step 2: Apply main protection only through an authorized admin-capable channel**

Target:
- require pull request before merge;
- prohibit force pushes;
- prohibit deletion;
- require successful `Quality Gate`;
- require successful `Python 3.12 Compatibility`;
- require successful `CodeQL Python` only after its baseline is proven stable.

Do not require a second human reviewer in v1.

- [ ] **Step 3: Read back protection state**

Expected when supported: `main` reports protected/ruleset state consistent with target.

If no authorized write capability exists:
- set acceptance state `ADMIN_BLOCKED`;
- record that repository-code controls are complete but remote branch enforcement remains unresolved;
- do not attempt credential extraction, browser-session theft, or token reuse.

- [ ] **Step 4: Inspect secret scanning, push protection, and Dependabot state**

Enable only through an authorized admin-capable channel if available.

Otherwise record exact `ADMIN_BLOCKED`/unknown state.

- [ ] **Step 5: Commit evidence update**

If acceptance evidence changed:
`git commit -m "docs: record GitHub repository protection state"`
and push branch.

---

### Task 15: Final branch review, merge, and post-merge main verification

**Files:**
- No planned source changes unless review finds a defect.

**Interfaces:**
- Produces: merged hardening control plane or a truthful blocked state.

- [ ] **Step 1: Whole-branch review**

Use the most capable available reviewer path:
- correctness/spec coverage;
- security;
- authority boundaries;
- tests/coverage;
- workflow semantics;
- no unnecessary dependencies.

Resolve blocking findings and re-verify.

- [ ] **Step 2: Confirm final PR checks**

All applicable required checks green.

If main protection is `ADMIN_BLOCKED`, explicitly surface that unresolved acceptance item before merge; user already authorized best-effort execution, but the final report must not call v1 fully accepted.

- [ ] **Step 3: Merge PR without force operations**

Use GitHub connector merge only after checks are green.

- [ ] **Step 4: Fetch and verify post-merge `main`**

Confirm local/remote main SHA convergence.

Read the push-triggered `Company Stage 0` run on merged main and require:
- `Quality Gate` success;
- `Python 3.12 Compatibility` success.

Read CodeQL main run and record its state.

- [ ] **Step 5: Run a final local main smoke verification**

After fast-forwarding local main:
- validator;
- compileall;
- full unittest;
- Ruff;
- coverage gate against previous main where applicable.

- [ ] **Step 6: Update Linear**

Move all completed hardening issues to completed/review-complete state with PR/merge reference.

Any `ADMIN_BLOCKED` external setting remains an open follow-up issue rather than falsely completed.

---

### Task 16: Clean execution workspace and establish milestone tag only after acceptance

**Files:**
- Optional final evidence update.

**Interfaces:**
- Produces: clean local worktree state and optional tag `work-environment-v1`.

- [ ] **Step 1: Determine acceptance status from the committed acceptance document**

If any mandatory criterion is `FAILED` or `ADMIN_BLOCKED`, do not create the milestone tag.

- [ ] **Step 2: If all mandatory criteria PASS, create annotated milestone tag**

`git tag -a work-environment-v1 -m "Universal Council Work Environment Hardening v1"`

`git push origin work-environment-v1`

No moving/retagging an existing tag.

- [ ] **Step 3: Remove the isolated worktree after branch integration**

From main repo:
`git worktree remove <hardening-worktree>`

Delete local feature branch only after verifying it is merged.

- [ ] **Step 4: Final readbacks**

Confirm:
- working tree clean;
- local main == origin/main;
- Linear project has no incorrectly completed blocked item;
- GitHub permission remains ask-before-writes;
- Agent Reach pin/boundaries unchanged;
- no credential material in git diff/history from this branch.

- [ ] **Step 5: Final report**

Report separately:
- repository controls completed;
- external controls completed;
- admin/provider blockers;
- final test/coverage/CodeQL evidence;
- final SHA;
- tag status;
- follow-ups, if any.

Never collapse a partial result into "all done."
