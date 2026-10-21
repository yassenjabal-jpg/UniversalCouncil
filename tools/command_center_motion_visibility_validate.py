from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "apps" / "UniversalCouncil.CommandCenter" / "MainWindow.xaml.cs"
RECORDER = ROOT / "apps" / "UniversalCouncil.CommandCenter.UiSmoke" / "MotionEvidence.cs"
WORKFLOW = ROOT / ".github" / "workflows" / "command-center-p1-exit-evidence.yml"
P1_VALIDATOR = ROOT / "tools" / "command_center_p1_exit_evidence_validate.py"

for required in (MAIN, RECORDER, WORKFLOW, P1_VALIDATOR):
    if not required.exists():
        raise SystemExit(f"missing owner-visible motion artifact: {required.relative_to(ROOT)}")

main = MAIN.read_text(encoding="utf-8")
recorder = RECORDER.read_text(encoding="utf-8")
workflow = WORKFLOW.read_text(encoding="utf-8")
p1_validator = P1_VALIDATOR.read_text(encoding="utf-8")

required_main_markers = (
    "RunScreenEntranceMotion(screen, isHome);",
    "private void RunScreenEntranceMotion(",
    "private void AnimateRoleRouteCue(",
    "private void AnimateDecisionIntentCue(",
    "private void AnimateRecoveryIntentCue(",
    "private void AnimateForkSplitCue(",
    "private void AnimateRewindCue(",
    "private void AnimatePulseInteractionCue(",
    "private void AnimateHandoffCue(",\n    "private void RunAfterSemanticMotion(",
    "ScreenKind.DecisionMode => (700d",
    "ScreenKind.RecoveryFork => (760d",
    "ScreenKind.WorkReceipt => (760d",
)
for marker in required_main_markers:
    if marker not in main:
        raise SystemExit(f"owner-visible semantic motion implementation missing: {marker}")

for forbidden in (
    "RepeatBehavior.Forever",
    "AutoReverse = true",
    "DoubleAnimationUsingPath",
):
    if forbidden in main:
        raise SystemExit(f"decorative/unbounded motion regression detected: {forbidden}")

if main.count("if (!MotionEnabled)") < 8:
    raise SystemExit("Reduced Motion guards do not cover the expanded semantic motion paths")

required_recorder_markers = (
    "private const int MotionFramesPerSecond = 20;",
    "MotionFrameEvidence",
    "ComputeFrameDelta(",
    "changed_frame_count = changedFrameCount",
    "longest_changed_run = longestChangedRun",
    "motion_run_count = motionRunCount",
)
for marker in required_recorder_markers:
    if marker not in recorder:
        raise SystemExit(f"20fps motion visibility evidence marker missing: {marker}")

if workflow.count("-framerate 20") < 2:
    raise SystemExit("WPF full/reduced motion videos are not both encoded at 20fps")

required_gate_markers = (
    'manifest["frame_rate"] < 20',
    "changed_frames < 60",
    "longest_run < 6",
    "motion_runs < 8",
    "reduced motion capture lost too much visible state-transition feedback",
)
for marker in required_gate_markers:
    if marker not in p1_validator:
        raise SystemExit(f"motion visibility acceptance gate missing: {marker}")

print(
    "Owner-visible semantic motion validation: PASS "
    "(screen travel + semantic cues + 20fps evidence + anti-slide metrics enforced)"
)
