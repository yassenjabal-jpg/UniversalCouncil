from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "state" / "command-center" / "project-governance" / "murtakaz-orchestration.json"

SOURCES = [
    "state/command-center/project-governance/al-murtakaz.json",
    "state/command-center/project-governance/inheritance-lock.json",
    "state/command-center/project-governance/project-council.json",
    "state/command-center/project-governance/product-studio.json",
    "state/command-center/project-governance/al-murtakaz-approval-policy.json",
    "state/command-center/project-governance/agentic-os-policy.json",
    "state/command-center/project-governance/architecture-invariants.json",
    "state/command-center/project-governance/context-capsule-contract.json",
    "state/command-center/project-governance/change-envelope-contract.json",
]


def load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def git_blob_sha(relative: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{relative}"],
        cwd=ROOT,
        text=True,
    ).strip()


def build() -> dict[str, Any]:
    identity = load(SOURCES[0])
    lock = load(SOURCES[1])
    council = load(SOURCES[2])
    studio = load(SOURCES[3])
    approval = load(SOURCES[4])
    agentic = load(SOURCES[5])
    invariants = load(SOURCES[6])
    capsule = load(SOURCES[7])
    envelope = load(SOURCES[8])

    if identity["id"] != "al-murtakaz":
        raise SystemExit("Murtakaz identity drifted")
    if lock["rules"]["allow_parent_mutation"]:
        raise SystemExit("Murtakaz projection may not inherit parent mutation authority")
    if council["authority"]["may_execute_tools_by_role_definition"]:
        raise SystemExit("Murtakaz governance role authority inflated")
    if council["authority"]["may_open_stage8"]:
        raise SystemExit("Murtakaz governance may not open Stage 8")
    if studio["authority"]["execution_authority"]:
        raise SystemExit("Murtakaz workshop may not gain execution authority")
    if studio["authority"]["live_publish_authority"]:
        raise SystemExit("Murtakaz workshop may not gain live-publish authority")
    if approval["status"] != "OWNER_DIRECTIVE_ACTIVE":
        raise SystemExit("Murtakaz mandatory approval policy must remain active")
    if not approval["implicit_approval_forbidden"]:
        raise SystemExit("Murtakaz approval may not become implicit")
    if agentic["identity"]["system"] != "al-murtakaz":
        raise SystemExit("Agentic OS policy is not project-local Murtakaz")
    if agentic["authority"]["execution_authority"] or agentic["authority"]["stage8_opened"]:
        raise SystemExit("Agentic OS policy may not grant execution authority or open Stage 8")
    if not agentic["logical_gateway"]["not_a_god_object"]:
        raise SystemExit("Murtakaz gateway boundary regressed into a monolith")
    if not agentic["visual_inheritance"]["generic_visual_capsule_may_not_weaken_existing_gate"]:
        raise SystemExit("Agentic OS policy may not weaken existing visual hard gates")
    if invariants["status"] != "ACTIVE":
        raise SystemExit("Agentic OS architecture invariants are not active")
    if not capsule["immutable_per_job"]:
        raise SystemExit("Context Capsule must remain immutable per job")
    if envelope["unplanned_scope_expansion"] != "RETURN_TICKET_OR_NEW_CHANGE_ENVELOPE":
        raise SystemExit("Change Envelope scope expansion rule drifted")

    return {
        "schema_version": "2.0",
        "source_type": "project_local_repository_projection",
        "project_id": council["project_id"],
        "source_files": [{"path": path, "blob_sha": git_blob_sha(path)} for path in SOURCES],
        "identity": {
            "id": identity["id"],
            "name_ar": identity["name_ar"],
            "governance_name_ar": identity["units"]["governance"]["name_ar"],
            "workshop_name_ar": identity["units"]["workshop"]["name_ar"],
        },
        "governance": {
            "profile_id": council["profile_id"],
            "status": council["status"],
            "core_roles": council["core_roles"],
            "on_demand_specialists": council["on_demand_specialists"],
            "mandatory_routes": council["mandatory_routes"],
            "default_modes": council["default_modes"],
            "blockers": council["blockers"],
            "owner_gates": council["owner_gates"],
            "truth_rules": council["truth_rules"],
        },
        "workshop": {
            "profile_id": studio["profile_id"],
            "status": studio["status"],
            "operating_model": studio["operating_model"],
            "functions": studio["functions"],
            "phases": studio["phases"],
            "mandatory_clearance": studio["mandatory_clearance"],
            "council_clearance_required_for": studio["council_clearance_required_for"],
            "handoff": studio["handoff"],
            "prototype_rules": studio["prototype_rules"],
            "motion_rules": studio["motion_rules"],
        },
        "mandatory_approval": {
            "policy_id": approval["policy_id"],
            "status": approval["status"],
            "rule": approval["rule"],
            "implementation_requires": approval["implementation_requires"],
            "adoption_requires": approval["adoption_requires"],
            "completion_requires": approval["completion_requires"],
            "merge_requires": approval["merge_requires"],
            "release_requires": approval["release_requires"],
            "next_phase_requires": approval["next_phase_requires"],
            "implicit_approval_forbidden": approval["implicit_approval_forbidden"],
            "material_change_invalidates_prior_approval": approval["material_change_invalidates_prior_approval"],
        },
        "agentic_os": {
            "policy_id": agentic["policy_id"],
            "status": agentic["status"],
            "logical_gateway": agentic["logical_gateway"],
            "orchestration_services": agentic["orchestration_services"],
            "change_cycle": agentic["murtakaz_change_cycle"],
            "result_model": agentic["result_model"],
            "context_security": agentic["context_security"],
            "project_knowledge": agentic["project_knowledge"],
            "owner_directives": agentic["owner_directives"],
            "visual_inheritance": agentic["visual_inheritance"],
            "execution": agentic["execution"],
            "owner_experience": agentic["owner_experience"],
            "cross_platform": agentic["cross_platform"],
            "invariant_policy_id": invariants["policy_id"],
            "context_capsule_contract": capsule["contract_id"],
            "change_envelope_contract": envelope["contract_id"],
        },
        "model_control": {
            "role_model_separation": True,
            "owner_controlled_selection": True,
            "silent_fallback_allowed": False,
            "selection_precedence": [
                "TASK_OVERRIDE",
                "ROLE_OVERRIDE",
                "PROJECT_DEFAULT",
                "GLOBAL_DEFAULT",
            ],
        },
        "authority": {
            "execution_authority": False,
            "stage8_opened": False,
            "parent_mutation_allowed": False,
            "owner_final_authority": True,
        },
        "runtime": {
            "task_state": "NO_LIVE_TASK",
            "active_governance_roles": [],
            "active_workshop_function": None,
            "active_model": None,
            "provider_call_in_flight": False,
        },
    }


def main() -> int:
    rendered = json.dumps(build(), ensure_ascii=False, indent=2) + "\n"
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
