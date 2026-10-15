from __future__ import annotations

from typing import Any


class StudioProductionLineError(ValueError):
    pass


TITLE_CARD_REQUIRED_FIELDS = {
    "id",
    "title",
    "why_now",
    "market_signal",
    "story_angle",
    "click_reason",
    "viewer_promise",
    "competition_level",
    "visual_potential",
    "evidence_feasibility",
    "eight_minute_story_feasibility",
    "risk_notes",
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

    candidates = packet.get("candidates", [])
    if len(candidates) != 3:
        raise StudioProductionLineError("exactly three title candidates are required")

    ids: set[str] = set()
    titles: set[str] = set()
    for candidate in candidates:
        missing = TITLE_CARD_REQUIRED_FIELDS - set(candidate)
        if missing:
            raise StudioProductionLineError(f"title card missing fields: {sorted(missing)}")
        candidate_id = str(candidate["id"]).strip()
        title = str(candidate["title"]).strip()
        if not candidate_id or not title:
            raise StudioProductionLineError("title candidate id and title must be non-empty")
        if candidate_id in ids:
            raise StudioProductionLineError("title candidate ids must be unique")
        if title.casefold() in titles:
            raise StudioProductionLineError("title candidates must be meaningfully distinct")
        ids.add(candidate_id)
        titles.add(title.casefold())
        if candidate.get("evidence_feasibility") != "PASS":
            raise StudioProductionLineError("every title candidate must be evidence-feasible")
        if candidate.get("eight_minute_story_feasibility") != "PASS":
            raise StudioProductionLineError("every title candidate must sustain the target long-form story")
        if candidate.get("visual_potential") not in {"MEDIUM", "HIGH"}:
            raise StudioProductionLineError("every title candidate needs adequate visual potential")

    return True


def validate_owner_title_lock(packet: dict[str, Any], selection: dict[str, Any]) -> bool:
    validate_title_candidate_packet(packet)
    if selection.get("authority") != "Owner":
        raise StudioProductionLineError("only Owner may lock the final title")
    if selection.get("status") != "OWNER_TITLE_LOCK":
        raise StudioProductionLineError("title selection must end in OWNER_TITLE_LOCK")
    selected_id = selection.get("selected_title_id")
    candidate_ids = {c["id"] for c in packet["candidates"]}
    if selected_id not in candidate_ids:
        raise StudioProductionLineError("selected title must be one of the three presented candidates")
    if not selection.get("locked_title"):
        raise StudioProductionLineError("locked title text is required")
    selected = next(c for c in packet["candidates"] if c["id"] == selected_id)
    if selection["locked_title"] != selected["title"]:
        raise StudioProductionLineError("locked title must match the selected candidate")
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
