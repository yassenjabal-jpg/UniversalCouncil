from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "state" / "command-center" / "orchestration-catalog.json"

SOURCES = [
    "config/roles.json",
    "company/config/council_role_contracts.json",
    "company/config/council_routing_candidate.json",
    "company/config/channel_operating_system.json",
    "company/config/media_venture.json",
]


def load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def git_blob_sha(relative: str) -> str:
    import subprocess

    return subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{relative}"],
        cwd=ROOT,
        text=True,
    ).strip()


def find_first(value: Any, key: str) -> Any:
    if isinstance(value, dict):
        if key in value:
            return value[key]
        for nested in value.values():
            found = find_first(nested, key)
            if found is not None:
                return found
    elif isinstance(value, list):
        for nested in value:
            found = find_first(nested, key)
            if found is not None:
                return found
    return None


def role_view(role: dict[str, Any], contracts: dict[str, Any]) -> dict[str, Any]:
    role_id = role["id"]
    contract = contracts["roles"].get(role_id)
    if contract is None:
        raise SystemExit(f"missing role contract for {role_id}")

    authority = contract["authority"]
    blocker = contract["blocker_scope"]
    activation = contract["activation"]

    return {
        "id": role_id,
        "name": role["name"],
        "activation_model": activation["model"],
        "blocker_type": blocker["type"],
        "blocker_domain": blocker["domain"],
        "may_execute_tools": bool(authority["may_execute_tools"]),
        "may_mutate_authority": bool(authority["may_mutate_authority"]),
        "may_self_approve": bool(authority["may_self_approve"]),
        "tools": list(contract["tools"]),
    }


def build() -> dict[str, Any]:
    roles = load("config/roles.json")
    contracts = load("company/config/council_role_contracts.json")
    routing = load("company/config/council_routing_candidate.json")
    channel = load("company/config/channel_operating_system.json")
    media = load("company/config/media_venture.json")

    core = [role_view(role, contracts) for role in roles["core_roles"]]
    specialists = [role_view(role, contracts) for role in roles["specialist_roles"]]

    departments = media["department_model"]["departments"]
    return_fields = find_first(channel, "return_ticket_required_fields")
    if not isinstance(return_fields, list) or not return_fields:
        return_fields = [
            "return_ticket_id",
            "source_department",
            "detecting_department",
            "artifact_ref",
            "defect",
            "reason_for_rejection",
            "requested_correction",
            "do_not_change",
            "resume_handoff",
        ]

    return {
        "schema_version": "1.0",
        "source_type": "repository_projection",
        "source_files": [
            {"path": path, "blob_sha": git_blob_sha(path)}
            for path in SOURCES
        ],
        "council": {
            "governing_version": roles["version"],
            "contracts_version": contracts["version"],
            "contracts_status": contracts["status"],
            "routing_version": routing["version"],
            "routing_status": routing["status"],
            "objective": routing["objective"],
            "free_text_keyword_routing": routing["free_text_keyword_routing"],
            "core_roles": core,
            "specialist_roles": specialists,
            "domain_specialists": routing["domain_specialists"],
            "commercial_mandatory_specialists": routing["commercial_mandatory_specialists"],
            "activation_rules": routing["activation_rules"],
        },
        "studio": {
            "visual_system": channel["visual_system"],
            "primary_language": channel["primary_language"],
            "publication_authority": channel["publication_authority"],
            "operating_mode": media["operating_model"]["mode"],
            "macro_phases": media["operating_model"]["macro_phases"],
            "control_plane_functions": media["operating_model"]["control_plane_functions"],
            "mandatory_clearance_functions": media["operating_model"]["mandatory_clearance_functions"],
            "departments": departments,
            "handoff_contract": media["handoff_contract"],
            "stage_execution_contract": media["stage_execution_contract"],
            "master_pipeline_contract": media["master_pipeline_contract"],
            "human_assistance": {
                "enabled": media["human_assistance"]["enabled"],
                "mode": media["human_assistance"]["mode"],
                "coordinator": media["human_assistance"]["coordinator"],
            },
            "return_ticket_required_fields": return_fields,
        },
        "model_control": {
            "role_model_separation": True,
            "owner_controlled_selection": True,
            "silent_fallback_allowed": False,
            "provider_calls_connected": False,
            "selection_precedence": [
                "TASK_OVERRIDE",
                "ROLE_OVERRIDE",
                "PROJECT_DEFAULT",
                "GLOBAL_DEFAULT",
            ],
        },
        "runtime": {
            "task_state": "NO_LIVE_TASK",
            "active_council_roles": [],
            "active_studio_department": None,
            "active_model": None,
            "provider_call_in_flight": False,
        },
    }


def main() -> int:
    data = build()
    rendered = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
