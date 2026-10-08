import json
from .policy import authorize,reserve,consume,release,h
from .states import ActionState

class Kernel:
    def __init__(self,db): self.db=db

    def set_budget(self,venture_id,currency,cap_minor):
        with self.db:
            self.db.execute('INSERT INTO budgets(venture_id,currency,cap_minor,reserved_minor,spent_minor) VALUES(?,?,?,0,0) ON CONFLICT(venture_id,currency) DO UPDATE SET cap_minor=excluded.cap_minor',(venture_id,currency,int(cap_minor)))

    def record_event(self,event_id,idempotency_key,type_,aggregate_id,venture_id,payload,simulated=True,evidence_ref=None):
        try:
            with self.db:
                self.db.execute('INSERT INTO events(id,idempotency_key,type,aggregate_id,venture_id,payload_json,simulated,evidence_ref) VALUES(?,?,?,?,?,?,?,?)',(event_id,idempotency_key,type_,aggregate_id,venture_id,json.dumps(payload,sort_keys=True),int(simulated),evidence_ref))
            return True
        except Exception as e:
            if 'UNIQUE' in str(e): return False
            raise

    def add_obligation(self,oid,venture_id,description,amount_minor=None,currency=None,order_id=None,due_at=None):
        with self.db:
            self.db.execute('INSERT INTO obligations(id,venture_id,order_id,description,due_at,amount_minor,currency) VALUES(?,?,?,?,?,?,?)',(oid,venture_id,order_id,description,due_at,amount_minor,currency))

    def close_obligation(self,oid):
        with self.db:
            self.db.execute("UPDATE obligations SET status='CLOSED' WHERE id=?",(oid,))

    def execute(self,*,action_id,idempotency_key,venture_id,command_type,operation,account,adapter,grant_id,destination=None,amount_minor=0,currency=None,data_scope=None,simulated=True,payload=None):
        existing=self.db.execute('SELECT * FROM actions WHERE idempotency_key=?',(idempotency_key,)).fetchone()
        if existing: return dict(existing)
        authorize(self.db,grant_id=grant_id,venture_id=venture_id,command_type=command_type,operation=operation,account=account,destination=destination,amount_minor=amount_minor,currency=currency,data_scope=data_scope,simulated=simulated)
        if amount_minor and currency: reserve(self.db,grant_id,venture_id,currency,amount_minor)
        try:
            with self.db:
                self.db.execute('INSERT INTO actions(id,idempotency_key,venture_id,command_type,amount_minor,currency,state,grant_id,input_hash,simulated) VALUES(?,?,?,?,?,?,?,?,?,?)',(action_id,idempotency_key,venture_id,command_type,amount_minor,currency,ActionState.RUNNING.value,grant_id,h(payload or {}),int(simulated)))
            result=adapter.dispatch(payload or {})
            if result.get('unknown_after_accept'):
                with self.db:
                    self.db.execute('UPDATE actions SET state=?,provider_ref=?,result_json=? WHERE id=?',(ActionState.UNKNOWN_OUTCOME.value,result.get('provider_ref'),json.dumps(result),action_id))
                return dict(self.db.execute('SELECT * FROM actions WHERE id=?',(action_id,)).fetchone())
            if not result.get('postcondition',False): raise RuntimeError('postcondition not verified')
            if amount_minor and currency: consume(self.db,grant_id,venture_id,currency,amount_minor)
            else:
                with self.db:
                    self.db.execute('UPDATE grants SET uses=uses+1 WHERE id=?',(grant_id,))
            with self.db:
                self.db.execute('UPDATE actions SET state=?,provider_ref=?,result_json=? WHERE id=?',(ActionState.SUCCEEDED.value,result.get('provider_ref'),json.dumps(result),action_id))
            return dict(self.db.execute('SELECT * FROM actions WHERE id=?',(action_id,)).fetchone())
        except Exception:
            if amount_minor and currency: release(self.db,grant_id,venture_id,currency,amount_minor)
            with self.db:
                self.db.execute('UPDATE actions SET state=? WHERE id=?',(ActionState.FAILED.value,action_id))
            raise

    def experiment_gate(self,experiment_id):
        e=self.db.execute('SELECT * FROM experiments WHERE id=?',(experiment_id,)).fetchone()
        if not e: return 'UNKNOWN'
        if e['paid']>=2 and (e['contribution_minor'] or 0)>0: return 'REPEATABILITY_CANDIDATE'
        if e['qualified_contacts']>=20 and e['replies']==0: return 'INCONCLUSIVE_CHANNEL_OR_TARGETING'
        if e['paid']>=1: return 'FIRST_PAYMENT_EVIDENCE'
        return 'VALIDATING'

    def add_cost(self,cid,venture_id,category,amount_minor=0,currency=None,owner_minutes=0,meta_work=False):
        with self.db:
            self.db.execute('INSERT INTO cost_records(id,venture_id,category,amount_minor,currency,owner_minutes,meta_work) VALUES(?,?,?,?,?,?,?)',(cid,venture_id,category,amount_minor,currency,owner_minutes,int(meta_work)))

    def meta_work_ratio(self,venture_id):
        r=self.db.execute('SELECT COALESCE(SUM(owner_minutes),0) t, COALESCE(SUM(CASE WHEN meta_work=1 THEN owner_minutes ELSE 0 END),0) m FROM cost_records WHERE venture_id=?',(venture_id,)).fetchone()
        return None if r['t']==0 else r['m']/r['t']

    def complexity_guard(self, bottleneck, metric):
        if not bottleneck or not metric: raise ValueError('new role/process requires measured bottleneck and target metric')
        return True
