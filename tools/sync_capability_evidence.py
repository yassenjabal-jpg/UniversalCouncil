from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from company.runtime.evidence_sync import EvidenceSyncError, sync_repository  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Import bounded capability evidence from approved subprojects.")
    parser.add_argument("--apply", action="store_true", help="write imported receipts and evidence metadata")
    args = parser.parse_args()
    try:
        result = sync_repository(ROOT, apply=args.apply)
    except EvidenceSyncError as exc:
        print(f"EVIDENCE_SYNC_ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({k: v for k, v in result.items() if k != "registry"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
