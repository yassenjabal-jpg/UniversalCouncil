from __future__ import annotations

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

MINIMUM_OPERATIONS = {
    "github.read",
    "github.write",
    "github.merge",
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


def get_capability(cfg: dict[str, Any], operation: str) -> dict[str, Any]:
    for record in cfg.get("capabilities", []):
        if record.get("operation") == operation:
            return record
    raise ToolAuthorityError(f"unknown operation: {operation}")


def requires_explicit_approval(record: dict[str, Any]) -> bool:
    return record.get("approval_policy") != "READ_ALLOWED"
