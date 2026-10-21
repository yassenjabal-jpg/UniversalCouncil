from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "command-center"
PROJECT = STATE / "project-governance"

LOCK = PROJECT / "repair-wave-a-truth-lock.json"
LOCK_BUILDER = ROOT / "tools" / "build_command_center_repair_wave_a_truth_lock.py"
A1_POST = PROJECT / "approvals" / "2026-10-21-repair-a1-context-baseline-post.json"
A2_POST = PROJECT / "approvals" / "2026-10-21-repair-a2-governance-metadata-post.json"
A3_PRE = PROJECT / "approvals" / "2026-10-21-repair-a3-truth-lock-pre.json"
A3_POST = PROJECT / "approvals" / "2026-10-21-repair-a3-truth-lock-post.json"
A3_CHANGE = PROJECT / "changes" / "2026-10-21-repair-a3-truth-lock.json"
A3_CAPSULE = PROJECT / "context-capsules" / "2026-10-21-repair-a3-truth-lock.json"
LOCK_FIX_PRE = PROJECT / "approvals" / "2026-10-21-wave-a-historical-lock-correction-pre.json"
LOCK_FIX_POST = PROJECT / "approvals" / "2026-10-21-wave-a-historical-lock-correction-post.json"
LOCK_FIX_CHANGE = PROJECT / "changes" / "2026-10-21-wave-a-historical-lock-correction.json"
LOCK_FIX_CAPSULE = PROJECT / "context-capsules" / "2026-10-21-wave-a-historical-lock-correction.json"

CURRENT_REVIEW = PROJECT / "agentic-os-current-review.json"
HISTORICAL_REVIEW = PROJECT / "agentic-os-latest-review.json"
STAGE_MAP = PROJECT / "stage-phase-map.json"
PHASE0 = STATE / "phase0-execution-gates.json"
CONTEXT = STATE / "context-pipeline-state.json"
GATEWAY = STATE / "gateway-routing-state.json"
CAP_MODEL = STATE / "capability-model-state.json"
MODEL_POLICY = STATE / "model-broker-policy.json"
GATEWAY_POLICY = STATE / "gateway-routing-policy.json"
VISUAL_P1 = STATE / "living-operations-p1-visual-phase.json"
REFERENCE_MANIFEST = STATE / "living-operations-reference-manifest.json"
UX_STATE = STATE / "living-operations-ux-state-contract.json"
ROADMAP = ROOT / "docs" / "operations" / "command-center" / "COMMAND_CENTER_ROADMAP_2026-10-19.md"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


for required in (
    LOCK,
    LOCK_BUILDER,
    A1_POST,
    A2_POST,
    A3_PRE,
    A3_CHANGE,
    A3_CAPSULE,
    LOCK_FIX_PRE,
    LOCK_FIX_CHANGE,
    LOCK_FIX_CAPSULE,
    CURRENT_REVIEW,
    HISTORICAL_REVIEW,
    STAGE_MAP,
    PHASE0,
    CONTEXT,
    GATEWAY,
    CAP_MODEL,
    MODEL_POLICY,
    GATEWAY_POLICY,
    VISUAL_P1,
    REFERENCE_MANIFEST,
    UX_STATE,
    ROADMAP,
):
    if not required.exists():
        raise SystemExit(f"missing Wave A closure artifact: {required.relative_to(ROOT)}")

lock = load(LOCK)
a1 = load(A1_POST)
a2 = load(A2_POST)
a3_pre = load(A3_PRE)
a3_post = load(A3_POST) if A3_POST.exists() else None
a3_change = load(A3_CHANGE)
a3_capsule = load(A3_CAPSULE)
lock_fix_pre = load(LOCK_FIX_PRE)
lock_fix_post = load(LOCK_FIX_POST) if LOCK_FIX_POST.exists() else None
lock_fix_change = load(LOCK_FIX_CHANGE)
lock_fix_capsule = load(LOCK_FIX_CAPSULE)
current_review = load(CURRENT_REVIEW)
historical_review = load(HISTORICAL_REVIEW)
stage_map = load(STAGE_MAP)
phase0 = load(PHASE0)
context = load(CONTEXT)
gateway = load(GATEWAY)
cap_model = load(CAP_MODEL)
model_policy = load(MODEL_POLICY)
gateway_policy = load(GATEWAY_POLICY)
visual_p1 = load(VISUAL_P1)
reference_manifest = load(REFERENCE_MANIFEST)
ux_state = load(UX_STATE)
roadmap = ROADMAP.read_text(encoding="utf-8")

