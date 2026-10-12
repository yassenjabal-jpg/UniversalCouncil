from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from company.runtime.evidence_sync import EvidenceSyncError, sync_repository  # noqa: E402
from company.runtime.memory_fabric import (  # noqa: E402
    MemoryFabricError,
    load_config as load_memory_config,
    memory_preflight,
)


def main() -> int:
    try:
        result = sync_repository(ROOT, apply=True)
    except EvidenceSyncError as exc:
        print(f"COUNCIL_PREFLIGHT_SYNC_ERROR: {exc}", file=sys.stderr)
        return 2

    validation = subprocess.run(
        [sys.executable, str(ROOT / "tools/validate_config.py")],
        cwd=ROOT,
        check=False,
    )
    if validation.returncode != 0:
        return validation.returncode

    try:
        memory_cfg = load_memory_config(ROOT / "company/config/memory_fabric.json")
        memory_result = memory_preflight(ROOT, memory_cfg, fetch=True)
    except MemoryFabricError as exc:
        print(f"COUNCIL_PREFLIGHT_MEMORY_ERROR: {exc}", file=sys.stderr)
        return 3

    summary = {key: value for key, value in result.items() if key != "registry"}
    print("COUNCIL_PREFLIGHT_OK")
    print(
        json.dumps(
            {
                "capability_evidence": summary,
                "memory": memory_result,
            },
            indent=2,
        )
    )
    if result["unavailable_sources"]:
        print(
            "WARNING: some approved evidence sources were unavailable; no capability was promoted from those sources.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
