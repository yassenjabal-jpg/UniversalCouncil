from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROADMAP = ROOT / "state" / "command-center" / "motion-remediation-master-roadmap.json"
APPROVAL = (
    ROOT
    / "state"
    / "command-center"
    / "project-governance"
    / "approvals"
    / "2026-10-21-motion-remediation-roadmap-approval.json"
)
RETURN_TICKET = (
    ROOT / "state" / "command-center" / "project-governance" / "return-tickets" / "CC-MOTION-RT-001-2026-10-21.json"
)
DOC = (
    ROOT
    / "docs"
    / "operations"
    / "command-center"
    / "living-operations"
    / "30_MOTION_REMEDIATION_MASTER_ROADMAP_2026-10-21.md"
)


def load(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing motion roadmap artifact: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


for required in (ROADMAP, APPROVAL, RETURN_TICKET, DOC):
    if not required.exists():
        raise SystemExit(f"missing motion roadmap artifact: {required.relative_to(ROOT)}")

roadmap = load(ROADMAP)
approval = load(APPROVAL)
ticket = load(RETURN_TICKET)
doc = DOC.read_text(encoding="utf-8")

if roadmap["roadmap_id"] != "CC-MOTION-REMEDIATION-MASTER-ROADMAP-2026-10-21":
    raise SystemExit("motion roadmap identity drifted")
if roadmap["status"] != "APPROVED_BY_AL_MURTAKAZ_AS_GOVERNING_PLAN":
    raise SystemExit("motion roadmap is not the approved governing plan")

waves = roadmap["waves"]
if [wave["id"] for wave in waves] != [f"W{i}" for i in range(7)]:
    raise SystemExit("motion roadmap must preserve ordered W0..W6 waves")
if any(len(wave["phases"]) != 3 for wave in waves):
    raise SystemExit("every motion remediation wave must preserve exactly three phases")

required_gates = {
    "W0": "MOTION_EVIDENCE_PIPELINE_LOCK",
    "W1": "NAVIGATION_ACTIVATION_MOTION_ACCEPTED",
    "W2": "LIVING_WORKFLOW_MOTION_ACCEPTED",
    "W3": "SIGNATURE_MOTION_ACCEPTED",
    "W4": "MOTION_ACCESSIBILITY_PERFORMANCE_PARITY_ACCEPTED",
    "W5": "OWNER_VISIBLE_MOTION_EVIDENCE_ACCEPTED",
    "W6": "MOTION_SYSTEM_LOCKED",
}
for wave in waves:
    if wave["gate"] != required_gates[wave["id"]]:
        raise SystemExit(f"motion roadmap gate drifted for {wave['id']}")

if set(roadmap["signature_motion_families"]) != {
    "ROLE_ACTIVATION",
    "ARTIFACT_HANDOFF_RETURN",
    "OWNER_DECISION_FOCUS",
    "RECOVERY",
    "FORK_BRANCH",
    "VERIFIED_COMPLETION_WORK_RECEIPT",
}:
    raise SystemExit("signature motion family coverage drifted")

acceptance = roadmap["acceptance_model"]
if acceptance["metrics_can_approve_alone"]:
    raise SystemExit("numeric motion metrics may never approve alone")
if not acceptance["owner_visual_rejection_overrides_numeric_pass"]:
    raise SystemExit("owner-visible rejection must override numeric pass")
if not acceptance["threshold_reduction_to_rescue_candidate_forbidden"]:
    raise SystemExit("motion threshold gaming became allowed")
if not acceptance["exact_head_evidence_required"]:
    raise SystemExit("exact-head motion evidence is mandatory")

truth = roadmap["protected_truth"]
if (
    truth["authoritative_stage"] != "STAGE_7"
    or truth["stage8_opened"]
    or truth["runtime_authority"]
    or truth["live_execution_authorized"]
    or not truth["visual_identity_locked"]
):
    raise SystemExit("motion roadmap inflated authority or reopened visual identity")

position = roadmap["current_position"]
if position["wave"] != "W0" or position["pr_merge_allowed"]:
    raise SystemExit("current motion remediation position must remain W0 and non-mergeable")

if roadmap["evidence_requirements"]["owner_review_capture_fps_target"] < 30:
    raise SystemExit("owner-review motion capture target fell below 30 FPS")
if roadmap["evidence_requirements"]["ci_capture_fps_floor"] < 20:
    raise SystemExit("CI motion capture floor fell below 20 FPS")

if approval["decision"] != "APPROVED_BY_AL_MURTAKAZ_AS_GOVERNING_PLAN":
    raise SystemExit("Murtakaz roadmap approval missing")
if approval["merge_authorized"]:
    raise SystemExit("roadmap approval may not authorize merge")
if approval["roadmap_structure"]["wave_count"] != 7:
    raise SystemExit("Murtakaz roadmap approval wave count drifted")

if ticket["status"] != "OPEN" or ticket["close_condition"] != "MOTION_SYSTEM_LOCKED":
    raise SystemExit("owner-return motion ticket must remain open until final system lock")

required_doc_markers = (
    "WAVE 0 — Truth Reset + Acceptance Repair",
    "WAVE 1 — Navigation + Activation Motion",
    "WAVE 2 — Living Workflow Motion",
    "WAVE 3 — Signature UniversalCouncil Motion",
    "WAVE 4 — Reduced Motion + Performance + Platform Assurance",
    "WAVE 5 — Evidence + Anti-False-Positive Hardening",
    "WAVE 6 — Final System Lock + Integration",
    "Metrics may **not alone approve**",
    "No threshold may be lowered",
    "At rest, the product is almost still",
)
for marker in required_doc_markers:
    if marker not in doc:
        raise SystemExit(f"governing motion roadmap documentation drifted: {marker}")

print(
    "Motion remediation master roadmap validation: PASS "
    "(7 waves x 3 phases; anti-false-positive + owner visual gate enforced)"
)