subprocess.run(
    [__import__("sys").executable, str(LOCK_BUILDER), "--check"],
    cwd=ROOT,
    check=True,
)

if a1["decision"] != "APPROVED_BY_AL_MURTAKAZ":
    raise SystemExit("Repair A1 is not approved")
if a2["decision"] != "APPROVED_BY_AL_MURTAKAZ":
    raise SystemExit("Repair A2 is not approved")
if a3_pre["decision"] != "APPROVE_TO_IMPLEMENT":
    raise SystemExit("Repair A3 lacks Murtakaz pre-approval")
if a3_pre["canonical_base"]["sha"] != "76eeca02b79790c28a181520cc019d3586769b26":
    raise SystemExit("Repair A3 baseline drifted")
if a3_pre["live_execution_authorized"] or a3_pre["stage8_opened"]:
    raise SystemExit("Repair A3 pre-approval inflated authority")
if a3_pre["final_adoption_granted"] or a3_pre["merge_authorized"]:
    raise SystemExit("Repair A3 pre-approval may not pre-authorize merge")

if a3_change["pre_approval_receipt"] != (
    "state/command-center/project-governance/approvals/2026-10-21-repair-a3-truth-lock-pre.json"
):
    raise SystemExit("Repair A3 Change Envelope is not bound to its pre-approval")
if a3_change["unplanned_scope_policy"] != "RETURN_TICKET_OR_NEW_CHANGE_ENVELOPE":
    raise SystemExit("Repair A3 scope-growth rule drifted")
if a3_capsule["job_or_change_id"] != a3_change["change_id"] or not a3_capsule["immutable"]:
    raise SystemExit("Repair A3 Context Capsule binding drifted")

if lock["lock_id"] != "MRTKZ-REPAIR-WAVE-A-TRUTH-LOCK-2026-10-21":
    raise SystemExit("Wave A truth lock id drifted")
if lock["schema_version"] != "1.1":
    raise SystemExit("Wave A truth lock must use historical-anchor schema 1.1")
if lock["baseline_revision"] != a3_pre["canonical_base"]["sha"]:
    raise SystemExit("Wave A truth lock baseline differs from A3 pre-approval")
if lock["locked_revision"] != "49a013f5fe653c40b43e7a0ca4dd68fc98845fc7":
    raise SystemExit("Wave A historical locked revision drifted")
if lock["validation_mode"] != "LOCKED_REVISION_SOURCE_BLOBS_MATCH_HISTORICAL_COMMIT":
    raise SystemExit("Wave A truth lock validation mode is not historical")
if lock["immutable_after_approval"] is not True:
    raise SystemExit("Wave A approved truth lock must be immutable")
if lock["head_progression_allowed_after_lock"] is not True:
    raise SystemExit("Wave A truth lock blocks governed post-lock progression")
if lock["repair_lineage"]["A1"] != "APPROVED_BY_AL_MURTAKAZ":
    raise SystemExit("Wave A truth lock lost A1 approval")
if lock["repair_lineage"]["A2"] != "APPROVED_BY_AL_MURTAKAZ":
    raise SystemExit("Wave A truth lock lost A2 approval")

if a3_post is None:
    if lock["status"] != "CANDIDATE_REVIEW":
        raise SystemExit("Wave A truth lock must remain candidate before A3 post-review")
    if lock["repair_lineage"]["A3"] != "IN_REVIEW":
        raise SystemExit("Wave A truth lock A3 state must remain IN_REVIEW before post-review")
    if lock["post_review_receipt"] is not None:
        raise SystemExit("Wave A truth lock cannot claim a post-review receipt before approval")
