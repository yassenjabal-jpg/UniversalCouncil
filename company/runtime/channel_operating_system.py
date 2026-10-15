from __future__ import annotations

from typing import Any


class ChannelOperatingSystemError(ValueError):
    pass


REQUIRED_WORKFLOW = [
    "signal_capture",
    "topic_clustering",
    "topic_scorecard",
    "evidence_pack",
    "visual_story_case",
    "packaging_hypotheses",
    "story_thesis",
    "preproduction_craft_review",
    "script_development",
    "independent_fact_check",
    "script_lock",
    "visual_treatment",
    "audio_spotting_and_sonic_concept",
    "reference_frame_assignment",
    "shot_design_and_camera_plan",
    "storyboard_transition_audio_map",
    "asset_registry",
    "animatic",
    "production_readiness_review",
    "narration_recording_and_dialogue_edit",
    "production",
    "editorial_rough_cut",
    "packaging_finalization_and_test_plan",
    "picture_lock",
    "music_sound_design",
    "mix_master",
    "audiovisual_sync_qc",
    "multilingual_preflight",
    "anti_slop_gate",
    "fact_policy_qc",
    "export_qc",
    "publish_gate",
    "analytics_postmortem",
    "memory_and_routine_update",
]

REQUIRED_GATES = {
    "G0 Trend/Topic Gate",
    "G1 Evidence Gate",
    "G2 Visual Story Case Gate",
    "G3 Packaging Hypothesis Gate",
    "G4 Pre-production Craft Review",
    "G5 Script + Independent Fact Check Lock",
    "G6 Visual + Sonic Treatment Lock",
    "G7 Shot Design + Animatic + Spotting Gate",
    "G8 Production Readiness Gate",
    "G9 Picture Lock Gate",
    "G10 Audio-Visual Sync Gate",
    "G11 Packaging Finalization Gate",
    "G12 Anti-Slop Gate",
    "G13 Fact/Policy/Continuity QC",
    "G14 Mix/Master QC",
    "G15 Export QC",
    "G16 Owner Publish Gate",
    "G17 Post-Publish Learning Gate",
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
    "S0 Story Skeleton",
    "S1 Evidence Draft",
    "S2 Visual Draft",
    "S3 Voice/Performance Draft",
    "S4 Locked Script",
]


