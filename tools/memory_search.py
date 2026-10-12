from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from company.runtime.memory_fabric import (  # noqa: E402
    MemoryFabricError,
    load_config,
    memory_preflight,
    search_index,
)

CONFIG = ROOT / "company/config/memory_fabric.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Search the canonical Universal Memory.")
    parser.add_argument("query")
    parser.add_argument("--top", type=int)
    parser.add_argument("--no-fetch", action="store_true")
    args = parser.parse_args()
    try:
        cfg = load_config(CONFIG)
        memory_preflight(ROOT, cfg, fetch=not args.no_fetch)
        rows = search_index(
            ROOT / cfg["local_index"],
            args.query,
            top_k=args.top or int(cfg["search_top_k"]),
        )
    except MemoryFabricError as exc:
        print(f"MEMORY_SEARCH_ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(rows, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
