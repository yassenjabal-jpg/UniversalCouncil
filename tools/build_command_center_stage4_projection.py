from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "state" / "command-center" / "execution-fabric.json"

SOURCES = [
    "company/config/hybrid_execution.json",
    "company/config/tool_authority.json",
    "company/config/execution_contract.json",
    "company/config/task_aware_router.json",
    "state/command-center/phase0-execution-gates.json",
]


def load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def blob_sha(relative: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{relative}"],
        cwd=ROOT,
        text=True,
    ).strip()


def authority_by_operation(registry: dict[str, Any], operation: str) -> dict[str, Any]:
    matches = [
        item for item in registry["capabilities"]
        if item.get("operation") == operation
    ]
    if len(matches) != 1:
        raise SystemExit(f"expected one authority record for {operation}, got {len(matches)}")
    return matches[0]


def build() -> dict[str, Any]:
    hybrid = load("company/config/hybrid_execution.json")
    authority = load("company/config/tool_authority.json")
    execution_contract = load("company/config/execution_contract.json")
    router = load("company/config/task_aware_router.json")
    phase0 = load("state/command-center/phase0-execution-gates.json")

    remote_read = authority_by_operation(authority, "remote_shell.read")
    remote_execute = authority_by_operation(authority, "remote_shell.execute")
    desktop_observe = authority_by_operation(authority, "desktop_computer_use.observe")
    desktop_control = authority_by_operation(authority, "desktop_computer_use.control")

    all_phase0_pass = all(
        item["status"] == "PASS"
        for item in phase0["gates"].values()
    )

    live_authorized = bool(phase0["live_execution_authorized"]) and all_phase0_pass

    if live_authorized:
        raise SystemExit(
            "Stage 4 build contract forbids live execution authorization; "
            "a later owner-gated transition is required."
        )

    providers = [
        {
            "id": "native_host_tooling",
            "display_name": "UniversalCouncil Native Host Tooling",
            "role": "PREFERRED_HOST_PROVIDER",
            "state": "DESIGN_ONLY",
            "can_observe": False,
            "can_execute": False,
            "source": "company/config/task_aware_router.json",
            "note": "Stage 4 defines the boundary only; no native host dispatcher exists yet.",
        },
        {
            "id": "semantic_uia_bridge",
            "display_name": "YASSIN Semantic UIA Bridge",
            "role": "PREFERRED_GUI_PROVIDER",
            "state": (
                "OBSERVE_ONLY_CURRENT"
                if desktop_observe.get("current_verified_capability") is not None
                and desktop_control.get("current_verified_capability") is None
                else "UNVERIFIED"
            ),
            "can_observe": desktop_observe.get("current_verified_capability") is not None,
            "can_execute": False,
            "source": "company/config/tool_authority.json",
            "note": "Control evidence is historical only; Stage 4 dispatch remains disabled.",
        },
        {
            "id": "visual_grounding",
            "display_name": "Visual Grounding",
            "role": "GUI_FALLBACK_PROVIDER",
            "state": "NOT_CONNECTED",
            "can_observe": False,
            "can_execute": False,
            "source": "company/config/task_aware_router.json",
            "note": "Reserved fallback; no active provider in Stage 4.",
        },
        {
            "id": "bounded_physical_input",
            "display_name": "Bounded Physical Input",
            "role": "LAST_RESORT_GUI_PROVIDER",
            "state": "BLOCKED_UNVERIFIED",
            "can_observe": False,
            "can_execute": False,
            "source": "company/config/task_aware_router.json",
            "note": "Physical input requires explicit bounded verification and Phase 0 PASS.",
        },
        {
            "id": "dc_control_plane",
            "display_name": "Remote Desktop Commander",
            "role": "LEGACY_REFERENCE_PROVIDER",
            "state": "BLOCKED_BY_PROVIDER_LIMIT",
            "can_observe": False,
            "can_execute": False,
            "source": "company/config/tool_authority.json",
            "note": (
                f"{remote_read['provider']} / {remote_execute['provider']} retained as legacy reference only; "
                "not the permanent Command Center execution backbone."
            ),
        },
        {
            "id": "native_api_or_connector",
            "display_name": "Authorized Native API / Connector",
            "role": "EXTERNAL_SERVICE_PROVIDER",
            "state": "POLICY_GATED",
            "can_observe": True,
            "can_execute": False,
            "source": "company/config/task_aware_router.json",
            "note": "External connector authority remains provider-specific and outside YASSIN host dispatch.",
        },
    ]

    return {
        "schema_version": "1.0",
        "source_type": "repository_projection",
        "source_files": [
            {"path": path, "blob_sha": blob_sha(path)}
            for path in SOURCES
        ],
        "phase0": phase0,
        "service": {
            "mode": "SAFE_DISABLED",
            "target_host": "YASSIN",
            "live_dispatch_enabled": False,
            "allowed_cli_commands": [
                "status",
                "validate-manifest",
                "inspect-provider-registry",
                "validate-receipt",
            ],
            "forbidden_cli_commands": [
                "execute",
                "run-shell",
                "click",
                "type",
                "invoke-provider",
                "send-model-request",
            ],
        },
        "execution_contract": {
            "version": execution_contract["version"],
            "status": execution_contract["status"],
            "council_owns": execution_contract["council_owns"],
            "orchestrator_owns": execution_contract["execution_orchestrator_owns"],
            "orchestrator_is_voting_member": execution_contract["execution_orchestrator_is_voting_member"],
        },
        "router": {
            "version": router["version"],
            "status": router["status"],
            "task_classes": router["task_classes"],
            "fallback_restrictions": router["fallback_restrictions"],
            "recovery_requires": router["recovery_requires"],
            "hybrid_primary_plane": hybrid["primary_plane"],
            "hybrid_secondary_plane": hybrid["secondary_plane"],
        },
        "providers": providers,
        "recovery": {
            "unknown_is_never_success": hybrid["verification"]["unknown_is_never_success"],
            "stop_on_unknown": hybrid["batching"]["stop_on_unknown"],
            "unknown_requires_reconciliation": hybrid["recovery"]["unknown_requires_reconciliation"],
            "replay_completed_action_default": hybrid["recovery"]["replay_completed_action_default"],
            "single_physical_controller": hybrid["shared_state"]["single_physical_controller"],
        },
        "receipt_states": [
            "PLANNED",
            "VALIDATED",
            "BLOCKED",
            "UNKNOWN",
            "FAILED",
            "POSTCONDITION_VERIFIED",
        ],
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
