from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from company.runtime.comparative_pilot import (
    ARCHITECTURE_IDS,
    ComparativePilotError,
    evaluate_result,
    prepare_task_packet,
    run_architecture,
    run_comparative_pilot,
    stop_the_line_violations,
    validate_case,
    validate_pilot_config,
)

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "company/config/comparative_pilot.json").read_text(encoding="utf-8"))
CASES = json.loads((ROOT / "benchmarks/canonical_phase4/cases.json").read_text(encoding="utf-8"))


def case(case_id: str) -> dict:
    return next(item for item in CASES if item["case_id"] == case_id)


class Phase4R17ComparativePilotTests(unittest.TestCase):
    def test_config_is_architecture_neutral_and_baseline_can_win(self):
        self.assertTrue(validate_pilot_config(CFG))
        self.assertEqual(set(CFG["architectures"]), {"A", "C", "D", "F"})
        self.assertTrue(CFG["baseline_may_win"])
        self.assertFalse(CFG["agent_mechanics_are_hard_gates"])
        self.assertTrue(CFG["mechanics_are_diagnostic_only"])
        self.assertFalse(CFG["synthetic_pilot_can_authorize_cutover"])

    def test_case_contracts_are_valid(self):
        for item in CASES:
            with self.subTest(case=item["case_id"]):
                self.assertTrue(validate_case(item, CFG))

    def test_task_packet_strips_scoring_truth(self):
        item = case("canary_material_commercial_blocker")
        packet = prepare_task_packet(item, CFG)
        for field in (
            "stage",
            "required_specialists",
            "expected_disposition",
            "expected_route",
            "evidence_required",
            "expected_recovery",
            "expected_dissent_preserved",
        ):
            self.assertNotIn(field, packet)
        self.assertEqual(packet["case_id"], item["case_id"])
        self.assertEqual(packet["operation"], item["operation"])

    def test_all_architectures_run_same_canary_without_authority_bypass(self):
        item = case("canary_authority_bounded_fallback")
        packet = prepare_task_packet(item, CFG)
        for architecture_id in ARCHITECTURE_IDS:
            with self.subTest(architecture=architecture_id):
                result = run_architecture(ROOT, architecture_id, packet, CFG)
                self.assertFalse(result["authority_bypass"])
                self.assertFalse(result["false_success"])
                self.assertIn(result["route"], item["authorized_routes"])
                self.assertEqual(result["authority"]["operation"], item["operation"])
                self.assertEqual(result["authority"]["target"], item["target"])
                self.assertEqual(result["authority"]["scope"], item["scope"])

    def test_material_commercial_canary_blocks_and_preserves_blockers(self):
        item = case("canary_material_commercial_blocker")
        packet = prepare_task_packet(item, CFG)
        for architecture_id in ARCHITECTURE_IDS:
            result = run_architecture(ROOT, architecture_id, packet, CFG)
            scored = evaluate_result(item, result, CFG)
            self.assertEqual(result["disposition"], "BLOCK")
            self.assertEqual(
                set(result["preserved_blockers"]),
                {"customer_skeptic", "moat_auditor"},
            )
            self.assertTrue(scored["hard_gates"]["blocker_preservation"])
            self.assertEqual(stop_the_line_violations(item, result, scored, packet), [])

    def test_hardened_v03_is_eligible_without_agent_mechanics(self):
        item = case("representative_science_freshness")
        packet = prepare_task_packet(item, CFG)
        result = run_architecture(ROOT, "A", packet, CFG)
        scored = evaluate_result(item, result, CFG)
        self.assertTrue(all(scored["hard_gates"].values()))
        self.assertIn("evidence", result["participants"])
        self.assertIn("science", result["participants"])

    def test_baseline_preserves_commercial_specialists(self):
        item = case("representative_commercial_value")
        packet = prepare_task_packet(item, CFG)
        result = run_architecture(ROOT, "A", packet, CFG)
        self.assertIn("customer_skeptic", result["participants"])
        self.assertIn("moat_auditor", result["participants"])

    def test_workflow_first_remains_low_overhead_but_has_lower_voice_coverage(self):
        item = case("representative_commercial_value")
        packet = prepare_task_packet(item, CFG)
        workflow = run_architecture(ROOT, "D", packet, CFG)
        selective = run_architecture(ROOT, "F", packet, CFG)
        workflow_score = evaluate_result(item, workflow, CFG)
        selective_score = evaluate_result(item, selective, CFG)
        self.assertLess(workflow["token_compute_units"], selective["token_compute_units"])
        self.assertLess(
            workflow_score["metrics"]["decision_quality"],
            selective_score["metrics"]["decision_quality"],
        )

    def test_hardened_v03_gui_bias_is_measured_not_disqualifying(self):
        item = case("representative_low_stakes_software")
        packet = prepare_task_packet(item, CFG)
        baseline = run_architecture(ROOT, "A", packet, CFG)
        score = evaluate_result(item, baseline, CFG)
        self.assertEqual(baseline["route"], "semantic_uia")
        self.assertEqual(item["expected_route"], "native_api")
        self.assertEqual(score["metrics"]["reliability"], 0.8)
        self.assertTrue(all(score["hard_gates"].values()))

    def test_selective_architecture_uses_task_aware_native_route(self):
        item = case("representative_low_stakes_software")
        packet = prepare_task_packet(item, CFG)
        result = run_architecture(ROOT, "F", packet, CFG)
        self.assertEqual(result["route"], "native_api")
        self.assertIn("software", result["participants"])
        self.assertIn("execution", result["participants"])

    def test_injected_failure_is_recovered_without_false_success(self):
        item = case("representative_unknown_recovery")
        packet = prepare_task_packet(item, CFG)
        for architecture_id in ARCHITECTURE_IDS:
            result = run_architecture(ROOT, architecture_id, packet, CFG)
            scored = evaluate_result(item, result, CFG)
            self.assertTrue(result["recovered"])
            self.assertFalse(result["false_success"])
            self.assertEqual(scored["metrics"]["recovery"], 1.0)
            self.assertTrue(scored["hard_gates"]["no_false_success"])

    def test_security_blocker_never_dispatches_without_authorized_route(self):
        item = case("representative_security_blocker")
        packet = prepare_task_packet(item, CFG)
        for architecture_id in ARCHITECTURE_IDS:
            result = run_architecture(ROOT, architecture_id, packet, CFG)
            scored = evaluate_result(item, result, CFG)
            self.assertEqual(result["disposition"], "BLOCK")
            self.assertIsNone(result["route"])
            self.assertEqual(result["status"], "BLOCKED")
            self.assertTrue(all(scored["hard_gates"].values()))

    def test_stop_the_line_detects_authority_bypass_false_success_and_routing_failure(self):
        item = case("canary_authority_bounded_fallback")
        packet = prepare_task_packet(item, CFG)
        result = run_architecture(ROOT, "F", packet, CFG)
        scored = evaluate_result(item, result, CFG)

        bypass = copy.deepcopy(result)
        bypass["authority_bypass"] = True
        bypass_score = copy.deepcopy(scored)
        bypass_score["hard_gates"]["authority_integrity"] = False
        self.assertIn(
            "authority_bypass",
            stop_the_line_violations(item, bypass, bypass_score, packet),
        )

        false_success = copy.deepcopy(result)
        false_success["false_success"] = True
        false_score = copy.deepcopy(scored)
        false_score["hard_gates"]["no_false_success"] = False
        self.assertIn(
            "false_success",
            stop_the_line_violations(item, false_success, false_score, packet),
        )

        no_route = copy.deepcopy(result)
        no_route["route"] = None
        self.assertIn(
            "routing_failure",
            stop_the_line_violations(item, no_route, scored, packet),
        )

    def test_full_pilot_runs_canary_before_representative_and_never_authorizes_cutover(self):
        report = run_comparative_pilot(ROOT, CASES, CFG)
        self.assertEqual(report["status"], "COMPLETED")
        self.assertFalse(report["violations"])
        self.assertEqual(
            {item["architecture_id"] for item in report["architecture_summaries"]},
            {"A", "C", "D", "F"},
        )
        self.assertIn(report["outcome"], CFG["allowed_outcomes"])
        self.assertFalse(report["cutover_authorized"])
        self.assertEqual(report["evidence_class"], "DETERMINISTIC_SYNTHETIC_PILOT")
        self.assertTrue(report["canary_scores"])
        self.assertTrue(report["representative_scores"])

    def test_invalid_config_case_packet_and_result_fail_closed(self):
        bad_cfg = copy.deepcopy(CFG)
        bad_cfg["baseline_may_win"] = False
        with self.assertRaises(ComparativePilotError):
            validate_pilot_config(bad_cfg)

        bad_case = copy.deepcopy(CASES[0])
        bad_case.pop("expected_disposition")
        with self.assertRaises(ComparativePilotError):
            validate_case(bad_case, CFG)

        packet = prepare_task_packet(CASES[0], CFG)
        with self.assertRaises(ComparativePilotError):
            run_architecture(ROOT, "Z", packet, CFG)
        with self.assertRaises(ComparativePilotError):
            run_architecture(ROOT, "A", {**packet, "expected_route": "leak"}, CFG)

        result = run_architecture(ROOT, "A", packet, CFG)
        bad_result = copy.deepcopy(result)
        bad_result["case_id"] = "wrong"
        with self.assertRaises(ComparativePilotError):
            evaluate_result(CASES[0], bad_result, CFG)

    def test_canary_stop_the_line_skips_representative_work(self):
        broken_cases = copy.deepcopy(CASES)
        canary = next(
            item
            for item in broken_cases
            if item["case_id"] == "canary_authority_bounded_fallback"
        )
        canary["available_routes"] = ["native_host_tooling"]
        canary["authorized_routes"] = ["native_host_tooling"]
        canary["expected_route"] = "native_host_tooling"
        canary["expected_disposition"] = "PROCEED"

        report = run_comparative_pilot(ROOT, broken_cases, CFG)
        self.assertEqual(report["status"], "STOP_THE_LINE")
        self.assertEqual(report["outcome"], "STOP_THE_LINE")
        self.assertTrue(report["violations"])
        self.assertEqual(report["representative_scores"], [])
        self.assertEqual(report["architecture_summaries"], [])


if __name__ == "__main__":
    unittest.main()
