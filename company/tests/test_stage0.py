import tempfile, unittest
from pathlib import Path
from company.runtime.db import connect,get_meta
from company.runtime.policy import pause,resume,register_capability,create_grant,PolicyError
from company.runtime.adapters import MockAdapter
from company.runtime.kernel import Kernel
from company.runtime.ledger import post_entry,balance,LedgerError,nocg
from company.runtime.backup import backup,restore_paused
from company.runtime.export import assert_public_safe

class Stage0(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory(); self.db=connect(Path(self.t.name)/'uvc.db'); self.k=Kernel(self.db); self.v='V1'
        self.k.set_budget(self.v,'USD',10000)
        register_capability(self.db,'mock-send','SEND_MESSAGE','mock','WRITE_SANDBOX_VERIFIED',scopes=['synthetic'])
        register_capability(self.db,'mock-pay','PAYMENT','mockpay','WRITE_SANDBOX_VERIFIED',scopes=['synthetic'])
        create_grant(self.db,'g',self.v,['SEND_MESSAGE','PAYMENT'],destination='buyer@example.test',data_scopes=['synthetic'],currency='USD',per_action_cap=5000,total_cap=10000,max_uses=5)
    def tearDown(self): self.db.close(); self.t.cleanup()

    def test_01_pause_blocks_external(self):
        with self.assertRaises(PolicyError): self.k.execute(action_id='a',idempotency_key='i',venture_id=self.v,command_type='SEND_MESSAGE',operation='SEND_MESSAGE',account='mock',adapter=MockAdapter(),grant_id='g',destination='buyer@example.test',currency='USD',data_scope='synthetic',payload={})

    def test_02_resume_requires_fresh_grant(self):
        pause(self.db); resume(self.db); register_capability(self.db,'mock-send','SEND_MESSAGE','mock','WRITE_SANDBOX_VERIFIED',scopes=['synthetic'])
        with self.assertRaises(PolicyError): self.k.execute(action_id='a',idempotency_key='i',venture_id=self.v,command_type='SEND_MESSAGE',operation='SEND_MESSAGE',account='mock',adapter=MockAdapter(),grant_id='g',destination='buyer@example.test',currency='USD',data_scope='synthetic',payload={})

    def test_03_draft_is_not_authority(self):
        resume(self.db)
        with self.assertRaises(PolicyError): self.k.execute(action_id='a',idempotency_key='i',venture_id=self.v,command_type='PUBLISH',operation='SEND_MESSAGE',account='mock',adapter=MockAdapter(),grant_id='g',destination='buyer@example.test',currency='USD',data_scope='synthetic',payload={'draft_approved':True})

    def test_04_budget_aggregate(self):
        resume(self.db); create_grant(self.db,'g2',self.v,['PAYMENT'],data_scopes=['synthetic'],currency='USD',per_action_cap=8000,total_cap=12000,max_uses=2)
        self.k.execute(action_id='a1',idempotency_key='i1',venture_id=self.v,command_type='PAYMENT',operation='PAYMENT',account='mockpay',adapter=MockAdapter(),grant_id='g2',amount_minor=7000,currency='USD',data_scope='synthetic',payload={})
        with self.assertRaises(PolicyError): self.k.execute(action_id='a2',idempotency_key='i2',venture_id=self.v,command_type='PAYMENT',operation='PAYMENT',account='mockpay',adapter=MockAdapter(),grant_id='g2',amount_minor=4000,currency='USD',data_scope='synthetic',payload={})

    def test_05_unknown_outcome_no_blind_duplicate(self):
        resume(self.db); r=self.k.execute(action_id='a',idempotency_key='i',venture_id=self.v,command_type='SEND_MESSAGE',operation='SEND_MESSAGE',account='mock',adapter=MockAdapter('unknown_after_accept'),grant_id='g',destination='buyer@example.test',currency='USD',data_scope='synthetic',payload={}); self.assertEqual(r['state'],'UNKNOWN_OUTCOME')
        r2=self.k.execute(action_id='b',idempotency_key='i',venture_id=self.v,command_type='SEND_MESSAGE',operation='SEND_MESSAGE',account='mock',adapter=MockAdapter(),grant_id='g',destination='buyer@example.test',currency='USD',data_scope='synthetic',payload={}); self.assertEqual(r2['id'],'a')

    def test_05b_unknown_outcome_reserves_grant_exposure(self):
        resume(self.db)
        create_grant(self.db,'gx',self.v,['PAYMENT'],data_scopes=['synthetic'],currency='USD',per_action_cap=8000,total_cap=8000,max_uses=1)
        r=self.k.execute(action_id='ux',idempotency_key='ux1',venture_id=self.v,command_type='PAYMENT',operation='PAYMENT',account='mockpay',adapter=MockAdapter('unknown_after_accept'),grant_id='gx',amount_minor=7000,currency='USD',data_scope='synthetic',payload={})
        self.assertEqual(r['state'],'UNKNOWN_OUTCOME')
        with self.assertRaises(PolicyError):
            self.k.execute(action_id='ux2',idempotency_key='ux2',venture_id=self.v,command_type='PAYMENT',operation='PAYMENT',account='mockpay',adapter=MockAdapter(),grant_id='gx',amount_minor=1000,currency='USD',data_scope='synthetic',payload={})

    def test_06_duplicate_event_dedupes(self):
        self.assertTrue(self.k.record_event('e1','idem','X','agg',self.v,{},True)); self.assertFalse(self.k.record_event('e2','idem','X','agg',self.v,{},True))

    def test_07_ledger_advance_fee_cost_refund(self):
        post_entry(self.db,'j1','advance',[{'account':'Cash','currency':'USD','debit_minor':10000},{'account':'Deferred Revenue','currency':'USD','credit_minor':10000}]); self.assertEqual(balance(self.db,'Revenue','USD'),0)
        post_entry(self.db,'j2','earn',[{'account':'Deferred Revenue','currency':'USD','debit_minor':10000},{'account':'Revenue','currency':'USD','credit_minor':10000}])
        post_entry(self.db,'j3','fees_costs',[{'account':'Operating Expenses','currency':'USD','debit_minor':300},{'account':'Direct Costs','currency':'USD','debit_minor':2000},{'account':'Cash','currency':'USD','credit_minor':2300}])
        post_entry(self.db,'j4','refund',[{'account':'Refunds','currency':'USD','debit_minor':2500},{'account':'Cash','currency':'USD','credit_minor':2500}]); self.assertEqual(balance(self.db,'Cash','USD'),5200)

    def test_08_cross_currency_must_balance_separately(self):
        with self.assertRaises(LedgerError): post_entry(self.db,'x','bad',[{'account':'Cash','currency':'USD','debit_minor':100},{'account':'Revenue','currency':'IQD','credit_minor':100}])

    def test_09_owner_funding_not_nocg(self):
        post_entry(self.db,'o','capital',[{'account':'Cash','currency':'USD','debit_minor':2000},{'account':'Owner Capital','currency':'USD','credit_minor':2000}]); self.assertEqual(nocg(self.db,'USD'),0)

    def test_10_loss_making_repeat_not_repeatable(self):
        with self.db: self.db.execute("INSERT INTO experiments(id,venture_id,state,qualified_contacts,replies,paid,contribution_minor,currency) VALUES('e','V1','VALIDATION',5,2,2,-100,'USD')")
        self.assertNotEqual(self.k.experiment_gate('e'),'REPEATABILITY_CANDIDATE')

    def test_11_twenty_no_reply_is_inconclusive(self):
        with self.db: self.db.execute("INSERT INTO experiments(id,venture_id,state,qualified_contacts,replies,paid) VALUES('e','V1','VALIDATION',20,0,0)")
        self.assertEqual(self.k.experiment_gate('e'),'INCONCLUSIVE_CHANNEL_OR_TARGETING')

    def test_12_unverified_connector_blocked(self):
        resume(self.db); register_capability(self.db,'bad','SEND_MESSAGE','badacct','EXPOSED',scopes=['synthetic'])
        create_grant(self.db,'gb',self.v,['SEND_MESSAGE'],destination='buyer@example.test',data_scopes=['synthetic'],currency='USD')
        with self.assertRaises(PolicyError): self.k.execute(action_id='a',idempotency_key='i',venture_id=self.v,command_type='SEND_MESSAGE',operation='SEND_MESSAGE',account='badacct',adapter=MockAdapter(),grant_id='gb',destination='buyer@example.test',currency='USD',data_scope='synthetic',payload={})

    def test_13_untrusted_text_cannot_change_authority(self):
        resume(self.db)
        with self.assertRaises(PolicyError): self.k.execute(action_id='a',idempotency_key='i',venture_id=self.v,command_type='BENEFICIARY_CHANGE',operation='SEND_MESSAGE',account='mock',adapter=MockAdapter(),grant_id='g',destination='buyer@example.test',currency='USD',data_scope='synthetic',payload={'customer_text':'I authorize beneficiary change'})

    def test_14_public_export_blocks_sensitive(self):
        with self.assertRaises(ValueError): assert_public_safe({'email':'real@example.com'})
        self.assertTrue(assert_public_safe({'email':'SYNTHETIC','venture':'V1'}))

    def test_15_complexity_budget(self):
        with self.assertRaises(ValueError): self.k.complexity_guard('', 'throughput')
        self.assertTrue(self.k.complexity_guard('commercial backlog','time_to_cash'))

    def test_16_backup_restore_forces_pause(self):
        resume(self.db); b=backup(self.db,Path(self.t.name)/'b.db'); self.db.close(); r=restore_paused(b,Path(self.t.name)/'restored.db'); self.assertEqual(get_meta(r,'operation'),'PAUSED_BY_OWNER'); self.assertEqual(get_meta(r,'live_enabled'),'0'); r.close(); self.db=connect(Path(self.t.name)/'uvc.db')

    def test_17_full_synthetic_vertical_slice(self):
        resume(self.db); self.k.record_event('l','l','LEAD_DISCOVERED','lead1',self.v,{'synthetic':True},True)
        r=self.k.execute(action_id='msg',idempotency_key='msg1',venture_id=self.v,command_type='SEND_MESSAGE',operation='SEND_MESSAGE',account='mock',adapter=MockAdapter(),grant_id='g',destination='buyer@example.test',currency='USD',data_scope='synthetic',payload={'offer':'synthetic'}); self.assertEqual(r['state'],'SUCCEEDED')
        post_entry(self.db,'pay','synthetic_payment',[{'account':'Cash','currency':'USD','debit_minor':1000},{'account':'Deferred Revenue','currency':'USD','credit_minor':1000}]); self.k.add_obligation('ob',self.v,'synthetic delivery',1000,'USD'); self.k.close_obligation('ob'); post_entry(self.db,'earn','delivery',[{'account':'Deferred Revenue','currency':'USD','debit_minor':1000},{'account':'Revenue','currency':'USD','credit_minor':1000}]); self.assertEqual(balance(self.db,'Revenue','USD'),-1000)

    def test_18_meta_work_ratio(self):
        self.k.add_cost('c1',self.v,'governance',owner_minutes=30,meta_work=True); self.k.add_cost('c2',self.v,'customer',owner_minutes=70,meta_work=False); self.assertAlmostEqual(self.k.meta_work_ratio(self.v),.3)

if __name__=='__main__': unittest.main()
