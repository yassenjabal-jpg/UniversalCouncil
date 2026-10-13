from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class ToolAuthorityError(ValueError):
    pass


REQUIRED_FIELDS = {
    "id",
    "provider",
    "operation",
    "classification",
    "evidence_level",
    "authentication_class",
    "effect",
    "approval_policy",
    "allowed_scope",
    "prohibited_scope",
    "last_verified_at",
    "review_trigger",
    "source_or_pin",
    "enforcement",
}

EVIDENCE_LEVELS = {
    "ADVERTISED",
    "METADATA_OBSERVED",
    "BYTES_VERIFIED",
    "SCRIPT_TESTED",
    "HOST_INVOKED",
    "BOUNDARY_ENFORCED",
}

AUTHORITY_ENUMS = {
    "classification": {"AVAILABLE", "OWNER_GATED", "BLOCKED", "UNAVAILABLE", "ADMIN_BLOCKED"},
    "authentication_class": {"CONNECTED_APP", "HOST_SESSION", "PUBLIC_ONLY", "AUTHENTICATED", "NONE"},
    "effect": {"READ", "WRITE", "EXECUTE"},
    "approval_policy": {"READ_ALLOWED", "ASK_BEFORE_WRITE", "OWNER_EXPLICIT", "BLOCKED"},
    "enforcement": {"CONNECTOR_POLICY", "POLICY_ENFORCED_ONLY", "GATEWAY_ENFORCED"},
}

EVIDENCE_STATES = {"HISTORICAL", "CURRENT_VERIFIED", "STALE", "REVOKED"}

EVIDENCE_MAX_AGE_DAYS = {
    "ADVERTISED": 7,
    "METADATA_OBSERVED": 14,
    "BYTES_VERIFIED": 30,
    "SCRIPT_TESTED": 14,
    "HOST_INVOKED": 7,
    "BOUNDARY_ENFORCED": 30,
}

MINIMUM_OPERATIONS = {
    "github.read",
    "github.write",
    "github.merge",
    "memory.github_sync",
    "linear.read",
    "linear.write",
    "remote_shell.read",
    "remote_shell.execute",
    "desktop_computer_use.observe",
    "desktop_computer_use.control",
    "agent_reach.public_read",
    "browser.authenticated",
    "external.publish",
}


def validate_registry(cfg: dict[str, Any]) -> bool:
    if cfg.get("version") != "1.0":
        raise ToolAuthorityError("tool authority registry must be version 1.0")
    records = cfg.get("capabilities")
    if not isinstance(records, list):
        raise ToolAuthorityError("capabilities must be a list")

    ids: set[str] = set()
    operations: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ToolAuthorityError(f"capability {index} must be an object")
        missing = REQUIRED_FIELDS - set(record)
        if missing:
            raise ToolAuthorityError(f"{record.get('operation', index)} missing fields: {sorted(missing)}")
        capability_id = record["id"]
        operation = record["operation"]
        if capability_id in ids:
            raise ToolAuthorityError(f"duplicate capability id: {capability_id}")
        if operation in operations:
            raise ToolAuthorityError(f"duplicate operation: {operation}")
        ids.add(capability_id)
        operations.add(operation)

        if record["evidence_level"] not in EVIDENCE_LEVELS:
            raise ToolAuthorityError(f"{operation}: unknown evidence level")
        for field, allowed_values in AUTHORITY_ENUMS.items():
            if record[field] not in allowed_values:
                raise ToolAuthorityError(f"{operation}: unknown {field}")
        if record["effect"] in {"WRITE", "EXECUTE"}:
            if record["approval_policy"] == "READ_ALLOWED":
                raise ToolAuthorityError(f"{operation}: write/execute cannot be READ_ALLOWED")
            if not isinstance(record["prohibited_scope"], list) or not record["prohibited_scope"]:
                raise ToolAuthorityError(f"{operation}: write/execute requires prohibited scope")
        if record["enforcement"] == "POLICY_ENFORCED_ONLY" and record["evidence_level"] == "BOUNDARY_ENFORCED":
            raise ToolAuthorityError(f"{operation}: policy-only enforcement cannot claim boundary evidence")
        try:
            datetime.fromisoformat(str(record["last_verified_at"]))
        except ValueError as exc:
            raise ToolAuthorityError(f"{operation}: invalid last_verified_at") from exc
        for constraint_name in ("allowed_targets", "allowed_principals", "allowed_action_scopes"):
            values = record.get(constraint_name)
            if values is not None:
                if not isinstance(values, list) or not values:
                    raise ToolAuthorityError(f"{operation}: {constraint_name} must be a non-empty list")
                if not all(isinstance(item, str) and item.strip() for item in values):
                    raise ToolAuthorityError(f"{operation}: {constraint_name} must contain non-empty strings")
        max_age = record.get("max_evidence_age_days")
        if max_age is not None and (not isinstance(max_age, int) or max_age < 1):
            raise ToolAuthorityError(f"{operation}: max_evidence_age_days must be a positive integer")
        evidence_state = record.get("evidence_state")
        if evidence_state is not None:
            if evidence_state not in EVIDENCE_STATES:
                raise ToolAuthorityError(f"{operation}: unknown evidence_state")
            historical = record.get("historical_capability")
            current = record.get("current_verified_capability")
            if not isinstance(historical, dict):
                raise ToolAuthorityError(f"{operation}: evidence_state requires historical_capability metadata")
            if evidence_state == "CURRENT_VERIFIED" and not isinstance(current, dict):
                raise ToolAuthorityError(f"{operation}: CURRENT_VERIFIED requires current_verified_capability metadata")
            if evidence_state != "CURRENT_VERIFIED" and current is not None:
                raise ToolAuthorityError(f"{operation}: non-current evidence cannot populate current_verified_capability")

    missing_operations = MINIMUM_OPERATIONS - operations
    if missing_operations:
        raise ToolAuthorityError(f"missing required operations: {sorted(missing_operations)}")

    authenticated = get_capability(cfg, "browser.authenticated")
    if authenticated["classification"] != "BLOCKED" or authenticated["approval_policy"] != "BLOCKED":
        raise ToolAuthorityError("authenticated browser must remain blocked in v1")

    publish = get_capability(cfg, "external.publish")
    if publish["classification"] != "BLOCKED" and publish["approval_policy"] != "OWNER_EXPLICIT":
        raise ToolAuthorityError("external publish must be blocked or owner-gated")

    agent_reach = get_capability(cfg, "agent_reach.public_read")
    if agent_reach["authentication_class"] != "PUBLIC_ONLY" or agent_reach["effect"] != "READ":
        raise ToolAuthorityError("Agent Reach public read must remain PUBLIC_ONLY / READ")

    return True


