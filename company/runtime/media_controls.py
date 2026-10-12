class MediaControlError(ValueError):
    pass


REQUIRED_MEDIA_FUNCTIONS = {
    "media_producer",
    "editorial_director",
    "independent_fact_checker",
    "script_voice_director",
    "visual_art_director",
    "motion_picture_editor",
    "music_sound_supervisor",
    "dialogue_mix_engineer",
    "audience_growth_strategist",
    "thumbnail_packaging_designer",
    "localization_producer",
}

ACTIVE_PILOT_FUNCTIONS = REQUIRED_MEDIA_FUNCTIONS - {"localization_producer"}

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
    if config.get("version") != "1.4":
        raise MediaControlError("media venture must be version 1.4")

    functions = {f["id"]: f for f in config.get("production_functions", [])}
    missing = REQUIRED_MEDIA_FUNCTIONS - set(functions)
    if missing:
        raise MediaControlError(f"missing media functions: {sorted(missing)}")

    for function_id in ACTIVE_PILOT_FUNCTIONS:
        if functions[function_id].get("default_status") != "ACTIVE_FOR_MEDIA_PILOT":
            raise MediaControlError(f"{function_id} must be active for pilot")

    if functions["localization_producer"].get("default_status") not in {
        "ON_DEMAND",
        "ACTIVE_FOR_MEDIA_PILOT",
    }:
        raise MediaControlError("localization producer must be on-demand or active")

    independence = set(config.get("function_independence_rules", []))
    required_independence = {
        "picture_editor_cannot_self_approve_picture_lock",
        "music_sound_supervisor_does_not_self_approve_final_mix_qc",
        "owner_voice_approval_is_separate_from_technical_mix_approval",
        "research_or_writer_cannot_self_clear_material_fact_check",
        "growth_strategist_does_not_replace_thumbnail_design_review",
        "producer_controls_schedule_resources_not_editorial_truth",
        "motion_editor_participates_before_script_lock",
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
    }:
        if capability not in toolchain:
            raise MediaControlError(f"missing audio capability state: {capability}")

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
