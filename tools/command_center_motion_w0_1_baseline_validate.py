from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "command-center"
PROJECT = STATE / "project-governance"
INVENTORY = STATE / "motion-implementation-inventory-w0-1.json"
ROADMAP = STATE / "motion-remediation-master-roadmap.json"
TICKET = PROJECT / "return-tickets" / "CC-MOTION-RT-001-2026-10-21.json"
GATE = PROJECT / "approvals" / "2026-10-21-motion-w0-1-baseline-lock.json"
VISUAL = STATE / "living-operations-reference-manifest.json"
DOC = ROOT / "docs" / "operations" / "command-center" / "living-operations" / "31_MOTION_IMPLEMENTATION_INVENTORY_W0_1_2026-10-21.md"

AUDITED_HEAD = "9285da24be6bee97564f7f47cbcaf7dee1ad3989"
SIGNATURES = {
    "ROLE_ACTIVATION",
    "ARTIFACT_HANDOFF_RETURN",
    "OWNER_DECISION_FOCUS",
    "RECOVERY",
    "FORK_BRANCH",
    "VERIFIED_COMPLETION_WORK_RECEIPT",
}


def load(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing W0.1 baseline artifact: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


for required in (INVENTORY, ROADMAP, TICKET, GATE, VISUAL, DOC):
    if not required.exists():
        raise SystemExit(f"missing W0.1 baseline artifact: {required.relative_to(ROOT)}")

inventory = load(INVENTORY)
roadmap = load(ROADMAP)
ticket = load(TICKET)
gate = load(GATE)
visual = load(VISUAL)

if inventory["status"] != "MOTION_RETURN_BASELINE_LOCK" or inventory["phase"] != "W0.1":
    raise SystemExit("W0.1 baseline lock status drifted")
if inventory["audited_implementation_head"] != AUDITED_HEAD:
    raise SystemExit("W0.1 audited implementation baseline drifted")
if inventory["pull_request"] != 72 or inventory["pull_request_merge_allowed"]:
    raise SystemExit("W0.1 must keep PR #72 non-mergeable")
if inventory["owner_rejection_retained"] is not True:
    raise SystemExit("W0.1 lost the owner rejection")
if inventory["w0_2_started"] is not False:
    raise SystemExit("W0.2 was marked started inside the W0.1 baseline artifact")

items = inventory["signature_motion_inventory"]
if {item["family"] for item in items} != SIGNATURES or len(items) != 6:
    raise SystemExit("W0.1 signature motion inventory is incomplete")
allowed = {"IMPLEMENTED", "PARTIAL", "MISSING", "SPEC_ONLY"}
if any(item["classification"] not in allowed for item in items):
    raise SystemExit("W0.1 signature classification is invalid")
if any(item["classification"] == "IMPLEMENTED" for item in items):
    raise SystemExit("W0.1 baseline falsely claims a complete signature motion family")

evidence = inventory["evidence_baseline"]
if evidence["gate_result"] != "FAIL":
    raise SystemExit("W0.1 must preserve failed owner-visible evidence truth")
if evidence["full_motion_known_metrics"]["changed_frames"] != 52:
    raise SystemExit("W0.1 changed-frame baseline drifted")
if evidence["full_motion_known_metrics"]["unchanged_acceptance_threshold_changed_frames"] != 60:
    raise SystemExit("W0.1 threshold anti-gaming lock drifted")

if ticket["status"] != "OPEN" or ticket["close_condition"] != "MOTION_SYSTEM_LOCKED":
    raise SystemExit("W0.1 may not close the motion Return Ticket")
if ticket["evidence"]["latest_head"] != AUDITED_HEAD:
    raise SystemExit("Return Ticket latest failed exact-head evidence is stale")
if ticket["evidence"]["latest_gate_result"] != "FAIL":
    raise SystemExit("Return Ticket must preserve the failed evidence gate")

position = roadmap["current_position"]
if position["wave"] != "W0" or position["phase"] != "W0.1":
    raise SystemExit("Roadmap advanced before W0.1 validation")
if position["phase_status"] != "MOTION_RETURN_BASELINE_LOCK":
    raise SystemExit("Roadmap does not record W0.1 baseline lock")
if position["next_phase_started"] is not False:
    raise SystemExit("W0.2 started before W0.1 validation")
if position["pr_merge_allowed"]:
    raise SystemExit("W0.1 may not authorize merge")

if gate["gate"] != "MOTION_RETURN_BASELINE_LOCK" or gate["decision"] != "APPROVED_BY_AL_MURTAKAZ":
    raise SystemExit("W0.1 Murtakaz gate receipt missing")
if gate["merge_authorized"] or gate["owner_visual_motion_acceptance"]:
    raise SystemExit("W0.1 receipt inflated acceptance or merge authority")
if gate["return_ticket_close_authorized"]:
    raise SystemExit("W0.1 receipt may not close the Return Ticket")

truth = inventory["protected_truth"]
if (
    truth["authoritative_stage"] != "STAGE_7"
    or truth["stage8_opened"]
    or truth["runtime_authority"]
    or truth["live_execution_authorized"]
    or not truth["visual_identity_locked"]
):
    raise SystemExit("W0.1 protected truth drifted")

inv_refs = inventory["visual_baseline"]["references"]
manifest_refs = visual["references"]
if len(inv_refs) != 8 or len(manifest_refs) != 8:
    raise SystemExit("W0.1 visual baseline must contain exactly eight references")
manifest_by_role = {item["role"]: item for item in manifest_refs}
for item in inv_refs:
    canonical = manifest_by_role.get(item["role"])
    if canonical is None:
        raise SystemExit(f"missing canonical visual role: {item['role']}")
    if canonical["path"] != item["path"] or canonical["sha256"] != item["sha256"]:
        raise SystemExit(f"visual baseline digest/path drift: {item['role']}")

doc = DOC.read_text(encoding="utf-8")
for marker in (
    "MOTION_RETURN_BASELINE_LOCK",
    "No signature family qualifies as fully **IMPLEMENTED**",
    "W0.2 status at this document: **NOT STARTED**",
    "The acceptance floor stays 60 changed frames",
):
    if marker not in doc:
        raise SystemExit(f"W0.1 human inventory drifted: {marker}")

print("Motion W0.1 baseline validation: PASS (truth reset + visual baseline + implementation inventory locked)")
