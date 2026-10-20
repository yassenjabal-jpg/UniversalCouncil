from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "command-center"
PROJECT = STATE / "project-governance"

UX_IMPACT = STATE / "living-operations-agentic-ux-impact.json"
UX_STATE = STATE / "living-operations-ux-state-contract.json"
REFERENCE_MANIFEST = STATE / "living-operations-reference-manifest.json"
OBJECT_INVENTORY = STATE / "living-operations-reference-object-inventory.json"
AGENTIC_POLICY = PROJECT / "agentic-os-policy.json"
PRE_APPROVAL = PROJECT / "approvals" / "2026-10-21-ux-impact-state-contract-pre.json"
CHANGE = PROJECT / "changes" / "2026-10-21-ux-impact-state-contract.json"
CAPSULE = PROJECT / "context-capsules" / "2026-10-21-ux-impact-state-contract.json"
COUNCIL = PROJECT / "project-council.json"
STUDIO = PROJECT / "product-studio.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


for required in (
    UX_IMPACT,
    UX_STATE,
    REFERENCE_MANIFEST,
    OBJECT_INVENTORY,
    AGENTIC_POLICY,
    PRE_APPROVAL,
    CHANGE,
    CAPSULE,
    COUNCIL,
    STUDIO,
):
    if not required.exists():
        raise SystemExit(f"missing UX state contract artifact: {required.relative_to(ROOT)}")

impact = load(UX_IMPACT)
ux = load(UX_STATE)
manifest = load(REFERENCE_MANIFEST)
inventory = load(OBJECT_INVENTORY)
agentic = load(AGENTIC_POLICY)
pre = load(PRE_APPROVAL)
change = load(CHANGE)
capsule = load(CAPSULE)
council = load(COUNCIL)
studio = load(STUDIO)

if impact["visual_direction_changed"]:
    raise SystemExit("UX impact audit may not change the visual direction")
if ux["visual_direction_change"]:
    raise SystemExit("UX State Contract may not change the visual direction")
if impact["canonical_reference_count"] != 8:
    raise SystemExit("UX impact audit must cover exactly eight canonical references")
if len(impact["screens"]) != 8:
    raise SystemExit("UX impact audit must contain exactly eight screens")

manifest_by_role = {item["role"]: item for item in manifest["references"]}
inventory_ids = set(inventory["screens"])
impact_ids = {item["id"] for item in impact["screens"]}

if impact_ids != set(manifest_by_role):
    raise SystemExit("UX impact screen ids drifted from the canonical visual reference manifest")
if impact_ids != inventory_ids:
    raise SystemExit("UX impact screen ids drifted from the canonical object inventory")

for screen in impact["screens"]:
    reference = manifest_by_role[screen["id"]]
    if screen["reference"] != Path(reference["path"]).name:
        raise SystemExit(f"UX impact reference path drift: {screen['id']}")
    if screen["reference_sha256"] != reference["sha256"]:
        raise SystemExit(f"UX impact reference hash drift: {screen['id']}")
    if "KEEP" not in screen["decisions"]:
        raise SystemExit(f"UX audit unexpectedly replaced canonical structure: {screen['id']}")

if impact["final_verdict"] != "KEEP_VISUAL_SYSTEM_MODIFY_UX_STATE_SEMANTICS":
    raise SystemExit("UX impact verdict drifted into redesign")

agentic_states = agentic["result_model"]["states"]
ux_states = [item["id"] for item in ux["primary_states"]]
if ux_states != agentic_states:
    raise SystemExit("UX primary Job states must exactly follow the Agentic OS result model")

success_states = [item["id"] for item in ux["primary_states"] if item["success"]]
if success_states != ["SUCCEEDED"]:
    raise SystemExit("Only SUCCEEDED may be presented as success")

laws = ux["laws"]
for required_flag in (
    "unknown_never_success",
    "succeeded_requires_independent_postcondition_verification",
    "tool_success_never_directly_maps_to_succeeded",
    "stale_context_requires_new_capsule_and_replan",
    "context_conflict_fails_closed",
    "no_fake_progress_percentage",
    "no_fake_eta",
    "no_fake_connected_ready_live_state",
    "state_never_depends_on_color_alone",
    "disabled_control_requires_reason",
    "progressive_disclosure_required",
    "same_semantics_across_windows_android",
):
    if laws.get(required_flag) is not True:
        raise SystemExit(f"UX truth law disabled: {required_flag}")

