from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "command-center"
PROJECT = STATE / "project-governance"

POLICY = PROJECT / "agentic-os-policy.json"
INVARIANTS = PROJECT / "architecture-invariants.json"
CAPSULE = PROJECT / "context-capsule-contract.json"
ENVELOPE = PROJECT / "change-envelope-contract.json"
APPROVAL = PROJECT / "al-murtakaz-approval-policy.json"
PRE_APPROVAL = PROJECT / "approvals" / "2026-10-21-agentic-os-integration-pre.json"
PROJECTION = PROJECT / "murtakaz-orchestration.json"
REFERENCE_MANIFEST = STATE / "living-operations-reference-manifest.json"
VISUAL_PROTOCOL = STATE / "living-operations-visual-production-protocol.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


for required in (
    POLICY,
    INVARIANTS,
    CAPSULE,
    ENVELOPE,
    APPROVAL,
    PRE_APPROVAL,
    PROJECTION,
    REFERENCE_MANIFEST,
    VISUAL_PROTOCOL,
):
    if not required.exists():
        raise SystemExit(f"missing Agentic OS contract: {required.relative_to(ROOT)}")

policy = load(POLICY)
invariants = load(INVARIANTS)
capsule = load(CAPSULE)
envelope = load(ENVELOPE)
approval = load(APPROVAL)
pre_approval = load(PRE_APPROVAL)
projection = load(PROJECTION)
reference_manifest = load(REFERENCE_MANIFEST)
visual_protocol = load(VISUAL_PROTOCOL)

if policy["status"] != "OWNER_ADOPTED_IMPLEMENTATION_GATED":
    raise SystemExit("Agentic OS policy status drifted")
if policy["identity"]["system"] != "al-murtakaz":
    raise SystemExit("Agentic OS policy is not project-local to Al-Murtakaz")

authority = policy["authority"]
if authority["execution_authority"] or authority["stage8_opened"] or authority["parent_mutation_allowed"]:
    raise SystemExit("Agentic OS policy inflated authority")
if not authority["owner_final_authority"]:
    raise SystemExit("Owner final authority must remain explicit")

gateway = policy["logical_gateway"]
if not gateway["not_a_god_object"]:
    raise SystemExit("Gateway monolith protection disabled")
if not gateway["front_door_business_logic_forbidden"]:
    raise SystemExit("Front-door business logic boundary disabled")
if not gateway["one_logical_authority_boundary"]:
    raise SystemExit("Command ingress authority split into competing paths")
if not gateway["remote_owner_transport_is_adapter"]:
    raise SystemExit("Remote Owner must remain an ingress adapter")

required_delegates = {
    "context_resolver",
    "authority_policy_service",
    "routing_coordinator",
    "skill_resolver",
    "model_broker",
    "job_service",
    "execution_fabric",
    "verification_service",
    "receipt_service",
}
if set(gateway["delegates_to"]) != required_delegates:
    raise SystemExit("Gateway service decomposition drifted")

cycle = policy["murtakaz_change_cycle"]
for required_step in (
    "MURTAKAZ_PRE_REVIEW",
    "APPROVE_TO_IMPLEMENT",
    "CONTEXT_CAPSULE",
    "TYPED_PLAN",
    "VERIFY",
    "MURTAKAZ_POST_REVIEW",
    "APPROVED_BY_AL_MURTAKAZ",
):
    if required_step not in cycle:
        raise SystemExit(f"Murtakaz change cycle missing: {required_step}")

result_model = policy["result_model"]
if not result_model["unknown_never_success"]:
    raise SystemExit("UNKNOWN may not equal success")
for state in ("STALE_CONTEXT", "CONTEXT_CONFLICT", "WAITING_FOR_APPROVAL", "SUCCEEDED"):
    if state not in result_model["states"]:
        raise SystemExit(f"Agentic result state missing: {state}")
if set(result_model["terminal"]) & set(result_model["resumable"]):
    raise SystemExit("Result state cannot be both terminal and resumable")

context_security = policy["context_security"]
for flag in (
    "all_retrieved_content_is_data_by_default",
    "retrieved_text_cannot_grant_permissions",
    "tool_output_cannot_modify_policy",
    "model_output_cannot_self_promote_to_canonical",
    "instruction_data_separation_required",
):
    if context_security.get(flag) is not True:
        raise SystemExit(f"Context security boundary disabled: {flag}")

knowledge = policy["project_knowledge"]
if knowledge["zones"] != ["SOURCE", "CANONICAL", "WORKING", "OUTPUT", "ARCHIVE"]:
    raise SystemExit("Project knowledge zones drifted")
if not knowledge["working_output_auto_promotion_forbidden"]:
    raise SystemExit("Working/output artifacts may not auto-promote to canonical")
if knowledge["conflict_policy"] != "FAIL_CLOSED":
    raise SystemExit("Canonical conflict policy must fail closed")

owner_directives = policy["owner_directives"]
if not owner_directives["typed_record_required_for_material_change"]:
    raise SystemExit("Material Owner directives require typed records")
if not owner_directives["supersedes_chain_required"]:
    raise SystemExit("Owner directive supersedes chain is required")
if not owner_directives["change_of_truth_gate_required_when_lock_or_reference_changes"]:
    raise SystemExit("Changing locked truth must pass Change-of-Truth gate")

