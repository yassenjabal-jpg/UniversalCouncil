from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "command-center"
PROJECT = STATE / "project-governance"

CHANGE = PROJECT / "changes" / "2026-10-21-repair-b2-cross-screen-consistency.json"
PRE = PROJECT / "approvals" / "2026-10-21-repair-b2-cross-screen-consistency-pre.json"
B2_1_CHECK = PROJECT / "approvals" / "2026-10-21-repair-b2-1-shared-visual-check.json"
POST = PROJECT / "approvals" / "2026-10-21-repair-b2-cross-screen-consistency-post.json"
CAPSULE = PROJECT / "context-capsules" / "2026-10-21-repair-b2-cross-screen-consistency.json"
B1_POST = PROJECT / "approvals" / "2026-10-21-repair-b1-native-completion-post.json"
FINAL_P1_POST = PROJECT / "approvals" / "2026-10-21-repair-b3-final-p1-acceptance-post.json"
PLAN = STATE / "living-operations-p1-b2-cross-screen-consistency.json"
P1 = STATE / "living-operations-p1-visual-phase.json"
SCREEN_REVIEW = STATE / "living-operations-p1-screen-review.json"
REMAINDER = STATE / "living-operations-p1-remainder-phases.json"
MAIN_WINDOW = ROOT / "apps" / "UniversalCouncil.CommandCenter" / "MainWindow.xaml.cs"
MAIN_XAML = ROOT / "apps" / "UniversalCouncil.CommandCenter" / "MainWindow.xaml"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


for required in (
    CHANGE,
    PRE,
    B2_1_CHECK,
    CAPSULE,
    B1_POST,
    PLAN,
    P1,
    SCREEN_REVIEW,
    REMAINDER,
    MAIN_WINDOW,
    MAIN_XAML,
):
    if not required.exists():
        raise SystemExit(f"missing B2 artifact: {required.relative_to(ROOT)}")

change = load(CHANGE)
pre = load(PRE)
b2_1_check = load(B2_1_CHECK)
capsule = load(CAPSULE)
b1_post = load(B1_POST)
plan = load(PLAN)
p1 = load(P1)
screen_review = load(SCREEN_REVIEW)
remainder = load(REMAINDER)
post = load(POST) if POST.exists() else None
final_p1_post = load(FINAL_P1_POST) if FINAL_P1_POST.exists() else None
final_p1_approved = final_p1_post is not None and final_p1_post.get("decision") == "APPROVED_BY_AL_MURTAKAZ" and final_p1_post.get("p1_complete") is True

if change["change_id"] != "CC-REPAIR-B2-CROSS-SCREEN-CONSISTENCY-2026-10-21":
    raise SystemExit("B2 change id drifted")
if change["base_revision"]["sha"] != "9352eada66776f1a87e7a10e599b7003c833b49d":
    raise SystemExit("B2 canonical base drifted")
if change["unplanned_scope_policy"] != "RETURN_TICKET_OR_NEW_CHANGE_ENVELOPE":
    raise SystemExit("B2 scope-growth policy drifted")
if change["pre_approval_receipt"] != (
    "state/command-center/project-governance/approvals/2026-10-21-repair-b2-cross-screen-consistency-pre.json"
):
    raise SystemExit("B2 change envelope lost its pre-approval binding")

if pre["decision"] != "APPROVE_TO_IMPLEMENT" or not pre["implementation_authorized"]:
    raise SystemExit("B2 implementation is not pre-approved")
if pre["canonical_base"]["sha"] != change["base_revision"]["sha"]:
    raise SystemExit("B2 pre-review base does not match the change envelope")
if pre["merge_authorized"] or pre["final_p1_approval_granted"]:
    raise SystemExit("B2 pre-review may not pre-authorize merge or final P1 approval")
if pre["b3_r10_opened"] or pre["live_execution_authorized"] or pre["stage8_opened"]:
    raise SystemExit("B2 pre-review inflated authority")

if capsule["job_or_change_id"] != change["change_id"] or not capsule["immutable"]:
    raise SystemExit("B2 Context Capsule binding drifted")
if b1_post["decision"] != "APPROVED_BY_AL_MURTAKAZ" or not b1_post["b2_r9_authorized"]:
    raise SystemExit("B2 started without approved B1 predecessor")

protected = plan["protected_truth"]
if protected != {
    "p1_status": "IN_PROGRESS",
    "authoritative_stage": "STAGE_7",
    "stage8_opened": False,
    "runtime_authority": False,
    "final_p1_approval": False,
    "b3_opened": False,
}:
    raise SystemExit("B2 protected truth drifted")

