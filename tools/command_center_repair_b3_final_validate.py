from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "command-center"
PROJECT = STATE / "project-governance"

CHANGE = PROJECT / "changes" / "2026-10-21-repair-b3-final-p1-acceptance.json"
PRE = PROJECT / "approvals" / "2026-10-21-repair-b3-final-p1-acceptance-pre.json"
RETURN = PROJECT / "approvals" / "2026-10-21-repair-b3-final-p1-acceptance-return.json"
RETURN_ADOPTION = PROJECT / "approvals" / "2026-10-21-repair-b3-return-state-adoption.json"
REMEDIATION_POST = PROJECT / "approvals" / "2026-10-21-p1-exit-remediation-motion-android-post.json"
POST = PROJECT / "approvals" / "2026-10-21-repair-b3-final-p1-acceptance-post.json"
CAPSULE = PROJECT / "context-capsules" / "2026-10-21-repair-b3-final-p1-acceptance.json"
PLAN = STATE / "living-operations-p1-b3-final-review.json"
RESULT = STATE / "living-operations-p1-b3-final-review-result.json"
P1 = STATE / "living-operations-p1-visual-phase.json"
SCREEN_REVIEW = STATE / "living-operations-p1-screen-review.json"
REMAINDER = STATE / "living-operations-p1-remainder-phases.json"

