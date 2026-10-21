from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "command-center"
PROJECT = STATE / "project-governance"
ROADMAP = ROOT / "docs" / "operations" / "command-center" / "COMMAND_CENTER_ROADMAP_2026-10-19.md"

INVARIANTS = PROJECT / "architecture-invariants.json"
OLD_REVIEW = PROJECT / "agentic-os-latest-review.json"
CURRENT_REVIEW = PROJECT / "agentic-os-current-review.json"
AGENTIC_POST = PROJECT / "approvals" / "2026-10-21-agentic-os-integration-post.json"
A2_PRE = PROJECT / "approvals" / "2026-10-21-repair-a2-governance-metadata-pre.json"
A2_POST = PROJECT / "approvals" / "2026-10-21-repair-a2-governance-metadata-post.json"
A2_CHANGE = PROJECT / "changes" / "2026-10-21-repair-a2-governance-metadata.json"
A2_CAPSULE = PROJECT / "context-capsules" / "2026-10-21-repair-a2-governance-metadata.json"
STAGE_MAP = PROJECT / "stage-phase-map.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


for required in (
    INVARIANTS,
    OLD_REVIEW,
    CURRENT_REVIEW,
    AGENTIC_POST,
    A2_PRE,
    A2_CHANGE,
    A2_CAPSULE,
    STAGE_MAP,
    ROADMAP,
):
    if not required.exists():
        raise SystemExit(f"missing governance-metadata artifact: {required.relative_to(ROOT)}")

invariants = load(INVARIANTS)
old_review = load(OLD_REVIEW)
current_review = load(CURRENT_REVIEW)
agentic_post = load(AGENTIC_POST)
a2_pre = load(A2_PRE)
a2_post = load(A2_POST) if A2_POST.exists() else None
a2_change = load(A2_CHANGE)
a2_capsule = load(A2_CAPSULE)
stage_map = load(STAGE_MAP)
roadmap = ROADMAP.read_text(encoding="utf-8")

if invariants["status"] != "ACTIVE":
    raise SystemExit("Architecture invariants must remain ACTIVE")
if invariants.get("last_reconciled_change_id") != "CC-REPAIR-A2-GOVERNANCE-METADATA-2026-10-21":
    raise SystemExit("Architecture invariants were not reconciled by A2")

by_id = {item["id"]: item for item in invariants["invariants"]}
expected_now = {
    "AO-003": (
        "ENFORCED_NOW",
        "command_center_gateway_routing_validate + UniversalCouncil.CommandCenter.GatewayValidation",
    ),
    "AO-008": (
        "ENFORCED_NOW",
        "command_center_context_pipeline_validate + UniversalCouncil.CommandCenter.ContextValidation",
    ),
    "AO-013": (
        "ENFORCED_NOW",
        "command_center_capability_model_validate + command_center_gateway_routing_validate",
    ),
    "AO-014": (
        "ENFORCED_NOW",
        "command_center_capability_model_validate + UniversalCouncil.CommandCenter.CapabilityModelValidation",
    ),
    "AO-021": (
        "ENFORCED_NOW",
        "command_center_capability_model_validate + UniversalCouncil.CommandCenter.CapabilityModelValidation",
    ),
}
for invariant_id, (state, validator_name) in expected_now.items():
    item = by_id[invariant_id]
    if item["implementation_state"] != state:
        raise SystemExit(f"{invariant_id} implementation metadata is stale")
    if item["validator"] != validator_name:
        raise SystemExit(f"{invariant_id} validator metadata is stale")

ao006 = by_id["AO-006"]
if ao006["implementation_state"] != "ENFORCED_FOR_CONTEXT_RESOLVER_EXTERNAL_RETRIEVAL_FUTURE":
    raise SystemExit("AO-006 must distinguish implemented Context Resolver from future retrieval adapters")
if ao006["validator"] != (
    "command_center_context_pipeline_validate + UniversalCouncil.CommandCenter.ContextValidation"
):
    raise SystemExit("AO-006 validator metadata drifted")

future_expected = {
    "AO-011": "CONTRACT_ACTIVE",
    "AO-015": "CONTRACT_ACTIVE",
    "AO-019": "CONTRACT_ACTIVE",
    "AO-020": "CONTRACT_ACTIVE",
    "AO-022": "FUTURE_BLOCKER",
    "AO-023": "FUTURE_BLOCKER",
}
for invariant_id, state in future_expected.items():
    if by_id[invariant_id]["implementation_state"] != state:
        raise SystemExit(f"{invariant_id} was falsely promoted or regressed")

