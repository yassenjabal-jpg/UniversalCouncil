from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "state" / "command-center"
PROJECT = STATE / "project-governance"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class CommandCenterUxStateContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ux = load(STATE / "living-operations-ux-state-contract.json")
        cls.impact = load(STATE / "living-operations-agentic-ux-impact.json")
        cls.agentic = load(PROJECT / "agentic-os-policy.json")
        cls.manifest = load(STATE / "living-operations-reference-manifest.json")

    def test_contracts_are_murtakaz_approved(self) -> None:
        self.assertEqual(self.ux["status"], "APPROVED_BY_AL_MURTAKAZ")
        self.assertEqual(self.impact["status"], "APPROVED_BY_AL_MURTAKAZ")

    def test_all_eight_canonical_screens_are_audited(self) -> None:
        self.assertEqual(len(self.impact["screens"]), 8)
        self.assertEqual(
            {screen["id"] for screen in self.impact["screens"]},
            {reference["role"] for reference in self.manifest["references"]},
        )

    def test_ux_states_match_agentic_result_model(self) -> None:
        self.assertEqual(
            [item["id"] for item in self.ux["primary_states"]],
            self.agentic["result_model"]["states"],
        )

    def test_only_succeeded_is_success(self) -> None:
        success = [item["id"] for item in self.ux["primary_states"] if item["success"]]
        self.assertEqual(success, ["SUCCEEDED"])
        self.assertTrue(self.ux["laws"]["unknown_never_success"])

    def test_context_drift_states_remain_distinct(self) -> None:
        states = {item["id"] for item in self.ux["primary_states"]}
        self.assertIn("STALE_CONTEXT", states)
        self.assertIn("CONTEXT_CONFLICT", states)
        self.assertIn("UNKNOWN", states)

    def test_android_complete_maps_only_to_verified_success(self) -> None:
        self.assertEqual(self.ux["android_projection"]["COMPLETE"], ["SUCCEEDED"])

    def test_progressive_disclosure_keeps_home_simple(self) -> None:
        levels = self.ux["default_surface_level"]
        self.assertEqual(levels["home"], 1)
        self.assertEqual(levels["project_workspace"], 2)
        self.assertEqual(levels["system"], 3)

    def test_visual_direction_is_unchanged(self) -> None:
        self.assertFalse(self.ux["visual_direction_change"])
        self.assertFalse(self.impact["visual_direction_changed"])
        for screen in self.impact["screens"]:
            self.assertIn("KEEP", screen["decisions"])

    def test_context_resolver_dependency_is_explicit(self) -> None:
        required = set(self.ux["engineering_requirements_for_context_resolver"])
        self.assertEqual(
            required,
            {
                "context_freshness",
                "context_conflict",
                "source_revision",
                "context_capsule_id",
                "canonical_source_ids",
                "conflict_provenance",
                "change_of_truth_flag",
            },
        )


if __name__ == "__main__":
    unittest.main()
