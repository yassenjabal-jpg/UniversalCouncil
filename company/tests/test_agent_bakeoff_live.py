from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools" / "run_agent_bakeoff_live.py"

spec = importlib.util.spec_from_file_location("run_agent_bakeoff_live", SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load live bakeoff runner")
live = importlib.util.module_from_spec(spec)
spec.loader.exec_module(live)


class LiveBakeoffRunnerTests(unittest.TestCase):
    def test_root_points_to_repository(self):
        self.assertEqual(live.ROOT, ROOT)
        self.assertTrue((live.ROOT / "benchmarks" / "agent_runtime" / "cases.json").is_file())

    def test_only_local_http_endpoints_are_allowed(self):
        self.assertEqual(live.ensure_local_endpoint("http://127.0.0.1:11434"), "http://127.0.0.1:11434")
        self.assertEqual(live.ensure_local_endpoint("http://localhost:11434/"), "http://localhost:11434")
        for endpoint in ("https://api.openai.com", "https://ollama.com", "http://192.168.1.10:11434"):
            with self.subTest(endpoint=endpoint):
                with self.assertRaises(ValueError):
                    live.ensure_local_endpoint(endpoint)

    def test_all_historical_cases_have_decision_options(self):
        cases = json.loads((ROOT / "benchmarks" / "agent_runtime" / "cases.json").read_text(encoding="utf-8"))
        case_ids = {case["case_id"] for case in cases}
        self.assertEqual(case_ids, set(live.DECISION_OPTIONS))
        for case in cases:
            options = live.DECISION_OPTIONS[case["case_id"]]
            self.assertGreaterEqual(len(options), 2)
            self.assertIn(case["expected_decision"], options)

    def test_stage_contract_is_canary_then_representative_then_full(self):
        self.assertEqual(live.STAGES["canary"], ["c14_specialized_tool_policy"])
        self.assertEqual(len(live.STAGES["representative"]), 4)
        self.assertIsNone(live.STAGES["full"])

    def test_historical_answer_is_masked(self):
        sample = """# Context
Useful evidence.
## Final verdict
ADOPT_V0_4_NOW
## Evidence
Status: ACCEPTED
The explicit token is PROVISIONAL_RESTRUCTURE_CANDIDATE.
"""
        masked = live.mask_historical_answer(sample, "PROVISIONAL_RESTRUCTURE_CANDIDATE")
        self.assertNotIn("ADOPT_V0_4_NOW", masked)
        self.assertNotIn("PROVISIONAL_RESTRUCTURE_CANDIDATE", masked)
        self.assertNotIn("Status: ACCEPTED", masked)
        self.assertIn("Useful evidence.", masked)
        self.assertIn("## Evidence", masked)

    def test_case_packets_do_not_contain_expected_decision_token(self):
        cases = json.loads((ROOT / "benchmarks" / "agent_runtime" / "cases.json").read_text(encoding="utf-8"))
        for case in cases:
            packet, packet_sha, source_sha = live.case_source(case)
            self.assertNotIn(case["expected_decision"], packet)
            self.assertEqual(len(packet_sha), 64)
            self.assertEqual(len(source_sha), 64)

    def test_role_registry_covers_all_expected_roles(self):
        cases = json.loads((ROOT / "benchmarks" / "agent_runtime" / "cases.json").read_text(encoding="utf-8"))
        expected_roles = {role for case in cases for role in case["required_roles"]}
        self.assertTrue(expected_roles.issubset(set(live.ROLE_DESCRIPTIONS)))

    def test_baseline_is_single_structured_v03_prompt(self):
        case = json.loads((ROOT / "benchmarks" / "agent_runtime" / "cases.json").read_text(encoding="utf-8"))[0]
        packet, _, _ = live.case_source(case)
        prompt = live.baseline_v03_prompt(
            case,
            packet,
            live.DECISION_OPTIONS[case["case_id"]],
            [],
            [],
        )
        self.assertIn("CURRENT Universal Council v0.3 baseline", prompt)
        self.assertIn("one structured model run", prompt)
        self.assertIn("not independent agents", prompt)

    def test_local_runner_hardcodes_zero_cost_and_yassin_only(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('"cost_usd": 0.0', source)
        self.assertIn("require_yassin_runner()", source)
        self.assertNotIn("api.openai.com", source)
        self.assertNotIn("ollama.com/v1", source)


if __name__ == "__main__":
    unittest.main()
