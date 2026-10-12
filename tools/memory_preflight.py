from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from company.runtime.memory_fabric import MemoryFabricError, load_config, memory_preflight  # noqa: E402

CONFIG = ROOT / "company/config/memory_fabric.json"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Refresh canonical Universal Memory from GitHub and rebuild local FTS."
    )
    parser.add_argument(
        "--no-fetch", action="store_true", help="Use the current working tree memory instead of origin/main."
    )
    args = parser.parse_args()
    try:
        cfg = load_config(CONFIG)
        result = memory_preflight(ROOT, cfg, fetch=not args.no_fetch)
    except MemoryFabricError as exc:
        print(f"MEMORY_PREFLIGHT_ERROR: {exc}", file=sys.stderr)
        return 2
    print("MEMORY_PREFLIGHT_OK")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
