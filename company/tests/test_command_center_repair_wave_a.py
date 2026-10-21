from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "state" / "command-center"
PROJECT = STATE / "project-governance"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class CommandCenterRepairWaveATruthLockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lock = load(PROJECT / "repair-wave-a-truth-lock.json")
        cls.stage = load(PROJECT / "stage-phase-map.json")
        cls.phase0 = load(STATE / "phase0-execution-gates.json")
        cls.visual = load(STATE / "living-operations-p1-visual-phase.json")
        cls.cap_model = load(STATE / "capability-model-state.json")
        cls.gateway = load(STATE / "gateway-routing-state.json")

    def test_lock_uses_non_self_referential_source_digest(self) -> None:
        self.assertTrue(self.lock["self_reference_excluded"])
        self.assertEqual(
            self.lock["lock_digest_algorithm"],
            "SHA256_SORTED_ID_PATH_BLOB_TUPLES",
        )
        self.assertEqual(len(self.lock["lock_digest"]), 64)

    def test_approved_lock_is_anchored_to_historical_merge(self) -> None:
        self.assertEqual(self.lock["schema_version"], "1.1")
        self.assertEqual(
            self.lock["locked_revision"],
            "49a013f5fe653c40b43e7a0ca4dd68fc98845fc7",
        )
        self.assertEqual(
            self.lock["validation_mode"],
            "LOCKED_REVISION_SOURCE_BLOBS_MATCH_HISTORICAL_COMMIT",
        )
        self.assertTrue(self.lock["immutable_after_approval"])
        self.assertTrue(self.lock["head_progression_allowed_after_lock"])

    def test_stage_and_execution_truth_remain_closed(self) -> None:
        self.assertEqual(
            self.stage["delivery"]["authoritative_current_stage"],
            "STAGE_7",
        )
        stage8 = next(item for item in self.stage["delivery"]["stages"] if item["id"] == "STAGE_8")
        self.assertEqual(stage8["status"], "NOT_OPENED")
        self.assertFalse(self.phase0["live_execution_authorized"])
        self.assertFalse(all(item["status"] == "PASS" for item in self.phase0["gates"].values()))

    def test_wave_a_did_not_weaken_visual_p1_final_gate(self) -> None:
        self.assertIn(self.visual["status"], {"IN_PROGRESS", "APPROVED_BY_AL_MURTAKAZ"})
        self.assertTrue(self.visual["governance"]["final_approval_required"])
        self.assertFalse(self.visual["runtime_authority"])
        self.assertFalse(self.visual["stage8_opened"])
        if self.visual["status"] == "APPROVED_BY_AL_MURTAKAZ":
            final_post = load(PROJECT / "approvals" / "2026-10-21-repair-b3-final-p1-acceptance-post.json")
            self.assertEqual(final_post["decision"], "APPROVED_BY_AL_MURTAKAZ")
            self.assertTrue(final_post["p1_complete"])

    def test_skill_and_job_engine_are_not_falsely_implemented(self) -> None:
        self.assertEqual(
            self.gateway["components"]["skill_registry"],
            "NOT_IMPLEMENTED",
        )
        self.assertEqual(
            self.gateway["components"]["job_engine"],
            "NOT_IMPLEMENTED",
        )
        self.assertEqual(
            self.cap_model["components"]["skill_registry"],
            "NOT_IMPLEMENTED",
        )
        self.assertEqual(
            self.cap_model["components"]["job_engine"],
            "NOT_IMPLEMENTED",
        )

    def test_model_provider_and_execution_authority_remain_off(self) -> None:
        self.assertEqual(
            self.cap_model["components"]["model_provider_calls"],
            "DISCONNECTED",
        )
        self.assertFalse(
            self.cap_model["laws"]["provider_invocation_authorized"],
        )
        self.assertFalse(
            self.cap_model["laws"]["execution_authority_granted"],
        )

    def test_repair_lineage_closes_in_order(self) -> None:
        self.assertEqual(
            self.lock["repair_lineage"]["A1"],
            "APPROVED_BY_AL_MURTAKAZ",
        )
        self.assertEqual(
            self.lock["repair_lineage"]["A2"],
            "APPROVED_BY_AL_MURTAKAZ",
        )
        self.assertIn(
            self.lock["repair_lineage"]["A3"],
            {"IN_REVIEW", "APPROVED_BY_AL_MURTAKAZ"},
        )


if __name__ == "__main__":
    unittest.main()
