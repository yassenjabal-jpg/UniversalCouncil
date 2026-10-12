from __future__ import annotations

from typing import Any


class ChannelOperatingSystemError(ValueError):
    pass


REQUIRED_WORKFLOW = [
    "signal_capture",
    "topic_clustering",
    "topic_scorecard",
    "evidence_pack",
    "packaging_hypotheses",
    "story_thesis",
    "script_and_voice_direction",
    "visual_treatment",
    "reference_frame_assignment",
    "storyboard_and_transition_map",
    "asset_registry",
    "animatic",
    "production",
    "audio_and_music",
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
    "G2 Packaging Gate",
    "G3 Script Lock",
    "G4 Visual Treatment Lock",
    "G5 Animatic Gate",
    "G6 Anti-Slop Gate",
    "G7 Fact/Policy QC",
    "G8 Export QC",
    "G9 Owner Publish Gate",
    "G10 Post-Publish Learning Gate",
}


def validate_config(cfg: dict[str, Any]) -> bool:
    if cfg.get("version") != "1.0":
        raise ChannelOperatingSystemError("channel operating system must be version 1.0")
    if cfg.get("channel_model") != "broad_format_first_multilingual_visual_documentary":
        raise ChannelOperatingSystemError("channel model drifted")
    if cfg.get("visual_system") != "Editorial Renaissance Motion":
        raise ChannelOperatingSystemError("visual system drifted")
    if cfg.get("publication_authority") != "GATED":
        raise ChannelOperatingSystemError("publishing must remain gated")

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
        "evidence_ids",
        "translation_note",
    }:
        if field not in required_columns:
            raise ChannelOperatingSystemError(f"script schema missing {field}")

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

    anti_slop = cfg.get("anti_slop_gate", {})
    if anti_slop.get("required") is not True:
        raise ChannelOperatingSystemError("anti-slop gate cannot be disabled")
    if len(anti_slop.get("checks", [])) < 8:
        raise ChannelOperatingSystemError("anti-slop gate is incomplete")
    if anti_slop.get("fail_action") != "RETURN_TO_EDITORIAL_OR_VISUAL_TREATMENT":
        raise ChannelOperatingSystemError("anti-slop failure must return to editorial/visual treatment")

    if set(cfg.get("quality_gates", [])) != REQUIRED_GATES:
        raise ChannelOperatingSystemError("quality gates drifted")

    roles = cfg.get("roles", {})
    for required_role in {
        "Audience Growth & Packaging Operator",
        "Evidence & Research Lead",
        "Editorial Director / Showrunner",
        "AI Visual & Post-Production Producer",
        "Risk & Assurance",
        "Technical Operator",
        "Red Team",
        "Owner",
    }:
        if required_role not in roles:
            raise ChannelOperatingSystemError(f"missing required media role: {required_role}")

    return True
