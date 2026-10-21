from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "command-center"
PROJECT = STATE / "project-governance"
PIPELINE = STATE / "motion-evidence-pipeline-w0-3.json"
GATE = PROJECT / "approvals" / "2026-10-21-motion-w0-3-evidence-pipeline-lock.json"
ROADMAP = STATE / "motion-remediation-master-roadmap.json"
RECORDER = ROOT / "apps" / "UniversalCouncil.CommandCenter.UiSmoke" / "MotionEvidence.cs"
WORKFLOW = ROOT / ".github" / "workflows" / "command-center-p1-exit-evidence.yml"
EVIDENCE_GATE = ROOT / "tools" / "command_center_p1_exit_evidence_validate.py"


def load(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing W0.3 evidence artifact: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


pipeline = load(PIPELINE)
gate = load(GATE)
roadmap = load(ROADMAP)
recorder = RECORDER.read_text(encoding="utf-8")
workflow = WORKFLOW.read_text(encoding="utf-8")
evidence_gate = EVIDENCE_GATE.read_text(encoding="utf-8")

if pipeline["status"] != "MOTION_EVIDENCE_PIPELINE_LOCK":
    raise SystemExit("W0.3 evidence pipeline is not locked")
if pipeline["owner_review_capture_fps"] != 30 or pipeline["ci_capture_fps_floor"] != 20:
    raise SystemExit("W0.3 capture rate contract drifted")

equivalence = pipeline["baseline_threshold_equivalence"]
if equivalence["baseline_full_changed_frames"] != 60:
    raise SystemExit("W0.3 baseline threshold was altered")
if equivalence["owner_full_changed_frames_required"] < 90:
    raise SystemExit("W0.3 30fps threshold became weaker than the 20fps baseline")
if equivalence["owner_longest_run_required"] < 9:
    raise SystemExit("W0.3 continuous-motion threshold became weaker")

requirements = pipeline["evidence_requirements"]
for key in (
    "actual_wpf",
    "exact_head_checkout",
    "candidate_sha_in_manifest",
    "candidate_sha_in_video_integrity",
    "full_motion",
    "reduced_motion",
    "raw_frames",
    "raw_frame_sha256",
    "encoded_video_sha256",
    "semantic_event_timestamps",
    "unedited",
):
    if requirements[key] is not True:
        raise SystemExit(f"W0.3 evidence requirement disabled: {key}")
for key in ("optical_flow", "frame_interpolation", "post_produced_animation"):
    if requirements[key] is not False:
        raise SystemExit(f"W0.3 forbidden evidence processing enabled: {key}")

for marker in (
    "private const int MotionFramesPerSecond = 30;",
    "candidate_sha = candidateSha",
    'source_surface = "ACTUAL_WPF"',
    "raw_frames_included = true",
    "semantic_event_timestamps = true",
    "occurred_at_seconds",
    "event_type = EvidenceEventType(step.Name)",
):
    if marker not in recorder:
        raise SystemExit(f"W0.3 recorder marker missing: {marker}")

if workflow.count("-framerate 30") < 2:
    raise SystemExit("W0.3 Full/Reduced videos are not both encoded at 30fps")
for marker in (
    "Verify exact candidate head",
    "candidate_sha = $env:CANDIDATE_SHA.ToLowerInvariant()",
    'source = "RAW_WPF_FRAME_SEQUENCE"',
    "frame_rate = 30",
):
    if marker not in workflow:
        raise SystemExit(f"W0.3 workflow marker missing: {marker}")

for marker in (
    "if frame_rate < 20:",
    "math.ceil(60 * fps_scale)",
    "math.ceil(6 * fps_scale)",
    "sha256(raw) != frame[",
    'manifest.get("candidate_sha"',
    'integrity.get("candidate_sha"',
):
    if marker not in evidence_gate:
        raise SystemExit(f"W0.3 evidence gate marker missing: {marker}")

anti = pipeline["anti_gaming"]
if not anti["threshold_lowering_forbidden"] or not anti["fps_increase_must_scale_frame_count_thresholds"]:
    raise SystemExit("W0.3 anti-gaming policy weakened")

truth = pipeline["protected_truth"]
if (
    truth["authoritative_stage"] != "STAGE_7"
    or truth["stage8_opened"]
    or truth["runtime_authority"]
    or truth["live_execution_authorized"]
    or not truth["visual_identity_locked"]
):
    raise SystemExit("W0.3 protected truth drifted")

if gate["decision"] != "APPROVED_BY_AL_MURTAKAZ" or gate["gate"] != "MOTION_EVIDENCE_PIPELINE_LOCK":
    raise SystemExit("W0.3 Murtakaz gate receipt missing")
if gate["merge_authorized"] or gate["owner_visual_motion_acceptance"]:
    raise SystemExit("W0.3 receipt inflated product acceptance")

position = roadmap["current_position"]
if position["wave"] != "W0" or position["phase"] != "W0.3":
    raise SystemExit("roadmap is not at W0.3")
if position["phase_status"] != "MOTION_EVIDENCE_PIPELINE_LOCK":
    raise SystemExit("roadmap does not record W0.3 pipeline lock")
if position["next_phase_started"] is not False:
    raise SystemExit("W1.1 started before W0.3 validation")

print("Motion W0.3 evidence validation: PASS (30fps exact-head raw evidence + time-normalized gates locked)")
