from __future__ import annotations

import json
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "UniversalCouncil.CommandCenter"
ENROLLMENT_APP = ROOT / "apps" / "UniversalCouncil.CommandCenter.OwnerEnrollment"
ENROLLMENT_INFRA = ROOT / "apps" / "UniversalCouncil.CommandCenter.Infrastructure" / "JsonOwnerEnrollmentRegistry.cs"
POLICY = ROOT / "state" / "command-center" / "owner-device-tailnet-policy.json"
PROJECTION = ROOT / "state" / "command-center" / "owner-device-tailnet.json"
REMOTE_TRANSPORT = ROOT / "state" / "command-center" / "remote-transport.json"
SERVE_SCRIPT = ROOT / "tools" / "stage7_configure_tailscale_serve.ps1"
PROBE_SCRIPT = ROOT / "tools" / "stage7_yassin_probe.ps1"
START_SCRIPT = ROOT / "tools" / "stage7_start_remote_transport.ps1"
STATE = ROOT / "state" / "command-center" / "command-center-state.json"

required = [
    APP / "MainWindow.xaml",
    APP / "MainWindow.xaml.cs",
    APP / "MainWindowViewModel.cs",
    ENROLLMENT_APP / "Program.cs",
    ENROLLMENT_INFRA,
    POLICY,
    PROJECTION,
    REMOTE_TRANSPORT,
    SERVE_SCRIPT,
    PROBE_SCRIPT,
    START_SCRIPT,
    ROOT / "tools" / "build_command_center_stage7_projection.py",
    STATE,
]

for path in required:
    if not path.exists():
        raise SystemExit(f"missing Stage 7 artifact: {path.relative_to(ROOT)}")

presentation_forbidden = {
    "System.IO": "Presentation may not own Stage 7 persistence",
    "File.Read": "Presentation may not read Stage 7 files directly",
    "File.Write": "Presentation may not write Stage 7 files directly",
    "HttpClient": "Presentation may not call the tailnet transport directly",
    "WebApplication": "Presentation may not host HTTP",
    "Kestrel": "Presentation may not host Kestrel",
    "Process.Start": "Presentation may not launch host processes",
    "PowerShell": "Presentation may not invoke PowerShell",
}

for path in list(APP.rglob("*.cs")) + list(APP.rglob("*.xaml")):
    text = path.read_text(encoding="utf-8")
    for token, reason in presentation_forbidden.items():
        if token.lower() in text.lower():
            raise SystemExit(
                f"Stage 7 presentation boundary violation in {path.relative_to(ROOT)}: {token!r} — {reason}"
            )

enrollment_infra = ENROLLMENT_INFRA.read_text(encoding="utf-8")
if "BearerToken" in enrollment_infra:
    raise SystemExit("Enrollment persistence may not reference plaintext bearer tokens")
if "TokenSha256" not in enrollment_infra:
    raise SystemExit("Enrollment persistence must store token SHA-256")

serve = SERVE_SCRIPT.read_text(encoding="utf-8")
probe = PROBE_SCRIPT.read_text(encoding="utf-8")
starter = START_SCRIPT.read_text(encoding="utf-8")

for text, label in ((serve, "serve"), (probe, "probe"), (starter, "starter")):
    if "0.0.0.0" in text or "IPAddress.Any" in text or "ListenAnyIP" in text:
        raise SystemExit(f"Stage 7 {label} script contains a public bind path")

if "http://127.0.0.1:$LocalPort" not in serve:
    raise SystemExit("Stage 7 Serve script must target the loopback backend")
if "serve --bg --yes $target" not in serve:
    raise SystemExit("Stage 7 Serve script must use the bounded background Serve path")
if "funnel status --json" not in serve:
    raise SystemExit("Stage 7 Serve script must check for existing Funnel configuration")
for forbidden in ("funnel --bg", "funnel --yes", "funnel 443", "funnel http"):
    if forbidden in serve.lower():
        raise SystemExit(f"Stage 7 Serve script may not enable Funnel: {forbidden}")

if "peer_list_persisted = $false" not in probe:
    raise SystemExit("Stage 7 host probe must explicitly avoid peer-list persistence")
if "auth_key_persisted = $false" not in probe:
    raise SystemExit("Stage 7 host probe must explicitly avoid auth-key persistence")
if "bearer_token_persisted = $false" not in probe:
    raise SystemExit("Stage 7 host probe must explicitly avoid bearer-token persistence")

if "127.0.0.1" not in starter:
    raise SystemExit("Stage 7 starter must verify loopback health")

owner_project = ET.fromstring(
    (ENROLLMENT_APP / "UniversalCouncil.CommandCenter.OwnerEnrollment.csproj").read_text(encoding="utf-8")
)
owner_refs = {item.attrib.get("Include", "").replace("\\", "/") for item in owner_project.iter("ProjectReference")}
expected_owner_refs = {
    "../UniversalCouncil.CommandCenter.Core/UniversalCouncil.CommandCenter.Core.csproj",
    "../UniversalCouncil.CommandCenter.Application/UniversalCouncil.CommandCenter.Application.csproj",
    "../UniversalCouncil.CommandCenter.Infrastructure/UniversalCouncil.CommandCenter.Infrastructure.csproj",
}
if owner_refs != expected_owner_refs:
    raise SystemExit("OwnerEnrollment project references drifted")

