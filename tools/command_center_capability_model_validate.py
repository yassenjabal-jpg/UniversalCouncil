from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "command-center"
PROJECT = STATE / "project-governance"

REGISTRY = STATE / "capability-registry.json"
MODEL_POLICY = STATE / "model-broker-policy.json"
MODEL_STATE = STATE / "capability-model-state.json"
AGENTIC = PROJECT / "agentic-os-policy.json"
GATEWAY_POLICY = STATE / "gateway-routing-policy.json"
GATEWAY_STATE = STATE / "gateway-routing-state.json"
PRE = PROJECT / "approvals" / "2026-10-21-capability-model-broker-pre.json"
POST = PROJECT / "approvals" / "2026-10-21-capability-model-broker-post.json"
CHANGE = PROJECT / "changes" / "2026-10-21-capability-model-broker.json"
CAPSULE = PROJECT / "context-capsules" / "2026-10-21-capability-model-broker.json"

ALLOWED_HEALTH = {"HEALTHY", "DEGRADED", "STALE", "IN_TEST", "UNAVAILABLE", "BLOCKED"}
ALLOWED_EFFECT = {"READ", "WRITE", "EXECUTE"}
ALLOWED_AUTH = {"INTERNAL", "CONNECTED", "NOT_CONNECTED", "OWNER_GATED", "BLOCKED"}
FORBIDDEN_SECRET_KEYS = {
    "password",
    "secret",
    "token",
    "api_key",
    "apikey",
    "access_token",
    "refresh_token",
    "private_key",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def scan_secret_keys(value: object, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.casefold() in FORBIDDEN_SECRET_KEYS:
                raise SystemExit(f"Sensitive field is forbidden in capability/model policy: {path}.{key}")
            scan_secret_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            scan_secret_keys(child, f"{path}[{index}]")


for required in (
    REGISTRY,
    MODEL_POLICY,
    MODEL_STATE,
    AGENTIC,
    GATEWAY_POLICY,
    GATEWAY_STATE,
    PRE,
    CHANGE,
    CAPSULE,
):
    if not required.exists():
        raise SystemExit(f"missing capability/model artifact: {required.relative_to(ROOT)}")

registry = load(REGISTRY)
model_policy = load(MODEL_POLICY)
state = load(MODEL_STATE)
agentic = load(AGENTIC)
gateway_policy = load(GATEWAY_POLICY)
gateway_state = load(GATEWAY_STATE)
pre = load(PRE)
post = load(POST) if POST.exists() else None
change = load(CHANGE)
capsule = load(CAPSULE)

scan_secret_keys(registry)
scan_secret_keys(model_policy)

if registry["schema_version"] != "1.0":
    raise SystemExit("Capability Registry schema drifted")
if registry["source_type"] != "project_local_repository_projection":
    raise SystemExit("Capability Registry source type drifted")
if registry["registry_id"] != "murtakaz-capability-registry":
    raise SystemExit("Capability Registry id drifted")
if registry["status"] != "READ_ONLY_OPERATION_TRUTH":
    raise SystemExit("Capability Registry must remain read-only operation truth")
if "health" in registry or "provider_health" in registry:
    raise SystemExit("Provider-level aggregate health is forbidden")

capabilities = registry["capabilities"]
if not capabilities:
    raise SystemExit("Capability Registry may not be empty")

ids = [item["id"] for item in capabilities]
if len(ids) != len(set(ids)):
    raise SystemExit("Capability ids must be unique")

tuples = [(item["operation"], item["provider_id"], item["environment_host"]) for item in capabilities]
if len(tuples) != len(set(tuples)):
    raise SystemExit("Capability operation/provider/host tuples must be unique")

for item in capabilities:
    if not item["operation"] or not item["provider_id"] or not item["environment_host"]:
        raise SystemExit(f"Capability operation/provider/host is incomplete: {item.get('id')}")
    if item["health"] not in ALLOWED_HEALTH:
        raise SystemExit(f"Unsupported capability health: {item['health']}")
    if item["effect"] not in ALLOWED_EFFECT:
        raise SystemExit(f"Unsupported capability effect: {item['effect']}")
    if item["authentication_state"] not in ALLOWED_AUTH:
        raise SystemExit(f"Unsupported capability authentication state: {item['authentication_state']}")
    if item["ttl_seconds"] <= 0 or item["ttl_seconds"] > 2_592_000:
        raise SystemExit(f"Capability TTL is invalid: {item['id']}")
    if item["health"] in {"BLOCKED", "UNAVAILABLE"} and not item["failure_reason"]:
        raise SystemExit(f"Blocked/unavailable capability lacks failure reason: {item['id']}")

by_id = {item["id"]: item for item in capabilities}
model_select = by_id.get("model-select-local")
model_invoke = by_id.get("model-invoke-external")
if not model_select or not model_invoke:
    raise SystemExit("Required model capability entries are missing")
if state["status"] == "IMPLEMENTED_VALIDATION_PENDING":
    if model_select["health"] != "IN_TEST":
        raise SystemExit("model.select must remain IN_TEST until exact-head validation and post-review")
elif state["status"] == "APPROVED_BY_AL_MURTAKAZ":
    if model_select["health"] != "HEALTHY":
        raise SystemExit("Approved model.select capability must be HEALTHY")
else:
    raise SystemExit("Unexpected Capability/Model state status")

if model_invoke["health"] != "BLOCKED":
    raise SystemExit("Production model.invoke must remain BLOCKED while providers are disconnected")
if model_invoke["authentication_state"] != "NOT_CONNECTED":
    raise SystemExit("Production model.invoke must remain NOT_CONNECTED")
if model_invoke["fallback_eligible"]:
    raise SystemExit("Disconnected model.invoke capability cannot be fallback eligible")

if model_policy["schema_version"] != "1.0":
    raise SystemExit("Model Broker policy schema drifted")
if model_policy["source_type"] != "project_local_repository_projection":
    raise SystemExit("Model Broker policy source type drifted")
if model_policy["policy_id"] != "murtakaz-model-broker":
    raise SystemExit("Model Broker policy id drifted")
if model_policy["status"] != "SELECTION_ONLY":
    raise SystemExit("Model Broker must remain selection-only")
if not model_policy["owner_controlled"]:
    raise SystemExit("Model Broker selection must remain Owner-controlled")
if model_policy["silent_fallback_allowed"]:
    raise SystemExit("Silent model fallback is forbidden")
if model_policy["provider_calls_connected"]:
    raise SystemExit("Production model provider calls must remain disconnected in this slice")
if model_policy["selection_precedence"] != [
    "TASK_OVERRIDE",
    "ROLE_OVERRIDE",
    "PROJECT_DEFAULT",
    "GLOBAL_DEFAULT",
]:
    raise SystemExit("Model selection precedence drifted")
if model_policy["allowed_fallback_modes"] != ["Disabled", "ExplicitAllowlist"]:
    raise SystemExit("Model fallback modes drifted")

for ordered_key in ("quality_order", "cost_order", "privacy_order"):
    values = model_policy[ordered_key]
    if not values or len(values) != len(set(values)):
        raise SystemExit(f"Model Broker {ordered_key} must be explicit and unique")

for model in model_policy["models"]:
    if model["provider_connected"]:
        raise SystemExit("No production model may claim connected provider while provider calls are disconnected")

agentic_model = agentic["orchestration_services"]["model_broker"]
if agentic_model["selection_precedence"] != model_policy["selection_precedence"]:
    raise SystemExit("Model Broker precedence drifted from Agentic OS policy")
if agentic_model["silent_fallback_allowed"]:
    raise SystemExit("Agentic OS silent fallback prohibition was weakened")
if not agentic_model["owner_controlled"]:
    raise SystemExit("Agentic OS Owner model control was weakened")
for required_input in (
    "capability",
    "context",
    "latency",
    "cost",
    "quality",
    "availability",
    "privacy",
    "fallback_policy",
):
    if required_input not in agentic_model["required_inputs"]:
        raise SystemExit(f"Agentic Model Broker input missing: {required_input}")

if gateway_policy["future_dependencies"] != {
    "skill_registry": "NOT_IMPLEMENTED",
    "model_broker": "IMPLEMENTED_SELECTION_ONLY",
    "capability_registry": "IMPLEMENTED_READ_ONLY",
    "job_engine": "NOT_IMPLEMENTED",
}:
    raise SystemExit("Gateway dependency activation drifted")

if gateway_state["status"] not in {"MURTAKAZ_REVIEW_REQUIRED", "APPROVED_BY_AL_MURTAKAZ"}:
    raise SystemExit("Gateway state must be reopened or approved for the model/capability extension")
if not gateway_state["laws"]["model_selection_owner_controlled"]:
    raise SystemExit("Gateway lost Owner-controlled model selection")
if gateway_state["laws"]["silent_model_fallback"]:
    raise SystemExit("Gateway enabled silent model fallback")
if gateway_state["laws"]["provider_invocation_authorized"]:
    raise SystemExit("Gateway may not authorize provider invocation")
if gateway_state["laws"]["execution_authorized"]:
    raise SystemExit("Gateway may not grant execution authority")

if pre["decision"] != "APPROVE_TO_IMPLEMENT":
    raise SystemExit("Capability/Model slice lacks Murtakaz pre-approval")
if pre["canonical_base"]["sha"] != state["canonical_base"]:
    raise SystemExit("Capability/Model state baseline differs from pre-approval")
if pre["provider_calls_authorized"] or pre["live_execution_authorized"] or pre["stage8_opened"]:
    raise SystemExit("Capability/Model pre-approval inflated runtime authority")
if pre["final_adoption_granted"] or pre["merge_authorized"]:
    raise SystemExit("Capability/Model pre-approval may not pre-authorize adoption/merge")

if change["pre_approval_receipt"] != (
    "state/command-center/project-governance/approvals/2026-10-21-capability-model-broker-pre.json"
):
    raise SystemExit("Capability/Model Change Envelope is not bound to its pre-approval")
if change["base_revision"]["sha"] != state["canonical_base"]:
    raise SystemExit("Capability/Model Change Envelope baseline drifted")
if change["unplanned_scope_policy"] != "RETURN_TICKET_OR_NEW_CHANGE_ENVELOPE":
    raise SystemExit("Capability/Model Change Envelope scope-growth rule drifted")

if capsule["job_or_change_id"] != change["change_id"]:
    raise SystemExit("Capability/Model Context Capsule is not bound to the active change")
if capsule["source_revision"]["sha"] != state["canonical_base"]:
    raise SystemExit("Capability/Model Context Capsule baseline drifted")
if not capsule["immutable"]:
    raise SystemExit("Capability/Model Context Capsule must remain immutable")

laws = state["laws"]
for flag in (
    "operation_scoped_health",
    "provider_level_green_forbidden",
    "freshness_ttl_enforced",
    "stale_capability_not_healthy",
    "task_role_project_global_precedence",
    "owner_controlled_selection",
    "role_is_not_model",
    "explicit_fallback_allowlist_required",
    "fallback_requires_capability_eligibility",
    "minimum_context_window_enforced",
    "latency_constraint_enforced",
    "quality_floor_enforced",
    "cost_ceiling_enforced",
    "privacy_constraint_enforced",
):
    if laws.get(flag) is not True:
        raise SystemExit(f"Capability/Model truth law disabled: {flag}")

for flag in (
    "silent_fallback",
    "provider_invocation_authorized",
    "execution_authority_granted",
):
    if laws.get(flag) is not False:
        raise SystemExit(f"Capability/Model forbidden authority enabled: {flag}")

if state["components"]["model_provider_calls"] != "DISCONNECTED":
    raise SystemExit("Model provider calls must remain disconnected")
if state["components"]["active_capability_probes"] != "NOT_IMPLEMENTED":
    raise SystemExit("Active capability probes are out of scope")

if state["status"] == "APPROVED_BY_AL_MURTAKAZ":
    if post is None or post.get("decision") != "APPROVED_BY_AL_MURTAKAZ":
        raise SystemExit("Capability/Model state claims approval without post-review")
    if not post["adoption_authorized"] or not post["merge_authorized"]:
        raise SystemExit("Capability/Model post-review did not authorize adoption/merge")
    if post["provider_calls_authorized"] or post["live_execution_authorized"] or post["stage8_opened"]:
        raise SystemExit("Capability/Model post-review inflated runtime authority")

broker_source = (ROOT / "apps" / "UniversalCouncil.CommandCenter.Application" / "ModelBroker.cs").read_text(
    encoding="utf-8"
)
registry_source = (
    ROOT / "apps" / "UniversalCouncil.CommandCenter.Application" / "CapabilityRegistryService.cs"
).read_text(encoding="utf-8")
host_source = (ROOT / "apps" / "UniversalCouncil.CommandCenter.Host" / "CommandCenterComposition.cs").read_text(
    encoding="utf-8"
)
wpf_project = (ROOT / "apps" / "UniversalCouncil.CommandCenter" / "UniversalCouncil.CommandCenter.csproj").read_text(
    encoding="utf-8"
)

for forbidden in ("HttpClient", "SendAsync(", "PostAsync(", "GetAsync(", "InvokeProvider", "ApiKey", "Bearer "):
    if forbidden in broker_source:
        raise SystemExit(f"Model Broker contains forbidden provider-invocation/secret surface: {forbidden}")

if "IExecutionFabric" in broker_source or "ExecutionFabricService" in broker_source:
    raise SystemExit("Model Broker may not call Execution Fabric")
if "ICapabilityRegistry CapabilityRegistry" not in host_source:
    raise SystemExit("Capability Registry is not exposed through Host composition")
if "IModelBroker ModelBroker" not in host_source:
    raise SystemExit("Model Broker is not exposed through Host composition")
if "capability-registry.json" not in wpf_project:
    raise SystemExit("Windows package does not include Capability Registry")
if "model-broker-policy.json" not in wpf_project:
    raise SystemExit("Windows package does not include Model Broker policy")
if "utcNow" not in registry_source or "TtlSeconds" not in registry_source:
    raise SystemExit("Capability Registry freshness enforcement is missing")
if "FallbackEligible" not in broker_source:
    raise SystemExit("Model Broker does not enforce fallback capability eligibility")
if "MinimumContextWindow" not in broker_source:
    raise SystemExit("Model Broker does not enforce context-window requirements")
if "AllowedLatencyCosts" not in broker_source:
    raise SystemExit("Model Broker does not enforce latency constraints")

print("Al-Murtakaz Capability Registry/Model Broker validation: PASS")
