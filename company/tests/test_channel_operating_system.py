import copy
import json
import unittest
from pathlib import Path

from company.runtime.channel_operating_system import (
    ChannelOperatingSystemError,
    EXACT_CONTRACTS,
    REQUIRED_AUDIO_STEMS,
    REQUIRED_PRODUCTION_ROLES,
    REQUIRED_WORKFLOW,
    REQUIRED_GATES,
    validate_config,
    value_at,
)
from company.runtime.lean_video_production import ProductionWorkflowError

ROOT = Path(__file__).resolve().parents[2]
CONFIG = json.loads((ROOT / "company/config/channel_operating_system.json").read_text(encoding="utf-8"))


def replace_at(cfg, path, replacement):
    parts = path.split(".")
    parent = cfg
    for part in parts[:-1]:
        parent = parent[part]
    parent[parts[-1]] = replacement


class ChannelOperatingSystemTests(unittest.TestCase):
    def test_current_config_is_valid(self):
        self.assertTrue(validate_config(copy.deepcopy(CONFIG)))
        self.assertEqual(CONFIG["workflow"], REQUIRED_WORKFLOW)
        self.assertEqual(CONFIG["quality_gates"], REQUIRED_GATES)

    def test_every_exact_contract_rejects_missing_changed_and_wrong_type(self):
        for path, expected in EXACT_CONTRACTS.items():
            changed = (
                not expected
                if isinstance(expected, bool)
                else (
                    expected + 1
                    if isinstance(expected, int)
                    else (expected + ["DRIFT"] if isinstance(expected, list) else expected + "_DRIFT")
                )
            )
            for replacement in [None, changed, {"wrong_type": expected}]:
                with self.subTest(path=path, replacement=replacement):
                    cfg = copy.deepcopy(CONFIG)
                    replace_at(cfg, path, replacement)
                    with self.assertRaises(ChannelOperatingSystemError):
                        validate_config(cfg)

    def test_required_substantive_sets_reject_each_missing_member(self):
        required_sets = {
            "roles": REQUIRED_PRODUCTION_ROLES,
            "audio_system.mandatory_stems": REQUIRED_AUDIO_STEMS,
            "script_schema.required_columns": {"timecode", "narration", "visual_beat_id", "evidence_ids"},
            "visual_generation_brief_system.required_fields": {
                "prompt_version",
                "final_generation_instruction",
                "documentary_evidence_boundary",
                "negative_constraints",
            },
            "visual_generation_brief_system.execution_rules": {
                "NO_PROMPT_NO_GENERATION",
                "PREPRODUCTION_LOCK_REQUIRED",
                "TOOL_MUST_NOT_CREATIVELY_REWRITE_APPROVED_BRIEF",
                "MATERIAL_DEVIATION_RETURNS_TO_STAGE_AUTHORITY",
            },
            "visual_identity.core_principles": {
                "editorial_clarity",
                "one_hero_object",
                "strong_negative_space",
                "episode_specific_visual_metaphor",
                "meaning_driven_motion",
            },
        }
        for path, required in required_sets.items():
            for member in required:
                with self.subTest(path=path, member=member):
                    cfg = copy.deepcopy(CONFIG)
                    replace_at(cfg, path, [item for item in value_at(cfg, path) if item != member])
                    with self.assertRaises(ChannelOperatingSystemError):
                        validate_config(cfg)

    def test_craft_guidance_minimum_lengths(self):
        for path, minimum in {
            "anti_slop_checks.checks": 8,
            "transition_system.canonical": 8,
            "trend_radar.sources": 6,
            "research_system.expert_consultation_required_when": 3,
        }.items():
            with self.subTest(path=path):
                cfg = copy.deepcopy(CONFIG)
                replace_at(cfg, path, value_at(cfg, path)[: minimum - 1])
                with self.assertRaises(ChannelOperatingSystemError):
                    validate_config(cfg)

    def test_topic_weights_and_threshold(self):
        for path, replacement in [("topic_scoring.fields", {"only": 99}), ("topic_scoring.gates.minimum_total", 69)]:
            with self.subTest(path=path):
                cfg = copy.deepcopy(CONFIG)
                replace_at(cfg, path, replacement)
                with self.assertRaises(ChannelOperatingSystemError):
                    validate_config(cfg)
        cfg = copy.deepcopy(CONFIG)
        cfg["topic_scoring"]["gates"]["minimum_total"] = 70
        self.assertTrue(validate_config(cfg))

    def test_lean_failure_is_converted_with_cause(self):
        cfg = copy.deepcopy(CONFIG)
        cfg["quality_gates"].append("P2 Pilot")
        with self.assertRaises(ChannelOperatingSystemError) as caught:
            validate_config(cfg)
        self.assertIsInstance(caught.exception.__cause__, ProductionWorkflowError)

    def test_cancelled_ladder_and_committee_cannot_return(self):
        for field, replacement in [
            ("pilot_ladder", ["P0", "P1", "P2"]),
            ("per_frame_review", True),
            ("per_prototype_review", True),
            ("committee_approval", True),
            ("publication_authorized", True),
        ]:
            with self.subTest(field=field):
                cfg = copy.deepcopy(CONFIG)
                cfg["production_system"][field] = replacement
                with self.assertRaises(ChannelOperatingSystemError):
                    validate_config(cfg)

    def test_value_at_missing_or_non_mapping_parent(self):
        self.assertIsNone(value_at({}, "missing.path"))
        self.assertIsNone(value_at({"a": []}, "a.b"))
        self.assertEqual(value_at({"a": {"b": 0}}, "a.b"), 0)


if __name__ == "__main__":
    unittest.main()
