from datetime import datetime, timezone

REQUIRED_OPERATIONS=(
    'payments.collect',
    'payments.settle',
    'payments.withdraw',
    'payments.refund',
    'payments.reconcile',
)

def assess(db, account, at=None):
    at=at or datetime.now(timezone.utc).isoformat()
    checks={}
    for operation in REQUIRED_OPERATIONS:
        row=db.execute('SELECT status,expires_at FROM capabilities WHERE operation=? AND account=?',(operation,account)).fetchone()
        checks[operation]=bool(row and row['status']=='LIVE_VERIFIED' and (not row['expires_at'] or row['expires_at']>=at))
    return {'ready':all(checks.values()),'account':account,'checks':checks}
