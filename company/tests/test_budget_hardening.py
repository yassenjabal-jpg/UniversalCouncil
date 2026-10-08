import tempfile, unittest
from pathlib import Path
from company.runtime.db import connect
from company.runtime.kernel import Kernel

class BudgetHardening(unittest.TestCase):
    def test_cap_preserves_and_respects_existing_exposure(self):
        with tempfile.TemporaryDirectory() as td:
            db=connect(Path(td)/'db.sqlite')
            k=Kernel(db)
            k.set_budget('V','USD',10000)
            with db:
                db.execute("UPDATE budgets SET reserved_minor=4000, spent_minor=3000 WHERE venture_id='V' AND currency='USD'")
            with self.assertRaises(ValueError):
                k.set_budget('V','USD',6000)
            k.set_budget('V','USD',12000)
            row=db.execute("SELECT cap_minor,reserved_minor,spent_minor FROM budgets WHERE venture_id='V' AND currency='USD'").fetchone()
            self.assertEqual((row['cap_minor'],row['reserved_minor'],row['spent_minor']),(12000,4000,3000))
            db.close()

if __name__=='__main__': unittest.main()
