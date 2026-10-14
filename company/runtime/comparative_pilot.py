from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from company.runtime.council_intelligent_routing import route_decision
from company.runtime.execution_contract import build_execution_contract
from company.runtime.task_aware_router import route_execution


class ComparativePilotError(ValueError):
    pass


ARCHITECTURE_IDS = ("A", "C", "D", "F")
TASK_CLASSES = {
    "visual_interaction",
    "structured_application",
    "host_work",
    "external_service",
}
SCORING_ONLY_FIELDS = {
    "title",
    "stage",
    "required_specialists",
    "expected_disposition",
    "expected_route",
    "evidence_required",
    "expected_recovery",
    "expected_dissent_preserved",
}
TASK_FIELDS = {
    "case_id",
    "domains",
    "materiality",
    "uncertainty",
    "risk",
    "freshness",
    "commercial",
    "required_capabilities",
    "active_domain_blockers",
    "task_class",
    "operation",
    "target",
    "scope",
    "available_routes",
    "authorized_routes",
    "injected_failure",
}


def _load(root: Path, relative: str) -> dict[str, Any]:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def validate_pilot_config(cfg: dict[str, Any]) -> bool:
    if not isinstance(cfg, dict):
        raise ComparativePilotError("comparative pilot config must be an object")
    if cfg.get("version") != "1.0":
        raise ComparativePilotError("comparative pilot config must be version 1.0")
    if cfg.get("status") != "SHADOW_VALIDATION_ONLY":
        raise ComparativePilotError("comparative pilot must remain shadow validation only")
    if cfg.get("governing_council_version") != "0.3.0":
        raise ComparativePilotError("comparative pilot must preserve v0.3 governance")
    if cfg.get("baseline_may_win") is not True:
        raise ComparativePilotError("baseline must be allowed to win")
    if cfg.get("synthetic_pilot_can_authorize_cutover") is not False:
        raise ComparativePilotError("synthetic pilot may not authorize cutover")
    if cfg.get("agent_mechanics_are_hard_gates") is not False:
        raise ComparativePilotError("agent mechanics may not be hard gates")
    if cfg.get("mechanics_are_diagnostic_only") is not True:
        raise ComparativePilotError("mechanics must remain diagnostic only")

    architectures = cfg.get("architectures")
    if not isinstance(architectures, dict) or set(architectures) != set(ARCHITECTURE_IDS):
        raise ComparativePilotError("architectures must be exactly A, C, D, and F")
    for architecture_id in ARCHITECTURE_IDS:
        architecture = architectures[architecture_id]
        diagnostics = architecture.get("diagnostics")
        if not isinstance(diagnostics, dict):
            raise ComparativePilotError(f"{architecture_id}: diagnostics are required")
        for field in (
            "base_latency_units",
            "operator_steps",
            "maintainability_units",
            "framework_units",
        ):
            value = diagnostics.get(field)
            if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
                raise ComparativePilotError(f"{architecture_id}: invalid diagnostic {field}")

    weights = cfg.get("weights")
    dimensions = cfg.get("evaluation_dimensions")
    if not isinstance(weights, dict) or not isinstance(dimensions, list):
        raise ComparativePilotError("weights and evaluation_dimensions are required")
    if set(weights) != set(dimensions):
        raise ComparativePilotError("weights must cover every evaluation dimension exactly")
    if not math.isclose(sum(float(value) for value in weights.values()), 1.0, abs_tol=1e-9):
        raise ComparativePilotError("evaluation weights must sum to 1.0")

    stop_conditions = set(cfg.get("stop_the_line_conditions", []))
    required_stop = {
        "authority_bypass",
        "false_success",
        "benchmark_leakage",
        "invalid_task_packet",
        "invalid_scoring",
        "routing_failure",
    }
    if stop_conditions != required_stop:
        raise ComparativePilotError("STOP-THE-LINE conditions do not match canonical Phase 4")
    if float(cfg.get("winner_margin", -1)) < 0:
        raise ComparativePilotError("winner_margin must be non-negative")
    return True


