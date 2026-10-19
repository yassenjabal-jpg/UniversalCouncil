from __future__ import annotations

import json
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "UniversalCouncil.CommandCenter"
TRANSPORT_APP = ROOT / "apps" / "UniversalCouncil.CommandCenter.RemoteTransport"
PROJECTION = ROOT / "state" / "command-center" / "remote-transport.json"
POLICY = ROOT / "state" / "command-center" / "remote-transport-policy.json"
STATE = ROOT / "state" / "command-center" / "command-center-state.json"

required = [
    APP / "MainWindow.xaml",
    APP / "MainWindow.xaml.cs",
    APP / "MainWindowViewModel.cs",
    TRANSPORT_APP / "RemoteTransportHost.cs",
    TRANSPORT_APP / "Program.cs",
    ROOT / "apps" / "UniversalCouncil.CommandCenter.Core" / "RemoteTransport.cs",
    ROOT / "apps" / "UniversalCouncil.CommandCenter.Application" / "RemoteTransportProjectionService.cs",
    ROOT / "apps" / "UniversalCouncil.CommandCenter.Infrastructure" / "JsonRemoteTransportReader.cs",
    ROOT / "tools" / "build_command_center_stage6_projection.py",
    PROJECTION,
    POLICY,
    STATE,
]

for path in required:
    if not path.exists():
        raise SystemExit(f"missing Stage 6 artifact: {path.relative_to(ROOT)}")

presentation_forbidden = {
    "System.IO": "Presentation may not own transport filesystem state",
    "File.Read": "Presentation may not read transport state directly",
    "File.Write": "Presentation may not write transport state directly",
    "HttpClient": "Presentation may not call transport endpoints",
    "WebApplication": "Presentation may not host HTTP",
    "Kestrel": "Presentation may not host Kestrel",
    "Process.Start": "Presentation may not launch processes",
    "Socket": "Presentation may not open sockets",
    "NamedPipe": "Presentation may not own IPC",
    "PowerShell": "Presentation may not invoke PowerShell",
    "cmd.exe": "Presentation may not invoke cmd",
}

for path in list(APP.rglob("*.cs")) + list(APP.rglob("*.xaml")):
    text = path.read_text(encoding="utf-8")
    for token, reason in presentation_forbidden.items():
        if token.lower() in text.lower():
            raise SystemExit(
                f"Stage 6 presentation boundary violation in {path.relative_to(ROOT)}: {token!r} — {reason}"
            )

transport_text = "\n".join(path.read_text(encoding="utf-8") for path in TRANSPORT_APP.rglob("*.cs"))
transport_forbidden = {
    "IPAddress.Any": "public wildcard bind is forbidden",
    "IPAddress.IPv6Any": "IPv6 wildcard bind is forbidden",
    "ListenAnyIP": "public wildcard listener is forbidden",
    "0.0.0.0": "public wildcard address is forbidden",
    "UseUrls": "free-form URL binding is forbidden",
    "tailscale serve": "product may not invoke Tailscale CLI",
    "tailscale funnel": "public Funnel is forbidden",
    "Process.Start": "transport may not execute processes",
    "System.Diagnostics.Process": "transport may not own process execution",
    "PowerShell": "transport may not invoke PowerShell",
    "cmd.exe": "transport may not invoke cmd",
    "semantic_invoke": "transport may not dispatch GUI",
    "physical_click": "transport may not dispatch physical input",
    "remote_shell.execute": "transport may not dispatch shell authority",
    "ExecutionService": "transport may not reference Execution Service",
    "AddCors": "Stage 6 CORS must remain disabled",
    "UseCors": "Stage 6 CORS must remain disabled",
    "AllowAnyOrigin": "Stage 6 CORS must remain disabled",
}
for token, reason in transport_forbidden.items():
    if token.lower() in transport_text.lower():
        raise SystemExit(f"Stage 6 transport violation: {token!r} — {reason}")

if "IPAddress.Loopback" not in transport_text:
    raise SystemExit("Stage 6 transport must bind explicitly to IPAddress.Loopback")

transport_project = ET.fromstring(
    (TRANSPORT_APP / "UniversalCouncil.CommandCenter.RemoteTransport.csproj").read_text(encoding="utf-8")
)
project_refs = {
    item.attrib.get("Include", "").replace("\\", "/") for item in transport_project.iter("ProjectReference")
}
expected_refs = {
    "../UniversalCouncil.CommandCenter.Core/UniversalCouncil.CommandCenter.Core.csproj",
    "../UniversalCouncil.CommandCenter.Application/UniversalCouncil.CommandCenter.Application.csproj",
    "../UniversalCouncil.CommandCenter.Infrastructure/UniversalCouncil.CommandCenter.Infrastructure.csproj",
}
if project_refs != expected_refs:
    raise SystemExit(
        f"RemoteTransport project references drifted. expected={sorted(expected_refs)} actual={sorted(project_refs)}"
    )