def capability_dimensions(
    record: dict[str, Any],
    *,
    as_of: datetime | None = None,
) -> dict[str, Any]:
    classification = str(record.get("classification", "UNAVAILABLE"))
    availability = (
        "UNAVAILABLE"
        if classification in {"UNAVAILABLE", "ADMIN_BLOCKED"}
        else "AVAILABLE"
    )
    currentness = capability_currentness(record, as_of=as_of)
    return {
        "availability": availability,
        "authority": classification,
        "historical_capability": bool(
            record.get("historical_capability")
            or record.get("evidence_receipt")
            or record.get("source_or_pin")
        ),
        "current_verified_capability": bool(currentness.get("current")),
        "currentness_reason": currentness.get("reason"),
    }


def capability_currentness(
    record: dict[str, Any],
    *,
    as_of: datetime | None = None,
) -> dict[str, Any]:
    as_of = as_of or datetime.now(timezone.utc)
    if as_of.tzinfo is None:
        raise ToolAuthorityError("as_of must be timezone-aware")
    evidence_state = record.get("evidence_state")
    if evidence_state is not None and evidence_state != "CURRENT_VERIFIED":
        reasons = {
            "HISTORICAL": "historical_capability_only",
            "STALE": "stale_capability_evidence",
            "REVOKED": "revoked_capability_evidence",
        }
        return {
            "current": False,
            "reason": reasons.get(str(evidence_state), "non_current_capability_evidence"),
            "age_days": None,
        }
    if evidence_state == "CURRENT_VERIFIED":
        metadata = record.get("current_verified_capability")
        if not isinstance(metadata, dict):
            return {"current": False, "reason": "missing_current_capability_metadata", "age_days": None}
        expires_at = metadata.get("expires_at")
        if expires_at:
            try:
                expiry = datetime.fromisoformat(str(expires_at))
            except ValueError:
                return {"current": False, "reason": "invalid_capability_expiry", "age_days": None}
            if expiry.tzinfo is None:
                return {"current": False, "reason": "invalid_capability_expiry", "age_days": None}
            if as_of.astimezone(timezone.utc) > expiry.astimezone(timezone.utc):
                return {"current": False, "reason": "expired_capability_evidence", "age_days": None}
    try:
        verified = datetime.fromisoformat(str(record["last_verified_at"]))
    except ValueError:
        return {"current": False, "reason": "invalid_last_verified_at", "age_days": None}
    if verified.tzinfo is None:
        verified = verified.replace(tzinfo=timezone.utc)
    else:
        verified = verified.astimezone(timezone.utc)
    age_days = (as_of.astimezone(timezone.utc) - verified).total_seconds() / 86400.0
    if age_days < -1:
        return {"current": False, "reason": "future_verification_timestamp", "age_days": age_days}
    maximum = int(
        record.get(
            "max_evidence_age_days",
            EVIDENCE_MAX_AGE_DAYS.get(str(record.get("evidence_level")), 14),
        )
    )
    if age_days > maximum:
        return {
            "current": False,
            "reason": "stale_capability_evidence",
            "age_days": age_days,
            "max_age_days": maximum,
        }
    return {
        "current": True,
        "reason": "current",
        "age_days": age_days,
        "max_age_days": maximum,
    }


def get_capability(cfg: dict[str, Any], operation: str) -> dict[str, Any]:
    for record in cfg.get("capabilities", []):
        if record.get("operation") == operation:
            return record
    raise ToolAuthorityError(f"unknown operation: {operation}")


def requires_explicit_approval(record: dict[str, Any]) -> bool:
    return record.get("approval_policy") != "READ_ALLOWED"
