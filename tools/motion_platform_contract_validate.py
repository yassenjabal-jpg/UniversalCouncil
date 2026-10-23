from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "state" / "motion-platform" / "platform-contract.json"
DOCS = [
    ROOT / "docs" / "operations" / "motion-platform" / "00_MOTION_PLATFORM_CHARTER.md",
    ROOT / "docs" / "operations" / "motion-platform" / "01_MOTION_PLATFORM_ARCHITECTURE.md",
    ROOT / "docs" / "operations" / "motion-platform" / "02_COMPATIBILITY_LAB.md",
    ROOT / "docs" / "operations" / "motion-platform" / "03_STUDIO_CAPABILITY_UPGRADE.md",
    ROOT / "docs" / "operations" / "motion-platform" / "04_MOTION_PLATFORM_ROADMAP.md",
]

if not CONTRACT.exists():
    raise SystemExit("missing Motion Platform contract")
for path in DOCS:
    if not path.exists():
        raise SystemExit(f"missing Motion Platform document: {path.relative_to(ROOT)}")

contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

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

if set(contract["purposes"]) != {
    "NAVIGATION",
    "STATE",
    "FEEDBACK",
    "ROUTING",
    "HANDOFF",
    "RECOVERY",
}:
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

markers = {
    DOCS[0]: ("Motion = State + Meaning + Interaction + Function", "No external engine becomes foundational"),
    DOCS[1]: ("The renderer is replaceable. The semantic meaning is not.", "Reduced Motion is a semantic adapter mode"),
    DOCS[2]: ("Five mandatory reference scenarios", "There may be multiple winners"),
    DOCS[3]: ("Motion Platform Cell", "APPROVED_WITH_CAPABILITY_GAP"),
    DOCS[4]: ("MP0 — Foundation Lock", "MP6 — Cross-project Proof"),
}
for path, required in markers.items():
    text = path.read_text(encoding="utf-8")
    for marker in required:
        if marker not in text:
            raise SystemExit(f"Motion Platform documentation drifted: {path.name}: {marker}")

print("Motion Platform contract validation: PASS (MP0 foundation guards enforced)")
