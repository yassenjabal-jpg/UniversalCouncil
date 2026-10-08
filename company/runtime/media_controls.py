class MediaControlError(ValueError):
    pass

REQUIRED_MEDIA_FUNCTIONS={
    "editorial_director",
    "ai_visual_post_producer",
    "audience_growth_packaging",
}

REQUIRED_PILOT_METRICS={
    "production_time_per_video",
    "owner_human_minutes_per_video",
    "tool_cost_per_video",
    "cost_per_published_minute",
    "revision_count",
    "factual_policy_defects",
    "packaging_quality",
}

PUBLISHED_PERFORMANCE_METRICS={
    "ctr",
    "first_30_second_retention",
    "average_percentage_viewed",
    "watch_time",
    "subscribers_per_video",
    "returning_viewers",
}

def validate_media_team(config):
    functions={f["id"]:f for f in config.get("production_functions",[])}
    missing=REQUIRED_MEDIA_FUNCTIONS-set(functions)
    if missing:
        raise MediaControlError(f"missing media functions: {sorted(missing)}")

    if functions["editorial_director"].get("default_status")!="ACTIVE_FOR_MEDIA_PILOT":
        raise MediaControlError("editorial director must be active for pilot")
    if functions["ai_visual_post_producer"].get("default_status")!="ACTIVE_FOR_MEDIA_PILOT":
        raise MediaControlError("visual/post producer must be active for pilot")
    if functions["audience_growth_packaging"].get("default_status") not in {"ON_DEMAND","ACTIVE_FOR_MEDIA_PILOT"}:
        raise MediaControlError("growth/packaging must be on-demand or active")

    pilot=config.get("pilot",{})
    if pilot.get("required_before_scale") is not True:
        raise MediaControlError("media pilot must be required before scale")
    if int(pilot.get("video_count",0))<3:
        raise MediaControlError("pilot must include at least 3 videos")
    return True

def validate_media_pilot_record(record, *, published=False):
    required={"videos_completed","metrics","hr_review_status","scale_decision"}
    missing=required-set(record)
    if missing:
        raise MediaControlError(f"media pilot record missing: {sorted(missing)}")

    if int(record["videos_completed"])<3:
        raise MediaControlError("scale decision forbidden before 3 completed pilot videos")

    metrics=set(record["metrics"])
    missing_metrics=REQUIRED_PILOT_METRICS-metrics
    if missing_metrics:
        raise MediaControlError(f"pilot metrics missing: {sorted(missing_metrics)}")

    if published:
        missing_published=PUBLISHED_PERFORMANCE_METRICS-metrics
        if missing_published:
            raise MediaControlError(f"published performance metrics missing: {sorted(missing_published)}")

    if record["hr_review_status"] not in {"KEEP","IMPROVEMENT_TRIAL","MERGE","REPLACE","REMOVE_WITHOUT_REPLACEMENT"}:
        raise MediaControlError("invalid HR media-team review status")

    if record["scale_decision"] not in {"HOLD","CONTINUE_PILOT","SCALE_CANDIDATE","REJECT"}:
        raise MediaControlError("invalid media scale decision")
    return True

def validate_media_scale_request(pilot_record):
    validate_media_pilot_record(pilot_record, published=False)
    if pilot_record["scale_decision"]!="SCALE_CANDIDATE":
        raise MediaControlError("media scale requires SCALE_CANDIDATE after pilot")
    return True
