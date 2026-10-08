# Stage 0 Hardening Review — 2026-10-08

## Verdict

**PASS for Stage 0 infrastructure. LIVE remains blocked pending external activation evidence.**

The branch is cleanly mergeable into main and CI is green, but this review does not authorize live commercial operation.

## Verified in code + CI

- Universal Council v0.3 regression validator remains green.
- Stage 0 deterministic suite plus hardening suites are green.
- Schema migration now records the current schema version instead of leaving an old value behind.
- Operation-scoped capability expiry is enforced.
- Evidence freshness has explicit helpers and expiry checks.
- Optimistic concurrency rejects stale experiment writers.
- Ledger corrections preserve history through reversal entries.
- FX conversion requires a stored rate backed by non-expired evidence.
- Operational health reports WATCH/DISTRESSED for stale evidence, expired capabilities, overdue obligations, unresolved outcomes, or ledger imbalance.
- Payment Readiness fails closed unless collect/settle/withdraw/refund/reconcile capabilities for the same account are all LIVE_VERIFIED and fresh.
- Budget cap updates preserve prior reserved/spent exposure.
- Budget caps cannot be lowered below current exposure.
- Existing owner-pause, grants, unknown-outcome, accounting, restore, synthetic vertical-slice, anti-meta-work, and public-data controls remain covered.

## Findings discovered during hardening

1. Schema version was previously insert-only and could remain stale after migration. Fixed.
2. Capability expiry was stored but not enforced before dispatch. Fixed.
3. Budget cap updates previously used replace semantics that could erase reserved/spent exposure. Fixed.
4. Unknown-outcome monetary exposure had already been hardened before this review to remain reserved against budget and grant caps.
5. Non-financial UNKNOWN_OUTCOME max-use exposure is enforced in ApprovedGateway and retained until reconciliation. Fixed.
6. ApprovedGateway rejects negative action amounts and negative grant limits. Fixed.
7. ApprovedGateway.reconcile resolves UNKNOWN_OUTCOME by atomically consuming or releasing the reserved exposure. Fixed.
8. Cross-currency conversion now uses a precision-aware path for IQD and USD and requires fresh stored FX evidence through verified_fx. Fixed for the current operating currencies.

## Acceptance boundary

Stage 0 may be treated as an internally tested bounded operating kernel, not a live autonomous company.

Before live activation, all of the following still require evidence:
- real action-gateway isolation from direct connector bypass;
- durable private operational storage;
- real provider/account capability verification;
- complete payment readiness;
- fresh owner mandate after PAUSED_BY_OWNER;
- real buyer evidence and tested delivery economics.

## External Reality Supremacy

No CI result, internal dashboard, council vote, or architecture review can substitute for verified external customer behavior, accepted delivery, or reconciled provider/payment state.
