from __future__ import annotations

import json
import unittest
from pathlib import Path

from company.runtime.agent_bakeoff import aggregate_runtime, load_cases, score_case

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "company/config/agent_bakeoff.json").read_text(encoding="utf-8"))
CASES = load_cases(ROOT / "benchmarks/agent_runtime/cases.json")
PROVENANCE = {
    "experiment_id": "desktop-gate-test",
    "source_sha": "abc123",
    "config_sha256": "config-hash",
    "cases_sha256": "cases-hash",
    "runner_sha256": "runner-hash",
    "requirements_sha256": "requirements-hash",
    "model": "qwen3:4b-instruct",
    "model_digest": "model-digest",
    "execution_host": "YASSIN",
    "financial_cost_usd": 0.0,
}


def result_for(case):
    return {
        "runtime_id": "openai_agents",
        "case_id": case["case_id"],
        "mode": "LIVE_DECISION",
        "status": "COMPLETED",
        "final_decision": case["expected_decision"],
        "participants": list(case["required_roles"]),
        "role_outputs": {"Evidence & Verification": "unique evidence"},
        "blockers": list(case["expected_blockers"]),
        "dissent_tags": list(case["required_dissent_tags"]),
        "policy_violations": [],
        "human_override": False,
        "failure_recovered": True,
        "desktop": {
            "task_completed": not case["desktop_required"],
            "verification_passed": not case["desktop_required"],
            "selector_recovered": not case["desktop_required"],
            "correct_execution_path": not case["desktop_required"],
            "no_unintended_action": True,
        },
        "usage": {"input_tokens": 1, "output_tokens": 1, "cost_usd": 0.0},
        "latency_ms": 1,
        "provenance": dict(PROVENANCE),
    }


class DesktopWinnerGateTests(unittest.TestCase):
    def test_desktop_evidence_is_required_for_winner(self):
        scores = [score_case(case, result_for(case)) for case in CASES]
        mechanics = {name: True for name in CFG["required_mechanics_for_winner"]}
        summary = aggregate_runtime("openai_agents", scores, mechanics, CFG)
        self.assertFalse(summary["eligible_for_winner"])
        self.assertEqual(summary["desktop_gate"]["required"], 2)
        self.assertEqual(summary["desktop_gate"]["passed"], 0)
        self.assertFalse(summary["desktop_gate"]["pass"])
        self.assertEqual(summary["metrics"]["desktop_execution"], 0.0)


if __name__ == "__main__":
    unittest.main()