else:
    if a3_post.get("decision") != "APPROVED_BY_AL_MURTAKAZ":
        raise SystemExit("A3 post-review receipt exists with non-approved decision")
    if lock["status"] != "APPROVED_BY_AL_MURTAKAZ":
        raise SystemExit("Wave A truth lock is not approved after A3 post-review")
    if lock["repair_lineage"]["A3"] != "APPROVED_BY_AL_MURTAKAZ":
        raise SystemExit("Wave A truth lock did not close A3")
    if lock["post_review_receipt"] != (
        "state/command-center/project-governance/approvals/2026-10-21-repair-a3-truth-lock-post.json"
    ):
        raise SystemExit("Wave A truth lock post-review pointer drifted")
    if not a3_post["adoption_authorized"] or not a3_post["merge_authorized"]:
        raise SystemExit("A3 post-review did not authorize adoption/merge")
    if a3_post["live_execution_authorized"] or a3_post["stage8_opened"]:
        raise SystemExit("A3 post-review inflated runtime authority")

if lock_fix_pre["decision"] != "APPROVE_TO_IMPLEMENT":
    raise SystemExit("Wave A historical-lock correction lacks Murtakaz pre-approval")
if lock_fix_pre["canonical_base"]["sha"] != "49a013f5fe653c40b43e7a0ca4dd68fc98845fc7":
    raise SystemExit("Wave A historical-lock correction canonical base drifted")
if lock_fix_pre["live_execution_authorized"] or lock_fix_pre["stage8_opened"]:
    raise SystemExit("Wave A historical-lock correction inflated authority")
if lock_fix_pre["final_adoption_granted"] or lock_fix_pre["merge_authorized"]:
    raise SystemExit("Wave A historical-lock correction pre-approved adoption/merge")
if lock_fix_change["pre_approval_receipt"] != (
    "state/command-center/project-governance/approvals/"
    "2026-10-21-wave-a-historical-lock-correction-pre.json"
):
    raise SystemExit("Wave A historical-lock correction Change Envelope drifted")
if lock_fix_change["evidence_precondition"]["mismatch_count"] != 0:
    raise SystemExit("Wave A historical-lock correction did not prove historical blob identity")
if lock_fix_capsule["job_or_change_id"] != lock_fix_change["change_id"] or not lock_fix_capsule["immutable"]:
    raise SystemExit("Wave A historical-lock correction capsule drifted")

anchor_correction = lock.get("historical_anchor_correction") or {}
if anchor_correction.get("change_id") != "CC-WAVE-A-HISTORICAL-LOCK-CORRECTION-2026-10-21":
    raise SystemExit("Wave A truth lock historical correction identity drifted")
if anchor_correction.get("proof") != "ALL_18_LOCKED_SOURCE_BLOBS_MATCH_A3_MERGE_REVISION":
    raise SystemExit("Wave A truth lock historical correction proof drifted")

if lock_fix_post is None:
    if anchor_correction.get("status") != "MURTAKAZ_REVIEW_REQUIRED":
        raise SystemExit("Wave A historical-lock correction must remain review-required before post-review")
else:
    if lock_fix_post.get("decision") != "APPROVED_BY_AL_MURTAKAZ":
        raise SystemExit("Wave A historical-lock correction post-review is not approved")
    if not lock_fix_post["adoption_authorized"] or not lock_fix_post["merge_authorized"]:
        raise SystemExit("Wave A historical-lock correction post-review did not authorize adoption/merge")
    if lock_fix_post["live_execution_authorized"] or lock_fix_post["stage8_opened"]:
        raise SystemExit("Wave A historical-lock correction post-review inflated authority")
    if anchor_correction.get("status") != "APPROVED_BY_AL_MURTAKAZ":
        raise SystemExit("Wave A truth lock historical correction did not finalize")
    if anchor_correction.get("post_approval") != (
        "state/command-center/project-governance/approvals/"
        "2026-10-21-wave-a-historical-lock-correction-post.json"
    ):
        raise SystemExit("Wave A truth lock historical correction post-review pointer drifted")

