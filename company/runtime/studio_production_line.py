from __future__ import annotations

from typing import Any


class StudioProductionLineError(ValueError):
    pass


ALLOWED_STORY_ARCHETYPES = {
    "mystery_investigation",
    "hidden_system",
    "human_odyssey",
    "engineering_impossibility",
    "rise_and_fall",
    "scam_or_heist",
    "survival_or_disaster",
    "transformation",
    "historical_paradox",
    "experiment_or_challenge",
}

TOPIC_CARD_REQUIRED_FIELDS = {
    "id",
    "topic",
    "story_premise",
    "story_archetype",
    "hero_anchor",
    "tension_or_mystery",
    "viewer_stakes",
    "why_now",
    "market_signal",
    "competition_level",
    "key_visual",
    "thumbnail_hypothesis",
    "visual_potential",
    "evidence_feasibility",
    "eight_minute_story_feasibility",
    "risk_notes",
    "title_variants",
}

THUMBNAIL_HYPOTHESIS_REQUIRED_FIELDS = {
    "hero_subject",
    "visual_tension",
    "composition",
    "text_0_4_words",
    "works_without_explanatory_text",
}

TITLE_VARIANT_REQUIRED_FIELDS = {
    "id",
    "title",
    "click_reason",
    "viewer_promise",
    "thumbnail_complement",
    "stranger_click_test",
    "youtube_title_style_status",
}

SCRIPT_LOCK_PASS_STATUSES = {
    "owner_title_lock_status",
    "story_question_status",
    "research_pack_status",
    "story_architecture_status",
    "hook_retention_map_status",
    "first_script_status",
    "youtube_editorial_rewrite_status",
    "visual_narrative_pass_status",
    "independent_fact_check_status",
    "voice_narration_rewrite_status",
    "red_team_retention_review_status",
    "first_30_second_retention_status",
    "anti_article_test_status",
    "spoken_language_test_status",
    "cold_viewer_test_status",
    "visual_beat_map_status",
    "open_loop_map_status",
    "filler_check_status",
}

FIRST_30_SECONDS_REQUIRED_FIELDS = {
    "hook",
    "central_mystery",
    "concrete_visual",
    "title_payoff_bridge",
    "background_exposition_before_hook",
    "status",
}

RETENTION_BEAT_REQUIRED_FIELDS = {
    "start_sec",
    "end_sec",
    "narrative_function",
    "reason_to_continue",
    "visual_beat",
    "open_loop_action",
}

ALLOWED_NARRATIVE_FUNCTIONS = {
    "HOOK",
    "SETUP",
    "ESCALATION",
    "REVEAL",
    "PAYOFF",
    "RESET",
}

