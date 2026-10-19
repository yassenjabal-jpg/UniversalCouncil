from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "state" / "command-center" / "owner-device-tailnet.json"

SOURCES = [
    "state/command-center/owner-device-tailnet-policy.json",
    "state/command-center/remote-transport.json",
]


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def blob_sha(relative: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{relative}"],
        cwd=ROOT,
        text=True,
    ).strip()


def main() -> int:
    policy = load("state/command-center/owner-device-tailnet-policy.json")
    transport = load("state/command-center/remote-transport.json")

    if transport["transport"]["mode"] != policy["transport_base"]["required_stage6_mode"]:
        raise SystemExit("Stage 7 requires the locked Stage 6 transport mode")
    if transport["transport"]["public_bind_allowed"] is not False:
        raise SystemExit("Stage 7 requires Stage 6 public bind to remain disabled")
    if transport["authority"]["live_execution_authorized"] is not False:
        raise SystemExit("Stage 7 requires Stage 6 execution lock")
    if policy["transport_base"]["tailscale_funnel_allowed"] is not False:
        raise SystemExit("Stage 7 Funnel must remain forbidden")
    if policy["transport_base"]["execution_authorized"] is not False:
        raise SystemExit("Stage 7 may not authorize execution")

    projection = {
        "schema_version": "1.0",
        "source_type": "repository_projection",
        "source_files": [{"path": path, "blob_sha": blob_sha(path)} for path in SOURCES],
        "runtime": {
            "mode": policy["mode"],
            "target_host": policy["target_host"],
            "required_stage6_mode": policy["transport_base"]["required_stage6_mode"],
            "required_local_bind": policy["transport_base"]["required_local_bind"],
            "required_local_port": policy["transport_base"]["required_local_port"],
            "public_bind_allowed": policy["transport_base"]["public_bind_allowed"],
            "router_port_forwarding_allowed": policy["transport_base"]["router_port_forwarding_allowed"],
            "cors_allowed": policy["transport_base"]["cors_allowed"],
            "tailscale_funnel_allowed": policy["transport_base"]["tailscale_funnel_allowed"],
            "execution_authorized": policy["transport_base"]["execution_authorized"],
            "execution_state": policy["transport_base"]["execution_state"],
        },
        "owner_device": policy["owner_device"],
        "tailscale": policy["tailscale"],
        "host_evidence": policy["host_evidence"],
        "gates": policy["gates"],
    }

    OUTPUT.write_text(
        json.dumps(projection, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