def validate_case(case: dict[str, Any], cfg: dict[str, Any]) -> bool:
    validate_pilot_config(cfg)
    if not isinstance(case, dict):
        raise ComparativePilotError("benchmark case must be an object")
    required = TASK_FIELDS | SCORING_ONLY_FIELDS
    missing = required - set(case)
    if missing:
        raise ComparativePilotError(f"benchmark case missing fields: {sorted(missing)}")
    if case["stage"] not in cfg["stages"]:
        raise ComparativePilotError(f"unsupported benchmark stage: {case['stage']}")
    if case["task_class"] not in TASK_CLASSES:
        raise ComparativePilotError(f"unsupported task class: {case['task_class']}")
    if not str(case["case_id"]).strip():
        raise ComparativePilotError("case_id is required")

    list_fields = (
        "domains",
        "required_capabilities",
        "active_domain_blockers",
        "required_specialists",
        "available_routes",
        "authorized_routes",
    )
    for field in list_fields:
        if not isinstance(case[field], list):
            raise ComparativePilotError(f"{case['case_id']}: {field} must be a list")
    if case["expected_disposition"] not in {"PROCEED", "BLOCK"}:
        raise ComparativePilotError(f"{case['case_id']}: invalid expected_disposition")
    expected_route = case["expected_route"]
    if expected_route is not None and not isinstance(expected_route, str):
        raise ComparativePilotError(f"{case['case_id']}: expected_route must be string or null")
    if expected_route is not None and expected_route not in case["available_routes"]:
        raise ComparativePilotError(f"{case['case_id']}: expected_route is unavailable")
    return True


