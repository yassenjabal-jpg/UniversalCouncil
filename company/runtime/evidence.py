from datetime import datetime, timezone

class EvidenceError(ValueError):
    pass

def add_evidence(db, evidence_id, claim, evidence_type, source, observed_at=None, expires_at=None, hash_value=None, restricted=False):
    with db:
        db.execute(
            'INSERT INTO evidence(id,claim,evidence_type,source,observed_at,expires_at,hash,restricted) VALUES(?,?,?,?,?,?,?,?)',
            (evidence_id, claim, evidence_type, source, observed_at, expires_at, hash_value, int(restricted)),
        )

def is_fresh(db, evidence_id, at=None):
    at = at or datetime.now(timezone.utc).isoformat()
    row = db.execute('SELECT * FROM evidence WHERE id=?',(evidence_id,)).fetchone()
    return bool(row and (not row['expires_at'] or row['expires_at'] >= at))

def require_fresh(db, evidence_id, at=None):
    if not is_fresh(db, evidence_id, at):
        raise EvidenceError('evidence missing or expired')
    return db.execute('SELECT * FROM evidence WHERE id=?',(evidence_id,)).fetchone()