ROLES = [
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


for required in (CHANGE, PRE, RETURN, RETURN_ADOPTION, CAPSULE, PLAN, RESULT, P1, SCREEN_REVIEW, REMAINDER):
    if not required.exists():
        raise SystemExit(f"missing B3 artifact: {required.relative_to(ROOT)}")

change = load(CHANGE)
pre = load(PRE)
returned = load(RETURN)
return_adoption = load(RETURN_ADOPTION)
capsule = load(CAPSULE)
plan = load(PLAN)
result = load(RESULT)
p1 = load(P1)
screen_review = load(SCREEN_REVIEW)
remainder = load(REMAINDER)
post = load(POST) if POST.exists() else None
remediation_post = load(REMEDIATION_POST) if REMEDIATION_POST.exists() else None

if change["change_id"] != "CC-REPAIR-B3-FINAL-P1-ACCEPTANCE-2026-10-21":
    raise SystemExit("B3 change id drifted")
if change["base_revision"]["sha"] != "77a0e21bd40fc4a306fe75cc131e9c5740110db6":
    raise SystemExit("B3 canonical base drifted")
if change["unplanned_scope_policy"] != "RETURN_TICKET_OR_NEW_CHANGE_ENVELOPE":
    raise SystemExit("B3 scope-growth policy drifted")

if pre["decision"] != "APPROVE_TO_IMPLEMENT" or not pre["implementation_authorized"]:
    raise SystemExit("B3 final review lacks Murtakaz pre-approval")
if pre["final_p1_approval_granted"] or pre["merge_authorized"]:
    raise SystemExit("B3 pre-review pre-authorized final P1 approval or merge")
if pre["live_execution_authorized"] or pre["stage8_opened"]:
    raise SystemExit("B3 pre-review inflated runtime authority")

if capsule["job_or_change_id"] != change["change_id"] or not capsule["immutable"]:
    raise SystemExit("B3 Context Capsule binding drifted")

if result["evidence"]["head_sha"] != "77a0e21bd40fc4a306fe75cc131e9c5740110db6":
    raise SystemExit("B3 review is not bound to the canonical B2 merge head")
if result["evidence"]["company_stage0_run_id"] != 39600198879:
    raise SystemExit("B3 Company Stage 0 evidence drifted")
if result["evidence"]["codeql_run_id"] != 39600198990:
    raise SystemExit("B3 CodeQL evidence drifted")
if result["evidence"]["reference_ui_run_id"] != 39600198955:
    raise SystemExit("B3 Reference UI evidence drifted")
if result["evidence"]["reference_ui_artifact_id"] != 12345134475:
    raise SystemExit("B3 Reference UI artifact drifted")

if [item["id"] for item in result["desktop_screens"]] != ROLES:
    raise SystemExit("B3 final review does not cover exactly the eight canonical desktop screens")
if any(item["verdict"] != "APPROVE_DESKTOP_FINAL_FIDELITY_ONLY" for item in result["desktop_screens"]):
    raise SystemExit("B3 desktop fidelity review contains an unresolved desktop blocker")

expected_blockers = {"P1_MOTION_CAPTURE_MISSING", "P1_ANDROID_SEMANTIC_ADAPTATION_MISSING"}
if {item["id"] for item in result["blockers"]} != expected_blockers:
    raise SystemExit("B3 return blockers drifted")
if set(returned["blockers"]) != expected_blockers:
    raise SystemExit("B3 return receipt blockers drifted")
if returned["decision"] != "RETURNED_FOR_CHANGES":
    raise SystemExit("B3 return receipt no longer records RETURNED_FOR_CHANGES")
if returned["final_p1_approval_granted"] or returned["p1_complete"]:
    raise SystemExit("B3 return receipt falsely closes P1")
if returned["live_execution_authorized"] or returned["stage8_opened"]:
    raise SystemExit("B3 return receipt inflated runtime authority")
if return_adoption["decision"] != "APPROVED_BY_AL_MURTAKAZ":
    raise SystemExit("B3 return state lacks Murtakaz adoption approval")
if not return_adoption["adoption_authorized"] or not return_adoption["merge_authorized"]:
    raise SystemExit("B3 return state adoption is not merge-authorized")
if return_adoption["final_p1_approval_granted"] or return_adoption["p1_complete"]:
    raise SystemExit("B3 return-state adoption falsely grants final P1 approval")
if return_adoption["live_execution_authorized"] or return_adoption["stage8_opened"]:
    raise SystemExit("B3 return-state adoption inflated runtime authority")

if remainder["phases"]["R9_CROSS_SCREEN_CONSISTENCY_AUDIT"]["state"] != "CLOSED":
    raise SystemExit("B3 final review requires R9/B2 to be closed first")
if p1["stage8_opened"] or p1["runtime_authority"]:
    raise SystemExit("B3 may not open Stage 8 or runtime authority")

if post is None:
    if p1["status"] != "IN_PROGRESS":
        raise SystemExit("Returned B3 review must keep P1 IN_PROGRESS")
    if plan["status"] != "RETURNED_FOR_CHANGES_EXIT_EVIDENCE_PENDING":
        raise SystemExit("B3 plan must expose returned-for-changes state")
    if result["status"] != "RETURNED_FOR_CHANGES_EXIT_EVIDENCE_PENDING":
        raise SystemExit("B3 result must expose returned-for-changes state")
    if result["final_p1_approval"] or result["p1_complete"]:
        raise SystemExit("B3 result falsely closes P1")
    if remainder["phases"]["R10_FINAL_MURTAKAZ_STUDIO_REVIEW"]["state"] != "RETURNED_FOR_CHANGES":
        raise SystemExit("R10 must be RETURNED_FOR_CHANGES while exit evidence is missing")
    if screen_review["status"] != "B3_RETURNED_FOR_CHANGES_EXIT_EVIDENCE_PENDING":
        raise SystemExit("Screen review is not aligned to the B3 return state")
    if screen_review["phase_complete"]:
        raise SystemExit("Returned B3 review may not complete P1")
    if [item["id"] for item in screen_review["screens"]] != ROLES:
        raise SystemExit("B3 screen review role set drifted")
    if any(item["murtakaz_decision"] != "B3_DESKTOP_FINAL_FIDELITY_APPROVED" for item in screen_review["screens"]):
        raise SystemExit("B3 desktop per-screen review decisions drifted")
    if screen_review["shared_motion"]["state"] != "B3_EXIT_EVIDENCE_MISSING":
        raise SystemExit("B3 motion exit blocker is not represented")
    if screen_review["android_semantic_pair"]["state"] != "B3_EXIT_EVIDENCE_MISSING":
        raise SystemExit("B3 Android exit blocker is not represented")
else:
    if post.get("decision") != "APPROVED_BY_AL_MURTAKAZ":
        raise SystemExit("B3 post-review exists without final Murtakaz approval")
    if not post.get("final_p1_approval_granted") or not post.get("p1_complete"):
        raise SystemExit("B3 post-review exists without complete final P1 approval")
    if post.get("live_execution_authorized") or post.get("stage8_opened"):
        raise SystemExit("Final P1 visual approval may not grant runtime authority or open Stage 8")
    if remediation_post is None or remediation_post.get("decision") != "APPROVED_BY_AL_MURTAKAZ":
        raise SystemExit("Final P1 approval lacks the governed exit-remediation receipt")
    if not remediation_post.get("motion_capture_accepted") or not remediation_post.get("reduced_motion_capture_accepted"):
        raise SystemExit("Final P1 approval lacks accepted full/reduced motion evidence")
    if not remediation_post.get("android_semantic_adaptation_accepted"):
        raise SystemExit("Final P1 approval lacks accepted Android semantic evidence")
    if remediation_post.get("final_p1_approval_granted"):
        raise SystemExit("Exit-remediation receipt improperly self-granted final P1 approval")
    if p1["status"] != "APPROVED_BY_AL_MURTAKAZ":
        raise SystemExit("Final P1 receipt exists but P1 state is not approved")
    if plan["status"] != "APPROVED_BY_AL_MURTAKAZ_P1_COMPLETE":
        raise SystemExit("B3 final-review plan is not resolved to P1 complete")
    if remainder["phases"]["R10_FINAL_MURTAKAZ_STUDIO_REVIEW"]["state"] != "CLOSED":
        raise SystemExit("Final P1 receipt exists but R10 is not closed")
    if not remainder["final_native_reconstruction_complete"]:
        raise SystemExit("Final P1 receipt exists but native reconstruction is not complete")
    if screen_review["status"] != "P1_FINAL_ACCEPTED_BY_AL_MURTAKAZ" or not screen_review["phase_complete"]:
        raise SystemExit("Final P1 receipt exists but screen review is not final")
    if screen_review["shared_motion"]["state"] != "P1_EXIT_EVIDENCE_ACCEPTED":
        raise SystemExit("Final P1 receipt exists without accepted motion state")
    if screen_review["android_semantic_pair"]["state"] != "P1_EXIT_EVIDENCE_ACCEPTED":
        raise SystemExit("Final P1 receipt exists without accepted Android semantic state")
    if not screen_review["native_reference_shell"]["final_native_reconstruction_complete"]:
        raise SystemExit("Final P1 receipt exists but native reference shell is not complete")

print("Al-Murtakaz Visual B3 final P1 review validation: PASS")
