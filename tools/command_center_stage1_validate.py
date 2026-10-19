from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "UniversalCouncil.CommandCenter"

FORBIDDEN_TOKENS = {
    "Process.Start": "UI may not launch processes",
    "System.Diagnostics.Process": "UI may not own process control",
    "powershell": "UI may not invoke PowerShell",
    "cmd.exe": "UI may not invoke cmd",
    "HttpClient": "UI may not call external services directly",
    "System.Net.Http": "UI may not call external services directly",
    "Octokit": "UI may not own GitHub clients",
    "api_key": "UI may not embed API keys",
    "access_token": "UI may not embed access tokens",
    "desktop_computer_use": "UI may not invoke computer-use providers",
    "mcp__": "UI may not bind directly to MCP/provider tools",
}

required = [
    APP / "MainWindow.xaml",
    APP / "MainWindow.xaml.cs",
    APP / "PrototypeCommandCenterSnapshotProvider.cs",
    ROOT / "apps" / "UniversalCouncil.CommandCenter.Core" / "CommandCenterSnapshot.cs",
]

for path in required:
    if not path.exists():
        raise SystemExit(f"missing required Stage 1 artifact: {path.relative_to(ROOT)}")

sources = []
for pattern in ("*.cs", "*.xaml", "*.csproj"):
    sources.extend(APP.rglob(pattern))

for path in sources:
    text = path.read_text(encoding="utf-8")
    for token, reason in FORBIDDEN_TOKENS.items():
        if token.lower() in text.lower():
            raise SystemExit(
                f"Stage 1 architecture boundary violation in {path.relative_to(ROOT)}: "
                f"{token!r} — {reason}"
            )

xaml = (APP / "MainWindow.xaml").read_text(encoding="utf-8")
provider = (APP / "PrototypeCommandCenterSnapshotProvider.cs").read_text(encoding="utf-8")
truth_surface = xaml + "\n" + provider
for required_label in (
    "بوابة التنفيذ مقفولة",
    "LOCKED BY PHASE 0",
    "لا توجد حالات تشغيل وهمية",
):
    if required_label not in truth_surface:
        raise SystemExit(f"Stage 1 truthfulness label missing: {required_label}")

if xaml.count("ScrollViewer") != 2:
    raise SystemExit("Stage 1 shell must use one explicit root ScrollViewer element")

print("Command Center Stage 1 static validation: PASS")
