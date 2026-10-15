from __future__ import annotations

import json
import unittest
from pathlib import Path

from company.runtime.agent_bakeoff_baseline import route_v03
from company.runtime.agent_bakeoff_provenance import result_provenance
from tools.build_agent_bakeoff_packets import redact_known_labels, strip_sensitive_sections

ROOT = Path(__file__).resolve().parents[2]


class BakeoffRemediationTests(unittest.TestCase):
    def test_sensitive_markdown_sections_are_removed(self):
        source = """# Context
Keep this evidence.
## Final verdict
ADOPT
This must not be shown.
## Evidence
Keep this too.
"""
        masked = strip_sensitive_sections(source)
        self.assertIn("Keep this evidence.", masked)
        self.assertIn("Keep this too.", masked)
        self.assertNotIn("ADOPT", masked)
        self.assertNotIn("This must not be shown.", masked)

    def test_expected_labels_are_redacted(self):
        case = {
            "expected_decision": "GO_WITH_CONDITIONS",
            "expected_blockers": ["OWNER_GATE"],
            "required_dissent_tags": ["KILL_CRITERIA_REQUIRED"],
        }
        masked = redact_known_labels(
            "GO WITH CONDITIONS only after OWNER GATE and KILL CRITERIA REQUIRED.",
            case,
        )
        self.assertNotIn("GO WITH CONDITIONS", masked)
        self.assertNotIn("OWNER GATE", masked)
        self.assertNotIn("KILL CRITERIA REQUIRED", masked)

    def test_v03_baseline_uses_existing_routing_contract(self):
        roles = route_v03(
            ROOT,
            "Review software architecture and security risk for a media application.",
            "The system has code, architecture, UI and content workflow concerns.",
        )
        self.assertIn("Evidence & Verification", roles)
        self.assertIn("Red Team / Falsification", roles)
        self.assertIn("Execution & Feasibility", roles)
        self.assertIn("Software & Systems", roles)
        self.assertLessEqual(len(roles), 7)
        self.assertTrue(
            {"Software & Systems", "Media & Content"} & set(roles),
            "v0.3 routing should include at least one relevant domain specialist within its 7-role cap",
        )

    def test_config_requires_yassin_only_live_execution(self):
        cfg = json.loads((ROOT / "company/config/agent_bakeoff.json").read_text(encoding="utf-8"))
        self.assertEqual(cfg["required_runner_id"], "YASSIN")
        self.assertEqual(cfg["maximum_cost_usd"], 0)
        self.assertEqual(cfg["live_execution_policy"]["execution_host"], "YASSIN_ONLY")
        self.assertFalse(cfg["live_execution_policy"]["external_compute"])
        self.assertTrue(cfg["live_execution_policy"]["staged_run_required"])
        self.assertTrue(cfg["live_execution_policy"]["resume_required"])

    def test_result_provenance_uses_canonical_keys(self):
        manifest = {
            "manifest_id": "manifest-x",
            "experiment_id": "x",
            "runner_id": "YASSIN",
            "source_sha": "s",
            "config_sha256": "c",
            "cases_sha256": "cases",
            "packets_sha256": "packets",
            "runner_sha256": "runner",
            "evaluator_sha256": "eval",
            "requirements_sha256": "req",
            "model": "m",
            "model_digest": "d",
            "execution_host": "YASSIN",
            "financial_cost_usd": 0.0,
        }
        self.assertEqual(result_provenance(manifest), manifest)


if __name__ == "__main__":
    unittest.main()
