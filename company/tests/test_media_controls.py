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
        self.assertEqual({x["id"] for x in cfg["production_functions"]}, REQUIRED_MEDIA_FUNCTIONS)

    def test_only_producer_is_always_active_control_plane(self):
        cfg = self.load_config()
        by_id = {x["id"]: x for x in cfg["production_functions"]}
        self.assertEqual(by_id["media_producer"]["default_status"], "CONTROL_PLANE_ALWAYS_ACTIVE")
        self.assertEqual(by_id["editorial_director"]["default_status"], "PHASE_ROUTED_CRAFT")
        self.assertEqual(by_id["independent_fact_checker"]["default_status"], "MANDATORY_CLEARANCE")
        for function_id in {
            "script_voice_director",
            "visual_art_director",
            "cinematography_shot_designer",
            "motion_picture_editor",
            "music_sound_supervisor",
            "dialogue_mix_engineer",
            "audience_growth_strategist",
            "thumbnail_packaging_designer",
        }:
            self.assertEqual(by_id[function_id]["default_status"], "PHASE_ROUTED_CRAFT")
        self.assertEqual(by_id["localization_producer"]["default_status"], "ON_DEMAND")
        self.assertEqual(by_id["human_assistance_pool"]["default_status"], "ON_DEMAND_ASSISTANCE")

    def test_three_macro_phases_are_locked(self):
        cfg = self.load_config()
        model = cfg["operating_model"]
        self.assertEqual(model["mode"], "THREE_PHASE_STUDIO_WITH_SERIAL_PRODUCTION")
        self.assertEqual(model["macro_phases"], ["writing", "pre_production", "production"])
        pipeline = cfg["master_pipeline_contract"]
        self.assertEqual(pipeline["phase_sequence"], ["writing", "pre_production", "production"])
        self.assertEqual(set(pipeline["writing_exit_requires"]), {"OWNER_TITLE_LOCK", "SCRIPT_LOCK"})
        self.assertEqual(pipeline["production_entry_requires"], "PRODUCTION_READY_LOCK")
        self.assertTrue(pipeline["phase_skip_forbidden"])

    def test_title_gate_is_owner_controlled_three_topics_two_titles_each(self):
        cfg = self.load_config()
        title = cfg["title_gate_contract"]
        self.assertEqual(title["topic_count"], 3)
        self.assertEqual(title["titles_per_topic"], 2)
        self.assertEqual(title["total_title_count"], 6)
        self.assertTrue(title["market_scan_required"])
        self.assertTrue(title["social_network_scan_required"])
        self.assertTrue(title["story_feasibility_required"])
        self.assertTrue(title["native_youtube_discovery_required"])
        self.assertTrue(title["authorized_native_fallback_allowed"])
        self.assertTrue(title["degraded_discovery_requires_hold"])
        self.assertTrue(title["story_premise_required"])
        self.assertTrue(title["story_archetype_diversity_required"])
        self.assertTrue(title["thumbnail_hypothesis_required"])
        self.assertTrue(title["red_team_click_pass_required"])
        self.assertTrue(title["owner_selection_required"])
        self.assertTrue(title["script_start_before_selection_forbidden"])
        self.assertTrue(title["automatic_post_lock_revision_forbidden"])
        self.assertTrue(title["owner_reapproval_for_revision"])

    def test_serial_production_rules_are_explicit(self):
        cfg = self.load_config()
        rules = set(cfg["operating_model"]["production_rules"])
        for rule in {
            "one_active_craft_department",
            "no_parallel_craft_departments",
            "each_department_completes_internal_stages_before_handoff",
            "one_program_per_stage",
            "program_change_only_at_stage_boundary",
            "accepted_handoff_required_before_next_department",
            "downstream_department_must_return_upstream_defects_to_source",
            "producer_coordinates_but_does_not_edit_craft_artifacts",
        }:
            self.assertIn(rule, rules)

    def test_handoff_and_stage_execution_fail_closed(self):
        cfg = self.load_config()
        stage = cfg["stage_execution_contract"]
        self.assertTrue(stage["exactly_one_primary_program"])
        self.assertTrue(stage["simultaneous_secondary_craft_program_forbidden"])
        self.assertTrue(stage["program_switch_requires_new_stage"])
        self.assertTrue(stage["checkpoint_before_stage_exit"])
        self.assertTrue(stage["output_verification_required"])

        handoff = cfg["handoff_contract"]
        self.assertTrue(handoff["acceptance_required_before_next_department"])
        self.assertTrue(handoff["downstream_direct_repair_forbidden"])
        self.assertEqual(handoff["rejection_action"], "RETURN_TICKET_TO_SOURCE_DEPARTMENT")

    def test_new_pipeline_metrics_are_required_for_pilot(self):
        for metric in {
            "topic_candidate_count",
            "title_variant_count",
            "owner_title_selection_rounds",
            "title_revision_requests",
            "story_premise_rejection_count",
            "degraded_discovery_hold_count",
            "thumbnail_hypothesis_count",
            "red_team_click_rejection_count",
            "owner_w1_rejection_count",
            "writing_cycle_time",
            "preproduction_cycle_time",
            "production_cycle_time",
            "department_cycle_time",
            "stage_cycle_time",
            "handoff_rejection_count",
            "return_ticket_count",
            "program_switch_violation_count",
            "parallel_department_violation_count",
        }:
            self.assertIn(metric, REQUIRED_PILOT_METRICS)

    def test_human_assistance_remains_bounded(self):
        cfg = self.load_config()
        assistance = cfg["human_assistance"]
        self.assertTrue(assistance["enabled"])
        self.assertEqual(assistance["mode"], "ON_DEMAND_BOUNDED_ASSISTANCE")
        self.assertEqual(assistance["coordinator"], "media_producer")
        self.assertIn("human_helper_does_not_gain_publish_authority", assistance["constraints"])
        self.assertIn("verify_human_return_against_acceptance_criteria", assistance["resume_policy"])

    def test_validator_fails_closed_on_pipeline_drift(self):
        mutations = [
            lambda c: c.__setitem__("version", "bad"),
            lambda c: next(f for f in c["production_functions"] if f["id"] == "media_producer").__setitem__(
                "default_status", "PHASE_ROUTED_CRAFT"
            ),
            lambda c: c["operating_model"].__setitem__("mode", "PARALLEL_STUDIO"),
            lambda c: c["operating_model"].__setitem__("macro_phases", ["production"]),
            lambda c: c["operating_model"].__setitem__("production_rules", []),
            lambda c: c["title_gate_contract"].__setitem__("topic_count", 4),
            lambda c: c["title_gate_contract"].__setitem__("owner_selection_required", False),
            lambda c: c["title_gate_contract"].__setitem__("native_youtube_discovery_required", False),
            lambda c: c["title_gate_contract"].__setitem__("story_premise_required", False),
            lambda c: c["title_gate_contract"].__setitem__("thumbnail_hypothesis_required", False),
            lambda c: c["master_pipeline_contract"].__setitem__("production_entry_requires", "NONE"),
            lambda c: c["stage_execution_contract"].__setitem__("exactly_one_primary_program", False),
            lambda c: c["handoff_contract"].__setitem__("downstream_direct_repair_forbidden", False),
            lambda c: c["human_assistance"].__setitem__("enabled", False),
            lambda c: c["execution_recovery"].__setitem__("unknown_is_never_success", False),
        ]
        for mutate in mutations:
            cfg = self.load_config()
            mutate(cfg)
            with self.assertRaises(MediaControlError):
                validate_media_team(cfg)

    def test_scale_is_forbidden_before_three_videos(self):
        record = {
            "videos_completed": 2,
            "metrics": self.base_metrics(),
            "hr_review_status": "KEEP",
            "scale_decision": "SCALE_CANDIDATE",
        }
        with self.assertRaises(MediaControlError):
            validate_media_scale_request(record)

    def test_valid_scale_candidate_passes_after_pilot(self):
        record = {
            "videos_completed": 3,
            "metrics": self.base_metrics(),
            "hr_review_status": "KEEP",
            "scale_decision": "SCALE_CANDIDATE",
        }
        self.assertTrue(validate_media_pilot_record(record))
        self.assertTrue(validate_media_scale_request(record))

    def test_media_team_validator_legacy_and_new_failure_paths(self):
        mutations = [
            lambda c: c.__setitem__(
                "production_functions",
                [f for f in c["production_functions"] if f["id"] != "cinematography_shot_designer"],
            ),
            lambda c: next(f for f in c["production_functions"] if f["id"] == "independent_fact_checker").__setitem__(
                "default_status", "PHASE_ROUTED_CRAFT"
            ),
            lambda c: next(f for f in c["production_functions"] if f["id"] == "motion_picture_editor").__setitem__(
                "default_status", "CONTROL_PLANE_ALWAYS_ACTIVE"
            ),
            lambda c: next(f for f in c["production_functions"] if f["id"] == "localization_producer").__setitem__(
                "default_status", "DISABLED"
            ),
            lambda c: next(f for f in c["production_functions"] if f["id"] == "human_assistance_pool").__setitem__(
                "default_status", "CONTROL_PLANE_ALWAYS_ACTIVE"
            ),
            lambda c: c["operating_model"].__setitem__("control_plane_functions", []),
            lambda c: c["operating_model"].__setitem__("mandatory_clearance_functions", []),
            lambda c: c["operating_model"].__setitem__("phase_routed_craft_functions", []),
            lambda c: c["operating_model"].__setitem__("on_demand_functions", []),
            lambda c: c["operating_model"].__setitem__("writing_rules", []),
            lambda c: c["operating_model"].__setitem__("forbidden_defaults", []),
            lambda c: c["master_pipeline_contract"].__setitem__("writing_exit_requires", []),
            lambda c: c["master_pipeline_contract"].__setitem__("preproduction_entry_requires", "NONE"),
            lambda c: c["master_pipeline_contract"].__setitem__("preproduction_exit_requires", "NONE"),
            lambda c: c["master_pipeline_contract"].__setitem__("phase_skip_forbidden", False),
            lambda c: c["stage_execution_contract"].__setitem__(
                "simultaneous_secondary_craft_program_forbidden", False
            ),
            lambda c: c["stage_execution_contract"].__setitem__("program_switch_requires_new_stage", False),
            lambda c: c["stage_execution_contract"].__setitem__("checkpoint_before_stage_exit", False),
            lambda c: c["stage_execution_contract"].__setitem__("output_verification_required", False),
            lambda c: c["handoff_contract"].__setitem__("acceptance_required_before_next_department", False),
            lambda c: c["handoff_contract"].__setitem__("rejection_action", "DOWNSTREAM_FIXES_IT"),
            lambda c: c.__setitem__(
                "function_independence_rules",
                [
                    rule
                    for rule in c["function_independence_rules"]
                    if rule != "script_cannot_start_before_owner_title_lock"
                ],
            ),
            lambda c: c["human_assistance"].__setitem__("mode", "ALWAYS_ACTIVE"),
            lambda c: c["human_assistance"].__setitem__("coordinator", "editorial_director"),
            lambda c: c["human_assistance"].__setitem__("trigger_conditions", []),
            lambda c: c["human_assistance"].__setitem__("request_packet_required_fields", []),
            lambda c: c["human_assistance"].__setitem__("constraints", []),
            lambda c: c["human_assistance"].__setitem__("resume_policy", []),
            lambda c: c["human_assistance"]["recurring_gap_policy"].__setitem__("repeated_same_gap_threshold", 0),
            lambda c: c["human_assistance"]["recurring_gap_policy"].__setitem__("action", "IGNORE"),
            lambda c: c.pop("benchmark_artifact"),
            lambda c: c["media_toolchain"].pop("dialogue_cleanup"),
            lambda c: c["pilot"].__setitem__("required_before_scale", False),
            lambda c: c["pilot"].__setitem__("video_count", 2),
        ]
        for mutate in mutations:
            cfg = self.load_config()
            mutate(cfg)
            with self.assertRaises(MediaControlError):
                validate_media_team(cfg)

    def test_every_title_gate_boolean_is_enforced(self):
        for key in {
            "market_scan_required",
            "social_network_scan_required",
            "story_feasibility_required",
            "owner_selection_required",
            "script_start_before_selection_forbidden",
            "automatic_post_lock_revision_forbidden",
            "owner_reapproval_for_revision",
        }:
            cfg = self.load_config()
            cfg["title_gate_contract"][key] = False
            with self.assertRaises(MediaControlError):
                validate_media_team(cfg)

    def test_assistance_and_pilot_record_failure_paths(self):
        cfg = self.load_config()
        cfg["human_assistance"]["enabled"] = False
        with self.assertRaises(MediaControlError):
            validate_media_team(cfg)

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

        published = dict(base)
        with self.assertRaises(MediaControlError):
            validate_media_pilot_record(published, published=True)

        with self.assertRaises(MediaControlError):
            validate_media_scale_request(base)


if __name__ == "__main__":
    unittest.main()
