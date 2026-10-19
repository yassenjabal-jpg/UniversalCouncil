from __future__ import annotations

import subprocess
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "UniversalCouncil.CommandCenter"
CATALOG = ROOT / "state" / "command-center" / "orchestration-catalog.json"
STATE = ROOT / "state" / "command-center" / "command-center-state.json"

required = [
    APP / "MainWindow.xaml",
    APP / "MainWindow.xaml.cs",
    APP / "MainWindowViewModel.cs",
    ROOT / "apps" / "UniversalCouncil.CommandCenter.Application" / "OrchestrationService.cs",
    ROOT / "apps" / "UniversalCouncil.CommandCenter.Infrastructure" / "JsonOrchestrationCatalogReader.cs",
    ROOT / "apps" / "UniversalCouncil.CommandCenter.Host" / "CommandCenterComposition.cs",
    ROOT / "tools" / "build_command_center_stage3_projection.py",
    CATALOG,
    STATE,
]

for path in required:
    if not path.exists():
        raise SystemExit(f"missing Stage 3 artifact: {path.relative_to(ROOT)}")

presentation_forbidden = {
    "System.IO": "Presentation may not read/write files directly",
    "File.Read": "Presentation may not read repository/runtime files directly",
    "Process.Start": "Presentation may not launch processes",
    "System.Diagnostics.Process": "Presentation may not own process control",
    "HttpClient": "Presentation may not call providers directly",
    "powershell": "Presentation may not invoke PowerShell",
    "cmd.exe": "Presentation may not invoke cmd",
    "mcp__": "Presentation may not bind directly to MCP",
    "api_key": "Presentation may not carry credentials",
    "access_token": "Presentation may not carry credentials",
    "OpenAI": "Presentation may not bind directly to a model provider",
    "Anthropic": "Presentation may not bind directly to a model provider",
    "Gemini": "Presentation may not bind directly to a model provider",
}

for path in list(APP.rglob("*.cs")) + list(APP.rglob("*.xaml")):
    text = path.read_text(encoding="utf-8")
    for token, reason in presentation_forbidden.items():
        if token.lower() in text.lower():
            raise SystemExit(
                f"Stage 3 presentation boundary violation in {path.relative_to(ROOT)}: "
                f"{token!r} — {reason}"
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

catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
if catalog.get("schema_version") != "1.0" or catalog.get("source_type") != "repository_projection":
    raise SystemExit("Stage 3 catalog schema/source mismatch")

def git_blob_sha(relative: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{relative}"],
        cwd=ROOT,
        text=True,
    ).strip()

for source in catalog["source_files"]:
    source_path = ROOT / source["path"]
    if not source_path.exists():
        raise SystemExit(f"catalog source missing: {source['path']}")
    actual = git_blob_sha(source["path"])
    if actual != source["blob_sha"]:
        raise SystemExit(
            f"catalog source digest drift: {source['path']} expected={source['blob_sha']} actual={actual}"
        )

all_roles = catalog["council"]["core_roles"] + catalog["council"]["specialist_roles"]
if any(
    role["may_execute_tools"] or role["may_mutate_authority"] or role["may_self_approve"]
    for role in all_roles
):
    raise SystemExit("Stage 3 catalog contains authority-inflated Council role")

if catalog["council"]["free_text_keyword_routing"] is not False:
    raise SystemExit("free-text authority routing must remain disabled")

model = catalog["model_control"]
if (
    model["role_model_separation"] is not True
    or model["owner_controlled_selection"] is not True
    or model["silent_fallback_allowed"] is not False
    or model["provider_calls_connected"] is not False
):
    raise SystemExit("unsafe Stage 3 model-control policy")

runtime = catalog["runtime"]
if (
    runtime["task_state"] != "NO_LIVE_TASK"
    or runtime["active_council_roles"]
    or runtime["active_studio_department"] is not None
    or runtime["active_model"] is not None
    or runtime["provider_call_in_flight"] is not False
):
    raise SystemExit("Stage 3 may not fabricate active orchestration")

studio = catalog["studio"]
if studio["master_pipeline_contract"]["phase_sequence"] != [
    "writing", "pre_production", "production"
]:
    raise SystemExit("Studio macro-phase sequence drifted")
if studio["handoff_contract"]["downstream_direct_repair_forbidden"] is not True:
    raise SystemExit("downstream direct repair must remain forbidden")
if studio["stage_execution_contract"]["exactly_one_primary_program"] is not True:
    raise SystemExit("one-stage-one-program invariant missing")
if len(studio["departments"]) != 12:
    raise SystemExit("unexpected Studio department count")
if len(studio["return_ticket_required_fields"]) < 9:
    raise SystemExit("return-ticket contract incomplete")

state = json.loads(STATE.read_text(encoding="utf-8"))
if state.get("execution_enabled") is not False:
    raise SystemExit("Stage 3 operational state may not enable execution")

xaml = (APP / "MainWindow.xaml").read_text(encoding="utf-8")
for required_label in (
    "COMMAND CENTER / STAGE 3",
    "ROLE ≠ MODEL",
    "Model Control",
    "الاستوديو",
    "المجلس",
    "Stage 4 — YASSIN Execution Service + Provider Fabric",
):
    if required_label not in xaml:
        raise SystemExit(f"Stage 3 UI label missing: {required_label}")

if xaml.count("<ScrollViewer") != 1:
    raise SystemExit("Stage 3 must preserve one root content ScrollViewer")

print("Command Center Stage 3 static validation: PASS")
