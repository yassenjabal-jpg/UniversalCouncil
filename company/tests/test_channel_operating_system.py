import copy
import json
import unittest
from pathlib import Path

from company.runtime.channel_operating_system import (
    ChannelOperatingSystemError,
    REQUIRED_AUDIO_STEMS,
    REQUIRED_PRODUCTION_ROLES,
    REQUIRED_SCRIPT_PASSES,
    REQUIRED_WORKFLOW,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[2]
CONFIG = json.loads((ROOT / "company" / "config" / "channel_operating_system.json").read_text(encoding="utf-8"))


class ChannelOperatingSystemTests(unittest.TestCase):
    def test_current_config_is_valid(self):
        self.assertTrue(validate_config(copy.deepcopy(CONFIG)))

    def test_topic_weights_total_100(self):
        self.assertEqual(sum(CONFIG["topic_scoring"]["fields"].values()), 100)

    def test_workflow_is_exact_and_ordered(self):
        self.assertEqual(CONFIG["workflow"], REQUIRED_WORKFLOW)
        workflow = CONFIG["workflow"]
        self.assertLess(workflow.index("visual_story_case"), workflow.index("script_development"))
        self.assertLess(workflow.index("preproduction_craft_review"), workflow.index("script_lock"))
        self.assertLess(workflow.index("independent_fact_check"), workflow.index("script_lock"))
        self.assertLess(
            workflow.index("audio_spotting_and_sonic_concept"), workflow.index("reference_frame_assignment")
        )
        self.assertLess(workflow.index("animatic"), workflow.index("production_readiness_review"))
        self.assertLess(workflow.index("production_readiness_review"), workflow.index("production"))
        self.assertLess(workflow.index("editorial_rough_cut"), workflow.index("packaging_finalization_and_test_plan"))
        self.assertLess(workflow.index("picture_lock"), workflow.index("music_sound_design"))
        self.assertLess(workflow.index("mix_master"), workflow.index("audiovisual_sync_qc"))

    def test_benchmark_roles_are_distinct_and_required(self):
        roles = set(CONFIG["roles"])
        self.assertTrue(REQUIRED_PRODUCTION_ROLES.issubset(roles))
        for role in {
            "Media Producer / Production Coordinator",
            "Independent Fact Checker",
            "Thumbnail & Packaging Designer",
            "Audience Growth & Packaging Strategist",
            "Motion & Picture Editor",
        }:
            self.assertIn(role, roles)
        self.assertNotEqual(
            CONFIG["roles"]["Audience Growth & Packaging Strategist"],
            CONFIG["roles"]["Thumbnail & Packaging Designer"],
        )

    def test_professional_preproduction_contract(self):
        benchmark = CONFIG["benchmark_profile"]
        self.assertTrue(benchmark["adopt_disciplines_not_headcount"])
        self.assertGreaterEqual(len(benchmark["reference_models"]), 5)

        visual = CONFIG["visual_story_case"]
        self.assertTrue(visual["required"])
        self.assertTrue(visual["must_precede_script_lock"])
        self.assertIn("why_video_not_article", visual["required_fields"])
        self.assertIn("key_visual", visual["required_fields"])
        self.assertIn("editor_feasibility_note", visual["required_fields"])

        preprod = CONFIG["preproduction_craft_review"]
        self.assertTrue(preprod["required"])
        self.assertIn("Motion & Picture Editor", preprod["participants"])
        self.assertIn("Music Supervisor & Sound Designer", preprod["participants"])
        self.assertIn("Media Producer / Production Coordinator", preprod["participants"])

    def test_script_development_is_multi_pass_and_fact_checked(self):
        scripts = CONFIG["script_development"]
        self.assertTrue(scripts["single_pass_forbidden"])
        self.assertEqual(scripts["required_passes"], REQUIRED_SCRIPT_PASSES)
        self.assertTrue(scripts["fact_check_before_lock"])
        self.assertTrue(scripts["visual_draft_requires_editor_review"])

    def test_evidence_and_visual_rights_are_separate(self):
        research = CONFIG["research_system"]
        self.assertTrue(research["claim_source_sheet_required"])
        self.assertTrue(research["visual_source_rights_sheet_required"])
        self.assertTrue(research["separate_claim_and_visual_ledgers"])

    def test_production_readiness_fails_closed(self):
        gate = CONFIG["production_readiness"]
        self.assertTrue(gate["required"])
        self.assertEqual(gate["fail_action"], "HOLD_PRODUCTION")
        for check in {
            "script_locked",
            "independent_fact_check_passed",
            "visual_rights_clear",
            "audio_spotting_complete",
            "specialized_tools_available",
            "schedule_acceptable",
            "budget_acceptable",
        }:
            self.assertIn(check, gate["required_checks"])

    def test_packaging_has_early_and_final_stages(self):
        packaging = CONFIG["packaging_system"]
        self.assertTrue(packaging["thumbnail_designer_independent_craft_function"])
        self.assertGreaterEqual(len(packaging["stage_a_before_script"]), 4)
        self.assertGreaterEqual(len(packaging["stage_b_after_rough_cut"]), 4)

    def test_audio_contract(self):
        audio = CONFIG["audio_system"]
        self.assertTrue(audio["spotting_required_before_reference_frame_lock"])
        self.assertTrue(audio["picture_lock_required_before_final_sound_design"])
        self.assertTrue(audio["post_picture_lock_timing_change_requires_audio_reconform"])
        self.assertEqual(set(audio["mandatory_stems"]), REQUIRED_AUDIO_STEMS)
        targets = audio["mix_targets_internal_not_platform_requirements"]
        self.assertEqual(targets["program_integrated_lufs_target"], "-14 LUFS ±1")
        self.assertEqual(targets["true_peak_ceiling"], "-1 dBTP")

    def test_fail_closed_on_governance_drift(self):
        mutations = [
            lambda c: c.__setitem__("version", "2"),
            lambda c: c.__setitem__("channel_model", "single_niche"),
            lambda c: c.__setitem__("visual_system", "other"),
            lambda c: c.__setitem__("publication_authority", "AUTO"),
            lambda c: c["benchmark_profile"].__setitem__("adopt_disciplines_not_headcount", False),
            lambda c: c["benchmark_profile"].__setitem__("reference_models", []),
            lambda c: c["portfolio_balance"].__setitem__("initial_window_videos", 5),
            lambda c: c["trend_radar"].__setitem__("sources", []),
            lambda c: c.__setitem__("workflow", c["workflow"][:-1]),
            lambda c: c["research_system"].__setitem__("claim_source_sheet_required", False),
            lambda c: c["research_system"].__setitem__("separate_claim_and_visual_ledgers", False),
            lambda c: c["visual_story_case"].__setitem__("required", False),
            lambda c: c["visual_story_case"].__setitem__("required_fields", []),
            lambda c: c["preproduction_craft_review"].__setitem__("required", False),
            lambda c: c["preproduction_craft_review"].__setitem__("participants", []),
            lambda c: c["script_development"].__setitem__("single_pass_forbidden", False),
            lambda c: c["script_development"].__setitem__("required_passes", ["one"]),
            lambda c: c["script_development"].__setitem__("fact_check_before_lock", False),
            lambda c: c["production_readiness"].__setitem__("required", False),
            lambda c: c["production_readiness"].__setitem__("required_checks", []),
            lambda c: c["packaging_system"].__setitem__("thumbnail_designer_independent_craft_function", False),
            lambda c: c["script_schema"].__setitem__("required_columns", ["narration"]),
            lambda c: c["frame_bible"].__setitem__(
                "canonical_frame_types", c["frame_bible"]["canonical_frame_types"][:-1]
            ),
            lambda c: c["transition_system"].__setitem__("canonical", ["cut"]),
            lambda c: c["audio_system"].__setitem__("principle", "sound added after picture"),
            lambda c: c["audio_system"].__setitem__("mandatory_stems", ["FULL master"]),
            lambda c: c["audio_system"]["mix_targets_internal_not_platform_requirements"].__setitem__(
                "true_peak_ceiling", "0 dBTP"
            ),
            lambda c: c["anti_slop_gate"].__setitem__("required", False),
            lambda c: c.__setitem__("quality_gates", []),
            lambda c: c["roles"].pop("Independent Fact Checker"),
            lambda c: c["roles"].pop("Thumbnail & Packaging Designer"),
            lambda c: c["roles"].pop("Media Producer / Production Coordinator"),
        ]
        for mutate in mutations:
            cfg = copy.deepcopy(CONFIG)
            mutate(cfg)
            with self.assertRaises(ChannelOperatingSystemError):
                validate_config(cfg)


if __name__ == "__main__":
    unittest.main()
