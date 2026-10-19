from __future__ import annotations

import json
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "UniversalCouncil.CommandCenter"
GATEWAY_APP = ROOT / "apps" / "UniversalCouncil.CommandCenter.RemoteGateway"
PROJECTION = ROOT / "state" / "command-center" / "remote-owner-gateway.json"
POLICY = ROOT / "state" / "command-center" / "remote-owner-policy.json"
STATE = ROOT / "state" / "command-center" / "command-center-state.json"

required = [
    APP / "MainWindow.xaml",
    APP / "MainWindow.xaml.cs",
    APP / "MainWindowViewModel.cs",
    APP / "App.xaml.cs",
    GATEWAY_APP / "Program.cs",
    ROOT / "apps" / "UniversalCouncil.CommandCenter.Core" / "RemoteOwnerGateway.cs",
    ROOT / "apps" / "UniversalCouncil.CommandCenter.Application" / "RemoteOwnerGatewayService.cs",
    ROOT / "apps" / "UniversalCouncil.CommandCenter.Infrastructure" / "RemoteOwnerLocalState.cs",
    ROOT / "tools" / "build_command_center_stage5_projection.py",
    PROJECTION,
    POLICY,
    STATE,
]

for path in required:
    if not path.exists():
        raise SystemExit(f"missing Stage 5 artifact: {path.relative_to(ROOT)}")

presentation_forbidden = {
    "System.IO": "Presentation may not own remote gateway filesystem state",
    "File.Read": "Presentation may not read remote command state directly",
    "File.Write": "Presentation may not write remote command state directly",
    "Process.Start": "Presentation may not launch processes",
    "System.Diagnostics.Process": "Presentation may not own process control",
    "HttpClient": "Presentation may not call transports/providers",
    "HttpListener": "Presentation may not expose a listener",
    "Socket": "Presentation may not open sockets",
    "NamedPipe": "Presentation may not own IPC",
    "powershell": "Presentation may not invoke PowerShell",
    "cmd.exe": "Presentation may not invoke cmd",
    "mcp__": "Presentation may not bind directly to MCP",
    "api_key": "Presentation may not carry credentials",
    "access_token": "Presentation may not carry credentials",
}

for path in list(APP.rglob("*.cs")) + list(APP.rglob("*.xaml")):
    text = path.read_text(encoding="utf-8")
    for token, reason in presentation_forbidden.items():
        if token.lower() in text.lower():
            raise SystemExit(
                f"Stage 5 presentation boundary violation in {path.relative_to(ROOT)}: {token!r} — {reason}"
            )

gateway_forbidden = {
    "Process.Start": "Stage 5 gateway may not dispatch processes",
    "System.Diagnostics.Process": "Stage 5 gateway may not own process execution",
    "HttpClient": "Stage 5 gateway may not call network providers",
    "HttpListener": "Stage 5 gateway may not expose HTTP",
    "TcpListener": "Stage 5 gateway may not expose TCP",
    "WebApplication": "Stage 5 gateway may not host ASP.NET",
    "Kestrel": "Stage 5 gateway may not host Kestrel",
    "System.Net.Sockets": "Stage 5 gateway may not open network sockets",
    "NamedPipeServerStream": "Stage 5 gateway may not expose IPC",
    "PowerShell": "Stage 5 gateway may not invoke PowerShell",
    "cmd.exe": "Stage 5 gateway may not invoke cmd",
    "semantic_invoke": "Stage 5 gateway may not dispatch GUI actions",
    "physical_click": "Stage 5 gateway may not dispatch physical input",
    "remote_shell.execute": "Stage 5 gateway may not dispatch shell authority",
}

gateway_text = "\n".join(path.read_text(encoding="utf-8") for path in GATEWAY_APP.rglob("*.cs"))
for token, reason in gateway_forbidden.items():
    if token.lower() in gateway_text.lower():
        raise SystemExit(f"Stage 5 gateway violation: {token!r} — {reason}")

actual_cases = {
    line.split('"')[1] for line in gateway_text.splitlines() if line.strip().startswith('case "') and '"' in line
}
expected_cases = {
    "status",
    "validate-envelope",
    "enqueue-synthetic",
    "inspect-queue",
    "validate-approval",
}
if actual_cases != expected_cases:
    raise SystemExit(f"RemoteGateway CLI drifted. expected={sorted(expected_cases)} actual={sorted(actual_cases)}")

project = ET.fromstring((APP / "UniversalCouncil.CommandCenter.csproj").read_text(encoding="utf-8"))
refs = {item.attrib.get("Include", "").replace("\\", "/") for item in project.iter("ProjectReference")}
expected_refs = {
    "../UniversalCouncil.CommandCenter.Core/UniversalCouncil.CommandCenter.Core.csproj",
    "../UniversalCouncil.CommandCenter.Host/UniversalCouncil.CommandCenter.Host.csproj",
}
if refs != expected_refs:
    raise SystemExit(f"Presentation references drifted. expected={sorted(expected_refs)} actual={sorted(refs)}")

projection = json.loads(PROJECTION.read_text(encoding="utf-8"))
policy = json.loads(POLICY.read_text(encoding="utf-8"))
state = json.loads(STATE.read_text(encoding="utf-8"))

