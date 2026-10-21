from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "state" / "command-center"
PROJECT = STATE / "project-governance"

ROLES = [
    "home_owner_workspace",
    "living_project_workspace",
    "software_autopilot_project",
    "studio_project",
    "owner_decision_mode",
    "checkpoint_recovery_fork",
    "pulse_visual_project_story",
    "project_complete_work_receipt",
]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class CommandCenterRepairB1NativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ledger = load(STATE / "living-operations-p1-b1-native-completion.json")
        cls.review = load(STATE / "living-operations-p1-b1-visual-review.json")
        cls.screen_review = load(STATE / "living-operations-p1-screen-review.json")
        cls.remainder = load(STATE / "living-operations-p1-remainder-phases.json")
        cls.p1 = load(STATE / "living-operations-p1-visual-phase.json")
        cls.context = load(STATE / "project-context-map.json")
        cls.post_path = PROJECT / "approvals" / "2026-10-21-repair-b1-native-completion-post.json"

    def test_all_eight_canonical_roles_have_triple_evidence(self) -> None:
        self.assertEqual(
            [item["role"] for item in self.ledger["screens"]],
            ROLES,
        )
        for item in self.ledger["screens"]:
            evidence = item["evidence"]
            self.assertEqual(len(evidence["reference_sha256"]), 64)
            self.assertEqual(len(evidence["native_sha256"]), 64)
            self.assertEqual(len(evidence["blend_sha256"]), 64)

    def test_material_native_evidence_hides_reference_pixels(self) -> None:
        material = self.ledger["material_evidence"]
        self.assertTrue(material["native_only_reference_hidden"])
        self.assertTrue(material["shared_secondary_chrome_completed"])
        self.assertTrue(material["decision_native_project_underlay_completed"])
        self.assertEqual(material["render"], "PASS")

    def test_visual_review_has_no_b1_structural_blocker(self) -> None:
        self.assertEqual(
            [item["role"] for item in self.review["findings"]],
            ROLES,
        )
        self.assertTrue(all(item["verdict"] == "NO_B1_BLOCKER" for item in self.review["findings"]))
        self.assertFalse(self.review["final_p1_approval"])

    def test_b1_never_closes_p1_or_opens_stage8(self) -> None:
        self.assertEqual(self.p1["status"], "IN_PROGRESS")
        self.assertFalse(self.p1["stage8_opened"])
        self.assertFalse(self.p1["runtime_authority"])
        self.assertFalse(self.screen_review["phase_complete"])

    def test_b1_lifecycle_advances_only_after_post_review(self) -> None:
        if self.post_path.exists():
            self.assertEqual(self.ledger["status"], "APPROVED_BY_AL_MURTAKAZ")
            self.assertTrue(all(item["state"] == "MICRO_POLISH_COMPLETE" for item in self.ledger["screens"]))
            self.assertEqual(
                self.remainder["phases"]["R9_CROSS_SCREEN_CONSISTENCY_AUDIT"]["state"],
                "READY_TO_CONTINUE",
            )
            self.assertEqual(
                self.context["active_work"],
                ["REPAIR_WAVE_B2_CROSS_SCREEN_CONSISTENCY"],
            )
        else:
            self.assertEqual(self.ledger["status"], "MURTAKAZ_REVIEW_REQUIRED")
            self.assertTrue(
                all(item["state"] == "MICRO_POLISH_COMPLETE_REVIEW_REQUIRED" for item in self.ledger["screens"])
            )
            self.assertEqual(
                self.remainder["phases"]["R9_CROSS_SCREEN_CONSISTENCY_AUDIT"]["state"],
                "NOT_OPENED",
            )
            self.assertEqual(
                self.context["active_work"],
                ["REPAIR_WAVE_B1_COMPLETE_REMAINING_NATIVE_WORK"],
            )


if __name__ == "__main__":
    unittest.main()
