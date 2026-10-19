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
    for job in manifest.get("visual_jobs", []):
        for field in manifest["visual_job_contract"]["required_fields"]:
            if not job.get(field):
                raise ValueError(f"Missing visual job evidence: {field}")
        parent = parents[job["parent_role"]]
        if job["parent_sha256"] != parent["sha256"] or job["reference_attached"] is not True:
            raise ValueError("Visual job parent/attachment mismatch")
        if job.get("source_generation_id") in manifest["rejected_recent_generations"]:
            raise ValueError("Rejected visual generation reused")
        if job["output_path"] in {ref["path"] for ref in refs}:
            raise ValueError("Visual output cannot overwrite a canonical reference")
        artifact(job["output_path"], job["output_sha256"])
        artifact(job["comparison_evidence"])
        status = job["review_status"]
        if status not in (
            "MURTAKAZ_REVIEW_REQUIRED",
            "RETURNED_FOR_CHANGES",
            "REJECTED_VISUAL_DRIFT",
            "APPROVED_BY_AL_MURTAKAZ",
        ):
            raise ValueError("Invalid visual review status")
        if status == "APPROVED_BY_AL_MURTAKAZ":
            for field in manifest["visual_job_contract"]["approval_requires"]:
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
    validate(root, json.loads((root / "state/command-center/living-operations-reference-manifest.json").read_text()))
    print("Visual reference integrity: PASS (not aesthetic approval)")