policy = json.loads(POLICY.read_text(encoding="utf-8"))
projection = json.loads(PROJECTION.read_text(encoding="utf-8"))
transport = json.loads(REMOTE_TRANSPORT.read_text(encoding="utf-8"))
state = json.loads(STATE.read_text(encoding="utf-8"))

if projection.get("schema_version") != "1.0" or projection.get("source_type") != "repository_projection":
    raise SystemExit("Stage 7 projection schema/source mismatch")


def blob_sha(relative: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{relative}"],
        cwd=ROOT,
        text=True,
    ).strip()


for source in projection["source_files"]:
    actual = blob_sha(source["path"])
    if actual != source["blob_sha"]:
        raise SystemExit(f"Stage 7 source drift: {source['path']} expected={source['blob_sha']} actual={actual}")

runtime = projection["runtime"]
if (
    runtime["mode"] != "OWNER_DEVICE_ENROLLMENT_TAILNET_PILOT"
    or runtime["target_host"] != "YASSIN"
    or runtime["required_stage6_mode"] != "LOOPBACK_AUTHENTICATED_PILOT"
    or runtime["required_local_bind"] != "127.0.0.1"
    or runtime["required_local_port"] != 47721
    or runtime["public_bind_allowed"] is not False
    or runtime["router_port_forwarding_allowed"] is not False
    or runtime["cors_allowed"] is not False
    or runtime["tailscale_funnel_allowed"] is not False
    or runtime["execution_authorized"] is not False
    or runtime["execution_state"] != "BLOCKED_PHASE0"
):
    raise SystemExit("Stage 7 runtime truth drifted")

owner = projection["owner_device"]
if (
    owner["device_enrolled"] is not False
    or owner["active_session_issued"] is not False
    or owner["phone_round_trip_proven"] is not False
    or owner["session_plaintext_persisted"] is not False
    or owner["session_token_minimum_entropy_bytes"] < 32
    or owner["session_ttl_max_minutes"] > 60
):
    raise SystemExit("Stage 7 repository projection fabricated owner-device success")

tailnet = projection["tailscale"]
if (
    tailnet["installation_state"] != "UNKNOWN"
    or tailnet["connection_state"] != "UNKNOWN"
    or tailnet["serve_configuration_state"] != "NOT_CONFIGURED"
    or tailnet["expected_backend"] != "http://127.0.0.1:47721"
    or tailnet["funnel_forbidden"] is not True
    or tailnet["host_probe_proven"] is not False
    or tailnet["tailnet_round_trip_proven"] is not False
):
    raise SystemExit("Stage 7 repository projection fabricated tailnet evidence")

gates = projection["gates"]
if gates["stage7_ci_foundation_passed"] is not True:
    raise SystemExit("Stage 7 exact-head CI foundation must remain verified")
for pending_gate in (
    "yassin_host_probe_passed",
    "owner_device_enrollment_passed",
    "tailscale_private_serve_passed",
    "real_owner_phone_round_trip_passed",
    "session_revocation_round_trip_passed",
):
    if gates[pending_gate] is not False:
        raise SystemExit(f"Stage 7 repository projection fabricated real-host/device success: {pending_gate}")
if gates["live_execution_authorized"] is not False:
    raise SystemExit("Stage 7 repository projection may not authorize live execution")

host = projection["host_evidence"]
if (
    host["yassin_remote_agent_seen_online"] is not True
    or host["remote_command_channel_state"] != "DEVICE_OFFLINE_AND_TOOL_QUOTA_BLOCKED"
    or host["tailscale_status_observed"] is not False
    or host["remote_transport_deployed_to_yassin"] is not False
    or host["remote_transport_running_on_yassin"] is not False
    or host["serve_running_on_yassin"] is not False
):
    raise SystemExit("Stage 7 host-evidence truth drifted")

if transport["transport"]["public_bind_allowed"] is not False:
    raise SystemExit("Stage 7 inherited Stage 6 public-bind lock drifted")
if transport["authority"]["live_execution_authorized"] is not False:
    raise SystemExit("Stage 7 inherited Stage 6 execution lock drifted")
if policy["transport_base"]["tailscale_funnel_allowed"] is not False:
    raise SystemExit("Stage 7 policy may not allow Funnel")
if state.get("execution_enabled") is not False:
    raise SystemExit("Command Center state may not enable execution")

xaml = (APP / "MainWindow.xaml").read_text(encoding="utf-8")
for label in (
    "COMMAND CENTER / STAGE 7",
    "Owner Device + Private Tailnet",
    "ONLINE OBSERVED / HOST COMMANDS BLOCKED",
    "FUNNEL / PUBLIC BIND: FORBIDDEN",
    'Text="{Binding Stage7HostAccessLabel}"',
    'Text="{Binding Stage7TailscaleLabel}"',
    'Text="{Binding Stage7EnrollmentLabel}"',
    'Text="{Binding Stage7PhoneLabel}"',
    'Text="{Binding Stage7ExecutionLabel}"',
):
    if label not in xaml:
        raise SystemExit(f"Stage 7 UI truth label missing: {label}")

if xaml.count("<ScrollViewer") != 1:
    raise SystemExit("Stage 7 must preserve one root ScrollViewer")

print("Command Center Stage 7 static validation: PASS")
