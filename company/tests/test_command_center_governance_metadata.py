from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "state" / "command-center"
PROJECT = STATE / "project-governance"
ROADMAP = ROOT / "docs" / "operations" / "command-center" / "COMMAND_CENTER_ROADMAP_2026-10-19.md"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class CommandCenterGovernanceMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.invariants = load(PROJECT / "architecture-invariants.json")
        cls.old_review = load(PROJECT / "agentic-os-latest-review.json")
        cls.current_review = load(PROJECT / "agentic-os-current-review.json")
        cls.agentic_post = load(PROJECT / "approvals" / "2026-10-21-agentic-os-integration-post.json")
        cls.b1_post = load(PROJECT / "approvals" / "2026-10-21-repair-b1-native-completion-post.json")
        cls.roadmap = ROADMAP.read_text(encoding="utf-8")

    def test_old_return_for_alignment_is_preserved_as_history(self) -> None:
        self.assertEqual(self.old_review["verdict"], "RETURN_FOR_ALIGNMENT")
        self.assertEqual(self.old_review["record_status"], "HISTORICAL_SUPERSEDED")
        self.assertTrue(self.old_review["historical_verdict_preserved"])

    def test_current_review_tracks_adopted_lineage(self) -> None:
        self.assertEqual(
            self.current_review["current_verdict"],
            "APPROVED_BY_AL_MURTAKAZ_WITH_REPAIR_PROGRAM_ACTIVE",
        )
        self.assertEqual(
            [item["pr"] for item in self.current_review["merged_lineage"]],
            [56, 57, 58, 59, 60, 61, 62],
        )
        self.assertEqual(
            self.current_review["repair_program"]["wave_a"]["A1"],
            "COMPLETE_APPROVED",
        )
        self.assertEqual(
            self.current_review["repair_program"]["wave_a"]["A2"],
            "COMPLETE_APPROVED",
        )
        self.assertEqual(
            self.current_review["repair_program"]["wave_a"]["A3"],
            "COMPLETE_APPROVED",
        )
        self.assertEqual(
            self.current_review["repair_program"]["wave_a"]["status"],
            "COMPLETE_APPROVED",
        )
        self.assertEqual(
            self.current_review["repair_program"]["wave_b"],
            "ACTIVE",
        )
        self.assertEqual(
            self.current_review["repair_program"]["wave_b_current_stage"],
            "B2_CROSS_SCREEN_CONSISTENCY",
        )
        self.assertEqual(
            self.current_review["repair_program"]["wave_b_b1"],
            "COMPLETE_APPROVED",
        )

    def test_agentic_post_receipt_is_machine_readable_history(self) -> None:
        self.assertEqual(self.agentic_post["normalized_from"]["source"], "PR_COMMENT")
        self.assertEqual(self.agentic_post["normalized_from"]["pr"], 56)
        self.assertFalse(self.agentic_post["normalized_from"]["historical_decision_changed"])
        self.assertTrue(self.agentic_post["adoption_authorized"])
        self.assertTrue(self.agentic_post["merge_authorized"])
        self.assertFalse(self.agentic_post["live_execution_authorized"])

    def test_implemented_invariants_are_not_marked_future(self) -> None:
        by_id = {item["id"]: item for item in self.invariants["invariants"]}
        for invariant_id in ("AO-003", "AO-008", "AO-013", "AO-014", "AO-021"):
            self.assertEqual(by_id[invariant_id]["implementation_state"], "ENFORCED_NOW")
        self.assertEqual(
            by_id["AO-006"]["implementation_state"],
            "ENFORCED_FOR_CONTEXT_RESOLVER_EXTERNAL_RETRIEVAL_FUTURE",
        )

    def test_future_capabilities_are_not_falsely_completed(self) -> None:
        by_id = {item["id"]: item for item in self.invariants["invariants"]}
        self.assertEqual(by_id["AO-022"]["implementation_state"], "FUTURE_BLOCKER")
        self.assertEqual(by_id["AO-023"]["implementation_state"], "FUTURE_BLOCKER")
        self.assertEqual(by_id["AO-015"]["implementation_state"], "CONTRACT_ACTIVE")

    def test_roadmap_marks_slices_one_through_five_complete(self) -> None:
        for marker in (
            "**COMPLETE** — Anti-Drift governance + Context/Change contracts.",
            "**COMPLETE** — Context Resolver and Context Capsule compiler.",
            "**COMPLETE** — Logical Murtakaz Gateway facade + bounded application-service interfaces.",
            "**COMPLETE** — Multi-stage Routing Coordinator.",
            "**COMPLETE** — Capability Registry + Model Broker.",
        ):
            self.assertIn(marker, self.roadmap)
        self.assertNotIn("POST-REVIEW REQUIRED", self.roadmap)

    def test_repairs_pause_skill_registry_without_opening_stage8(self) -> None:
        self.assertIn("**PENDING AFTER REPAIR CLOSURE** — Skill Registry.", self.roadmap)
        self.assertIn(
            "**A2 Governance Metadata Reconciliation — COMPLETE / APPROVED_BY_AL_MURTAKAZ**",
            self.roadmap,
        )
        self.assertIn(
            "**A3 Truth Lock + Murtakaz Closure — COMPLETE / APPROVED_BY_AL_MURTAKAZ**",
            self.roadmap,
        )
        self.assertIn(
            "**B1 Complete Remaining Native Work — COMPLETE / APPROVED_BY_AL_MURTAKAZ**",
            self.roadmap,
        )
        self.assertIn("**B2 Cross-Screen Consistency & Polish — ACTIVE**", self.roadmap)
        self.assertIn("Stage 8 = **NOT_OPENED**", self.roadmap)


    def test_b1_receipt_is_scoped_and_does_not_close_p1(self) -> None:
        self.assertEqual(
            self.b1_post["scoped_verdict"],
            "APPROVE_B1_NATIVE_COMPLETION_ONLY",
        )
        self.assertFalse(self.b1_post["final_p1_approval_granted"])
        self.assertFalse(self.b1_post["p1_complete"])
        self.assertTrue(self.b1_post["b2_r9_authorized"])
        self.assertFalse(self.b1_post["r10_opened"])
        self.assertFalse(self.b1_post["stage8_opened"])

if __name__ == "__main__":
    unittest.main()
