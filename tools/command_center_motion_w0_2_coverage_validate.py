from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "command-center"
PROJECT = STATE / "project-governance"
MATRIX = STATE / "motion-storyboard-code-coverage-w0-2.json"
GATE = PROJECT / "approvals" / "2026-10-21-motion-w0-2-coverage-lock.json"
ROADMAP = STATE / "motion-remediation-master-roadmap.json"
DOC = (
    ROOT
    / "docs"
    / "operations"
    / "command-center"
    / "living-operations"
    / "32_MOTION_STORYBOARD_CODE_COVERAGE_W0_2_2026-10-21.md"
)

SIGNATURES = {
    "ROLE_ACTIVATION",
    "ARTIFACT_HANDOFF_RETURN",
    "OWNER_DECISION_FOCUS",
    "RECOVERY",
    "FORK_BRANCH",
    "VERIFIED_COMPLETION_WORK_RECEIPT",
}
REQUIRED_EVENTS = {
    "ROLE_ACTIVATED",
    "ROLE_STATE_CHANGED",
    "ARTIFACT_HANDOFF_STARTED",
    "ARTIFACT_HANDOFF_ACCEPTED",
    "ARTIFACT_RETURNED",
    "OWNER_DECISION_REQUIRED",
    "OWNER_DECISION_RECORDED",
    "AUTOPILOT_RECOVERY_STARTED",
    "CHECKPOINT_RESTORE_REQUESTED",
    "CHECKPOINT_RESTORED_VERIFIED",
    "FORK_CREATED",
    "BRANCH_SELECTED",
    "PROJECT_COMPLETED_VERIFIED",
}
REQUIRED_COLUMNS = {
    "semantic_event",
    "semantic_object",
    "screen",
    "full_motion",
    "reduced_motion",
    "code_path",
    "evidence_step",
}


def load(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing W0.2 coverage artifact: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


matrix = load(MATRIX)
gate = load(GATE)
roadmap = load(ROADMAP)
if not DOC.exists():
    raise SystemExit("missing W0.2 human coverage contract")

if matrix["status"] != "MOTION_STORYBOARD_CODE_COVERAGE_LOCK" or matrix["phase"] != "W0.2":
    raise SystemExit("W0.2 coverage contract status drifted")
if set(matrix["signature_families"]) != SIGNATURES:
    raise SystemExit("W0.2 signature family set drifted")
if set(matrix["required_columns"]) != REQUIRED_COLUMNS:
    raise SystemExit("W0.2 required coverage columns drifted")

rows = matrix["rows"]
events = {row["semantic_event"] for row in rows}
if not REQUIRED_EVENTS.issubset(events):
    raise SystemExit(f"W0.2 semantic event coverage missing: {sorted(REQUIRED_EVENTS - events)}")
if {row["signature_family"] for row in rows} != SIGNATURES:
    raise SystemExit("W0.2 does not cover every signature family")
for row in rows:
    for key in REQUIRED_COLUMNS:
        if not str(row.get(key, "")).strip():
            raise SystemExit(f"W0.2 row missing {key}: {row.get('semantic_event')}")
    if row["signature_family"] not in SIGNATURES:
        raise SystemExit("W0.2 row uses unknown signature family")

laws = matrix["laws"]
if not laws["runtime_emits_facts_client_chooses_presentation"]:
    raise SystemExit("W0.2 event/presentation boundary drifted")
if not laws["unknown_event_must_not_fabricate_motion"]:
    raise SystemExit("W0.2 unknown-event fail-closed rule drifted")
if not laws["full_and_reduced_share_semantics"]:
    raise SystemExit("W0.2 Reduced Motion semantic parity drifted")

contract = matrix["implementation_contract"]
if contract["required_router"] != "ApplyMotionEvent":
    raise SystemExit("W0.2 implementation seam drifted")
if not contract["event_backing_required"] or not contract["no_hotspot_only_signature_acceptance"]:
    raise SystemExit("W0.2 event-backed signature acceptance weakened")
if matrix["w0_3_started"] is not False:
    raise SystemExit("W0.3 was marked started inside W0.2 contract")

truth = matrix["protected_truth"]
if (
    truth["authoritative_stage"] != "STAGE_7"
    or truth["stage8_opened"]
    or truth["runtime_authority"]
    or truth["live_execution_authorized"]
    or not truth["visual_identity_locked"]
):
    raise SystemExit("W0.2 protected truth drifted")

if gate["decision"] != "APPROVED_BY_AL_MURTAKAZ":
    raise SystemExit("W0.2 Murtakaz phase receipt missing")
if gate["gate"] != "MOTION_STORYBOARD_CODE_COVERAGE_LOCK":
    raise SystemExit("W0.2 phase gate drifted")
if gate["merge_authorized"] or gate["owner_visual_motion_acceptance"]:
    raise SystemExit("W0.2 receipt inflated acceptance")

position = roadmap["current_position"]
if position["pr_merge_allowed"]:
    raise SystemExit("motion remediation may not authorize merge before W6")
if position["wave"] not in {"W0", "W1", "W2", "W3", "W4", "W5", "W6"}:
    raise SystemExit("motion remediation roadmap position is invalid")

doc = DOC.read_text(encoding="utf-8")
for marker in (
    "MOTION_STORYBOARD_CODE_COVERAGE_LOCK",
    "hotspot-only cues cannot satisfy this contract",
    "W0.3 status here: **NOT STARTED**",
):
    if marker not in doc:
        raise SystemExit(f"W0.2 human contract drifted: {marker}")

print("Motion W0.2 coverage validation: PASS (semantic event -> object -> motion -> code -> evidence locked)")
