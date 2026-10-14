from __future__ import annotations

from typing import Any


class MediaExecutionRecoveryError(ValueError):
    pass


VALID_HANDOFF_STATES = {
    "PLANNED",
    "APPLICATION_READY",
    "PROJECT_OPENED",
    "ACTION_DISPATCHED",
    "POSTCONDITION_VERIFIED",
    "CHECKPOINT_SAVED",
    "FAILED",
    "UNKNOWN",
}

REQUIRED_CHECKPOINT_FIELDS = {
    "episode_id",
    "stage_id",
    "action_id",
    "application",
    "application_version",
    "project_path",
    "artifact_or_project_version",
    "expected_postcondition",
    "last_verified_state",
    "next_safe_action",
}


def validate_execution_recovery_policy(policy: dict[str, Any]) -> bool:
    if not isinstance(policy, dict):
        raise MediaExecutionRecoveryError("execution recovery policy must be an object")
    if policy.get("policy_version") != "1.0":
        raise MediaExecutionRecoveryError("execution recovery policy must be version 1.0")
    for field in {
        "uses_hybrid_execution_journal",
        "checkpoint_required_before_application_handoff",
        "checkpoint_required_after_verified_state_change",
        "unknown_is_never_success",
    }:
        if policy.get(field) is not True:
            raise MediaExecutionRecoveryError(f"{field} must be true")
    if policy.get("replay_unknown_default") is not False:
        raise MediaExecutionRecoveryError("UNKNOWN actions must not replay by default")

    try:
        retry_limit = int(policy.get("same_route_retry_limit"))
    except (TypeError, ValueError) as exc:
        raise MediaExecutionRecoveryError("same-route retry limit must be an integer") from exc
    if retry_limit < 0 or retry_limit > 2:
        raise MediaExecutionRecoveryError("same-route retry limit must stay bounded to 0..2")

    states = set(policy.get("application_handoff_states", []))
    if states != VALID_HANDOFF_STATES:
        raise MediaExecutionRecoveryError("application handoff states drifted")

    checkpoint_fields = set(policy.get("required_checkpoint_fields", []))
    if not REQUIRED_CHECKPOINT_FIELDS.issubset(checkpoint_fields):
        raise MediaExecutionRecoveryError("application checkpoint contract is incomplete")

    sequence = policy.get("recovery_sequence", [])
    required_sequence = [
        "observe_current_application_state",
        "reconcile_journal_and_project_checkpoint",
        "resume_from_last_verified_checkpoint",
        "retry_same_route_once_if_idempotent_or_reversible",
        "use_authorized_fallback_tool_or_route",
        "hold_and_escalate_when_state_remains_unknown",
    ]
    if sequence != required_sequence:
        raise MediaExecutionRecoveryError("recovery sequence drifted")

    no_progress = policy.get("no_progress_policy", {})
    for field in {
        "detect_no_progress",
        "require_bounded_timeout",
        "capture_diagnostic_state",
        "do_not_repeat_blind_clicks",
    }:
        if no_progress.get(field) is not True:
            raise MediaExecutionRecoveryError("no-progress policy is incomplete")

    constraints = set(policy.get("fallback_constraints", []))
    required_constraints = {
        "fallback_must_preserve_task_intent",
        "fallback_must_be_authorized",
        "fallback_must_not_silently_reduce_quality_gate",
        "fallback_must_not_destroy_or_overwrite_unverified_work",
    }
    if not required_constraints.issubset(constraints):
        raise MediaExecutionRecoveryError("fallback constraints are incomplete")
    return True


def validate_handoff_checkpoint(checkpoint: dict[str, Any], policy: dict[str, Any]) -> bool:
    validate_execution_recovery_policy(policy)
    if not isinstance(checkpoint, dict):
        raise MediaExecutionRecoveryError("handoff checkpoint must be an object")
    missing = REQUIRED_CHECKPOINT_FIELDS - set(checkpoint)
    if missing:
        raise MediaExecutionRecoveryError(f"handoff checkpoint missing: {sorted(missing)}")
    for field in REQUIRED_CHECKPOINT_FIELDS:
        if checkpoint.get(field) in (None, ""):
            raise MediaExecutionRecoveryError(f"handoff checkpoint field is empty: {field}")
    state = str(checkpoint.get("state") or "CHECKPOINT_SAVED")
    if state not in VALID_HANDOFF_STATES:
        raise MediaExecutionRecoveryError("handoff checkpoint has invalid state")
    return True


def resolve_handoff_state(provider_state: str, *, postcondition_verified: bool) -> str:
    state = str(provider_state or "").upper()
    if state in {"FAILED", "ERROR", "BLOCKED"}:
        return "FAILED"
    if state in {"UNKNOWN", "TIMEOUT", "STALLED", ""}:
        return "UNKNOWN"
    if state in {"SUCCEEDED", "SUCCESS", "COMPLETED"}:
        return "POSTCONDITION_VERIFIED" if postcondition_verified else "UNKNOWN"
    return "UNKNOWN"


def next_recovery_action(
    handoff_state: str,
    *,
    retry_count: int,
    policy: dict[str, Any],
    authorized_fallback_available: bool = False,
) -> str:
    validate_execution_recovery_policy(policy)
    state = str(handoff_state or "").upper()
    if state in {"POSTCONDITION_VERIFIED", "CHECKPOINT_SAVED"}:
        return "COMPLETE"
    if state == "UNKNOWN":
        return "RECONCILE_JOURNAL_AND_PROJECT_CHECKPOINT"
    if state != "FAILED":
        raise MediaExecutionRecoveryError("recovery action requested for unsupported state")

    limit = int(policy["same_route_retry_limit"])
    if retry_count < 0:
        raise MediaExecutionRecoveryError("retry_count cannot be negative")
    if retry_count < limit:
        return "RESUME_CHECKPOINT_AND_RETRY_SAME_ROUTE"
    if authorized_fallback_available:
        return "USE_AUTHORIZED_FALLBACK"
    return "HOLD_AND_ESCALATE"
