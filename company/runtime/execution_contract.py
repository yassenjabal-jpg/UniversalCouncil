from __future__ import annotations

from typing import Any


class ExecutionContractError(ValueError):
    pass


def validate_execution_contract_config(cfg: dict[str, Any]) -> bool:
    if not isinstance(cfg, dict) or cfg.get("status") != "CANDIDATE_SHADOW_ONLY":
        raise ExecutionContractError("ExecutionContract config must remain candidate shadow-only")
    council = set(cfg.get("council_owns", []))
    orchestrator = set(cfg.get("execution_orchestrator_owns", []))
    expected_council = {
        "what",
        "why",
        "constraints",
        "authority",
        "blocking_conditions",
        "verification_target",
    }
    expected_orchestrator = {
        "how",
        "where",
        "tool",
        "route",
        "recovery",
        "verification_method",
    }
    if council != expected_council:
        raise ExecutionContractError("Council ownership does not match canonical R13 contract")
    if orchestrator != expected_orchestrator:
        raise ExecutionContractError("Execution Orchestrator ownership does not match canonical R13 contract")
    if council & orchestrator:
        raise ExecutionContractError("Council and Execution Orchestrator ownership must not overlap")
    if cfg.get("execution_orchestrator_is_voting_member") is not False:
        raise ExecutionContractError("Execution Orchestrator must not be a voting Council member")
    return True


def _validate_authority(authority: dict[str, Any]) -> None:
    if not isinstance(authority, dict):
        raise ExecutionContractError("authority must be an object")
    if not str(authority.get("principal") or "").strip():
        raise ExecutionContractError("authority principal is required")
    for field in ("operations", "targets", "scopes"):
        values = authority.get(field)
        if not isinstance(values, list) or not values:
            raise ExecutionContractError(f"authority {field} must be a non-empty list")
        if not all(isinstance(item, str) and item.strip() for item in values):
            raise ExecutionContractError(f"authority {field} must contain non-empty strings")


def build_execution_contract(decision: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    validate_execution_contract_config(cfg)
    if not isinstance(decision, dict):
        raise ExecutionContractError("decision must be an object")

    for forbidden in cfg["council_forbidden_execution_fields"]:
        if forbidden in decision:
            raise ExecutionContractError(f"Council may not preselect execution field: {forbidden}")

    required = set(cfg["council_owns"]) | {"decision_id"}
    missing = [field for field in required if field not in decision]
    if missing:
        raise ExecutionContractError(f"decision missing fields: {sorted(missing)}")

    decision_id = str(decision["decision_id"]).strip()
    if not decision_id:
        raise ExecutionContractError("decision_id is required")
    if not str(decision["what"]).strip() or not str(decision["why"]).strip():
        raise ExecutionContractError("what and why are required")
    if not isinstance(decision["constraints"], list):
        raise ExecutionContractError("constraints must be a list")
    if not isinstance(decision["blocking_conditions"], list):
        raise ExecutionContractError("blocking_conditions must be a list")
    if not str(decision["verification_target"]).strip():
        raise ExecutionContractError("verification_target is required")
    _validate_authority(decision["authority"])

    unresolved_states = set(cfg.get("unresolved_blocker_states", []))
    unresolved = []
    for blocker in decision["blocking_conditions"]:
        if not isinstance(blocker, dict):
            raise ExecutionContractError("blocking condition must be an object")
        status = str(blocker.get("status") or "").upper()
        if status in unresolved_states:
            unresolved.append(blocker)

    return {
        "schema_version": "1.0-candidate",
        "decision_id": decision_id,
        "what": decision["what"],
        "why": decision["why"],
        "constraints": list(decision["constraints"]),
        "authority": {
            "principal": str(decision["authority"]["principal"]),
            "operations": list(decision["authority"]["operations"]),
            "targets": list(decision["authority"]["targets"]),
            "scopes": list(decision["authority"]["scopes"]),
        },
        "blocking_conditions": list(decision["blocking_conditions"]),
        "verification_target": decision["verification_target"],
        "execution_ready": len(unresolved) == 0,
        "unresolved_blockers": unresolved,
        "council_owned": True,
        "shadow_only": True,
    }


def build_execution_plan(
    contract: dict[str, Any],
    proposal: dict[str, Any],
    cfg: dict[str, Any],
) -> dict[str, Any]:
    validate_execution_contract_config(cfg)
    if contract.get("execution_ready") is not True:
        raise ExecutionContractError("ExecutionContract is not ready while blockers remain unresolved")
    if not isinstance(proposal, dict):
        raise ExecutionContractError("execution proposal must be an object")

    for forbidden in cfg["orchestrator_forbidden_decision_fields"]:
        if forbidden in proposal:
            raise ExecutionContractError(f"Execution Orchestrator may not redefine Council field: {forbidden}")

    required = set(cfg["execution_orchestrator_owns"]) | {"operation", "target", "scope"}
    missing = [field for field in required if field not in proposal]
    if missing:
        raise ExecutionContractError(f"execution proposal missing fields: {sorted(missing)}")
    if any(proposal[field] in (None, "") for field in required):
        raise ExecutionContractError("execution proposal fields must be non-empty")

    authority = contract.get("authority")
    _validate_authority(authority)
    operation = str(proposal["operation"])
    target = str(proposal["target"])
    scope = str(proposal["scope"])
    if operation not in authority["operations"]:
        raise ExecutionContractError("execution operation exceeds Council authority")
    if target not in authority["targets"]:
        raise ExecutionContractError("execution target exceeds Council authority")
    if scope not in authority["scopes"]:
        raise ExecutionContractError("execution scope exceeds Council authority")

    return {
        "decision_id": contract["decision_id"],
        "contract_schema_version": contract.get("schema_version"),
        "how": proposal["how"],
        "where": proposal["where"],
        "tool": proposal["tool"],
        "route": proposal["route"],
        "recovery": proposal["recovery"],
        "verification_method": proposal["verification_method"],
        "operation": operation,
        "target": target,
        "scope": scope,
        "verification_target": contract["verification_target"],
        "constraints": list(contract["constraints"]),
        "authority_principal": authority["principal"],
        "voting_member": False,
        "shadow_only": True,
    }
