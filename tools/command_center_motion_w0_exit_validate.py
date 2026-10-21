from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "command-center"
PROJECT = STATE / "project-governance"
PIPELINE = STATE / "motion-evidence-pipeline-w0-3.json"
EXIT = PROJECT / "approvals" / "2026-10-21-motion-w0-exit-evidence-verification.json"
PRE = PROJECT / "approvals" / "2026-10-21-motion-w1-1-navigation-pre.json"
CHANGE = PROJECT / "changes" / "2026-10-21-motion-w1-1-navigation.json"
CAPSULE = PROJECT / "context-capsules" / "2026-10-21-motion-w1-1-navigation.json"
ROADMAP = STATE / "motion-remediation-master-roadmap.json"


def load(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing W0 exit / W1.1 governance artifact: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


pipeline = load(PIPELINE)
receipt = load(EXIT)
pre = load(PRE)
change = load(CHANGE)
capsule = load(CAPSULE)
roadmap = load(ROADMAP)

verification = pipeline.get("verification", {})
if pipeline.get("w0_exit_verified") is not True:
    raise SystemExit("W0 evidence pipeline exit is not verified")
if verification.get("candidate_sha") != "5bf76e46990f7a44e0f7ff733d065933174c9752":
    raise SystemExit("W0 exit evidence candidate SHA drifted")
if verification.get("wpf_job_result") != "SUCCESS" or verification.get("android_job_result") != "SUCCESS":
    raise SystemExit("W0 evidence capture/encode/upload pipeline did not pass")
if verification.get("pipeline_acceptance") != "PASS":
    raise SystemExit("W0 evidence mechanism is not accepted")
if verification.get("product_motion_acceptance") != "FAIL":
    raise SystemExit("W0 exit must preserve current product-motion failure")
full = verification["full_motion"]
if full["fps"] != 30 or full["changed_frames"] != 65 or full["required_changed_frames"] != 90:
    raise SystemExit("W0 full-motion exit metrics drifted")
if full["longest_changed_run"] != 8 or full["required_longest_run"] != 9:
    raise SystemExit("W0 continuous-motion exit metrics drifted")

if receipt["decision"] != "APPROVED_BY_AL_MURTAKAZ":
    raise SystemExit("W0 exit verification approval is missing")
if receipt["interpretation"]["evidence_mechanism"] != "PASS":
    raise SystemExit("W0 exit receipt does not approve the evidence mechanism")
if receipt["interpretation"]["product_motion"] != "FAIL":
    raise SystemExit("W0 exit receipt fabricated product motion acceptance")
if receipt["interpretation"]["owner_motion_acceptance"]:
    raise SystemExit("W0 exit receipt fabricated owner motion acceptance")
if receipt["merge_authorized"] or receipt["stage8_opened"] or receipt["return_ticket_close_authorized"]:
    raise SystemExit("W0 exit receipt inflated authority")

allowed_w1_1_progress = {
    "APPROVE_TO_IMPLEMENT",
    "IMPLEMENT",
    "VERIFY",
    "STUDIO_REVIEW",
    "MURTAKAZ_POST_REVIEW",
    "APPROVED_BY_AL_MURTAKAZ",
}
if change["current_state"] not in allowed_w1_1_progress:
    raise SystemExit("W1.1 change left the approved implementation lifecycle")
if pre["decision"] != "APPROVE_TO_IMPLEMENT" or pre["final_adoption_granted"]:
    raise SystemExit("W1.1 pre-review approval is invalid")
if capsule["status"] != "ACTIVE_FOR_IMPLEMENTATION":
    raise SystemExit("W1.1 context capsule is not active")
if (
    capsule["implementation_contract"]["reduced_motion"]
    != "no translation or scale travel; bounded crossfade/state handoff only"
):
    raise SystemExit("W1.1 Reduced Motion contract drifted")

position = roadmap["current_position"]
if position["wave"] != "W1" or position["phase"] != "W1.1":
    raise SystemExit("roadmap did not advance exactly to W1.1")
if position["phase_status"] not in allowed_w1_1_progress:
    raise SystemExit("W1.1 roadmap state left the approved implementation lifecycle")
if position["pr_merge_allowed"]:
    raise SystemExit("W1.1 may not authorize PR merge")

print("Motion W0 exit / W1.1 pre-implementation validation: PASS")
