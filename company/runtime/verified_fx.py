from datetime import datetime, timezone
from .currency import convert_minor as convert_precision_aware
from .evidence import require_fresh

class VerifiedFXError(ValueError):
    pass

def convert_minor(db, amount_minor, source_currency, target_currency, rate_id, at=None):
    at = at or datetime.now(timezone.utc).isoformat()
    row = db.execute(
        "SELECT * FROM fx_rates WHERE id=? AND source_currency=? AND target_currency=?",
        (rate_id, source_currency, target_currency),
    ).fetchone()
    if not row:
        raise VerifiedFXError("verified FX rate unavailable")
    if row["expires_at"] and row["expires_at"] < at:
        raise VerifiedFXError("FX rate expired")
    require_fresh(db, row["evidence_ref"], at)
    return convert_precision_aware(
        amount_minor, source_currency, target_currency, row["rate_text"]
    )
