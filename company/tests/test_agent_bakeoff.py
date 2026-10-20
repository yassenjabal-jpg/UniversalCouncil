from __future__ import annotations

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
    validate_result,
)

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "company/config/agent_bakeoff.json").read_text(encoding="utf-8"))
CASES = load_cases(ROOT / "benchmarks/agent_runtime/cases.json")
ALL_CASE_IDS = [case["case_id"] for case in CASES]


def manifest(stage: str = "full", case_ids: list[str] | None = None) -> dict:
    return {
        "schema_version": "1.1",
        "runner_id": "YASSIN",
        "execution_host": "YASSIN",
        "financial_cost_usd": 0.0,
        "manifest_id": "test-manifest",
        "experiment_id": "test-manifest",
        "source_sha": "source-sha",
        "config_sha256": "config-sha",
        "cases_sha256": "cases-sha",
        "packets_sha256": "packets-sha",
        "runner_sha256": "runner-sha",
        "evaluator_sha256": "evaluator-sha",
        "requirements_sha256": "requirements-sha",
        "model": "qwen3:4b-instruct",
        "model_digest": "model-digest",
        "selected_case_ids": list(case_ids or ALL_CASE_IDS),
        "stage": stage,
    }


def result_for(case, runtime_id="openai_agents", mode="LIVE_DECISION", manifest_id="test-manifest"):
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
        "provenance": {
            **{
                key: (
                    manifest_id
                    if key == "experiment_id"
                    else manifest()[key]
                )
                for key in CFG["required_provenance_keys"]
            },
            "manifest_id": manifest_id,
            "runner_id": "YASSIN",
            "case_packet_sha256": "packet",
            "source_artifact_sha256": "source",
            "source_artifact": case["source_artifact"],
        },
    }


def mechanics_all_true() -> dict[str, bool]:
    return {name: True for name in CFG["required_mechanics_for_winner"]}


def all_runtime_results(case_subset=None):
    subset = list(case_subset or CASES)
    results = []
    for runtime_id in CFG["runtimes"]:
        for case in subset:
            results.append(result_for(case, runtime_id))
    return results


