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

    def test_only_local_endpoints_are_allowed(self):
        self.assertEqual(live.ensure_local_endpoint("http://127.0.0.1:11434"), "http://127.0.0.1:11434")
        self.assertEqual(live.ensure_local_endpoint("http://localhost:11434/"), "http://localhost:11434")
        with self.assertRaises(ValueError):
            live.ensure_local_endpoint("https://api.openai.com")
        with self.assertRaises(ValueError):
            live.ensure_local_endpoint("https://ollama.com")

    def test_all_historical_cases_have_decision_options(self):
        cases = json.loads((ROOT / "benchmarks" / "agent_runtime" / "cases.json").read_text(encoding="utf-8"))
        case_ids = {case["case_id"] for case in cases}
        self.assertEqual(case_ids, set(live.DECISION_OPTIONS))
        for case in cases:
            options = live.DECISION_OPTIONS[case["case_id"]]
            self.assertGreaterEqual(len(options), 2)
            self.assertIn(case["expected_decision"], options)

    def test_role_registry_covers_all_expected_roles(self):
        cases = json.loads((ROOT / "benchmarks" / "agent_runtime" / "cases.json").read_text(encoding="utf-8"))
        expected_roles = {role for case in cases for role in case["required_roles"]}
        self.assertTrue(expected_roles.issubset(set(live.ROLE_DESCRIPTIONS)))

    def test_global_vocabulary_contains_expected_labels(self):
        cases = json.loads((ROOT / "benchmarks" / "agent_runtime" / "cases.json").read_text(encoding="utf-8"))
        blockers = set(live.global_vocab(cases, "expected_blockers"))
        dissent = set(live.global_vocab(cases, "required_dissent_tags"))
        for case in cases:
            self.assertTrue(set(case["expected_blockers"]).issubset(blockers))
            self.assertTrue(set(case["required_dissent_tags"]).issubset(dissent))

    def test_local_runner_hardcodes_zero_cost(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('"cost_usd": 0.0', source)
        self.assertNotIn("api.openai.com", source)
        self.assertNotIn("ollama.com/v1", source)


if __name__ == "__main__":
    unittest.main()
