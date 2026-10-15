import copy
import json
import unittest
from pathlib import Path

from company.runtime.channel_operating_system import (
    ChannelOperatingSystemError,
    REQUIRED_AUDIO_STEMS,
    REQUIRED_GATES,
    REQUIRED_PRODUCTION_DEPARTMENTS,
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

    def test_master_pipeline_is_writing_preproduction_production(self):
        self.assertEqual(CONFIG["master_pipeline"]["phases"], ["writing", "pre_production", "production"])
        self.assertTrue(CONFIG["master_pipeline"]["phase_order_locked"])
        self.assertEqual(CONFIG["workflow"], REQUIRED_WORKFLOW)

    def test_title_gate_requires_three_topics_two_titles_each_and_owner_selection(self):
        title = CONFIG["writing_phase"]["title_system"]
        self.assertEqual(title["required_topic_count"], 3)
        self.assertEqual(title["required_titles_per_topic"], 2)
        self.assertTrue(title["owner_selection_required"])
        self.assertTrue(title["owner_is_only_final_title_authority"])
        self.assertTrue(title["script_start_before_owner_selection_forbidden"])
        self.assertTrue(title["post_lock_revision"]["owner_reapproval_required"])
        self.assertIn("eight_minute_story_feasibility", title["topic_required_fields"])
        self.assertIn("viewer_promise", title["title_variant_required_fields"])

    def test_writing_has_title_then_script_sections(self):
        sections = CONFIG["writing_phase"]["sections"]
        self.assertEqual([s["id"] for s in sections], ["W1_title_development", "W2_script_development"])
        self.assertEqual(sections[1]["entry_requirement"], "OWNER_TITLE_LOCK")
        self.assertEqual(CONFIG["writing_phase"]["exit_gate"], "SCRIPT_LOCK")
        self.assertEqual(CONFIG["script_development"]["required_passes"], REQUIRED_SCRIPT_PASSES)

    def test_preproduction_is_between_script_and_production(self):
        pre = CONFIG["pre_production_phase"]
        self.assertEqual(pre["entry_requirement"], "SCRIPT_LOCK")
        self.assertEqual(pre["exit_gate"], "PRODUCTION_READY_LOCK")
        ids = [s["id"] for s in pre["stages"]]
        self.assertLess(ids.index("shot_design"), ids.index("animatic"))
        self.assertLess(ids.index("sonic_concept"), ids.index("animatic"))
        self.assertLess(ids.index("title_promise_alignment"), ids.index("animatic"))
        self.assertEqual(ids[-1], "production_readiness_review")

    def test_preproduction_can_return_but_not_silently_change_title(self):
        rules = set(CONFIG["pre_production_phase"]["stage_rules"])
        self.assertIn("material_script_problem_returns_to_writing_with_return_ticket", rules)
        self.assertIn(
            "title_mismatch_creates_owner_title_revision_request_not_automatic_title_change",
            rules,
        )

    def test_production_line_is_serial(self):
        production = CONFIG["production_phase"]
        self.assertEqual(production["mode"], "SERIAL_PRODUCTION_LINE_WITH_FEEDBACK_GATES")
        self.assertTrue(production["one_active_department"])
        self.assertFalse(production["parallel_craft_departments"])
        self.assertTrue(production["one_program_per_stage"])
        self.assertTrue(production["next_department_requires_accepted_handoff"])
        self.assertTrue(production["downstream_direct_upstream_edit_forbidden"])
        self.assertEqual(
            [d["id"] for d in production["departments"]],
            REQUIRED_PRODUCTION_DEPARTMENTS,
        )

    def test_every_stage_has_one_named_program(self):
        stages = []
        for section in CONFIG["writing_phase"]["sections"]:
            stages.extend(section["stages"])
        stages.extend(CONFIG["pre_production_phase"]["stages"])
        for department in CONFIG["production_phase"]["departments"]:
            stages.extend(department["stages"])
        self.assertTrue(stages)
        for stage in stages:
            self.assertIsInstance(stage["program"], str)
            self.assertTrue(stage["program"].strip())

    def test_feedback_gate_returns_defects_to_source(self):
        handoff = CONFIG["handoff_contract"]
        self.assertTrue(handoff["acceptance_required_before_next_department"])
        self.assertTrue(handoff["downstream_direct_repair_forbidden"])
        self.assertEqual(handoff["rejection_action"], "RETURN_TICKET_TO_SOURCE_DEPARTMENT")
        self.assertIn("do_not_change", handoff["return_ticket_required_fields"])

    def test_production_readiness_fails_closed(self):
        gate = CONFIG["production_readiness"]
        self.assertTrue(gate["required"])
        self.assertEqual(gate["fail_action"], "HOLD_PRODUCTION")
        for check in {
            "owner_title_locked",
            "script_locked",
            "independent_fact_check_passed",
            "shot_design_approved",
            "sonic_concept_complete",
            "title_promise_alignment_passed",
            "animatic_locked",
        }:
            self.assertIn(check, gate["required_checks"])

    def test_audio_is_split_between_preproduction_and_post_picture_lock(self):
        audio = CONFIG["audio_system"]
        self.assertTrue(audio["sonic_concept_required_in_preproduction"])
        self.assertTrue(audio["final_sound_design_after_picture_lock"])
        self.assertTrue(audio["picture_lock_required_before_final_sound_design"])
        self.assertEqual(set(audio["mandatory_stems"]), REQUIRED_AUDIO_STEMS)

    def test_packaging_strategy_is_early_but_execution_is_late(self):
        packaging = CONFIG["packaging_system"]
        self.assertIn("three_distinct_topics_with_two_titles_each", packaging["stage_a_before_script"])
        self.assertIn("owner_title_selection", packaging["stage_a_before_script"])
        self.assertTrue(packaging["title_changes_after_owner_lock_require_owner_reapproval"])
        self.assertGreaterEqual(len(packaging["stage_b_after_picture_lock"]), 4)

    def test_quality_gates_are_exact(self):
        self.assertEqual(set(CONFIG["quality_gates"]), REQUIRED_GATES)

    def test_required_roles_remain_present(self):
        self.assertTrue(REQUIRED_PRODUCTION_ROLES.issubset(set(CONFIG["roles"])))

    def test_human_assistance_remains_bounded(self):
        assistance = CONFIG["human_assistance_lane"]
        self.assertTrue(assistance["enabled"])
        self.assertTrue(assistance["available_at_any_stage"])
        self.assertIn("do not transfer publish authority", assistance["rules"])
        self.assertIn("verify human output before resuming automated production", assistance["rules"])

    def test_validator_fails_closed_on_core_drift(self):
        mutations = [
            lambda c: c.__setitem__("version", "bad"),
            lambda c: c["master_pipeline"].__setitem__("phases", ["production"]),
            lambda c: c["writing_phase"]["title_system"].__setitem__("required_topic_count", 4),
            lambda c: c["writing_phase"]["title_system"].__setitem__("owner_selection_required", False),
            lambda c: c["script_development"].__setitem__("required_passes", ["one"]),
            lambda c: c["pre_production_phase"].__setitem__("entry_requirement", "NONE"),
            lambda c: c["production_phase"].__setitem__("parallel_craft_departments", True),
            lambda c: c["production_phase"].__setitem__("one_program_per_stage", False),
            lambda c: c["handoff_contract"].__setitem__("downstream_direct_repair_forbidden", False),
            lambda c: c["production_readiness"].__setitem__("fail_action", "CONTINUE"),
            lambda c: c["audio_system"].__setitem__("sonic_concept_required_in_preproduction", False),
            lambda c: c["studio_routing_model"].__setitem__("mode", "EVERYONE_PARALLEL"),
            lambda c: c["human_assistance_lane"].__setitem__("enabled", False),
        ]
        for mutate in mutations:
            cfg = copy.deepcopy(CONFIG)
            mutate(cfg)
            with self.assertRaises(ChannelOperatingSystemError):
                validate_config(cfg)


if __name__ == "__main__":
    unittest.main()
