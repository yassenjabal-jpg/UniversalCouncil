from __future__ import annotations

import hashlib
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
CAPSULE_CONTRACT = PROJECT / "context-capsule-contract.json"

HISTORICAL_PRE = PROJECT / "approvals" / "2026-10-21-context-resolver-compiler-pre.json"
HISTORICAL_POST = PROJECT / "approvals" / "2026-10-21-context-resolver-compiler-post.json"
HISTORICAL_CHANGE = PROJECT / "changes" / "2026-10-21-context-resolver-compiler.json"
HISTORICAL_CAPSULE = PROJECT / "context-capsules" / "2026-10-21-context-resolver-compiler.json"
PACKAGING_ADDENDUM = PROJECT / "changes" / "2026-10-21-context-resolver-packaging-addendum.json"

A1_PRE = PROJECT / "approvals" / "2026-10-21-repair-a1-context-baseline-pre.json"
A1_POST = PROJECT / "approvals" / "2026-10-21-repair-a1-context-baseline-post.json"
A1_CHANGE = PROJECT / "changes" / "2026-10-21-repair-a1-context-baseline.json"
A1_CAPSULE = PROJECT / "context-capsules" / "2026-10-21-repair-a1-context-baseline.json"
MAP_BUILDER = ROOT / "tools" / "build_command_center_project_context_map.py"

ALLOWED_AUTHORITY_CLASSES = {
    "OWNER_DIRECTIVE_TYPED",
    "LOCKED_POLICY",
    "CANONICAL_ARTIFACT",
    "ACCEPTED_EVIDENCE",
    "WORKING_DATA",
    "UNTRUSTED_EXTERNAL_DATA",
}

REQUIRED_SOURCE_IDS = {
    "agentic-os-policy",
    "architecture-invariants",
    "context-capsule-contract",
    "ux-state-contract",
    "murtakaz-approval-policy",
    "stage-phase-map",
    "visual-reference-manifest",
    "project-council",
    "product-studio",
    "phase0-execution-gates",
    "gateway-routing-policy",
    "gateway-routing-state",
    "capability-registry",
    "model-broker-policy",
    "capability-model-state",
    "context-pipeline-state",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=check,
    )


def blob_sha(relative: str) -> str:
    return git("rev-parse", f"HEAD:{relative}").stdout.strip()


def is_lower_hex(value: str, length: int) -> bool:
    return len(value) == length and all(character in "0123456789abcdef" for character in value)


