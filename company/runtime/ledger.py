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