class AgentBakeoffTests(unittest.TestCase):
    def test_config_and_cases_are_valid(self):
        self.assertTrue(validate_config(CFG))
        self.assertEqual(len(CASES), 16)
        self.assertEqual(CFG["minimum_live_decision_cases"], 16)
        self.assertEqual(CFG["required_runner_id"], "YASSIN")
        self.assertEqual(CFG["desktop_required_passes"], 2)

    def test_perfect_live_case_scores_correctly(self):
        score = score_case(CASES[0], result_for(CASES[0]))
        self.assertTrue(score["decision_correct"])
        self.assertEqual(score["routing_accuracy"], 1.0)
        self.assertEqual(score["blocker_f1"], 1.0)
        self.assertEqual(score["dissent_preservation"], 1.0)
        self.assertEqual(score["policy_compliance"], 1.0)

    def test_non_desktop_case_does_not_inflate_desktop_metric(self):
        case = copy.deepcopy(CASES[0])
        case["desktop_required"] = False
        score = score_case(case, result_for(case))
        self.assertIsNone(score["desktop_execution"])
        self.assertIsNone(score["desktop_pass"])

    def test_desktop_required_case_requires_every_evidence_field(self):
        case = next(case for case in CASES if case["desktop_required"])
        result = result_for(case)
        result["desktop"]["selector_recovered"] = False
        score = score_case(case, result)
        self.assertFalse(score["desktop_pass"])
        self.assertLess(score["desktop_execution"], 1.0)

    def test_mechanics_only_does_not_fake_decision_correctness(self):
        result = result_for(CASES[0], mode="MECHANICS_ONLY")
        score = score_case(CASES[0], result)
        self.assertIsNone(score["decision_correct"])

    def test_policy_violation_blocks_runtime_eligibility(self):
        scores = []
        for case in CASES:
            result = result_for(case)
            result["policy_violations"] = ["silent_external_write"]
            scores.append(score_case(case, result))
        summary = aggregate_runtime("openai_agents", scores, mechanics_all_true(), CFG)
        self.assertFalse(summary["eligible_for_winner"])
        self.assertEqual(summary["metrics"]["policy_compliance"], 0.0)

    def test_full_perfect_runtime_can_be_selected(self):
        scores = [score_case(case, result_for(case)) for case in CASES]
        summary = aggregate_runtime("openai_agents", scores, mechanics_all_true(), CFG)
        self.assertTrue(summary["hard_mechanics_pass"])
        self.assertEqual(summary["desktop_cases_total"], 2)
        self.assertEqual(summary["desktop_cases_passed"], 2)
        self.assertTrue(summary["eligible_for_winner"])
        self.assertEqual(select_winner([summary])["winner"], "openai_agents")

    def test_only_one_of_two_desktop_cases_blocks_winner(self):
        scores = []
        seen = 0
        for case in CASES:
            result = result_for(case)
            if case["desktop_required"]:
                seen += 1
                if seen == 2:
                    result["desktop"]["verification_passed"] = False
            scores.append(score_case(case, result))
        summary = aggregate_runtime("openai_agents", scores, mechanics_all_true(), CFG)
        self.assertEqual(summary["desktop_cases_total"], 2)
        self.assertEqual(summary["desktop_cases_passed"], 1)
        self.assertFalse(summary["eligible_for_winner"])

    def test_live_evaluate_requires_manifest(self):
        with self.assertRaises(BakeoffError):
            evaluate(CASES, all_runtime_results(), {}, CFG)

    def test_wrong_runner_or_manifest_id_is_rejected(self):
        results = all_runtime_results()
        bad_manifest = manifest()
        bad_manifest["runner_id"] = "OTHER"
        with self.assertRaises(BakeoffError):
            evaluate(CASES, results, {}, CFG, bad_manifest)

        bad_manifest = manifest()
        results[0]["provenance"]["manifest_id"] = "stale"
        with self.assertRaises(BakeoffError):
            evaluate(CASES, results, {}, CFG, bad_manifest)

    def test_missing_runtime_or_duplicate_case_is_rejected(self):
        two_runtimes = [
            result
            for result in all_runtime_results()
            if result["runtime_id"] != "microsoft_agent_framework"
        ]
        with self.assertRaises(BakeoffError):
            evaluate(CASES, two_runtimes, {}, CFG, manifest())

        duplicated = all_runtime_results()
        duplicated.append(copy.deepcopy(duplicated[0]))
        with self.assertRaises(BakeoffError):
            evaluate(CASES, duplicated, {}, CFG, manifest())

    def test_nonzero_cost_is_rejected(self):
        results = all_runtime_results()
        results[0]["usage"]["cost_usd"] = 0.01
        with self.assertRaises(BakeoffError):
            evaluate(CASES, results, {}, CFG, manifest())

    def test_canary_stage_never_selects_winner(self):
        case = next(case for case in CASES if case["case_id"] == "c14_specialized_tool_policy")
        results = [result_for(case, runtime_id) for runtime_id in CFG["runtimes"]]
        mechanics = {runtime_id: mechanics_all_true() for runtime_id in CFG["runtimes"]}
        report = evaluate(
            CASES,
            results,
            mechanics,
            CFG,
            manifest("canary", [case["case_id"]]),
        )
        self.assertEqual(report["decision"]["state"], "NO_WINNER")
        self.assertIsNone(report["decision"]["winner"])

    def test_unknown_result_shapes_fail_closed(self):
        bad = result_for(CASES[0])
        bad["mode"] = "PRETEND_LIVE"
        with self.assertRaises(BakeoffError):
            validate_result(bad)

        bad = result_for(CASES[0])
        bad["provenance"] = []
        with self.assertRaises(BakeoffError):
            validate_result(bad)

    def test_routing_penalizes_forbidden_participant(self):
        case = copy.deepcopy(CASES[0])
        case["forbidden_roles"] = ["Unneeded Observer"]
        result = result_for(case)
        result["participants"].append("Unneeded Observer")
        self.assertLess(score_case(case, result)["routing_accuracy"], 1.0)

    def test_config_rejects_invalid_desktop_and_provenance_contract(self):
        bad = copy.deepcopy(CFG)
        bad["required_desktop_case_count"] = 1
        with self.assertRaises(BakeoffError):
            validate_config(bad)

        bad = copy.deepcopy(CFG)
        bad["desktop_required_passes"] = 1
        with self.assertRaises(BakeoffError):
            validate_config(bad)

        bad = copy.deepcopy(CFG)
        bad["require_provenance"] = False
        with self.assertRaises(BakeoffError):
            validate_config(bad)

        bad = copy.deepcopy(CFG)
        bad["required_provenance_keys"] = []
        with self.assertRaises(BakeoffError):
            validate_config(bad)

    def test_case_and_json_loading_fail_closed(self):
        bad_case = copy.deepcopy(CASES[0])
        bad_case["case_id"] = "Bad ID!"
        with self.assertRaises(BakeoffError):
            validate_case(bad_case)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            invalid = root / "invalid.json"
            invalid.write_text("{", encoding="utf-8")
            with self.assertRaises(BakeoffError):
                load_json(invalid)

            duplicate = root / "duplicate.json"
            duplicate.write_text(json.dumps([CASES[0], CASES[0]]), encoding="utf-8")
            with self.assertRaises(BakeoffError):
                load_cases(duplicate)

    def test_mechanics_and_contribution_metrics_remain_measured(self):
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

        duplicate = {"A": "same useful evidence", "B": "same useful evidence"}
        distinct = {"A": "source provenance timestamp", "B": "human burden accessibility"}
        self.assertGreater(duplicate_content_ratio(duplicate), duplicate_content_ratio(distinct))
        self.assertGreater(unique_contribution_score(distinct), unique_contribution_score(duplicate))


if __name__ == "__main__":
    unittest.main()
