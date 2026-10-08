from decimal import Decimal, ROUND_HALF_EVEN
from datetime import datetime, timezone

class LedgerError(ValueError): pass

def post_entry(db, entry_id, kind, lines, evidence_ref=None, reversal_of=None):
    by_cur={}
    for ln in lines:
        cur=ln['currency']; by_cur.setdefault(cur,[0,0]); by_cur[cur][0]+=int(ln.get('debit_minor',0)); by_cur[cur][1]+=int(ln.get('credit_minor',0))
    bad={c:v for c,v in by_cur.items() if v[0]!=v[1]}
    if bad: raise LedgerError(f'unbalanced currencies: {bad}')
    with db:
        db.execute('INSERT INTO ledger_entries(id,kind,evidence_ref,reversal_of) VALUES(?,?,?,?)',(entry_id,kind,evidence_ref,reversal_of))
        db.executemany('INSERT INTO ledger_lines(entry_id,account,currency,debit_minor,credit_minor) VALUES(?,?,?,?,?)',[(entry_id,l['account'],l['currency'],int(l.get('debit_minor',0)),int(l.get('credit_minor',0))) for l in lines])

def balance(db, account, currency):
    r=db.execute('SELECT COALESCE(SUM(debit_minor-credit_minor),0) x FROM ledger_lines WHERE account=? AND currency=?',(account,currency)).fetchone(); return int(r['x'])

def nocg(db,currency):
    receipts=balance(db,'Cash',currency)
    owner=balance(db,'Owner Capital',currency)
    return receipts+owner

def reverse_entry(db, original_entry_id, reversal_entry_id, evidence_ref=None):
    original=db.execute('SELECT id FROM ledger_entries WHERE id=?',(original_entry_id,)).fetchone()
    if not original: raise LedgerError('original entry not found')
    if db.execute('SELECT 1 FROM ledger_entries WHERE reversal_of=?',(original_entry_id,)).fetchone():
        raise LedgerError('entry already reversed')
    lines=db.execute('SELECT account,currency,debit_minor,credit_minor FROM ledger_lines WHERE entry_id=?',(original_entry_id,)).fetchall()
    if not lines: raise LedgerError('original entry has no lines')
    return post_entry(db,reversal_entry_id,'reversal',[
        {'account':r['account'],'currency':r['currency'],'debit_minor':r['credit_minor'],'credit_minor':r['debit_minor']}
        for r in lines
    ],evidence_ref=evidence_ref,reversal_of=original_entry_id)

def register_fx_rate(db, rate_id, source_currency, target_currency, rate_text, evidence_ref, effective_at=None, expires_at=None):
    ev=db.execute('SELECT * FROM evidence WHERE id=?',(evidence_ref,)).fetchone()
    if not ev: raise LedgerError('FX rate requires evidence')
    now=datetime.now(timezone.utc).isoformat()
    if ev['expires_at'] and ev['expires_at'] < now: raise LedgerError('FX evidence expired')
    with db:
        db.execute('INSERT INTO fx_rates(id,source_currency,target_currency,rate_text,evidence_ref,effective_at,expires_at) VALUES(?,?,?,?,?,?,?)',
                   (rate_id,source_currency,target_currency,str(rate_text),evidence_ref,effective_at,expires_at))

def convert_minor(db, amount_minor, source_currency, target_currency, rate_id):
    r=db.execute('SELECT * FROM fx_rates WHERE id=? AND source_currency=? AND target_currency=?',(rate_id,source_currency,target_currency)).fetchone()
    if not r: raise LedgerError('verified FX rate unavailable')
    now=datetime.now(timezone.utc).isoformat()
    ev=db.execute('SELECT * FROM evidence WHERE id=?',(r['evidence_ref'],)).fetchone()
    if not ev: raise LedgerError('FX evidence missing')
    if (r['expires_at'] and r['expires_at'] < now) or (ev['expires_at'] and ev['expires_at'] < now):
        raise LedgerError('FX evidence expired')
    return int((Decimal(int(amount_minor))*Decimal(r['rate_text'])).quantize(Decimal('1'),rounding=ROUND_HALF_EVEN))
