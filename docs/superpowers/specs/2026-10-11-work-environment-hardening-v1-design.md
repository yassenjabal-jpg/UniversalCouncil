# Universal Council - Work Environment Hardening v1 Design

Date: 2026-10-11
Status: Owner-approved design, implementation not yet authorized
Repository: `yassenjabal-jpg/UniversalCouncil`
Baseline: `main@bfc08b5ea98f352f595029f62fcefe6cc93395fb`

## 1. Purpose

Work Environment Hardening v1 turns the existing Universal Council development environment into a controlled, measurable engineering operating system without adding unnecessary platforms or duplicating tools.

The desired outcome is not "more tooling." The desired outcome is:

- no silent bypass of engineering gates;
- a single source of truth for code and governance;
- a traceable source of truth for work items;
- measurable quality rather than test-count confidence;
- explicit authority boundaries for read/write/execute tools;
- deterministic verification before merge;
- minimum justified tool count;
- reversible adoption with clear kill criteria.

The repository remains the canonical source of truth for code, governance, contracts, engineering configuration, and durable technical evidence. Linear is the work tracker, not a second source of technical truth.

## 2. Current-state evidence

The design is grounded in observed state rather than conversation memory.

### 2.1 GitHub and delivery

Observed at baseline:

- `main` is not protected.
- No repository rulesets are present.
- The current `.github/workflows/company-stage0.yml` runs on pull requests for selected paths.
- Its push trigger targets the historical branch `codex/venture-operating-system-v1`, not `main`.
- GitHub reported no workflow runs on `main` at audit time.
- Direct push to `main` therefore bypasses the current workflow.
- GitHub plugin permissions are configured with an app-specific "Allow all actions" override.
- Multiple historical remote branches remain.
- No release tags exist.

### 2.2 Quality tooling

Observed on YASSIN and in the repository:

- Python on YASSIN: 3.13.3.
- CI currently uses Python 3.12.
- Existing tests use `unittest`.
- The current company suite contains 125 tests and was green at the baseline.
- No `pyproject.toml` exists.
- No repository coverage configuration exists.
- `coverage`, `ruff`, and `pre-commit` are not installed on YASSIN.
- No committed Dev Kit configuration exists.
- No repository-level lint gate exists.

### 2.3 Work tracking

Observed:

- Linear connector is available.
- Workspace: `yassin`.
- Team key: `YAS`.
- There are no real projects.
- Existing issues are only default onboarding issues.

### 2.4 Security and capability evidence

Observed:

- Agent Reach is already constrained by Council Intelligence Gateway v1 to public-read operations and a pinned commit.
- Codex Security appears installed in plugin metadata, but no callable tool or skill was observable in the session; it therefore cannot count as an enforced security gate.
- Remote Desktop Commander can execute shell processes and therefore represents execution authority materially higher than ordinary read tools.
- Existing company capability examples focus on venture/external operations and do not yet describe engineering-tool operations such as GitHub write/merge or remote shell execution.

## 3. Scope

Work Environment Hardening v1 includes seven coordinated workstreams:

1. GitHub delivery protection.
2. Deterministic CI on pull requests and `main`.
3. Python quality and coverage measurement.
4. Security automation and supply-chain hardening.
5. Linear + Fullstack Dev Kit work tracking.
6. Engineering tool authority registry.
7. Repository and branch hygiene.

This is one architecture because the safety of each part depends on the others. For example, coverage is not a meaningful gate if direct pushes can bypass CI.

## 4. Explicit non-goals

Version 1 does not:

- replace `unittest` with pytest;
- add Jira, ClickUp, Datadog, Vanta, Coda, Dropbox Dash, MongoDB Atlas, or another project-management/observability/compliance platform;
- require GitBook or Notion as a canonical engineering source;
- expand Agent Reach into authenticated social, browser-cookie, OpenCLI, or write-capable usage;
- install `gh` CLI solely to satisfy Fullstack Dev Kit;
- require a human reviewer on every pull request for a single-owner repository;
- require 95% whole-repository coverage immediately;
- claim Codex Security is active until callable evidence exists;
- grant Remote Desktop Commander broader authority;
- enable automatic publishing, messaging, spending, or venture activation;
- delete unmerged historical branches without provenance review.

