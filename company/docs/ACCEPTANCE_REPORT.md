# Stage 0 Acceptance Report

Isolated verification completed before upload:
- Stage 0 behavioral, hardening, operational-health, payment-readiness, and budget-invariant suites passed in GitHub Actions.
- Universal Council v0.3 configuration validator remained green: 8 core roles, 16 specialists, 14 routing rules, 3 modes, pulse enabled.
- Python compileall passed for the company package.

The test suites cover owner pause/grants, capability gates and expiry, aggregate budget/grant exposure, unknown outcomes, event dedupe, accounting, immutable reversals, evidence-backed FX, evidence freshness, schema migration, optimistic concurrency, payment readiness, operational health, budget exposure preservation, currency isolation, owner funding exclusion from NOCG, experiment gates, sensitive export, complexity budget, paused restore, full synthetic vertical slice, and meta-work measurement. Final acceptance adds the sanctioned ApprovedGateway, full UNKNOWN_OUTCOME reconciliation, non-negative financial invariants, and precision-aware evidence-backed IQD/USD conversion. See HARDENING_REPORT.md for live-activation dependencies.

Live provider paths remain intentionally unaccepted.
