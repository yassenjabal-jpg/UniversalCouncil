from __future__ import annotations

import hashlib
import json
from pathlib import Path

def evidence_sha256(path: Path) -> str:
    if path.suffix.lower() in {".json", ".md", ".txt"}:
        text = path.read_text(encoding="utf-8-sig")
        canonical = text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()
    return hashlib.sha256(path.read_bytes()).hexdigest()


ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "motion-platform" / "mp4-reference-integration.json"
SPEC = ROOT / "docs" / "operations" / "motion-platform" / "09_MP4_REFERENCE_INTEGRATION.md"
COMMAND_PROJECT = ROOT / "apps" / "UniversalCouncil.CommandCenter" / "UniversalCouncil.CommandCenter.csproj"
MAIN_WINDOW = ROOT / "apps" / "UniversalCouncil.CommandCenter" / "MainWindow.xaml.cs"
SKIA_ANIMATOR = ROOT / "apps" / "UniversalCouncil.CommandCenter" / "SkiaMotionCueAnimator.cs"
SCREEN_TRANSITIONS = ROOT / "apps" / "UniversalCouncil.CommandCenter" / "ScreenTransitionMotion.cs"
UI_SMOKE_PROGRAM = ROOT / "apps" / "UniversalCouncil.CommandCenter.UiSmoke" / "Program.cs"
UI_SMOKE_MOTION = ROOT / "apps" / "UniversalCouncil.CommandCenter.UiSmoke" / "MotionEvidence.cs"
UI_SMOKE_WGC = ROOT / "apps" / "UniversalCouncil.CommandCenter.UiSmoke" / "WgcMotionEvidence.cs"
EVIDENCE_ROOT = ROOT / "lab" / "motion-platform" / "evidence" / "yassin-20261023-mp4"
EVIDENCE_SUMMARY = EVIDENCE_ROOT / "mp4-reference-evidence-summary.json"

for path in (
    STATE,
    SPEC,
    COMMAND_PROJECT,
    MAIN_WINDOW,
    SKIA_ANIMATOR,
    SCREEN_TRANSITIONS,
    UI_SMOKE_PROGRAM,
    UI_SMOKE_MOTION,
    UI_SMOKE_WGC,
):
    if not path.exists():
        raise SystemExit(f"missing MP4 artifact: {path.relative_to(ROOT)}")

state = json.loads(STATE.read_text(encoding="utf-8"))
if state["candidate_id"] != "motionkit-mp4-command-center-reference-integration-20261023":
    raise SystemExit("MP4 identity drifted")
if state["parent_mp3_sha"] != "602639dbc10a25824aa0b1f131fd6fc184771ac0":
    raise SystemExit("MP4 parent MP3 binding drifted")
if state.get("parent_mp3_gate") != "RENDERER_ROLE_MATRIX_ACCEPTED" or not state.get("parent_mp3_gate_passed"):
    raise SystemExit("MP4 is not bound to an accepted MP3 renderer role matrix")
if state.get("restacked_from_head_sha") != "0813a617f3ad1db0c67387c196fc965d44f8ce41":
    raise SystemExit("MP4 restack provenance drifted")
if state["status"] != "REFERENCE_RUNTIME_EVIDENCE_COMPLETE_OWNER_VISUAL_REVIEW_PENDING":
    raise SystemExit("MP4 runtime-evidence status drifted or self-promoted beyond owner review")

runtime_evidence = state.get("reference_runtime_evidence") or {}
if runtime_evidence.get("candidate_sha") != "c13fa2ad069075e21f35b3970b388b5922826ee8":
    raise SystemExit("MP4 reference runtime evidence candidate binding drifted")
if runtime_evidence.get("evidence_directory") != "lab/motion-platform/evidence/yassin-20261023-mp4":
    raise SystemExit("MP4 reference runtime evidence directory drifted")
if runtime_evidence.get("source_surface") != "ACTUAL_WPF_RENDER_TARGET_BITMAP":
    raise SystemExit("MP4 reference evidence source surface drifted")
if runtime_evidence.get("owner_visual_acceptance"):
    raise SystemExit("MP4 may not self-promote owner visual acceptance")
if not runtime_evidence.get("same_semantic_steps"):
    raise SystemExit("MP4 Full/Reduced evidence lost semantic-step parity")

full_evidence = runtime_evidence.get("full") or {}
reduced_evidence = runtime_evidence.get("reduced") or {}
for label, evidence in (("full", full_evidence), ("reduced", reduced_evidence)):
    if evidence.get("frame_count") != 360 or evidence.get("duration_seconds") != 12:
        raise SystemExit(f"MP4 {label} focused evidence protocol drifted")
if int(full_evidence.get("changed_frame_count", 0)) <= int(reduced_evidence.get("changed_frame_count", 0)):
    raise SystemExit("MP4 Full evidence no longer shows more motion than Reduced")
if int(full_evidence.get("longest_changed_run", 0)) <= int(reduced_evidence.get("longest_changed_run", 0)):
    raise SystemExit("MP4 Full evidence no longer shows longer travel than Reduced")

