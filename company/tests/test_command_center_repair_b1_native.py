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
        cls.stage7_post_path = (
            PROJECT / "approvals" / "2026-10-21-stage7-real-host-evidence-readiness-post.json"
        )

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

    def test_b1_never_granted_final_p1_or_opened_stage8(self) -> None:
        self.assertFalse(self.review["final_p1_approval"])
        if self.post_path.exists():
            post = load(self.post_path)
            self.assertFalse(post["final_p1_approval_granted"])
        self.assertIn(self.p1["status"], {"IN_PROGRESS", "APPROVED_BY_AL_MURTAKAZ"})
        self.assertFalse(self.p1["stage8_opened"])
        self.assertFalse(self.p1["runtime_authority"])
        if self.p1["status"] == "APPROVED_BY_AL_MURTAKAZ":
            self.assertTrue(self.screen_review["phase_complete"])

    def test_b1_lifecycle_advances_only_after_post_review(self) -> None:
        if self.post_path.exists():
            self.assertEqual(self.ledger["status"], "APPROVED_BY_AL_MURTAKAZ")
            self.assertTrue(all(item["state"] == "MICRO_POLISH_COMPLETE" for item in self.ledger["screens"]))
            self.assertIn(
                self.remainder["phases"]["R9_CROSS_SCREEN_CONSISTENCY_AUDIT"]["state"],
                {"READY_TO_CONTINUE", "CLOSED"},
            )
            self.assertIn(
                self.remainder["phases"]["R10_FINAL_MURTAKAZ_STUDIO_REVIEW"]["state"],
                {"NOT_OPENED", "MURTAKAZ_STUDIO_REVIEW", "RETURNED_FOR_CHANGES", "CLOSED"},
            )
            allowed_active_work = [
                ["REPAIR_WAVE_B2_CROSS_SCREEN_CONSISTENCY"],
                ["REPAIR_WAVE_B3_FINAL_REVIEW_P1_ACCEPTANCE_PENDING"],
                ["P1_EXIT_REMEDIATION_MOTION_AND_ANDROID"],
                ["P1_COMPLETE_NEXT_PHASE_OWNER_DECISION_REQUIRED"],
            ]
            if self.stage7_post_path.exists():
                stage7_post = load(self.stage7_post_path)
                self.assertEqual(stage7_post["decision"], "APPROVED_BY_AL_MURTAKAZ")
                self.assertTrue(stage7_post["repository_readiness_complete"])
                self.assertFalse(stage7_post["stage7_final_lock_granted"])
                allowed_active_work.append(["STAGE7_REAL_HOST_EVIDENCE_PENDING"])
            self.assertIn(self.context["active_work"], allowed_active_work)
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
