from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "state" / "motion-platform" / "platform-contract.json"
CATALOG = ROOT / "state" / "motion-platform" / "semantic-catalog.json"
CANDIDATES = ROOT / "state" / "motion-platform" / "open-source-candidates.json"
PROFILE = ROOT / "state" / "motion-platform" / "profiles" / "command-center-reference.json"
DOCS = [
    ROOT / "docs" / "operations" / "motion-platform" / "00_MOTION_PLATFORM_CHARTER.md",
    ROOT / "docs" / "operations" / "motion-platform" / "01_MOTION_PLATFORM_ARCHITECTURE.md",
    ROOT / "docs" / "operations" / "motion-platform" / "02_COMPATIBILITY_LAB.md",
    ROOT / "docs" / "operations" / "motion-platform" / "03_STUDIO_CAPABILITY_UPGRADE.md",
    ROOT / "docs" / "operations" / "motion-platform" / "04_MOTION_PLATFORM_ROADMAP.md",
]

for path in (CONTRACT, CATALOG, CANDIDATES, PROFILE, *DOCS):
    if not path.exists():
        raise SystemExit(f"missing Motion Platform artifact: {path.relative_to(ROOT)}")

contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
candidates = json.loads(CANDIDATES.read_text(encoding="utf-8"))
profile = json.loads(PROFILE.read_text(encoding="utf-8"))

if contract["platform_id"] != "motionkit":
    raise SystemExit("Motion Platform identity drifted")
if contract["scope"] != "MULTI_PROJECT":
    raise SystemExit("Motion Platform became product-local")

truth = contract["protected_truth"]
required_false = (
    "motion_creates_operational_truth",
    "unknown_is_success",
    "fake_activity_allowed",
    "renderer_may_own_product_state",
)
for key in required_false:
    if truth[key]:
        raise SystemExit(f"Motion Platform truth boundary weakened: {key}")
if not truth["reduced_motion_semantic_parity_required"]:
    raise SystemExit("Reduced Motion semantic parity became optional")
if not truth["owner_visible_rejection_overrides_numeric_pass"]:
    raise SystemExit("numeric motion metrics may not override owner-visible failure")

purpose_set = {
    "NAVIGATION",
    "STATE",
    "FEEDBACK",
    "ROUTING",
    "HANDOFF",
    "RECOVERY",
}
if set(contract["purposes"]) != purpose_set:
    raise SystemExit("semantic motion purpose set drifted")

if contract["layers"] != [
    "SEMANTIC_CONTRACT",
    "ORCHESTRATOR",
    "CHOREOGRAPHY_TOKENS",
    "PRODUCT_MOTION_PROFILE",
    "RENDERER_ADAPTER",
    "EVIDENCE_QA",
]:
    raise SystemExit("Motion Platform architecture layer order drifted")

allowed_candidate_states = {"LAB_ONLY", "REFERENCE_ONLY"}
for group in ("candidate_renderers", "architecture_references", "qa_candidates"):
    for name, status in contract[group].items():
        if status not in allowed_candidate_states:
            raise SystemExit(f"candidate {name} bypassed the Compatibility Lab: {status}")

adoption = contract["adoption_policy"]
if adoption["single_renderer_required"]:
    raise SystemExit("Motion Platform incorrectly requires a single renderer")
if adoption["direct_product_dependency_on_renderer_allowed"]:
    raise SystemExit("products may not bypass MotionKit adapters")
for key in (
    "adapter_isolation_required",
    "license_review_required",
    "performance_evidence_required",
    "reduced_motion_evidence_required",
    "interruption_evidence_required",
    "weak_hardware_fallback_required",
):
    if not adoption[key]:
        raise SystemExit(f"Motion Platform adoption guard disabled: {key}")

authority = contract["authority"]
if not authority["architecture_research_authorized"]:
    raise SystemExit("Motion Platform architecture research unexpectedly disabled")
for key in (
    "production_renderer_adoption_authorized",
    "command_center_refactor_authorized",
    "pr72_merge_authorized",
    "stage8_opened",
    "runtime_authority_expanded",
):
    if authority[key]:
        raise SystemExit(f"foundation draft inflated authority: {key}")

roadmap = contract["roadmap"]
if roadmap["ordered_waves"] != [f"MP{i}" for i in range(7)]:
    raise SystemExit("Motion Platform roadmap must preserve MP0..MP6")
if roadmap["current_wave"] != "MP0":
    raise SystemExit("foundation branch advanced beyond MP0 without evidence")
if roadmap["final_gate"] != "MOTION_PLATFORM_GENERAL_ADOPTION_APPROVED":
    raise SystemExit("Motion Platform final adoption gate drifted")

# Semantic catalog invariants.
if catalog["catalog_id"] != "motionkit-semantic-catalog":
    raise SystemExit("semantic catalog identity drifted")
