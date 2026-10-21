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
        self.assertEqual(
            self.context_map["active_work"],
            ["REPAIR_WAVE_A1_CONTEXT_BASELINE"],
        )
        self.assertIn(
            "CAPABILITY_REGISTRY_MODEL_BROKER_APPROVED",
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