DROPOFF_RISK_REQUIRED_FIELDS = {
    "time_sec",
    "risk",
    "correction",
    "status",
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
    if packet.get("youtube_native_discovery_status") != "PASS":
        raise StudioProductionLineError("YouTube-native discovery must pass before Owner Title Gate")
    if packet.get("discovery_evidence_mode") not in {"FULL", "AUTHORIZED_NATIVE_FALLBACK"}:
        raise StudioProductionLineError("degraded discovery evidence requires HOLD before Owner Title Gate")
    if packet.get("packaging_hypothesis_status") != "PASS":
        raise StudioProductionLineError("packaging hypothesis must pass before title candidates")
    if packet.get("red_team_click_challenge_status") != "PASS":
        raise StudioProductionLineError("Red Team stranger-click challenge must pass before Owner Title Gate")

    topics = packet.get("topics", [])
    if len(topics) != 3:
        raise StudioProductionLineError("exactly three distinct topic candidates are required")

    topic_ids: set[str] = set()
    topic_names: set[str] = set()
    story_archetypes: set[str] = set()
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

        for field in {
            "story_premise",
            "hero_anchor",
            "tension_or_mystery",
            "viewer_stakes",
            "key_visual",
        }:
            if not str(topic_card.get(field, "")).strip():
                raise StudioProductionLineError(f"topic card {field} must be non-empty")

        story_archetype = str(topic_card["story_archetype"]).strip()
        if story_archetype not in ALLOWED_STORY_ARCHETYPES:
            raise StudioProductionLineError("topic uses an unsupported story archetype")
        if story_archetype in story_archetypes:
            raise StudioProductionLineError("the three topics must use distinct story archetypes")
        story_archetypes.add(story_archetype)

        thumbnail = topic_card.get("thumbnail_hypothesis")
        if not isinstance(thumbnail, dict):
            raise StudioProductionLineError("thumbnail hypothesis must be a structured object")
        thumbnail_missing = THUMBNAIL_HYPOTHESIS_REQUIRED_FIELDS - set(thumbnail)
        if thumbnail_missing:
            raise StudioProductionLineError(f"thumbnail hypothesis missing fields: {sorted(thumbnail_missing)}")
        for field in {"hero_subject", "visual_tension", "composition"}:
            if not str(thumbnail.get(field, "")).strip():
                raise StudioProductionLineError(f"thumbnail hypothesis {field} must be non-empty")
        thumbnail_text = thumbnail.get("text_0_4_words")
        if not isinstance(thumbnail_text, str) or len(thumbnail_text.split()) > 4:
            raise StudioProductionLineError("thumbnail text must contain zero to four words")
        if thumbnail.get("works_without_explanatory_text") is not True:
            raise StudioProductionLineError("thumbnail must work without explanatory copy")

        variants = topic_card.get("title_variants", [])
        if len(variants) != 2:
            raise StudioProductionLineError("each topic must contain exactly two title variants")
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
            if not str(variant.get("click_reason", "")).strip():
                raise StudioProductionLineError("title variant click reason must be non-empty")
            if not str(variant.get("viewer_promise", "")).strip():
                raise StudioProductionLineError("title variant viewer promise must be non-empty")
            if not str(variant.get("thumbnail_complement", "")).strip():
                raise StudioProductionLineError("title must explain how it complements the thumbnail")
            if variant.get("stranger_click_test") != "PASS":
                raise StudioProductionLineError("every title must pass the stranger-click test")
            if variant.get("youtube_title_style_status") != "PASS":
                raise StudioProductionLineError("article-like titles cannot reach Owner Title Gate")
            title_ids.add(title_id)
            titles.add(title.casefold())

        if topic_card.get("evidence_feasibility") != "PASS":
            raise StudioProductionLineError("every topic candidate must be evidence-feasible")
        if topic_card.get("eight_minute_story_feasibility") != "PASS":
            raise StudioProductionLineError("every topic candidate must sustain the target long-form story")
        if topic_card.get("visual_potential") != "HIGH":
            raise StudioProductionLineError("every topic candidate needs high visual potential")

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


def validate_script_lock_packet(packet: dict[str, Any]) -> bool:
    required_refs = {
        "locked_title",
        "script_title",
        "owner_title_lock_ref",
        "claim_source_sheet_ref",
        "retention_map_ref",
        "visual_beat_map_ref",
        "script_ref",
    }
    missing_refs = required_refs - set(packet)
    if missing_refs:
        raise StudioProductionLineError(f"script lock packet missing references: {sorted(missing_refs)}")
    for field in required_refs:
        if not isinstance(packet.get(field), str) or not packet[field].strip():
            raise StudioProductionLineError(f"script lock field {field} must be non-empty")
    if packet["script_title"] != packet["locked_title"]:
        raise StudioProductionLineError("script title must match the Owner-locked title")

    for status_field in SCRIPT_LOCK_PASS_STATUSES:
        if packet.get(status_field) != "PASS":
            raise StudioProductionLineError(f"Script Lock requires {status_field}=PASS")
    if packet.get("script_lock_status") != "SCRIPT_LOCK":
        raise StudioProductionLineError("final script status must be SCRIPT_LOCK")

    first_30 = packet.get("first_30_seconds")
    if not isinstance(first_30, dict):
        raise StudioProductionLineError("first 30 seconds must be a structured object")
    missing_first_30 = FIRST_30_SECONDS_REQUIRED_FIELDS - set(first_30)
    if missing_first_30:
        raise StudioProductionLineError(f"first 30 seconds missing: {sorted(missing_first_30)}")
    for field in {"hook", "central_mystery", "concrete_visual", "title_payoff_bridge"}:
        if not isinstance(first_30.get(field), str) or not first_30[field].strip():
            raise StudioProductionLineError(f"first 30 seconds {field} must be non-empty")
    if first_30.get("background_exposition_before_hook") is not False:
        raise StudioProductionLineError("background exposition cannot precede the hook")
    if first_30.get("status") != "PASS":
        raise StudioProductionLineError("first 30 seconds must pass the retention gate")

    beats = packet.get("retention_beats")
    if not isinstance(beats, list) or not beats:
        raise StudioProductionLineError("retention beat map is required")
    previous_end = 0.0
    functions_used: set[str] = set()
    for index, beat in enumerate(beats):
        if not isinstance(beat, dict):
            raise StudioProductionLineError("every retention beat must be structured")
        missing = RETENTION_BEAT_REQUIRED_FIELDS - set(beat)
        if missing:
            raise StudioProductionLineError(f"retention beat missing fields: {sorted(missing)}")
        start = beat.get("start_sec")
        end = beat.get("end_sec")
        if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
            raise StudioProductionLineError("retention beat times must be numeric")
        if start != previous_end:
            raise StudioProductionLineError("retention beat map must cover the script without gaps")
        if end <= start:
            raise StudioProductionLineError("retention beat end must follow start")
        if end - start > 90:
            raise StudioProductionLineError("no script interval may exceed 90 seconds without a new reason to continue")
        narrative_function = beat.get("narrative_function")
        if narrative_function not in ALLOWED_NARRATIVE_FUNCTIONS:
            raise StudioProductionLineError("retention beat uses an invalid narrative function")
        functions_used.add(narrative_function)
        for field in {"reason_to_continue", "visual_beat", "open_loop_action"}:
            if not isinstance(beat.get(field), str) or not beat[field].strip():
                raise StudioProductionLineError(f"retention beat {field} must be non-empty")
        previous_end = end

    if previous_end < 480:
        raise StudioProductionLineError("locked long-form script must cover at least eight minutes")
    if not {"HOOK", "REVEAL", "PAYOFF"}.issubset(functions_used):
        raise StudioProductionLineError("retention map must contain hook, reveal and payoff functions")

    if packet.get("filler_segments_detected") != 0:
        raise StudioProductionLineError("Script Lock forbids unresolved filler segments")
    if packet.get("article_like_paragraphs_remaining") != 0:
        raise StudioProductionLineError("Script Lock forbids article-like paragraphs")
    if packet.get("unsourced_material_claims_remaining") != 0:
        raise StudioProductionLineError("Script Lock forbids unsourced material claims")

    risks = packet.get("red_team_dropoff_risks")
    if not isinstance(risks, list) or not risks:
        raise StudioProductionLineError("Red Team must record drop-off risks before Script Lock")
    for risk in risks:
        if not isinstance(risk, dict):
            raise StudioProductionLineError("drop-off risk must be structured")
        missing = DROPOFF_RISK_REQUIRED_FIELDS - set(risk)
        if missing:
            raise StudioProductionLineError(f"drop-off risk missing fields: {sorted(missing)}")
        if risk.get("status") != "RESOLVED":
            raise StudioProductionLineError("all Red Team drop-off risks must be resolved")
        if not isinstance(risk.get("time_sec"), (int, float)) or risk["time_sec"] < 0:
            raise StudioProductionLineError("drop-off risk time must be a non-negative number")
        for field in {"risk", "correction"}:
            if not isinstance(risk.get(field), str) or not risk[field].strip():
                raise StudioProductionLineError(f"drop-off risk {field} must be non-empty")

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
