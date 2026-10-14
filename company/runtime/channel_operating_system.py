from __future__ import annotations

from typing import Any

from company.runtime.lean_video_production import ProductionWorkflowError, validate_production_config


class ChannelOperatingSystemError(ValueError):
    pass


REQUIRED_WORKFLOW = ["research_script", "visual_direction", "asset_pack", "edit_motion", "final_qc"]
REQUIRED_GATES = ["Preproduction Lock", "Rough Cut Review", "Final QC"]
REQUIRED_SCRIPT_PASSES = ["Evidence Draft", "Locked Script"]
REQUIRED_AUDIO_STEMS = {"DX dialogue", "MX music", "FX sound design", "FULL master"}

# Craft functions may be consulted on demand; they do not each own an approval queue.
REQUIRED_PRODUCTION_ROLES = {
    "Media Producer / Production Coordinator",
    "Editorial Director / Showrunner",
    "Independent Fact Checker",
    "Visual Art Director / Frame Curator",
    "Motion & Picture Editor",
    "Independent QC Reviewer",
    "Owner",
}

EXACT_CONTRACTS = {
    "version": "2.0",
    "channel_model": "broad_format_first_multilingual_visual_documentary",
    "visual_system": "Modern Editorial Surrealism",
    "publication_authority": "GATED",
    "visual_identity.version": "2.1-candidate",
    "visual_identity.bible": "docs/operations/media/MODERN_EDITORIAL_SURREALISM_VISUAL_BIBLE.md",
    "visual_identity.primary_reference": "user-provided 1000061003.mp4",
    "visual_identity.reference_authority": "PRIMARY_VISUAL_REFERENCE",
    "visual_identity.episode_accent_required": True,
    "visual_identity.architecture_is_topic_dependent_only": True,
    "visual_identity.classical_art_is_optional_not_mandatory": True,
    "visual_identity.thumbnail_hypotheses_per_episode": 1,
    "visual_identity.generated_thumbnail_assets_per_episode": 1,
    "visual_identity.single_thumbnail_lock": True,
    "visual_identity.multi_panel_thumbnail_output_forbidden": True,
    "visual_identity.hero_objects_per_key_frame": 1,
    "visual_identity.synthetic_documentary_evidence_forbidden": True,
    "visual_generation_brief_system.version": "2.0",
    "visual_generation_brief_system.status": "REQUIRED_FOR_ANY_GENERATED_VISUAL",
    "visual_generation_brief_system.composed_by": ["Visual Art Director / Frame Curator"],
    "visual_generation_brief_system.approval_required_from": ["Visual Art Director / Frame Curator"],
    "visual_generation_brief_system.approval_scope": "ASSET_PACK_NOT_PER_FRAME",
    "visual_generation_brief_system.approval_state_required": "APPROVED_IN_PREPRODUCTION_LOCK",
    "visual_generation_brief_system.executor": "Technical Operator",
    "visual_generation_brief_system.official_thumbnail_concepts_per_episode": 1,
    "visual_generation_brief_system.generated_thumbnail_assets_per_episode": 1,
    "visual_generation_brief_system.generation_jobs_per_episode_thumbnail_stage": 1,
    "visual_generation_brief_system.context_isolation_required": True,
    "visual_generation_brief_system.only_selected_brief_may_enter_generation_context": True,
    "visual_generation_brief_system.multi_panel_output_forbidden": True,
    "script_development.required_passes": REQUIRED_SCRIPT_PASSES,
    "script_development.drafts_max": 2,
    "script_development.fact_check_before_lock": True,
    "script_development.fact_checker_independent": True,
    "preproduction_craft_review.embedded_in": "Preproduction Lock",
    "preproduction_craft_review.unanimous_approval_required": False,
    "production_readiness.embedded_in": "Preproduction Lock",
    "research_system.claim_source_sheet_required": True,
    "research_system.visual_source_rights_sheet_required": True,
    "research_system.separate_claim_and_visual_ledgers": True,
    "frame_bible.composition_rules.editable_language_layers": True,
    "audio_system.spotting_embedded_in": "Preproduction Lock",
    "audio_system.picture_lock_embedded_in": "Rough Cut Review",
    "audio_system.post_picture_lock_timing_change_requires_audio_reconform": True,
    "audio_system.mix_targets_internal_not_platform_requirements.program_integrated_lufs_target": "-14 LUFS ±1",
    "audio_system.mix_targets_internal_not_platform_requirements.true_peak_ceiling": "-1 dBTP",
    "anti_slop_checks.required": True,
    "anti_slop_checks.embedded_in": ["Preproduction Lock", "Final QC"],
    "portfolio_balance.initial_window_videos": 6,
    "portfolio_balance.max_same_family_in_window": 2,
    "portfolio_balance.minimum_distinct_families_in_initial_window": 4,
    "portfolio_balance.relax_only_after_first_party_audience_evidence": True,
    "trend_radar.evergreen_reframe_required": True,
    "benchmark_profile.adopt_disciplines_not_headcount": True,
}


def value_at(cfg: dict[str, Any], path: str) -> Any:
    value = cfg
    for part in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def validate_config(cfg: dict[str, Any]) -> bool:
    for path, expected in EXACT_CONTRACTS.items():
        actual = value_at(cfg, path)
        if type(actual) is not type(expected) or actual != expected:
            raise ChannelOperatingSystemError(f"channel contract drift: {path}")
    try:
        validate_production_config(cfg)
    except ProductionWorkflowError as exc:
        raise ChannelOperatingSystemError(str(exc)) from exc
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
        if not required.issubset(set(value_at(cfg, path) or [])):
            raise ChannelOperatingSystemError(f"missing substantive protection: {path}")
    for path, minimum in {
        "anti_slop_checks.checks": 8,
        "transition_system.canonical": 8,
        "trend_radar.sources": 6,
        "research_system.expert_consultation_required_when": 3,
    }.items():
        if len(value_at(cfg, path) or []) < minimum:
            raise ChannelOperatingSystemError(f"incomplete craft/evidence guidance: {path}")
    if sum(cfg.get("topic_scoring", {}).get("fields", {}).values()) != 100:
        raise ChannelOperatingSystemError("topic weights must total 100")
    if cfg.get("topic_scoring", {}).get("gates", {}).get("minimum_total", 0) < 70:
        raise ChannelOperatingSystemError("topic score threshold too weak")
    return True
