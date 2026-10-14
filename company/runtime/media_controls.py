from company.runtime.media_execution_recovery import (
    MediaExecutionRecoveryError,
    validate_execution_recovery_policy,
)


class MediaControlError(ValueError):
    pass


REQUIRED_MEDIA_FUNCTIONS = {
    "media_producer",
    "editorial_director",
    "independent_fact_checker",
    "script_voice_director",
    "visual_art_director",
    "cinematography_shot_designer",
    "motion_picture_editor",
    "music_sound_supervisor",
    "dialogue_mix_engineer",
    "audience_growth_strategist",
    "thumbnail_packaging_designer",
    "localization_producer",
}

CORE_FUNCTIONS = {
    "media_producer",
    "editorial_director",
}

MANDATORY_CLEARANCE_FUNCTIONS = {
    "independent_fact_checker",
}

ROUTED_CRAFT_FUNCTIONS = {
    "script_voice_director",
    "visual_art_director",
    "cinematography_shot_designer",
    "motion_picture_editor",
    "music_sound_supervisor",
    "dialogue_mix_engineer",
    "audience_growth_strategist",
    "thumbnail_packaging_designer",
}

REQUIRED_PILOT_METRICS = {
    "production_time_per_video",
    "owner_human_minutes_per_video",
    "tool_cost_per_video",
    "cost_per_published_minute",
    "revision_count",
    "factual_policy_defects",
    "packaging_quality",
    "audio_revision_count",
    "dialogue_cleanup_minutes",
    "music_sound_design_minutes",
    "mix_master_minutes",
    "av_sync_defects",
    "audio_qc_defects",
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
    "routed_function_invocations",
    "unnecessary_function_invocations",
    "handoff_recovery_count",
    "unknown_execution_events",
}

PUBLISHED_PERFORMANCE_METRICS = {
    "ctr",
    "first_30_second_retention",
    "average_percentage_viewed",
    "watch_time",
    "subscribers_per_video",
    "returning_viewers",
}


def validate_media_team(config):
    if config.get("version") != "1.5":
        raise MediaControlError("media venture must be version 1.5")

    functions = {f["id"]: f for f in config.get("production_functions", [])}
    missing = REQUIRED_MEDIA_FUNCTIONS - set(functions)
    if missing:
        raise MediaControlError(f"missing media functions: {sorted(missing)}")

    for function_id in CORE_FUNCTIONS:
        if functions[function_id].get("default_status") != "CORE_ALWAYS_ACTIVE":
            raise MediaControlError(f"{function_id} must remain core-active")

    for function_id in MANDATORY_CLEARANCE_FUNCTIONS:
        if functions[function_id].get("default_status") != "MANDATORY_CLEARANCE":
            raise MediaControlError(f"{function_id} must remain mandatory clearance")

    for function_id in ROUTED_CRAFT_FUNCTIONS:
        if functions[function_id].get("default_status") != "ROUTED_CRAFT_CAPABILITY":
            raise MediaControlError(f"{function_id} must be stage-routed craft capability")

    if functions["localization_producer"].get("default_status") != "ON_DEMAND":
        raise MediaControlError("localization producer must remain on-demand")

    model = config.get("operating_model", {})
    if model.get("mode") != "SMALL_CORE_ROUTED_CRAFT_CAPABILITIES":
        raise MediaControlError("studio operating model must use a small core with routed craft capabilities")
    if set(model.get("core_functions", [])) != CORE_FUNCTIONS:
        raise MediaControlError("studio core function set drifted")
    if set(model.get("mandatory_clearance_functions", [])) != MANDATORY_CLEARANCE_FUNCTIONS:
        raise MediaControlError("mandatory clearance function set drifted")
    if set(model.get("routed_craft_functions", [])) != ROUTED_CRAFT_FUNCTIONS:
        raise MediaControlError("routed craft function set drifted")
    if model.get("parallelize_when_safe") is not True or model.get("single_synthesis_per_gate") is not True:
        raise MediaControlError("studio efficiency controls are incomplete")
    forbidden = set(model.get("forbidden_defaults", []))
    if {
        "every_function_reviews_every_stage",
        "mandatory_long_form_reports",
        "one_independent_agent_process_per_function",
    } - forbidden:
        raise MediaControlError("anti-bureaucracy defaults are incomplete")

    independence = set(config.get("function_independence_rules", []))
    required_independence = {
        "picture_editor_cannot_self_approve_picture_lock",
        "music_sound_supervisor_does_not_self_approve_final_mix_qc",
        "owner_voice_approval_is_separate_from_technical_mix_approval",
        "research_or_writer_cannot_self_clear_material_fact_check",
        "growth_strategist_does_not_replace_thumbnail_design_review",
        "producer_controls_schedule_resources_not_editorial_truth",
        "motion_editor_participates_before_script_lock",
        "cinematography_defines_shot_language_but_does_not_self_approve_picture_lock",
        "routed_craft_function_is_invoked_by_stage_not_kept_permanently_active",
        "unknown_execution_state_cannot_be_promoted_to_success",
    }
    if not required_independence.issubset(independence):
        raise MediaControlError("media function independence rules are incomplete")

    if "benchmark_artifact" not in config:
        raise MediaControlError("studio benchmark artifact is required")

    toolchain = config.get("media_toolchain", {})
    for capability in {
        "dialogue_cleanup",
        "music_supervision",
        "sound_design",
        "mix_mastering",
        "audiovisual_sync_qc",
        "cinematography_shot_design",
    }:
        if capability not in toolchain:
            raise MediaControlError(f"missing media capability state: {capability}")

    try:
        validate_execution_recovery_policy(config.get("execution_recovery", {}))
    except MediaExecutionRecoveryError as exc:
        raise MediaControlError(str(exc)) from exc

    pilot = config.get("pilot", {})
    if pilot.get("required_before_scale") is not True:
        raise MediaControlError("media pilot must be required before scale")
    if int(pilot.get("video_count", 0)) < 3:
        raise MediaControlError("pilot must include at least 3 videos")
    return True


def validate_media_pilot_record(record, *, published=False):
    required = {"videos_completed", "metrics", "hr_review_status", "scale_decision"}
    missing = required - set(record)
    if missing:
        raise MediaControlError(f"media pilot record missing: {sorted(missing)}")

    if int(record["videos_completed"]) < 3:
        raise MediaControlError("scale decision forbidden before 3 completed pilot videos")

    metrics = set(record["metrics"])
    missing_metrics = REQUIRED_PILOT_METRICS - metrics
    if missing_metrics:
        raise MediaControlError(f"pilot metrics missing: {sorted(missing_metrics)}")

    if published:
        missing_published = PUBLISHED_PERFORMANCE_METRICS - metrics
        if missing_published:
            raise MediaControlError(f"published performance metrics missing: {sorted(missing_published)}")

    if record["hr_review_status"] not in {
        "KEEP",
        "IMPROVEMENT_TRIAL",
        "MERGE",
        "REPLACE",
        "REMOVE_WITHOUT_REPLACEMENT",
    }:
        raise MediaControlError("invalid HR media-team review status")

    if record["scale_decision"] not in {"HOLD", "CONTINUE_PILOT", "SCALE_CANDIDATE", "REJECT"}:
        raise MediaControlError("invalid media scale decision")
    return True


def validate_media_scale_request(pilot_record):
    validate_media_pilot_record(pilot_record, published=False)
    if pilot_record["scale_decision"] != "SCALE_CANDIDATE":
        raise MediaControlError("media scale requires SCALE_CANDIDATE after pilot")
    return True
