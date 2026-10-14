# Studio Execution Recovery

Status: CANONICAL MEDIA OPERATIONS
Version: 1.0
Date: 2026-10-15

## Purpose

Prevent a frozen, ambiguous or partially completed creative-application action from being mistaken for success or blindly replayed.

This applies to application handoffs such as:
- design/frame tool -> editor;
- editor -> After Effects;
- After Effects -> NLE;
- NLE -> audio finishing;
- audio finishing -> export/QC;
- any GUI/DC/native automation that changes project state.

## Governing invariants

- UNKNOWN != SUCCESS.
- DISPATCHED != VERIFIED.
- Provider success text is not enough for a state-changing action.
- Save before risky handoff; verify after state change.
- Never replay an UNKNOWN action by default.
- Fallback may change the tool, never the required quality gate or authority boundary.
- Do not overwrite unverified work.

## Required checkpoint

Each handoff checkpoint records:
- episode ID;
- production stage;
- action ID;
- application and version;
- project path;
- artifact/project version;
- expected postcondition;
- last verified state;
- next safe action.

## Handoff states

PLANNED
-> APPLICATION_READY
-> PROJECT_OPENED
-> ACTION_DISPATCHED
-> POSTCONDITION_VERIFIED
-> CHECKPOINT_SAVED

Exceptional terminal/intermediate states:
- FAILED
- UNKNOWN

## Recovery sequence

1. Observe the real current application state.
2. Reconcile execution journal and project checkpoint.
3. Resume from the last verified checkpoint.
4. Retry the same route once only if reversible/idempotent.
5. Use an authorized fallback route/tool if available.
6. HOLD and escalate if state remains unknown.

## No-progress behavior

A frozen screen is not a reason to keep clicking.

The controller must:
- use bounded timeouts;
- detect no progress;
- capture diagnostic state;
- avoid blind repeated input;
- preserve the project before recovery whenever possible.

## Owner interruption policy

Routine recovery should not interrupt the Owner.

Owner input is requested only for:
- a material creative/brand conflict;
- owner narration/performance approval;
- credentials, subscription or spend;
- destructive or irreversible action;
- public publication.

## Implementation

- Policy: `company/config/media_venture.json -> execution_recovery`
- Validator/state decisions: `company/runtime/media_execution_recovery.py`
- Durable generic journal/lease: `company/runtime/execution_controls.py`
