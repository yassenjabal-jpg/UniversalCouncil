from __future__ import annotations

import json
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "UniversalCouncil.CommandCenter"
SERVICE = ROOT / "apps" / "UniversalCouncil.CommandCenter.ExecutionService"
FABRIC = ROOT / "state" / "command-center" / "execution-fabric.json"
PHASE0 = ROOT / "state" / "command-center" / "phase0-execution-gates.json"
STATE = ROOT / "state" / "command-center" / "command-center-state.json"

required = [
    APP / "MainWindow.xaml",
    APP / "MainWindowViewModel.cs",
    APP / "App.xaml.cs",
    SERVICE / "Program.cs",
    ROOT / "apps" / "UniversalCouncil.CommandCenter.Application" / "ExecutionFabricService.cs",
    ROOT / "apps" / "UniversalCouncil.CommandCenter.Infrastructure" / "JsonExecutionFabricReader.cs",
    ROOT / "apps" / "UniversalCouncil.CommandCenter.Infrastructure" / "LocalExecutionPrimitives.cs",
    ROOT / "tools" / "build_command_center_stage4_projection.py",
    FABRIC,
    PHASE0,
    STATE,
]

for path in required:
    if not path.exists():
        raise SystemExit(f"missing Stage 4 artifact: {path.relative_to(ROOT)}")

presentation_forbidden = {
    "System.IO": "Presentation may not own filesystem execution state",
    "File.Read": "Presentation may not read execution files directly",
    "File.Write": "Presentation may not write execution files directly",
    "Process.Start": "Presentation may not launch processes",
    "System.Diagnostics.Process": "Presentation may not own process control",
    "HttpClient": "Presentation may not call providers",
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
                f"Stage 4 presentation boundary violation in {path.relative_to(ROOT)}: "
                f"{token!r} — {reason}"
            )

service_forbidden = {
    "Process.Start": "Stage 4 service may not dispatch processes",
    "System.Diagnostics.Process": "Stage 4 service may not own process execution",
    "HttpClient": "Stage 4 service may not dispatch network providers",
    "System.Net.Sockets": "Stage 4 service may not open network sockets",
    "NamedPipeServerStream": "Stage 4 service may not expose IPC yet",
    "PowerShell": "Stage 4 service may not invoke PowerShell",
    "cmd.exe": "Stage 4 service may not invoke cmd",
    "semantic_invoke": "Stage 4 service may not dispatch GUI actions",
    "physical_click": "Stage 4 service may not dispatch physical input",
}

service_text = "\n".join(
    path.read_text(encoding="utf-8")
    for path in SERVICE.rglob("*.cs")
)
for token, reason in service_forbidden.items():
    if token.lower() in service_text.lower():
        raise SystemExit(f"Stage 4 service dispatch violation: {token!r} — {reason}")

allowed_cases = {
    line.split('"')[1]
    for line in service_text.splitlines()
    if line.strip().startswith('case "') and '"' in line
}
expected_cases = {
    "status",
    "validate-manifest",
    "inspect-provider-registry",
    "validate-receipt",
}
if allowed_cases != expected_cases:
    raise SystemExit(
        f"ExecutionService CLI drifted. expected={sorted(expected_cases)} actual={sorted(allowed_cases)}"
    )

project = ET.fromstring((APP / "UniversalCouncil.CommandCenter.csproj").read_text(encoding="utf-8"))
refs = {
    item.attrib.get("Include", "").replace("\\", "/")
    for item in project.iter("ProjectReference")
}
expected_refs = {
    "../UniversalCouncil.CommandCenter.Core/UniversalCouncil.CommandCenter.Core.csproj",
    "../UniversalCouncil.CommandCenter.Host/UniversalCouncil.CommandCenter.Host.csproj",
}
if refs != expected_refs:
    raise SystemExit(
        f"Presentation references drifted. expected={sorted(expected_refs)} actual={sorted(refs)}"
    )

