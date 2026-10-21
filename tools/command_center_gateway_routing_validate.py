from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "command-center"
PROJECT = STATE / "project-governance"

POLICY = STATE / "gateway-routing-policy.json"
ROUTING_STATE = STATE / "gateway-routing-state.json"
AGENTIC = PROJECT / "agentic-os-policy.json"
UX = STATE / "living-operations-ux-state-contract.json"
CONTEXT_PIPELINE = STATE / "context-pipeline-state.json"
PRE = PROJECT / "approvals" / "2026-10-21-gateway-routing-pre.json"
POST = PROJECT / "approvals" / "2026-10-21-gateway-routing-post.json"
CHANGE = PROJECT / "changes" / "2026-10-21-gateway-routing.json"
CAPSULE = PROJECT / "context-capsules" / "2026-10-21-gateway-routing.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


for required in (
    POLICY,
    ROUTING_STATE,
    AGENTIC,
    UX,
    CONTEXT_PIPELINE,
    PRE,
    POST,
    CHANGE,
    CAPSULE,
):
    if not required.exists():
        raise SystemExit(f"missing Gateway/Routing artifact: {required.relative_to(ROOT)}")

policy = load(POLICY)
state = load(ROUTING_STATE)
agentic = load(AGENTIC)
ux = load(UX)
context_pipeline = load(CONTEXT_PIPELINE)
pre = load(PRE)
post = load(POST)
change = load(CHANGE)
capsule = load(CAPSULE)

if policy["schema_version"] != "1.0":
    raise SystemExit("Gateway routing policy schema drifted")
if policy["source_type"] != "project_local_repository_projection":
    raise SystemExit("Gateway routing policy source type drifted")
if policy["policy_id"] != "murtakaz-gateway-routing":
    raise SystemExit("Gateway routing policy id drifted")
if policy["status"] != "SHADOW_PLANNING_ONLY":
    raise SystemExit("Gateway routing policy may only be SHADOW_PLANNING_ONLY")
if policy["project_id"] != "universal-council-command-center":
    raise SystemExit("Gateway routing policy project id drifted")

if policy["live_dispatch_allowed"]:
    raise SystemExit("Gateway routing policy may not enable live dispatch")
if policy["free_text_intent_inference_allowed"]:
    raise SystemExit("Free-text intent inference is forbidden in this slice")
if policy["llm_route_proposal_connected"]:
    raise SystemExit("LLM route proposal may not be connected in this slice")

expected_stages = [
    "intent",
    "project_context",
    "authority_risk",
    "skill",
    "reasoning_path",
    "model",
    "execution",
    "verification",
]
if policy["stage_order"] != expected_stages:
    raise SystemExit("Gateway routing stage order drifted")

if policy["future_dependencies"] != {
    "skill_registry": "NOT_IMPLEMENTED",
    "model_broker": "IMPLEMENTED_SELECTION_ONLY",
    "capability_registry": "IMPLEMENTED_READ_ONLY",
    "job_engine": "NOT_IMPLEMENTED",
}:
    raise SystemExit("Gateway routing dependency state drifted")

execution = policy["execution_policy"]
if (
    not execution["read_only_shadow_planning_allowed"]
    or execution["write_dispatch_allowed"]
    or execution["execute_dispatch_allowed"]
    or execution["live_execution_authorized"]
    or execution["stage8_opened"]
):
    raise SystemExit("Gateway execution policy inflated capability")

if policy["verification_policy"] != {
    "read": "SOURCE_PROVENANCE_REQUIRED",
    "write": "INDEPENDENT_POSTCONDITION_REQUIRED",
    "execute": "INDEPENDENT_POSTCONDITION_REQUIRED",
}:
    raise SystemExit("Gateway verification policy drifted")

if state["status"] not in {
    "IMPLEMENTED_VALIDATION_PENDING",
    "APPROVED_BY_AL_MURTAKAZ",
}:
    raise SystemExit("Gateway routing state has an unexpected status")

laws = state["laws"]
for flag in (
    "one_logical_gateway_contract",
    "typed_intent_required",
    "approval_is_not_execution_authority",
    "role_is_not_model",
    "silent_model_selection",
    "stale_context_propagates",
    "context_conflict_propagates",
    "context_resolved_before_routing",
    "route_reason_required",
    "gateway_does_not_call_execution_fabric",
):
    expected = False if flag == "silent_model_selection" else True
    if laws.get(flag) is not expected:
        raise SystemExit(f"Gateway routing law drifted: {flag}")

if laws["free_text_intent_inference"]:
    raise SystemExit("Gateway state may not enable free-text intent inference")
if laws["execution_authorized"]:
    raise SystemExit("Gateway state may not authorize execution")
if laws["live_dispatch_allowed"]:
    raise SystemExit("Gateway state may not enable live dispatch")

if context_pipeline["status"] != "APPROVED_BY_AL_MURTAKAZ":
    raise SystemExit("Gateway must build on the approved Context pipeline")
if not context_pipeline["truth_rules"]["stale_context_blocks_compilation"]:
    raise SystemExit("Gateway foundation lost STALE_CONTEXT fail-closed behavior")
if not context_pipeline["truth_rules"]["context_conflict_blocks_compilation"]:
    raise SystemExit("Gateway foundation lost CONTEXT_CONFLICT fail-closed behavior")

if ux["status"] != "APPROVED_BY_AL_MURTAKAZ":
    raise SystemExit("Gateway must use the approved UX State Contract")
