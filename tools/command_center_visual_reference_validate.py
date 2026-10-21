"""Verify visual provenance, not aesthetic fidelity or runtime readiness."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROLES = (
    "home_owner_workspace",
    "living_project_workspace",
    "software_autopilot_project",
    "studio_project",
    "owner_decision_mode",
    "checkpoint_recovery_fork",
    "pulse_visual_project_story",
    "project_complete_work_receipt",
)


def validate(root: Path, manifest: dict) -> None:
    def artifact(path: str, digest: str | None = None) -> str:
        target = (root / path).resolve()
        if not target.is_relative_to(root.resolve()) or not target.is_file():
            raise ValueError(f"Missing or unsafe visual artifact: {path}")
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if digest is not None and actual != digest:
            raise ValueError(f"Visual digest mismatch: {path}")
        return actual

    refs = manifest["references"]
    if [ref["role"] for ref in refs] != list(ROLES):
        raise ValueError("Canonical reference roles/order changed")
    if len({ref["sha256"] for ref in refs}) != 8:
        raise ValueError("Canonical references must be distinct")
    for ref in refs:
        artifact(ref["path"], ref["sha256"])
    parents = {ref["role"]: ref for ref in refs}
    inventory_path = manifest.get("object_inventory_path")
    if not inventory_path:
        raise ValueError("Missing canonical screen object inventory")
    artifact(inventory_path)
    inventory = json.loads((root / inventory_path).read_text())
    if inventory.get("source_of_truth") != "EIGHT_PINNED_CANONICAL_IMAGES":
        raise ValueError("Screen object inventory source of truth drifted")
    screen_inventories = inventory.get("screens", {})
    if set(screen_inventories) != set(ROLES):
        raise ValueError("Screen object inventory roles do not match canonical references")

    protocol_path = manifest.get("production_protocol_path")
    if not protocol_path:
        raise ValueError("Missing fail-closed visual production protocol")
    artifact(protocol_path)
    protocol = json.loads((root / protocol_path).read_text())
    if protocol.get("status") != "FAIL_CLOSED":
        raise ValueError("Visual production protocol is not fail-closed")

    contract = manifest["visual_job_contract"]
    allowed_modes = set(contract["allowed_production_modes"])
    if allowed_modes != set(protocol["allowed_production_modes"]):
        raise ValueError("Visual production mode allow-list drifted")
    if protocol.get("one_job_one_screen") is not True:
        raise ValueError("Visual production protocol must enforce one job per screen")
    if protocol.get("actual_reference_bytes_required") is not True:
        raise ValueError("Visual production protocol must require actual reference bytes")

    home_geometry_path = manifest.get("home_geometry_lock_path")
    if not home_geometry_path:
        raise ValueError("Missing Home geometry lock")
    artifact(home_geometry_path)
    home_geometry = json.loads((root / home_geometry_path).read_text())
    if (
        home_geometry.get("screen_id") != "home_owner_workspace"
        or home_geometry.get("parent_sha256") != parents["home_owner_workspace"]["sha256"]
        or home_geometry.get("council_pulse", {}).get("topology") != "HORIZONTAL_STRIP"
        or home_geometry.get("council_pulse", {}).get("exact_member_count") != 8
        or home_geometry.get("creativity_budget") != "MICRO_ONLY"
    ):
        raise ValueError("Home geometry/composition lock drifted")
    for job in manifest.get("visual_jobs", []):
        state = job.get("state")
        if state not in contract["allowed_states"]:
            raise ValueError("Invalid visual job state")

        for field in contract["preflight_required_fields"]:
            if field not in job or job[field] in ("", None):
                raise ValueError(f"Missing visual preflight evidence: {field}")

        parent = parents.get(job["parent_role"])
        if parent is None:
            raise ValueError("Unknown visual job parent role")
        if job["parent_sha256"] != parent["sha256"]:
            raise ValueError("Visual job parent hash mismatch")
        if job["production_mode"] not in allowed_modes:
            raise ValueError("Forbidden visual production mode")
        if job["single_screen_only"] is not True:
            raise ValueError("Canonical visual jobs must be single-screen")
        if job["preflight_registered"] is not True:
            raise ValueError("Visual job was not registered before render")
        if job["screen_inventory_id"] != job["parent_role"]:
            raise ValueError("Visual job screen inventory does not match parent role")
        if job["parent_role"] not in screen_inventories:
            raise ValueError("Visual job has no canonical screen object inventory")

        conditional = contract.get("conditional_requirements", {}).get(job["parent_role"], {})
        for field in conditional.get("preflight_required_fields", []):
            if field not in job or job[field] in ("", None):
                raise ValueError(f"Missing conditional visual preflight evidence: {field}")

        if job["parent_role"] == "home_owner_workspace":
            if job.get("geometry_lock_id") != home_geometry["lock_id"]:
                raise ValueError("Home visual job geometry lock does not match canonical lock")

        member_set = screen_inventories[job["parent_role"]].get("member_set", [])
        if member_set and job["member_inventory_verified"] is not True:
            raise ValueError("Visual job member inventory was not verified")

        if job.get("source_generation_id"):
            raise ValueError("Generated images may not be canonical UI parents or sources")

        binding_path = job["reference_binding_evidence"]
        artifact(binding_path)
        binding = json.loads((root / binding_path).read_text())
        for field in contract["reference_binding_receipt_schema"]["required_fields"]:
            if field not in binding or binding[field] in ("", None):
                raise ValueError(f"Missing reference-binding evidence: {field}")

        if (
            binding["job_id"] != job["job_id"]
            or binding["parent_role"] != job["parent_role"]
            or binding["parent_path"] != parent["path"]
            or binding["parent_sha256"] != job["parent_sha256"]
            or binding["tool_name"] != job["tool_name"]
            or binding["production_mode"] != job["production_mode"]
            or binding["screen_inventory_id"] != job["screen_inventory_id"]
            or binding["member_inventory_verified"] != job["member_inventory_verified"]
        ):
            raise ValueError("Reference-binding receipt does not match visual job")

        if binding["tool_received_reference_bytes"] is not True:
            raise ValueError("Production tool did not receive canonical reference bytes")
        if binding["single_screen"] is not True:
            raise ValueError("Reference-binding receipt is not single-screen")
        if binding["phase"] != contract["reference_binding_receipt_schema"]["phase"]:
            raise ValueError("Reference-binding receipt is not PRE_RENDER")
        if binding["render_not_started"] is not True:
            raise ValueError("Reference-binding receipt was not captured before render")

        if state == "PREFLIGHT_REGISTERED":
            if any(field in job for field in contract["rendered_required_fields"]):
                raise ValueError("Preflight visual job already claims rendered output")
            continue

        for field in contract["rendered_required_fields"]:
            if field not in job or job[field] in ("", None):
                raise ValueError(f"Missing rendered visual evidence: {field}")
        for field in conditional.get("rendered_required_fields", []):
            if field not in job or job[field] in ("", None):
                raise ValueError(f"Missing conditional rendered visual evidence: {field}")
        if job["render_started_after_preflight"] is not True:
            raise ValueError("Rendered output did not prove preflight ancestry")

        if job["parent_role"] == "home_owner_workspace":
            review_path = job["structural_review_evidence"]
            artifact(review_path)
            structural = json.loads((root / review_path).read_text())
            if (
                structural.get("decision") != "STRUCTURE_PASS"
                or structural.get("job_id") != job["job_id"]
                or structural.get("parent_sha256") != job["parent_sha256"]
                or structural.get("output_sha256") != job["output_sha256"]
                or structural.get("geometry_lock_id") != home_geometry["lock_id"]
                or structural.get("reviewed_before_aesthetic_review") is not True
            ):
                raise ValueError("Home structural review did not pass canonical geometry lock")
        if job["output_path"] in {ref["path"] for ref in refs}:
            raise ValueError("Visual output cannot overwrite a canonical reference")

        artifact(job["output_path"], job["output_sha256"])
        artifact(job["comparison_evidence"])

        if state == "APPROVED_BY_AL_MURTAKAZ":
            for field in contract["approval_requires"]:
                receipt_path = job.get(field, "")
                artifact(receipt_path)
                receipt = json.loads((root / receipt_path).read_text())
                if (
                    receipt.get("decision") != "APPROVED_BY_AL_MURTAKAZ"
                    or receipt.get("job_id") != job["job_id"]
                    or receipt.get("output_sha256") != job["output_sha256"]
                    or receipt.get("parent_sha256") != job["parent_sha256"]
                    or receipt.get("allowed_delta") != job["allowed_delta"]
                    or not receipt.get("reviewer")
                    or not receipt.get("review_mode")
                ):
                    raise ValueError("Approval scope/hash/reviewer mismatch")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    manifest_path = root / "state" / "command-center" / "living-operations-reference-manifest.json"
    validate(root, json.loads(manifest_path.read_text()))
    print("Visual reference integrity: PASS (not aesthetic approval)")
