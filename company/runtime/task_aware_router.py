from __future__ import annotations

from typing import Any


class TaskAwareRoutingError(ValueError):
    pass


def validate_task_router_config(cfg: dict[str, Any]) -> bool:
    if not isinstance(cfg, dict) or cfg.get("status") != "CANDIDATE_SHADOW_ONLY":
        raise TaskAwareRoutingError("task-aware router must remain candidate shadow-only")
    task_classes = cfg.get("task_classes")
    expected = {
        "visual_interaction",
        "structured_application",
        "host_work",
        "external_service",
        "recovery",
    }
    if not isinstance(task_classes, dict) or set(task_classes) != expected:
        raise TaskAwareRoutingError("task classes do not match canonical R14 contract")
    for task_class, spec in task_classes.items():
        order = spec.get("order")
        if not isinstance(order, list) or not order or len(order) != len(set(order)):
            raise TaskAwareRoutingError(f"{task_class}: route order must be non-empty and unique")
    if not str(cfg.get("route_version") or "").strip():
        raise TaskAwareRoutingError("route_version is required")
    required_restrictions = {
        "no_authority_expansion",
        "alternate_route_must_be_authorized",
        "physical_input_must_be_explicitly_bounded",
    }
    if not required_restrictions.issubset(set(cfg.get("fallback_restrictions", []))):
        raise TaskAwareRoutingError("canonical fallback restrictions are missing")
    return True


def _validate_contract_authority(request: dict[str, Any], contract: dict[str, Any]) -> dict[str, str]:
    if contract.get("execution_ready") is not True:
        raise TaskAwareRoutingError("ExecutionContract is not execution-ready")
    authority = contract.get("authority")
    if not isinstance(authority, dict):
        raise TaskAwareRoutingError("ExecutionContract authority is missing")
    operation = str(request.get("operation") or "")
    target = str(request.get("target") or "")
    scope = str(request.get("scope") or "")
    if operation not in authority.get("operations", []):
        raise TaskAwareRoutingError("router operation exceeds contract authority")
    if target not in authority.get("targets", []):
        raise TaskAwareRoutingError("router target exceeds contract authority")
    if scope not in authority.get("scopes", []):
        raise TaskAwareRoutingError("router scope exceeds contract authority")
    return {
        "principal": str(authority.get("principal") or ""),
        "operation": operation,
        "target": target,
        "scope": scope,
    }


def route_execution(
    request: dict[str, Any],
    contract: dict[str, Any],
    cfg: dict[str, Any],
) -> dict[str, Any]:
    validate_task_router_config(cfg)
    if not isinstance(request, dict):
        raise TaskAwareRoutingError("routing request must be an object")
    task_class = str(request.get("task_class") or "")
    if task_class not in cfg["task_classes"]:
        raise TaskAwareRoutingError(f"unknown task_class: {task_class}")

    authority = _validate_contract_authority(request, contract)
    available = request.get("available_routes")
    authorized = request.get("authorized_routes")
    if not isinstance(available, list) or not isinstance(authorized, list):
        raise TaskAwareRoutingError("available_routes and authorized_routes must be lists")
    available_set = {str(item) for item in available}
    authorized_set = {str(item) for item in authorized}

    fallback_reasons: list[str] = []
    route: str | None = None
    recovery_sequence: list[str] | None = None

    if task_class == "recovery":
        recovery = request.get("recovery")
        if not isinstance(recovery, dict):
            raise TaskAwareRoutingError("recovery context is required")
        if recovery.get("inspected") is not True:
            raise TaskAwareRoutingError("recovery alternate path requires Inspect first")
        if recovery.get("diagnosed") is not True:
            raise TaskAwareRoutingError("recovery alternate path requires Diagnose first")
        approved = recovery.get("approved_alternate_routes")
        if not isinstance(approved, list) or not approved:
            raise TaskAwareRoutingError("recovery requires an approved alternate route")
        for candidate in approved:
            candidate = str(candidate)
            if candidate in available_set and candidate in authorized_set:
                route = candidate
                break
        if route is None:
            raise TaskAwareRoutingError("no approved authorized recovery route is available")
        recovery_sequence = list(cfg["recovery_requires"])
    else:
        order = cfg["task_classes"][task_class]["order"]
        preferred = order[0]
        if preferred in available_set and preferred not in authorized_set:
            fallback_reasons.append("preferred_route_not_authorized")
        elif preferred not in available_set:
            fallback_reasons.append("preferred_route_unavailable")

        for candidate in order:
            if candidate not in available_set:
                continue
            if candidate not in authorized_set:
                continue
            if candidate == "bounded_physical_input" and request.get("allow_physical_input") is not True:
                fallback_reasons.append("physical_input_not_explicitly_bounded")
                continue
            route = candidate
            break
        if route is None:
            raise TaskAwareRoutingError("no available authorized route satisfies fallback restrictions")

    reason = f"{task_class}: selected first available authorized route within ExecutionContract authority"
    if fallback_reasons:
        reason += f"; fallback because {', '.join(fallback_reasons)}"
    if task_class == "recovery":
        reason += "; recovery alternate was explicitly inspected, diagnosed, and approved"

    result = {
        "task_class": task_class,
        "route": route,
        "route_reason": reason,
        "route_version": cfg["route_version"],
        "authority": authority,
        "fallback_restrictions": list(cfg["fallback_restrictions"]),
        "fallback_reasons": fallback_reasons,
        "shadow_only": True,
    }
    if recovery_sequence is not None:
        result["recovery_sequence"] = recovery_sequence
    return result
