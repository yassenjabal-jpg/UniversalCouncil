from __future__ import annotations

import json
import unittest
from pathlib import Path

from company.runtime.agent_bakeoff import aggregate_runtime, load_cases, score_case

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "company/config/agent_bakeoff.json").read_text(encoding="utf-8"))
CASES = load_cases(ROOT / "benchmarks/agent_runtime/cases.json")


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
    }


class DesktopWinnerGateTests(unittest.TestCase):
    def test_desktop_evidence_is_required_for_winner(self):
        scores = [score_case(case, result_for(case)) for case in CASES]
        mechanics = {name: True for name in CFG["required_mechanics_for_winner"]}
        summary = aggregate_runtime("openai_agents", scores, mechanics, CFG)
        self.assertFalse(summary["eligible_for_winner"])
        self.assertLess(summary["metrics"]["desktop_execution"], CFG["minimum_desktop_execution_score"])


if __name__ == "__main__":
    unittest.main()
