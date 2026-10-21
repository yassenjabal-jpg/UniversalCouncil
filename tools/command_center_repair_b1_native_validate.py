from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "command-center"
PROJECT = STATE / "project-governance"

MANIFEST = STATE / "living-operations-reference-manifest.json"
P1 = STATE / "living-operations-p1-visual-phase.json"
LEDGER = STATE / "living-operations-p1-b1-native-completion.json"
B1_REVIEW = STATE / "living-operations-p1-b1-visual-review.json"
SCREEN_REVIEW = STATE / "living-operations-p1-screen-review.json"
REFERENCE_SHELL = STATE / "living-operations-p1-reference-shell-implementation.json"
REMAINDER = STATE / "living-operations-p1-remainder-phases.json"
HOME_SHELL = STATE / "living-operations-p1-home-native-shell.json"
HOME_FIDELITY = STATE / "living-operations-p1-home-fidelity.json"
PROJECT_CONTEXT = STATE / "project-context-map.json"

B1_PRE = PROJECT / "approvals" / "2026-10-21-repair-b1-native-completion-pre.json"
B1_POST = PROJECT / "approvals" / "2026-10-21-repair-b1-native-completion-post.json"
B1_CHANGE = PROJECT / "changes" / "2026-10-21-repair-b1-native-completion.json"
B1_CAPSULE = PROJECT / "context-capsules" / "2026-10-21-repair-b1-native-completion.json"
FINAL_P1_POST = PROJECT / "approvals" / "2026-10-21-repair-b3-final-p1-acceptance-post.json"
STAGE7_READINESS_POST = PROJECT / "approvals" / "2026-10-21-stage7-real-host-evidence-readiness-post.json"

MAIN_WINDOW = ROOT / "apps" / "UniversalCouncil.CommandCenter" / "MainWindow.xaml.cs"
UI_SMOKE = ROOT / "apps" / "UniversalCouncil.CommandCenter.UiSmoke" / "Program.cs"

CANONICAL_ROLES = [
    "home_owner_workspace",
    "living_project_workspace",
    "software_autopilot_project",
    "studio_project",
    "owner_decision_mode",
    "checkpoint_recovery_fork",
    "pulse_visual_project_story",
    "project_complete_work_receipt",
]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


for required in (
    MANIFEST,
    P1,
    LEDGER,
    B1_REVIEW,
    SCREEN_REVIEW,
    REFERENCE_SHELL,
    REMAINDER,
    HOME_SHELL,
    HOME_FIDELITY,
    PROJECT_CONTEXT,
    B1_PRE,
    B1_CHANGE,
    B1_CAPSULE,
    MAIN_WINDOW,
    UI_SMOKE,
):
    if not required.exists():
        raise SystemExit(f"missing B1 artifact: {required.relative_to(ROOT)}")

manifest = load(MANIFEST)
p1 = load(P1)
ledger = load(LEDGER)
b1_review = load(B1_REVIEW)
screen_review = load(SCREEN_REVIEW)
reference_shell = load(REFERENCE_SHELL)
remainder = load(REMAINDER)
home_shell = load(HOME_SHELL)
home_fidelity = load(HOME_FIDELITY)
project_context = load(PROJECT_CONTEXT)
pre = load(B1_PRE)
post = load(B1_POST) if B1_POST.exists() else None
change = load(B1_CHANGE)
capsule = load(B1_CAPSULE)
final_p1_post = load(FINAL_P1_POST) if FINAL_P1_POST.exists() else None
stage7_readiness_post = load(STAGE7_READINESS_POST) if STAGE7_READINESS_POST.exists() else None
final_p1_approved = (
    final_p1_post is not None
    and final_p1_post.get("decision") == "APPROVED_BY_AL_MURTAKAZ"
    and final_p1_post.get("p1_complete") is True
)

manifest_roles = [item["role"] for item in manifest["references"]]
if manifest_roles != CANONICAL_ROLES:
    raise SystemExit("Canonical visual reference roles/order drifted")
if [item["order"] for item in manifest["references"]] != list(range(1, 9)):
    raise SystemExit("Canonical visual reference order drifted")

if pre["decision"] != "APPROVE_TO_IMPLEMENT":
    raise SystemExit("B1 lacks Murtakaz pre-approval")
if pre["canonical_base"]["sha"] != "49a013f5fe653c40b43e7a0ca4dd68fc98845fc7":
    raise SystemExit("B1 pre-approval baseline drifted")
