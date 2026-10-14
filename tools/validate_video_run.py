"""Check a private production receipt against actual local artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from company.runtime.lean_video_production import GATES, ProductionWorkflowError, validate_gate  # noqa: E402


def load_record(path: Path) -> dict:
    record = json.loads(path.read_text(encoding="utf-8"))
    for name, value in record.get("artifacts", {}).items():
        if isinstance(value, str):
            record["artifacts"][name] = str((path.parent / value).resolve())
    for receipt in record.get("gates", {}).values():
        for observation in receipt.get("checks", {}).values():
            value = observation.get("evidence_ref")
            if isinstance(value, str):
                observation["evidence_ref"] = str((path.parent / value).resolve())
        delivery = receipt.get("delivery", {})
        value = delivery.get("measurement_evidence_ref")
        if isinstance(value, str):
            delivery["measurement_evidence_ref"] = str((path.parent / value).resolve())
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, required=True)
    parser.add_argument("--gate", choices=GATES, required=True)
    parser.add_argument("--system-pilot", type=Path)
    args = parser.parse_args(argv)
    try:
        config = json.loads((ROOT / "company/config/channel_operating_system.json").read_text(encoding="utf-8"))
        run = load_record(args.record.resolve())
        pilot = load_record(args.system_pilot.resolve()) if args.system_pilot else None
        validate_gate(config, run, args.gate, system_pilot=pilot)
    except (OSError, ValueError, KeyError, TypeError, AttributeError, ProductionWorkflowError) as exc:
        print(json.dumps({"status": "BLOCKED", "gate": args.gate, "reason": str(exc)}, ensure_ascii=False))
        return 1
    print(
        json.dumps(
            {
                "status": "PASS",
                "gate": args.gate,
                "episode_id": run["episode_id"],
                "publication_authorized": False,
                "main_merge_authorized": False,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