delivery = stage_map["delivery"]
if delivery["authoritative_current_stage"] != "STAGE_7":
    raise SystemExit("Wave A closure changed authoritative stage")
stage8 = next(item for item in delivery["stages"] if item["id"] == "STAGE_8")
if stage8["status"] != "NOT_OPENED" or stage_map["rules"]["stage8_opened"]:
    raise SystemExit("Wave A closure opened Stage 8")

if phase0["live_execution_authorized"]:
    raise SystemExit("Wave A closure may not enable live execution")
if all(item["status"] == "PASS" for item in phase0["gates"].values()):
    raise SystemExit("Wave A closure falsely treats Phase0 as fully passed")

if context["status"] != "APPROVED_BY_AL_MURTAKAZ":
    raise SystemExit("Context pipeline is not approved at Wave A closure")
if context["authority"]["live_execution_authorized"] or context["authority"]["stage8_opened"]:
    raise SystemExit("Context pipeline inflated authority")

if gateway["status"] != "APPROVED_BY_AL_MURTAKAZ":
    raise SystemExit("Gateway is not approved at Wave A closure")
if gateway["laws"]["execution_authorized"] or gateway["laws"]["live_dispatch_allowed"]:
    raise SystemExit("Gateway inflated execution authority")
if gateway["laws"]["provider_invocation_authorized"]:
    raise SystemExit("Gateway inflated provider invocation authority")
if gateway["components"]["skill_registry"] != "NOT_IMPLEMENTED":
    raise SystemExit("Skill Registry was implemented before repair closure")
if gateway["components"]["job_engine"] != "NOT_IMPLEMENTED":
    raise SystemExit("Job Engine was implemented before repair closure")

if cap_model["status"] != "APPROVED_BY_AL_MURTAKAZ":
    raise SystemExit("Capability/Model state is not approved")
if cap_model["components"]["model_provider_calls"] != "DISCONNECTED":
    raise SystemExit("Model provider calls were connected during repairs")
if cap_model["components"]["skill_registry"] != "NOT_IMPLEMENTED":
    raise SystemExit("Capability state falsely implements Skill Registry")
if cap_model["components"]["job_engine"] != "NOT_IMPLEMENTED":
    raise SystemExit("Capability state falsely implements Job Engine")
if cap_model["laws"]["provider_invocation_authorized"]:
    raise SystemExit("Capability/Model state authorized provider invocation")
if cap_model["laws"]["execution_authority_granted"]:
    raise SystemExit("Capability/Model state granted execution authority")

if model_policy["provider_calls_connected"]:
    raise SystemExit("Model Broker policy connected provider calls")
if model_policy["silent_fallback_allowed"]:
    raise SystemExit("Model Broker policy enabled silent fallback")
if model_policy["models"]:
    raise SystemExit("Production model catalog must remain empty while providers are disconnected")

if gateway_policy["live_dispatch_allowed"]:
    raise SystemExit("Gateway policy enabled live dispatch")
if gateway_policy["execution_policy"]["live_execution_authorized"]:
    raise SystemExit("Gateway policy enabled live execution")
if gateway_policy["execution_policy"]["stage8_opened"]:
    raise SystemExit("Gateway policy opened Stage 8")
if gateway_policy["future_dependencies"]["skill_registry"] != "NOT_IMPLEMENTED":
    raise SystemExit("Gateway policy falsely implements Skill Registry")
if gateway_policy["future_dependencies"]["job_engine"] != "NOT_IMPLEMENTED":
    raise SystemExit("Gateway policy falsely implements Job Engine")

if visual_p1["status"] != "IN_PROGRESS":
    raise SystemExit("Wave A closure falsely completed Visual P1")
if visual_p1["governance"]["final_approval_required"] is not True:
    raise SystemExit("Visual P1 final approval requirement was weakened")
if visual_p1["stage8_opened"]:
    raise SystemExit("Visual P1 opened Stage 8")
