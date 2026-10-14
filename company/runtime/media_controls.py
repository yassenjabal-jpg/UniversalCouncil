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
    "independent_qc_reviewer",
}

STAGE_AUTHORITY_FUNCTIONS = {
    "media_producer",
    "editorial_director",
    "visual_art_director",
    "motion_picture_editor",
    "independent_qc_reviewer",
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
    "generation_brief_rework_rounds",
    "prompt_drift_defects",
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
    if config.get("version") != "2.0":
        raise MediaControlError("media venture must be version 2.0")
    functions = {f["id"]: f for f in config.get("production_functions", [])}
    if set(functions) != REQUIRED_MEDIA_FUNCTIONS:
        raise MediaControlError("media functions missing or duplicated")
    if len(functions) != len(config["production_functions"]):
        raise MediaControlError("duplicate media function")
    for function_id in STAGE_AUTHORITY_FUNCTIONS:
        if functions[function_id].get("default_status") != "STAGE_AUTHORITY":
            raise MediaControlError("stage authority must remain active")
    for function_id in REQUIRED_MEDIA_FUNCTIONS - STAGE_AUTHORITY_FUNCTIONS:
        if functions[function_id].get("default_status") != "ON_DEMAND":
            raise MediaControlError("specialist advice must stay on demand")
    required = {
        "research_or_writer_cannot_self_clear_material_fact_check",
        "producer_controls_schedule_resources_not_editorial_truth",
        "final_qc_reviewer_independent_of_editor",
        "stage_owner_has_final_authority",
        "technical_operator_cannot_creatively_rewrite_approved_visual_brief",
    }
    if not required.issubset(set(config.get("function_independence_rules", []))):
        raise MediaControlError("independent facts/QC and final authority required")
    brief = config.get("visual_generation_brief_capability", {})
    for key, expected in {
        "permanent_role": False,
        "final_approver": "Visual Art Director / Frame Curator",
        "approval_scope": "ASSET_PACK_NOT_PER_FRAME",
        "preproduction_lock_required": True,
        "no_prompt_no_generation": True,
        "tool_creative_rewrite_forbidden": True,
        "one_generated_thumbnail_asset_per_episode": True,
        "multi_panel_thumbnail_output_forbidden": True,
    }.items():
        if type(brief.get(key)) is not type(expected) or brief.get(key) != expected:
            raise MediaControlError(f"visual brief contract drift: {key}")
    if config.get("production_workflow_config") != "company/config/channel_operating_system.json":
        raise MediaControlError("single governing workflow required")
    if config.get("visual_production_system") != {
        "governing_doc": "docs/operations/media/LEAN_VIDEO_PRODUCTION_WORKFLOW.md",
        "config_pointer": "company/config/channel_operating_system.json#production_system",
    }:
        raise MediaControlError("legacy production mirror must not return")
    if config.get("system_pilot", {}).get("count") != 1:
        raise MediaControlError("exactly one system pilot required")
    if config.get("live_publish_authority") is not False:
        raise MediaControlError("publication remains unauthorized")
    pilot = config.get("pilot", {})
    if (
        pilot.get("scope") != "BUSINESS_SCALE_OBSERVATION_ONLY_NOT_EPISODE_PRODUCTION"
        or pilot.get("blocks_episode_production") is not False
    ):
        raise MediaControlError("business observation must not block episode production")
    if pilot.get("required_before_scale") is not True or pilot.get("video_count") != 3:
        raise MediaControlError("business-scale observation contract drift")
    tools = config.get("media_toolchain", {})
    if tools.get("video_editing") != "DESCRIPT_PRIMARY_DELIVERY_PENDING_SYSTEM_PILOT":
        raise MediaControlError("single primary editor contract drift")
    if tools.get("after_effects_motion_assembly") != "BACKUP_NATIVE_ONLY_HISTORICAL_EVIDENCE_REVERIFY_ON_USE":
        raise MediaControlError("backup cannot imply current delivery verification")
    return True


def validate_media_pilot_record(record, *, published=False):
    """Business-scale observation only; never an episode-production prerequisite."""
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
