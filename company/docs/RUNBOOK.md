# Runbook

1. Open a private durable SQLite store through company.runtime.db.connect.
2. Confirm operation is PAUSED_BY_OWNER before migrations or recovery.
3. Register only operation-scoped capabilities supported by evidence.
4. Set budgets, then create fresh grants after any stop generation.
5. Dispatch controlled actions only through Kernel.execute.
6. Reconcile UNKNOWN_OUTCOME before retry.
7. Restore from backup only into paused state.
8. Keep live provider adapters disabled until enforcement isolation and payment readiness are proven.
