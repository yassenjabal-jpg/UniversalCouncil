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

    def test_studio_uses_small_core_and_routed_craft_capabilities(self):
        cfg = self.load_config()
        by_id = {x["id"]: x for x in cfg["production_functions"]}
        self.assertEqual(by_id["media_producer"]["default_status"], "CORE_ALWAYS_ACTIVE")
        self.assertEqual(by_id["editorial_director"]["default_status"], "CORE_ALWAYS_ACTIVE")
        self.assertEqual(by_id["independent_fact_checker"]["default_status"], "MANDATORY_CLEARANCE")
        for function_id in {
            "script_voice_director",
            "visual_art_director",
            "cinematography_shot_designer",
            "audience_growth_strategist",
            "thumbnail_packaging_designer",
            "motion_picture_editor",
            "music_sound_supervisor",
            "dialogue_mix_engineer",
        }:
            self.assertEqual(by_id[function_id]["default_status"], "ROUTED_CRAFT_CAPABILITY")
        self.assertEqual(by_id["localization_producer"]["default_status"], "ON_DEMAND")
        self.assertEqual(cfg["operating_model"]["mode"], "SMALL_CORE_ROUTED_CRAFT_CAPABILITIES")
        self.assertTrue(cfg["operating_model"]["parallelize_when_safe"])
        self.assertTrue(cfg["operating_model"]["single_synthesis_per_gate"])

    def test_growth_and_thumbnail_craft_are_separate(self):
        cfg = self.load_config()
        by_id = {x["id"]: x for x in cfg["production_functions"]}
        self.assertNotEqual(
            set(by_id["audience_growth_strategist"]["owns"]),
            set(by_id["thumbnail_packaging_designer"]["owns"]),
        )
        self.assertIn("title_strategy", by_id["audience_growth_strategist"]["owns"])
        self.assertIn("typography", by_id["thumbnail_packaging_designer"]["owns"])

    def test_cinematography_is_explicit_and_separate_from_editing(self):
        cfg = self.load_config()
        by_id = {x["id"]: x for x in cfg["production_functions"]}
        cine = by_id["cinematography_shot_designer"]
        motion = by_id["motion_picture_editor"]
        self.assertIn("framing_and_shot_size", cine["owns"])
        self.assertIn("camera_motion_intent", cine["owns"])
        self.assertIn("shot_to_shot_continuity", cine["owns"])
        self.assertNotEqual(set(cine["owns"]), set(motion["owns"]))
        self.assertEqual(cfg["media_toolchain"]["cinematography_shot_design"], "PROCESS_DEFINED_SPECIALIZED_TOOL_REQUIRED")

    def test_fact_check_and_producer_boundaries_are_explicit(self):
        cfg = self.load_config()
        rules = set(cfg["function_independence_rules"])
        for rule in {
            "research_or_writer_cannot_self_clear_material_fact_check",
            "producer_controls_schedule_resources_not_editorial_truth",
            "motion_editor_participates_before_script_lock",
            "growth_strategist_does_not_replace_thumbnail_design_review",
            "cinematography_defines_shot_language_but_does_not_self_approve_picture_lock",
            "routed_craft_function_is_invoked_by_stage_not_kept_permanently_active",
            "unknown_execution_state_cannot_be_promoted_to_success",
        }:
            self.assertIn(rule, rules)

    def test_audio_roles_are_distinct_and_stage_routed(self):
        cfg = self.load_config()
        by_id = {x["id"]: x for x in cfg["production_functions"]}
        self.assertEqual(by_id["music_sound_supervisor"]["default_status"], "ROUTED_CRAFT_CAPABILITY")
        self.assertEqual(by_id["dialogue_mix_engineer"]["default_status"], "ROUTED_CRAFT_CAPABILITY")
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
            "shot_design_rework",
            "camera_continuity_defects",
            "studio_coordination_overhead_minutes",
            "unnecessary_function_invocations",
            "handoff_recovery_count",
            "unknown_execution_events",
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
                [f for f in c["production_functions"] if f["id"] != "cinematography_shot_designer"],
            ),
            lambda c: next(f for f in c["production_functions"] if f["id"] == "media_producer").__setitem__(
                "default_status", "ROUTED_CRAFT_CAPABILITY"
            ),
            lambda c: next(f for f in c["production_functions"] if f["id"] == "motion_picture_editor").__setitem__(
                "default_status", "CORE_ALWAYS_ACTIVE"
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
            lambda c: c["operating_model"].__setitem__("mode", "EVERYONE_ALWAYS_ACTIVE"),
            lambda c: c["operating_model"].__setitem__("forbidden_defaults", []),
            lambda c: c["media_toolchain"].pop("dialogue_cleanup"),
            lambda c: c["execution_recovery"].__setitem__("unknown_is_never_success", False),
            lambda c: c["pilot"].__setitem__("required_before_scale", False),
            lambda c: c["pilot"].__setitem__("video_count", 2),
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
