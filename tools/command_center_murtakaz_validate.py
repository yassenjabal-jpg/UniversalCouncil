from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "command-center"
PROJECT = STATE / "project-governance"
PROJECTION = PROJECT / "murtakaz-orchestration.json"
STAGE_MAP = PROJECT / "stage-phase-map.json"
APPROVAL_POLICY = PROJECT / "al-murtakaz-approval-policy.json"
VISUAL_PHASE = STATE / "living-operations-p1-visual-phase.json"
SCREEN_REVIEW = STATE / "living-operations-p1-screen-review.json"
FINAL_P1_POST = PROJECT / "approvals" / "2026-10-21-repair-b3-final-p1-acceptance-post.json"
REFERENCE_MANIFEST = STATE / "living-operations-reference-manifest.json"
VISUAL_APPROVAL = PROJECT / "approvals" / "2026-10-19-visual-direction-continuation.json"
TAILNET_POLICY = STATE / "owner-device-tailnet-policy.json"
TAILNET_PROJECTION = STATE / "owner-device-tailnet.json"
BUILDER = ROOT / "tools" / "build_command_center_murtakaz_projection.py"
AGENTIC_VALIDATOR = ROOT / "tools" / "command_center_agentic_os_validate.py"
UX_STATE_VALIDATOR = ROOT / "tools" / "command_center_ux_state_validate.py"
CONTEXT_PIPELINE_VALIDATOR = ROOT / "tools" / "command_center_context_pipeline_validate.py"
GATEWAY_ROUTING_VALIDATOR = ROOT / "tools" / "command_center_gateway_routing_validate.py"
CAPABILITY_MODEL_VALIDATOR = ROOT / "tools" / "command_center_capability_model_validate.py"
GOVERNANCE_METADATA_VALIDATOR = ROOT / "tools" / "command_center_governance_metadata_validate.py"
REPAIR_WAVE_A_VALIDATOR = ROOT / "tools" / "command_center_repair_wave_a_validate.py"
REPAIR_B1_NATIVE_VALIDATOR = ROOT / "tools" / "command_center_repair_b1_native_validate.py"
REPAIR_B2_CONSISTENCY_VALIDATOR = ROOT / "tools" / "command_center_repair_b2_validate.py"
REPAIR_B3_FINAL_VALIDATOR = ROOT / "tools" / "command_center_repair_b3_final_validate.py"
POST_P1_INTERACTION_MOTION_VALIDATOR = ROOT / "tools" / "command_center_post_p1_interaction_motion_validate.py"

