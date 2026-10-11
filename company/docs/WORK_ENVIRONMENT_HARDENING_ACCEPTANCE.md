# Work Environment Hardening v1 - Acceptance Evidence

Status: IN_PROGRESS
Observed: 2026-10-12
Repository baseline: `main@bfc08b5ea98f352f595029f62fcefe6cc93395fb`
Execution branch: `feat/work-environment-hardening-v1`

This document records acceptance evidence. It does not promote UNKNOWN, UNAVAILABLE, CONNECTOR_ENDPOINT_UNSUPPORTED, ADMIN_BLOCKED, or PENDING states to PASS.

## Current security and repository state

- CodeQL: PASS_BASELINE - GitHub Actions run `38133650804`, job `CodeQL Python`, Initialize + Analyze completed successfully.
- Secret scanning: CONNECTOR_ENDPOINT_UNSUPPORTED - the current GitHub connector does not expose this repository endpoint through its approved fetch surface; this is not evidence that the feature is disabled.
- Push protection: CONNECTOR_ENDPOINT_UNSUPPORTED - the current GitHub connector does not expose the required administration/security endpoint; this is not evidence that the feature is disabled.
- Dependabot alerts: CONNECTOR_ENDPOINT_UNSUPPORTED - the current GitHub connector does not expose the alerts endpoint through its approved fetch surface; this is not evidence that alerts are disabled.
- Code scanning alerts endpoint: CONNECTOR_ENDPOINT_UNSUPPORTED - CodeQL workflow execution itself is independently proven by Actions evidence.
- Codex Security callable capability: UNAVAILABLE_IN_CURRENT_SESSION - no callable Codex Security tool or skill is present in the current tool inventory. Catalog metadata is not enforcement evidence.
- Main ruleset: UNPROTECTED_BASELINE - rulesets readback returned `[]`; `main` readback reports `protected: false`.
- Repository permission readback: ADMIN_REPORTED - the connected GitHub account reports `admin: true`, but the managed connector's available tools do not expose repository administration writes.
- GitHub ChatGPT permission: PASS - app-specific permission is read-allowed / ask-before-write; receipt: `company/docs/evidence/tool_permissions_2026-10-11.json`.

## Acceptance criteria

- AC-01 - PENDING_REMOTE_ENFORCEMENT - `main` must be protected against force-push and normal direct-push bypass.
- AC-02 - PENDING_REMOTE_ENFORCEMENT - required PR status checks must be enforced.
- AC-03 - CONFIG_PASS_REMOTE_MAIN_PENDING - core workflow is configured for push to `main`; post-merge run still required.
- AC-04 - PASS - company tests are green on Python 3.12 CI and Python 3.13 local/CI execution.
- AC-05 - PASS - Ruff 0.17.0 lint plus changed-file format checking is active without legacy-wide formatting churn.
- AC-06 - PASS - branch coverage is measured; changed legacy runtime files cannot regress and new runtime files require at least 95% line coverage.
- AC-07 - PASS_BASELINE - CodeQL Python baseline completed successfully; final branch/main evidence will be refreshed before acceptance.
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
- AC-18 - PENDING_FINAL_RERUN - local verification has passed intermediate gates; one final full run is required after Tasks 10-11.
- AC-19 - PENDING - PR #7 must be updated with the reconciled local branch and pass all remote checks.
- AC-20 - PENDING - post-merge `main` workflow and CodeQL runs must be observed.
- AC-21 - PASS_SO_FAR - no unnecessary new platform/plugin was installed; only Ruff and coverage.py were added as pinned development dependencies.
- AC-22 - PASS_SO_FAR_FINAL_REVIEW_PENDING - no credential, cookie, session token, browser-debugger access, or secret has been intentionally introduced; final review/scan remains required.

## Evidence notes

- Measured runtime coverage baseline is committed at `company/config/coverage_baseline.json`.
- `company/runtime/tool_authority.py` reached 100% line and branch coverage in its focused test run before full-suite revalidation.
- The Git repository remains canonical for technical/governance truth; Linear tracks work status and linkage only.
- Provider administration limitations are reported explicitly and do not authorize workarounds involving token extraction, cookie/session reuse, or browser credential harvesting.

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
