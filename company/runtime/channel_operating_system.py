from __future__ import annotations

from typing import Any


class ChannelOperatingSystemError(ValueError):
    pass


REQUIRED_WORKFLOW = [
    "market_scan",
    "social_trend_scan",
    "market_synthesis",
    "story_premise_generation",
    "story_feasibility_check",
    "packaging_hypothesis",
    "title_candidate_generation",
    "red_team_click_challenge",
    "owner_title_gate",
    "story_question",
    "script_research_pack",
    "story_architecture",
    "first_script",
    "editorial_rewrite",
    "independent_fact_check",
    "narration_rewrite",
    "script_lock",
    "script_breakdown",
    "visual_story_case",
    "art_direction",
    "asset_plan",
    "rights_and_source_preclearance",
    "shot_design",
    "storyboard",
    "camera_plan",
    "sonic_concept",
    "narration_plan",
    "title_promise_alignment",
    "animatic",
    "production_readiness_review",
    "narration_recording",
    "dialogue_cleanup",
    "narration_master_qc",
    "production_asset_ingest",
    "raster_asset_build",
    "vector_asset_build",
    "optional_3d_asset_build",
    "visual_asset_qc",
    "motion_build",
    "compositing",
    "motion_qc",
    "editorial_rough_cut",
    "picture_refinement",
    "picture_lock",
    "detailed_sound_design",
    "mix_master",
    "audiovisual_sync_qc",
    "thumbnail_composite",
    "packaging_typography",
    "packaging_variants",
    "packaging_qc",
    "final_fact_policy_qc",
    "anti_slop_gate",
    "multilingual_preflight",
    "final_conform_qc",
    "render_export_master",
    "export_qc",
    "owner_publish_gate",
    "analytics_postmortem",
    "project_archive",
    "memory_and_routine_update",
]

REQUIRED_GATES = {
    "G0 Market Opportunity Gate",
    "G1 Owner Title Lock",
    "G2 Script Lock",
    "G3 Production Ready Lock",
    "G4 Narration Handoff",
    "G5 Visual Asset Handoff",
    "G6 Motion Handoff",
    "G7 Picture Lock",
    "G8 Sound/Mix + AV Sync Handoff",
    "G9 Packaging Handoff",
    "G10 Assurance + Export + Owner Publish Gate",
    "G11 Learning + Archive Closeout",
}

REQUIRED_PRODUCTION_ROLES = {
    "Media Producer / Production Coordinator",
    "Audience Growth & Packaging Strategist",
    "Thumbnail & Packaging Designer",
    "Evidence & Research Lead",
    "Independent Fact Checker",
    "Editorial Director / Showrunner",
    "Script & Voice Director",
    "Visual Art Director / Frame Curator",
    "Cinematography / Shot Design",
    "Motion & Picture Editor",
    "Music Supervisor & Sound Designer",
    "Dialogue & Mix Engineer",
    "Localization Producer",
    "Risk & Assurance",
    "Technical Operator",
    "Finance Controller",
    "Red Team",
    "Owner",
    "Human Assistance Pool / On-Demand Specialist",
}

REQUIRED_AUDIO_STEMS = {
    "DX dialogue",
    "MX music",
    "FX sound design",
    "AMB atmosphere",
    "FULL master",
}

REQUIRED_SCRIPT_PASSES = [
    "S0 Story Question",
    "S1 Research Pack",
    "S2 Story Architecture",
    "S3 First Script",
    "S4 Editorial Rewrite",
    "S5 Independent Fact Check",
    "S6 Narration Rewrite",
    "S7 Locked Script",
]

REQUIRED_PRODUCTION_DEPARTMENTS = [
    "P01_voice_narration",
    "P02_visual_assets",
    "P03_motion_compositing",
    "P04_picture_edit",
    "P05_sound_mix",
    "P06_packaging",
    "P07_assurance_delivery",
    "P08_learning_archive",
]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ChannelOperatingSystemError(message)


def _validate_single_program_stages(stages: list[dict[str, Any]], context: str) -> None:
    for stage in stages:
        _require(bool(stage.get("id")), f"{context} stage missing id")
        _require(bool(stage.get("program")), f"{context} stage {stage.get('id')} missing program")
        _require(bool(stage.get("output")), f"{context} stage {stage.get('id')} missing output")


