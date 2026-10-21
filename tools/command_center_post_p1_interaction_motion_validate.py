from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
XAML = ROOT / "apps" / "UniversalCouncil.CommandCenter" / "MainWindow.xaml"
CODE = ROOT / "apps" / "UniversalCouncil.CommandCenter" / "MainWindow.xaml.cs"
LAW = ROOT / "docs" / "operations" / "command-center" / "living-operations" / "23_POST_P1_INTERACTION_MOTION_LAW.md"

for required in (XAML, CODE, LAW):
    if not required.exists():
        raise SystemExit(f"missing interaction/motion law artifact: {required.relative_to(ROOT)}")

xaml = XAML.read_text(encoding="utf-8")
code = CODE.read_text(encoding="utf-8")
law = LAW.read_text(encoding="utf-8")

# Every explicit WPF Button surface must have a semantic action binding.
buttons = re.findall(r"<Button\b(?:(?!>).)*>", xaml, flags=re.DOTALL)
if len(buttons) < 60:
    raise SystemExit("unexpected drop in governed WPF button coverage")
missing = [button for button in buttons if 'Click="' not in button and 'Command="' not in button]
if missing:
    raise SystemExit(f"clickable-looking WPF buttons without action binding: {len(missing)}")

# All eight governed screens must remain explicit.
for screen in (
    "Home",
    "ProjectWorkspace",
    "SoftwareAutopilot",
    "StudioProject",
    "DecisionMode",
    "RecoveryFork",
    "PulseStory",
    "WorkReceipt",
):
    if screen not in code:
        raise SystemExit(f"missing governed screen interaction surface: {screen}")

# Dynamic hotspots are centrally mapped to inspect/navigation/state/intent functions.
for required in (
    "case HotspotKind.Navigate:",
    "case HotspotKind.Role:",
    "case HotspotKind.Reasoning:",
    "case HotspotKind.Filmstrip:",
    "case HotspotKind.Tool:",
    "case HotspotKind.DecisionAction:",
    "case HotspotKind.RecoveryAction:",
    "case HotspotKind.Artifact:",
    "case HotspotKind.Stage:",
    "case HotspotKind.Pulse:",
):
    if required not in code:
        raise SystemExit(f"dynamic hotspot routing drifted: {required}")

# Owner-facing primary actions may not terminate in feedback-only behavior.
required_functional_routes = (
    "OpenExecutionReadiness();",
    "OpenAttachmentReadiness();",
    "OpenOwnerIntentPreview(action, label);",
    "OpenRecoveryIntentPreview(action, message);",
    'OpenGenericRegion(\n            "Ask This"',
    'OpenGenericRegion(\n            "Contribution History"',
)
for route in required_functional_routes:
    if route not in code:
        raise SystemExit(f"functional interaction route missing: {route}")

if 'ShowNotice("التنفيذ الحي غير مفعل' in code:
    raise SystemExit("Start action regressed to feedback-only behavior")
if 'ShowNotice($"{label}: تم اختبار تفاعل القرار فقط' in code:
    raise SystemExit("Decision action regressed to feedback-only behavior")
if "ShowNotice(message);" in code:
    raise SystemExit("Recovery action regressed to feedback-only behavior")

# Truthful visible affordances while Stage 8 is closed.
for visible_label in (
    "فحص الجاهزية",
    "حالة الإرفاق",
    "جاهزية الويب",
    "حالة النموذج",
    "حالة التفكير",
):
    if visible_label not in xaml:
        raise SystemExit(f"truthful unavailable/readiness affordance missing: {visible_label}")

# Motion must remain bounded, purpose-specific and reduced-motion aware.
motion_markers = (
    "private void NavigateTo(ScreenKind screen)",
    "private void OpenDrawer(",
    "private void CloseDrawer()",
    "private static void AnimateNativeRoleButton(Button button)",
    "private void ShowRoleActivation(Button button)",
    "private void ShowSecondaryActivation(FrameworkElement target)",
    "private async void ShowNotice(string message)",
)
for marker in motion_markers:
    if marker not in code:
        raise SystemExit(f"approved motion implementation missing: {marker}")

if code.count("if (!MotionEnabled)") < 5:
    raise SystemExit("Reduced Motion guards are no longer covering primary motion paths")

for forbidden in ("RepeatBehavior.Forever", "AutoReverse = true", "DoubleAnimationUsingPath"):
    if forbidden in code:
        raise SystemExit(f"decorative/unbounded motion pattern detected: {forbidden}")

for statement in (
    "A visual affordance is a promise.",
    "Decorative-only motion is rejected.",
    "A primary action MUST NOT exist only to play an animation",
    "Reduced Motion preserves all meaning.",
):
    if statement not in law:
        raise SystemExit(f"governing interaction/motion law drifted: {statement}")

print(
    f"Post-P1 interaction/motion law validation: PASS "
    f"({len(buttons)} bound WPF buttons; purposeful motion + Reduced Motion enforced)"
)
