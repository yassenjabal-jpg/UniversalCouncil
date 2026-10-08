import tempfile, unittest
from pathlib import Path
from company.runtime.db import connect
from company.runtime.health import snapshot, clears_live_slo
from company.runtime.payment_readiness import assess, REQUIRED_OPERATIONS
from company.runtime.kernel import Kernel
from company.runtime.policy import register_capability

class OperationalHardening(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.db=connect(Path(self.t.name)/'db.sqlite')
    def tearDown(self):
        self.db.close(); self.t.cleanup()

    def test_health_is_watch_on_stale_evidence(self):
        with self.db:
            self.db.execute("INSERT INTO evidence(id,claim,evidence_type,source,expires_at) VALUES('e','c','AUTHORITATIVE_EXTERNAL','s','2000-01-01T00:00:00+00:00')")
        self.assertEqual(snapshot(self.db)['health'],'WATCH')

    def test_health_is_distressed_on_unknown_outcome(self):
        with self.db:
            self.db.execute("INSERT INTO actions(id,idempotency_key,venture_id,command_type,state,input_hash) VALUES('a','i','V','X','UNKNOWN_OUTCOME','h')")
        s=snapshot(self.db)
        self.assertEqual(s['health'],'DISTRESSED')
        self.assertFalse(clears_live_slo(self.db))

    def test_payment_readiness_fails_closed(self):
        self.assertFalse(assess(self.db,'acct')['ready'])

    def test_payment_readiness_requires_every_operation(self):
        for op in REQUIRED_OPERATIONS[:-1]:
            register_capability(self.db,op,op,'acct','LIVE_VERIFIED',expires_at='2999-01-01T00:00:00+00:00')
        self.assertFalse(assess(self.db,'acct')['ready'])
        op=REQUIRED_OPERATIONS[-1]
        register_capability(self.db,op,op,'acct','LIVE_VERIFIED',expires_at='2999-01-01T00:00:00+00:00')
        self.assertTrue(assess(self.db,'acct')['ready'])

    def test_budget_cap_update_preserves_exposure(self):
        k=Kernel(self.db)
        k.set_budget('V','USD',10000)
        with self.db:
            self.db.execute("UPDATE budgets SET reserved_minor=2000, spent_minor=3000 WHERE venture_id='V' AND currency='USD'")
        k.set_budget('V','USD',12000)
        row=self.db.execute("SELECT * FROM budgets WHERE venture_id='V' AND currency='USD'").fetchone()
        self.assertEqual((row['cap_minor'],row['reserved_minor'],row['spent_minor']),(12000,2000,3000))

    def test_payment_readiness_expires(self):
        for op in REQUIRED_OPERATIONS:
            register_capability(self.db,op,op,'acct','LIVE_VERIFIED',expires_at='2000-01-01T00:00:00+00:00')
        self.assertFalse(assess(self.db,'acct')['ready'])

if __name__=='__main__': unittest.main()