def validate_config(cfg: dict[str, Any]) -> bool:
    if cfg.get("version") != "1.4":
        raise ChannelOperatingSystemError("channel operating system must be version 1.4")
    if cfg.get("channel_model") != "broad_format_first_multilingual_visual_documentary":
        raise ChannelOperatingSystemError("channel model drifted")
    if cfg.get("visual_system") != "Editorial Renaissance Motion":
        raise ChannelOperatingSystemError("visual system drifted")
    if cfg.get("publication_authority") != "GATED":
        raise ChannelOperatingSystemError("publishing must remain gated")

    benchmark = cfg.get("benchmark_profile", {})
    if benchmark.get("name") != "professional_youtube_studio_benchmark_2026_10_13":
        raise ChannelOperatingSystemError("studio benchmark profile missing")
    if benchmark.get("adopt_disciplines_not_headcount") is not True:
        raise ChannelOperatingSystemError("benchmark must adopt disciplines, not headcount")
    if len(benchmark.get("reference_models", [])) < 5:
        raise ChannelOperatingSystemError("studio benchmark reference set is too small")

    portfolio = cfg.get("portfolio_balance", {})
    if int(portfolio.get("initial_window_videos", 0)) != 6:
        raise ChannelOperatingSystemError("initial portfolio window must remain six videos")
    if int(portfolio.get("max_same_family_in_window", 99)) > 2:
        raise ChannelOperatingSystemError("initial portfolio must not over-concentrate one family")
    if int(portfolio.get("minimum_distinct_families_in_initial_window", 0)) < 4:
        raise ChannelOperatingSystemError("initial portfolio needs at least four topic families")
    if portfolio.get("relax_only_after_first_party_audience_evidence") is not True:
        raise ChannelOperatingSystemError("portfolio balance may relax only after first-party evidence")

    sources = cfg.get("trend_radar", {}).get("sources", [])
    if len(sources) < 6:
        raise ChannelOperatingSystemError("trend radar is too narrow")
    if cfg.get("trend_radar", {}).get("evergreen_reframe_required") is not True:
        raise ChannelOperatingSystemError("trend radar must require evergreen reframing")

    fields = cfg.get("topic_scoring", {}).get("fields", {})
    if sum(int(value) for value in fields.values()) != 100:
        raise ChannelOperatingSystemError("topic scoring weights must total 100")
    gates = cfg.get("topic_scoring", {}).get("gates", {})
    if int(gates.get("minimum_total", 0)) < 70:
        raise ChannelOperatingSystemError("topic score gate too weak")
    if gates.get("require_one_sentence_question") is not True:
        raise ChannelOperatingSystemError("topic must have a one-sentence question")
    if gates.get("reject_if_only_trending_without_durable_question") is not True:
        raise ChannelOperatingSystemError("trend-only topics must fail")

    workflow = cfg.get("workflow", [])
    if workflow != REQUIRED_WORKFLOW:
        raise ChannelOperatingSystemError("workflow stages or order drifted")

    research = cfg.get("research_system", {})
    if research.get("claim_source_sheet_required") is not True:
        raise ChannelOperatingSystemError("claim source sheet is required")
    if research.get("visual_source_rights_sheet_required") is not True:
        raise ChannelOperatingSystemError("visual source/rights sheet is required")
    if research.get("separate_claim_and_visual_ledgers") is not True:
        raise ChannelOperatingSystemError("claim and visual-source ledgers must stay separate")
    if len(research.get("expert_consultation_required_when", [])) < 3:
        raise ChannelOperatingSystemError("expert-consultation triggers are incomplete")

    visual_case = cfg.get("visual_story_case", {})
    if visual_case.get("required") is not True:
        raise ChannelOperatingSystemError("visual story case is required")
    if visual_case.get("must_precede_script_lock") is not True:
        raise ChannelOperatingSystemError("visual story case must precede script lock")
    required_visual_fields = {
        "why_video_not_article",
        "key_visual",
        "key_demonstration_or_diagram",
        "archive_or_real_world_evidence",
        "visual_transformation_or_reveal",
        "editor_feasibility_note",
    }
    if not required_visual_fields.issubset(set(visual_case.get("required_fields", []))):
        raise ChannelOperatingSystemError("visual story case contract is incomplete")
    if visual_case.get("fail_action") != "RETURN_TOPIC_TO_BACKLOG_OR_REFRAME":
        raise ChannelOperatingSystemError("visual story case must fail back to topic/reframe")

    preprod = cfg.get("preproduction_craft_review", {})
    if preprod.get("required") is not True or preprod.get("must_precede_script_lock") is not True:
        raise ChannelOperatingSystemError("pre-production craft review is mandatory before script lock")
    required_preprod = {
        "Editorial Director / Showrunner",
        "Media Producer / Production Coordinator",
        "Evidence & Research Lead",
        "Motion & Picture Editor",
        "Visual Art Director / Frame Curator",
        "Cinematography / Shot Design",
        "Music Supervisor & Sound Designer",
        "Audience Growth & Packaging Strategist",
    }
    if not required_preprod.issubset(set(preprod.get("participants", []))):
        raise ChannelOperatingSystemError("pre-production craft review participants are incomplete")

    shot_design = cfg.get("shot_design_system", {})
    if shot_design.get("required") is not True:
        raise ChannelOperatingSystemError("shot design system is required")
    if shot_design.get("must_precede_animatic") is not True:
        raise ChannelOperatingSystemError("shot design must precede animatic")
    if shot_design.get("accountable_function") != "Cinematography / Shot Design":
        raise ChannelOperatingSystemError("cinematography accountability drifted")
    required_shot_fields = {
        "shot_id",
        "story_beat_id",
        "shot_purpose",
        "framing",
        "shot_size",
        "camera_motion",
        "depth_layers",
        "subject_staging",
        "screen_direction",
        "continuity_link",
        "transition_motivation",
        "sound_sync_note",
        "asset_requirements",
    }
    if not required_shot_fields.issubset(set(shot_design.get("required_fields", []))):
        raise ChannelOperatingSystemError("shot design contract is incomplete")
    if shot_design.get("fail_action") != "RETURN_TO_VISUAL_TREATMENT_OR_STORYBOARD":
        raise ChannelOperatingSystemError("shot design failure must return to visual treatment/storyboard")
    if len(shot_design.get("rules", [])) < 6:
        raise ChannelOperatingSystemError("shot design rules are incomplete")

    scripts = cfg.get("script_development", {})
    if scripts.get("single_pass_forbidden") is not True:
        raise ChannelOperatingSystemError("single-pass script development is forbidden")
    if scripts.get("required_passes") != REQUIRED_SCRIPT_PASSES:
        raise ChannelOperatingSystemError("script development passes drifted")
    if scripts.get("fact_check_before_lock") is not True:
        raise ChannelOperatingSystemError("fact check must precede script lock")
    if scripts.get("visual_draft_requires_editor_review") is not True:
        raise ChannelOperatingSystemError("visual script draft requires editor review")

    script = cfg.get("script_schema", {})
    required_columns = set(script.get("required_columns", []))
    for field in {
        "narration",
        "intent",
        "emotion_tag",
        "energy_1_5",
        "pace",
        "pitch_contour",
        "emphasis_words",
        "pause_before_ms",
        "pause_after_ms",
        "visual_beat_id",
        "shot_design_id",
        "camera_intent",
        "music_state",
        "sfx",
        "evidence_ids",
        "translation_note",
    }:
        if field not in required_columns:
            raise ChannelOperatingSystemError(f"script schema missing {field}")

    production_ready = cfg.get("production_readiness", {})
    if production_ready.get("required") is not True:
        raise ChannelOperatingSystemError("production readiness gate is required")
    required_readiness = {
        "script_locked",
        "independent_fact_check_passed",
        "key_visuals_approved",
        "claim_sources_complete",
        "visual_rights_clear",
        "storyboard_sufficient",
        "shot_design_approved",
        "camera_continuity_checked",
        "audio_spotting_complete",
        "asset_registry_ready",
        "specialized_tools_available",
        "schedule_acceptable",
        "budget_acceptable",
    }
    if not required_readiness.issubset(set(production_ready.get("required_checks", []))):
        raise ChannelOperatingSystemError("production-readiness checks are incomplete")
    if production_ready.get("fail_action") != "HOLD_PRODUCTION":
        raise ChannelOperatingSystemError("production readiness must fail closed")

    packaging = cfg.get("packaging_system", {})
    if packaging.get("thumbnail_designer_independent_craft_function") is not True:
        raise ChannelOperatingSystemError("thumbnail design must remain an independent craft function")
    if len(packaging.get("stage_a_before_script", [])) < 4:
        raise ChannelOperatingSystemError("early packaging stage is incomplete")
    if len(packaging.get("stage_b_after_rough_cut", [])) < 4:
        raise ChannelOperatingSystemError("final packaging stage is incomplete")

    frame_types = cfg.get("frame_bible", {}).get("canonical_frame_types", [])
    if len(frame_types) != 12:
        raise ChannelOperatingSystemError("frame bible must contain 12 canonical frame families")
    if cfg.get("frame_bible", {}).get("composition_rules", {}).get("editable_language_layers") is not True:
        raise ChannelOperatingSystemError("reference frames must remain language-portable")

    transitions = cfg.get("transition_system", {})
    if len(transitions.get("canonical", [])) < 8:
        raise ChannelOperatingSystemError("transition grammar is too small")
    if not transitions.get("forbidden_default"):
        raise ChannelOperatingSystemError("transition anti-patterns are required")

    audio = cfg.get("audio_system", {})
    if audio.get("principle") != "sound is designed with picture, not added after picture":
        raise ChannelOperatingSystemError("audio system principle drifted")
    if audio.get("spotting_required_before_reference_frame_lock") is not True:
        raise ChannelOperatingSystemError("audio spotting must precede reference-frame lock")
    if audio.get("picture_lock_required_before_final_sound_design") is not True:
        raise ChannelOperatingSystemError("final sound design requires picture lock")
    if audio.get("post_picture_lock_timing_change_requires_audio_reconform") is not True:
        raise ChannelOperatingSystemError("post-picture-lock timing changes must trigger audio reconform")
    if len(audio.get("music_states", [])) < 8:
        raise ChannelOperatingSystemError("music-state grammar is incomplete")
    if len(audio.get("cue_sheet_required_fields", [])) < 12:
        raise ChannelOperatingSystemError("music cue sheet contract is incomplete")
    if len(audio.get("av_beat_map_required_fields", [])) < 10:
        raise ChannelOperatingSystemError("audio-visual beat map contract is incomplete")
    if set(audio.get("mandatory_stems", [])) != REQUIRED_AUDIO_STEMS:
        raise ChannelOperatingSystemError("mandatory audio stems drifted")
    mix = audio.get("mix_targets_internal_not_platform_requirements", {})
    if mix.get("program_integrated_lufs_target") != "-14 LUFS ±1":
        raise ChannelOperatingSystemError("internal master loudness target drifted")
    if mix.get("true_peak_ceiling") != "-1 dBTP":
        raise ChannelOperatingSystemError("true-peak ceiling drifted")
    if not audio.get("anti_patterns"):
        raise ChannelOperatingSystemError("audio anti-patterns are required")

    anti_slop = cfg.get("anti_slop_gate", {})
    if anti_slop.get("required") is not True:
        raise ChannelOperatingSystemError("anti-slop gate cannot be disabled")
    if len(anti_slop.get("checks", [])) < 8:
        raise ChannelOperatingSystemError("anti-slop gate is incomplete")
    if anti_slop.get("fail_action") != "RETURN_TO_EDITORIAL_OR_VISUAL_TREATMENT":
        raise ChannelOperatingSystemError("anti-slop failure must return to editorial/visual treatment")

    if set(cfg.get("quality_gates", [])) != REQUIRED_GATES:
        raise ChannelOperatingSystemError("quality gates drifted")

    routing = cfg.get("studio_routing_model", {})
    if routing.get("mode") != "SMALL_CORE_ROUTED_CAPABILITIES":
        raise ChannelOperatingSystemError("studio must use small-core routed-capability model")
    if set(routing.get("core_functions", [])) != {
        "Media Producer / Production Coordinator",
        "Editorial Director / Showrunner",
    }:
        raise ChannelOperatingSystemError("studio core functions drifted")
    routed = set(routing.get("stage_routed_craft_functions", []))
    required_routed = {
        "Script & Voice Director",
        "Visual Art Director / Frame Curator",
        "Cinematography / Shot Design",
        "Motion & Picture Editor",
        "Music Supervisor & Sound Designer",
        "Dialogue & Mix Engineer",
        "Audience Growth & Packaging Strategist",
        "Thumbnail & Packaging Designer",
        "Localization Producer",
    }
    if routed != required_routed:
        raise ChannelOperatingSystemError("stage-routed craft function set drifted")
    if set(routing.get("on_demand_support_functions", [])) != {"Human Assistance Pool / On-Demand Specialist"}:
        raise ChannelOperatingSystemError("on-demand human support routing drifted")
    routing_rules = set(routing.get("rules", []))
    if {
        "do_not_call_every_function_for_every_stage",
        "default_to_artifact_delta_or_blocker_not_long_report",
        "parallelize_independent_craft_work_when_safe",
        "one_synthesis_per_gate",
        "shared_production_state_prevents_context_repetition",
        "owner_interruption_is_exception_not_default",
    } - routing_rules:
        raise ChannelOperatingSystemError("studio anti-bureaucracy routing rules are incomplete")

    assistance = cfg.get("human_assistance_lane", {})
    if assistance.get("enabled") is not True or assistance.get("available_at_any_stage") is not True:
        raise ChannelOperatingSystemError("human assistance lane must remain available on demand")
    if assistance.get("coordinator") != "Media Producer / Production Coordinator":
        raise ChannelOperatingSystemError("human assistance must be producer-coordinated")
    if assistance.get("principle") != "smallest necessary human intervention, then return control to the studio":
        raise ChannelOperatingSystemError("human assistance principle drifted")
    triggers = set(assistance.get("trigger_conditions", []))
    required_triggers = {
        "automated recovery exhausted",
        "physical action required",
        "credentials or identity step required",
        "specialized human craft gap",
        "material domain expertise gap",
        "high-uncertainty visual/audio judgment",
        "human contact required for rights/source confirmation",
        "bounded human action is materially faster and lower risk than further automation",
    }
    if not required_triggers.issubset(triggers):
        raise ChannelOperatingSystemError("human assistance triggers are incomplete")
    request_packet = set(assistance.get("request_packet", []))
    if {
        "reason",
        "exact task",
        "current verified state",
        "artifact/project reference",
        "allowed scope",
        "do not change",
        "expected return",
        "acceptance criteria",
        "return handoff",
    } - request_packet:
        raise ChannelOperatingSystemError("human assistance request contract is incomplete")
    assistance_rules = set(assistance.get("rules", []))
    if {
        "human assistance is optional and on-demand, never an always-active bottleneck",
        "request the smallest useful action",
        "do not transfer publish authority",
        "owner approval required for credentials, spend, subscriptions, external sharing or irreversible actions",
        "verify human output before resuming automated production",
        "checkpoint before and after the human handoff",
        "record recurring human-help causes as capability gaps",
    } - assistance_rules:
        raise ChannelOperatingSystemError("human assistance governance rules are incomplete")
    if int(assistance.get("recurring_gap_threshold", 0)) < 2:
        raise ChannelOperatingSystemError("human assistance recurring-gap threshold is invalid")
    if assistance.get("recurring_gap_action") != "capability review for tool, training, workflow or staffing change":
        raise ChannelOperatingSystemError("human assistance recurring-gap action drifted")

    roles = cfg.get("roles", {})
    missing_roles = REQUIRED_PRODUCTION_ROLES - set(roles)
    if missing_roles:
        raise ChannelOperatingSystemError(f"missing required media roles: {sorted(missing_roles)}")

    return True