events = catalog["events"]
event_ids = [event["id"] for event in events]
if len(event_ids) != len(set(event_ids)):
    raise SystemExit("semantic catalog contains duplicate event IDs")
required_events = {
    "ROLE_ACTIVATED",
    "ROUTE_TRANSFER",
    "WAITING_OWNER",
    "BLOCKED",
    "VERIFIED_COMPLETE",
    "EXPAND",
    "COLLAPSE",
    "SELECT",
    "INSPECT",
    "HANDOFF",
    "RETURN",
    "RECOVERY_FOCUS",
    "FORK",
}
if set(event_ids) != required_events:
    raise SystemExit("semantic event coverage drifted")
allowed_interruptions = set(contract["interruption_modes"])
for event in events:
    if not event["purpose"] or not set(event["purpose"]).issubset(purpose_set):
        raise SystemExit(f"invalid purpose on semantic event: {event['id']}")
    if event["default_interruption"] not in allowed_interruptions:
        raise SystemExit(f"invalid interruption policy on semantic event: {event['id']}")
    if not event["truth_requirement"]:
        raise SystemExit(f"semantic event lacks truth requirement: {event['id']}")
    if not event["reduced_motion"]:
        raise SystemExit(f"semantic event lacks Reduced Motion equivalent: {event['id']}")
    if not event["quiet_when_false"]:
        raise SystemExit(f"semantic event may animate without backing truth: {event['id']}")

# Open-source registry is research only.
allowed_registry_states = {
    "LAB_ONLY",
    "REFERENCE_ONLY",
    "QA_CANDIDATE",
    "DEFERRED_REFERENCE",
}
seen_candidates: set[str] = set()
for item in candidates["candidates"]:
    if item["id"] in seen_candidates:
        raise SystemExit(f"duplicate open-source candidate: {item['id']}")
    seen_candidates.add(item["id"])
    if item["status"] not in allowed_registry_states:
        raise SystemExit(f"open-source candidate bypassed lab governance: {item['id']}")
    if not item["repository"] or not item["license"] or not item["source"]:
        raise SystemExit(f"open-source candidate metadata incomplete: {item['id']}")
if {"RIVE", "LOTTIE_ANDROID", "SKIASHARP", "FLAUI", "BENCHMARKDOTNET"} - seen_candidates:
    raise SystemExit("core Motion Platform research candidates missing")

# Reference profile cannot silently bind production renderers or alter identity.
if profile["profile_id"] != "command-center-reference":
    raise SystemExit("Command Center Motion Profile identity drifted")
if not profile["inherits_platform_semantics"]:
    raise SystemExit("Command Center Motion Profile detached from platform semantics")
if profile["visual_identity_source"] != "LOCKED_COMMAND_CENTER_VISUAL_SYSTEM":
    raise SystemExit("Command Center visual identity source drifted")
if profile["personality"]["at_rest"] != "QUIET":
    raise SystemExit("Command Center lost quiet-at-rest motion law")
if profile["personality"]["decorative_loops"] != "FORBIDDEN":
    raise SystemExit("decorative loops became allowed")
reduced = profile["reduced_motion"]
for key in ("travel_removed", "pulse_removed", "spring_removed", "state_labels_preserved", "focus_preserved"):
    if not reduced[key]:
        raise SystemExit(f"Command Center Reduced Motion profile weakened: {key}")
for motion_class, bounds in profile["duration_classes_ms"].items():
    if len(bounds) != 2 or bounds[0] < 0 or bounds[1] <= bounds[0]:
        raise SystemExit(f"invalid duration bounds: {motion_class}")
profile_authority = profile["authority"]
if (
    profile_authority["production_binding_authorized"]
    or profile_authority["visual_identity_change_authorized"]
    or profile_authority["stage8_opened"]
):
    raise SystemExit("reference Motion Profile inflated authority")

markers = {
    DOCS[0]: ("Motion = State + Meaning + Interaction + Function", "No external engine becomes foundational"),
    DOCS[1]: ("The renderer is replaceable. The semantic meaning is not.", "Reduced Motion is a semantic adapter mode"),
    DOCS[2]: ("Five mandatory reference scenarios", "There may be multiple winners"),
    DOCS[3]: ("Motion Platform Cell", "APPROVED_WITH_CAPABILITY_GAP"),
    DOCS[4]: ("MP0 — Foundation Lock", "MP6 — Cross-project Proof"),
}
for path, required in markers.items():
    doc = path.read_text(encoding="utf-8")
    for marker in required:
        if marker not in doc:
            raise SystemExit(f"Motion Platform documentation drifted: {path.name}: {marker}")

print(
    "Motion Platform contract validation: PASS "
    "(MP0 foundation + semantic catalog + candidate registry + reference profile)"
)