if projection.get("schema_version") != "1.0" or projection.get("source_type") != "repository_projection":
    raise SystemExit("Stage 5 projection schema/source mismatch")


def blob_sha(relative: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{relative}"],
        cwd=ROOT,
        text=True,
    ).strip()


for source in projection["source_files"]:
    path = ROOT / source["path"]
    if not path.exists():
        raise SystemExit(f"Stage 5 source missing: {source['path']}")
    actual = blob_sha(source["path"])
    if actual != source["blob_sha"]:
        raise SystemExit(f"Stage 5 source drift: {source['path']} expected={source['blob_sha']} actual={actual}")

phase0 = projection["phase0_remote_command_source"]
if phase0["branch"] != "phase0/feasibility-adversarial-prototype":
    raise SystemExit("Stage 5 Phase 0 source branch drifted")
if phase0["head_sha"] != "63a4a446bc1e87f5352915f1e86c463de82e9b81":
    raise SystemExit("Stage 5 Phase 0 source head drifted")

expected_phase0_blobs = {
    "company/runtime/phase0_guardrails.py": "56d76a96c0ab5d74e703f69a53b2cd51d0d2843c",
    "company/config/phase0_feasibility.json": "57b26c4d8fc65c9e866ddefd826784f7826c7f24",
    "company/tests/test_phase0_feasibility.py": "f0ac55efd4e3462e0a1a56b376140db07fd20739",
}
actual_phase0_blobs = {item["path"]: item["blob_sha"] for item in phase0["files"]}
if actual_phase0_blobs != expected_phase0_blobs:
    raise SystemExit("Stage 5 Phase 0 source blob pins drifted")

gateway = projection["gateway"]
for field in (
    "authentication_backend_connected",
    "live_network_listener_enabled",
    "public_internet_exposure_allowed",
    "router_port_forwarding_allowed",
    "github_queue_transport_enabled",
    "chat_transport_enabled",
    "live_execution_authorized",
):
    if gateway[field] is not False:
        raise SystemExit(f"Stage 5 gateway must keep {field}=false")

if gateway["mode"] != "LOCAL_TRUST_GATE_ONLY":
    raise SystemExit("Stage 5 gateway mode drifted")
if gateway["target_host"] != "YASSIN":
    raise SystemExit("Stage 5 target host drifted")
if gateway["phase0_remote_trust_status"] != "IN_TEST":
    raise SystemExit("Stage 5 G0-C truth drifted")

runtime = projection["runtime_truth"]
if any(
    (
        runtime["registered_devices"] != 0,
        runtime["registered_sessions"] != 0,
        runtime["queue_depth"] != 0,
        runtime["phone_connected"],
        runtime["tailscale_connected"],
        runtime["github_transport_connected"],
        runtime["chat_transport_connected"],
    )
):
    raise SystemExit("Stage 5 repository projection fabricates live remote runtime state")

service = projection["service"]
if service["allowed_cli_commands"] != [
    "status",
    "validate-envelope",
    "enqueue-synthetic",
    "inspect-queue",
    "validate-approval",
]:
    raise SystemExit("Stage 5 service allowlist drifted")
if set(service["allowed_cli_commands"]) & set(service["forbidden_cli_commands"]):
    raise SystemExit("Stage 5 forbidden command leaked into allowlist")

trust = projection["trust_contract"]
for field in (
    "owner_authorization_required",
    "authorization_context_must_be_out_of_band",
    "device_id_required",
    "session_id_required",
    "nonce_required",
    "idempotency_key_required",
    "issued_at_required",
    "expiry_required",
    "target_scope_required",
    "effect_scope_required",
    "approval_intent_required",
    "persistent_replay_ledger_required",
):
    if trust[field] is not True:
        raise SystemExit(f"Stage 5 trust invariant missing: {field}")
if trust["replay_policy"] != "FAIL_CLOSED":
    raise SystemExit("Stage 5 replay policy must fail closed")

queue = projection["queue_contract"]
if (
    queue["append_only"] is not True
    or queue["live_dispatch_allowed"] is not False
    or queue["unknown_is_never_success"] is not True
    or queue["execution_state"] != "BLOCKED_PHASE0"
):
    raise SystemExit("Stage 5 queue authority contract drifted")

if policy["live_execution_authorized"] is not False:
    raise SystemExit("Stage 5 policy may not authorize live execution")
if policy["transport"]["live_network_listener_enabled"] is not False:
    raise SystemExit("Stage 5 policy may not enable live network listener")

if state.get("execution_enabled") is not False:
    raise SystemExit("Command Center operational state may not enable execution")

xaml = (APP / "MainWindow.xaml").read_text(encoding="utf-8")
for label in (
    "COMMAND CENTER / STAGE 5",
    "Remote Owner / Secure Command Gateway",
    'Text="{Binding RemoteOwnerConnectionLabel}"',
    "AUTH BACKEND: NOT CONNECTED",
    "NETWORK LISTENER: OFF",
    "EXECUTION: BLOCKED_PHASE0",
    "Stage 6 — Authenticated Local / Tailscale Transport Pilot",
):
    if label not in xaml:
        raise SystemExit(f"Stage 5 UI truth label missing: {label}")

if xaml.count("<ScrollViewer") != 1:
    raise SystemExit("Stage 5 must preserve one root ScrollViewer")

print("Command Center Stage 5 static validation: PASS")