if b2_1_check["decision"] != "APPROVE_B2_1_CONTINUE":
    raise SystemExit("B2.1 did not pass its Murtakaz slice check")
if plan["slices"]["B2.1_SHARED_VISUAL_TOKENS_AND_CHROME"]["state"] != "APPROVED_TO_CONTINUE":
    raise SystemExit("B2.1 is not closed before later B2 slices")

if p1["status"] not in {"IN_PROGRESS", "APPROVED_BY_AL_MURTAKAZ"}:
    raise SystemExit("B2 historical validation observed an unsupported P1 lifecycle state")
if p1["status"] == "APPROVED_BY_AL_MURTAKAZ" and not final_p1_approved:
    raise SystemExit("P1 claims final approval without the later governed R10 receipt")
if p1["stage8_opened"] or p1["runtime_authority"]:
    raise SystemExit("B2/later P1 lifecycle inflated runtime authority")
if screen_review["phase_complete"] and not final_p1_approved:
    raise SystemExit("P1 completed without the later governed R10 receipt")
r10_state = remainder["phases"]["R10_FINAL_MURTAKAZ_STUDIO_REVIEW"]["state"]
if r10_state not in {"NOT_OPENED", "MURTAKAZ_STUDIO_REVIEW", "RETURNED_FOR_CHANGES", "CLOSED"}:
    raise SystemExit("B2 historical validation observed an unsupported later R10 state")

main_source = MAIN_WINDOW.read_text(encoding="utf-8")
xaml_source = MAIN_XAML.read_text(encoding="utf-8")

for marker in (
    "private static class CrossScreenVisualTokens",
    "CrossScreenVisualTokens.NavGlyphSize",
    "CrossScreenVisualTokens.DockLabelSize",
    "_viewModel.ExecutionFabric.LiveDispatchEnabled",
    'ChromeText("UNKNOWN", 9, "#6B7280"',
    '"Autopilot — حالة التنفيذ"',
    "AutomationProperties.SetHelpText",
    "UNKNOWN / SEARCH PROVIDER NOT CONNECTED",
    "SecondaryNativeLayer.Opacity = _nativeReferenceBlendEnabled && !isHome ? 0.46 : 1;",
    "AddFixtureTruthBadge",
    "REFERENCE FIXTURE · NOT LIVE",
):
    if marker not in main_source:
        raise SystemExit(f"B2 implementation marker missing: {marker}")

if '"Autopilot — يعمل الآن"' in main_source:
    raise SystemExit("Shared Autopilot hotspot still claims unverified live activity")
if 'ChromeText("يعمل الآن"' in main_source:
    raise SystemExit("Native fixture still contains a hard-coded live-now claim")
if main_source.count("AddFixtureTruthBadge(") < 3:
    raise SystemExit("Reference-fixture truth badge is not applied to Home and secondary chrome")
if 'KeyboardNavigation.TabNavigation="Cycle"' not in xaml_source:
    raise SystemExit("B2 keyboard traversal is not explicitly cyclic")
if 'KeyboardNavigation.ControlTabNavigation="Cycle"' not in xaml_source:
    raise SystemExit("B2 Ctrl+Tab traversal is not explicitly cyclic")
if 'AutomationProperties.Name="UniversalCouncil Command Center"' not in xaml_source:
    raise SystemExit("B2 root accessibility name missing")

key_block = main_source.split("private void Window_PreviewKeyDown", 1)[1]
if "e.Key == Key.K" not in key_block:
    raise SystemExit("Advertised Ctrl+K shortcut is still dead")
home_only_overlay_gate = "e.Key == Key.O &&\n            _currentScreen == ScreenKind.Home"
if "e.Key == Key.O" not in key_block or home_only_overlay_gate in key_block:
    raise SystemExit("Reference/native overlay shortcut is still Home-only")

if post is not None:
    if post["decision"] != "APPROVED_BY_AL_MURTAKAZ":
        raise SystemExit("B2 post-review exists without Al-Murtakaz approval")
    if not post["merge_authorized"] or not post["adoption_authorized"]:
        raise SystemExit("B2 post-review did not authorize adoption/merge")
    if post["final_p1_approval_granted"] or post["r10_opened"]:
        raise SystemExit("B2 post-review improperly granted final P1 approval or opened R10")
    if post["live_execution_authorized"] or post["stage8_opened"]:
        raise SystemExit("B2 post-review inflated runtime authority")

print("Al-Murtakaz Visual B2 cross-screen consistency validation: PASS")
