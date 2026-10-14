import json
import unittest
from pathlib import Path

from company.runtime.media_controls import (
    REQUIRED_MEDIA_FUNCTIONS,
    REQUIRED_PILOT_METRICS,
    MediaControlError,
    validate_media_pilot_record,
    validate_media_scale_request,
    validate_media_team,
)

ROOT = Path(__file__).resolve().parents[2]


class MediaCapabilityTests(unittest.TestCase):
    def load_config(self):
        return json.loads((ROOT / "company/config/media_venture.json").read_text(encoding="utf-8"))

    def base_metrics(self):
        return sorted(REQUIRED_PILOT_METRICS)

    def test_required_media_functions_exist(self):
        cfg = self.load_config()
        self.assertTrue(validate_media_team(cfg))
        ids = {x["id"] for x in cfg["production_functions"]}
        self.assertEqual(ids, REQUIRED_MEDIA_FUNCTIONS)

    def test_studio_benchmark_functions_are_active(self):
        cfg = self.load_config()
        by_id = {x["id"]: x for x in cfg["production_functions"]}
        for function_id in {
            "media_producer",
            "independent_fact_checker",
            "audience_growth_strategist",
            "thumbnail_packaging_designer",
            "motion_picture_editor",
        }:
            self.assertEqual(by_id[function_id]["default_status"], "ACTIVE_FOR_MEDIA_PILOT")
        self.assertEqual(by_id["localization_producer"]["default_status"], "ON_DEMAND")

    def test_growth_and_thumbnail_craft_are_separate(self):
        cfg = self.load_config()
        by_id = {x["id"]: x for x in cfg["production_functions"]}
        self.assertNotEqual(
            set(by_id["audience_growth_strategist"]["owns"]),
            set(by_id["thumbnail_packaging_designer"]["owns"]),
        )
        self.assertIn("title_strategy", by_id["audience_growth_strategist"]["owns"])
        self.assertIn("typography", by_id["thumbnail_packaging_designer"]["owns"])

    def test_fact_check_and_producer_boundaries_are_explicit(self):
        cfg = self.load_config()
        rules = set(cfg["function_independence_rules"])
        for rule in {
            "research_or_writer_cannot_self_clear_material_fact_check",
            "producer_controls_schedule_resources_not_editorial_truth",
            "motion_editor_participates_before_script_lock",
            "growth_strategist_does_not_replace_thumbnail_design_review",
        }:
            self.assertIn(rule, rules)

    def test_visual_generation_brief_capability_is_composed_and_fail_closed(self):
        cfg = self.load_config()
        capability = cfg["visual_generation_brief_capability"]
        self.assertFalse(capability["permanent_role"])
        self.assertEqual(
            set(capability["composed_by"]),
            {
                "Visual Art Director / Frame Curator",
                "Thumbnail & Packaging Designer",
                "Synthesis & Alternatives Designer",
            },
        )
        self.assertEqual(capability["anti_slop_approver"], "Red Team")
        self.assertEqual(capability["executor"], "Technical Operator")
        self.assertTrue(capability["no_prompt_no_generation"])
        self.assertTrue(capability["no_anti_slop_approval_no_execution"])
        self.assertTrue(capability["tool_creative_rewrite_forbidden"])
        self.assertTrue(capability["material_deviation_returns_to_council"])
        self.assertTrue(capability["one_official_thumbnail_concept_per_episode"])
        self.assertTrue(capability["one_generation_job_per_episode_thumbnail_stage"])
        self.assertTrue(capability["one_generated_thumbnail_asset_per_episode"])
        self.assertTrue(capability["multi_panel_thumbnail_output_forbidden"])
        self.assertTrue(capability["generation_context_must_contain_only_selected_brief"])

    def test_locked_visual_production_authority_and_pilot_ladder(self):
        cfg = self.load_config()
        system = cfg["visual_production_system"]
        self.assertTrue(system["art_director_final_visual_authority_within_lock"])
        self.assertTrue(system["council_gate_review_only_after_lock"])
        self.assertFalse(system["per_frame_full_council_review_after_lock"])
        self.assertEqual(system["full_episode_requires"], "P2_PASS")
        self.assertEqual(
            system["pilot_ladder"],
            [
                "P0_REFERENCE_FRAME_LOCK",
                "P1_COHERENCE_30_45",
                "P2_PRODUCTION_60_90",
                "P3_FULL_EPISODE_8_PLUS_MINUTES",
            ],
        )
        art = next(f for f in cfg["production_functions"] if f["id"] == "visual_art_director")
        self.assertIn("final_visual_decision_within_locked_system", art["owns"])
        self.assertEqual(
            cfg["media_toolchain"]["image_generation_primary_tool"],
            "UNQUALIFIED_PENDING_TOOL_QUALIFICATION",
        )

    def test_audio_roles_are_distinct_and_active(self):
        cfg = self.load_config()
        by_id = {x["id"]: x for x in cfg["production_functions"]}
        self.assertEqual(by_id["music_sound_supervisor"]["default_status"], "ACTIVE_FOR_MEDIA_PILOT")
        self.assertEqual(by_id["dialogue_mix_engineer"]["default_status"], "ACTIVE_FOR_MEDIA_PILOT")
        self.assertNotEqual(
            set(by_id["music_sound_supervisor"]["owns"]),
            set(by_id["dialogue_mix_engineer"]["owns"]),
        )

    def test_media_toolchain_is_bounded_and_honest(self):
        cfg = self.load_config()
        self.assertFalse(cfg["live_publish_authority"])
        self.assertEqual(cfg["media_toolchain"]["platform_publishing"], "CAPABILITY_GAP")
        self.assertEqual(cfg["media_toolchain"]["video_editing"], "PARTIAL_RUNTIME_VERIFIED")
        self.assertEqual(cfg["media_toolchain"]["after_effects_motion_assembly"], "RUNTIME_VERIFIED")
        self.assertEqual(cfg["media_toolchain"]["dialogue_cleanup"], "CONNECTED_DESCRIPT_AVAILABLE")
        self.assertEqual(
            cfg["media_toolchain"]["picture_edit_finishing"],
            "PUBLIC_FINISHING_CAPABILITY_GAP",
        )
        self.assertEqual(
            cfg["media_toolchain"]["mix_mastering"],
            "PUBLIC_FINISHING_CAPABILITY_GAP",
        )

    def test_benchmark_metrics_are_required_before_scale(self):
        for metric in {
            "schedule_variance",
            "milestone_slips",
            "script_revision_rounds",
            "fact_check_defects_caught_prelock",
            "visual_story_case_rework",
            "thumbnail_variants_produced",
            "production_readiness_failures",
            "edit_rework_after_script_lock",
            "generation_brief_rework_rounds",
            "prompt_drift_defects",
        }:
            self.assertIn(metric, REQUIRED_PILOT_METRICS)

    def test_scale_is_forbidden_before_three_videos(self):
        record = {
            "videos_completed": 2,
            "metrics": self.base_metrics(),
            "hr_review_status": "KEEP",
            "scale_decision": "SCALE_CANDIDATE",
        }
        with self.assertRaises(MediaControlError):
            validate_media_scale_request(record)

    def test_three_video_pilot_requires_all_professional_metrics(self):
        record = {
            "videos_completed": 3,
            "metrics": ["production_time_per_video"],
            "hr_review_status": "KEEP",
            "scale_decision": "HOLD",
        }
        with self.assertRaises(MediaControlError):
            validate_media_pilot_record(record)

        record["metrics"] = self.base_metrics()
        self.assertTrue(validate_media_pilot_record(record))

    def test_published_pilot_requires_audience_metrics(self):
        base = {
            "videos_completed": 3,
            "metrics": self.base_metrics(),
            "hr_review_status": "KEEP",
            "scale_decision": "CONTINUE_PILOT",
        }
        with self.assertRaises(MediaControlError):
            validate_media_pilot_record(base, published=True)

        base["metrics"] += [
            "ctr",
            "first_30_second_retention",
            "average_percentage_viewed",
            "watch_time",
            "subscribers_per_video",
            "returning_viewers",
        ]
        self.assertTrue(validate_media_pilot_record(base, published=True))

    def test_valid_scale_candidate_passes_after_pilot(self):
        record = {
            "videos_completed": 3,
            "metrics": self.base_metrics(),
            "hr_review_status": "KEEP",
            "scale_decision": "SCALE_CANDIDATE",
        }
        self.assertTrue(validate_media_scale_request(record))

    def test_media_team_validator_failure_paths_are_covered(self):
        mutations = [
            lambda c: c.__setitem__("version", "broken"),
            lambda c: c.__setitem__(
                "production_functions",
                [f for f in c["production_functions"] if f["id"] != "media_producer"],
            ),
            lambda c: next(f for f in c["production_functions"] if f["id"] == "media_producer").__setitem__(
                "default_status", "ON_DEMAND"
            ),
            lambda c: next(f for f in c["production_functions"] if f["id"] == "localization_producer").__setitem__(
                "default_status", "DISABLED"
            ),
            lambda c: c.__setitem__(
                "function_independence_rules",
                [
                    rule
                    for rule in c["function_independence_rules"]
                    if rule != "research_or_writer_cannot_self_clear_material_fact_check"
                ],
            ),
            lambda c: c.pop("benchmark_artifact"),
            lambda c: c["media_toolchain"].pop("dialogue_cleanup"),
            lambda c: c["pilot"].__setitem__("required_before_scale", False),
            lambda c: c["pilot"].__setitem__("video_count", 2),
            lambda c: c.pop("visual_generation_brief_capability"),
            lambda c: c["visual_generation_brief_capability"].__setitem__("permanent_role", True),
            lambda c: c["visual_generation_brief_capability"].__setitem__("composed_by", ["Prompt Engineer"]),
            lambda c: c["visual_generation_brief_capability"].__setitem__("anti_slop_approver", "Technical Operator"),
            lambda c: c["visual_generation_brief_capability"].__setitem__("no_prompt_no_generation", False),
            lambda c: c["visual_generation_brief_capability"].__setitem__(
                "one_official_thumbnail_concept_per_episode", False
            ),
            lambda c: c["visual_generation_brief_capability"].__setitem__(
                "one_generation_job_per_episode_thumbnail_stage", False
            ),
            lambda c: c["visual_generation_brief_capability"].__setitem__(
                "one_generated_thumbnail_asset_per_episode", False
            ),
            lambda c: c["visual_generation_brief_capability"].__setitem__(
                "multi_panel_thumbnail_output_forbidden", False
            ),
            lambda c: c["visual_production_system"].__setitem__(
                "art_director_final_visual_authority_within_lock", False
            ),
            lambda c: c["visual_production_system"].__setitem__(
                "per_frame_full_council_review_after_lock", True
            ),
            lambda c: c["visual_production_system"].__setitem__("full_episode_requires", "NONE"),
        ]
        for mutate in mutations:
            cfg = self.load_config()
            mutate(cfg)
            with self.assertRaises(MediaControlError):
                validate_media_team(cfg)

    def test_pilot_record_invalid_statuses_and_missing_fields_fail_closed(self):
        base = {
            "videos_completed": 3,
            "metrics": self.base_metrics(),
            "hr_review_status": "KEEP",
            "scale_decision": "HOLD",
        }

        missing = dict(base)
        missing.pop("metrics")
        with self.assertRaises(MediaControlError):
            validate_media_pilot_record(missing)

        invalid_hr = dict(base)
        invalid_hr["hr_review_status"] = "SELF_APPROVED"
        with self.assertRaises(MediaControlError):
            validate_media_pilot_record(invalid_hr)

        invalid_scale = dict(base)
        invalid_scale["scale_decision"] = "AUTO_SCALE"
        with self.assertRaises(MediaControlError):
            validate_media_pilot_record(invalid_scale)

        with self.assertRaises(MediaControlError):
            validate_media_scale_request(base)


if __name__ == "__main__":
    unittest.main()
