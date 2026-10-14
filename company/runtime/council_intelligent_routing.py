from __future__ import annotations

from typing import Any


class IntelligentRoutingError(ValueError):
    pass


def _rank(value: str, levels: list[str], field: str) -> int:
    try:
        return levels.index(value)
    except ValueError as exc:
        raise IntelligentRoutingError(f"unknown {field} level: {value}") from exc


def _at_least(value: str, threshold: str, levels: list[str], field: str) -> bool:
    return _rank(value, levels, field) >= _rank(threshold, levels, field)


def validate_routing_candidate(cfg: dict[str, Any], roles: dict[str, Any]) -> bool:
    if not isinstance(cfg, dict) or cfg.get("status") != "CANDIDATE_SHADOW_ONLY":
        raise IntelligentRoutingError("routing candidate must remain shadow-only")
    if cfg.get("governing_council_version") != roles.get("version"):
        raise IntelligentRoutingError("routing candidate must target the current governing version")
    if cfg.get("free_text_keyword_routing") is not False:
        raise IntelligentRoutingError("R11 routing may not depend on free-text keyword routing")

    core_ids = {item["id"] for item in roles.get("core_roles", [])}
    specialist_ids = {item["id"] for item in roles.get("specialist_roles", [])}
    callable_core = set(cfg.get("callable_core_capabilities", []))
    if "chair" not in callable_core or "synthesis" in callable_core:
        raise IntelligentRoutingError("callable core must include Chair and keep Synthesis as protocol")
    if not callable_core.issubset(core_ids):
        raise IntelligentRoutingError("unknown core capability in routing candidate")

    mapping = cfg.get("domain_specialists", {})
    if not isinstance(mapping, dict) or not mapping:
        raise IntelligentRoutingError("domain_specialists mapping is required")
    if not set(mapping.values()).issubset(specialist_ids):
        raise IntelligentRoutingError("domain mapping references unknown specialists")

    mandatory = set(cfg.get("commercial_mandatory_specialists", []))
    if mandatory != {"customer_skeptic", "moat_auditor"}:
        raise IntelligentRoutingError("commercial mandatory specialists must be preserved")
    if not mandatory.issubset(specialist_ids):
        raise IntelligentRoutingError("commercial mandatory specialists are not defined")

    required_dimensions = {
        "domain",
        "materiality",
        "uncertainty",
        "risk",
        "freshness",
        "blocker_authority",
        "required_capability",
    }
    if set(cfg.get("dimensions", [])) != required_dimensions:
        raise IntelligentRoutingError("routing dimensions do not match the canonical R11 contract")
    return True


def route_decision(
    decision: dict[str, Any],
    cfg: dict[str, Any],
    roles: dict[str, Any],
) -> dict[str, Any]:
    validate_routing_candidate(cfg, roles)

    decision_id = str(decision.get("decision_id") or "").strip()
    if not decision_id:
        raise IntelligentRoutingError("decision_id is required")

    levels = cfg["levels"]
    materiality = str(decision.get("materiality", "LOW")).upper()
    uncertainty = str(decision.get("uncertainty", "LOW")).upper()
    risk = str(decision.get("risk", "LOW")).upper()
    freshness = str(decision.get("freshness", "LOW")).upper()
    _rank(materiality, levels["materiality"], "materiality")
    _rank(uncertainty, levels["uncertainty"], "uncertainty")
    _rank(risk, levels["risk"], "risk")
    _rank(freshness, levels["freshness"], "freshness")

    domain_mapping = cfg["domain_specialists"]
    specialists: list[str] = []
    core: list[str] = ["chair"]
    reasons: dict[str, list[str]] = {"chair": ["decision_coordination"]}

    domains = decision.get("domains", [])
    if not isinstance(domains, list):
        raise IntelligentRoutingError("domains must be a list")
    for raw_domain in domains:
        domain = str(raw_domain).strip().lower()
        if domain not in domain_mapping:
            raise IntelligentRoutingError(f"unknown domain: {domain}")
        specialist = domain_mapping[domain]
        if specialist not in specialists:
            specialists.append(specialist)
            reasons.setdefault(specialist, []).append(f"domain:{domain}")

    required = decision.get("required_capabilities", [])
    if not isinstance(required, list):
        raise IntelligentRoutingError("required_capabilities must be a list")
    allowed_core = set(cfg["callable_core_capabilities"])
    for raw in required:
        capability = str(raw).strip()
        if capability not in allowed_core or capability == "chair":
            raise IntelligentRoutingError(f"unknown or invalid required capability: {capability}")
        if capability not in core:
            core.append(capability)
        reasons.setdefault(capability, []).append("required_capability")

    rules = cfg["activation_rules"]
    evidence_rule = rules["evidence"]
    if (
        _at_least(
            uncertainty,
            evidence_rule["uncertainty_at_least"],
            levels["uncertainty"],
            "uncertainty",
        )
        or _at_least(
            freshness,
            evidence_rule["freshness_at_least"],
            levels["freshness"],
            "freshness",
        )
    ):
        if "evidence" not in core:
            core.append("evidence")
        if _at_least(
            uncertainty,
            evidence_rule["uncertainty_at_least"],
            levels["uncertainty"],
            "uncertainty",
        ):
            reasons.setdefault("evidence", []).append("high_uncertainty")
        if _at_least(
            freshness,
            evidence_rule["freshness_at_least"],
            levels["freshness"],
            "freshness",
        ):
            reasons.setdefault("evidence", []).append("freshness_requirement")

    red_rule = rules["redteam"]
    if (
        _at_least(
            materiality,
            red_rule["materiality_at_least"],
            levels["materiality"],
            "materiality",
        )
        and _at_least(
            uncertainty,
            red_rule["uncertainty_at_least"],
            levels["uncertainty"],
            "uncertainty",
        )
    ):
        if "redteam" not in core:
            core.append("redteam")
        reasons.setdefault("redteam", []).append("material_uncertainty")

    risk_rule = rules["risk"]
    if _at_least(risk, risk_rule["risk_at_least"], levels["risk"], "risk"):
        if "risk" not in core:
            core.append("risk")
        reasons.setdefault("risk", []).append("risk_threshold")

    blockers = decision.get("active_domain_blockers", [])
    if not isinstance(blockers, list):
        raise IntelligentRoutingError("active_domain_blockers must be a list")
    specialist_ids = {item["id"] for item in roles.get("specialist_roles", [])}
    for raw in blockers:
        specialist = str(raw).strip()
        if specialist not in specialist_ids:
            raise IntelligentRoutingError(f"unknown blocker authority: {specialist}")
        if specialist not in specialists:
            specialists.append(specialist)
        reasons.setdefault(specialist, []).append("active_domain_blocker")

    if decision.get("commercial") is True and materiality != "LOW":
        for specialist in cfg["commercial_mandatory_specialists"]:
            if specialist not in specialists:
                specialists.append(specialist)
            reasons.setdefault(specialist, []).append("material_commercial_decision")

    return {
        "decision_id": decision_id,
        "core_capabilities": core,
        "specialists": specialists,
        "voice_count": len(core) + len(specialists),
        "activation_reasons": reasons,
        "dimensions": list(cfg["dimensions"]),
        "objective": cfg["objective"],
        "free_text_keyword_routing": False,
        "shadow_only": True,
    }
