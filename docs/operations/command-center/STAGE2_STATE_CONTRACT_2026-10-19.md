# Command Center — Stage 2 Operational State Contract
Date: 2026-10-19
Status: OPEN / OWNER-AUTHORIZED
Branch: command-center/stage2-operational-state
Parent product SHA: 0d3b89e81c001fe0ccfc23f502bb17ae9e114a9f
Parent lock: COMMAND_CENTER_STAGE1_SHELL_LOCK

## Mission
Replace the Stage 1 prototype read model with a real, read-only operational state pipeline.

Stage 2 must make project state, evidence receipts, owner approvals, usage status and execution-manifest status visible without granting execution authority.

## Owner authorization
The owner explicitly instructed the project to continue after Stage 1 lock on 2026-10-19.

This authorizes opening Stage 2 only.

It does not authorize:
- shell/process execution;
- GUI automation;
- remote commands;
- model-provider calls;
- credentials;
- provider fallback;
- approval writes;
- filesystem mutation from Presentation.

## Architecture
Presentation
  -> Host/Composition
      -> Application
          -> Infrastructure read-only adapter
              -> command-center-state.json

Rules:
- Presentation may reference Core and Host only.
- Presentation may not reference Infrastructure.
- Application may not reference WPF.
- Infrastructure implements Application read contracts.
- state read failures fail closed and remain visible to the owner.
- execution remains false regardless of state-file content until a later execution-authority stage.

## State source
Stage 2 uses a real runtime JSON read model copied beside the published application.

The document is:
- versioned;
- schema validated;
- read-only to this application stage;
- explicit about source/baseline;
- explicit about unavailable model/cost data;
- explicit about Phase 0 execution lock.

The bundled Stage 2 document is a repository projection, not production telemetry.

## Required projections
1. Project/stage state.
2. Evidence receipts.
3. Owner approval ledger.
4. Usage/cost connection status.
5. Execution manifest status.
6. Shell/module connectivity derived from the state projection.

## Truthfulness rules
- missing state file => UNAVAILABLE, never READY;
- malformed state => UNAVAILABLE, never partial success;
- unsupported schema => UNAVAILABLE;
- unconnected usage source => show NOT CONNECTED, not $0;
- no execution manifest => show NO EXECUTION AUTHORIZED;
- owner approval display is read-only in Stage 2;
- Phase 0 lock remains visible at all times.

## Acceptance
Stage 2 may lock only when:
1. Presentation references Core + Host only.
2. read model is loaded at runtime from JSON through Infrastructure.
3. fail-closed missing/malformed-state tests pass.
4. execution remains disabled even if a hostile state document claims otherwise.
5. exact-head Windows CI passes.
6. exact-size 1440×900 and 1180×720 UI evidence exists.
7. Council security/architecture/reliability review passes.
8. Studio workflow/visual-density review passes.
9. Stage 3 remains unopened until this stage is locked.

Exit:
COMMAND_CENTER_STAGE2_STATE_LOCK