framework_refs = {item.attrib.get("Include", "") for item in transport_project.iter("FrameworkReference")}
if framework_refs != {"Microsoft.AspNetCore.App"}:
    raise SystemExit("RemoteTransport must use only Microsoft.AspNetCore.App framework reference")

app_project = ET.fromstring((APP / "UniversalCouncil.CommandCenter.csproj").read_text(encoding="utf-8"))
app_refs = {item.attrib.get("Include", "").replace("\\", "/") for item in app_project.iter("ProjectReference")}
if app_refs != {
    "../UniversalCouncil.CommandCenter.Core/UniversalCouncil.CommandCenter.Core.csproj",
    "../UniversalCouncil.CommandCenter.Host/UniversalCouncil.CommandCenter.Host.csproj",
}:
    raise SystemExit("Presentation project references drifted")

projection = json.loads(PROJECTION.read_text(encoding="utf-8"))
policy = json.loads(POLICY.read_text(encoding="utf-8"))
state = json.loads(STATE.read_text(encoding="utf-8"))

if projection.get("schema_version") != "1.0" or projection.get("source_type") != "repository_projection":
    raise SystemExit("Stage 6 projection schema/source mismatch")


def blob_sha(relative: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{relative}"],
        cwd=ROOT,
        text=True,
    ).strip()


for source in projection["source_files"]:
    actual = blob_sha(source["path"])
    if actual != source["blob_sha"]:
        raise SystemExit(f"Stage 6 source drift: {source['path']} expected={source['blob_sha']} actual={actual}")

transport = projection["transport"]
if (
    transport["mode"] != "LOOPBACK_AUTHENTICATED_PILOT"
    or transport["target_host"] != "YASSIN"
    or transport["listener_configured"] is not True
    or transport["runtime_listener_active"] is not False
    or transport["listener_scope"] != "LOOPBACK_ONLY"
    or transport["allowed_bind_addresses"] != ["127.0.0.1", "::1"]
    or transport["public_bind_allowed"] is not False
    or transport["router_port_forwarding_allowed"] is not False
    or transport["tailscale_connected"] is not False
    or transport["tailscale_serve_configured"] is not False
    or transport["tailscale_funnel_allowed"] is not False
    or transport["phone_connected"] is not False
):
    raise SystemExit("Stage 6 transport truth drifted")

auth = projection["authentication"]
if (
    auth["backend"] != "LOCAL_HASHED_SESSION_TOKEN"
    or auth["bearer_token_required"] is not True
    or auth["device_header_required"] is not True
    or auth["session_header_required"] is not True
    or auth["token_plaintext_persisted"] is not False
    or auth["minimum_token_entropy_bytes"] < 32
    or auth["short_lived_sessions_required"] is not True
    or auth["max_session_ttl_minutes"] > 60
    or auth["revocation_required"] is not True
):
    raise SystemExit("Stage 6 authentication contract drifted")

authority = projection["authority"]
if (
    authority["command_queue_acceptance_grants_execution"] is not False
    or authority["approval_transport_grants_execution"] is not False
    or authority["phase0_bypass_allowed"] is not False
    or authority["live_execution_authorized"] is not False
    or authority["execution_state_after_transport_acceptance"] != "BLOCKED_PHASE0"
):
    raise SystemExit("Stage 6 authority contract drifted")

if policy["transport"]["tailscale_funnel_allowed"] is not False:
    raise SystemExit("Stage 6 policy may not allow Tailscale Funnel")
if state.get("execution_enabled") is not False:
    raise SystemExit("Command Center operational state may not enable execution")

xaml = (APP / "MainWindow.xaml").read_text(encoding="utf-8")
for label in (
    "COMMAND CENTER / STAGE 6",
    "Authenticated Local Transport",
    "127.0.0.1 / ::1 ONLY",
    "PUBLIC BIND: FORBIDDEN",
    'Text="{Binding RemoteTransportRuntimeLabel}"',
    'Text="{Binding RemoteTransportTailnetLabel}"',
    'Text="{Binding RemoteTransportPhoneLabel}"',
    'Text="{Binding RemoteTransportExecutionLabel}"',
):
    if label not in xaml:
        raise SystemExit(f"Stage 6 UI truth label missing: {label}")

if xaml.count("<ScrollViewer") != 1:
    raise SystemExit("Stage 6 must preserve one root ScrollViewer")

print("Command Center Stage 6 static validation: PASS")
