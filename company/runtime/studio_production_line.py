from __future__ import annotations

from typing import Any


class StudioProductionLineError(ValueError):
    pass


TOPIC_CARD_REQUIRED_FIELDS = {
    "id",
    "topic",
    "why_now",
    "market_signal",
    "story_angle",
    "competition_level",
    "visual_potential",
    "evidence_feasibility",
    "eight_minute_story_feasibility",
    "risk_notes",
    "title_variants",
}

TITLE_VARIANT_REQUIRED_FIELDS = {
    "id",
    "title",
    "click_reason",
    "viewer_promise",
}

PHASE_SEQUENCE = ["writing", "pre_production", "production"]

HANDOFF_STATUSES = {
    "READY_FOR_REVIEW",
    "ACCEPTED",
    "REJECTED_RETURN_TO_SOURCE",
}


def validate_title_candidate_packet(packet: dict[str, Any]) -> bool:
    if packet.get("market_scan_status") != "PASS":
        raise StudioProductionLineError("market scan must pass before title candidates")
    if packet.get("social_trend_scan_status") != "PASS":
        raise StudioProductionLineError("social trend scan must pass before title candidates")
    if packet.get("story_feasibility_status") != "PASS":
        raise StudioProductionLineError("story feasibility must pass before title candidates")

    topics = packet.get("topics", [])
    if len(topics) != 3:
        raise StudioProductionLineError("exactly three distinct topic candidates are required")

    topic_ids: set[str] = set()
    topic_names: set[str] = set()
    title_ids: set[str] = set()
    titles: set[str] = set()
    for topic_card in topics:
        missing = TOPIC_CARD_REQUIRED_FIELDS - set(topic_card)
        if missing:
            raise StudioProductionLineError(f"topic card missing fields: {sorted(missing)}")
        topic_id = str(topic_card["id"]).strip()
        topic_name = str(topic_card["topic"]).strip()
        if not topic_id or not topic_name:
            raise StudioProductionLineError("topic candidate id and topic must be non-empty")
        if topic_id in topic_ids:
            raise StudioProductionLineError("topic candidate ids must be unique")
        if topic_name.casefold() in topic_names:
            raise StudioProductionLineError("the three topic candidates must be meaningfully distinct")
        topic_ids.add(topic_id)
        topic_names.add(topic_name.casefold())

        variants = topic_card.get("title_variants", [])
        if len(variants) != 2:
            raise StudioProductionLineError("each topic must contain exactly two title variants")
        local_titles: set[str] = set()
        for variant in variants:
            variant_missing = TITLE_VARIANT_REQUIRED_FIELDS - set(variant)
            if variant_missing:
                raise StudioProductionLineError(f"title variant missing fields: {sorted(variant_missing)}")
            title_id = str(variant["id"]).strip()
            title = str(variant["title"]).strip()
            if not title_id or not title:
                raise StudioProductionLineError("title variant id and title must be non-empty")
            if title_id in title_ids:
                raise StudioProductionLineError("title variant ids must be globally unique")
            if title.casefold() in titles:
                raise StudioProductionLineError("all presented title variants must be distinct")
            if title.casefold() in local_titles:
                raise StudioProductionLineError("the two title variants for a topic must be distinct")
            title_ids.add(title_id)
            titles.add(title.casefold())
            local_titles.add(title.casefold())

        if topic_card.get("evidence_feasibility") != "PASS":
            raise StudioProductionLineError("every topic candidate must be evidence-feasible")
        if topic_card.get("eight_minute_story_feasibility") != "PASS":
            raise StudioProductionLineError("every topic candidate must sustain the target long-form story")
        if topic_card.get("visual_potential") not in {"MEDIUM", "HIGH"}:
            raise StudioProductionLineError("every topic candidate needs adequate visual potential")

    return True


