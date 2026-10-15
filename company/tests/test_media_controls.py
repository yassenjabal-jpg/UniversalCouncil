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

    def test_title_gate_is_owner_controlled_and_exactly_three(self):
        cfg = self.load_config()
        title = cfg["title_gate_contract"]
        self.assertEqual(title["candidate_count"], 3)
        self.assertTrue(title["market_scan_required"])
        self.assertTrue(title["social_network_scan_required"])
        self.assertTrue(title["story_feasibility_required"])
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
            "title_candidate_count",
            "owner_title_selection_rounds",
            "title_revision_requests",
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
            lambda c: c["title_gate_contract"].__setitem__("candidate_count", 4),
            lambda c: c["title_gate_contract"].__setitem__("owner_selection_required", False),
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


if __name__ == "__main__":
    unittest.main()
