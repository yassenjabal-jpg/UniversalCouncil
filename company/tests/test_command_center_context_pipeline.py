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
        cls.pre = load(
            PROJECT
            / "approvals"
            / "2026-10-21-context-resolver-compiler-pre.json"
        )

    def test_context_map_is_read_only_project_local_truth(self) -> None:
        self.assertEqual(
            self.context_map["source_type"],
            "project_local_repository_projection",
        )
        self.assertEqual(
            self.context_map["project_manifest"]["governance_system"],
            "al-murtakaz",
        )
        self.assertFalse(
            self.context_map["current_state"]["live_execution_authorized"]
        )
        self.assertFalse(self.context_map["current_state"]["stage8_opened"])

    def test_context_map_is_pinned_to_preapproved_baseline(self) -> None:
        self.assertEqual(
            self.context_map["source_revision"],
            self.pre["canonical_base"]["sha"],
        )

    def test_canonical_context_starts_without_unresolved_conflict(self) -> None:
        self.assertEqual(self.context_map["conflicts"], [])
        self.assertTrue(
            all(
                source["freshness"] == "CURRENT"
                for source in self.context_map["sources"]
            )
        )

    def test_context_pipeline_does_not_expand_authority(self) -> None:
        authority = self.pipeline["authority"]
        self.assertFalse(authority["live_execution_authorized"])
        self.assertFalse(authority["stage8_opened"])
        self.assertFalse(authority["tool_execution_added"])
        self.assertFalse(authority["model_provider_calls_added"])

    def test_untrusted_content_never_governs(self) -> None:
        self.assertFalse(
            self.pipeline["truth_rules"]["untrusted_content_can_govern"]
        )

    def test_capsule_foundation_is_deterministic_and_fail_closed(self) -> None:
        truth = self.pipeline["truth_rules"]
        self.assertTrue(truth["deterministic_capsule_id"])
        self.assertTrue(truth["source_digest_changes_capsule_id"])
        self.assertTrue(truth["stale_context_blocks_compilation"])
        self.assertTrue(truth["context_conflict_blocks_compilation"])


if __name__ == "__main__":
    unittest.main()
