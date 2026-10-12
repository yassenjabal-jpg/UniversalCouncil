from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from company.runtime.memory_fabric import (  # noqa: E402
    MemoryFabricError,
    load_config,
    new_event,
    rebuild_memory,
    write_event,
)

CONFIG = ROOT / "company/config/memory_fabric.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Write an append-only Universal Memory delta and sync it to GitHub.")
    parser.add_argument("spec", type=Path, help="JSON event specification without event_id/created_at.")
    parser.add_argument("--no-sync", action="store_true")
    args = parser.parse_args()
    try:
        cfg = load_config(CONFIG)
        spec = json.loads(args.spec.read_text(encoding="utf-8"))
        if not isinstance(spec, dict):
            raise MemoryFabricError("memory spec root must be an object")
        event = new_event(cfg=cfg, **spec)
        path = write_event(ROOT / cfg["memory_root"], event, cfg)
        catalog = rebuild_memory(ROOT / cfg["memory_root"], cfg)
        if catalog["conflict_count"]:
            path.unlink(missing_ok=True)
            rebuild_memory(ROOT / cfg["memory_root"], cfg)
            raise MemoryFabricError("new memory delta would create a canonical conflict")
        sync_result = None
        if not args.no_sync:
            proc = subprocess.run(
                [sys.executable, str(ROOT / "tools/memory_sync.py")],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            if proc.returncode != 0:
                raise MemoryFabricError(f"GitHub autosync failed: {proc.stderr.strip() or proc.stdout.strip()}")
            sync_result = proc.stdout.strip()
    except (OSError, json.JSONDecodeError, TypeError, MemoryFabricError) as exc:
        print(f"MEMORY_WRITE_ERROR: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "event": event,
                "path": str(path.relative_to(ROOT)),
                "synced": not args.no_sync,
                "sync_result": sync_result,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
