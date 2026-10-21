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
    "ScreenKind.DecisionMode => new(210, 450, 0, 62, 0.968)",
    "ScreenKind.RecoveryFork => new(210, 450, -68, 0, 0.972)",
    "ScreenKind.WorkReceipt => new(210, 450, 0, 64, 0.968)",
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
    "var ease = new QuadraticEase { EasingMode = easingMode };",
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
    "referenceImage.Visibility = Visibility.Visible;",
    "Stopwatch.StartNew()",
    "Channel.CreateBounded<byte[]>(",
    "frameEncoder.Queue(capture.Pixels)",
    'clock = "STOPWATCH_REALTIME_WPF"',
    'pipeline = "RENDERTARGETBITMAP_BGRA_TO_BACKGROUND_FFMPEG_PNG"',
    'background_encoder = "FFMPEG_LOSSLESS_PNG"',
    "png_encoding_on_wpf_capture_thread = false",
    'capture_surface_cache = "REFERENCE_HOST_AND_CONTEXT_DRAWER_BITMAP_CACHE"',
    "synchronous_layout_per_frame = false",
    "png_compression_level = 1",
    "referenceHost.CacheMode = new BitmapCache(1.0)",
    "contextDrawer.CacheMode = new BitmapCache(1.0)",
)
for marker in required_recorder_markers:
    if marker not in recorder:
        raise SystemExit(f"30fps owner-review motion evidence marker missing: {marker}")

if "new PngBitmapEncoder" in recorder:
    raise SystemExit("WPF recorder reintroduced synchronous PNG encoding and time dilation")

if "wpf-{mode}-capture.bgra" in recorder or "ExtractRawFramesWithFfmpeg(" in recorder:
    raise SystemExit("WPF recorder reintroduced synchronous raw-disk frame persistence")

if recorder.count("root.UpdateLayout();") != 1:
    raise SystemExit("WPF recorder must perform layout only during initial evidence-window setup")

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
    'timing.get("clock") != "STOPWATCH_REALTIME_WPF"',
    'timing.get("pipeline") != "RENDERTARGETBITMAP_BGRA_TO_BACKGROUND_FFMPEG_PNG"',
    'timing.get("background_encoder") != "FFMPEG_LOSSLESS_PNG"',
    'timing.get("png_encoding_on_wpf_capture_thread") is not False',
    'timing.get("capture_surface_cache") != "REFERENCE_HOST_AND_CONTEXT_DRAWER_BITMAP_CACHE"',
    'timing.get("synchronous_layout_per_frame") is not False',
    'int(timing.get("png_compression_level", -1)) != 1',
    "abs(actual_capture - target_capture) > 1.25",
    'float(timing.get("max_capture_lateness_ms", 999999)) > 100',
)
for marker in required_gate_markers:
    if marker not in p1_validator:
        raise SystemExit(f"motion visibility acceptance gate missing: {marker}")

print(
    "Owner-visible semantic motion validation: PASS "
    "(screen travel + semantic cues + 30fps owner evidence + time-normalized anti-slide metrics enforced)"
)