## 5. Governing principles

### 5.1 Source of truth

Priority:

1. current repository and current default branch;
2. committed governance/contracts/configuration;
3. CI, tests, workflow runs, rulesets and generated verification evidence;
4. tracker records;
5. conversation context only for interpretation.

### 5.2 Read/write separation

Read operations should be low-friction. External writes, merges, pushes, permission changes, credential connections, installs, publication, and remote shell execution must be explicit and attributable.

### 5.3 Evidence labels

Tool availability must distinguish:

- `ADVERTISED`;
- `METADATA_OBSERVED`;
- `BYTES_VERIFIED`;
- `SCRIPT_TESTED`;
- `HOST_INVOKED`;
- `BOUNDARY_ENFORCED`.

A plugin name or permission description never proves backend enforcement.

### 5.4 Minimal justified tooling

A new tool is adopted only when an existing capability cannot absorb the gap without material cost, risk, or recurring friction.

## 6. Target operating model

The standard engineering path becomes:

`Linear issue -> isolated branch/worktree -> approved plan -> TDD/implementation -> quality/security gates -> PR -> CI -> review -> merge -> tracker update -> follow-up capture`

Direct work on `main` is an exception path, not the normal path.

## 7. GitHub delivery protection

### 7.1 Main branch policy

The target policy for `main` is:

- prohibit force pushes;
- prohibit branch deletion;
- require pull request before merge;
- require all configured status checks to pass;
- require branch to be up to date when the required-check configuration supports it reliably;
- do not require a second human reviewer in v1;
- do not allow administrators/bots to silently bypass required checks unless GitHub account limitations make an exception unavoidable and the exception is documented.

### 7.2 CI triggers

`Company Stage 0` must run on:

- every pull request targeting the default branch when repository-relevant files change;
- every push to `main`.

The existing historical push branch trigger must be removed.

For v1, the preferred design is to remove narrow path filtering from the core verification workflow because the suite is small and fast. A change to governance, docs used as contracts, skills, workflow configuration, or tooling can be material even when it does not match `company/**`.

If measured CI cost later becomes material, path filtering may be reintroduced only with explicit invariant coverage.

### 7.3 Merge evidence

A merge is considered engineering-complete only when:

- required checks passed for the merged commit or PR;
- the resulting `main` commit exists remotely;
- post-merge `main` verification is observable through the push workflow;
- the tracker reflects the delivery state.

## 8. Python environment and reproducibility

### 8.1 Python support

Version 1 supports Python 3.12 and 3.13.

CI must verify both versions for behavior that is expected to be runtime-portable, unless a later documented compatibility decision narrows the supported range.

### 8.2 Project metadata

Add a minimal `pyproject.toml` that defines:

- supported Python range;
- development dependencies required for repository verification;
- Ruff configuration;
- coverage configuration where supported;
- no runtime dependency inflation.

The company runtime must continue to work with the standard library where it currently does so.

### 8.3 Dependency strategy

Initial development-tool dependencies:

- `ruff`;
- `coverage`.

Do not add pytest, mypy, pre-commit, uv, Black, Flake8, or isort in v1 unless implementation discovers a concrete blocker that cannot be solved without one of them.

Any such discovery upgrades into an HR capability-gap decision rather than silent dependency growth.

## 9. Quality gates

The target CI order is:

1. repository/configuration validation;
2. compile check;
3. Ruff lint/format verification;
4. unit/behavior test execution;
5. branch coverage measurement;
6. security/static-analysis checks;
7. final status aggregation when useful.

### 9.1 Ruff

Ruff is the single v1 lint/format engine.

Initial rollout must avoid a mass unrelated reformat. Existing files are checked with a staged adoption strategy:

- new/changed code must be clean;
- existing high-confidence violations that can be fixed mechanically without semantic risk may be included;
- broad stylistic churn is excluded from the first hardening PR.

### 9.2 Coverage

Coverage must use branch coverage.

The rollout is two-stage:

**Stage A - baseline measurement**

- record actual repository coverage;
- record per-file coverage for production modules;
- do not invent a 95% global result.

**Stage B - ratchet**

