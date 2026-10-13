from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from company.runtime.agent_bakeoff_provenance import validate_manifest  # noqa: E402

ALLOWED_CASES = {"c02_gui_primary_hybrid", "c04_after_effects_runtime_status"}
ALLOWED_RUNTIMES = {"baseline", "openai_agents", "microsoft_agent_framework"}
REQUIRED_TRUE = (
    "task_completed",
    "verification_passed",
    "selector_recovered",
    "correct_execution_path",
    "no_unintended_action",
)
REQUIRED_EVIDENCE = (
    "before_evidence",
    "semantic_action_receipt",
    "after_evidence",
    "execution_path",
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write(path: Path, payload) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temp.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Attach verified YASSIN desktop evidence to a full bake-off result.")
    parser.add_argument("--runtime", required=True, choices=sorted(ALLOWED_RUNTIMES))
    parser.add_argument("--case", required=True, choices=sorted(ALLOWED_CASES))
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--results", default="benchmarks/agent_runtime/results.json")
    parser.add_argument("--manifest", default="benchmarks/agent_runtime/experiment_manifest.json")
    args = parser.parse_args()

    if (os.environ.get("COMPUTERNAME") or "").strip().upper() != "YASSIN":
        raise SystemExit("DESKTOP_EVIDENCE_BLOCKED: host must be YASSIN")

    manifest_path = ROOT / args.manifest
    manifest = load_json(manifest_path)
    validate_manifest(manifest, ROOT)
    if manifest.get("stage") != "full":
        raise SystemExit("DESKTOP_EVIDENCE_BLOCKED: full-stage manifest required")

    receipt_path = ROOT / args.receipt
    receipt = load_json(receipt_path)
    if str(receipt.get("host", "")).upper() != "YASSIN":
        raise SystemExit("DESKTOP_EVIDENCE_BLOCKED: receipt host must be YASSIN")
    if receipt.get("case_id") != args.case or receipt.get("runtime_id") != args.runtime:
        raise SystemExit("DESKTOP_EVIDENCE_BLOCKED: receipt runtime/case mismatch")
    for key in REQUIRED_TRUE:
        if receipt.get(key) is not True:
            raise SystemExit(f"DESKTOP_EVIDENCE_BLOCKED: {key} must be true")
    for key in REQUIRED_EVIDENCE:
        if not str(receipt.get(key, "")).strip():
            raise SystemExit(f"DESKTOP_EVIDENCE_BLOCKED: {key} is required")

    results_path = ROOT / args.results
    results = load_json(results_path)
    matched = 0
    receipt_hash = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
    for item in results:
        if (
            item.get("runtime_id") == args.runtime
            and item.get("case_id") == args.case
            and item.get("provenance", {}).get("experiment_id") == manifest["experiment_id"]
        ):
            if item.get("status") != "COMPLETED":
                raise SystemExit("DESKTOP_EVIDENCE_BLOCKED: live result is not completed")
            item["desktop"] = {key: True for key in REQUIRED_TRUE}
            item["desktop_evidence"] = {
                "receipt_path": str(receipt_path.relative_to(ROOT)),
                "receipt_sha256": receipt_hash,
                "host": "YASSIN",
                "execution_path": receipt["execution_path"],
                "before_evidence": receipt["before_evidence"],
                "semantic_action_receipt": receipt["semantic_action_receipt"],
                "after_evidence": receipt["after_evidence"],
            }
            matched += 1

    if matched != 1:
        raise SystemExit(f"DESKTOP_EVIDENCE_BLOCKED: expected one matching result, found {matched}")

    atomic_write(results_path, results)
    print(json.dumps({
        "status": "DESKTOP_EVIDENCE_ATTACHED",
        "runtime_id": args.runtime,
        "case_id": args.case,
        "receipt_sha256": receipt_hash,
        "cost_usd": 0.0,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
