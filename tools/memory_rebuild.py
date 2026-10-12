from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from company.runtime.memory_fabric import MemoryFabricError, load_config, rebuild_memory  # noqa: E402

CONFIG = ROOT / "company/config/memory_fabric.json"


def main() -> int:
    try:
        cfg = load_config(CONFIG)
        catalog = rebuild_memory(ROOT / cfg["memory_root"], cfg)
    except MemoryFabricError as exc:
        print(f"MEMORY_REBUILD_ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(catalog, indent=2, ensure_ascii=False))
    return 3 if catalog["conflict_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
