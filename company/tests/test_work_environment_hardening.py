import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "company-stage0.yml"


class WorkEnvironmentHardeningContracts(unittest.TestCase):
    def _workflow_text(self):
        return WORKFLOW.read_text(encoding="utf-8")

    def test_company_workflow_targets_pull_requests_and_main_pushes(self):
        text = self._workflow_text()
        self.assertIn("pull_request:", text)
        self.assertIn("push:", text)
        self.assertIn('- "main"', text)
        self.assertNotIn("codex/venture-operating-system-v1", text)
        self.assertNotIn("paths:", text)

    def test_company_workflow_uses_immutable_action_pins(self):
        text = self._workflow_text()
        self.assertIn(
            "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
            text,
        )
        self.assertIn(
            "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97",
            text,
        )
        self.assertNotIn("actions/checkout@v", text)
        self.assertNotIn("actions/setup-python@v", text)

    def test_company_workflow_has_stable_python_jobs(self):
        text = self._workflow_text()
        self.assertIn("name: Quality Gate", text)
        self.assertIn("name: Python 3.12 Compatibility", text)
        self.assertIn('python-version: "3.13"', text)
        self.assertIn('python-version: "3.12"', text)


if __name__ == "__main__":
    unittest.main()
