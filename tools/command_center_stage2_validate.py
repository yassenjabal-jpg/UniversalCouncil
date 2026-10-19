from __future__ import annotations

import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "UniversalCouncil.CommandCenter"
STATE = ROOT / "state" / "command-center" / "command-center-state.json"

required = [
    APP / "MainWindow.xaml",
    APP / "MainWindow.xaml.cs",
    APP / "MainWindowViewModel.cs",
    ROOT / "apps" / "UniversalCouncil.CommandCenter.Application" / "OperationalStateService.cs",
    ROOT / "apps" / "UniversalCouncil.CommandCenter.Infrastructure" / "JsonOperationalStateReader.cs",
    ROOT / "apps" / "UniversalCouncil.CommandCenter.Host" / "CommandCenterComposition.cs",
    STATE,
]

for path in required:
    if not path.exists():
        raise SystemExit(f"missing Stage 2 artifact: {path.relative_to(ROOT)}")

presentation_forbidden = {
    "System.IO": "Presentation may not read/write files directly",
    "File.Read": "Presentation may not read files directly",
    "Process.Start": "Presentation may not launch processes",
    "System.Diagnostics.Process": "Presentation may not own process control",
    "HttpClient": "Presentation may not call services directly",
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
                f"Stage 2 presentation boundary violation in {path.relative_to(ROOT)}: "
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
        f"Presentation project references drifted. expected={sorted(expected_refs)} actual={sorted(refs)}"
    )

state = json.loads(STATE.read_text(encoding="utf-8"))
if state.get("schema_version") != "1.0":
    raise SystemExit("Stage 2 bundled state must use schema 1.0")
if state.get("source_type") != "repository_projection":
    raise SystemExit("Stage 2 bundled state source type must be repository_projection")
if state.get("execution_enabled") is not False:
    raise SystemExit("Stage 2 bundled state may never enable execution")
if state.get("usage", {}).get("state") == "NOT_CONNECTED":
    if state["usage"].get("recorded_cost_usd") is not None:
        raise SystemExit("Unconnected usage source may not invent recorded cost")

xaml = (APP / "MainWindow.xaml").read_text(encoding="utf-8")
for required_label in (
    "COMMAND CENTER / STAGE 2",
    "بوابة التنفيذ مقفولة",
    "لا توجد حالات تشغيل وهمية",
    "سجل الأدلة",
    "مكتب المالك",
    "NO EXECUTION AUTHORIZED",
):
    # NO EXECUTION AUTHORIZED may arrive through a binding rather than literal XAML.
    if required_label == "NO EXECUTION AUTHORIZED":
        state_text = STATE.read_text(encoding="utf-8")
        if required_label not in state_text:
            raise SystemExit(f"Stage 2 truth label missing: {required_label}")
    elif required_label not in xaml:
        raise SystemExit(f"Stage 2 UI label missing: {required_label}")

if xaml.count("<ScrollViewer") != 1:
    raise SystemExit("Stage 2 must keep one root content ScrollViewer")

print("Command Center Stage 2 static validation: PASS")