complete_projection = ux["android_projection"]["COMPLETE"]
if complete_projection != ["SUCCEEDED"]:
    raise SystemExit("Android COMPLETE may map only from SUCCEEDED")

for forbidden in (
    "UNKNOWN->COMPLETE",
    "STALE_CONTEXT->GENERIC_BLOCKED_WITHOUT_EXPLANATION",
    "CONTEXT_CONFLICT->GENERIC_WAITING_OWNER_WITHOUT_EXPLANATION",
):
    if forbidden not in ux["android_projection"]["forbidden_projection"]:
        raise SystemExit(f"Android semantic anti-drift rule missing: {forbidden}")

if ux["completion"]["verified_success_hero_state"] != "SUCCEEDED":
    raise SystemExit("Verified completion hero must remain reserved for SUCCEEDED")
if not ux["completion"]["non_success_may_not_use_verified_completion_hero"]:
    raise SystemExit("Non-success results may not reuse the verified completion hero")

required_context_fields = {
    "context_freshness",
    "context_conflict",
    "source_revision",
    "context_capsule_id",
    "canonical_source_ids",
    "conflict_provenance",
    "change_of_truth_flag",
}
if set(ux["engineering_requirements_for_context_resolver"]) != required_context_fields:
    raise SystemExit("UX contract no longer defines the required Context Resolver truth surface")

if pre["decision"] != "APPROVE_TO_IMPLEMENT":
    raise SystemExit("UX state work lacks Murtakaz pre-approval")
if pre["visual_direction_change_authorized"]:
    raise SystemExit("UX pre-approval may not authorize visual direction changes")
if pre["final_adoption_granted"] or pre["merge_authorized"]:
    raise SystemExit("UX pre-approval may not pre-authorize adoption or merge")

if change["pre_approval_receipt"] != (
    "state/command-center/project-governance/approvals/"
    "2026-10-21-ux-impact-state-contract-pre.json"
):
    raise SystemExit("UX Change Envelope is not bound to its pre-approval")
if change["unplanned_scope_policy"] != "RETURN_TICKET_OR_NEW_CHANGE_ENVELOPE":
    raise SystemExit("UX Change Envelope scope policy drifted")

if capsule["job_or_change_id"] != change["change_id"]:
    raise SystemExit("UX Context Capsule is not bound to the active change")
if capsule["source_revision"] != pre["canonical_base"]:
    raise SystemExit("UX Context Capsule baseline differs from Murtakaz pre-approval")
if not capsule["immutable"]:
    raise SystemExit("UX Context Capsule must remain immutable")
if capsule["visual_binding"]["mutation_authorized"]:
    raise SystemExit("UX Context Capsule may not authorize visual reference mutation")
if capsule["visual_binding"]["generated_visual_output_authorized"]:
    raise SystemExit("UX Context Capsule may not authorize visual generation")

expected_route = {
    "cc_owner_experience",
    "cc_product_truth",
    "cc_red_team",
    "cc_cross_platform",
    "cc_durable_autopilot",
    "cc_ai_runtime",
}
if set(council["mandatory_routes"]["agentic_ux_state"]) != expected_route:
    raise SystemExit("Agentic UX state no longer routes through the required Murtakaz reviewers")

if studio["operating_model"].get("agentic_ux_rule") != (
    "KEEP_CANONICAL_VISUAL_SYSTEM_MODIFY_STATE_SEMANTICS_ONLY_UNLESS_SEPARATELY_APPROVED"
):
    raise SystemExit("Murtakaz workshop Agentic UX rule drifted")

if set(studio["council_clearance_required_for"]["agentic_ux_state_surface"]) != {
    "cc_owner_experience",
    "cc_product_truth",
    "cc_cross_platform",
}:
    raise SystemExit("Agentic UX state surface clearance drifted")

print("Al-Murtakaz Agentic UX state validation: PASS")
