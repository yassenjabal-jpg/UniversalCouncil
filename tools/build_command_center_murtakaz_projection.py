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

    return {
        "schema_version": "1.0",
        "source_type": "project_local_repository_projection",
        "project_id": council["project_id"],
        "source_files": [
            {"path": path, "blob_sha": git_blob_sha(path)}
            for path in SOURCES
        ],
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
