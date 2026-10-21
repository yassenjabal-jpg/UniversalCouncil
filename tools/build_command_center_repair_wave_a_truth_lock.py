from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "state" / "command-center" / "project-governance" / "repair-wave-a-truth-lock.json"


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


def digest(sources: list[dict[str, object]]) -> str:
    payload = "".join(
        f"{item['id']}|{item['path']}|{item['blob_sha']}\n"
        for item in sorted(sources, key=lambda item: str(item["id"]))
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def baseline_is_ancestor(baseline: str) -> bool:
    return git("merge-base", "--is-ancestor", baseline, "HEAD", check=False).returncode == 0


def refresh(document: dict[str, object]) -> dict[str, object]:
    sources = document.get("sources")
    if not isinstance(sources, list) or not sources:
        raise SystemExit("Wave A truth lock sources are missing")

    for source in sources:
        if not isinstance(source, dict):
            raise SystemExit("Wave A truth lock source must be an object")
        source["blob_sha"] = blob_sha(str(source["path"]))

    document["lock_digest"] = digest(sources)
    return document


def validate(document: dict[str, object]) -> None:
    if document.get("schema_version") != "1.0":
        raise SystemExit("Wave A truth lock schema drifted")
    if document.get("validation_mode") != "BASELINE_ANCESTOR_PLUS_LOCKED_SOURCE_BLOBS_MATCH_HEAD":
        raise SystemExit("Wave A truth lock validation mode drifted")
    if document.get("self_reference_excluded") is not True:
        raise SystemExit("Wave A truth lock must exclude self-reference")
    if document.get("lock_digest_algorithm") != "SHA256_SORTED_ID_PATH_BLOB_TUPLES":
        raise SystemExit("Wave A truth lock digest algorithm drifted")

    baseline = str(document.get("baseline_revision", ""))
    if len(baseline) != 40:
        raise SystemExit("Wave A truth lock baseline must be a Git SHA")
    if not baseline_is_ancestor(baseline):
        raise SystemExit("Wave A truth lock baseline is not an ancestor of checkout HEAD")

    sources = document.get("sources")
    if not isinstance(sources, list) or not sources:
        raise SystemExit("Wave A truth lock sources are missing")

    ids = [str(item["id"]) for item in sources]
    if len(ids) != len(set(ids)):
        raise SystemExit("Wave A truth lock source ids must be unique")

    for source in sources:
        expected = blob_sha(str(source["path"]))
        if source.get("blob_sha") != expected:
            raise SystemExit(f"Wave A truth lock source drift: {source.get('id')}")

    expected_digest = digest(sources)
    if document.get("lock_digest") != expected_digest:
        raise SystemExit("Wave A truth lock digest drifted")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate the committed Wave A truth lock against the actual checkout HEAD.",
    )
    args = parser.parse_args()

    document = json.loads(LOCK.read_text(encoding="utf-8"))
    if args.check:
        validate(document)
        print("Command Center Repair Wave A truth lock: CURRENT")
        return 0

    refreshed = refresh(document)
    LOCK.write_text(
        json.dumps(refreshed, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    validate(refreshed)
    print(f"Updated {LOCK.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
