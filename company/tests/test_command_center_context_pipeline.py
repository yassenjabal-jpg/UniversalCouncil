from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "state" / "command-center"
PROJECT = STATE / "project-governance"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class CommandCenterContextPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.context_map = load(STATE / "project-context-map.json")
        cls.pipeline = load(STATE / "context-pipeline-state.json")
        cls.a1_pre = load(PROJECT / "approvals" / "2026-10-21-repair-a1-context-baseline-pre.json")
        cls.a2_post_path = PROJECT / "approvals" / "2026-10-21-repair-a2-governance-metadata-post.json"
        cls.a3_post_path = PROJECT / "approvals" / "2026-10-21-repair-a3-truth-lock-post.json"
        cls.b1_post_path = PROJECT / "approvals" / "2026-10-21-repair-b1-native-completion-post.json"
        cls.b2_post_path = PROJECT / "approvals" / "2026-10-21-repair-b2-cross-screen-consistency-post.json"
        cls.b3_return_path = PROJECT / "approvals" / "2026-10-21-repair-b3-final-p1-acceptance-return.json"
        cls.b3_return_adoption_path = PROJECT / "approvals" / "2026-10-21-repair-b3-return-state-adoption.json"
        cls.final_p1_post_path = PROJECT / "approvals" / "2026-10-21-repair-b3-final-p1-acceptance-post.json"
        cls.stage7_readiness_post_path = (
            PROJECT / "approvals" / "2026-10-21-stage7-real-host-evidence-readiness-post.json"
        )

    def test_context_map_uses_repaired_provenance_schema(self) -> None:
        self.assertEqual(self.context_map["schema_version"], "2.0")
        self.assertEqual(
            self.context_map["source_type"],
            "project_local_repository_projection",
        )
        self.assertEqual(
            self.context_map["head_validation_mode"],
            "BASELINE_ANCESTOR_AND_SOURCE_BLOBS_MATCH_HEAD",
        )
        self.assertEqual(
            self.context_map["project_manifest"]["governance_system"],
            "al-murtakaz",
        )

    def test_baseline_is_provenance_not_source_revision(self) -> None:
        self.assertEqual(
            self.context_map["baseline_revision"],
            self.a1_pre["canonical_base"]["sha"],
        )
        self.assertEqual(len(self.context_map["baseline_revision"]), 40)
        self.assertEqual(len(self.context_map["source_revision"]), 64)
        self.assertNotEqual(
            self.context_map["baseline_revision"],
            self.context_map["source_revision"],
        )

    def test_context_map_tracks_current_repair_work(self) -> None:
        if self.stage7_readiness_post_path.exists():
            stage7_post = load(self.stage7_readiness_post_path)
            self.assertEqual(stage7_post["decision"], "APPROVED_BY_AL_MURTAKAZ")
            self.assertTrue(stage7_post["repository_readiness_complete"])
            self.assertFalse(stage7_post["stage7_final_lock_granted"])
            expected = ["STAGE7_REAL_HOST_EVIDENCE_PENDING"]
        elif self.final_p1_post_path.exists():
            final_post = load(self.final_p1_post_path)
            self.assertEqual(final_post["decision"], "APPROVED_BY_AL_MURTAKAZ")
            self.assertTrue(final_post["p1_complete"])
            expected = ["P1_COMPLETE_NEXT_PHASE_OWNER_DECISION_REQUIRED"]
        elif self.b3_return_path.exists() and self.b3_return_adoption_path.exists():
            b3_return = load(self.b3_return_path)
            b3_adoption = load(self.b3_return_adoption_path)
            self.assertEqual(b3_return["decision"], "RETURNED_FOR_CHANGES")
            self.assertEqual(b3_adoption["decision"], "APPROVED_BY_AL_MURTAKAZ")
            self.assertTrue(b3_adoption["adoption_authorized"])
            expected = ["P1_EXIT_REMEDIATION_MOTION_AND_ANDROID"]
        elif self.b2_post_path.exists():
            expected = ["REPAIR_WAVE_B3_FINAL_REVIEW_P1_ACCEPTANCE_PENDING"]
        elif self.b1_post_path.exists():
            expected = ["REPAIR_WAVE_B2_CROSS_SCREEN_CONSISTENCY"]
        elif self.a3_post_path.exists():
            expected = ["REPAIR_WAVE_B1_COMPLETE_REMAINING_NATIVE_WORK"]
        elif self.a2_post_path.exists():
            expected = ["REPAIR_WAVE_A3_TRUTH_LOCK_AND_MURTAKAZ_CLOSURE"]
        else:
            expected = ["REPAIR_WAVE_A2_GOVERNANCE_METADATA_RECONCILIATION"]
        self.assertEqual(self.context_map["active_work"], expected)
        self.assertIn(
            "CAPABILITY_REGISTRY_MODEL_BROKER_APPROVED",
            self.context_map["recent_events"],
        )
        self.assertIn(
            "REPAIR_WAVE_A1_CONTEXT_BASELINE_APPROVED",
            self.context_map["recent_events"],
        )
        if self.final_p1_post_path.exists():
            self.assertIn(
                "P1_FINAL_ACCEPTANCE_APPROVED_BY_AL_MURTAKAZ",
                self.context_map["recent_events"],
            )

    def test_canonical_context_has_current_source_truth(self) -> None:
        self.assertEqual(self.context_map["conflicts"], [])
        self.assertTrue(all(source["freshness"] == "CURRENT" for source in self.context_map["sources"]))
        self.assertGreaterEqual(len(self.context_map["sources"]), 16)

    def test_context_pipeline_does_not_expand_authority(self) -> None:
        authority = self.pipeline["authority"]
        self.assertFalse(authority["live_execution_authorized"])
        self.assertFalse(authority["stage8_opened"])
        self.assertFalse(authority["tool_execution_added"])
        self.assertFalse(authority["model_provider_calls_added"])

    def test_a1_anti_drift_truth_rules_are_active(self) -> None:
        truth = self.pipeline["truth_rules"]
        self.assertTrue(truth["baseline_may_be_historical_provenance"])
        self.assertTrue(truth["baseline_must_be_ancestor_of_validated_head"])
        self.assertTrue(truth["source_revision_is_source_set_sha256"])
        self.assertTrue(truth["declared_source_blobs_must_match_validated_head"])
        self.assertTrue(truth["stale_context_blocks_compilation"])
        self.assertTrue(truth["context_conflict_blocks_compilation"])

    def test_untrusted_content_never_governs(self) -> None:
        self.assertFalse(self.pipeline["truth_rules"]["untrusted_content_can_govern"])


if __name__ == "__main__":
    unittest.main()