if old_review["verdict"] != "RETURN_FOR_ALIGNMENT":
    raise SystemExit("Historical Agentic review verdict was rewritten")
if old_review.get("record_status") != "HISTORICAL_SUPERSEDED":
    raise SystemExit("Old Agentic review still presents itself as current truth")
if old_review.get("historical_verdict_preserved") is not True:
    raise SystemExit("Historical review preservation marker missing")
if old_review.get("superseded_by") != (
    "state/command-center/project-governance/agentic-os-current-review.json"
):
    raise SystemExit("Historical review supersession pointer drifted")

if current_review["record_status"] != "CURRENT_CANONICAL_REVIEW_SUMMARY":
    raise SystemExit("Current Agentic review record is not canonical")
if current_review["current_verdict"] != "APPROVED_BY_AL_MURTAKAZ_WITH_REPAIR_PROGRAM_ACTIVE":
    raise SystemExit("Current Agentic review verdict drifted")
if current_review["historical_review_verdict_preserved"] != "RETURN_FOR_ALIGNMENT":
    raise SystemExit("Current review lost the historical dissent/return verdict")

expected_lineage = {
    56: "91aa5604fea04d6ddb9cc89769e5afa139e817d6",
    57: "379820e27e70609c724740e2e138baa8b8a92c7d",
    58: "8cb72d3f04b6396d9d594924446dd8dc9c896aff",
    59: "ea35e6d24931e5981d164fed89b0d494f80c2b44",
    60: "b3ef5d8f60e3f623371b40036bcea01f7a396d2a",
    61: "f55d6f924d0e29a27eebead09e342e899615b38f",
}
actual_lineage = {item["pr"]: item["merge_sha"] for item in current_review["merged_lineage"]}
if actual_lineage != expected_lineage:
    raise SystemExit("Current Agentic review merge lineage drifted")

repair = current_review["repair_program"]
if repair["wave_a"]["A1"] != "COMPLETE_APPROVED":
    raise SystemExit("Current review lost A1 completion truth")
if repair["wave_a"]["A2"] not in {"ACTIVE", "COMPLETE_APPROVED"}:
    raise SystemExit("Current review A2 repair state is invalid")
if repair["wave_a"]["A3"] not in {"PENDING", "ACTIVE"}:
    raise SystemExit("Current review A3 repair state is invalid")
if current_review["next_engineering_after_repairs"] != "SKILL_REGISTRY":
    raise SystemExit("Current review engineering continuation drifted")

protected = current_review["protected_truth"]
if protected["live_execution_authorized"] or protected["stage8_opened"]:
    raise SystemExit("Current review inflated live execution or Stage 8")
if protected["canonical_visual_reference_count"] != 8:
    raise SystemExit("Current review visual truth count drifted")
if protected["visual_p1_status"] != "IN_PROGRESS":
    raise SystemExit("Current review falsely closed Visual P1")
if protected["real_autopilot"] != "NOT_IMPLEMENTED":
    raise SystemExit("Current review falsely implemented real Autopilot")
if protected["model_provider_calls"] != "DISCONNECTED":
    raise SystemExit("Current review falsely connected model providers")

if agentic_post["approval_id"] != "MRTKZ-AGENTIC-OS-INTEGRATION-POST-2026-10-21":
    raise SystemExit("Normalized Agentic post-review approval id drifted")
if agentic_post["approved_revision"] != "02a92f1e90fe3d36b51880c1cbd8d7cc22b3be0a":
    raise SystemExit("Normalized Agentic post-review approved revision drifted")
if agentic_post["merge_commit_sha"] != "91aa5604fea04d6ddb9cc89769e5afa139e817d6":
    raise SystemExit("Normalized Agentic post-review merge revision drifted")
if agentic_post["normalized_from"] != {
    "source": "PR_COMMENT",
    "pr": 56,
    "comment_id": 6303028014,
    "created_at": "2026-10-20T22:17:58Z",
    "historical_decision_changed": False,
}:
    raise SystemExit("Normalized Agentic post-review provenance drifted")