if pre["final_p1_approval_granted"] or pre["merge_authorized"]:
    raise SystemExit("B1 pre-approval may not pre-authorize final P1 approval or merge")
if pre["live_execution_authorized"] or pre["stage8_opened"]:
    raise SystemExit("B1 pre-approval inflated runtime authority")

if change["pre_approval_receipt"] != (
    "state/command-center/project-governance/approvals/2026-10-21-repair-b1-native-completion-pre.json"
):
    raise SystemExit("B1 Change Envelope is not bound to its pre-approval")
if change["unplanned_scope_policy"] != "RETURN_TICKET_OR_NEW_CHANGE_ENVELOPE":
    raise SystemExit("B1 scope-growth policy drifted")
if capsule["job_or_change_id"] != change["change_id"] or not capsule["immutable"]:
    raise SystemExit("B1 Context Capsule binding drifted")

if p1["status"] not in {"IN_PROGRESS", "APPROVED_BY_AL_MURTAKAZ"}:
    raise SystemExit("B1 historical validation observed an unsupported P1 lifecycle state")
if p1["status"] == "APPROVED_BY_AL_MURTAKAZ" and not final_p1_approved:
    raise SystemExit("P1 claims final approval without the later governed R10 receipt")
if not p1["governance"]["final_approval_required"]:
    raise SystemExit("B1 weakened final P1 approval requirement")
if p1["stage8_opened"] or p1["runtime_authority"]:
    raise SystemExit("B1 inflated Stage8/runtime authority")

if ledger["change_id"] != change["change_id"]:
    raise SystemExit("B1 ledger change id drifted")
if ledger["final_p1_approval_allowed"]:
    raise SystemExit("B1 ledger may not grant final P1 approval")
if ledger["truth"] != {
    "p1_status": "IN_PROGRESS",
    "stage8_opened": False,
    "runtime_authority": False,
    "final_visual_approval": False,
}:
    raise SystemExit("B1 ledger protected truth drifted")

ledger_roles = [item["role"] for item in ledger["screens"]]
if ledger_roles != CANONICAL_ROLES:
    raise SystemExit("B1 ledger does not cover exactly the eight canonical roles")
if [item["order"] for item in ledger["screens"]] != list(range(1, 9)):
    raise SystemExit("B1 ledger screen order drifted")
for screen in ledger["screens"]:
    if len(screen["evidence"]["reference_sha256"]) != 64:
        raise SystemExit(f"B1 reference evidence hash invalid: {screen['role']}")
    if len(screen["evidence"]["native_sha256"]) != 64:
        raise SystemExit(f"B1 native evidence hash invalid: {screen['role']}")
    if len(screen["evidence"]["blend_sha256"]) != 64:
        raise SystemExit(f"B1 blend evidence hash invalid: {screen['role']}")
    if screen["review"] != "NO_B1_STRUCTURAL_BLOCKER_R9_CROSS_SCREEN_AUDIT_PENDING":
        raise SystemExit(f"B1 screen review state drifted: {screen['role']}")

material = ledger["material_evidence"]
if material["head_sha"] != "69dc13fa94928be292237f082e77e656f792222b":
    raise SystemExit("B1 material evidence head drifted")
if material["reference_ui_run_id"] != 39583770008 or material["artifact_id"] != 12338007893:
    raise SystemExit("B1 material Reference UI evidence drifted")
if material["native_only_reference_hidden"] is not True:
    raise SystemExit("B1 native-only evidence may not include reference pixels")
if material["shared_secondary_chrome_completed"] is not True:
    raise SystemExit("B1 shared secondary chrome completion evidence missing")
if material["decision_native_project_underlay_completed"] is not True:
    raise SystemExit("B1 Decision native-underlay evidence missing")

screen_roles = [item["id"] for item in screen_review["screens"]]
if screen_roles != CANONICAL_ROLES:
    raise SystemExit("P1 screen review does not contain exactly the eight canonical roles")
if "recovery_checkpoint_fork" in screen_roles:
    raise SystemExit("Legacy recovery screen id survived B1 reconciliation")
if screen_review["phase_complete"] and not final_p1_approved:
    raise SystemExit("P1 screen review completed without the later governed R10 receipt")
if screen_review["native_reference_shell"]["final_native_reconstruction_complete"] and not final_p1_approved:
    raise SystemExit("Native reconstruction completed without the later governed R10 receipt")

