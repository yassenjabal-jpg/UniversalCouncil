from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

from company.runtime.agent_bakeoff_provenance import validate_manifest  # noqa: E402

REQUIRED_CASES = {"c02_gui_primary_hybrid", "c04_after_effects_runtime_status"}
REQUIRED_RUNTIMES = {"baseline", "openai_agents", "microsoft_agent_framework"}
DESKTOP_KEYS = (
    "task_completed",
    "verification_passed",
    "selector_recovered",
    "correct_execution_path",
    "no_unintended_action",
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temp.replace(path)


def validate_receipts(receipts: list[dict[str, Any]], manifest: dict[str, Any]) -> None:
    if str(manifest.get("execution_host", "")).upper() != "YASSIN":
        raise ValueError("full manifest execution_host must be YASSIN")
    if float(manifest.get("financial_cost_usd", -1)) != 0.0:
        raise ValueError("full manifest must be zero cost")

    expected = {(runtime_id, case_id) for runtime_id in REQUIRED_RUNTIMES for case_id in REQUIRED_CASES}
    actual: set[tuple[str, str]] = set()

    for receipt in receipts:
        runtime_id = str(receipt.get("runtime_id", ""))
        case_id = str(receipt.get("case_id", ""))
        key = (runtime_id, case_id)
        if key in actual:
            raise ValueError(f"duplicate desktop receipt: {runtime_id}/{case_id}")
        actual.add(key)

        if str(receipt.get("execution_host", "")).upper() != "YASSIN":
            raise ValueError(f"{runtime_id}/{case_id}: desktop receipt is not from YASSIN")
        if receipt.get("manifest_id") != manifest.get("manifest_id"):
            raise ValueError(f"{runtime_id}/{case_id}: desktop receipt manifest mismatch")
        if float(receipt.get("cost_usd", -1)) != 0.0:
            raise ValueError(f"{runtime_id}/{case_id}: desktop receipt is not zero cost")
        desktop = receipt.get("desktop")
        if not isinstance(desktop, dict):
            raise ValueError(f"{runtime_id}/{case_id}: desktop object is required")
        if not all(desktop.get(name) is True for name in DESKTOP_KEYS):
            raise ValueError(f"{runtime_id}/{case_id}: desktop gate fields are not all true")
        execution_path = str(receipt.get("execution_path", "")).strip()
        if execution_path not in {"GUI_SEMANTIC", "GUI_PHYSICAL_FALLBACK"}:
            raise ValueError(f"{runtime_id}/{case_id}: invalid or missing execution_path")
        if execution_path == "GUI_PHYSICAL_FALLBACK" and not str(receipt.get("fallback_reason", "")).strip():
            raise ValueError(f"{runtime_id}/{case_id}: physical fallback requires a reason")

        evidence = receipt.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            raise ValueError(f"{runtime_id}/{case_id}: evidence list is required")
        evidence_kinds = {
            str(item.get("kind", "")).strip()
            for item in evidence
            if isinstance(item, dict) and str(item.get("ref", "")).strip()
        }
        required_kinds = {"before", "semantic_action", "after"}
        if not required_kinds.issubset(evidence_kinds):
            raise ValueError(
                f"{runtime_id}/{case_id}: evidence must include before, semantic_action and after refs"
            )

    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(f"desktop receipt set mismatch; missing={missing} extra={extra}")


def apply(results: list[dict[str, Any]], receipts: list[dict[str, Any]], manifest: dict[str, Any]) -> list[dict[str, Any]]:
    validate_receipts(receipts, manifest)
    receipt_map = {(r["runtime_id"], r["case_id"]): r for r in receipts}

    found: set[tuple[str, str]] = set()
    for result in results:
        key = (result.get("runtime_id"), result.get("case_id"))
        if key not in receipt_map:
            continue
        if result.get("provenance", {}).get("manifest_id") != manifest.get("manifest_id"):
            raise ValueError(f"{key[0]}/{key[1]}: result manifest mismatch before desktop merge")
        receipt = receipt_map[key]
        result["desktop"] = dict(receipt["desktop"])
        result["desktop_evidence"] = {
            "execution_path": receipt["execution_path"],
            "fallback_reason": receipt.get("fallback_reason"),
            "evidence": list(receipt["evidence"]),
        }
        found.add((str(key[0]), str(key[1])))

    expected = {(runtime_id, case_id) for runtime_id in REQUIRED_RUNTIMES for case_id in REQUIRED_CASES}
    if found != expected:
        raise ValueError(f"results do not contain every required desktop case: missing={sorted(expected - found)}")
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply verified YASSIN desktop receipts to full bake-off results.")
    parser.add_argument("--results", default="benchmarks/agent_runtime/results.json")
    parser.add_argument("--manifest", default="benchmarks/agent_runtime/experiment_manifest.json")
    parser.add_argument("--receipts", default="benchmarks/agent_runtime/desktop_receipts.json")
    args = parser.parse_args()

    if (os.environ.get("COMPUTERNAME") or "").strip().upper() != "YASSIN":
        print(json.dumps({"status": "BLOCKED", "reason": "desktop receipt merge is YASSIN-only"}, indent=2))
        return 3

    results_path = ROOT / args.results
    manifest_path = ROOT / args.manifest
    receipts_path = ROOT / args.receipts
    for path in (results_path, manifest_path, receipts_path):
        if not path.is_file():
            print(json.dumps({"status": "BLOCKED", "missing": str(path.relative_to(ROOT))}, indent=2))
            return 3

    results = load_json(results_path)
    manifest = load_json(manifest_path)
    validate_manifest(manifest, ROOT)
    if manifest.get("stage") != "full":
        raise ValueError("desktop receipt merge requires the full-stage manifest")
    receipts = load_json(receipts_path)
    if not isinstance(results, list) or not isinstance(receipts, list):
        raise ValueError("results and desktop receipts must be lists")

    updated = apply(results, receipts, manifest)
    write_json(results_path, updated)
    print(json.dumps({"status": "DESKTOP_RECEIPTS_APPLIED", "receipts": len(receipts), "cost_usd": 0.0}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
