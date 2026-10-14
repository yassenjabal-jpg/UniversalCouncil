from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import company.runtime.comparative_pilot as cp

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "company/config/comparative_pilot.json").read_text(encoding="utf-8"))
CASES = json.loads((ROOT / "benchmarks/canonical_phase4/cases.json").read_text(encoding="utf-8"))


def get_case(case_id: str) -> dict:
    return copy.deepcopy(next(item for item in CASES if item["case_id"] == case_id))


def normalized_without_dimension(cfg: dict, dimension: str) -> dict:
    broken = copy.deepcopy(cfg)
    broken["evaluation_dimensions"] = [item for item in broken["evaluation_dimensions"] if item != dimension]
    broken["weights"].pop(dimension)
    total = sum(broken["weights"].values())
    broken["weights"] = {key: value / total for key, value in broken["weights"].items()}
    return broken


class Phase4R17FailClosedCoverageTests(unittest.TestCase):
    def test_config_validation_fail_closed_matrix(self):
        invalid_configs = []

        invalid_configs.append("bad")

        broken = copy.deepcopy(CFG)
        broken["version"] = "2.0"
        invalid_configs.append(broken)

        broken = copy.deepcopy(CFG)
        broken["status"] = "GOVERNING"
        invalid_configs.append(broken)

        broken = copy.deepcopy(CFG)
        broken["governing_council_version"] = "0.4.0"
        invalid_configs.append(broken)

        broken = copy.deepcopy(CFG)
        broken["synthetic_pilot_can_authorize_cutover"] = True
        invalid_configs.append(broken)

        broken = copy.deepcopy(CFG)
        broken["agent_mechanics_are_hard_gates"] = True
        invalid_configs.append(broken)

        broken = copy.deepcopy(CFG)
        broken["mechanics_are_diagnostic_only"] = False
        invalid_configs.append(broken)

        broken = copy.deepcopy(CFG)
        broken["architectures"].pop("A")
        invalid_configs.append(broken)

        broken = copy.deepcopy(CFG)
        broken["architectures"]["A"]["diagnostics"] = None
        invalid_configs.append(broken)

        broken = copy.deepcopy(CFG)
        broken["architectures"]["A"]["diagnostics"]["operator_steps"] = -1
        invalid_configs.append(broken)

        broken = copy.deepcopy(CFG)
        broken["weights"] = []
        invalid_configs.append(broken)

        broken = copy.deepcopy(CFG)
        broken["weights"].pop("latency")
        invalid_configs.append(broken)

        broken = copy.deepcopy(CFG)
        broken["weights"]["latency"] += 0.2
        invalid_configs.append(broken)

        broken = copy.deepcopy(CFG)
        broken["stop_the_line_conditions"] = ["authority_bypass"]
        invalid_configs.append(broken)

        broken = copy.deepcopy(CFG)
        broken["winner_margin"] = -0.1
        invalid_configs.append(broken)

        for index, invalid in enumerate(invalid_configs):
            with self.subTest(index=index):
                with self.assertRaises(cp.ComparativePilotError):
                    cp.validate_pilot_config(invalid)

    def test_case_validation_fail_closed_matrix(self):
        invalid_cases = []

        invalid_cases.append("bad")

        broken = get_case("representative_low_stakes_software")
        broken["stage"] = "FULL"
        invalid_cases.append(broken)

        broken = get_case("representative_low_stakes_software")
        broken["task_class"] = "unknown"
        invalid_cases.append(broken)

        broken = get_case("representative_low_stakes_software")
        broken["case_id"] = ""
        invalid_cases.append(broken)

        broken = get_case("representative_low_stakes_software")
        broken["domains"] = "software"
        invalid_cases.append(broken)

        broken = get_case("representative_low_stakes_software")
        broken["expected_disposition"] = "MAYBE"
        invalid_cases.append(broken)

        broken = get_case("representative_low_stakes_software")
        broken["expected_route"] = 5
        invalid_cases.append(broken)

        broken = get_case("representative_low_stakes_software")
        broken["expected_route"] = "visual_grounding"
        invalid_cases.append(broken)

        for index, invalid in enumerate(invalid_cases):
            with self.subTest(index=index):
                with self.assertRaises(cp.ComparativePilotError):
                    cp.validate_case(invalid, CFG)

    def test_prepare_packet_and_architecture_leakage_guards(self):
        item = get_case("representative_low_stakes_software")
        original_task_fields = cp.TASK_FIELDS
        try:
            cp.TASK_FIELDS = set(original_task_fields) | {"expected_route"}
            with self.assertRaises(cp.ComparativePilotError):
                cp.prepare_task_packet(item, CFG)
        finally:
            cp.TASK_FIELDS = original_task_fields

        packet = cp.prepare_task_packet(item, CFG)
        leaked = {**packet, "expected_route": item["expected_route"]}
        with self.assertRaises(cp.ComparativePilotError):
            cp.run_architecture(ROOT, "A", leaked, CFG)

    def test_legacy_host_work_route_branch(self):
        packet = cp.prepare_task_packet(get_case("representative_low_stakes_software"), CFG)
        packet["task_class"] = "host_work"
        packet["available_routes"] = ["dc_control_plane", "native_host_tooling"]
        packet["authorized_routes"] = ["dc_control_plane"]
        self.assertEqual(cp._legacy_route(packet), "dc_control_plane")

    def test_evaluate_result_rejects_bad_architecture_dimension_set_and_metric_range(self):
        item = get_case("representative_low_stakes_software")
        packet = cp.prepare_task_packet(item, CFG)
        result = cp.run_architecture(ROOT, "F", packet, CFG)

        bad_architecture = copy.deepcopy(result)
        bad_architecture["architecture_id"] = "Z"
        with self.assertRaises(cp.ComparativePilotError):
            cp.evaluate_result(item, bad_architecture, CFG)

        bad_dimensions = normalized_without_dimension(CFG, "latency")
        with self.assertRaises(cp.ComparativePilotError):
            cp.evaluate_result(item, result, bad_dimensions)

        bad_metric = copy.deepcopy(result)
        bad_metric["latency_units"] = -10.0
        with self.assertRaises(cp.ComparativePilotError):
            cp.evaluate_result(item, bad_metric, CFG)

    def test_stop_line_covers_leakage_and_invalid_scoring(self):
        item = get_case("canary_authority_bounded_fallback")
        packet = cp.prepare_task_packet(item, CFG)
        result = cp.run_architecture(ROOT, "F", packet, CFG)
        scored = cp.evaluate_result(item, result, CFG)

        leaked_packet = {**packet, "expected_route": item["expected_route"]}
        self.assertIn(
            "benchmark_leakage",
            cp.stop_the_line_violations(item, result, scored, leaked_packet),
        )

        bad_scoring = copy.deepcopy(scored)
        bad_scoring["hard_gates"]["scoring_validity"] = False
        self.assertIn(
            "invalid_scoring",
            cp.stop_the_line_violations(item, result, bad_scoring, packet),
        )

    def test_aggregate_requires_representative_scores(self):
        with self.assertRaises(cp.ComparativePilotError):
            cp._aggregate_architecture("A", [], CFG)

    def test_outcome_paths_are_available_without_forcing_winner(self):
        no_eligible = [
            {"architecture_id": architecture_id, "eligible": False, "score": 0.9}
            for architecture_id in cp.ARCHITECTURE_IDS
        ]
        result = cp._select_outcome(no_eligible, CFG)
        self.assertEqual(result["outcome"], "INCONCLUSIVE")
        self.assertIsNone(result["leader"])
        self.assertFalse(result["cutover_authorized"])

        close = [
            {"architecture_id": "A", "eligible": True, "score": 0.91},
            {"architecture_id": "F", "eligible": True, "score": 0.90},
        ]
        result = cp._select_outcome(close, CFG)
        self.assertEqual(result["outcome"], "INCONCLUSIVE")

        baseline_clear = [
            {"architecture_id": "A", "eligible": True, "score": 0.95},
            {"architecture_id": "F", "eligible": True, "score": 0.80},
        ]
        result = cp._select_outcome(baseline_clear, CFG)
        self.assertEqual(result["outcome"], "KEEP_v0.3")
        self.assertEqual(result["leader"], "A")
        self.assertFalse(result["cutover_authorized"])

        candidate_clear = [
            {"architecture_id": "F", "eligible": True, "score": 0.95},
            {"architecture_id": "A", "eligible": True, "score": 0.80},
        ]
        result = cp._select_outcome(candidate_clear, CFG)
        self.assertEqual(result["outcome"], "ADOPT_COMPONENTS")
        self.assertEqual(result["leader"], "F")
        self.assertFalse(result["cutover_authorized"])

    def test_run_pilot_rejects_missing_case_set(self):
        for invalid in (None, [], "bad"):
            with self.subTest(invalid=invalid):
                with self.assertRaises(cp.ComparativePilotError):
                    cp.run_comparative_pilot(ROOT, invalid, CFG)


if __name__ == "__main__":
    unittest.main()
