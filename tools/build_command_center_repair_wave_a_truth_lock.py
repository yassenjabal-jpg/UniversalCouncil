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


def blob_sha_at_revision(revision: str, relative: str) -> str:
    return git("rev-parse", f"{revision}:{relative}").stdout.strip()


def digest(sources: list[dict[str, object]]) -> str:
    payload = "".join(
        f"{item['id']}|{item['path']}|{item['blob_sha']}\n"
        for item in sorted(sources, key=lambda item: str(item["id"]))
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def is_ancestor(older: str, newer: str) -> bool:
    return git("merge-base", "--is-ancestor", older, newer, check=False).returncode == 0


def refresh_candidate(document: dict[str, object]) -> dict[str, object]:
    if document.get("status") == "APPROVED_BY_AL_MURTAKAZ":
        raise SystemExit("Approved Wave A truth lock is immutable and may not be refreshed")

    locked_revision = str(document.get("locked_revision", ""))
    sources = document.get("sources")
    if not isinstance(sources, list) or not sources:
        raise SystemExit("Wave A truth lock sources are missing")

    for source in sources:
        if not isinstance(source, dict):
            raise SystemExit("Wave A truth lock source must be an object")
        source["blob_sha"] = blob_sha_at_revision(locked_revision, str(source["path"]))

    document["lock_digest"] = digest(sources)
    return document


def validate(document: dict[str, object]) -> None:
    if document.get("schema_version") != "1.1":
        raise SystemExit("Wave A truth lock schema drifted")
    if document.get("validation_mode") != "LOCKED_REVISION_SOURCE_BLOBS_MATCH_HISTORICAL_COMMIT":
        raise SystemExit("Wave A truth lock validation mode drifted")
    if document.get("self_reference_excluded") is not True:
        raise SystemExit("Wave A truth lock must exclude self-reference")
    if document.get("immutable_after_approval") is not True:
        raise SystemExit("Approved Wave A truth lock must be immutable")
    if document.get("head_progression_allowed_after_lock") is not True:
        raise SystemExit("Wave A truth lock must permit governed post-lock HEAD progression")
    if document.get("lock_digest_algorithm") != "SHA256_SORTED_ID_PATH_BLOB_TUPLES":
        raise SystemExit("Wave A truth lock digest algorithm drifted")

    baseline = str(document.get("baseline_revision", ""))
    locked_revision = str(document.get("locked_revision", ""))
    if len(baseline) != 40 or len(locked_revision) != 40:
        raise SystemExit("Wave A baseline/locked revision must be Git SHAs")
    if not is_ancestor(baseline, locked_revision):
        raise SystemExit("Wave A baseline is not an ancestor of the locked revision")
    if not is_ancestor(locked_revision, "HEAD"):
        raise SystemExit("Wave A locked revision is not an ancestor of checkout HEAD")

    sources = document.get("sources")
    if not isinstance(sources, list) or not sources:
        raise SystemExit("Wave A truth lock sources are missing")

    ids = [str(item["id"]) for item in sources]
    if len(ids) != len(set(ids)):
        raise SystemExit("Wave A truth lock source ids must be unique")

    for source in sources:
        expected = blob_sha_at_revision(locked_revision, str(source["path"]))
        if source.get("blob_sha") != expected:
            raise SystemExit(f"Wave A historical source drift: {source.get('id')}")

    if document.get("lock_digest") != digest(sources):
        raise SystemExit("Wave A truth lock digest drifted")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate the approved historical Wave A lock against its locked revision.",
    )
    parser.add_argument(
        "--refresh-candidate",
        action="store_true",
        help="Refresh a non-approved candidate from locked_revision. Approved locks are immutable.",
    )
    args = parser.parse_args()

    document = json.loads(LOCK.read_text(encoding="utf-8"))
    if args.refresh_candidate:
        refreshed = refresh_candidate(document)
        LOCK.write_text(
            json.dumps(refreshed, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        validate(refreshed)
        print(f"Updated candidate {LOCK.relative_to(ROOT)}")
        return 0

    validate(document)
    print("Command Center Repair Wave A historical truth lock: CURRENT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
