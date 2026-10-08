from datetime import datetime, timezone
from .db import get_meta

def snapshot(db, at=None):
    at=at or datetime.now(timezone.utc).isoformat()
    unknown=db.execute("SELECT COUNT(*) n FROM actions WHERE state='UNKNOWN_OUTCOME'").fetchone()['n']
    expired_caps=db.execute("SELECT COUNT(*) n FROM capabilities WHERE expires_at IS NOT NULL AND expires_at < ?",(at,)).fetchone()['n']
    stale_evidence=db.execute("SELECT COUNT(*) n FROM evidence WHERE expires_at IS NOT NULL AND expires_at < ?",(at,)).fetchone()['n']
    overdue=db.execute("SELECT COUNT(*) n FROM obligations WHERE status='OPEN' AND due_at IS NOT NULL AND due_at < ?",(at,)).fetchone()['n']
    imbalances=db.execute("""
        SELECT COUNT(*) n FROM (
          SELECT entry_id,currency,SUM(debit_minor) d,SUM(credit_minor) c
          FROM ledger_lines GROUP BY entry_id,currency HAVING d<>c
        )
    """).fetchone()['n']
    if unknown or imbalances:
        health='DISTRESSED'
    elif expired_caps or stale_evidence or overdue:
        health='WATCH'
    else:
        health='HEALTHY'
    return {
        'health':health,
        'operation':get_meta(db,'operation'),
        'live_enabled':get_meta(db,'live_enabled')=='1',
        'unknown_outcomes':unknown,
        'expired_capabilities':expired_caps,
        'stale_evidence':stale_evidence,
        'overdue_obligations':overdue,
        'ledger_imbalances':imbalances,
    }

def clears_live_slo(db, at=None):
    s=snapshot(db,at)
    return s['health']=='HEALTHY' and s['unknown_outcomes']==0 and s['ledger_imbalances']==0
