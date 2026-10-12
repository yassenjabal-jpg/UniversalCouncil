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
    load_events,
    memory_preflight,
    new_event,
    reduce_events,
    write_event,
)

CONFIG = ROOT / "company/config/memory_fabric.json"


def _validate_against_canonical_and_pending(
    cfg: dict,
    event: dict,
) -> None:
    memory_preflight(ROOT, cfg, fetch=True)
    canonical_root = ROOT / cfg["cache_root"] / "memory"
    pending_root = ROOT / cfg["pending_root"]
    canonical = load_events(canonical_root, cfg)
    pending = load_events(pending_root, cfg)
    reduction = reduce_events([*canonical, *pending, event])
    if reduction.conflicts:
        conflict_text = "; ".join(
            f"{item.scope}:{item.subject}={','.join(item.event_ids)}" for item in reduction.conflicts
        )
        raise MemoryFabricError(f"new memory delta would create a canonical conflict: {conflict_text}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Queue an append-only Universal Memory delta and sync it to GitHub.")
    parser.add_argument("spec", type=Path, help="JSON event specification without event_id/created_at.")
    parser.add_argument("--no-sync", action="store_true")
    args = parser.parse_args()

    event = None
    path = None
    try:
        cfg = load_config(CONFIG)
        spec = json.loads(args.spec.read_text(encoding="utf-8"))
        if not isinstance(spec, dict):
            raise MemoryFabricError("memory spec root must be an object")

        event = new_event(cfg=cfg, **spec)
        _validate_against_canonical_and_pending(cfg, event)

        pending_root = ROOT / cfg["pending_root"]
        path = write_event(pending_root, event, cfg)

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
                rel = path.relative_to(ROOT)
                raise MemoryFabricError(
                    "GitHub autosync failed; event remains queued at "
                    f"{rel}: {proc.stderr.strip() or proc.stdout.strip()}"
                )
            sync_result = proc.stdout.strip()
    except (OSError, json.JSONDecodeError, TypeError, MemoryFabricError) as exc:
        print(f"MEMORY_WRITE_ERROR: {exc}", file=sys.stderr)
        return 2

    print(
        json.dumps(
            {
                "event": event,
                "pending_path": str(path.relative_to(ROOT)),
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
