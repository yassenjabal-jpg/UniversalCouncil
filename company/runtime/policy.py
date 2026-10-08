import json, hashlib
from datetime import datetime, timezone
from .db import get_meta, set_meta
from .states import CapabilityStatus

EXTERNAL={'SEND_MESSAGE','PUBLISH','PURCHASE','REFUND','PAYMENT','BENEFICIARY_CHANGE'}
class PolicyError(PermissionError): pass

def now_iso(): return datetime.now(timezone.utc).isoformat()
def h(obj): return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def pause(db):
    with db:
        gen=int(get_meta(db,'stop_generation','1'))+1
        set_meta(db,'stop_generation',gen)
        set_meta(db,'operation','PAUSED_BY_OWNER')
        set_meta(db,'live_enabled','0')
        db.execute('UPDATE grants SET revoked=1')
    return gen

def resume(db, bounded_live=False):
    with db:
        set_meta(db,'operation','RUNNING')
        set_meta(db,'live_enabled','1' if bounded_live else '0')

def register_capability(db, cap_id, operation, account, status, scopes=(), **kw):
    with db:
        db.execute('INSERT OR REPLACE INTO capabilities(id,operation,account,status,scopes_json,last_test,expires_at,cost_minor,currency) VALUES(?,?,?,?,?,?,?,?,?)',(cap_id,operation,account,status,json.dumps(list(scopes)),kw.get('last_test'),kw.get('expires_at'),int(kw.get('cost_minor',0)),kw.get('currency')))

def create_grant(db, grant_id, venture_id, commands, *, channel=None,destination=None,data_scopes=(),payee=None,currency=None,per_action_cap=None,total_cap=None,max_uses=None,expires_at=None):
    generation=int(get_meta(db,'stop_generation','1'))
    with db:
        db.execute('INSERT INTO grants(id,generation,venture_id,commands_json,channel,destination,data_scopes_json,payee,currency,per_action_cap,total_cap,max_uses,expires_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',(grant_id,generation,venture_id,json.dumps(list(commands)),channel,destination,json.dumps(list(data_scopes)),payee,currency,per_action_cap,total_cap,max_uses,expires_at))

def _grant(db, grant_id):
    g=db.execute('SELECT * FROM grants WHERE id=?',(grant_id,)).fetchone()
    if not g: raise PolicyError('missing grant')
    if g['revoked'] or g['generation']!=int(get_meta(db,'stop_generation','1')): raise PolicyError('stale or revoked grant')
    if g['expires_at'] and g['expires_at'] < now_iso(): raise PolicyError('expired grant')
    return g

def authorize(db, *, grant_id, venture_id, command_type, operation, account, destination=None, amount_minor=0, currency=None, data_scope=None, simulated=True):
    if command_type in EXTERNAL and get_meta(db,'operation')!='RUNNING': raise PolicyError('owner pause blocks external action')
    if command_type in EXTERNAL and not simulated and get_meta(db,'live_enabled')!='1': raise PolicyError('live execution disabled')
    g=_grant(db,grant_id)
    if g['venture_id']!=venture_id or command_type not in json.loads(g['commands_json']): raise PolicyError('grant scope mismatch')
    if g['destination'] and destination!=g['destination']: raise PolicyError('destination mismatch')
    if g['currency'] and currency!=g['currency']: raise PolicyError('currency mismatch')
    if data_scope and data_scope not in json.loads(g['data_scopes_json']): raise PolicyError('data scope mismatch')
    if g['per_action_cap'] is not None and amount_minor>g['per_action_cap']: raise PolicyError('per-action cap exceeded')
    if g['total_cap'] is not None and g['used_amount']+g['reserved_amount']+amount_minor>g['total_cap']: raise PolicyError('grant total cap exceeded')
    if g['max_uses'] is not None and g['uses']+g['reserved_uses']>=g['max_uses']: raise PolicyError('grant use limit exceeded')
    c=db.execute('SELECT * FROM capabilities WHERE operation=? AND account=?',(operation,account)).fetchone()
    if not c: raise PolicyError('capability not registered')
    allowed={CapabilityStatus.WRITE_SANDBOX_VERIFIED.value} if simulated else {CapabilityStatus.LIVE_VERIFIED.value}
    if c['status'] not in allowed: raise PolicyError(f'capability not ready: {c["status"]}')
    return g

def reserve(db, grant_id, venture_id,currency,amount_minor):
    with db:
        b=db.execute('SELECT * FROM budgets WHERE venture_id=? AND currency=?',(venture_id,currency)).fetchone()
        if not b or b['spent_minor']+b['reserved_minor']+amount_minor>b['cap_minor']: raise PolicyError('budget exceeded')
        db.execute('UPDATE budgets SET reserved_minor=reserved_minor+? WHERE venture_id=? AND currency=?',(amount_minor,venture_id,currency))
        db.execute('UPDATE grants SET reserved_amount=reserved_amount+?, reserved_uses=reserved_uses+1 WHERE id=?',(amount_minor,grant_id))

def consume(db, grant_id, venture_id,currency,amount_minor):
    with db:
        db.execute('UPDATE grants SET reserved_amount=MAX(0,reserved_amount-?), reserved_uses=MAX(0,reserved_uses-1), used_amount=used_amount+?, uses=uses+1 WHERE id=?',(amount_minor,amount_minor,grant_id))
        db.execute('UPDATE budgets SET reserved_minor=reserved_minor-?, spent_minor=spent_minor+? WHERE venture_id=? AND currency=?',(amount_minor,amount_minor,venture_id,currency))

def release(db,grant_id,venture_id,currency,amount_minor):
    with db:
        db.execute('UPDATE budgets SET reserved_minor=MAX(0,reserved_minor-?) WHERE venture_id=? AND currency=?',(amount_minor,venture_id,currency))
        db.execute('UPDATE grants SET reserved_amount=MAX(0,reserved_amount-?), reserved_uses=MAX(0,reserved_uses-1) WHERE id=?',(amount_minor,grant_id))