def validate_config(cfg: dict[str, Any]) -> bool:
    _require(cfg.get("version") == "1.8", "channel operating system must be version 1.8")
    _require(
        cfg.get("channel_model") == "broad_format_first_multilingual_visual_documentary",
        "channel model drifted",
    )
    _require(cfg.get("visual_system") == "Editorial Renaissance Motion", "visual system drifted")
    _require(cfg.get("publication_authority") == "GATED", "publishing must remain gated")

    benchmark = cfg.get("benchmark_profile", {})
    _require(
        benchmark.get("name") == "professional_youtube_studio_benchmark_2026_10_13",
        "studio benchmark profile missing",
    )
    _require(benchmark.get("adopt_disciplines_not_headcount") is True, "benchmark discipline rule drifted")
    _require(len(benchmark.get("reference_models", [])) >= 5, "studio benchmark reference set is too small")

    portfolio = cfg.get("portfolio_balance", {})
    _require(int(portfolio.get("initial_window_videos", 0)) == 6, "initial portfolio window must remain six")
    _require(int(portfolio.get("max_same_family_in_window", 99)) <= 2, "portfolio over-concentrates one family")
    _require(
        int(portfolio.get("minimum_distinct_families_in_initial_window", 0)) >= 4,
        "initial portfolio needs at least four topic families",
    )

    sources = cfg.get("trend_radar", {}).get("sources", [])
    _require(len(sources) >= 6, "trend radar is too narrow")
    _require(cfg.get("trend_radar", {}).get("evergreen_reframe_required") is True, "evergreen reframe required")

    fields = cfg.get("topic_scoring", {}).get("fields", {})
    _require(sum(int(value) for value in fields.values()) == 100, "topic scoring weights must total 100")
    for required_field in {
        "curiosity_gap",
        "story_novelty",
        "story_engine_strength",
        "thumbnail_one_frame_strength",
        "viewer_stakes_or_emotional_charge",
        "evidence_sourceability",
    }:
        _require(required_field in fields, f"topic scoring missing {required_field}")
    topic_gates = cfg.get("topic_scoring", {}).get("gates", {})
    _require(int(topic_gates.get("minimum_total", 0)) >= 70, "topic score gate too weak")
    minimum_to_field = {
        "minimum_curiosity_gap": "curiosity_gap",
        "minimum_story_novelty": "story_novelty",
        "minimum_story_engine_strength": "story_engine_strength",
        "minimum_thumbnail_one_frame_strength": "thumbnail_one_frame_strength",
        "minimum_evidence_sourceability": "evidence_sourceability",
        "minimum_visual_explainability": "visual_explainability",
    }
    for minimum_key, field_key in minimum_to_field.items():
        _require(
            int(topic_gates.get(minimum_key, 0)) <= int(fields.get(field_key, 0)),
            f"{minimum_key} cannot exceed its scoring weight",
        )
    _require(int(topic_gates.get("minimum_curiosity_gap", 0)) >= 7, "curiosity gate too weak")
    _require(int(topic_gates.get("minimum_story_engine_strength", 0)) >= 7, "story-engine gate too weak")
    _require(
        int(topic_gates.get("minimum_thumbnail_one_frame_strength", 0)) >= 7,
        "thumbnail one-frame gate too weak",
    )
    _require(topic_gates.get("require_one_sentence_question") is True, "topic must have one-sentence question")
    _require(topic_gates.get("require_concrete_story_anchor") is True, "topic needs a concrete story anchor")
    _require(
        topic_gates.get("require_unresolved_tension_or_contradiction") is True,
        "topic needs tension or contradiction",
    )
    _require(topic_gates.get("require_story_archetype") is True, "topic needs a story archetype")
    _require(topic_gates.get("require_thumbnail_hypothesis") is True, "topic needs a thumbnail hypothesis")
    _require(
        topic_gates.get("reject_if_only_trending_without_durable_question") is True,
        "trend-only topics must fail",
    )
    _require(
        topic_gates.get("reject_if_abstract_category_without_story_premise") is True,
        "abstract category-only topics must fail",
    )

    _require(cfg.get("workflow") == REQUIRED_WORKFLOW, "workflow stages or order drifted")
    _require(set(cfg.get("quality_gates", [])) == REQUIRED_GATES, "quality gates drifted")

    master = cfg.get("master_pipeline", {})
    _require(master.get("phases") == ["writing", "pre_production", "production"], "master phase order drifted")
    _require(master.get("phase_order_locked") is True, "master phase order must be locked")
    phase_rules = set(master.get("phase_transition_rules", []))
    _require(
        {
            "writing_cannot_complete_without_owner_title_lock_and_script_lock",
            "pre_production_cannot_start_before_script_lock",
            "production_cannot_start_before_production_ready_lock",
            "feedback_returns_to_source_phase_or_department_with_formal_return_ticket",
            "locked_title_cannot_change_without_owner_reapproval",
        }.issubset(phase_rules),
        "master phase transition rules are incomplete",
    )

    writing = cfg.get("writing_phase", {})
    _require(writing.get("exit_gate") == "SCRIPT_LOCK", "writing must end at Script Lock")
    sections = writing.get("sections", [])
    _require(
        [s.get("id") for s in sections] == ["W1_title_development", "W2_script_development"], "writing sections drifted"
    )
    title_section, script_section = sections
    _validate_single_program_stages(title_section.get("stages", []), "title development")
    _validate_single_program_stages(script_section.get("stages", []), "script development")
    _require(script_section.get("entry_requirement") == "OWNER_TITLE_LOCK", "script must require Owner Title Lock")

    title_system = writing.get("title_system", {})
    _require(int(title_system.get("required_topic_count", 0)) == 3, "exactly three topic candidates required")
    _require(int(title_system.get("required_titles_per_topic", 0)) == 2, "each topic must have exactly two titles")
    _require(title_system.get("topic_distinctness_required") is True, "topic candidates must be distinct")
    _require(title_system.get("story_archetype_diversity_required") is True, "story archetypes must be diverse")
    _require(
        title_system.get("title_distinctness_within_topic_required") is True,
        "title variants within each topic must be distinct",
    )
    _require(title_system.get("youtube_native_discovery_required") is True, "YouTube-native discovery is required")
    _require(title_system.get("authorized_native_fallback_allowed") is True, "authorized native fallback is required")
    _require(title_system.get("degraded_discovery_requires_hold") is True, "degraded discovery must hold")
    _require(title_system.get("packaging_hypothesis_required") is True, "thumbnail hypothesis is required")
    _require(title_system.get("red_team_stranger_click_required") is True, "Red Team click challenge is required")
    _require(title_system.get("owner_selection_required") is True, "Owner title selection is required")
    _require(title_system.get("owner_is_only_final_title_authority") is True, "Owner must retain title authority")
    _require(
        title_system.get("script_start_before_owner_selection_forbidden") is True,
        "script cannot start before title selection",
    )
    _require(len(title_system.get("allowed_story_archetypes", [])) >= 8, "story archetype set is too narrow")
    required_topic_fields = {
        "topic",
        "story_premise",
        "story_archetype",
        "hero_anchor",
        "tension_or_mystery",
        "viewer_stakes",
        "why_now",
        "market_signal",
        "competition_level",
        "key_visual",
        "thumbnail_hypothesis",
        "visual_potential",
        "evidence_feasibility",
        "eight_minute_story_feasibility",
        "risk_notes",
    }
    _require(
        required_topic_fields.issubset(set(title_system.get("topic_required_fields", []))),
        "topic cards are incomplete",
    )
    required_thumbnail_fields = {
        "hero_subject",
        "visual_tension",
        "composition",
        "text_0_4_words",
        "works_without_explanatory_text",
    }
    _require(
        required_thumbnail_fields.issubset(set(title_system.get("thumbnail_hypothesis_required_fields", []))),
        "thumbnail hypothesis contract is incomplete",
    )
    required_title_variant_fields = {
        "title",
        "click_reason",
        "viewer_promise",
        "thumbnail_complement",
        "stranger_click_test",
        "youtube_title_style_status",
    }
    _require(
        required_title_variant_fields.issubset(set(title_system.get("title_variant_required_fields", []))),
        "title variants are incomplete",
    )
    required_feasibility = {
        "sufficient_research_material",
        "credible_sources_available",
        "supports_at_least_eight_minutes_without_filler",
        "strong_visual_potential",
        "meaningful_payoff_or_insight",
        "title_promise_can_be_fulfilled",
    }
    _require(
        required_feasibility.issubset(set(title_system.get("feasibility_checks", []))),
        "title feasibility checks are incomplete",
    )
    revision = title_system.get("post_lock_revision", {})
    _require(revision.get("automatic_change_forbidden") is True, "locked title cannot change automatically")
    _require(revision.get("owner_reapproval_required") is True, "title revision requires Owner reapproval")

    scripts = cfg.get("script_development", {})
    _require(scripts.get("single_pass_forbidden") is True, "single-pass scripting is forbidden")
    _require(scripts.get("required_passes") == REQUIRED_SCRIPT_PASSES, "script passes drifted")
    _require(scripts.get("fact_check_before_lock") is True, "fact check must precede Script Lock")
    _require(scripts.get("title_lock_required_before_start") is True, "script start must require title lock")
    _require(scripts.get("owner_title_authority_preserved") is True, "Owner title authority must be preserved")

    research = cfg.get("research_system", {})
    _require(research.get("claim_source_sheet_required") is True, "claim source sheet required")
    _require(research.get("visual_source_rights_sheet_required") is True, "visual rights sheet required")
    _require(research.get("separate_claim_and_visual_ledgers") is True, "claim and visual ledgers must stay separate")
    _require(research.get("market_and_social_scan_required_before_title_gate") is True, "market/social scan required")
    _require(research.get("title_feasibility_required_before_owner_gate") is True, "title feasibility required")
    _require(
        research.get("native_youtube_outlier_evidence_required_before_owner_gate") is True,
        "YouTube-native outlier evidence is required",
    )
    _require(research.get("authorized_native_fallback_allowed") is True, "authorized native fallback is required")
    _require(research.get("degraded_discovery_requires_hold") is True, "degraded discovery must hold")
    _require(int(research.get("required_topic_candidates", 0)) == 3, "exactly three topics are required")
    _require(
        int(research.get("required_title_variants_per_topic", 0)) == 2,
        "exactly two title variants per topic are required",
    )

    pre = cfg.get("pre_production_phase", {})
    _require(pre.get("entry_requirement") == "SCRIPT_LOCK", "pre-production must require Script Lock")
    _require(pre.get("exit_gate") == "PRODUCTION_READY_LOCK", "pre-production must end at Production Ready Lock")
    _validate_single_program_stages(pre.get("stages", []), "pre-production")
    pre_ids = [s.get("id") for s in pre.get("stages", [])]
    _require(pre_ids[0] == "script_breakdown", "pre-production must start with script breakdown")
    _require("title_promise_alignment" in pre_ids, "pre-production must verify title promise alignment")
    _require(pre_ids[-2:] == ["animatic", "production_readiness_review"], "animatic must precede production readiness")
    pre_rules = set(pre.get("stage_rules", []))
    _require("one_program_per_stage" in pre_rules, "pre-production must use one program per stage")
    _require(
        "title_mismatch_creates_owner_title_revision_request_not_automatic_title_change" in pre_rules,
        "pre-production cannot silently change the title",
    )

    visual_case = cfg.get("visual_story_case", {})
    _require(visual_case.get("required") is True, "visual story case is required")
    _require(visual_case.get("must_follow_script_lock") is True, "visual story case must follow Script Lock")
    _require(
        visual_case.get("must_precede_production_ready_lock") is True,
        "visual story case must precede Production Ready Lock",
    )
    _require(
        visual_case.get("fail_action") == "RETURN_TO_WRITING_OR_REFRAME_WITH_RETURN_TICKET",
        "visual story failure must return through feedback gate",
    )

    pre_review = cfg.get("preproduction_craft_review", {})
    _require(pre_review.get("required") is True, "pre-production craft review required")
    _require(pre_review.get("must_follow_script_lock") is True, "pre-production craft review must follow Script Lock")
    _require(
        pre_review.get("must_precede_production_ready_lock") is True, "pre-production review must precede readiness"
    )
    _require(pre_review.get("may_return_to_writing_via_ticket") is True, "pre-production must use return tickets")

    shot = cfg.get("shot_design_system", {})
    _require(shot.get("required") is True, "shot design required")
    _require(shot.get("must_precede_animatic") is True, "shot design must precede animatic")
    _require(shot.get("accountable_function") == "Cinematography / Shot Design", "shot design accountability drifted")
    _require(len(shot.get("rules", [])) >= 6, "shot design rules incomplete")

    readiness = cfg.get("production_readiness", {})
    _require(readiness.get("required") is True, "production readiness required")
    required_readiness = {
        "owner_title_locked",
        "script_locked",
        "independent_fact_check_passed",
        "visual_story_case_approved",
        "visual_rights_precleared",
        "asset_plan_ready",
        "shot_design_approved",
        "camera_continuity_checked",
        "sonic_concept_complete",
        "narration_plan_complete",
        "title_promise_alignment_passed",
        "animatic_locked",
        "required_specialized_tools_available",
        "schedule_acceptable",
        "budget_acceptable",
    }
    _require(
        required_readiness.issubset(set(readiness.get("required_checks", []))), "production readiness checks incomplete"
    )
    _require(readiness.get("fail_action") == "HOLD_PRODUCTION", "production readiness must fail closed")

    production = cfg.get("production_phase", {})
    _require(
        production.get("entry_requirement") == "PRODUCTION_READY_LOCK", "production must require Production Ready Lock"
    )
    _require(production.get("mode") == "SERIAL_PRODUCTION_LINE_WITH_FEEDBACK_GATES", "production line mode drifted")
    _require(production.get("one_active_department") is True, "only one production department may be active")
    _require(production.get("parallel_craft_departments") is False, "parallel craft departments must be forbidden")
    _require(production.get("one_program_per_stage") is True, "production must use one program per stage")
    _require(
        production.get("program_switch_only_at_stage_boundary") is True, "program changes require a stage boundary"
    )
    _require(production.get("next_department_requires_accepted_handoff") is True, "accepted handoff required")
    _require(production.get("downstream_direct_upstream_edit_forbidden") is True, "downstream direct repair forbidden")
    _require(production.get("defect_action") == "RETURN_TICKET_TO_SOURCE_DEPARTMENT", "defects must return to source")

    departments = production.get("departments", [])
    _require(
        [d.get("id") for d in departments] == REQUIRED_PRODUCTION_DEPARTMENTS, "production department order drifted"
    )
    for department in departments:
        _require(bool(department.get("accountable")), f"department {department.get('id')} missing accountable function")
        _require(bool(department.get("handoff")), f"department {department.get('id')} missing handoff")
        _validate_single_program_stages(department.get("stages", []), f"department {department.get('id')}")

    handoff = cfg.get("handoff_contract", {})
    _require(handoff.get("acceptance_required_before_next_department") is True, "handoff acceptance required")
    _require(handoff.get("downstream_direct_repair_forbidden") is True, "downstream direct repair forbidden")
    _require(
        handoff.get("rejection_action") == "RETURN_TICKET_TO_SOURCE_DEPARTMENT",
        "rejected work must return to source department",
    )
    _require(
        set(handoff.get("valid_statuses", [])) == {"READY_FOR_REVIEW", "ACCEPTED", "REJECTED_RETURN_TO_SOURCE"},
        "handoff statuses drifted",
    )
    required_return_fields = {
        "return_ticket_id",
        "source_department",
        "detecting_department",
        "artifact_ref",
        "defect",
        "reason_for_rejection",
        "requested_correction",
        "do_not_change",
        "resume_handoff",
    }
    _require(
        required_return_fields.issubset(set(handoff.get("return_ticket_required_fields", []))),
        "return ticket incomplete",
    )

    stage_contract = cfg.get("stage_execution_contract", {})
    _require(stage_contract.get("exactly_one_primary_program") is True, "one primary program required")
    _require(
        stage_contract.get("simultaneous_secondary_craft_program_forbidden") is True, "second craft program forbidden"
    )
    _require(stage_contract.get("program_switch_requires_new_stage") is True, "program switch requires new stage")
    _require(stage_contract.get("checkpoint_before_stage_exit") is True, "checkpoint required before stage exit")
    _require(stage_contract.get("output_verification_required") is True, "stage output verification required")

    routing = cfg.get("studio_routing_model", {})
    _require(routing.get("mode") == "THREE_PHASE_STUDIO_WITH_SERIAL_PRODUCTION", "studio routing mode drifted")
    _require(
        routing.get("phase_sequence") == ["Writing", "Pre-production", "Production"], "studio phase sequence drifted"
    )
    _require(
        set(routing.get("core_functions", [])) == {"Media Producer / Production Coordinator"},
        "only Producer may remain always-active control plane",
    )
    rules = set(routing.get("rules", []))
    required_rules = {
        "writing_precedes_preproduction",
        "preproduction_precedes_production",
        "three_topics_two_titles_each_before_owner_title_gate",
        "script_cannot_start_before_owner_title_lock",
        "one_program_only_per_stage",
        "activate_one_production_department_only",
        "next_department_waits_for_handoff_acceptance",
        "downstream_department_returns_defects_to_source_instead_of_cross_editing",
    }
    _require(required_rules.issubset(rules), "studio routing rules incomplete")

    packaging = cfg.get("packaging_system", {})
    _require(
        packaging.get("thumbnail_designer_independent_craft_function") is True, "thumbnail craft must stay distinct"
    )
    stage_a = set(packaging.get("stage_a_before_script", []))
    _require(
        {
            "youtube_native_outlier_read",
            "three_distinct_story_premises",
            "three_distinct_story_archetypes",
            "one_thumbnail_hypothesis_per_topic",
            "two_title_variants_per_topic",
            "title_thumbnail_pair_review",
            "red_team_stranger_click_pass",
            "owner_title_selection",
        }.issubset(stage_a),
        "early packaging must enforce story, thumbnail and click gates",
    )
    _require(
        packaging.get("title_changes_after_owner_lock_require_owner_reapproval") is True, "title revisions need Owner"
    )
    _require(len(packaging.get("stage_b_after_picture_lock", [])) >= 4, "final packaging stage incomplete")

    audio = cfg.get("audio_system", {})
    _require(
        audio.get("principle") == "sound is designed with picture, not added after picture", "audio principle drifted"
    )
    _require(
        audio.get("sonic_concept_required_in_preproduction") is True, "sonic concept must happen in pre-production"
    )
    _require(audio.get("final_sound_design_after_picture_lock") is True, "final sound design requires Picture Lock")
    _require(audio.get("picture_lock_required_before_final_sound_design") is True, "picture lock audio rule drifted")
    _require(set(audio.get("mandatory_stems", [])) == REQUIRED_AUDIO_STEMS, "mandatory audio stems drifted")
    mix = audio.get("mix_targets_internal_not_platform_requirements", {})
    _require(mix.get("program_integrated_lufs_target") == "-14 LUFS ±1", "internal loudness target drifted")
    _require(mix.get("true_peak_ceiling") == "-1 dBTP", "true peak ceiling drifted")

    frame_types = cfg.get("frame_bible", {}).get("canonical_frame_types", [])
    _require(len(frame_types) == 12, "frame bible must contain 12 canonical frame families")
    _require(
        cfg.get("frame_bible", {}).get("composition_rules", {}).get("editable_language_layers") is True,
        "reference frames must remain language-portable",
    )
    _require(len(cfg.get("transition_system", {}).get("canonical", [])) >= 8, "transition grammar too small")

    anti_slop = cfg.get("anti_slop_gate", {})
    _require(anti_slop.get("required") is True, "anti-slop gate cannot be disabled")
    _require(len(anti_slop.get("checks", [])) >= 8, "anti-slop gate incomplete")

    roles = cfg.get("roles", {})
    missing_roles = REQUIRED_PRODUCTION_ROLES - set(roles)
    _require(not missing_roles, f"missing required media roles: {sorted(missing_roles)}")

    assistance = cfg.get("human_assistance_lane", {})
    _require(assistance.get("enabled") is True, "human assistance lane must remain enabled")
    _require(assistance.get("available_at_any_stage") is True, "human assistance must remain available")
    _require(
        assistance.get("coordinator") == "Media Producer / Production Coordinator",
        "human assistance must be Producer-coordinated",
    )
    _require(
        "do not transfer publish authority" in assistance.get("rules", []),
        "human assistance cannot transfer publish authority",
    )
    _require(
        "verify human output before resuming automated production" in assistance.get("rules", []),
        "human assistance return must be verified",
    )

    return True
