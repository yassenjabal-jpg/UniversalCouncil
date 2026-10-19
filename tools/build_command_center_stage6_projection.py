from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "state" / "command-center" / "remote-transport.json"

SOURCES = [
    "state/command-center/remote-transport-policy.json",
    "state/command-center/remote-owner-gateway.json",
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
    policy = load("state/command-center/remote-transport-policy.json")
    gateway = load("state/command-center/remote-owner-gateway.json")

    if policy["authority"]["live_execution_authorized"] is not False:
        raise SystemExit("Stage 6 transport may not authorize live execution")
    if policy["transport"]["public_bind_allowed"] is not False:
        raise SystemExit("Stage 6 public bind must remain disabled")
    if policy["transport"]["tailscale_funnel_allowed"] is not False:
        raise SystemExit("Stage 6 Tailscale Funnel must remain forbidden")
    if gateway["gateway"]["live_execution_authorized"] is not False:
        raise SystemExit("Stage 6 requires Stage 5 execution lock")

    projection = {
        "schema_version": "1.0",
        "source_type": "repository_projection",
        "source_files": [{"path": path, "blob_sha": blob_sha(path)} for path in SOURCES],
        "transport": {
            "mode": policy["mode"],
            "target_host": policy["target_host"],
            "listener_configured": policy["transport"]["listener_enabled"],
            "runtime_listener_active": False,
            "listener_scope": policy["transport"]["listener_scope"],
            "allowed_bind_addresses": policy["transport"]["allowed_bind_addresses"],
            "public_bind_allowed": policy["transport"]["public_bind_allowed"],
            "router_port_forwarding_allowed": policy["transport"]["router_port_forwarding_allowed"],
            "tailscale_serve_compatible": policy["transport"]["tailscale_serve_compatible"],
            "tailscale_connected": policy["transport"]["tailscale_connected"],
            "tailscale_serve_configured": policy["transport"]["tailscale_serve_configured"],
            "tailscale_funnel_allowed": policy["transport"]["tailscale_funnel_allowed"],
            "github_transport_connected": policy["transport"]["github_transport_connected"],
            "chat_transport_connected": policy["transport"]["chat_transport_connected"],
            "phone_connected": policy["transport"]["phone_connected"],
        },
        "authentication": policy["authentication"],
        "http": policy["http"],
        "round_trip": policy["round_trip"],
        "authority": policy["authority"],
    }

    OUTPUT.write_text(
        json.dumps(projection, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
