# Incidents and Recovery

Unknown remote outcome is never blindly retried. Provider state must be reconciled first.

Critical risk may pause immediately. Resume requires fresh grants. Restore always comes up paused and invalidates pre-restore grants.

Operational health should surface unresolved UNKNOWN_OUTCOME, cash discrepancies, stale evidence, expired grants, overdue blocked tasks, and backup state.

A healthy dashboard cannot override contradictory external evidence.
