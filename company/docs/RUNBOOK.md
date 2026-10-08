# Runbook

1. Open a private durable SQLite store through company.runtime.db.connect.
2. Confirm operation is PAUSED_BY_OWNER before migrations or recovery.
3. Register only operation-scoped capabilities supported by evidence.
4. Set budgets, then create fresh grants after any stop generation.
5. Dispatch controlled actions only through ApprovedGateway.execute. Direct Kernel.execute is internal/legacy and not an approved live path.
6. Reconcile UNKNOWN_OUTCOME through ApprovedGateway.reconcile before any retry.
7. Restore from backup only into paused state.
8. Use company.runtime.verified_fx for real cross-currency calculations; legacy ledger conversion is synthetic-only.
9. Keep live provider adapters disabled until enforcement isolation and payment readiness are proven.
