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

    def test_rebuilt_visual_identity_contract(self):
        self.assertEqual(CONFIG["version"], "1.6")
        self.assertEqual(CONFIG["visual_system"], "Modern Editorial Surrealism")
        identity = CONFIG["visual_identity"]
        self.assertEqual(identity["version"], "2.1-candidate")
        self.assertEqual(
            identity["bible"],
            "docs/operations/media/MODERN_EDITORIAL_SURREALISM_VISUAL_BIBLE.md",
        )
        self.assertEqual(identity["primary_reference"], "user-provided 1000061003.mp4")
        self.assertTrue(identity["episode_accent_required"])
        self.assertTrue(identity["architecture_is_topic_dependent_only"])
        self.assertTrue(identity["classical_art_is_optional_not_mandatory"])
        self.assertEqual(identity["thumbnail_hypotheses_per_episode"], 1)
        self.assertEqual(identity["generated_thumbnail_assets_per_episode"], 1)
        self.assertTrue(identity["single_thumbnail_lock"])
        self.assertTrue(identity["multi_panel_thumbnail_output_forbidden"])
        self.assertEqual(identity["hero_objects_per_key_frame"], 1)
        self.assertTrue(identity["synthetic_documentary_evidence_forbidden"])
        self.assertEqual(CONFIG["frame_bible"]["composition_rules"]["negative_space_percent"], "35-60")

    def test_visual_generation_brief_is_mandatory_and_fail_closed(self):
        brief = CONFIG["visual_generation_brief_system"]
        self.assertEqual(brief["status"], "REQUIRED_FOR_ANY_GENERATED_VISUAL")
        self.assertFalse("Prompt Engineer" in brief["composed_by"])
        self.assertEqual(
            set(brief["composed_by"]),
            {
                "Visual Art Director / Frame Curator",
                "Thumbnail & Packaging Designer",
                "Synthesis & Alternatives Designer",
            },
        )
        self.assertEqual(brief["approval_required_from"], ["Red Team / Anti-Slop"])
        self.assertEqual(brief["executor"], "Technical Operator")
        self.assertEqual(brief["approval_state_required"], "APPROVED_BY_ANTI_SLOP")
        self.assertIn("NO_PROMPT_NO_GENERATION", brief["execution_rules"])
        self.assertIn("NO_ANTI_SLOP_APPROVAL_NO_EXECUTION", brief["execution_rules"])
        self.assertIn("TOOL_MUST_NOT_CREATIVELY_REWRITE_APPROVED_BRIEF", brief["execution_rules"])
        self.assertIn("MATERIAL_DEVIATION_RETURNS_TO_COUNCIL", brief["execution_rules"])
        self.assertEqual(brief["official_thumbnail_concepts_per_episode"], 1)
        self.assertEqual(brief["generated_thumbnail_assets_per_episode"], 1)
        self.assertEqual(brief["generation_jobs_per_episode_thumbnail_stage"], 1)
        self.assertTrue(brief["context_isolation_required"])
        self.assertTrue(brief["multi_panel_output_forbidden"])
        self.assertIn("visual_generation_briefs_approved", CONFIG["production_readiness"]["required_checks"])
        self.assertIn("G6A Visual Generation Brief + Anti-Slop Approval", CONFIG["quality_gates"])

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

    def test_locked_production_system_and_pilot_ladder(self):
        system = CONFIG["production_system"]
        self.assertEqual(
            system["governing_principle"],
            "COUNCIL_DESIGNS_SYSTEM_ART_DIRECTOR_LOCKS_OPERATORS_PRODUCE_COUNCIL_REVIEWS_GATES",
        )
        lock = system["visual_system_lock"]
        self.assertTrue(lock["required"])
        self.assertGreaterEqual(lock["reference_frame_count_min"], 4)
        self.assertLessEqual(lock["reference_frame_count_max"], 6)
        self.assertTrue(lock["production_kit_required"])
        self.assertEqual(lock["lock_authority"], "Visual Art Director / Frame Curator")

        authority = system["authority_model"]
        self.assertEqual(authority["council_after_lock"], "SYSTEM_AND_GATE_REVIEW_ONLY")
        self.assertEqual(
            authority["visual_art_director"],
            "FINAL_VISUAL_DECISION_WITHIN_LOCKED_SYSTEM",
        )
        self.assertFalse(authority["per_frame_full_council_review_after_lock"])

        qualification = system["tool_qualification"]
        self.assertTrue(qualification["required_before_visual_system_lock"])
        self.assertEqual(qualification["comparison_contract"], "SAME_FRAME_SAME_BRIEF")
        self.assertTrue(qualification["remaining_credits_must_not_select_primary_tool"])
        self.assertEqual(sum(qualification["score_weights"].values()), 100)
        self.assertTrue(qualification["qualification_passed"])
        self.assertEqual(qualification["primary_generator_status"], "QUALIFIED_PRIMARY")
        self.assertEqual(qualification["backup_generator_status"], "QUALIFIED_BACKUP")
        self.assertEqual(qualification["primary_generator"], "runway:nano-banana-2-lite")
        self.assertEqual(qualification["backup_generator"], "runway:nano-banana-pro")
        self.assertGreater(qualification["primary_score"], qualification["backup_score"])
        self.assertTrue(qualification["qualification_artifact"])

        ladder = {stage["id"]: stage for stage in system["pilot_ladder"]}
        self.assertEqual(ladder["P1_COHERENCE_30_45"]["duration_seconds_min"], 30)
        self.assertEqual(ladder["P1_COHERENCE_30_45"]["duration_seconds_max"], 45)
        self.assertEqual(ladder["P2_PRODUCTION_60_90"]["duration_seconds_min"], 60)
        self.assertEqual(ladder["P2_PRODUCTION_60_90"]["duration_seconds_max"], 90)
        self.assertEqual(ladder["P3_FULL_EPISODE_8_PLUS_MINUTES"]["duration_seconds_min"], 480)
        self.assertEqual(system["full_length_episode_before_p2_pass"], "BLOCK")

    def test_production_system_fail_closed_paths(self):
        mutations = [
            lambda c: c["production_system"].__setitem__("version", "broken"),
            lambda c: c["production_system"].__setitem__("governing_principle", "committee_per_frame"),
            lambda c: c["production_system"]["visual_system_lock"].__setitem__("required", False),
            lambda c: c["production_system"]["visual_system_lock"].__setitem__("reference_frame_count_min", 3),
            lambda c: c["production_system"]["visual_system_lock"].__setitem__("reference_frame_count_max", 7),
            lambda c: c["production_system"]["visual_system_lock"].__setitem__("production_kit_required", False),
            lambda c: c["production_system"]["visual_system_lock"].__setitem__("lock_authority", "Council"),
            lambda c: c["production_system"]["visual_system_lock"].__setitem__("red_team_blocker", False),
            lambda c: c["production_system"]["authority_model"].__setitem__("council_after_lock", "PER_FRAME"),
            lambda c: c["production_system"]["authority_model"].__setitem__("visual_art_director", "ADVISORY"),
            lambda c: c["production_system"]["authority_model"].__setitem__(
                "technical_operator", "CREATIVE_REWRITE_ALLOWED"
            ),
            lambda c: c["production_system"]["authority_model"].__setitem__(
                "per_frame_full_council_review_after_lock", True
            ),
            lambda c: c["production_system"]["tool_qualification"].__setitem__(
                "required_before_visual_system_lock", False
            ),
            lambda c: c["production_system"]["tool_qualification"].__setitem__(
                "comparison_contract", "DIFFERENT_PROMPTS"
            ),
            lambda c: c["production_system"]["tool_qualification"].__setitem__("minimum_viable_candidates", 1),
            lambda c: c["production_system"]["tool_qualification"]["score_weights"].__setitem__("cost", 6),
            lambda c: (
                c["production_system"]["tool_qualification"]["score_weights"].__setitem__("prompt_fidelity", 10),
                c["production_system"]["tool_qualification"]["score_weights"].__setitem__("style_consistency", 10),
                c["production_system"]["tool_qualification"]["score_weights"].__setitem__("cost", 35),
            ),
            lambda c: c["production_system"]["tool_qualification"].__setitem__(
                "remaining_credits_must_not_select_primary_tool", False
            ),
            lambda c: c["production_system"]["tool_qualification"].__setitem__("qualification_passed", False),
            lambda c: c["production_system"]["tool_qualification"].__setitem__(
                "primary_generator_status", "UNQUALIFIED"
            ),
            lambda c: c["production_system"]["tool_qualification"].__setitem__(
                "backup_generator_status", "UNQUALIFIED"
            ),
            lambda c: c["production_system"].__setitem__("pilot_ladder", c["production_system"]["pilot_ladder"][:-1]),
            lambda c: c["production_system"]["pilot_ladder"][1].__setitem__("duration_seconds_min", 20),
            lambda c: c["production_system"]["pilot_ladder"][2].__setitem__("duration_seconds_max", 120),
            lambda c: c["production_system"]["pilot_ladder"][3].__setitem__("duration_seconds_min", 300),
            lambda c: c["production_system"].__setitem__("full_length_episode_before_p2_pass", "ALLOW"),
            lambda c: c["production_system"].__setitem__("per_frame_council_review_after_lock", "ALLOWED"),
            lambda c: c["visual_identity"].__setitem__("generated_thumbnail_assets_per_episode", 2),
            lambda c: c["visual_identity"].__setitem__("single_thumbnail_lock", False),
            lambda c: c["visual_identity"].__setitem__("multi_panel_thumbnail_output_forbidden", False),
            lambda c: c["visual_generation_brief_system"].__setitem__(
                "only_selected_brief_may_enter_generation_context", False
            ),
            lambda c: c["packaging_system"].__setitem__(
                "generated_visual_rule",
                "no generated thumbnail asset may be executed before an approved Visual Generation Brief",
            ),
        ]
        for mutate in mutations:
            cfg = copy.deepcopy(CONFIG)
            mutate(cfg)
            with self.assertRaises(ChannelOperatingSystemError):
                validate_config(cfg)

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
            lambda c: c["visual_identity"].__setitem__("version", "1.0"),
            lambda c: c["visual_identity"].__setitem__("bible", "wrong.md"),
            lambda c: c["visual_identity"].__setitem__("primary_reference", "other.mp4"),
            lambda c: c["visual_identity"].__setitem__("reference_authority", "SECONDARY"),
            lambda c: c["visual_identity"].__setitem__("core_principles", []),
            lambda c: c["visual_identity"].__setitem__("episode_accent_required", False),
            lambda c: c["visual_identity"].__setitem__("architecture_is_topic_dependent_only", False),
            lambda c: c["visual_identity"].__setitem__("classical_art_is_optional_not_mandatory", False),
            lambda c: c["visual_identity"].__setitem__("thumbnail_hypotheses_per_episode", 2),
            lambda c: c["visual_identity"].__setitem__("hero_objects_per_key_frame", 2),
            lambda c: c["visual_identity"].__setitem__("synthetic_documentary_evidence_forbidden", False),
            lambda c: c.pop("visual_generation_brief_system"),
            lambda c: c["visual_generation_brief_system"].__setitem__("status", "OPTIONAL"),
            lambda c: c["visual_generation_brief_system"].__setitem__("composed_by", ["Prompt Engineer"]),
            lambda c: c["visual_generation_brief_system"].__setitem__("approval_required_from", []),
            lambda c: c["visual_generation_brief_system"].__setitem__("executor", "Image Tool"),
            lambda c: c["visual_generation_brief_system"].__setitem__("required_fields", []),
            lambda c: c["visual_generation_brief_system"].__setitem__("execution_rules", []),
            lambda c: c["visual_generation_brief_system"].__setitem__("approval_state_required", "AUTO"),
            lambda c: c["visual_generation_brief_system"].__setitem__("allowed_thumbnail_image_languages", ["same"]),
            lambda c: c["visual_generation_brief_system"].__setitem__("official_thumbnail_concepts_per_episode", 2),
            lambda c: c["visual_generation_brief_system"].__setitem__("generated_thumbnail_assets_per_episode", 2),
            lambda c: c["visual_generation_brief_system"].__setitem__("generation_jobs_per_episode_thumbnail_stage", 2),
            lambda c: c["visual_generation_brief_system"].__setitem__("single_asset_only", False),
            lambda c: c["visual_generation_brief_system"].__setitem__("multi_panel_output_forbidden", False),
            lambda c: c["visual_generation_brief_system"].__setitem__("context_isolation_required", False),
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
            lambda c: c["packaging_system"].__setitem__("generated_visual_rule", "generate freely"),
            lambda c: c["packaging_system"].__setitem__("thumbnail_designer_independent_craft_function", False),
            lambda c: c["production_system"].__setitem__("full_length_episode_before_p2_pass", "ALLOW"),
            lambda c: c["production_system"]["authority_model"].__setitem__(
                "per_frame_full_council_review_after_lock", True
            ),
            lambda c: c["production_system"]["tool_qualification"].__setitem__(
                "remaining_credits_must_not_select_primary_tool", False
            ),
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

    def test_validator_failure_paths_are_explicitly_covered(self):
        mutations = [
            lambda c: c["benchmark_profile"].__setitem__("name", "wrong"),
            lambda c: c["portfolio_balance"].__setitem__("max_same_family_in_window", 3),
            lambda c: c["portfolio_balance"].__setitem__("minimum_distinct_families_in_initial_window", 3),
            lambda c: c["portfolio_balance"].__setitem__("relax_only_after_first_party_audience_evidence", False),
            lambda c: c["trend_radar"].__setitem__("evergreen_reframe_required", False),
            lambda c: c["topic_scoring"]["fields"].__setitem__("cross_platform_velocity", 14),
            lambda c: c["topic_scoring"]["gates"].__setitem__("minimum_total", 50),
            lambda c: c["topic_scoring"]["gates"].__setitem__("require_one_sentence_question", False),
            lambda c: c["topic_scoring"]["gates"].__setitem__(
                "reject_if_only_trending_without_durable_question", False
            ),
            lambda c: c["research_system"].__setitem__("visual_source_rights_sheet_required", False),
            lambda c: c["research_system"].__setitem__("expert_consultation_required_when", []),
            lambda c: c["visual_story_case"].__setitem__("must_precede_script_lock", False),
            lambda c: c["visual_story_case"].__setitem__("fail_action", "IGNORE"),
            lambda c: c["preproduction_craft_review"].__setitem__("must_precede_script_lock", False),
            lambda c: c["script_development"].__setitem__("visual_draft_requires_editor_review", False),
            lambda c: c["production_readiness"].__setitem__("fail_action", "CONTINUE"),
            lambda c: c["packaging_system"].__setitem__("stage_a_before_script", []),
            lambda c: c["packaging_system"].__setitem__("stage_b_after_rough_cut", []),
            lambda c: c["frame_bible"].__setitem__(
                "canonical_frame_types", c["frame_bible"]["canonical_frame_types"][:-1]
            ),
            lambda c: c["frame_bible"]["composition_rules"].__setitem__("editable_language_layers", False),
            lambda c: c["transition_system"].__setitem__("canonical", ["cut"]),
            lambda c: c["transition_system"].__setitem__("forbidden_default", []),
            lambda c: c["audio_system"].__setitem__("spotting_required_before_reference_frame_lock", False),
            lambda c: c["audio_system"].__setitem__("picture_lock_required_before_final_sound_design", False),
            lambda c: c["audio_system"].__setitem__("post_picture_lock_timing_change_requires_audio_reconform", False),
            lambda c: c["audio_system"].__setitem__("music_states", ["M0"]),
            lambda c: c["audio_system"].__setitem__("cue_sheet_required_fields", ["cue_id"]),
            lambda c: c["audio_system"].__setitem__("av_beat_map_required_fields", ["beat_id"]),
            lambda c: c["audio_system"]["mix_targets_internal_not_platform_requirements"].__setitem__(
                "program_integrated_lufs_target", "-8 LUFS"
            ),
            lambda c: c["audio_system"].__setitem__("anti_patterns", []),
            lambda c: c["anti_slop_gate"].__setitem__("checks", ["one"]),
            lambda c: c["anti_slop_gate"].__setitem__("fail_action", "IGNORE"),
        ]
        for mutate in mutations:
            cfg = copy.deepcopy(CONFIG)
            mutate(cfg)
            with self.assertRaises(ChannelOperatingSystemError):
                validate_config(cfg)


if __name__ == "__main__":
    unittest.main()