if reference_shell["final_native_reconstruction_complete"]:
    raise SystemExit("Reference shell may not claim final reconstruction in B1")
if not reference_shell["native_reconstruction"]["all_eight_macro_reconstruction_complete"]:
    raise SystemExit("B1 lost the eight-screen macro reconstruction foundation")

if remainder["final_native_reconstruction_complete"] and not final_p1_approved:
    raise SystemExit("Remainder plan claimed final reconstruction without the later governed R10 receipt")
if remainder["stage8_opened"]:
    raise SystemExit("Remainder plan opened Stage 8")

expected_home_shell_status = (
    "IMPLEMENTED_INTERACTION_REVIEW_COMPLETE_B1_NATIVE_COMPLETION_APPROVED"
    if post is not None
    else "IMPLEMENTED_INTERACTION_REVIEW_COMPLETE_B1_NATIVE_COMPLETION_REVIEW_REQUIRED"
)
if home_shell["status"] != expected_home_shell_status:
    raise SystemExit("Home native-shell B1 lifecycle status drifted")
if home_fidelity["screen_final_approval"] or home_fidelity["p1_complete"]:
    raise SystemExit("Home fidelity contract falsely claims final approval")
if home_fidelity["stage8_opened"] or home_fidelity["runtime_authority"]:
    raise SystemExit("Home fidelity contract inflated authority")

review_roles = [item["role"] for item in b1_review["findings"]]
if review_roles != CANONICAL_ROLES:
    raise SystemExit("B1 material visual review does not cover all eight canonical roles")
if any(item["verdict"] != "NO_B1_BLOCKER" for item in b1_review["findings"]):
    raise SystemExit("B1 visual review contains an unresolved B1 blocker")
if b1_review["final_p1_approval"]:
    raise SystemExit("B1 visual review may not grant final P1 approval")
if post is None:
    if b1_review["r9_cross_screen_audit_opened"] or b1_review["r10_final_review_opened"]:
        raise SystemExit("B1 visual review opened R9/R10 before post-review")
else:
    if not b1_review["r9_cross_screen_audit_opened"]:
        raise SystemExit("B1 approval did not open R9/B2")
    if b1_review["r10_final_review_opened"]:
        raise SystemExit("B1 approval opened R10 too early")
    if b1_review["status"] != "APPROVED_B1_NATIVE_COMPLETION_ONLY":
        raise SystemExit("B1 material visual review did not finalize to scoped approval")

main_source = MAIN_WINDOW.read_text(encoding="utf-8")
ui_smoke_source = UI_SMOKE.read_text(encoding="utf-8")

for required_marker in (
    "BuildSecondarySharedChrome(screen);",
    "BuildSecondaryTopChrome();",
    "BuildSecondaryRightNavigation(screen);",
    "BuildSecondarySharedInteractions(screen);",
    "BuildNativeProjectWorkspaceCore();",
):
    if required_marker not in main_source:
        raise SystemExit(f"B1 native implementation marker missing: {required_marker}")

if 'Render(output, 1440, 900, "home-native-1440x900.png", "native")' not in ui_smoke_source:
    raise SystemExit("UiSmoke does not emit Home native-only evidence")
if 'referenceImage.Visibility = variant == "native"' not in ui_smoke_source:
    raise SystemExit("UiSmoke native mode does not explicitly hide reference pixels")

if post is None:
    if ledger["status"] != "MURTAKAZ_REVIEW_REQUIRED":
        raise SystemExit("B1 ledger must remain review-required before post-review")
    if any(item["state"] != "MICRO_POLISH_COMPLETE_REVIEW_REQUIRED" for item in ledger["screens"]):
        raise SystemExit("B1 screen states must remain review-required before post-review")
    if screen_review["status"] != "B1_NATIVE_COMPLETION_REVIEW_REQUIRED":
        raise SystemExit("P1 screen review must remain review-required before B1 approval")
    if remainder["phases"]["R9_CROSS_SCREEN_CONSISTENCY_AUDIT"]["state"] != "NOT_OPENED":
        raise SystemExit("R9 may not open before B1 post-review")
    if remainder["phases"]["R10_FINAL_MURTAKAZ_STUDIO_REVIEW"]["state"] != "NOT_OPENED":
        raise SystemExit("R10 may not open before B1 post-review")
    if project_context["active_work"] != ["REPAIR_WAVE_B1_COMPLETE_REMAINING_NATIVE_WORK"]:
        raise SystemExit("Project context must remain on B1 before post-review")