VISUAL_DIRECTION_ROOT = ROOT / "docs" / "operations" / "command-center" / "living-operations"
VISUAL_DIRECTION_FILES = (
    VISUAL_DIRECTION_ROOT / "01_VISUAL_BIBLE.md",
    VISUAL_DIRECTION_ROOT / "15_P1_VISUAL_DIRECTION_LOCK.md",
    VISUAL_DIRECTION_ROOT / "18_REFERENCE_ONLY_VISUAL_LOCK.md",
    VISUAL_DIRECTION_ROOT / "19_REFERENCE_FIDELITY_AUDIT_AND_CONTRACT.md",
)
FORBIDDEN_VISUAL_THEME_TERMS = ("architecture", "architectural", "عمارة", "معمار")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location("murtakaz_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise SystemExit("Cannot load Murtakaz projection builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def blob_sha(relative: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{relative}"],
        cwd=ROOT,
        text=True,
    ).strip()


for required in (
    PROJECTION,
    STAGE_MAP,
    APPROVAL_POLICY,
    VISUAL_PHASE,
    SCREEN_REVIEW,
    REFERENCE_MANIFEST,
    VISUAL_APPROVAL,
    TAILNET_POLICY,
    TAILNET_PROJECTION,
    BUILDER,
    AGENTIC_VALIDATOR,
    UX_STATE_VALIDATOR,
    CONTEXT_PIPELINE_VALIDATOR,
    GATEWAY_ROUTING_VALIDATOR,
    CAPABILITY_MODEL_VALIDATOR,
    GOVERNANCE_METADATA_VALIDATOR,
    REPAIR_WAVE_A_VALIDATOR,
    REPAIR_B1_NATIVE_VALIDATOR,
    REPAIR_B2_CONSISTENCY_VALIDATOR,
    REPAIR_B3_FINAL_VALIDATOR,
    POST_P1_INTERACTION_MOTION_VALIDATOR,
):
    if not required.exists():
        raise SystemExit(f"missing Murtakaz alignment artifact: {required.relative_to(ROOT)}")

projection = load(PROJECTION)
builder = load_builder()
expected = builder.build()
if projection != expected:
    raise SystemExit("Murtakaz orchestration projection drifted; regenerate it")

if projection["source_type"] != "project_local_repository_projection":
    raise SystemExit("Murtakaz projection source type drifted")
for source in projection["source_files"]:
    if blob_sha(source["path"]) != source["blob_sha"]:
        raise SystemExit(f"Murtakaz source digest drift: {source['path']}")

authority = projection["authority"]
if (
    authority["execution_authority"]
    or authority["stage8_opened"]
    or authority["parent_mutation_allowed"]
    or not authority["owner_final_authority"]
):
    raise SystemExit("Murtakaz authority boundary drifted")

runtime = projection["runtime"]
if (
    runtime["task_state"] != "NO_LIVE_TASK"
    or runtime["active_governance_roles"]
    or runtime["active_workshop_function"] is not None
    or runtime["active_model"] is not None
    or runtime["provider_call_in_flight"]
):
    raise SystemExit("Murtakaz projection fabricated live activity")

model = projection["model_control"]
if not model["role_model_separation"] or not model["owner_controlled_selection"] or model["silent_fallback_allowed"]:
    raise SystemExit("Murtakaz model-control policy drifted")

approval = load(APPROVAL_POLICY)
if approval["status"] != "OWNER_DIRECTIVE_ACTIVE":
    raise SystemExit("Murtakaz mandatory approval policy is not active")
if approval["implicit_approval_forbidden"] is not True:
    raise SystemExit("Murtakaz implicit approval must remain forbidden")
for required_gate in (
    "implementation_requires",
    "adoption_requires",
    "completion_requires",
    "merge_requires",
    "release_requires",
    "next_phase_requires",
):
    if not approval.get(required_gate):
        raise SystemExit(f"Murtakaz approval gate missing: {required_gate}")

visual_phase = load(VISUAL_PHASE)
final_p1_post = load(FINAL_P1_POST) if FINAL_P1_POST.exists() else None
final_p1_approved = (
    final_p1_post is not None
    and final_p1_post.get("decision") == "APPROVED_BY_AL_MURTAKAZ"
    and final_p1_post.get("p1_complete") is True
)
if visual_phase["status"] not in {"IN_PROGRESS", "APPROVED_BY_AL_MURTAKAZ"}:
    raise SystemExit("P1 visual phase entered an unsupported lifecycle state")
if visual_phase["status"] == "APPROVED_BY_AL_MURTAKAZ" and not final_p1_approved:
    raise SystemExit("P1 visual phase claims final approval without the final Murtakaz receipt")
if visual_phase["exit_requires"] != "APPROVED_BY_AL_MURTAKAZ":
    raise SystemExit("P1 visual phase exit is not Murtakaz-gated")
if visual_phase["runtime_authority"] is not False or visual_phase["stage8_opened"] is not False:
    raise SystemExit("Visual phase may not grant runtime authority or open Stage 8")

screen_review = load(SCREEN_REVIEW)
allowed_screen_review_states = {
    "IN_PROGRESS",
    "B1_NATIVE_COMPLETION_REVIEW_REQUIRED",
    "B1_NATIVE_COMPLETION_APPROVED_R9_READY",
    "B2_CROSS_SCREEN_REVIEW_REQUIRED",
    "B2_CROSS_SCREEN_APPROVED_B3_READY",
    "B3_RETURNED_FOR_CHANGES_EXIT_EVIDENCE_PENDING",
    "P1_FINAL_ACCEPTED_BY_AL_MURTAKAZ",
}
if screen_review["status"] not in allowed_screen_review_states:
    raise SystemExit("P1 screen review entered an unsupported lifecycle state")
if screen_review["final_state_requires"] != "APPROVED_BY_AL_MURTAKAZ":
    raise SystemExit("P1 screen review exit is not Murtakaz-gated")
if screen_review["phase_complete"] is True and not final_p1_approved:
    raise SystemExit("P1 screen review fabricated phase completion")
if final_p1_approved and screen_review["phase_complete"] is not True:
    raise SystemExit("Final P1 receipt exists but screen review is not complete")
allowed_scoped_decisions = {
    "PENDING",
    "B1_NATIVE_COMPLETION_APPROVED",
    "B2_CROSS_SCREEN_CONSISTENCY_APPROVED",
    "B3_DESKTOP_FINAL_FIDELITY_APPROVED",
}
if any(item["murtakaz_decision"] not in allowed_scoped_decisions for item in screen_review["screens"]):
    raise SystemExit("P1 screen state claimed unsupported/final approval during scoped P1 repair")
if any(item["murtakaz_decision"] == "APPROVED_BY_AL_MURTAKAZ" for item in screen_review["screens"]):
    raise SystemExit("Scoped B1/B2 repair may not grant final per-screen P1 approval")

subprocess.run(
    [__import__("sys").executable, str(ROOT / "tools" / "command_center_visual_reference_validate.py")], check=True
)

subprocess.run([__import__("sys").executable, str(AGENTIC_VALIDATOR)], check=True)
subprocess.run([__import__("sys").executable, str(UX_STATE_VALIDATOR)], check=True)
subprocess.run([__import__("sys").executable, str(CONTEXT_PIPELINE_VALIDATOR)], check=True)
subprocess.run([__import__("sys").executable, str(GATEWAY_ROUTING_VALIDATOR)], check=True)
subprocess.run([__import__("sys").executable, str(CAPABILITY_MODEL_VALIDATOR)], check=True)
subprocess.run([__import__("sys").executable, str(GOVERNANCE_METADATA_VALIDATOR)], check=True)
subprocess.run([__import__("sys").executable, str(REPAIR_WAVE_A_VALIDATOR)], check=True)
subprocess.run([__import__("sys").executable, str(REPAIR_B1_NATIVE_VALIDATOR)], check=True)
subprocess.run([__import__("sys").executable, str(REPAIR_B2_CONSISTENCY_VALIDATOR)], check=True)
subprocess.run([__import__("sys").executable, str(REPAIR_B3_FINAL_VALIDATOR)], check=True)
subprocess.run([__import__("sys").executable, str(POST_P1_INTERACTION_MOTION_VALIDATOR)], check=True)

for visual_file in VISUAL_DIRECTION_FILES:
    text = visual_file.read_text(encoding="utf-8").casefold()
    for term in FORBIDDEN_VISUAL_THEME_TERMS:
        if term.casefold() in text:
            raise SystemExit(
                f"Rejected decorative-theme vocabulary returned to governing visual direction: {visual_file.relative_to(ROOT)}"
            )

reference_manifest = load(REFERENCE_MANIFEST)
if reference_manifest["status"] != "OWNER_ADOPTED_MURTAKAZ_ENFORCED":
    raise SystemExit("Living Operations visual reference lock is not active")
if reference_manifest["source_of_truth"] != "APPROVED_REFERENCE_IMAGES_ONLY":
    raise SystemExit("Visual source of truth drifted away from approved reference images")
if len(reference_manifest["references"]) != 8:
    raise SystemExit("Canonical visual reference set must contain exactly eight approved images")
if reference_manifest["rejected_classification"] != "REJECTED_VISUAL_DRIFT":
    raise SystemExit("Rejected visual drift classification changed")
if not reference_manifest["rules"]["reference_first"]:
    raise SystemExit("Reference-first visual rule must remain active")
if not reference_manifest["rules"]["delta_only_generation"]:
    raise SystemExit("New visual generation must remain delta-only")
if not reference_manifest["rules"].get("unapproved_decorative_theme_forbidden"):
    raise SystemExit("Unapproved decorative themes must remain forbidden")
if not reference_manifest["rules"].get("reference_observed_visual_language_only"):
    raise SystemExit("Visual language must remain restricted to observed reference properties")
if "architecture_decorative_theme_forbidden" in reference_manifest["rules"]:
    raise SystemExit("Legacy rejected-theme rule name returned to the visual manifest")

visual_approval = load(VISUAL_APPROVAL)
if visual_approval["decision"] != "APPROVE_TO_IMPLEMENT":
    raise SystemExit("Visual continuation is missing pre-change Murtakaz approval")
if visual_approval["final_adoption_granted"] is not False:
    raise SystemExit("Visual continuation receipt may not pre-approve final adoption")

stage_map = load(STAGE_MAP)
if stage_map["status"] != "CANONICAL":
    raise SystemExit("Stage/Phase map is not canonical")
if stage_map["delivery"]["authoritative_current_stage"] != "STAGE_7":
    raise SystemExit("Unexpected current delivery stage")
if not stage_map["rules"]["phase_number_is_not_stage_number"]:
    raise SystemExit("Stage/Phase ambiguity protection missing")
if stage_map["rules"]["stage8_opened"]:
    raise SystemExit("Stage 8 may not be opened by taxonomy mapping")
stage8 = next(item for item in stage_map["delivery"]["stages"] if item["id"] == "STAGE_8")
if stage8["status"] != "NOT_OPENED":
    raise SystemExit("Stage 8 taxonomy state drifted")

policy = load(TAILNET_POLICY)
tailnet = load(TAILNET_PROJECTION)
if policy["gates"]["stage7_ci_foundation_passed"] is not True:
    raise SystemExit("Stage 7 CI foundation policy must record verified baseline PASS")
if tailnet["gates"]["stage7_ci_foundation_passed"] is not True:
    raise SystemExit("Stage 7 CI foundation projection must record verified baseline PASS")

for pending_gate in (
    "yassin_host_probe_passed",
    "owner_device_enrollment_passed",
    "tailscale_private_serve_passed",
    "real_owner_phone_round_trip_passed",
    "session_revocation_round_trip_passed",
):
    if policy["gates"][pending_gate] or tailnet["gates"][pending_gate]:
        raise SystemExit(f"Real-host/device gate must remain pending: {pending_gate}")

if policy["gates"]["live_execution_authorized"] or tailnet["gates"]["live_execution_authorized"]:
    raise SystemExit("Murtakaz alignment may not authorize live execution")

print("Al-Murtakaz pre-prototype alignment validation: PASS")
