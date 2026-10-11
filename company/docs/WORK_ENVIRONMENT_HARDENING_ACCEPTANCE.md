# Work Environment Hardening v1 - Acceptance Evidence

Status: IMPLEMENTATION_COMPLETE_ADMIN_BLOCKED
Observed: 2026-10-12
Repository baseline: `main@bfc08b5ea98f352f595029f62fcefe6cc93395fb`
Execution branch: `feat/work-environment-hardening-v1`

This document records acceptance evidence. It does not promote UNKNOWN, UNAVAILABLE, CONNECTOR_ENDPOINT_UNSUPPORTED, ADMIN_BLOCKED, or PENDING states to PASS.

## Current security and repository state

- CodeQL: PASS_BASELINE / PASS_POST_MERGE - PR baseline and main push both completed successfully; main run `38180289825`, job `CodeQL Python`, Initialize + Analyze SUCCESS on `ffa3567d6a225f5a97c420c5cd354f6be4fa7248`.
- Secret scanning: CONNECTOR_ENDPOINT_UNSUPPORTED - the current GitHub connector does not expose this repository endpoint through its approved fetch surface; this is not evidence that the feature is disabled.
- Push protection: CONNECTOR_ENDPOINT_UNSUPPORTED - the current GitHub connector does not expose the required administration/security endpoint; this is not evidence that the feature is disabled.
- Dependabot alerts: CONNECTOR_ENDPOINT_UNSUPPORTED - the current GitHub connector does not expose the alerts endpoint through its approved fetch surface; this is not evidence that alerts are disabled.
- Code scanning alerts endpoint: CONNECTOR_ENDPOINT_UNSUPPORTED - CodeQL workflow execution itself is independently proven by Actions evidence.
- Codex Security callable capability: UNAVAILABLE_IN_CURRENT_SESSION - no callable Codex Security tool or skill is present in the current tool inventory. Catalog metadata is not enforcement evidence.
- Main ruleset: UNPROTECTED_BASELINE / ADMIN_BLOCKED - rulesets readback returned `[]`; `main` reports `protected: false`; current connector exposes reads but no repository-administration write operation.
- Repository permission readback: ADMIN_REPORTED - the connected GitHub account reports `admin: true`, but the managed connector's available tools do not expose repository administration writes.
- GitHub ChatGPT permission: PASS - app-specific permission is read-allowed / ask-before-write; receipt: `company/docs/evidence/tool_permissions_2026-10-11.json`.

## Acceptance criteria

- AC-01 - ADMIN_BLOCKED - `main` protection remains unresolved because the connected GitHub tool surface exposes branch/ruleset reads but no repository-administration write action; no credential/token workaround was used.
- AC-02 - ADMIN_BLOCKED - required status-check enforcement cannot be configured through the currently exposed GitHub administration surface; actual check names are proven as `Quality Gate`, `Python 3.12 Compatibility`, and `CodeQL Python`.
- AC-03 - PASS - core workflow ran on push to `main` at merge SHA `ffa3567d6a225f5a97c420c5cd354f6be4fa7248`; Company Stage 0 run `38180289803` succeeded.
- AC-04 - PASS - company tests are green on Python 3.12 CI and Python 3.13 local/CI execution.
- AC-05 - PASS - Ruff 0.17.0 lint plus changed-file format checking is active without legacy-wide formatting churn.
- AC-06 - PASS - branch coverage is measured; changed legacy runtime files cannot regress and new runtime files require at least 95% line coverage.
- AC-07 - PASS_POST_MERGE - CodeQL Python completed successfully on the hardening PR and on post-merge `main`; main run `38180289825` succeeded.
- AC-08 - PARTIAL_CONNECTOR_ENDPOINT_UNSUPPORTED - Secret Scanning, Push Protection, and Dependabot state cannot currently be read or changed through the exposed GitHub connector administration surface.
- AC-09 - PASS - checkout, setup-python, and CodeQL Actions are pinned to full immutable commit SHAs.
- AC-10 - PASS - GitHub ChatGPT plugin no longer has the previous unqualified full-access override; writes require confirmation.
- AC-11 - PASS - Linear contains one `Universal Council` project and the 11 hardening issues `YAS-5` through `YAS-15`.
- AC-12 - PASS - `.claude/dev-kit.json` is committed/configured for Linear, GitHub, and Python without credentials or telemetry.
- AC-13 - PASS - engineering tool capabilities are represented with evidence, effects, scopes, approval policies, and enforcement boundaries.
- AC-14 - PASS - remote shell execution is classified as high-impact and policy-governed, not falsely represented as backend-enforced.
- AC-15 - PASS - Agent Reach remains public-read only at pin `94f06c1969dfc1834001269d79d3ad0972d9dee6`; authenticated social remains blocked.
- AC-16 - PASS_CLASSIFICATION - Codex Security is classified truthfully as unavailable in the current callable tool inventory; no metadata-only PASS exists.
- AC-17 - PASS - historical remote branches were classified; only the proven merged-equivalent Council Intelligence Gateway branch was deleted, and all unmerged branches were preserved.
- AC-18 - PASS - final local verification on `58c21f336c1e0cc730bd63fabd23a543a8c10ff9` passed: 169 tests, one expected skip, Ruff lint/format, compileall, config validator, coverage ratchet, diff check, and secret heuristic.
- AC-19 - PASS - PR #7 at `0e6664e11e874ae70a5e7acd59f5f07bd5985cf1` passed Company Stage 0 run `38179817328` (`Quality Gate` + `Python 3.12 Compatibility`) and CodeQL run `38179817363` (`CodeQL Python`).
- AC-20 - PASS - post-merge `main` evidence is complete: Company Stage 0 run `38180289803` and CodeQL run `38180289825` both succeeded on `ffa3567d6a225f5a97c420c5cd354f6be4fa7248`; YASSIN post-merge local smoke also passed 169 tests with one expected skip.
- AC-21 - PASS - no unnecessary new platform/plugin was installed; only Ruff and coverage.py were added as pinned development dependencies.
- AC-22 - PASS_REVIEWED - final VibeSec/PR review, local secret heuristic, CodeQL, and post-merge verification found no blocking secret/session/credential issue in the hardening change.

## Evidence notes

- Measured runtime coverage baseline is committed at `company/config/coverage_baseline.json`.
- `company/runtime/tool_authority.py` reached 100% line and branch coverage in its focused test run before full-suite revalidation.
- The Git repository remains canonical for technical/governance truth; Linear tracks work status and linkage only.
- Provider administration limitations are reported explicitly and do not authorize workarounds involving token extraction, cookie/session reuse, or browser credential harvesting.
- Fullstack PR Review + VibeSec source/config review found one blocking contract gap (unknown authority enums were not fail-closed); it was fixed with RED/GREEN tests before final local verification. No blocking finding remains in the reviewed hardening diff.

## Reopen triggers

Reopen this design/acceptance review if any of the following occurs:

- CI runtime or cost becomes materially burdensome.
- GitHub account/plan limitations prevent required branch rules.
- The coverage ratchet causes repeated false blocks.
- Fullstack Dev Kit causes repeated unsupported CLI handoffs.
- A permanent additional developer changes reviewer-policy needs.
- Repository visibility changes.
- A second repository joins this delivery surface.
- Engineering tools gain materially broader write, execute, session, or credential authority.
- A security incident invalidates the current assumptions.

## Final acceptance rule

Work Environment Hardening v1 is not FINAL_ACCEPTED while any mandatory criterion is `FAILED`, `PENDING`, or `ADMIN_BLOCKED`. A milestone tag must not be created in that state.
