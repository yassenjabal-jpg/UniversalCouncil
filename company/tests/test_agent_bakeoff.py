import copy
import json
import unittest
from pathlib import Path

from company.runtime.agent_bakeoff import (
    BakeoffError,
    aggregate_runtime,
    duplicate_content_ratio,
    evaluate,
    load_cases,
    score_case,
    score_mechanics,
    select_winner,
    unique_contribution_score,
    validate_config,
    validate_result,
)

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "company/config/agent_bakeoff.json").read_text(encoding="utf-8"))
CASES = load_cases(ROOT / "benchmarks/agent_runtime/cases.json")


def result_for(case, runtime_id="baseline", mode="LIVE_DECISION"):
    return {
        "runtime_id": runtime_id,
        "case_id": case["case_id"],
        "mode": mode,
        "status": "COMPLETED",
        "final_decision": case["expected_decision"],
        "participants": list(case["required_roles"]),
        "role_outputs": {
            "Evidence & Verification": "Verified evidence and source freshness are decisive.",
            "Red Team / Falsification": "Challenge irreversible assumptions and preserve dissent.",
        },
        "blockers": list(case["expected_blockers"]),
        "dissent_tags": list(case["required_dissent_tags"]),
        "policy_violations": [],
        "human_override": False,
        "failure_recovered": True,
        "desktop": {
            "task_completed": True,
            "verification_passed": True,
            "selector_recovered": True,
            "correct_execution_path": True,
            "no_unintended_action": True,
        },
        "usage": {"input_tokens": 100, "output_tokens": 50, "cost_usd": 0.01},
        "latency_ms": 100,
    }


class AgentBakeoffTests(unittest.TestCase):
    def test_config_and_cases_are_valid(self):
        self.assertTrue(validate_config(CFG))
        self.assertGreaterEqual(len(CASES), 12)

    def test_score_perfect_live_case(self):
        case = CASES[0]
        score = score_case(case, result_for(case))
        self.assertTrue(score["decision_correct"])
        self.assertEqual(score["routing_accuracy"], 1.0)
        self.assertEqual(score["blocker_f1"], 1.0)
        self.assertEqual(score["dissent_preservation"], 1.0)
        self.assertEqual(score["policy_compliance"], 1.0)

    def test_mechanics_only_does_not_fake_decision_correctness(self):
        case = CASES[0]
        result = result_for(case, mode="MECHANICS_ONLY")
        result["final_decision"] = case["expected_decision"]
        score = score_case(case, result)
        self.assertIsNone(score["decision_correct"])

    def test_policy_violation_blocks_runtime_eligibility(self):
        scores = []
        for case in CASES:
            result = result_for(case)
            result["policy_violations"] = ["silent_external_write"]
            scores.append(score_case(case, result))
        mechanics = {
            key: True
            for key in (
                "framework_import",
                "isolated_roles",
                "parallel_first_positions",
                "fan_in",
                "failure_injection",
                "failure_recovery",
                "checkpoint_resume",
                "hitl_pause",
                "usage_capture",
                "trace_capture",
            )
        }
        summary = aggregate_runtime("baseline", scores, mechanics, CFG)
        self.assertFalse(summary["eligible_for_winner"])
        self.assertEqual(summary["metrics"]["policy_compliance"], 0.0)

    def test_no_live_cases_means_no_winner(self):
        scores = [score_case(case, result_for(case, mode="MECHANICS_ONLY")) for case in CASES]
        summary = aggregate_runtime("openai_agents", scores, {}, CFG)
        decision = select_winner([summary])
        self.assertEqual(decision["state"], "NO_WINNER")

    def test_mechanics_score_is_measured_not_advertised(self):
        receipt = {
            "framework_import": True,
            "isolated_roles": True,
            "parallel_first_positions": True,
            "fan_in": True,
            "failure_injection": False,
            "failure_recovery": False,
            "checkpoint_resume": False,
            "hitl_pause": False,
            "usage_capture": True,
            "trace_capture": False,
        }
        self.assertEqual(score_mechanics(receipt), 0.5)

    def test_duplicate_and_unique_contribution_metrics(self):
        duplicate = {"A": "same useful evidence", "B": "same useful evidence"}
        distinct = {"A": "source provenance timestamp", "B": "human burden accessibility"}
        self.assertGreater(duplicate_content_ratio(duplicate), duplicate_content_ratio(distinct))
        self.assertGreater(unique_contribution_score(distinct), unique_contribution_score(duplicate))

    def test_unknown_result_fields_fail_closed(self):
        bad = result_for(CASES[0])
        bad["mode"] = "PRETEND_LIVE"
        with self.assertRaises(BakeoffError):
            validate_result(bad)

    def test_evaluate_requires_live_gate_before_winner(self):
        results = [result_for(case, "openai_agents", "MECHANICS_ONLY") for case in CASES]
        mechanics = {
            "openai_agents": {
                "framework_import": True,
                "isolated_roles": True,
                "parallel_first_positions": True,
                "fan_in": True,
                "failure_injection": True,
                "failure_recovery": True,
                "checkpoint_resume": True,
                "hitl_pause": True,
                "usage_capture": True,
                "trace_capture": True,
            }
        }
        report = evaluate(CASES, results, mechanics, CFG)
        self.assertEqual(report["decision"]["state"], "NO_WINNER")

    def test_routing_penalizes_forbidden_participant(self):
        case = copy.deepcopy(CASES[0])
        case["forbidden_roles"] = ["Unneeded Observer"]
        result = result_for(case)
        result["participants"].append("Unneeded Observer")
        score = score_case(case, result)
        self.assertLess(score["routing_accuracy"], 1.0)


if __name__ == "__main__":
    unittest.main()