- no touched production file may regress below its pre-change coverage;
- new production modules should target at least 95% line coverage when the metric is meaningful;
- branch coverage must be reported separately;
- legacy files below the eventual target remain visible debt rather than causing unrelated work to fail immediately.

A later Council decision may raise the global minimum after baseline evidence exists.

### 9.3 Tests

Keep `unittest` as the primary test framework in v1.

Behavioral changes require tests that would fail without the change. Tests without meaningful assertions do not count as adequate verification.

## 10. Security automation

### 10.1 CodeQL

Enable GitHub CodeQL for Python using the lowest-maintenance configuration that provides reliable default-branch and pull-request scanning.

CodeQL becomes a required merge check only after at least one successful baseline run demonstrates that configuration is valid and stable.

### 10.2 Secret scanning and push protection

Inspect repository capabilities first.

If available for this repository/account:

- enable secret scanning;
- enable push protection.

If an administrative/account limitation blocks either setting, record `ADMIN_BLOCKED` with the exact limitation. Do not simulate success.

### 10.3 Dependabot

Enable dependency alerts where available.

Automated dependency pull requests are optional in v1 and should only be enabled if they do not create high-noise churn. Alerts are higher priority than automatic update PR volume.

### 10.4 GitHub Actions supply chain

Third-party and GitHub-owned actions in committed workflows must be pinned to full immutable commit SHAs where feasible.

The committed file should retain an inline comment identifying the human-readable action release corresponding to the pinned SHA.

A tag such as `@v7` is not treated as immutable provenance.

## 11. ChatGPT plugin permissions

### 11.1 GitHub

Target permission policy:

- reads may proceed without per-read friction;
- writes require explicit approval/confirmation;
- remove the current plugin-specific `Allow all actions` override.

The intended setting is `ask_before_writes` or the closest available equivalent.

### 11.2 Linear

Linear may remain on the global/default permission policy unless a later review finds write risk that justifies a stricter override.

### 11.3 Permission receipts

Every permission review/change used as governance evidence must record:

- provider;
- action family;
- reported scope;
- observed time;
- evidence source;
- whether a change occurred.

## 12. Linear work management

### 12.1 Project structure

Create one initial Linear project:

`Universal Council`

Use the existing `YAS` team.

Do not create additional teams or projects in v1 unless a measurable workflow bottleneck requires them.

### 12.2 Initial backlog

The hardening findings become real tracked work items, including at minimum:

- P0 - main branch/CI bypass protection;
- P0 - GitHub plugin permission reduction;
- P1 - Python reproducibility + pyproject;
- P1 - Ruff gate;
- P1 - branch coverage baseline and ratchet;
- P1 - CodeQL / secret scanning / dependency security;
- P1 - Fullstack Dev Kit repository bootstrap;
- P1 - engineering tool authority registry;
- P2 - historical branch hygiene;
- P2 - Codex Security callable-capability investigation;
- P2 - release/tag discipline.

Implementation may consolidate tightly coupled items under an epic/project milestone, but each acceptance criterion must remain traceable.

### 12.3 Tracker role

Linear tracks:

- intent;
- status;
- priority;
- acceptance criteria;
- PR linkage;
- follow-ups.

Linear must not duplicate full technical specs or governance contracts that live in Git.

## 13. Fullstack Dev Kit integration

### 13.1 Repository bootstrap

Add a committed `.claude/dev-kit.json` configured for:

- tracker type: Linear;
- team key: `YAS`;
- PR host: GitHub;
- stack: Python;
- coverage gate mode: auto during initial bootstrap;
- coverage threshold: based on the approved ratchet design, not an invented global pass;
- e2e: not applicable for the current non-UI company module.

### 13.2 Connector-first adaptation

The installed Fullstack Dev Kit assumes `gh` for some GitHub operations.

Version 1 does not install `gh` merely to satisfy that assumption.

Operational policy:

- use Linear connector for Linear reads/writes;
- use GitHub connector/native Git for GitHub actions already supported;
- record any repeated Dev Kit step that truly requires `gh` and cannot be cleanly adapted;
- only after two material repeated handoffs may HR open a `REPEATED_MANUAL_WORK` gap for GitHub CLI.

### 13.3 No silent automation authority