if visual_p1["runtime_authority"]:
    raise SystemExit("Visual P1 gained runtime authority")

refs = reference_manifest["references"]
if len(refs) != 8:
    raise SystemExit("Canonical visual reference count drifted from eight")
if len({item["role"] for item in refs}) != 8:
    raise SystemExit("Canonical visual reference roles are not unique")
if [item["order"] for item in refs] != list(range(1, 9)):
    raise SystemExit("Canonical visual reference order drifted")

if ux_state["status"] != "APPROVED_BY_AL_MURTAKAZ":
    raise SystemExit("UX State Contract lost Murtakaz approval")

if historical_review["record_status"] != "HISTORICAL_SUPERSEDED":
    raise SystemExit("Historical Agentic review again presents as current")
if historical_review["verdict"] != "RETURN_FOR_ALIGNMENT":
    raise SystemExit("Historical RETURN_FOR_ALIGNMENT verdict was rewritten")
if current_review["record_status"] != "CURRENT_CANONICAL_REVIEW_SUMMARY":
    raise SystemExit("Current Agentic review lost canonical status")
if current_review["repair_program"]["wave_a"]["A1"] != "COMPLETE_APPROVED":
    raise SystemExit("Current review lost A1 completion")
if current_review["repair_program"]["wave_a"]["A2"] != "COMPLETE_APPROVED":
    raise SystemExit("Current review lost A2 completion")

if a3_post is None:
    if current_review["repair_program"]["wave_a"]["A3"] != "ACTIVE":
        raise SystemExit("Current review must keep A3 ACTIVE before post-review")
else:
    if current_review["repair_program"]["wave_a"]["A3"] != "COMPLETE_APPROVED":
        raise SystemExit("Current review did not close A3 after approval")
    if current_review["repair_program"]["wave_b"] != "ACTIVE":
        raise SystemExit("Current review did not activate Wave B after A3 approval")

protected = lock["protected_truth"]
expected_protected = {
    "authoritative_stage": "STAGE_7",
    "stage8_status": "NOT_OPENED",
    "live_execution_authorized": False,
    "phase0_all_gates_passed": False,
    "visual_reference_count": 8,
    "visual_p1_status": "IN_PROGRESS",
    "model_provider_calls_connected": False,
    "real_autopilot_status": "NOT_IMPLEMENTED",
    "skill_registry_status": "NOT_IMPLEMENTED",
    "job_engine_status": "NOT_IMPLEMENTED",
    "android_live_state": "UNPROVEN",
}
if protected != expected_protected:
    raise SystemExit("Wave A truth lock protected-truth snapshot drifted")

if lock["next_active_work_after_approval"] != "REPAIR_WAVE_B1_COMPLETE_REMAINING_NATIVE_WORK":
    raise SystemExit("Wave A truth lock next active work drifted")

required_roadmap = (
    "A1 Context & Baseline Repair — COMPLETE / APPROVED_BY_AL_MURTAKAZ",
    "A2 Governance Metadata Reconciliation — COMPLETE / APPROVED_BY_AL_MURTAKAZ",
)
for marker in required_roadmap:
    if marker not in roadmap:
        raise SystemExit(f"Roadmap lost repair completion marker: {marker}")

if a3_post is None:
    if "A3 Truth Lock + Murtakaz Closure — ACTIVE" not in roadmap:
        raise SystemExit("Roadmap must show A3 ACTIVE before post-review")
else:
    if "A3 Truth Lock + Murtakaz Closure — COMPLETE / APPROVED_BY_AL_MURTAKAZ" not in roadmap:
        raise SystemExit("Roadmap did not close A3")
    if "**Wave status: COMPLETE / APPROVED_BY_AL_MURTAKAZ**" not in roadmap:
        raise SystemExit("Roadmap lost Wave A closure")
    if "### Wave B — Visual P1 Completion" not in roadmap:
        raise SystemExit("Roadmap lost governed Wave B continuation")

print("Al-Murtakaz Repair Wave A truth-lock validation: PASS")