wgc_diagnostic = runtime_evidence.get("wgc_diagnostic") or {}
if wgc_diagnostic.get("status") != "REJECTED_STALE_SOURCE":
    raise SystemExit("MP4 stale WGC diagnostic was not preserved as rejected evidence")
if wgc_diagnostic.get("source_frames_arrived") != 1 or wgc_diagnostic.get("changed_frame_count") != 0:
    raise SystemExit("MP4 stale WGC diagnostic facts drifted")
if not wgc_diagnostic.get("fail_closed_guard_added"):
    raise SystemExit("MP4 WGC fail-closed guard is not recorded")

if not EVIDENCE_SUMMARY.exists():
    raise SystemExit("MP4 owner-review evidence summary is missing")
summary = json.loads(EVIDENCE_SUMMARY.read_text(encoding="utf-8-sig"))
if summary.get("hash_mode") != "CANONICAL_LF_TEXT_OR_RAW_BINARY":
    raise SystemExit("MP4 evidence summary hash mode drifted")
if summary.get("candidate_sha") != runtime_evidence.get("candidate_sha"):
    raise SystemExit("MP4 evidence summary candidate SHA drifted")
if not summary.get("same_semantic_steps"):
    raise SystemExit("MP4 evidence summary lost Full/Reduced semantic parity")
if summary.get("owner_visual_acceptance") or summary.get("production_adoption") or summary.get("stage8_opened"):
    raise SystemExit("MP4 evidence summary self-promoted authority")

required_evidence_files = {
    "full-motion-evidence-manifest.json",
    "reduced-motion-evidence-manifest.json",
    "full-role-activation-mid.png",
    "full-handoff-mid.png",
    "reduced-role-state-change.png",
    "reduced-role-settled.png",
    "reduced-handoff-state-change.png",
    "reduced-handoff-settled.png",
    "mp4-owner-review-contact-sheet.png",
    "mp4-reference-full-motion.mp4",
    "mp4-reference-reduced-motion.mp4",
}
listed_files = {entry["name"]: entry for entry in summary.get("files", [])}
if not required_evidence_files.issubset(listed_files):
    raise SystemExit("MP4 owner-review evidence package is incomplete")
for name, entry in listed_files.items():
    path = EVIDENCE_ROOT / name
    if not path.exists():
        raise SystemExit(f"MP4 evidence file missing: {name}")
    actual = evidence_sha256(path)
    if actual != entry.get("sha256"):
        raise SystemExit(f"MP4 evidence hash mismatch: {name}")

full_manifest = json.loads((EVIDENCE_ROOT / "full-motion-evidence-manifest.json").read_text(encoding="utf-8"))
reduced_manifest = json.loads((EVIDENCE_ROOT / "reduced-motion-evidence-manifest.json").read_text(encoding="utf-8"))
for label, manifest in (("full", full_manifest), ("reduced", reduced_manifest)):
    if manifest.get("evidence_type") != "MOTION_PLATFORM_MP4_REFERENCE":
        raise SystemExit(f"MP4 {label} manifest evidence type drifted")
    if manifest.get("candidate_sha") != runtime_evidence.get("candidate_sha"):
        raise SystemExit(f"MP4 {label} manifest candidate SHA drifted")
full_steps = [(item["frame"], item["Name"]) for item in full_manifest.get("steps", [])]
reduced_steps = [(item["frame"], item["Name"]) for item in reduced_manifest.get("steps", [])]
if full_steps != reduced_steps:
    raise SystemExit("MP4 Full/Reduced manifests do not execute identical semantic steps")

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

ui_smoke_program = UI_SMOKE_PROGRAM.read_text(encoding="utf-8")
ui_smoke_motion = UI_SMOKE_MOTION.read_text(encoding="utf-8")
ui_smoke_wgc = UI_SMOKE_WGC.read_text(encoding="utf-8")

for marker in (
    "--mp4-motion-evidence",
    "RenderMotionEvidence(output, reducedMotion, mp4Reference: true)",
):
    if marker not in ui_smoke_program:
        raise SystemExit(f"MP4 focused evidence entry point missing: {marker}")

for marker in (
    "BuildMp4MotionSteps",
    "MOTION_PLATFORM_MP4_REFERENCE",
    "MP4_REFERENCE_INTEGRATION",
    "Activate Evidence role and open context",
    "Open Handoff Pulse context",
):
    if marker not in ui_smoke_motion:
        raise SystemExit(f"MP4 focused evidence marker missing: {marker}")

for marker in (
    "Persistent WGC evidence is stale",
    "Persistent WGC evidence observed no visible frame changes; refusing a false PASS.",
):
    if marker not in ui_smoke_wgc:
        raise SystemExit(f"MP4 evidence fail-closed guard missing: {marker}")

spec = SPEC.read_text(encoding="utf-8")
for marker in (
    "SkiaSharp inside Command Center only",
    "ROLE_ACTIVATION",
    "ARTIFACT_HANDOFF",
    "does NOT:",
    "Focused MP4 evidence was captured on YASSIN",
    "Owner visual acceptance remains pending.",
):
    if marker not in spec:
        raise SystemExit(f"MP4 specification drifted: {marker}")

print("Motion Platform MP4 validation: PASS (Open-Source-First Command Center Skia route/handoff integration)")
