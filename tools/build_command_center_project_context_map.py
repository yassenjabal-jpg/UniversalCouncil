from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTEXT_MAP = ROOT / "state" / "command-center" / "project-context-map.json"


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=check,
    )


def blob_sha(relative: str) -> str:
    return git("rev-parse", f"HEAD:{relative}").stdout.strip()


def source_revision(sources: list[dict[str, object]]) -> str:
    payload = "".join(
        f"{item['id']}|{item['path']}|{item['blob_sha']}\n"
        for item in sorted(sources, key=lambda item: str(item["id"]))
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def baseline_is_ancestor(baseline: str) -> bool:
    return git("merge-base", "--is-ancestor", baseline, "HEAD", check=False).returncode == 0


def refresh(document: dict[str, object]) -> dict[str, object]:
    sources = document["sources"]
    if not isinstance(sources, list):
        raise SystemExit("project-context-map sources must be a list")

    for source in sources:
        if not isinstance(source, dict):
            raise SystemExit("project-context-map source entry must be an object")
        relative = str(source["path"])
        source["blob_sha"] = blob_sha(relative)

    document["source_revision"] = source_revision(sources)
    return document


def validate(document: dict[str, object]) -> None:
    if document.get("schema_version") != "2.0":
        raise SystemExit("project-context-map schema must be 2.0")
    if document.get("head_validation_mode") != "BASELINE_ANCESTOR_AND_SOURCE_BLOBS_MATCH_HEAD":
        raise SystemExit("project-context-map head validation mode drifted")

    baseline = str(document.get("baseline_revision", ""))
    if len(baseline) != 40:
        raise SystemExit("project-context-map baseline_revision must be a SHA-1 Git revision")
    if not baseline_is_ancestor(baseline):
        raise SystemExit("project-context-map baseline_revision is not an ancestor of checkout HEAD")

    sources = document.get("sources")
    if not isinstance(sources, list) or not sources:
        raise SystemExit("project-context-map sources are missing")

    for source in sources:
        if not isinstance(source, dict):
            raise SystemExit("project-context-map source entry must be an object")
        expected = blob_sha(str(source["path"]))
        if source.get("blob_sha") != expected:
            raise SystemExit(f"context source blob drift: {source.get('id')}")

    expected_revision = source_revision(sources)
    if document.get("source_revision") != expected_revision:
        raise SystemExit("project-context-map source_revision fingerprint drifted")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate the committed map against the actual checkout HEAD without writing.",
    )
    args = parser.parse_args()

    document = json.loads(CONTEXT_MAP.read_text(encoding="utf-8"))

    if args.check:
        validate(document)
        print("Command Center project context map: CURRENT")
        return 0

    refreshed = refresh(document)
    CONTEXT_MAP.write_text(
        json.dumps(refreshed, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    validate(refreshed)
    print(f"Updated {CONTEXT_MAP.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
