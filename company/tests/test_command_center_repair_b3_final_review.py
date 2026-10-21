from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "state" / "command-center"
PROJECT = STATE / "project-governance"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class CommandCenterRepairB3FinalReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = load(STATE / "living-operations-p1-b3-final-review.json")
        cls.result = load(STATE / "living-operations-p1-b3-final-review-result.json")
        cls.p1 = load(STATE / "living-operations-p1-visual-phase.json")
        cls.screen_review = load(STATE / "living-operations-p1-screen-review.json")
        cls.remainder = load(STATE / "living-operations-p1-remainder-phases.json")
        cls.return_receipt = load(
            PROJECT / "approvals" / "2026-10-21-repair-b3-final-p1-acceptance-return.json"
        )

    def test_desktop_final_fidelity_review_covers_all_eight(self) -> None:
        self.assertEqual(len(self.result["desktop_screens"]), 8)
        self.assertTrue(
            all(item["verdict"] == "APPROVE_DESKTOP_FINAL_FIDELITY_ONLY" for item in self.result["desktop_screens"])
        )

    def test_b3_returns_for_missing_exit_evidence(self) -> None:
        self.assertEqual(self.return_receipt["decision"], "RETURNED_FOR_CHANGES")
        self.assertEqual(
            set(self.return_receipt["blockers"]),
            {"P1_MOTION_CAPTURE_MISSING", "P1_ANDROID_SEMANTIC_ADAPTATION_MISSING"},
        )
        self.assertFalse(self.return_receipt["final_p1_approval_granted"])
        self.assertFalse(self.return_receipt["p1_complete"])

    def test_p1_remains_open_and_stage8_remains_closed(self) -> None:
        self.assertEqual(self.p1["status"], "IN_PROGRESS")
        self.assertFalse(self.p1["stage8_opened"])
        self.assertFalse(self.p1["runtime_authority"])
        self.assertFalse(self.screen_review["phase_complete"])

    def test_r10_is_explicitly_returned_not_ambiguously_pending(self) -> None:
        self.assertEqual(
            self.remainder["phases"]["R10_FINAL_MURTAKAZ_STUDIO_REVIEW"]["state"],
            "RETURNED_FOR_CHANGES",
        )
        self.assertEqual(self.plan["status"], "RETURNED_FOR_CHANGES_EXIT_EVIDENCE_PENDING")

    def test_required_motion_and_android_exit_evidence_remain_blocking(self) -> None:
        self.assertEqual(self.screen_review["shared_motion"]["state"], "B3_EXIT_EVIDENCE_MISSING")
        self.assertEqual(self.screen_review["android_semantic_pair"]["state"], "B3_EXIT_EVIDENCE_MISSING")


if __name__ == "__main__":
    unittest.main()
