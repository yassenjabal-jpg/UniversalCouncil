from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "command-center"
PROJECT = STATE / "project-governance"

CONTEXT_MAP = STATE / "project-context-map.json"
PIPELINE_STATE = STATE / "context-pipeline-state.json"
AGENTIC_POLICY = PROJECT / "agentic-os-policy.json"
UX_STATE = STATE / "living-operations-ux-state-contract.json"
PRE_APPROVAL = PROJECT / "approvals" / "2026-10-21-context-resolver-compiler-pre.json"
CHANGE = PROJECT / "changes" / "2026-10-21-context-resolver-compiler.json"
BOOTSTRAP_CAPSULE = PROJECT / "context-capsules" / "2026-10-21-context-resolver-compiler.json"
PACKAGING_ADDENDUM = PROJECT / "changes" / "2026-10-21-context-resolver-packaging-addendum.json"

ALLOWED_AUTHORITY_CLASSES = {
    "OWNER_DIRECTIVE_TYPED",
    "LOCKED_POLICY",
    "CANONICAL_ARTIFACT",
    "ACCEPTED_EVIDENCE",
    "WORKING_DATA",
    "UNTRUSTED_EXTERNAL_DATA",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def blob_sha(relative: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{relative}"],
        cwd=ROOT,
        text=True,
    ).strip()


for required in (
    CONTEXT_MAP,
    PIPELINE_STATE,
    AGENTIC_POLICY,
    UX_STATE,
    PRE_APPROVAL,
    CHANGE,
    BOOTSTRAP_CAPSULE,
    PACKAGING_ADDENDUM,
):
    if not required.exists():
        raise SystemExit(f"missing context-pipeline artifact: {required.relative_to(ROOT)}")

context_map = load(CONTEXT_MAP)
pipeline = load(PIPELINE_STATE)
agentic = load(AGENTIC_POLICY)
ux = load(UX_STATE)
pre = load(PRE_APPROVAL)
change = load(CHANGE)
bootstrap = load(BOOTSTRAP_CAPSULE)
addendum = load(PACKAGING_ADDENDUM)

if context_map["schema_version"] != "1.0":
    raise SystemExit("Unsupported project context map schema")
if context_map["source_type"] != "project_local_repository_projection":
    raise SystemExit("Project context map source type drifted")
if context_map["project_id"] != "universal-council-command-center":
    raise SystemExit("Project context map project id drifted")
if context_map["source_revision"] != pre["canonical_base"]["sha"]:
    raise SystemExit("Project context map baseline differs from Murtakaz pre-approval")
if context_map["source_revision"] != change["base_revision"]["sha"]:
    raise SystemExit("Project context map baseline differs from Change Envelope")
if bootstrap["source_revision"]["sha"] != context_map["source_revision"]:
    raise SystemExit("Bootstrap capsule baseline differs from context map")

manifest = context_map["project_manifest"]
if manifest["governance_system"] != "al-murtakaz":
    raise SystemExit("Project context map governance system drifted")
if manifest["owner_authority"] != "FINAL":
    raise SystemExit("Owner final authority is missing from context map")

current = context_map["current_state"]
if current["live_execution_authorized"] or current["stage8_opened"]:
    raise SystemExit("Context pipeline may not authorize live execution or Stage 8")

sources = context_map["sources"]
if not sources:
    raise SystemExit("Project context map must contain sources")
ids = [item["id"] for item in sources]
if len(ids) != len(set(ids)):
    raise SystemExit("Duplicate project context source id")

for source in sources:
    if source["authority_class"] not in ALLOWED_AUTHORITY_CLASSES:
        raise SystemExit(f"Unsupported context authority class: {source['authority_class']}")
    if source["freshness"] not in {"CURRENT", "STALE"}:
        raise SystemExit(f"Unsupported context freshness: {source['freshness']}")
    if len(source["blob_sha"]) != 40:
        raise SystemExit(f"Invalid context source blob sha: {source['id']}")
    if blob_sha(source["path"]) != source["blob_sha"]:
        raise SystemExit(f"Context source digest drift: {source['id']}")
    expected_untrusted = source["authority_class"] == "UNTRUSTED_EXTERNAL_DATA"
    if source["untrusted"] is not expected_untrusted:
        raise SystemExit(f"Untrusted flag/authority mismatch: {source['id']}")
    if not source["domains"] or not source["scopes"]:
        raise SystemExit(f"Context source domains/scopes missing: {source['id']}")

if context_map["conflicts"]:
    raise SystemExit("Canonical project context map currently expects no unresolved conflicts")

required_source_ids = {
    "agentic-os-policy",
    "architecture-invariants",
    "context-capsule-contract",
    "ux-state-contract",
    "murtakaz-approval-policy",
    "stage-phase-map",
    "visual-reference-manifest",
    "project-council",
    "product-studio",
}
if set(ids) != required_source_ids:
    raise SystemExit("Project context map canonical source set drifted")

if ux["status"] != "APPROVED_BY_AL_MURTAKAZ":
    raise SystemExit("Context pipeline must consume the approved UX State Contract")
if not ux["laws"]["stale_context_requires_new_capsule_and_replan"]:
    raise SystemExit("UX stale-context law is not active")
if not ux["laws"]["context_conflict_fails_closed"]:
    raise SystemExit("UX context-conflict fail-closed law is not active")

agentic_security = agentic["context_security"]
if not agentic_security["all_retrieved_content_is_data_by_default"]:
    raise SystemExit("Retrieved content must remain data by default")
if not agentic_security["retrieved_text_cannot_grant_permissions"]:
    raise SystemExit("Retrieved text may not grant permissions")
if not agentic_security["model_output_cannot_self_promote_to_canonical"]:
    raise SystemExit("Model output may not self-promote to canonical")

if pre["decision"] != "APPROVE_TO_IMPLEMENT":
    raise SystemExit("Context pipeline lacks Murtakaz pre-approval")
if pre["live_execution_authorized"] or pre["stage8_opened"]:
    raise SystemExit("Context pipeline pre-approval may not enable execution or Stage 8")
if pre["final_adoption_granted"] or pre["merge_authorized"]:
    raise SystemExit("Pre-approval may not pre-authorize adoption or merge")

if change["pre_approval_receipt"] != (
    "state/command-center/project-governance/approvals/"
    "2026-10-21-context-resolver-compiler-pre.json"
):
    raise SystemExit("Context pipeline Change Envelope is not bound to its pre-approval")
if change["unplanned_scope_policy"] != "RETURN_TICKET_OR_NEW_CHANGE_ENVELOPE":
    raise SystemExit("Context pipeline scope-growth rule drifted")

if bootstrap["job_or_change_id"] != change["change_id"]:
    raise SystemExit("Bootstrap capsule is not bound to the context-pipeline change")
if not bootstrap["immutable"]:
    raise SystemExit("Bootstrap context capsule must remain immutable")

if addendum["classification"] != "NON_MATERIAL_SCOPE_CLARIFICATION":
    raise SystemExit("Context packaging addendum classification drifted")
if addendum["material_scope_expansion"]:
    raise SystemExit("Context packaging addendum may not expand material scope")

if pipeline["status"] not in {
    "IMPLEMENTED_VALIDATION_PENDING",
    "APPROVED_BY_AL_MURTAKAZ",
}:
    raise SystemExit("Unexpected context pipeline implementation status")

authority = pipeline["authority"]
if (
    authority["live_execution_authorized"]
    or authority["stage8_opened"]
    or authority["tool_execution_added"]
    or authority["model_provider_calls_added"]
):
    raise SystemExit("Context pipeline implementation inflated authority")

truth = pipeline["truth_rules"]
for flag in (
    "current_only_compilation",
    "stale_context_blocks_compilation",
    "context_conflict_blocks_compilation",
    "unknown_never_success",
    "deterministic_capsule_id",
    "source_digest_changes_capsule_id",
):
    if truth.get(flag) is not True:
        raise SystemExit(f"Context pipeline truth rule disabled: {flag}")
if truth["untrusted_content_can_govern"]:
    raise SystemExit("Untrusted content may not govern compiled context")

host_file = (
    ROOT
    / "apps"
    / "UniversalCouncil.CommandCenter.Host"
    / "CommandCenterComposition.cs"
).read_text(encoding="utf-8")
if "IProjectContextResolver ContextResolver" not in host_file:
    raise SystemExit("Context Resolver is not exposed through Host composition")
if "IContextCapsuleCompiler ContextCapsuleCompiler" not in host_file:
    raise SystemExit("Context Capsule Compiler is not exposed through Host composition")

wpf_project = (
    ROOT
    / "apps"
    / "UniversalCouncil.CommandCenter"
    / "UniversalCouncil.CommandCenter.csproj"
).read_text(encoding="utf-8")
if "project-context-map.json" not in wpf_project:
    raise SystemExit("Windows package does not include project-context-map.json")

print("Al-Murtakaz Context Resolver/Capsule Compiler validation: PASS")
