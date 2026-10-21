from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "apps" / "UniversalCouncil.CommandCenter" / "MainWindow.xaml.cs"
RECORDER = ROOT / "apps" / "UniversalCouncil.CommandCenter.UiSmoke" / "MotionEvidence.cs"
WORKFLOW = ROOT / ".github" / "workflows" / "command-center-p1-exit-evidence.yml"
P1_VALIDATOR = ROOT / "tools" / "command_center_p1_exit_evidence_validate.py"
SCREEN_TRANSITION = ROOT / "apps" / "UniversalCouncil.CommandCenter" / "ScreenTransitionMotion.cs"

for required in (MAIN, RECORDER, WORKFLOW, P1_VALIDATOR, SCREEN_TRANSITION):
    if not required.exists():
        raise SystemExit(f"missing owner-visible motion artifact: {required.relative_to(ROOT)}")

main = MAIN.read_text(encoding="utf-8")
recorder = RECORDER.read_text(encoding="utf-8")
workflow = WORKFLOW.read_text(encoding="utf-8")
p1_validator = P1_VALIDATOR.read_text(encoding="utf-8")
screen_transition = SCREEN_TRANSITION.read_text(encoding="utf-8")

required_main_markers = (
    "private void NavigateTo(ScreenKind screen)",
    "private async Task RunNavigationTransitionQueueAsync()",
    "private void CommitScreen(ScreenKind screen)",
    "private static ScreenTransitionProfile GetNavigationMotionProfile(ScreenKind screen)",
    "ScreenTransitionMotion.RunExitAsync(ReferenceHost, profile, MotionEnabled)",
    "ScreenTransitionMotion.RunEntryAsync(ReferenceHost, profile, MotionEnabled)",
    "ReferenceHost.IsHitTestVisible = false",
    "_queuedNavigationTarget = screen",
    "if (!_navigationTransitionActive && screen == _currentScreen)",

    "private void AnimateRoleRouteCue(",
    "private void AnimateDecisionIntentCue(",
    "private void AnimateRecoveryIntentCue(",
    "private void AnimateForkSplitCue(",
    "private void AnimateRewindCue(",
    "private void AnimatePulseInteractionCue(",
    "private void AnimateHandoffCue(",
    "private void RunAfterSemanticMotion(",
    "ScreenKind.DecisionMode => new(175, 380, 0, 30, 0.982)",
    "ScreenKind.RecoveryFork => new(175, 390, -34, 0, 0.986)",
    "ScreenKind.WorkReceipt => new(175, 390, 0, 32, 0.982)",
)
for marker in required_main_markers:
    if marker not in main:
        raise SystemExit(f"owner-visible semantic motion implementation missing: {marker}")

for forbidden in (
    "RepeatBehavior.Forever",
    "AutoReverse = true",
    "DoubleAnimationUsingPath",
):
    if forbidden in main or forbidden in screen_transition:
        raise SystemExit(f"decorative/unbounded motion regression detected: {forbidden}")

required_transition_markers = (
    "internal static Task RunExitAsync(",
    "internal static async Task RunEntryAsync(",
    "if (!fullMotion)",
    "surface.RenderTransform = Transform.Identity;",
    "ReducedHandoffOpacity",
    "internal static void Settle(",
)
for marker in required_transition_markers:
    if marker not in screen_transition:
        raise SystemExit(f"screen transition motion contract missing: {marker}")

if "RunScreenEntranceMotion(screen, isHome);" in main:
    raise SystemExit("legacy target-only entrance motion is still active after W1.1 navigation choreography")

if main.count("if (!MotionEnabled)") < 8:
    raise SystemExit("Reduced Motion guards do not cover the expanded semantic motion paths")

required_recorder_markers = (
    "private const int MotionFramesPerSecond = 30;",
    "MotionFrameEvidence",
    "ComputeFrameDelta(",
    "changed_frame_count = changedFrameCount",
    "longest_changed_run = longestChangedRun",
    "motion_run_count = motionRunCount",
    "candidate_sha = candidateSha",
    'source_surface = "ACTUAL_WPF"',
    "raw_frames_included = true",
    "semantic_event_timestamps = true",
)
for marker in required_recorder_markers:
    if marker not in recorder:
        raise SystemExit(f"30fps owner-review motion evidence marker missing: {marker}")

if workflow.count("-framerate 30") < 2:
    raise SystemExit("WPF full/reduced owner-review motion videos are not both encoded at 30fps")
if "Verify exact candidate head" not in workflow:
    raise SystemExit("WPF evidence workflow does not verify the exact candidate head")

required_gate_markers = (
    "if frame_rate < 20:",
    "math.ceil(60 * fps_scale)",
    "math.ceil(6 * fps_scale)",
    "motion_runs < 8",
    "reduced motion capture lost required discrete state-transition feedback",
    "math.ceil(3 * fps_scale)",
)
for marker in required_gate_markers:
    if marker not in p1_validator:
        raise SystemExit(f"motion visibility acceptance gate missing: {marker}")

print(
    "Owner-visible semantic motion validation: PASS "
    "(screen travel + semantic cues + 30fps owner evidence + time-normalized anti-slide metrics enforced)"
)
