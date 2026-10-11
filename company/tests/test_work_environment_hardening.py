import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "company-stage0.yml"
PYPROJECT = ROOT / "pyproject.toml"


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

    def test_pyproject_pins_supported_python_and_dev_tools(self):
        with PYPROJECT.open("rb") as handle:
            cfg = tomllib.load(handle)
        self.assertEqual(cfg["project"]["requires-python"], ">=3.12,<3.14")
        self.assertEqual(
            cfg["project"]["optional-dependencies"]["dev"],
            ["ruff==0.17.0", "coverage==7.16.2"],
        )
        self.assertEqual(cfg["tool"]["ruff"]["target-version"], "py312")
        self.assertEqual(cfg["tool"]["ruff"]["lint"]["select"], ["E4", "E7", "E9", "F"])
        self.assertTrue(cfg["tool"]["coverage"]["run"]["branch"])

    def test_company_workflow_enforces_branch_coverage_ratchet(self):
        text = self._workflow_text()
        self.assertIn("coverage run --branch", text)
        self.assertIn("coverage json -o build/coverage.json", text)
        self.assertIn("tools/coverage_gate.py", text)
        self.assertIn("company/config/coverage_baseline.json", text)

    def test_codeql_workflow_is_python_scoped_and_immutably_pinned(self):
        path = ROOT / ".github" / "workflows" / "codeql.yml"
        text = path.read_text(encoding="utf-8")
        self.assertIn("pull_request:", text)
        self.assertIn("push:", text)
        self.assertIn('- "main"', text)
        self.assertIn("name: CodeQL Python", text)
        self.assertIn("languages: python", text)
        self.assertIn(
            "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
            text,
        )
        pin = "24c54180a607b1449ed407dd24f251e4e9147c8d"
        self.assertIn(f"github/codeql-action/init@{pin}", text)
        self.assertIn(f"github/codeql-action/analyze@{pin}", text)
        self.assertNotIn("github/codeql-action/init@v4", text)
        self.assertNotIn("github/codeql-action/analyze@v4", text)


if __name__ == "__main__":
    unittest.main()