def validate_owner_title_lock(packet: dict[str, Any], selection: dict[str, Any]) -> bool:
    validate_title_candidate_packet(packet)
    if selection.get("authority") != "Owner":
        raise StudioProductionLineError("only Owner may lock the final title")
    if selection.get("status") != "OWNER_TITLE_LOCK":
        raise StudioProductionLineError("title selection must end in OWNER_TITLE_LOCK")
    selected_topic_id = selection.get("selected_topic_id")
    selected_title_id = selection.get("selected_title_id")
    selected_topic = next((t for t in packet["topics"] if t["id"] == selected_topic_id), None)
    if selected_topic is None:
        raise StudioProductionLineError("selected topic must be one of the three presented topics")
    selected_title = next(
        (v for v in selected_topic["title_variants"] if v["id"] == selected_title_id),
        None,
    )
    if selected_title is None:
        raise StudioProductionLineError("selected title must be one of the two variants for the selected topic")
    if not selection.get("locked_topic") or not selection.get("locked_title"):
        raise StudioProductionLineError("locked topic and title text are required")
    if selection["locked_topic"] != selected_topic["topic"]:
        raise StudioProductionLineError("locked topic must match the selected topic")
    if selection["locked_title"] != selected_title["title"]:
        raise StudioProductionLineError("locked title must match the selected title variant")
    return True


def validate_title_revision_request(request: dict[str, Any]) -> bool:
    required = {"current_title", "proposed_title", "reason", "evidence", "impact_on_script_or_packaging"}
    missing = required - set(request)
    if missing:
        raise StudioProductionLineError(f"title revision request missing: {sorted(missing)}")
    if request.get("owner_reapproval_status") != "APPROVED":
        raise StudioProductionLineError("locked title revision requires explicit Owner reapproval")
    return True


def validate_phase_transition(current_phase: str, target_phase: str, state: dict[str, Any]) -> bool:
    if current_phase not in PHASE_SEQUENCE or target_phase not in PHASE_SEQUENCE:
        raise StudioProductionLineError("unknown studio phase")
    if PHASE_SEQUENCE.index(target_phase) != PHASE_SEQUENCE.index(current_phase) + 1:
        raise StudioProductionLineError("phase skipping or reverse transition is forbidden")

    if current_phase == "writing" and target_phase == "pre_production":
        if state.get("owner_title_lock") is not True:
            raise StudioProductionLineError("Owner Title Lock required before pre-production")
        if state.get("script_lock") is not True:
            raise StudioProductionLineError("Script Lock required before pre-production")

    if current_phase == "pre_production" and target_phase == "production":
        if state.get("production_ready_lock") is not True:
            raise StudioProductionLineError("Production Ready Lock required before production")

    return True


def validate_stage_record(stage: dict[str, Any]) -> bool:
    required = {"stage_id", "program", "status", "output_ref", "checkpoint_ref"}
    missing = required - set(stage)
    if missing:
        raise StudioProductionLineError(f"stage record missing: {sorted(missing)}")
    if not isinstance(stage.get("program"), str) or not stage["program"].strip():
        raise StudioProductionLineError("stage must name exactly one primary program")
    if stage.get("secondary_craft_programs"):
        raise StudioProductionLineError("a stage cannot use a simultaneous second craft program")
    if stage.get("status") != "VERIFIED_COMPLETE":
        raise StudioProductionLineError("stage cannot exit before verified completion")
    return True


def validate_department_handoff(handoff: dict[str, Any]) -> bool:
    required = {
        "project_id",
        "handoff_id",
        "from_department",
        "to_department",
        "completed_stage_ids",
        "artifact_manifest",
        "locked_artifacts",
        "change_log",
        "known_limitations",
        "qc_result",
        "acceptance_criteria",
        "checkpoint_ref",
        "handoff_status",
    }
    missing = required - set(handoff)
    if missing:
        raise StudioProductionLineError(f"handoff missing: {sorted(missing)}")
    if handoff["handoff_status"] not in HANDOFF_STATUSES:
        raise StudioProductionLineError("invalid handoff status")
    if handoff["handoff_status"] == "ACCEPTED" and handoff.get("qc_result") != "PASS":
        raise StudioProductionLineError("handoff cannot be accepted without QC PASS")
    return True


def validate_return_ticket(ticket: dict[str, Any]) -> bool:
    required = {
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
    missing = required - set(ticket)
    if missing:
        raise StudioProductionLineError(f"return ticket missing: {sorted(missing)}")
    if ticket["source_department"] == ticket["detecting_department"]:
        raise StudioProductionLineError("return ticket must identify a distinct source department")
    return True