for state_id in ("WAITING_FOR_APPROVAL", "BLOCKED", "STALE_CONTEXT", "CONTEXT_CONFLICT"):
    if state_id not in {item["id"] for item in ux["primary_states"]}:
        raise SystemExit(f"Gateway projects an unknown UX state: {state_id}")

logical_gateway = agentic["logical_gateway"]
if not logical_gateway["not_a_god_object"]:
    raise SystemExit("Murtakaz Gateway boundary regressed into a God Object")
if not logical_gateway["one_logical_authority_boundary"]:
    raise SystemExit("Murtakaz Gateway lost its single logical authority boundary")
if not logical_gateway["front_door_business_logic_forbidden"]:
    raise SystemExit("Front-door business logic boundary was weakened")

if state["status"] != "APPROVED_BY_AL_MURTAKAZ":
    raise SystemExit("Gateway/Routing state is not Murtakaz-approved")
if post["decision"] != "APPROVED_BY_AL_MURTAKAZ":
    raise SystemExit("Gateway/Routing work lacks Murtakaz post-approval")
if not post["adoption_authorized"] or not post["merge_authorized"]:
    raise SystemExit("Gateway/Routing post-approval must authorize adoption and merge")
if post["live_execution_authorized"] or post["stage8_opened"]:
    raise SystemExit("Gateway/Routing post-approval may not enable live execution or Stage 8")
if (
    post["model_broker_implemented"]
    or post["skill_registry_implemented"]
    or post["capability_registry_implemented"]
    or post["job_engine_implemented"]
):
    raise SystemExit("Gateway/Routing approval fabricated later roadmap components")
if post["next_roadmap_slice_authorized"] != "CAPABILITY_REGISTRY_AND_MODEL_BROKER":
    raise SystemExit("Gateway/Routing next roadmap slice drifted")
if state.get("murtakaz_post_approval") != (
    "state/command-center/project-governance/approvals/2026-10-21-gateway-routing-post.json"
):
    raise SystemExit("Gateway/Routing state is not bound to its post-approval receipt")

if pre["decision"] != "APPROVE_TO_IMPLEMENT":
    raise SystemExit("Gateway/Routing work lacks Murtakaz pre-approval")
if pre["canonical_base"]["sha"] != state["canonical_base"]:
    raise SystemExit("Gateway routing state baseline differs from pre-approval")
if pre["live_execution_authorized"] or pre["stage8_opened"]:
    raise SystemExit("Gateway pre-approval may not enable live execution or Stage 8")
if pre["final_adoption_granted"] or pre["merge_authorized"]:
    raise SystemExit("Gateway pre-approval may not pre-authorize adoption or merge")

if change["pre_approval_receipt"] != (
    "state/command-center/project-governance/approvals/2026-10-21-gateway-routing-pre.json"
):
    raise SystemExit("Gateway Change Envelope is not bound to its pre-approval")
if change["base_revision"]["sha"] != state["canonical_base"]:
    raise SystemExit("Gateway Change Envelope baseline drifted")
if change["unplanned_scope_policy"] != "RETURN_TICKET_OR_NEW_CHANGE_ENVELOPE":
    raise SystemExit("Gateway Change Envelope scope-growth rule drifted")

if capsule["job_or_change_id"] != change["change_id"]:
    raise SystemExit("Gateway bootstrap Context Capsule is not bound to the active change")
if capsule["source_revision"]["sha"] != state["canonical_base"]:
    raise SystemExit("Gateway bootstrap Context Capsule baseline drifted")
if not capsule["immutable"]:
    raise SystemExit("Gateway bootstrap Context Capsule must remain immutable")

gateway_source = (ROOT / "apps" / "UniversalCouncil.CommandCenter.Application" / "MurtakazCommandGateway.cs").read_text(
    encoding="utf-8"
)
routing_source = (ROOT / "apps" / "UniversalCouncil.CommandCenter.Application" / "RoutingCoordinator.cs").read_text(
    encoding="utf-8"
)
host_source = (ROOT / "apps" / "UniversalCouncil.CommandCenter.Host" / "CommandCenterComposition.cs").read_text(
    encoding="utf-8"
)
wpf_project = (ROOT / "apps" / "UniversalCouncil.CommandCenter" / "UniversalCouncil.CommandCenter.csproj").read_text(
    encoding="utf-8"
)

if "IExecutionFabric" in gateway_source or "ExecutionFabricService" in gateway_source:
    raise SystemExit("Gateway may not call Execution Fabric in this slice")
if "IExecutionFabric" in routing_source or "ExecutionFabricService" in routing_source:
    raise SystemExit("Routing Coordinator may not call Execution Fabric in this slice")
if "IMurtakazCommandGateway CommandGateway" not in host_source:
    raise SystemExit("Gateway is not exposed through Host composition")
if "IRoutingCoordinator RoutingCoordinator" not in host_source:
    raise SystemExit("Routing Coordinator is not exposed through Host composition")
if "gateway-routing-policy.json" not in wpf_project:
    raise SystemExit("Windows package does not include Gateway routing policy")
if "capability-registry.json" not in wpf_project:
    raise SystemExit("Windows package does not include Capability Registry")
if "model-broker-policy.json" not in wpf_project:
    raise SystemExit("Windows package does not include Model Broker policy")

print("Al-Murtakaz Gateway/Routing validation: PASS")
