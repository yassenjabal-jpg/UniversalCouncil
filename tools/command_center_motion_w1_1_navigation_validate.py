from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "command-center"
PROJECT = STATE / "project-governance"
MAIN = ROOT / "apps" / "UniversalCouncil.CommandCenter" / "MainWindow.xaml.cs"
TRANSITION = ROOT / "apps" / "UniversalCouncil.CommandCenter" / "ScreenTransitionMotion.cs"
RECORDER = ROOT / "apps" / "UniversalCouncil.CommandCenter.UiSmoke" / "MotionEvidence.cs"
P1_VALIDATOR = ROOT / "tools" / "command_center_p1_exit_evidence_validate.py"
NAV_STATE = STATE / "motion-w1-1-navigation.json"
CHANGE = PROJECT / "changes" / "2026-10-21-motion-w1-1-navigation.json"
PRE = PROJECT / "approvals" / "2026-10-21-motion-w1-1-navigation-pre.json"
CAPSULE = PROJECT / "context-capsules" / "2026-10-21-motion-w1-1-navigation.json"
ROADMAP = STATE / "motion-remediation-master-roadmap.json"

NAV_STEPS = {
    "Navigate Home -> Project Workspace",
    "Navigate Project -> Software Autopilot",
    "Navigate Autopilot -> Studio Project",
    "Navigate Studio -> Decision Mode",
    "Navigate Decision -> Recovery/Fork",
    "Navigate Recovery -> Pulse Story",
    "Navigate Pulse -> Work Receipt",
    "Navigate Receipt -> Home",
}


def load(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing W1.1 navigation artifact: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


for required in (MAIN, TRANSITION, RECORDER, P1_VALIDATOR, NAV_STATE, CHANGE, PRE, CAPSULE, ROADMAP):
    if not required.exists():
        raise SystemExit(f"missing W1.1 navigation artifact: {required.relative_to(ROOT)}")

main = MAIN.read_text(encoding="utf-8")
transition = TRANSITION.read_text(encoding="utf-8")
recorder = RECORDER.read_text(encoding="utf-8")
p1_validator = P1_VALIDATOR.read_text(encoding="utf-8")
state = load(NAV_STATE)
change = load(CHANGE)
pre = load(PRE)
capsule = load(CAPSULE)
roadmap = load(ROADMAP)

for marker in (
    "private void NavigateTo(ScreenKind screen)",
    "private async Task RunNavigationTransitionQueueAsync()",
    "private void CommitScreen(ScreenKind screen)",
    "private static ScreenTransitionProfile GetNavigationMotionProfile(ScreenKind screen)",
    "_queuedNavigationTarget = screen",
    "ReferenceHost.IsHitTestVisible = false",
    "ScreenTransitionMotion.RunExitAsync(ReferenceHost, profile, MotionEnabled)",
    "ScreenTransitionMotion.RunEntryAsync(ReferenceHost, profile, MotionEnabled)",
):
    if marker not in main:
        raise SystemExit(f"W1.1 navigation orchestration missing: {marker}")

if "RunScreenEntranceMotion(screen, isHome);" in main:
    raise SystemExit("W1.1 still uses target-only legacy entrance motion")

if main.count("ScreenKind.") < 8:
    raise SystemExit("W1.1 lost canonical screen coverage")

for marker in (
    "internal sealed record ScreenTransitionProfile(",
    "internal static Task RunExitAsync(",
    "internal static async Task RunEntryAsync(",
    "if (!fullMotion)",
    "ReducedHandoffOpacity",
    "surface.RenderTransform = Transform.Identity;",
    "internal static void Settle(",
):
    if marker not in transition:
        raise SystemExit(f"W1.1 transition helper missing: {marker}")

for forbidden in (
    "RepeatBehavior.Forever",
    "AutoReverse = true",
    "DoubleAnimationUsingPath",
    "AppDbContext",
    "SaveChanges",
    "HttpClient",
):
    if forbidden in transition:
        raise SystemExit(f"W1.1 presentation helper crossed a forbidden boundary: {forbidden}")

for step in NAV_STEPS:
    if step not in recorder:
        raise SystemExit(f"W1.1 exact-head evidence does not visit all eight screens: {step}")
    if step not in p1_validator:
        raise SystemExit(f"W1.1 evidence gate does not require navigation step: {step}")

if state["phase"] != "W1.1" or state["status"] != "VERIFY":
    raise SystemExit("W1.1 state is not in VERIFY")
if state["canonical_screen_count"] != 8:
    raise SystemExit("W1.1 canonical screen count drifted")
if not state["same_screen_navigation_noop"]:
    raise SystemExit("W1.1 same-screen navigation no-op rule drifted")
if state["reentrant_policy"] != "QUEUE_LATEST_TARGET_NO_OVERLAP":
    raise SystemExit("W1.1 reentrant navigation policy drifted")
if state["reduced_motion_policy"] != "CROSSFADE_ONLY_NO_TRANSLATE_OR_SCALE":
    raise SystemExit("W1.1 Reduced Motion policy drifted")
if state["w1_2_started"]:
    raise SystemExit("W1.2 started before W1.1 verification")

if change["current_state"] != "VERIFY":
    raise SystemExit("W1.1 governance lifecycle is not at VERIFY")
for lifecycle_state in ("PROPOSED", "MURTAKAZ_PRE_REVIEW", "APPROVE_TO_IMPLEMENT", "CONTEXT_CAPSULE", "IMPLEMENT", "VERIFY"):
    if lifecycle_state not in change["lifecycle"]:
        raise SystemExit(f"W1.1 governance lifecycle missing: {lifecycle_state}")

if pre["decision"] != "APPROVE_TO_IMPLEMENT":
    raise SystemExit("W1.1 pre-implementation approval is missing")
if capsule["status"] != "ACTIVE_FOR_IMPLEMENTATION":
    raise SystemExit("W1.1 context capsule is not active")

position = roadmap["current_position"]
if position["wave"] != "W1" or position["phase"] != "W1.1":
    raise SystemExit("roadmap is not at W1.1")
if position["phase_status"] != "VERIFY":
    raise SystemExit("roadmap does not record W1.1 VERIFY")
if position["pr_merge_allowed"] or position["next_phase_started"]:
    raise SystemExit("W1.1 advanced or authorized merge before verification")

truth = state["protected_truth"]
if (
    truth["authoritative_stage"] != "STAGE_7"
    or truth["stage8_opened"]
    or truth["runtime_authority"]
    or truth["live_execution_authorized"]
    or not truth["visual_identity_locked"]
):
    raise SystemExit("W1.1 protected truth drifted")

print("Motion W1.1 navigation validation: PASS (8-screen source-exit/target-entry + Reduced Motion parity locked)")
