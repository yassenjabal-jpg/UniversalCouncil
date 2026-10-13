from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from company.runtime.agent_bakeoff import BakeoffError, evaluate, load_cases, load_json, validate_config  # noqa: E402


def _load_results(path: Path) -> list[dict]:
    data = load_json(path)
    if not isinstance(data, list):
        raise BakeoffError("results file must contain a list")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate Universal Council agent-runtime bake-off results.")
    parser.add_argument("--config", default="company/config/agent_bakeoff.json")
    parser.add_argument("--cases", default="benchmarks/agent_runtime/cases.json")
    parser.add_argument("--results", default="benchmarks/agent_runtime/results.json")
    parser.add_argument("--mechanics", default="benchmarks/agent_runtime/mechanics.json")
    parser.add_argument("--manifest", default="benchmarks/agent_runtime/experiment_manifest.json")
    parser.add_argument("--out", default="benchmarks/agent_runtime/report.json")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    try:
        cfg = load_json(ROOT / args.config)
        validate_config(cfg)
        cases = load_cases(ROOT / args.cases)
        if args.validate_only:
            print(json.dumps({"status": "VALID", "cases": len(cases), "runtimes": sorted(cfg["runtimes"])}, indent=2))
            return 0

        results_path = ROOT / args.results
        mechanics_path = ROOT / args.mechanics
        manifest_path = ROOT / args.manifest
        missing_inputs = [
            str(path.relative_to(ROOT))
            for path in (results_path, mechanics_path, manifest_path)
            if not path.exists()
        ]
        if missing_inputs:
            print(
                json.dumps(
                    {
                        "status": "BLOCKED",
                        "reason": "required scoring inputs are missing",
                        "missing_inputs": missing_inputs,
                        "winner": None,
                    },
                    indent=2,
                )
            )
            return 3

        results = _load_results(results_path)
        mechanics = load_json(mechanics_path)
        if not isinstance(mechanics, dict):
            raise BakeoffError("mechanics file must contain an object keyed by runtime_id")
        manifest = load_json(manifest_path)
        if not isinstance(manifest, dict):
            raise BakeoffError("experiment manifest must contain an object")
        report = evaluate(cases, results, mechanics, cfg, expected_provenance=manifest)
        out = ROOT / args.out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0
    except BakeoffError as exc:
        print(f"AGENT_BAKEOFF_ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