def source_revision(sources: list[dict]) -> str:
    payload = "".join(
        f"{item['id']}|{item['path']}|{item['blob_sha']}\n"
        for item in sorted(sources, key=lambda item: item["id"])
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


for required in (
    CONTEXT_MAP,
    PIPELINE_STATE,
    AGENTIC_POLICY,
    UX_STATE,
    CAPSULE_CONTRACT,
    HISTORICAL_PRE,
    HISTORICAL_POST,
    HISTORICAL_CHANGE,
    HISTORICAL_CAPSULE,
    PACKAGING_ADDENDUM,
    A1_PRE,
    A1_CHANGE,
    A1_CAPSULE,
    MAP_BUILDER,
):
    if not required.exists():
        raise SystemExit(f"missing context-pipeline artifact: {required.relative_to(ROOT)}")

context_map = load(CONTEXT_MAP)
pipeline = load(PIPELINE_STATE)
agentic = load(AGENTIC_POLICY)
ux = load(UX_STATE)
capsule_contract = load(CAPSULE_CONTRACT)
historical_post = load(HISTORICAL_POST)
a1_pre = load(A1_PRE)
a1_change = load(A1_CHANGE)
a1_capsule = load(A1_CAPSULE)
a1_post = load(A1_POST) if A1_POST.exists() else None

if context_map["schema_version"] != "2.0":
    raise SystemExit("Project context map must use repaired schema 2.0")
if context_map["source_type"] != "project_local_repository_projection":
    raise SystemExit("Project context map source type drifted")
if context_map["project_id"] != "universal-council-command-center":
    raise SystemExit("Project context map project id drifted")
if context_map["baseline_branch"] != "command-center/project-local-council-studio-20261019":
    raise SystemExit("Project context map canonical branch drifted")
if context_map["head_validation_mode"] != "BASELINE_ANCESTOR_AND_SOURCE_BLOBS_MATCH_HEAD":
    raise SystemExit("Project context map HEAD validation mode drifted")

baseline = context_map["baseline_revision"]
if not is_lower_hex(baseline, 40):
    raise SystemExit("Project context baseline_revision is not a valid Git SHA")
if baseline != a1_pre["canonical_base"]["sha"]:
    raise SystemExit("Project context baseline differs from A1 Murtakaz pre-approval")
if baseline != a1_change["base_revision"]["sha"]:
    raise SystemExit("Project context baseline differs from A1 Change Envelope")
if baseline != a1_capsule["source_revision"]["sha"]:
    raise SystemExit("Project context baseline differs from A1 bootstrap capsule")
if git("merge-base", "--is-ancestor", baseline, "HEAD", check=False).returncode != 0:
    raise SystemExit("Project context baseline is not an ancestor of the actual checkout HEAD")

sources = context_map["sources"]
if not sources:
    raise SystemExit("Project context map must contain sources")
ids = [item["id"] for item in sources]
if len(ids) != len(set(ids)):
    raise SystemExit("Duplicate project context source id")
if set(ids) != REQUIRED_SOURCE_IDS:
    raise SystemExit("Project context map canonical source set drifted")

for source in sources:
    if source["authority_class"] not in ALLOWED_AUTHORITY_CLASSES:
        raise SystemExit(f"Unsupported context authority class: {source['authority_class']}")
    if source["freshness"] not in {"CURRENT", "STALE"}:
        raise SystemExit(f"Unsupported context freshness: {source['freshness']}")
    if not is_lower_hex(source["blob_sha"], 40):
        raise SystemExit(f"Invalid context source blob SHA: {source['id']}")
    if blob_sha(source["path"]) != source["blob_sha"]:
        raise SystemExit(f"Context source blob drift at actual HEAD: {source['id']}")
    expected_untrusted = source["authority_class"] == "UNTRUSTED_EXTERNAL_DATA"
    if source["untrusted"] is not expected_untrusted:
        raise SystemExit(f"Untrusted flag/authority mismatch: {source['id']}")
    if not source["domains"] or not source["scopes"]:
        raise SystemExit(f"Context source domains/scopes missing: {source['id']}")

expected_revision = source_revision(sources)
if not is_lower_hex(context_map["source_revision"], 64):
    raise SystemExit("Project context source_revision must be SHA-256")
if context_map["source_revision"] != expected_revision:
    raise SystemExit("Project context source-set fingerprint drifted")

if context_map["conflicts"]:
    raise SystemExit("Canonical project context map currently expects no unresolved conflicts")
if context_map["active_work"] != ["REPAIR_WAVE_A1_CONTEXT_BASELINE"]:
    raise SystemExit("Project context active work is not aligned with repair A1")

manifest = context_map["project_manifest"]
if manifest["governance_system"] != "al-murtakaz" or manifest["owner_authority"] != "FINAL":
    raise SystemExit("Project context governance identity drifted")

current = context_map["current_state"]
if current["live_execution_authorized"] or current["stage8_opened"]:
    raise SystemExit("Context map may not authorize live execution or Stage 8")

if capsule_contract["schema_version"] != "1.1":
    raise SystemExit("Context Capsule contract was not upgraded for A1 provenance semantics")
for field in ("baseline_revision", "source_revision"):
    if field not in capsule_contract["required_fields"]:
        raise SystemExit(f"Context Capsule contract missing repaired provenance field: {field}")
semantics = capsule_contract.get("revision_semantics", {})
if "ANCESTOR" not in semantics.get("baseline_revision", ""):
    raise SystemExit("Context Capsule baseline semantics are not fail-closed")
if "SHA256" not in semantics.get("source_revision", ""):
    raise SystemExit("Context Capsule source revision is not defined as SHA-256 source-set truth")

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

if historical_post["decision"] != "APPROVED_BY_AL_MURTAKAZ":
    raise SystemExit("Historical Context pipeline approval evidence is missing")
if a1_pre["decision"] != "APPROVE_TO_IMPLEMENT":
    raise SystemExit("A1 context repair lacks Murtakaz pre-approval")
if a1_pre["live_execution_authorized"] or a1_pre["stage8_opened"]:
    raise SystemExit("A1 pre-approval may not enable live execution or Stage 8")
if a1_pre["final_adoption_granted"] or a1_pre["merge_authorized"]:
    raise SystemExit("A1 pre-approval may not pre-authorize adoption/merge")

if a1_change["pre_approval_receipt"] != (
    "state/command-center/project-governance/approvals/2026-10-21-repair-a1-context-baseline-pre.json"
):
    raise SystemExit("A1 Change Envelope is not bound to its pre-approval")
if a1_change["unplanned_scope_policy"] != "RETURN_TICKET_OR_NEW_CHANGE_ENVELOPE":
    raise SystemExit("A1 scope-growth rule drifted")
if a1_capsule["job_or_change_id"] != a1_change["change_id"] or not a1_capsule["immutable"]:
    raise SystemExit("A1 bootstrap Context Capsule binding drifted")

status = pipeline["status"]
extension = pipeline.get("current_extension")
if status == "MURTAKAZ_REVIEW_REQUIRED":
    if not extension or extension.get("change_id") != "CC-REPAIR-A1-CONTEXT-BASELINE-2026-10-21":
        raise SystemExit("Context pipeline repair extension is not tracked")
    if extension.get("status") != "IMPLEMENTING":
        raise SystemExit("Context pipeline A1 extension status drifted")
    if a1_post is not None:
        raise SystemExit("A1 post-approval exists while pipeline still claims review required")
elif status == "APPROVED_BY_AL_MURTAKAZ":
    if not extension or extension.get("status") != "APPROVED_BY_AL_MURTAKAZ":
        raise SystemExit("Approved Context pipeline lacks approved A1 extension")
    if a1_post is None or a1_post.get("decision") != "APPROVED_BY_AL_MURTAKAZ":
        raise SystemExit("Context pipeline claims A1 approval without post-review receipt")
    if not a1_post["adoption_authorized"] or not a1_post["merge_authorized"]:
        raise SystemExit("A1 post-review did not authorize adoption/merge")
    if a1_post["live_execution_authorized"] or a1_post["stage8_opened"]:
        raise SystemExit("A1 post-review inflated runtime authority")
else:
    raise SystemExit(f"Unexpected Context pipeline status: {status}")

truth = pipeline["truth_rules"]
for flag in (
    "current_only_compilation",
    "stale_context_blocks_compilation",
    "context_conflict_blocks_compilation",
    "unknown_never_success",
    "deterministic_capsule_id",
    "source_digest_changes_capsule_id",
    "baseline_may_be_historical_provenance",
    "baseline_must_be_ancestor_of_validated_head",
    "source_revision_is_source_set_sha256",
    "declared_source_blobs_must_match_validated_head",
):
    if truth.get(flag) is not True:
        raise SystemExit(f"Context pipeline truth rule disabled: {flag}")
if truth["untrusted_content_can_govern"]:
    raise SystemExit("Untrusted content may not govern compiled context")

authority = pipeline["authority"]
if (
    authority["live_execution_authorized"]
    or authority["stage8_opened"]
    or authority["tool_execution_added"]
    or authority["model_provider_calls_added"]
):
    raise SystemExit("Context pipeline implementation inflated authority")

subprocess.run(
    [__import__("sys").executable, str(MAP_BUILDER), "--check"],
    cwd=ROOT,
    check=True,
)

host_file = (ROOT / "apps" / "UniversalCouncil.CommandCenter.Host" / "CommandCenterComposition.cs").read_text(
    encoding="utf-8"
)
if "IProjectContextResolver ContextResolver" not in host_file:
    raise SystemExit("Context Resolver is not exposed through Host composition")
if "IContextCapsuleCompiler ContextCapsuleCompiler" not in host_file:
    raise SystemExit("Context Capsule Compiler is not exposed through Host composition")

wpf_project = (ROOT / "apps" / "UniversalCouncil.CommandCenter" / "UniversalCouncil.CommandCenter.csproj").read_text(
    encoding="utf-8"
)
if "project-context-map.json" not in wpf_project:
    raise SystemExit("Windows package does not include project-context-map.json")

print("Al-Murtakaz Context Resolver/Capsule Compiler A1 validation: PASS")
