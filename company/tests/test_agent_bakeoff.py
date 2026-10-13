import copy
import json
import tempfile
import unittest
from pathlib import Path

from company.runtime.agent_bakeoff import (
    BakeoffError,
    aggregate_runtime,
    duplicate_content_ratio,
    evaluate,
    load_cases,
    load_json,
    score_case,
    score_mechanics,
    select_winner,
    unique_contribution_score,
    validate_case,
    validate_config,
    validate_provenance,
    validate_result,
)

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "company/config/agent_bakeoff.json").read_text(encoding="utf-8"))
CASES = load_cases(ROOT / "benchmarks/agent_runtime/cases.json")
PROVENANCE = {
    "experiment_id": "test-experiment",
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
        "usage": {"input_tokens": 100, "output_tokens": 50, "cost_usd": 0.0},
        "latency_ms": 100,
        "provenance": copy.deepcopy(PROVENANCE),
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
        report = evaluate(CASES, results, mechanics, CFG, expected_provenance=PROVENANCE)
        self.assertEqual(report["decision"]["state"], "NO_WINNER")

    def test_routing_penalizes_forbidden_participant(self):
        case = copy.deepcopy(CASES[0])
        case["forbidden_roles"] = ["Unneeded Observer"]
        result = result_for(case)
        result["participants"].append("Unneeded Observer")
        score = score_case(case, result)
        self.assertLess(score["routing_accuracy"], 1.0)

    def test_validate_config_rejects_invalid_shapes(self):
        mutations = []

        bad = copy.deepcopy(CFG)
        bad["version"] = "2.0"
        mutations.append(bad)

        bad = copy.deepcopy(CFG)
        bad["minimum_live_decision_cases"] = 0
        mutations.append(bad)

        bad = copy.deepcopy(CFG)
        bad["minimum_mechanics_score"] = -1
        mutations.append(bad)

        for desktop_min in (-0.1, 1.1):
            bad = copy.deepcopy(CFG)
            bad["minimum_desktop_execution_score"] = desktop_min
            mutations.append(bad)

        bad = copy.deepcopy(CFG)
        bad["required_desktop_case_count"] = 0
        mutations.append(bad)

        bad = copy.deepcopy(CFG)
        bad["require_provenance"] = False
        mutations.append(bad)

        bad = copy.deepcopy(CFG)
        bad["required_provenance_keys"] = []
        mutations.append(bad)

        bad = copy.deepcopy(CFG)
        bad["required_mechanics_for_winner"] = []
        mutations.append(bad)

        bad = copy.deepcopy(CFG)
        bad["weights"] = {}
        mutations.append(bad)

        bad = copy.deepcopy(CFG)
        bad["weights"] = {"completion": 0.5}
        mutations.append(bad)

        bad = copy.deepcopy(CFG)
        bad["runtimes"] = {}
        mutations.append(bad)

        for bad in mutations:
            with self.subTest(bad=bad):
                with self.assertRaises(BakeoffError):
                    validate_config(bad)

    def test_validate_case_rejects_missing_bad_id_and_non_list_fields(self):
        case = copy.deepcopy(CASES[0])
        del case["prompt"]
        with self.assertRaises(BakeoffError):
            validate_case(case)

        case = copy.deepcopy(CASES[0])
        case["case_id"] = "Bad ID!"
        with self.assertRaises(BakeoffError):
            validate_case(case)

        for field in ("required_roles", "forbidden_roles", "expected_blockers", "required_dissent_tags"):
            case = copy.deepcopy(CASES[0])
            case[field] = "not-a-list"
            with self.subTest(field=field):
                with self.assertRaises(BakeoffError):
                    validate_case(case)

    def test_validate_result_rejects_schema_and_type_errors(self):
        base = result_for(CASES[0])

        bad = copy.deepcopy(base)
        del bad["latency_ms"]
        with self.assertRaises(BakeoffError):
            validate_result(bad)

        field_values = {
            "mode": "INVALID",
            "status": "INVALID",
            "participants": {},
            "role_outputs": [],
            "blockers": "bad",
            "policy_violations": "bad",
            "desktop": [],
            "usage": [],
            "provenance": [],
        }
        for field, value in field_values.items():
            bad = copy.deepcopy(base)
            bad[field] = value
            with self.subTest(field=field):
                with self.assertRaises(BakeoffError):
                    validate_result(bad)

        bad = copy.deepcopy(base)
        bad["dissent_tags"] = "bad"
        with self.assertRaises(BakeoffError):
            validate_result(bad)

    def test_json_and_case_loading_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            missing = root / "missing.json"
            with self.assertRaises(BakeoffError):
                load_json(missing)

            invalid = root / "invalid.json"
            invalid.write_text("{", encoding="utf-8")
            with self.assertRaises(BakeoffError):
                load_json(invalid)

            empty = root / "empty.json"
            empty.write_text("[]", encoding="utf-8")
            with self.assertRaises(BakeoffError):
                load_cases(empty)

            wrong_root = root / "wrong-root.json"
            wrong_root.write_text("{}", encoding="utf-8")
            with self.assertRaises(BakeoffError):
                load_cases(wrong_root)

            non_object = root / "non-object.json"
            non_object.write_text('["bad"]', encoding="utf-8")
            with self.assertRaises(BakeoffError):
                load_cases(non_object)

            duplicate = root / "duplicate.json"
            duplicate.write_text(json.dumps([CASES[0], CASES[0]]), encoding="utf-8")
            with self.assertRaises(BakeoffError):
                load_cases(duplicate)

    def test_score_case_covers_empty_sets_failure_and_non_desktop_paths(self):
        case = copy.deepcopy(CASES[0])
        case["expected_blockers"] = []
        case["required_dissent_tags"] = []
        case["desktop_required"] = False
        case["injected_failure"] = False

        result = result_for(case)
        result["blockers"] = []
        result["dissent_tags"] = []
        result["status"] = "FAILED"
        result["role_outputs"] = {}
        result["policy_violations"] = ["probe"]
        result["human_override"] = True
        score = score_case(case, result)

        self.assertEqual(score["blocker_f1"], 1.0)
        self.assertEqual(score["dissent_preservation"], 1.0)
        self.assertIsNone(score["desktop_execution"])
        self.assertEqual(score["completion"], 0.0)
        self.assertEqual(score["policy_compliance"], 0.0)
        self.assertEqual(score["unique_contribution"], 0.0)
        self.assertTrue(score["human_override"])

    def test_score_case_detects_id_mismatch_and_failed_recovery(self):
        case = copy.deepcopy(CASES[1])
        result = result_for(case)
        result["failure_recovered"] = False
        score = score_case(case, result)
        self.assertEqual(score["failure_recovery"], 0.0)

        result["case_id"] = "different_case"
        with self.assertRaises(BakeoffError):
            score_case(case, result)

    def test_duplicate_content_ratio_handles_empty_and_single_outputs(self):
        self.assertEqual(duplicate_content_ratio({}), 0.0)
        self.assertEqual(duplicate_content_ratio({"A": "one contribution"}), 0.0)

    def test_aggregate_rejects_empty_scores(self):
        with self.assertRaises(BakeoffError):
            aggregate_runtime("baseline", [], {}, CFG)

    def test_perfect_live_runtime_can_be_selected_when_all_hard_gates_pass(self):
        scores = [score_case(case, result_for(case, "openai_agents")) for case in CASES]
        mechanics = {name: True for name in CFG["required_mechanics_for_winner"]}
        summary = aggregate_runtime("openai_agents", scores, mechanics, CFG)
        self.assertTrue(summary["hard_mechanics_pass"])
        self.assertTrue(summary["eligible_for_winner"])

        decision = select_winner([summary])
        self.assertEqual(decision["state"], "WINNER_SELECTED")
        self.assertEqual(decision["winner"], "openai_agents")

    def test_winner_tie_break_path_and_evaluate_unknown_case_fail_closed(self):
        first = {
            "runtime_id": "first",
            "eligible_for_winner": True,
            "score": 0.9,
            "cost_usd_total": 0.0,
            "latency_ms_total": 20.0,
        }
        second = {
            "runtime_id": "second",
            "eligible_for_winner": True,
            "score": 0.9,
            "cost_usd_total": 0.0,
            "latency_ms_total": 10.0,
        }
        self.assertEqual(select_winner([first, second])["winner"], "second")

        result = result_for(CASES[0])
        result["case_id"] = "unknown_case"
        with self.assertRaises(BakeoffError):
            evaluate(CASES, [result], {}, CFG, expected_provenance=PROVENANCE)

    def test_evaluate_requires_provenance_manifest(self):
        result = result_for(CASES[0], "openai_agents")
        with self.assertRaises(BakeoffError):
            evaluate(CASES, [result], {}, CFG)

    def test_provenance_mismatch_cost_and_host_fail_closed(self):
        result = result_for(CASES[0], "openai_agents")
        self.assertTrue(validate_provenance(result, PROVENANCE, CFG))

        stale = copy.deepcopy(result)
        stale["provenance"]["source_sha"] = "stale"
        with self.assertRaises(BakeoffError):
            validate_provenance(stale, PROVENANCE, CFG)

        paid = copy.deepcopy(result)
        paid["usage"]["cost_usd"] = 0.01
        with self.assertRaises(BakeoffError):
            validate_provenance(paid, PROVENANCE, CFG)

        wrong_host = copy.deepcopy(result)
        wrong_host["provenance"]["execution_host"] = "NOT_YASSIN"
        wrong_expected = copy.deepcopy(PROVENANCE)
        wrong_expected["execution_host"] = "NOT_YASSIN"
        with self.assertRaises(BakeoffError):
            validate_provenance(wrong_host, wrong_expected, CFG)


if __name__ == "__main__":
    unittest.main()
