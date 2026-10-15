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
    "human_assistance_pool",
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
    "human_assistance_requests",
    "human_assistance_minutes",
    "human_assistance_resolution_rate",
    "repeated_human_assistance_gap_count",
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
    if config.get("version") != "1.6":
        raise MediaControlError("media venture must be version 1.6")

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
    if functions["human_assistance_pool"].get("default_status") != "ON_DEMAND_ASSISTANCE":
        raise MediaControlError("human assistance pool must remain on-demand")

    model = config.get("operating_model", {})
    if model.get("mode") != "SMALL_CORE_ROUTED_CRAFT_CAPABILITIES":
        raise MediaControlError("studio operating model must use a small core with routed craft capabilities")
    if set(model.get("core_functions", [])) != CORE_FUNCTIONS:
        raise MediaControlError("studio core function set drifted")
    if set(model.get("mandatory_clearance_functions", [])) != MANDATORY_CLEARANCE_FUNCTIONS:
        raise MediaControlError("mandatory clearance function set drifted")
    if set(model.get("routed_craft_functions", [])) != ROUTED_CRAFT_FUNCTIONS:
        raise MediaControlError("routed craft function set drifted")
    if set(model.get("on_demand_functions", [])) != {"localization_producer", "human_assistance_pool"}:
        raise MediaControlError("on-demand function set drifted")
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
        "human_assistance_is_bounded_and_does_not_transfer_stage_or_publish_authority",
        "human_return_must_be_verified_before_resume",
    }
    if not required_independence.issubset(independence):
        raise MediaControlError("media function independence rules are incomplete")

    assistance = config.get("human_assistance", {})
    if assistance.get("enabled") is not True:
        raise MediaControlError("human assistance lane must be enabled")
    if assistance.get("mode") != "ON_DEMAND_BOUNDED_ASSISTANCE":
        raise MediaControlError("human assistance must remain bounded and on-demand")
    if assistance.get("coordinator") != "media_producer":
        raise MediaControlError("media producer must coordinate human assistance")
    triggers = set(assistance.get("trigger_conditions", []))
    required_triggers = {
        "automation_or_application_recovery_exhausted",
        "physical_world_action_required",
        "credential_or_login_step_required",
        "specialized_craft_capability_gap",
        "high_uncertainty_visual_or_audio_judgment",
        "material_domain_expertise_gap",
        "rights_or_source_confirmation_requires_human_contact",
        "human_intervention_is_materially_faster_and_lower_risk_than_further_automation",
    }
    if not required_triggers.issubset(triggers):
        raise MediaControlError("human assistance triggers are incomplete")
    packet = set(assistance.get("request_packet_required_fields", []))
    required_packet = {
        "request_id",
        "episode_id",
        "stage_id",
        "reason",
        "exact_human_task",
        "current_verified_state",
        "artifact_or_project_reference",
        "allowed_scope",
        "do_not_change",
        "expected_return_artifact_or_answer",
        "acceptance_criteria",
        "return_handoff",
    }
    if not required_packet.issubset(packet):
        raise MediaControlError("human assistance request packet is incomplete")
    constraints = set(assistance.get("constraints", []))
    required_constraints = {
        "request_only_the_minimum_human_action",
        "do_not_delegate_entire_stage_when_a_bounded_action_is_enough",
        "do_not_share_private_or_sensitive_material_without_authorization",
        "no_spend_subscription_or_purchase_without_owner_approval",
        "no_credentials_or_identity_use_without_owner_authorization",
        "human_helper_does_not_gain_publish_authority",
        "human_output_must_be_verified_before_rejoining_automated_flow",
        "record_reason_and_outcome_for_capability_learning",
    }
    if not required_constraints.issubset(constraints):
        raise MediaControlError("human assistance constraints are incomplete")
    resume = assistance.get("resume_policy", [])
    if resume != [
        "verify_human_return_against_acceptance_criteria",
        "save_checkpoint",
        "record_assistance_outcome",
        "resume_from_return_handoff",
        "do_not_repeat_completed_human_work",
    ]:
        raise MediaControlError("human assistance resume policy drifted")
    recurring = assistance.get("recurring_gap_policy", {})
    if int(recurring.get("repeated_same_gap_threshold", 0)) < 2:
        raise MediaControlError("recurring human-assistance gap threshold is too low or missing")
    if recurring.get("action") != "OPEN_CAPABILITY_REVIEW_FOR_TOOL_TRAINING_WORKFLOW_OR_STAFFING_FIX":
        raise MediaControlError("recurring human-assistance gap action drifted")

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
