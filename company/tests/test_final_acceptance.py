import tempfile, unittest
from pathlib import Path

from company.runtime.db import connect
from company.runtime.policy import resume, register_capability
from company.runtime.adapters import MockAdapter
from company.runtime.approved_gateway import ApprovedGateway, GatewayError
from company.runtime.states import ActionState
from company.runtime.evidence import add_evidence
from company.runtime.ledger import register_fx_rate
from company.runtime.verified_fx import convert_minor as verified_convert
from company.runtime.currency import convert_minor as convert_currency, CurrencyError

class FinalAcceptance(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.db=connect(Path(self.t.name)/"db.sqlite")
        self.gw=ApprovedGateway(self.db)
        with self.db:
            self.db.execute(
                "INSERT INTO budgets(venture_id,currency,cap_minor,reserved_minor,spent_minor) VALUES('V','USD',10000,0,0)"
            )
        register_capability(
            self.db,"send","SEND_MESSAGE","mock","WRITE_SANDBOX_VERIFIED",
            scopes=["synthetic"],expires_at="2999-01-01T00:00:00+00:00"
        )
        register_capability(
            self.db,"pay","PAYMENT","mockpay","WRITE_SANDBOX_VERIFIED",
            scopes=["synthetic"],expires_at="2999-01-01T00:00:00+00:00"
        )
        resume(self.db)

    def tearDown(self):
        self.db.close(); self.t.cleanup()

    def test_gateway_rejects_negative_grant_limits(self):
        with self.assertRaises(GatewayError):
            self.gw.create_grant("bad","V",["PAYMENT"],total_cap=-1)

    def test_gateway_rejects_negative_action_amount(self):
        self.gw.create_grant("g","V",["PAYMENT"],currency="USD",total_cap=1000,max_uses=1)
        with self.assertRaises(GatewayError):
            self.gw.execute(
                action_id="a",idempotency_key="i",venture_id="V",
                command_type="PAYMENT",operation="PAYMENT",account="mockpay",
                adapter=MockAdapter(),grant_id="g",amount_minor=-1,
                currency="USD",data_scope="synthetic",payload={}
            )

    def test_nonfinancial_unknown_reserves_use_until_reconciled(self):
        self.gw.create_grant(
            "g","V",["SEND_MESSAGE"],destination="buyer@example.test",
            data_scopes=["synthetic"],currency="USD",max_uses=1
        )
        row=self.gw.execute(
            action_id="a",idempotency_key="i",venture_id="V",
            command_type="SEND_MESSAGE",operation="SEND_MESSAGE",account="mock",
            adapter=MockAdapter("unknown_after_accept"),grant_id="g",
            destination="buyer@example.test",currency="USD",
            data_scope="synthetic",payload={}
        )
        self.assertEqual(row["state"],ActionState.UNKNOWN_OUTCOME.value)
        grant=self.db.execute("SELECT * FROM grants WHERE id='g'").fetchone()
        self.assertEqual((grant["uses"],grant["reserved_uses"]),(0,1))
        with self.assertRaises(PermissionError):
            self.gw.execute(
                action_id="b",idempotency_key="j",venture_id="V",
                command_type="SEND_MESSAGE",operation="SEND_MESSAGE",account="mock",
                adapter=MockAdapter(),grant_id="g",
                destination="buyer@example.test",currency="USD",
                data_scope="synthetic",payload={}
            )
        done=self.gw.reconcile("a",ActionState.SUCCEEDED.value,evidence_ref="provider-check")
        self.assertEqual(done["state"],ActionState.SUCCEEDED.value)
        grant=self.db.execute("SELECT * FROM grants WHERE id='g'").fetchone()
        self.assertEqual((grant["uses"],grant["reserved_uses"]),(1,0))

    def test_financial_unknown_reconcile_failure_releases_exposure(self):
        self.gw.create_grant(
            "g","V",["PAYMENT"],data_scopes=["synthetic"],
            currency="USD",total_cap=5000,max_uses=1
        )
        row=self.gw.execute(
            action_id="a",idempotency_key="i",venture_id="V",
            command_type="PAYMENT",operation="PAYMENT",account="mockpay",
            adapter=MockAdapter("unknown_after_accept"),grant_id="g",
            amount_minor=5000,currency="USD",data_scope="synthetic",payload={}
        )
        self.assertEqual(row["state"],ActionState.UNKNOWN_OUTCOME.value)
        self.gw.reconcile("a",ActionState.FAILED.value,evidence_ref="provider-no-effect")
        budget=self.db.execute("SELECT * FROM budgets WHERE venture_id='V' AND currency='USD'").fetchone()
        grant=self.db.execute("SELECT * FROM grants WHERE id='g'").fetchone()
        self.assertEqual((budget["reserved_minor"],budget["spent_minor"]),(0,0))
        self.assertEqual((grant["reserved_amount"],grant["used_amount"]),(0,0))

    def test_precision_aware_iqd_to_usd(self):
        # 100,000 IQD = 100,000,000 IQD minor units (3 digits).
        # At 0.00076 USD/IQD => 76 USD = 7,600 USD minor units.
        self.assertEqual(
            convert_currency(100_000_000,"IQD","USD","0.00076"),
            7600,
        )

    def test_verified_fx_requires_fresh_evidence_and_precision(self):
        add_evidence(
            self.db,"fxev","IQD/USD rate","AUTHORITATIVE_EXTERNAL","source",
            expires_at="2999-01-01T00:00:00+00:00"
        )
        register_fx_rate(
            self.db,"r1","IQD","USD","0.00076","fxev",
            expires_at="2999-01-01T00:00:00+00:00"
        )
        self.assertEqual(
            verified_convert(self.db,100_000_000,"IQD","USD","r1"),
            7600,
        )

    def test_unknown_currency_precision_fails_closed(self):
        with self.assertRaises(CurrencyError):
            convert_currency(100,"ZZZ","USD","1")

if __name__=="__main__": unittest.main()