fabric = json.loads(FABRIC.read_text(encoding="utf-8"))
phase0 = json.loads(PHASE0.read_text(encoding="utf-8"))
state = json.loads(STATE.read_text(encoding="utf-8"))

if fabric.get("schema_version") != "1.0" or fabric.get("source_type") != "repository_projection":
    raise SystemExit("Stage 4 execution fabric schema/source mismatch")

def blob_sha(relative: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{relative}"],
        cwd=ROOT,
        text=True,
    ).strip()

for source in fabric["source_files"]:
    path = ROOT / source["path"]
    if not path.exists():
        raise SystemExit(f"execution-fabric source missing: {source['path']}")
    actual = blob_sha(source["path"])
    if actual != source["blob_sha"]:
        raise SystemExit(
            f"execution-fabric source drift: {source['path']} expected={source['blob_sha']} actual={actual}"
        )

if phase0["source_head_sha"] != "63a4a446bc1e87f5352915f1e86c463de82e9b81":
    raise SystemExit("Phase 0 source head drifted without contract update")
if phase0["status_blob_sha"] != "454f07f73a631627eae2eff2f8c229c8eb270ee1":
    raise SystemExit("Phase 0 status blob drifted without contract update")
if phase0["live_execution_authorized"] is not False:
    raise SystemExit("Stage 4 Phase 0 projection may not authorize live execution")
if all(item["status"] == "PASS" for item in phase0["gates"].values()):
    raise SystemExit("Stage 4 cannot silently transition after all Phase 0 gates PASS")

service = fabric["service"]
if service["mode"] != "SAFE_DISABLED" or service["live_dispatch_enabled"] is not False:
    raise SystemExit("Stage 4 service must remain SAFE_DISABLED")
if service["target_host"] != "YASSIN":
    raise SystemExit("Stage 4 target host drifted")
if service["allowed_cli_commands"] != [
    "status",
    "validate-manifest",
    "inspect-provider-registry",
    "validate-receipt",
]:
    raise SystemExit("Stage 4 CLI allowlist drifted")
if set(service["allowed_cli_commands"]) & set(service["forbidden_cli_commands"]):
    raise SystemExit("forbidden CLI command leaked into allowlist")

providers = fabric["providers"]
if any(item["can_execute"] for item in providers):
    raise SystemExit("Stage 4 provider advertises execute capability")
dc = next((item for item in providers if item["id"] == "dc_control_plane"), None)
if not dc or dc["role"] != "LEGACY_REFERENCE_PROVIDER" or dc["state"] != "BLOCKED_BY_PROVIDER_LIMIT":
    raise SystemExit("Desktop Commander role/state drifted")
native = next((item for item in providers if item["id"] == "native_host_tooling"), None)
if not native or native["state"] != "DESIGN_ONLY" or native["can_execute"]:
    raise SystemExit("native host tooling must remain design-only in Stage 4")

recovery = fabric["recovery"]
for field in (
    "unknown_is_never_success",
    "stop_on_unknown",
    "unknown_requires_reconciliation",
    "single_physical_controller",
):
    if recovery[field] is not True:
        raise SystemExit(f"Stage 4 recovery invariant missing: {field}")
if recovery["replay_completed_action_default"] is not False:
    raise SystemExit("completed/unknown actions may not replay by default")

if state.get("execution_enabled") is not False:
    raise SystemExit("Command Center operational state may not enable execution")

xaml = (APP / "MainWindow.xaml").read_text(encoding="utf-8")
for label in (
    "COMMAND CENTER / STAGE 4",
    "Execution Fabric",
    "LIVE DISPATCH: DISABLED",
    "Desktop Commander محفوظ كمرجع قديم فقط",
    "Stage 5 — Remote Owner + Secure Command Gateway",
):
    if label not in xaml:
        raise SystemExit(f"Stage 4 UI truth label missing: {label}")

if xaml.count("<ScrollViewer") != 1:
    raise SystemExit("Stage 4 must preserve one root ScrollViewer")

print("Command Center Stage 4 static validation: PASS")