Dev Kit workflows coordinate steps; they do not expand authority. Owner approvals and write boundaries remain governing.

## 14. Engineering tool authority registry

### 14.1 Goal

Extend capability governance so engineering tools are represented explicitly rather than inferred from connector visibility.

### 14.2 Minimum operations

The registry must support entries for at least:

- `github.read`;
- `github.write`;
- `github.merge`;
- `linear.read`;
- `linear.write`;
- `remote_shell.read`;
- `remote_shell.execute`;
- `agent_reach.public_read`;
- `browser.authenticated`;
- `external.publish`.

### 14.3 Required fields

Each tool capability record must include:

- capability id;
- provider/tool;
- operation;
- classification;
- evidence level;
- authentication class;
- read/write/execute effect;
- approval policy;
- allowed scope;
- prohibited scope;
- last verified time;
- expiry/review trigger;
- source/version/pin when relevant;
- rollback/disable path when relevant.

### 14.4 Enforcement boundary

In v1, the registry is authoritative governance evidence and validation input.

It must not falsely claim it can technically intercept every ChatGPT connector or Remote Desktop execution. Where backend enforcement does not exist, the record must say `POLICY_ENFORCED_ONLY`.

A future version may add executable mediation only through a separately approved architecture.

## 15. Remote shell policy

Remote Desktop Commander is classified as high-impact execution authority.

Rules:

- use only on explicitly authorized user-controlled devices;
- prefer read-only inspection for audits;
- no credential extraction;
- no hidden browser/session extraction;
- no widening of system permissions as part of ordinary development;
- commands that mutate repository/system state must correspond to an approved implementation step;
- results from remote execution must be reported as host-invoked evidence, not boundary-enforced evidence.

## 16. Agent Reach policy

No change to Council Intelligence Gateway v1 authority.

Agent Reach remains:

- public-read only;
- strict commit pin;
- no OpenCLI;
- no cookies;
- no browser debugger;
- no credentials;
- no authenticated social;
- no external writes.

Work Environment Hardening must not weaken these guarantees.

## 17. Codex Security policy

Current state is `METADATA_OBSERVED`, not callable/enforced.

Version 1 task:

- investigate whether a callable Codex Security capability can be exposed in the current ChatGPT environment;
- if callable, run a bounded repository security pilot and record evidence;
- if not callable, record `UNAVAILABLE` and continue using CodeQL + VibeSec/source review + repository tests;
- do not install an unrelated security tool solely to make the checklist green.

## 18. Repository hygiene

### 18.1 Branch classification

Every remote branch must be classified as:

- `MERGED_EQUIVALENT`;
- `SUPERSEDED`;
- `ACTIVE`;
- `UNMERGED_REQUIRES_REVIEW`.

Deletion is allowed only for branches proven merged/equivalent or explicitly superseded with durable evidence.

### 18.2 Feature branch cleanup

The remote `feat/council-intelligence-gateway-v1` is known to point to an older commit than the implementation merged into `main`. It must not be assumed safe to delete merely from its name; equivalence/ancestry must be verified.

### 18.3 Tags

Introduce lightweight milestone tagging only after a coherent hardening release is integrated.

Recommended first tag after acceptance:

`work-environment-v1`

The exact tag is created only after Owner approval of the completed integration.

## 19. Migration and rollout order

The implementation order must preserve a usable repository at each step:

1. create isolated hardening branch/worktree;
2. add tests/validators for governance invariants where practical;
3. repair CI triggers;
4. add project metadata and development-tool configuration;
5. establish quality baseline locally and in CI;
6. add CodeQL/security settings;
7. reduce GitHub plugin permission;
8. configure Linear project/backlog;
9. add Dev Kit configuration;
10. add engineering tool authority registry + validation;
11. perform repository hygiene review;
12. run complete verification;
13. open/update PR and observe all remote checks;
14. merge only after required checks are stable;
15. verify post-merge `main` workflow;
16. update Linear and capability evidence;
17. offer milestone tag.

Steps may be reordered inside the implementation plan only when dependency evidence justifies it.

## 20. Rollback strategy

Every hardening component must be independently reversible.