expected_runs = {
    "Company Stage 0": 39506822281,
    "CodeQL": 39506822402,
    "Command Center Reference UI": 39506822268,
}
actual_runs = {item["workflow"]: item["run_id"] for item in agentic_post["exact_head_evidence"]}
if actual_runs != expected_runs:
    raise SystemExit("Normalized Agentic post-review CI evidence drifted")
if not agentic_post["adoption_authorized"] or not agentic_post["merge_authorized"]:
    raise SystemExit("Normalized Agentic post-review lost its original approval")
if agentic_post["live_execution_authorized"] or agentic_post["stage8_opened"]:
    raise SystemExit("Normalized Agentic post-review inflated authority")

if a2_pre["decision"] != "APPROVE_TO_IMPLEMENT":
    raise SystemExit("A2 metadata reconciliation lacks Murtakaz pre-approval")
if a2_pre["canonical_base"]["sha"] != "f55d6f924d0e29a27eebead09e342e899615b38f":
    raise SystemExit("A2 pre-approval baseline drifted")
if a2_pre["live_execution_authorized"] or a2_pre["stage8_opened"]:
    raise SystemExit("A2 pre-approval inflated authority")
if a2_pre["final_adoption_granted"] or a2_pre["merge_authorized"]:
    raise SystemExit("A2 pre-approval may not pre-authorize adoption/merge")

if a2_change["pre_approval_receipt"] != (
    "state/command-center/project-governance/approvals/"
    "2026-10-21-repair-a2-governance-metadata-pre.json"
):
    raise SystemExit("A2 Change Envelope is not bound to its pre-approval")
if a2_change["unplanned_scope_policy"] != "RETURN_TICKET_OR_NEW_CHANGE_ENVELOPE":
    raise SystemExit("A2 scope-growth policy drifted")
if a2_capsule["job_or_change_id"] != a2_change["change_id"] or not a2_capsule["immutable"]:
    raise SystemExit("A2 bootstrap Context Capsule binding drifted")

if stage_map["delivery"]["authoritative_current_stage"] != "STAGE_7":
    raise SystemExit("Roadmap reconciliation must not change the authoritative delivery stage")
stage8 = next(item for item in stage_map["delivery"]["stages"] if item["id"] == "STAGE_8")
if stage8["status"] != "NOT_OPENED":
    raise SystemExit("A2 may not open Stage 8")

required_roadmap_markers = (
    "Last reconciled: 2026-10-21",
    "Current authoritative delivery stage at this reconciliation: `STAGE_7`.",
    "Status: APPROVED_BY_AL_MURTAKAZ / MERGED / IMPLEMENTATION SLICES 1–5 COMPLETE",
    "**COMPLETE** — Anti-Drift governance + Context/Change contracts.",
    "**COMPLETE** — Context Resolver and Context Capsule compiler.",
    "**COMPLETE** — Logical Murtakaz Gateway facade + bounded application-service interfaces.",
    "**COMPLETE** — Multi-stage Routing Coordinator.",
    "**COMPLETE** — Capability Registry + Model Broker.",
    "**PENDING AFTER REPAIR CLOSURE** — Skill Registry.",
    "**A1 Context & Baseline Repair — COMPLETE / APPROVED_BY_AL_MURTAKAZ**",
    "**A2 Governance Metadata Reconciliation — ACTIVE**",
    "**A3 Truth Lock + Murtakaz Closure — PENDING**",
)
for marker in required_roadmap_markers:
    if marker not in roadmap:
        raise SystemExit(f"Roadmap reconciliation marker missing: {marker}")

if "POST-REVIEW REQUIRED" in roadmap:
    raise SystemExit("Roadmap still advertises stale Agentic post-review-required state")

if a2_post is not None:
    if a2_post.get("decision") != "APPROVED_BY_AL_MURTAKAZ":
        raise SystemExit("A2 post-review receipt exists with a non-approved decision")
    if not a2_post["adoption_authorized"] or not a2_post["merge_authorized"]:
        raise SystemExit("A2 post-review does not authorize adoption/merge")
    if a2_post["live_execution_authorized"] or a2_post["stage8_opened"]:
        raise SystemExit("A2 post-review inflated runtime authority")

print("Al-Murtakaz governance metadata reconciliation validation: PASS")
