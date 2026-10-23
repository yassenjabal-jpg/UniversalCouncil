from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "motion-platform" / "mp4-reference-integration.json"
SPEC = ROOT / "docs" / "operations" / "motion-platform" / "09_MP4_REFERENCE_INTEGRATION.md"
COMMAND_PROJECT = ROOT / "apps" / "UniversalCouncil.CommandCenter" / "UniversalCouncil.CommandCenter.csproj"
MAIN_WINDOW = ROOT / "apps" / "UniversalCouncil.CommandCenter" / "MainWindow.xaml.cs"
SKIA_ANIMATOR = ROOT / "apps" / "UniversalCouncil.CommandCenter" / "SkiaMotionCueAnimator.cs"
SCREEN_TRANSITIONS = ROOT / "apps" / "UniversalCouncil.CommandCenter" / "ScreenTransitionMotion.cs"

for path in (STATE, SPEC, COMMAND_PROJECT, MAIN_WINDOW, SKIA_ANIMATOR, SCREEN_TRANSITIONS):
    if not path.exists():
        raise SystemExit(f"missing MP4 artifact: {path.relative_to(ROOT)}")

state = json.loads(STATE.read_text(encoding="utf-8"))
if state["candidate_id"] != "motionkit-mp4-command-center-reference-integration-20261023":
    raise SystemExit("MP4 identity drifted")
if state["parent_mp3_sha"] != "f7e2db143898e4f1d1a43e8d43dc875632c2ed0a":
    raise SystemExit("MP4 parent MP3 binding drifted")
if state["status"] != "REFERENCE_INTEGRATION_CANDIDATE_NOT_VISUALLY_ACCEPTED":
    raise SystemExit("MP4 may not self-promote to visual acceptance")
if state["strategy"] != "OPEN_SOURCE_FIRST_INTEGRATION_OVER_INVENTION":
    raise SystemExit("MP4 strategy drifted")
if state["shared_motionkit_changes"]:
    raise SystemExit("MP4 reference integration may not expand shared MotionKit layers")

renderer = state["renderer"]
if renderer != {
    "id": "SKIASHARP",
    "version": "4.153.1",
    "scope": "COMMAND_CENTER_ADAPTER_LOCAL",
    "package": "SkiaSharp",
    "blocked_package": "SkiaSharp.Views.WPF",
}:
    raise SystemExit("MP4 renderer binding drifted")

if {target["family"] for target in state["targets"]} != {
    "ROLE_ACTIVATION",
    "ARTIFACT_HANDOFF_RETURN",
}:
    raise SystemExit("MP4 first integration target set drifted")

for key, value in state["authority"].items():
    if value:
        raise SystemExit(f"MP4 authority unexpectedly enabled: {key}")

project = COMMAND_PROJECT.read_text(encoding="utf-8")
if '<PackageReference Include="SkiaSharp" Version="4.153.1" />' not in project:
    raise SystemExit("Command Center SkiaSharp pin missing")
if "SkiaSharp.Views.WPF" in project:
    raise SystemExit("blocked SkiaSharp.Views.WPF dependency entered Command Center")
for forbidden in ("Rive", "Lottie", "Microsoft.WindowsAppSDK"):
    if forbidden in project:
        raise SystemExit(f"MP4 first slice acquired an unapproved renderer dependency: {forbidden}")

animator = SKIA_ANIMATOR.read_text(encoding="utf-8")
for marker in (
    "SKPathBuilder",
    "SKPathEffect.CreateDash",
    "SKPathEffect.CreateTrim",
    "SKPathEffect.CreateCompose",
    "BitmapSource.Create",
    "CompositionTarget.Rendering",
    "AnimateRouteReveal",
    "AnimateArtifactHandoff",
):
    if marker not in animator:
        raise SystemExit(f"MP4 Skia adapter marker missing: {marker}")

for forbidden in ("SkiaSharp.Views.WPF", "Task.Delay", "DispatcherTimer"):
    if forbidden in animator:
        raise SystemExit(f"MP4 adapter acquired forbidden coupling: {forbidden}")

main_window = MAIN_WINDOW.read_text(encoding="utf-8")
if "SkiaMotionCueAnimator.AnimateRouteReveal" not in main_window:
    raise SystemExit("ROLE_ACTIVATION is not routed through Skia adapter")
if "SkiaMotionCueAnimator.AnimateArtifactHandoff" not in main_window:
    raise SystemExit("ARTIFACT_HANDOFF is not routed through Skia adapter")


def method_body(source: str, method_name: str) -> str:
    marker = f"    private void {method_name}"
    start = source.find(marker)
    if start < 0:
        raise SystemExit(f"MP4 target method missing: {method_name}")
    next_method = source.find("\n    private ", start + len(marker))
    return source[start:] if next_method < 0 else source[start:next_method]


role_body = method_body(main_window, "AnimateRoleRouteCue")
handoff_body = method_body(main_window, "AnimateHandoffCue")
for name, body in (("AnimateRoleRouteCue", role_body), ("AnimateHandoffCue", handoff_body)):
    for old_marker in ("new Line", "new DoubleAnimation", "BeginAnimation("):
        if old_marker in body:
            raise SystemExit(f"{name} still contains bespoke WPF route animation: {old_marker}")

if "Skia" in SCREEN_TRANSITIONS.read_text(encoding="utf-8"):
    raise SystemExit("MP4 Skia integration incorrectly expanded into screen transitions")

for shared_path in (
    ROOT / "apps" / "UniversalCouncil.MotionKit.Core",
    ROOT / "apps" / "UniversalCouncil.MotionKit.Runtime",
):
    for file in shared_path.glob("*.cs"):
        if "SkiaSharp" in file.read_text(encoding="utf-8"):
            raise SystemExit(f"Skia leaked into shared MotionKit layer: {file.relative_to(ROOT)}")
    for file in shared_path.glob("*.csproj"):
        if "SkiaSharp" in file.read_text(encoding="utf-8"):
            raise SystemExit(f"Skia package leaked into shared MotionKit layer: {file.relative_to(ROOT)}")

spec = SPEC.read_text(encoding="utf-8")
for marker in (
    "SkiaSharp inside Command Center only",
    "ROLE_ACTIVATION",
    "ARTIFACT_HANDOFF",
    "does NOT:",
    "actual owner-visible/reference-Windows evidence is still required",
):
    if marker not in spec:
        raise SystemExit(f"MP4 specification drifted: {marker}")

print("Motion Platform MP4 validation: PASS (Open-Source-First Command Center Skia route/handoff integration)")
