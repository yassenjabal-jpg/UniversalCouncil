from __future__ import annotations

from typing import Any


class RoleContractError(ValueError):
    pass


_REQUIRED = {
    "mission",
    "inputs",
    "outputs",
    "activation",
    "blocker_scope",
    "authority",
    "tools",
    "escalation",
    "conflicts",
    "contribution_criteria",
    "merge_remove_trigger",
}


def validate_role_contracts(cfg: dict[str, Any], roles: dict[str, Any]) -> bool:
    if not isinstance(cfg, dict) or cfg.get("status") != "CANDIDATE_SHADOW_ONLY":
        raise RoleContractError("role contracts must remain candidate shadow configuration")
    if cfg.get("governing_council_version") != roles.get("version"):
        raise RoleContractError("role contracts must target the current governing Council version")

    expected = {item["id"] for item in roles.get("core_roles", []) + roles.get("specialist_roles", [])}
    contracts = cfg.get("roles")
    if not isinstance(contracts, dict) or set(contracts) != expected:
        raise RoleContractError("role contracts must cover every governing role exactly once")

    specialists = {item["id"] for item in roles.get("specialist_roles", [])}
    for role_id, contract in contracts.items():
        if not isinstance(contract, dict):
            raise RoleContractError(f"{role_id}: contract must be an object")
        missing = _REQUIRED - set(contract)
        if missing:
            raise RoleContractError(f"{role_id}: missing contract fields {sorted(missing)}")
        for key in ("mission", "inputs", "outputs", "activation", "blocker_scope", "authority"):
            if contract.get(key) in (None, ""):
                raise RoleContractError(f"{role_id}: {key} is required")

        authority = contract["authority"]
        if not isinstance(authority, dict):
            raise RoleContractError(f"{role_id}: authority must be an object")
        for flag in ("may_execute_tools", "may_mutate_authority", "may_self_approve"):
            if authority.get(flag) is not False:
                raise RoleContractError(f"{role_id}: {flag} must remain false in candidate role contracts")

        blocker = contract["blocker_scope"]
        if not isinstance(blocker, dict):
            raise RoleContractError(f"{role_id}: blocker_scope must be an object")
        blocker_type = blocker.get("type")
        if blocker_type not in {"none", "function_bounded", "domain_bounded"}:
            raise RoleContractError(f"{role_id}: invalid blocker scope type")
        if role_id in specialists:
            if blocker_type != "domain_bounded":
                raise RoleContractError(f"{role_id}: specialist blockers must be domain-bounded")
            if blocker.get("requires_evidence") is not True:
                raise RoleContractError(f"{role_id}: specialist blockers require evidence")

        trigger = contract["merge_remove_trigger"]
        if not isinstance(trigger, dict) or trigger.get("automatic") is not False:
            raise RoleContractError(f"{role_id}: merge/remove cannot be automatic")
        if int(trigger.get("minimum_observation_count", 0)) < 3:
            raise RoleContractError(f"{role_id}: merge/remove requires repeated observations")
        signals = set(trigger.get("signals", []))
        if not {"duplicate_reasoning", "low_unique_contribution"}.issubset(signals):
            raise RoleContractError(f"{role_id}: merge/remove trigger lacks contribution/duplication evidence")

    chair = contracts["chair"]
    if "synthesis" in set(chair.get("outputs", [])):
        raise RoleContractError("Chair contract must not own synthesis output in the candidate architecture")
    if chair["authority"].get("decision_function") != "coordinate_and_record":
        raise RoleContractError("Chair candidate contract must coordinate and record only")

    synthesis = contracts["synthesis"]
    if synthesis["activation"].get("model") != "protocol_stage":
        raise RoleContractError("Synthesis must remain a protocol stage")
    if synthesis["authority"].get("may_override_dissent") is not False:
        raise RoleContractError("Synthesis may not override dissent")
    if synthesis["authority"].get("may_override_domain_blockers") is not False:
        raise RoleContractError("Synthesis may not override domain blockers")

    for role_id in ("customer_skeptic", "moat_auditor"):
        required_when = set(contracts[role_id]["activation"].get("required_when", []))
        if "material_commercial_decision" not in required_when:
            raise RoleContractError(f"{role_id}: material commercial activation is mandatory")

    return True
