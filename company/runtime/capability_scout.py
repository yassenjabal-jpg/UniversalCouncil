from datetime import datetime, timezone

TRIGGER_TYPES = {
    "CAPABILITY_UNAVAILABLE",
    "REPEATED_MANUAL_WORK",
    "RECURRING_TOOL_FAILURE",
    "EVIDENCE_CHANNEL_GAP",
    "REPEATED_HUMAN_HANDOFF",
    "SLOW_OR_HIGH_FRICTION_WORKFLOW",
    "DUPLICATE_TOOLING",
    "SECURITY_OR_COST_REGRESSION",
    "EXTERNAL_CAPABILITY_ADVANCE",
}

READ_ONLY_ACTIONS = {
    "DISCOVER",
    "COMPARE",
    "READ_DOCS",
    "INSPECT_PUBLIC_REPO",
    "SEARCH_COMMUNITY",
    "REVIEW_RELEASE_NOTES",
    "REVIEW_SECURITY_ADVISORIES",
}

OWNER_GATED_ACTIONS = {
    "INSTALL_TOOL",
    "CONNECT_CREDENTIALS",
    "AUTHENTICATE_ACCOUNT",
    "PURCHASE",
    "CHANGE_PERMISSIONS",
    "ENABLE_BROWSER_EXTENSION",
    "WRITE_EXTERNAL",
    "PUBLISH",
    "SEND_MESSAGE",
}

REQUIRED_CANDIDATE_FIELDS = (
    "gap_id",
    "candidate_name",
    "source_url_or_identifier",
    "capability_added",
    "existing_capability_overlap",
    "maintenance_signal",
    "license_or_terms",
    "install_or_connection_method",
    "permissions_required",
    "data_access",
    "external_write_capable",
    "cost_model",
    "security_risks",
    "rollback_plan",
    "sandbox_test",
    "success_metric",
    "kill_trigger",
    "version_or_commit_pin",
)

G0_DECISIONS = {
    "ADOPT",
    "ADAPT",
    "COMPOSE",
    "PILOT",
    "REJECT",
    "CUSTOM_BUILD_JUSTIFIED",
}

REQUIRED_G0_EVIDENCE_FIELDS = (
    "problem_statement",
    "official_or_maintainer_sources",
    "github_or_open_source_candidates",
    "specialist_community_evidence",
    "known_failure_modes",
    "existing_capability_overlap",
    "decision",
    "expected_custom_loc",
    "estimated_loc_avoided",
    "rollback_or_exit_plan",
)


def _parse_iso(value):
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc)
    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def should_open_gap(signal_type, repeat_count=1):
    if signal_type not in TRIGGER_TYPES:
        return False
    if signal_type == "REPEATED_MANUAL_WORK" and int(repeat_count) < 2:
        return False
    return True


def build_gap(gap_id, signal_type, summary, *, repeat_count=1, impact_metric=None):
    if not gap_id or not str(gap_id).strip():
        raise ValueError("gap_id is required")
    if not summary or not str(summary).strip():
        raise ValueError("summary is required")
    if not should_open_gap(signal_type, repeat_count):
        raise ValueError("signal does not meet capability-gap trigger")
    return {
        "id": str(gap_id),
        "status": "GAP_OPEN",
        "owner": "HR & Capability Director",
        "function": "Technology & Capability Scout",
        "signal_type": signal_type,
        "repeat_count": int(repeat_count),
        "summary": str(summary).strip(),
        "impact_metric": impact_metric,
    }


def build_evidence_channel_gap(gap_id, summary, *, impact_metric=None):
    return build_gap(
        gap_id,
        "EVIDENCE_CHANNEL_GAP",
        summary,
        impact_metric=impact_metric,
    )


def scouting_due(last_scan_at, now_at=None, *, active=True):
    now = _parse_iso(now_at or datetime.now(timezone.utc))
    if not last_scan_at:
        return True
    last = _parse_iso(last_scan_at)
    max_days = 7 if active else 30
    return (now - last).total_seconds() >= max_days * 86400


def hr_may_execute(action):
    return action in READ_ONLY_ACTIONS


def approval_gate_for(action):
    if action in READ_ONLY_ACTIONS:
        return "HR_READ_ONLY_DISCOVERY"
    if action in OWNER_GATED_ACTIONS:
        return "OWNER_APPROVAL_REQUIRED"
    return "COUNCIL_REVIEW_REQUIRED"


def validate_candidate(candidate):
    missing = [field for field in REQUIRED_CANDIDATE_FIELDS if field not in candidate]
    blockers = []

    if candidate.get("external_write_capable") and not candidate.get("write_boundary"):
        blockers.append("external write capability requires an explicit write boundary")

    permissions = candidate.get("permissions_required", [])
    if isinstance(permissions, str):
        permissions = [permissions]
    if any(x in permissions for x in ("cookies", "browser_debugger", "all_urls", "credentials")):
        if not candidate.get("isolation_plan"):
            blockers.append("sensitive browser/session permissions require an isolation plan")

    install = str(candidate.get("install_or_connection_method", "")).lower()
    pin = str(candidate.get("version_or_commit_pin", "")).strip()
    if install and any(token in install for token in ("main", "master", "latest")) and not pin:
        blockers.append("moving install target requires an explicit version or commit pin")

    if candidate.get("system_mutation") and not candidate.get("rollback_plan"):
        blockers.append("system mutation requires rollback plan")

    cost = candidate.get("cost_minor", 0)
    if cost is not None and int(cost) < 0:
        blockers.append("cost cannot be negative")

    ready = not missing and not blockers
    return {
        "ready_for_council_review": ready,
        "missing_fields": missing,
        "blockers": blockers,
        "next_gate": "SECURITY_REVIEW" if ready else "HR_DISCOVERY",
    }


def validate_g0_evidence(evidence):
    """Validate the mandatory Research / Reuse Before Build gate.

    G0 is renderer-, framework-, and project-agnostic. It does not select a
    technology; it proves that existing solutions and practitioner evidence
    were reviewed before custom implementation is allowed.
    """
    missing = [field for field in REQUIRED_G0_EVIDENCE_FIELDS if field not in evidence]
    blockers = []

    decision = str(evidence.get("decision", "")).strip().upper()
    if decision and decision not in G0_DECISIONS:
        blockers.append("decision must be one of the governed G0 decisions")

    for field in (
        "official_or_maintainer_sources",
        "github_or_open_source_candidates",
        "specialist_community_evidence",
        "known_failure_modes",
    ):
        if field in evidence and not evidence.get(field):
            blockers.append(f"{field} must contain evidence, not an empty placeholder")

    if decision == "CUSTOM_BUILD_JUSTIFIED":
        if not str(evidence.get("custom_build_justification", "")).strip():
            blockers.append("custom build requires explicit justification")
        if not evidence.get("rejected_alternatives"):
            blockers.append("custom build requires documented rejected alternatives")

    for field in ("expected_custom_loc", "estimated_loc_avoided"):
        if field in evidence:
            try:
                value = int(evidence[field])
            except (TypeError, ValueError):
                blockers.append(f"{field} must be a non-negative integer")
            else:
                if value < 0:
                    blockers.append(f"{field} must be a non-negative integer")

    passed = not missing and not blockers
    return {
        "g0_passed": passed,
        "missing_fields": missing,
        "blockers": blockers,
        "decision": decision or None,
        "next_gate": "ARCHITECTURE_AND_DUPLICATION_REVIEW" if passed else "G0_RESEARCH_REUSE",
    }
