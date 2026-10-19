from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "state" / "command-center" / "remote-owner-gateway.json"

SOURCES = [
    "state/command-center/remote-owner-policy.json",
    "state/command-center/execution-fabric.json",
]

PHASE0_SOURCE = {
    "branch": "phase0/feasibility-adversarial-prototype",
    "head_sha": "63a4a446bc1e87f5352915f1e86c463de82e9b81",
    "files": [
        {
            "path": "company/runtime/phase0_guardrails.py",
            "blob_sha": "56d76a96c0ab5d74e703f69a53b2cd51d0d2843c",
        },
        {
            "path": "company/config/phase0_feasibility.json",
            "blob_sha": "57b26c4d8fc65c9e866ddefd826784f7826c7f24",
        },
        {
            "path": "company/tests/test_phase0_feasibility.py",
            "blob_sha": "f0ac55efd4e3462e0a1a56b376140db07fd20739",
        },
    ],
}


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def blob_sha(relative: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{relative}"],
        cwd=ROOT,
        text=True,
    ).strip()


def main() -> int:
    policy = load("state/command-center/remote-owner-policy.json")
    fabric = load("state/command-center/execution-fabric.json")

    if policy["live_execution_authorized"] is not False:
        raise SystemExit("Stage 5 policy may not authorize live execution")
    if policy["transport"]["live_network_listener_enabled"] is not False:
        raise SystemExit("Stage 5 may not enable a live network listener")
    if fabric["service"]["live_dispatch_enabled"] is not False:
        raise SystemExit("Stage 5 requires Stage 4 live dispatch to remain disabled")

    projection = {
        "schema_version": "1.0",
        "source_type": "repository_projection",
        "source_files": [{"path": path, "blob_sha": blob_sha(path)} for path in SOURCES],
        "phase0_remote_command_source": PHASE0_SOURCE,
        "gateway": {
            "mode": policy["mode"],
            "owner_principal": policy["owner_principal"],
            "target_host": policy["target_host"],
            "authentication_backend_connected": False,
            "live_network_listener_enabled": False,
            "local_cli_ingress_enabled": policy["transport"]["local_cli_ingress_enabled"],
            "tailscale_compatible_architecture": policy["transport"]["tailscale_compatible_architecture"],
            "public_internet_exposure_allowed": False,
            "router_port_forwarding_allowed": False,
            "github_queue_transport_enabled": False,
            "chat_transport_enabled": False,
            "phase0_remote_trust_status": policy["phase0_current_status"],
            "live_execution_authorized": False,
        },
        "trust_contract": policy["remote_command"],
        "approval_contract": policy["approval"],
        "device_session_contract": policy["device_session"],
        "queue_contract": policy["queue"],
        "service": {
            "allowed_cli_commands": [
                "status",
                "validate-envelope",
                "enqueue-synthetic",
                "inspect-queue",
                "validate-approval",
            ],
            "forbidden_cli_commands": [
                "listen",
                "serve",
                "execute",
                "dispatch",
                "run-shell",
                "click",
                "type",
                "invoke-provider",
                "send-model-request",
            ],
        },
        "runtime_truth": {
            "registered_devices": 0,
            "registered_sessions": 0,
            "queue_depth": 0,
            "phone_connected": False,
            "tailscale_connected": False,
            "github_transport_connected": False,
            "chat_transport_connected": False,
        },
    }

    OUTPUT.write_text(
        json.dumps(projection, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
