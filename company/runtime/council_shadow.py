from __future__ import annotations

from typing import Any


class CouncilShadowError(ValueError):
    pass


def validate_shadow_config(cfg: dict[str, Any], roles: dict[str, Any]) -> bool:
    if not isinstance(cfg, dict):
        raise CouncilShadowError("Council Shadow config must be an object")
    if cfg.get("status") != "CANDIDATE_SHADOW_ONLY":
        raise CouncilShadowError("Council Shadow must remain candidate-only")
    if cfg.get("governing_council_version") != roles.get("version"):
        raise CouncilShadowError("Council Shadow governing version must match current governing Council")
    for field in ("may_replace_governing_council", "may_execute_tools", "may_mutate_authority"):
        if cfg.get(field) is not False:
            raise CouncilShadowError(f"{field} must remain false")

    core_ids = {item["id"] for item in roles.get("core_roles", [])}
    specialist_ids = {item["id"] for item in roles.get("specialist_roles", [])}
    callable_core = set(cfg.get("callable_core_capabilities", []))
    if not callable_core or not callable_core.issubset(core_ids):
        raise CouncilShadowError("callable core capabilities must exist in governing v0.3 roles")
    if "synthesis" in callable_core:
        raise CouncilShadowError("synthesis must remain a protocol stage in the shadow candidate")
    if "synthesis" not in set(cfg.get("protocol_stages", [])):
        raise CouncilShadowError("synthesis protocol stage is required")

    mandatory = set(cfg.get("commercial_mandatory_specialists", []))
    if mandatory != {"customer_skeptic", "moat_auditor"}:
        raise CouncilShadowError("commercial shadow must preserve Customer Skeptic and Moat Auditor")
    if not mandatory.issubset(specialist_ids):
        raise CouncilShadowError("commercial mandatory specialists must exist in governing roles")

    orchestrator = cfg.get("decision_orchestrator", {})
    if orchestrator.get("coordinates") != ["chair"]:
        raise CouncilShadowError("Decision Orchestrator may coordinate Chair only in R9 shadow")
    if orchestrator.get("protocol_stages") != ["synthesis"]:
        raise CouncilShadowError("Decision Orchestrator must preserve synthesis as a protocol stage")
    if orchestrator.get("cannot_override_domain_blockers") is not True:
        raise CouncilShadowError("domain blockers must remain protected")
    if orchestrator.get("cannot_erase_dissent") is not True:
        raise CouncilShadowError("dissent must remain protected")
    return True


def _matched_routes(signals: set[str], routing: dict[str, Any]) -> list[dict[str, Any]]:
    matched: list[dict[str, Any]] = []
    for route in routing.get("routes", []):
        route_signals = {str(item).lower() for item in route.get("signals", [])}
        if signals & route_signals:
            matched.append(route)
    return matched


def build_shadow_plan(
    decision: dict[str, Any],
    cfg: dict[str, Any],
    roles: dict[str, Any],
    routing: dict[str, Any],
) -> dict[str, Any]:
    validate_shadow_config(cfg, roles)
    decision_id = str(decision.get("decision_id") or "").strip()
    if not decision_id:
        raise CouncilShadowError("decision_id is required")

    signals = {str(item).strip().lower() for item in decision.get("domain_signals", []) if str(item).strip()}
    matched = _matched_routes(signals, routing)

    capabilities: list[str] = ["chair"]
    specialists: list[str] = []
    allowed_core = set(cfg["callable_core_capabilities"])
    for route in matched:
        for core_id in route.get("core_add", []):
            if core_id in allowed_core and core_id not in capabilities:
                capabilities.append(core_id)
        for specialist in route.get("specialists", []):
            if specialist not in specialists:
                specialists.append(specialist)

    if decision.get("commercial") is True and str(decision.get("materiality", "")).upper() != "LOW":
        for specialist in cfg["commercial_mandatory_specialists"]:
            if specialist not in specialists:
                specialists.append(specialist)

    return {
        "decision_id": decision_id,
        "candidate_version": cfg["version"],
        "coordinator": cfg["decision_orchestrator"]["id"],
        "capabilities": capabilities,
        "specialists": specialists,
        "protocol_stages": list(cfg["protocol_stages"]),
        "shadow_only": True,
        "execution_authority": False,
        "governing_decision": False,
        "runtime_model": cfg["runtime_model"],
        "matched_route_count": len(matched),
    }


def synthesize_shadow(packet: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    if cfg.get("status") != "CANDIDATE_SHADOW_ONLY":
        raise CouncilShadowError("shadow synthesis requires candidate-only mode")
    if not str(packet.get("decision_id") or "").strip():
        raise CouncilShadowError("decision_id is required")

    if packet.get("execute") is True:
        raise CouncilShadowError("Council Shadow cannot execute")
    if packet.get("authority_change"):
        raise CouncilShadowError("Council Shadow cannot mutate authority")
    if packet.get("governing_decision") is True:
        raise CouncilShadowError("Council Shadow cannot claim a governing decision")

    dissent = packet.get("dissent", [])
    blockers = packet.get("domain_blockers", [])
    alternatives = packet.get("alternatives", [])
    if not isinstance(dissent, list) or not isinstance(blockers, list) or not isinstance(alternatives, list):
        raise CouncilShadowError("dissent, domain_blockers, and alternatives must be lists")

    return {
        "decision_id": str(packet["decision_id"]),
        "candidate_recommendation": packet.get("candidate_recommendation"),
        "alternatives": list(alternatives),
        "dissent": list(dissent),
        "domain_blockers": list(blockers),
        "minority_preserved": bool(dissent or blockers),
        "shadow_only": True,
        "execution_authority": False,
        "governing_decision": False,
    }