else:
    if post.get("decision") != "APPROVED_BY_AL_MURTAKAZ":
        raise SystemExit("B1 post-review exists with non-approved decision")
    if not post["adoption_authorized"] or not post["merge_authorized"]:
        raise SystemExit("B1 post-review did not authorize adoption/merge")
    if post["final_p1_approval_granted"]:
        raise SystemExit("B1 post-review may not grant final P1 approval")
    if post["live_execution_authorized"] or post["stage8_opened"]:
        raise SystemExit("B1 post-review inflated runtime authority")
    if ledger["status"] != "APPROVED_BY_AL_MURTAKAZ":
        raise SystemExit("B1 ledger did not finalize after post-review")
    if any(item["state"] != "MICRO_POLISH_COMPLETE" for item in ledger["screens"]):
        raise SystemExit("B1 did not close all eight screen micro-polish states")
    r9_state = remainder["phases"]["R9_CROSS_SCREEN_CONSISTENCY_AUDIT"]["state"]
    if r9_state not in {"READY_TO_CONTINUE", "CLOSED"}:
        raise SystemExit("B1 lifecycle regressed: R9 must be ready or validly closed by B2")
    r10_state = remainder["phases"]["R10_FINAL_MURTAKAZ_STUDIO_REVIEW"]["state"]
    if r10_state not in {"NOT_OPENED", "MURTAKAZ_STUDIO_REVIEW", "RETURNED_FOR_CHANGES", "CLOSED"}:
        raise SystemExit("B1 lifecycle advanced R10 outside the governed B3 review states")

    allowed_active_work = [
        ["REPAIR_WAVE_B2_CROSS_SCREEN_CONSISTENCY"],
        ["REPAIR_WAVE_B3_FINAL_REVIEW_P1_ACCEPTANCE_PENDING"],
        ["P1_EXIT_REMEDIATION_MOTION_AND_ANDROID"],
        ["P1_COMPLETE_NEXT_PHASE_OWNER_DECISION_REQUIRED"],
    ]
    if (
        stage7_readiness_post is not None
        and stage7_readiness_post.get("decision") == "APPROVED_BY_AL_MURTAKAZ"
        and stage7_readiness_post.get("repository_readiness_complete") is True
        and stage7_readiness_post.get("stage7_final_lock_granted") is False
    ):
        allowed_active_work.append(["STAGE7_REAL_HOST_EVIDENCE_PENDING"])
    if project_context["active_work"] not in allowed_active_work:
        raise SystemExit(
            "B1 lifecycle active work is outside the governed B2/B3/P1/Stage7 successor states"
        )

    allowed_screen_review_status = {
        "B1_NATIVE_COMPLETION_APPROVED_R9_READY",
        "B2_CROSS_SCREEN_APPROVED_B3_READY",
        "B3_RETURNED_FOR_CHANGES_EXIT_EVIDENCE_PENDING",
        "P1_FINAL_ACCEPTED_BY_AL_MURTAKAZ",
    }
    if screen_review["status"] not in allowed_screen_review_status:
        raise SystemExit("B1 lifecycle screen review regressed or advanced outside the governed B2 successor")

    allowed_screen_decisions = {
        "B1_NATIVE_COMPLETION_APPROVED",
        "B2_CROSS_SCREEN_CONSISTENCY_APPROVED",
        "B3_DESKTOP_FINAL_FIDELITY_APPROVED",
    }
    if any(item["murtakaz_decision"] not in allowed_screen_decisions for item in screen_review["screens"]):
        raise SystemExit("B1 scoped per-screen Murtakaz decisions regressed or drifted")
    if any(item["workshop_decision"] not in allowed_screen_decisions for item in screen_review["screens"]):
        raise SystemExit("B1 scoped per-screen Workshop decisions regressed or drifted")

    if reference_shell["status"] != "B1_NATIVE_COMPLETION_APPROVED_R9_READY":
        raise SystemExit("Reference shell lost the approved B1 checkpoint")
    if home_fidelity["status"] != "NATIVE_REFERENCE_SHELL_B1_COMPLETION_APPROVED_R9_READY":
        raise SystemExit("Home fidelity lost the approved B1 checkpoint")

print("Al-Murtakaz Visual B1 native completion validation: PASS")
