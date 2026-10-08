import sqlite3, tempfile, unittest
from pathlib import Path
from company.runtime.db import connect, get_meta
from company.runtime.policy import resume, register_capability, create_grant, PolicyError
from company.runtime.adapters import MockAdapter
from company.runtime.kernel import Kernel
from company.runtime.evidence import add_evidence, is_fresh, require_fresh, EvidenceError
from company.runtime.experiments import update_experiment, ConcurrencyConflict
from company.runtime.ledger import post_entry, balance, reverse_entry, register_fx_rate, convert_minor, LedgerError

class Hardening(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.path=Path(self.t.name)/'db.sqlite'
        self.db=connect(self.path)
    def tearDown(self):
        self.db.close(); self.t.cleanup()

    def test_schema_upgrade_updates_version(self):
        self.db.execute("UPDATE meta SET value='2' WHERE key='schema_version'"); self.db.commit(); self.db.close()
        self.db=connect(self.path)
        self.assertEqual(get_meta(self.db,'schema_version'),'4')

    def test_capability_expiry_blocks_dispatch(self):
        k=Kernel(self.db); k.set_budget('V','USD',1000); resume(self.db)
        register_capability(self.db,'cap','SEND_MESSAGE','mock','WRITE_SANDBOX_VERIFIED',scopes=['synthetic'],expires_at='2000-01-01T00:00:00+00:00')
        create_grant(self.db,'g','V',['SEND_MESSAGE'],destination='x@example.test',data_scopes=['synthetic'],currency='USD',max_uses=1)
        with self.assertRaises(PolicyError):
            k.execute(action_id='a',idempotency_key='i',venture_id='V',command_type='SEND_MESSAGE',operation='SEND_MESSAGE',account='mock',adapter=MockAdapter(),grant_id='g',destination='x@example.test',currency='USD',data_scope='synthetic',payload={})

    def test_evidence_freshness(self):
        add_evidence(self.db,'fresh','claim','AUTHORITATIVE_EXTERNAL','source',expires_at='2999-01-01T00:00:00+00:00')
        add_evidence(self.db,'old','claim','AUTHORITATIVE_EXTERNAL','source',expires_at='2000-01-01T00:00:00+00:00')
        self.assertTrue(is_fresh(self.db,'fresh'))
        self.assertFalse(is_fresh(self.db,'old'))
        with self.assertRaises(EvidenceError): require_fresh(self.db,'old')

    def test_optimistic_concurrency_rejects_stale_writer(self):
        with self.db:
            self.db.execute("INSERT INTO experiments(id,venture_id,version,state) VALUES('e','V',1,'VALIDATION')")
        updated=update_experiment(self.db,'e',1,replies=1)
        self.assertEqual(updated['version'],2)
        with self.assertRaises(ConcurrencyConflict):
            update_experiment(self.db,'e',1,replies=2)

    def test_ledger_reversal_preserves_history(self):
        post_entry(self.db,'j1','sale',[{'account':'Cash','currency':'USD','debit_minor':1000},{'account':'Revenue','currency':'USD','credit_minor':1000}])
        reverse_entry(self.db,'j1','j2','ev')
        self.assertEqual(balance(self.db,'Cash','USD'),0)
        self.assertEqual(self.db.execute("SELECT COUNT(*) n FROM ledger_entries").fetchone()['n'],2)
        with self.assertRaises(LedgerError): reverse_entry(self.db,'j1','j3','ev')

    def test_fx_requires_fresh_evidence(self):
        with self.assertRaises(LedgerError):
            register_fx_rate(self.db,'r0','IQD','USD','0.00076','missing')
        add_evidence(self.db,'fxev','rate','AUTHORITATIVE_EXTERNAL','central-source',expires_at='2999-01-01T00:00:00+00:00')
        register_fx_rate(self.db,'r1','IQD','USD','0.00076','fxev',expires_at='2999-01-01T00:00:00+00:00')
        self.assertEqual(convert_minor(self.db,100000,'IQD','USD','r1'),76)

    def test_fx_expired_evidence_blocks_conversion(self):
        add_evidence(self.db,'oldfx','rate','AUTHORITATIVE_EXTERNAL','central-source',expires_at='2000-01-01T00:00:00+00:00')
        with self.assertRaises(LedgerError):
            register_fx_rate(self.db,'r2','IQD','USD','0.00076','oldfx',expires_at='2999-01-01T00:00:00+00:00')

if __name__=='__main__': unittest.main()