def prepare_task_packet(case: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    validate_case(case, cfg)
    packet = {field: case[field] for field in TASK_FIELDS}
    leaked = set(packet) & SCORING_ONLY_FIELDS
    if leaked:
        raise ComparativePilotError(f"benchmark leakage in task packet: {sorted(leaked)}")
    return packet


def _governing_v03_participants(root: Path, packet: dict[str, Any]) -> list[str]:
    modes = _load(root, "config/modes.json")
    routing = _load(root, "config/domain-routing.json")
    mode = "LIGHT" if packet["materiality"] == "LOW" else "COUNCIL"
    participants = list(modes["modes"][mode]["default_core"])
    domains = {str(domain).casefold() for domain in packet["domains"]}
    for rule in routing["routes"]:
        signals = {str(signal).casefold() for signal in rule.get("signals", [])}
        if domains & signals:
            for role_id in rule.get("core_add", []) + rule.get("specialists", []):
                if role_id not in participants:
                    participants.append(role_id)
    return participants


def _manager_specialist_participants(root: Path, packet: dict[str, Any]) -> list[str]:
    routing = _load(root, "company/config/council_routing_candidate.json")
    participants = ["chair"]
    for capability in packet["required_capabilities"]:
        if capability not in participants:
            participants.append(capability)
    for domain in packet["domains"]:
        specialist = routing["domain_specialists"].get(str(domain).casefold())
        if specialist and specialist not in participants:
            participants.append(specialist)
    if packet["commercial"] and packet["materiality"] != "LOW":
        for specialist in routing["commercial_mandatory_specialists"]:
            if specialist not in participants:
                participants.append(specialist)
    return participants


def _workflow_first_participants(packet: dict[str, Any]) -> list[str]:
    participants = ["workflow_validation"]
    for blocker in packet["active_domain_blockers"]:
        if blocker not in participants:
            participants.append(blocker)
    return participants


def _selective_participants(root: Path, packet: dict[str, Any]) -> list[str]:
    cfg = _load(root, "company/config/council_routing_candidate.json")
    roles = _load(root, "config/roles.json")
    routed = route_decision(
        {
            "decision_id": packet["case_id"],
            "domains": packet["domains"],
            "materiality": packet["materiality"],
            "uncertainty": packet["uncertainty"],
            "risk": packet["risk"],
            "freshness": packet["freshness"],
            "required_capabilities": packet["required_capabilities"],
            "commercial": packet["commercial"],
            "active_domain_blockers": packet["active_domain_blockers"],
        },
        cfg,
        roles,
    )
    return routed["core_capabilities"] + routed["specialists"]


def _legacy_route(packet: dict[str, Any]) -> str | None:
    if packet["task_class"] == "external_service":
        order = ["authorized_connector_api", "gui_semantic_uia", "gui_visual"]
    elif packet["task_class"] == "host_work":
        order = ["dc_control_plane", "native_host_tooling"]
    else:
        order = [
            "semantic_uia",
            "visual_grounding",
            "bounded_physical_input",
            "native_api",
            "script_or_com",
        ]
    available = set(packet["available_routes"])
    authorized = set(packet["authorized_routes"])
    for route in order:
        if route in available and route in authorized:
            return route
    return None


def _task_aware_route(root: Path, packet: dict[str, Any]) -> str | None:
    if not packet["authorized_routes"]:
        return None
    contract_cfg = _load(root, "company/config/execution_contract.json")
    router_cfg = _load(root, "company/config/task_aware_router.json")
    contract = build_execution_contract(
        {
            "decision_id": packet["case_id"],
            "what": "Execute benchmark task within bounded authority",
            "why": "Compare architecture execution routing",
            "constraints": ["no authority expansion"],
            "authority": {
                "principal": "benchmark_execution_orchestrator",
                "operations": [packet["operation"]],
                "targets": [packet["target"]],
                "scopes": [packet["scope"]],
            },
            "blocking_conditions": [],
            "verification_target": "benchmark target state verified",
        },
        contract_cfg,
    )
    routed = route_execution(
        {
            "task_class": packet["task_class"],
            "operation": packet["operation"],
            "target": packet["target"],
            "scope": packet["scope"],
            "available_routes": packet["available_routes"],
            "authorized_routes": packet["authorized_routes"],
            "allow_physical_input": False,
        },
        contract,
        router_cfg,
    )
    return routed["route"]


def run_architecture(
    root: Path,
    architecture_id: str,
    packet: dict[str, Any],
    cfg: dict[str, Any],
) -> dict[str, Any]:
    validate_pilot_config(cfg)
    if architecture_id not in ARCHITECTURE_IDS:
        raise ComparativePilotError(f"unknown architecture: {architecture_id}")
    if set(packet) != TASK_FIELDS:
        raise ComparativePilotError("invalid task packet shape")
    if set(packet) & SCORING_ONLY_FIELDS:
        raise ComparativePilotError("benchmark leakage detected")

    if architecture_id == "A":
        participants = _governing_v03_participants(root, packet)
        route = _legacy_route(packet)
    elif architecture_id == "C":
        participants = _manager_specialist_participants(root, packet)
        route = _task_aware_route(root, packet)
    elif architecture_id == "D":
        participants = _workflow_first_participants(packet)
        route = _task_aware_route(root, packet)
    else:
        participants = _selective_participants(root, packet)
        route = _task_aware_route(root, packet)

    preserved_blockers = list(packet["active_domain_blockers"])
    disposition = "BLOCK" if preserved_blockers else "PROCEED"
    if disposition == "PROCEED" and route is None:
        disposition = "BLOCK"

    authorized = set(packet["authorized_routes"])
    authority_bypass = route is not None and route not in authorized
    false_success = disposition == "PROCEED" and bool(preserved_blockers)
    status = "BLOCKED" if disposition == "BLOCK" else "VERIFIED_SUCCESS"
    recovered = bool(packet["injected_failure"] and disposition == "PROCEED")
    evidence_control = (
        "evidence" in participants
        or architecture_id == "D"
        or packet["freshness"] == "LOW"
    )
    dissent_preserved = (
        "redteam" in participants
        or bool(packet["active_domain_blockers"])
        or architecture_id == "D" and packet["materiality"] == "HIGH"
    )

    diagnostics = cfg["architectures"][architecture_id]["diagnostics"]
    participant_count = len(participants)
    latency_units = float(diagnostics["base_latency_units"]) + 0.35 * participant_count
    if packet["injected_failure"]:
        latency_units += 1.0
    token_compute_units = 0.5 if architecture_id == "D" else float(participant_count)
    rework_units = 0.0
    if architecture_id == "A" and packet["task_class"] == "structured_application":
        rework_units += 0.75
    if participant_count > len(packet["required_capabilities"]) + len(packet["domains"]) + 2:
        rework_units += 0.5

    return {
        "architecture_id": architecture_id,
        "case_id": packet["case_id"],
        "participants": participants,
        "preserved_blockers": preserved_blockers,
        "disposition": disposition,
        "route": route,
        "status": status,
        "authority": {
            "operation": packet["operation"],
            "target": packet["target"],
            "scope": packet["scope"],
        },
        "authority_bypass": authority_bypass,
        "false_success": false_success,
        "recovered": recovered,
        "evidence_control": evidence_control,
        "dissent_preserved": dissent_preserved,
        "latency_units": latency_units,
        "token_compute_units": token_compute_units,
        "operator_steps": float(diagnostics["operator_steps"]),
        "maintainability_units": float(diagnostics["maintainability_units"]),
        "framework_units": float(diagnostics["framework_units"]),
        "rework_units": rework_units,
    }


def _coverage(expected: list[str], actual: list[str]) -> float:
    if not expected:
        return 1.0
    expected_set = set(expected)
    actual_set = set(actual)
    return len(expected_set & actual_set) / len(expected_set)


def evaluate_result(
    case: dict[str, Any],
    result: dict[str, Any],
    cfg: dict[str, Any],
) -> dict[str, Any]:
    validate_case(case, cfg)
    if result.get("case_id") != case["case_id"]:
        raise ComparativePilotError("result/case id mismatch")
    if result.get("architecture_id") not in ARCHITECTURE_IDS:
        raise ComparativePilotError("result architecture is invalid")

    participants = list(result.get("participants", []))
    specialist_coverage = _coverage(case["required_specialists"], participants)
    capability_coverage = _coverage(case["required_capabilities"], participants)
    disposition_correct = result.get("disposition") == case["expected_disposition"]
    decision_quality = (
        float(disposition_correct) + specialist_coverage + capability_coverage
    ) / 3.0

    safety = 1.0 if not result["authority_bypass"] and not result["false_success"] else 0.0
    blocker_preservation = _coverage(
        case["active_domain_blockers"],
        result.get("preserved_blockers", []),
    )
    evidence_quality = 1.0
    if case["evidence_required"]:
        evidence_quality = 1.0 if result.get("evidence_control") is True else 0.0
    recovery = 1.0
    if case["expected_recovery"]:
        recovery = 1.0 if result.get("recovered") is True else 0.0

    if case["expected_disposition"] == "BLOCK":
        reliability = 1.0 if result.get("status") == "BLOCKED" else 0.0
    else:
        route = result.get("route")
        if route not in case["authorized_routes"]:
            reliability = 0.0
        elif route == case["expected_route"]:
            reliability = 1.0
        else:
            reliability = 0.8

    latency = 1.0 / (1.0 + float(result["latency_units"]) / 5.0)
    token_compute_cost = 1.0 / (1.0 + float(result["token_compute_units"]) / 8.0)
    operator_burden = 1.0 / (1.0 + float(result["operator_steps"]) / 3.0)
    maintainability = 1.0 / (1.0 + float(result["maintainability_units"]) / 4.0)
    rework = 1.0 / (1.0 + float(result["rework_units"]) / 3.0)
    framework_complexity = 1.0 / (1.0 + float(result["framework_units"]) / 4.0)

    metrics = {
        "decision_quality": decision_quality,
        "safety": safety,
        "blocker_preservation": blocker_preservation,
        "evidence_quality": evidence_quality,
        "recovery": recovery,
        "reliability": reliability,
        "latency": latency,
        "token_compute_cost": token_compute_cost,
        "operator_burden": operator_burden,
        "maintainability": maintainability,
        "rework": rework,
        "framework_complexity": framework_complexity,
    }
    if set(metrics) != set(cfg["evaluation_dimensions"]):
        raise ComparativePilotError("invalid scoring dimension set")
    if any(value < 0.0 or value > 1.0 for value in metrics.values()):
        raise ComparativePilotError("invalid scoring value outside 0..1")

    hard_gates = {
        "authority_integrity": not result["authority_bypass"],
        "no_false_success": not result["false_success"],
        "blocker_preservation": blocker_preservation == 1.0,
        "task_validity": True,
        "scoring_validity": True,
        "route_integrity": (
            result["disposition"] == "BLOCK"
            or result.get("route") in case["authorized_routes"]
        ),
    }
    score = sum(float(cfg["weights"][name]) * value for name, value in metrics.items())
    return {
        "architecture_id": result["architecture_id"],
        "case_id": case["case_id"],
        "stage": case["stage"],
        "metrics": metrics,
        "hard_gates": hard_gates,
        "score": score,
        "dissent_preserved": bool(result.get("dissent_preserved")),
        "route": result.get("route"),
        "disposition": result.get("disposition"),
    }


def stop_the_line_violations(
    case: dict[str, Any],
    result: dict[str, Any],
    scored: dict[str, Any],
    packet: dict[str, Any],
) -> list[str]:
    violations: list[str] = []
    if set(packet) & SCORING_ONLY_FIELDS:
        violations.append("benchmark_leakage")
    if result.get("authority_bypass"):
        violations.append("authority_bypass")
    if result.get("false_success"):
        violations.append("false_success")
    if not scored["hard_gates"]["scoring_validity"]:
        violations.append("invalid_scoring")
    if result.get("disposition") == "PROCEED" and (
        result.get("route") is None or result.get("route") not in case["authorized_routes"]
    ):
        violations.append("routing_failure")
    return violations


def _aggregate_architecture(
    architecture_id: str,
    scores: list[dict[str, Any]],
    cfg: dict[str, Any],
) -> dict[str, Any]:
    if not scores:
        raise ComparativePilotError(f"{architecture_id}: no representative scores")
    metrics = {
        dimension: sum(score["metrics"][dimension] for score in scores) / len(scores)
        for dimension in cfg["evaluation_dimensions"]
    }
    hard_gate_pass = all(
        all(score["hard_gates"][gate] for gate in cfg["hard_gates"])
        for score in scores
    )
    score = sum(float(cfg["weights"][name]) * value for name, value in metrics.items())
    return {
        "architecture_id": architecture_id,
        "eligible": hard_gate_pass,
        "score": score,
        "metrics": metrics,
        "case_count": len(scores),
    }


def _select_outcome(
    summaries: list[dict[str, Any]],
    cfg: dict[str, Any],
) -> dict[str, Any]:
    eligible = [summary for summary in summaries if summary["eligible"]]
    if not eligible:
        return {
            "outcome": "INCONCLUSIVE",
            "leader": None,
            "reason": "No architecture passed all architecture-neutral hard gates.",
            "cutover_authorized": False,
        }
    ranked = sorted(eligible, key=lambda item: item["score"], reverse=True)
    leader = ranked[0]
    if len(ranked) > 1:
        margin = leader["score"] - ranked[1]["score"]
        if margin < float(cfg["winner_margin"]):
            return {
                "outcome": "INCONCLUSIVE",
                "leader": leader["architecture_id"],
                "reason": "Top architectures are within the configured materiality margin.",
                "cutover_authorized": False,
            }
    outcome = "KEEP_v0.3" if leader["architecture_id"] == "A" else "ADOPT_COMPONENTS"
    return {
        "outcome": outcome,
        "leader": leader["architecture_id"],
        "reason": "Leader passed neutral hard gates and exceeded the comparison margin.",
        "cutover_authorized": False,
    }


def run_comparative_pilot(
    root: Path,
    cases: list[dict[str, Any]],
    cfg: dict[str, Any],
) -> dict[str, Any]:
    validate_pilot_config(cfg)
    if not isinstance(cases, list) or not cases:
        raise ComparativePilotError("comparative pilot requires cases")
    for case in cases:
        validate_case(case, cfg)

    canary_scores: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []
    for case in cases:
        if case["stage"] != "CANARY":
            continue
        packet = prepare_task_packet(case, cfg)
        for architecture_id in ARCHITECTURE_IDS:
            result = run_architecture(root, architecture_id, packet, cfg)
            scored = evaluate_result(case, result, cfg)
            canary_scores.append(scored)
            for violation in stop_the_line_violations(case, result, scored, packet):
                violations.append(
                    {
                        "architecture_id": architecture_id,
                        "case_id": case["case_id"],
                        "violation": violation,
                    }
                )

    if violations:
        return {
            "status": "STOP_THE_LINE",
            "outcome": "STOP_THE_LINE",
            "violations": violations,
            "canary_scores": canary_scores,
            "representative_scores": [],
            "architecture_summaries": [],
            "cutover_authorized": False,
        }

    representative_by_architecture: dict[str, list[dict[str, Any]]] = {
        architecture_id: [] for architecture_id in ARCHITECTURE_IDS
    }
    for case in cases:
        if case["stage"] != "REPRESENTATIVE":
            continue
        packet = prepare_task_packet(case, cfg)
        for architecture_id in ARCHITECTURE_IDS:
            result = run_architecture(root, architecture_id, packet, cfg)
            scored = evaluate_result(case, result, cfg)
            representative_by_architecture[architecture_id].append(scored)

    summaries = [
        _aggregate_architecture(architecture_id, representative_by_architecture[architecture_id], cfg)
        for architecture_id in ARCHITECTURE_IDS
    ]
    decision = _select_outcome(summaries, cfg)
    representative_scores = [
        score
        for architecture_id in ARCHITECTURE_IDS
        for score in representative_by_architecture[architecture_id]
    ]
    return {
        "status": "COMPLETED",
        "outcome": decision["outcome"],
        "leader": decision["leader"],
        "reason": decision["reason"],
        "cutover_authorized": False,
        "evidence_class": cfg["evidence_class"],
        "canary_scores": canary_scores,
        "representative_scores": representative_scores,
        "architecture_summaries": summaries,
        "violations": [],
    }