- Workflow failures: revert workflow/config commit from feature branch before merge.
- Ruff adoption: remove gate/config without touching runtime semantics.
- Coverage: remove threshold gate while retaining generated baseline evidence if useful.
- CodeQL: disable the repository configuration without changing runtime code.
- Ruleset: revert repository rule settings if it blocks legitimate repository recovery.
- Plugin permission: restore only by explicit Owner decision.
- Linear: archive project/issues; repository remains unaffected.
- Dev Kit config: remove committed config.
- Tool authority registry: revert registry/validator changes; no external permission changes are implied.
- Branch deletion: must not occur until classification evidence exists, so rollback is not the primary protection.

## 21. Testing strategy

### 21.1 Pre-change baseline

Before implementation changes:

- full company test suite;
- `tools/validate_config.py`;
- `compileall`;
- clean working tree;
- record CI/ruleset/plugin permission baseline.

### 21.2 TDD

Behavioral/runtime changes use RED -> GREEN tests.

Configuration invariants should be expressed as deterministic tests or validators where practical, including:

- expected CI trigger includes `main`;
- development configuration is parseable;
- tool authority records contain required fields;
- prohibited authority states are rejected;
- Agent Reach invariants remain unchanged.

### 21.3 Remote verification

Final evidence must include:

- local YASSIN verification;
- GitHub PR CI;
- CodeQL state when enabled;
- ruleset/protection readback;
- plugin permission readback;
- Linear project/issues readback;
- post-merge `main` workflow run.

No remote result may be inferred from local success.

## 22. Acceptance criteria

Work Environment Hardening v1 is accepted only when all applicable criteria are proven:

1. `main` is protected against force-push and normal direct-push bypass.
2. Required PR status checks are enforced.
3. A push to `main` triggers the core workflow.
4. Company tests remain green on supported Python versions.
5. Ruff runs locally and in CI with a documented staged-adoption policy.
6. Branch coverage is measured and a non-regression ratchet is enforced for changed production code.
7. CodeQL has a successful baseline or an explicit provider/account blocker is recorded.
8. Secret scanning/push protection and Dependabot state are explicitly known; enabled where available and justified.
9. Workflow actions use immutable full-SHA pins where feasible.
10. GitHub ChatGPT plugin no longer has an unqualified `Allow all actions` override.
11. Linear contains a real `Universal Council` project and the hardening backlog.
12. `.claude/dev-kit.json` is committed and correctly points to Linear/GitHub/Python.
13. Engineering tool capabilities are represented with evidence/authority boundaries.
14. Remote shell execution is classified as high-impact authority.
15. Agent Reach public-read restrictions remain unchanged and tested.
16. Codex Security is classified accurately as callable or unavailable; no metadata-only false claim exists.
17. Historical remote branches are classified before any cleanup.
18. Full local verification passes.
19. PR verification passes remotely.
20. Post-merge `main` verification passes remotely.
21. No unnecessary new platform/plugin is installed.
22. No credentials, cookies, session tokens, browser-debugger access, or secrets are committed or exposed.

## 23. Success metrics

Within the first review cycle after adoption:

- zero unverified direct-to-main delivery events;
- every material engineering change has a tracker item or explicit owner exception;
- every merged change has remote verification evidence;
- quality regressions are visible through lint/coverage/test gates;
- no tool is counted as available solely from catalog metadata;
- no capability adoption bypasses HR -> Security -> Architecture/Duplication -> Council -> Pilot -> Owner where those gates apply;
- no increase in unnecessary tool count.

## 24. Review and reopen triggers

Reopen this design if any of the following occurs:

- CI runtime/cost becomes materially burdensome;
- GitHub account limitations prevent required rules;
- branch coverage ratchet causes repeated false blocks;
- Fullstack Dev Kit requires repeated unsupported CLI handoffs;
- a new permanent developer joins and human-review policy becomes materially different;
- repository visibility changes;
- a second repository becomes part of the same delivery surface;
- engineering tools gain materially broader write/credential authority;
- a security incident invalidates current assumptions.

## 25. Owner decisions captured

The Owner approved the Integrated Engineering Control Plane approach and instructed implementation of the full hardening package with high precision.

This approval authorizes writing this design specification. Per the governing Superpowers architectural workflow, implementation planning remains gated on Owner review of this written specification.