visual = policy["visual_inheritance"]
if visual["canonical_reference_manifest"] != "state/command-center/living-operations-reference-manifest.json":
    raise SystemExit("Agentic OS policy points at a non-canonical visual manifest")
if visual["production_protocol"] != "state/command-center/living-operations-visual-production-protocol.json":
    raise SystemExit("Agentic OS policy points at a non-canonical visual protocol")
if not visual["generic_visual_capsule_may_not_weaken_existing_gate"]:
    raise SystemExit("Generic Agentic visual rules may not weaken existing visual gates")
if visual["canonical_reference_count"] != 8:
    raise SystemExit("Agentic OS visual inheritance must preserve exactly eight references")

if reference_manifest["status"] != "OWNER_ADOPTED_MURTAKAZ_ENFORCED":
    raise SystemExit("Canonical visual reference manifest is not active")
if len(reference_manifest["references"]) != 8:
    raise SystemExit("Canonical visual reference set is not eight images")
if reference_manifest["rules"].get("generated_image_parent_forbidden") is not True:
    raise SystemExit("Generated visual output quarantine weakened")
if reference_manifest["rules"].get("actual_reference_binding_receipt_required") is not True:
    raise SystemExit("Actual reference binding evidence is required")

if visual_protocol["status"] != "FAIL_CLOSED":
    raise SystemExit("Visual production protocol must fail closed")
for key in (
    "one_job_one_screen",
    "preflight_registration_required",
    "actual_reference_bytes_required",
    "generated_image_parent_forbidden",
    "reference_binding_receipt_required",
    "fail_closed_when_tool_ineligible",
):
    if visual_protocol.get(key) is not True:
        raise SystemExit(f"Visual hard gate weakened: {key}")

if invariants["status"] != "ACTIVE":
    raise SystemExit("Architecture invariants are not active")
items = invariants["invariants"]
if len(items) != 24:
    raise SystemExit("Expected exactly 24 reconciled architecture invariants")
ids = [item["id"] for item in items]
if len(ids) != len(set(ids)):
    raise SystemExit("Architecture invariant ids must be unique")
for item in items:
    for field in (
        "id",
        "rule",
        "severity",
        "applies_from",
        "change_classes",
        "enforcement",
        "implementation_state",
        "validator",
    ):
        if not item.get(field):
            raise SystemExit(f"Invariant {item.get('id')} missing applicability metadata: {field}")
if all(item["applies_from"] == "NOW" for item in items):
    raise SystemExit("Invariant applicability regressed to globally blocking all future capabilities")

if capsule["status"] != "DESIGN_CONTRACT_ACTIVE_RUNTIME_PENDING":
    raise SystemExit("Context Capsule contract status drifted")
if not capsule["immutable_per_job"]:
    raise SystemExit("Context Capsule must be immutable per job")
if capsule["conflict_result"] != "CONTEXT_CONFLICT" or capsule["stale_result"] != "STALE_CONTEXT":
    raise SystemExit("Context Capsule fail-closed results drifted")
if capsule["domain_precedence"]["visual"][0] != "EIGHT_PINNED_CANONICAL_REFERENCE_IMAGES":
    raise SystemExit("Visual Context Capsule does not prioritize canonical reference bytes")
if not capsule["visual_binding"]["new_generic_visual_rules_may_not_weaken_existing_protocol"]:
    raise SystemExit("Context Capsule may not weaken existing visual protocol")

if envelope["status"] != "DESIGN_CONTRACT_ACTIVE_PROCESS_ENFORCED":
    raise SystemExit("Change Envelope contract status drifted")
if envelope["unplanned_scope_expansion"] != "RETURN_TICKET_OR_NEW_CHANGE_ENVELOPE":
    raise SystemExit("Unplanned scope expansion policy drifted")
if not envelope["material_mutation_from_freeform_prompt_only_forbidden"]:
    raise SystemExit("Material mutation cannot start from a free-form prompt alone")
if not envelope["delta_only_default"]:
    raise SystemExit("Bounded delta must remain the implementation default")

if approval["status"] != "OWNER_DIRECTIVE_ACTIVE":
    raise SystemExit("Murtakaz mandatory approval policy is not active")
if pre_approval["decision"] != "APPROVE_TO_IMPLEMENT":
    raise SystemExit("Agentic OS integration lacks Murtakaz pre-approval")
if pre_approval["final_adoption_granted"]:
    raise SystemExit("Pre-approval cannot grant final adoption")
if pre_approval["merge_authorized"]:
    raise SystemExit("Pre-approval cannot authorize merge")

if projection["schema_version"] != "2.0":
    raise SystemExit("Murtakaz projection was not upgraded for Agentic OS")
if projection["agentic_os"]["policy_id"] != policy["policy_id"]:
    raise SystemExit("Murtakaz projection is not bound to Agentic OS policy")
if projection["agentic_os"]["invariant_policy_id"] != invariants["policy_id"]:
    raise SystemExit("Murtakaz projection is not bound to Agentic OS invariants")

if policy["execution"]["live_execution_authorized"]:
    raise SystemExit("Agentic OS integration may not authorize live execution")
if policy["cross_platform"]["android_is_authority_host"]:
    raise SystemExit("Android may not become an authority host")

print("Al-Murtakaz Agentic Work OS contract validation: PASS")
