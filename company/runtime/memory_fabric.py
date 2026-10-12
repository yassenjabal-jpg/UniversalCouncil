from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import subprocess
import tarfile
import uuid
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any


class MemoryFabricError(ValueError):
    pass


EVENT_ID_RE = re.compile(r"^MEM-[0-9]{8}-[0-9]{6}-[a-z0-9]{6}$")
LEVELS = {"L2_PROJECT", "L3_CANONICAL", "L4_OWNER_DIRECTIVE"}
KINDS = {
    "decision",
    "requirement",
    "status",
    "capability",
    "preference",
    "cancellation",
    "evidence",
    "proposal",
    "policy",
    "architecture",
}
CONFIDENCE = {"owner_confirmed", "verified", "evidence_backed", "proposal"}
SENSITIVITY = {"normal", "private_non_sensitive"}
SECRET_KEYS = {
    "password",
    "passwd",
    "api_key",
    "apikey",
    "token",
    "secret",
    "credential",
    "credentials",
    "private_key",
}


@dataclass(frozen=True)
class MemoryConflict:
    scope: str
    subject: str
    event_ids: tuple[str, ...]


@dataclass
class MemoryReduction:
    active: list[dict[str, Any]]
    superseded: set[str]
    conflicts: list[MemoryConflict]
    by_scope: dict[str, list[dict[str, Any]]]


def load_config(path: Path) -> dict[str, Any]:
    try:
        cfg = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MemoryFabricError(f"cannot load memory config: {exc}") from exc
    validate_config(cfg)
    return cfg


def validate_config(cfg: dict[str, Any]) -> bool:
    if cfg.get("version") != "1.0":
        raise MemoryFabricError("memory config must be version 1.0")
    if cfg.get("enabled") is not True:
        raise MemoryFabricError("memory fabric must be enabled")
    if cfg.get("conflict_policy") != "FAIL_PREFLIGHT":
        raise MemoryFabricError("memory conflicts must fail preflight")
    if set(cfg.get("persistence_levels", [])) != LEVELS:
        raise MemoryFabricError("persistence levels drifted")
    if not set(cfg.get("event_kinds", [])).issuperset(KINDS):
        raise MemoryFabricError("memory event kinds are incomplete")
    if cfg.get("autosync", {}).get("enabled") is not True:
        raise MemoryFabricError("memory autosync must stay enabled")
    if not isinstance(cfg.get("pending_root"), str) or not cfg["pending_root"].strip():
        raise MemoryFabricError("memory pending_root is required")
    autosync = cfg.get("autosync", {})
    if int(autosync.get("max_push_retries", 0)) < 1:
        raise MemoryFabricError("memory autosync retry count must be positive")
    if float(autosync.get("lock_wait_seconds", 0)) <= 0:
        raise MemoryFabricError("memory sync lock wait must be positive")
    if float(autosync.get("lock_stale_seconds", 0)) <= float(autosync.get("lock_wait_seconds", 0)):
        raise MemoryFabricError("memory sync stale-lock threshold must exceed lock wait")
    return True


def _parse_timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise MemoryFabricError("created_at must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise MemoryFabricError("created_at must include timezone")
    return parsed


def _walk_secret_keys(value: Any, prefix: str = "") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_norm = str(key).lower().strip()
            current = f"{prefix}.{key}" if prefix else str(key)
            if key_norm in SECRET_KEYS:
                findings.append(current)
            findings.extend(_walk_secret_keys(child, current))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(_walk_secret_keys(child, f"{prefix}[{index}]"))
    return findings


def validate_event(event: dict[str, Any], cfg: dict[str, Any] | None = None) -> bool:
    required = {
        "schema_version",
        "event_id",
        "created_at",
        "scope",
        "level",
        "kind",
        "subject",
        "summary",
        "details",
        "supersedes",
        "confidence",
        "sensitivity",
        "tags",
        "source",
    }
    missing = required - set(event)
    extras = set(event) - required
    if missing:
        raise MemoryFabricError(f"event missing fields: {sorted(missing)}")
    if extras:
        raise MemoryFabricError(f"event has unsupported fields: {sorted(extras)}")
    if event["schema_version"] != "1.0":
        raise MemoryFabricError("event schema_version must be 1.0")
    if not EVENT_ID_RE.fullmatch(str(event["event_id"])):
        raise MemoryFabricError("invalid memory event id")
    _parse_timestamp(str(event["created_at"]))
    scope = str(event["scope"])
    if not (scope in {"global", "council"} or re.fullmatch(r"(project|venture)/[a-z0-9_-]+", scope)):
        raise MemoryFabricError("invalid memory scope")
    if event["level"] not in LEVELS:
        raise MemoryFabricError("invalid memory level")
    if event["kind"] not in KINDS:
        raise MemoryFabricError("invalid memory kind")
    if not isinstance(event["subject"], str) or not event["subject"].strip():
        raise MemoryFabricError("memory subject is required")
    if len(event["subject"]) > 160:
        raise MemoryFabricError("memory subject is too long")
    if not isinstance(event["summary"], str) or not event["summary"].strip():
        raise MemoryFabricError("memory summary is required")
    max_summary = int((cfg or {}).get("max_summary_chars", 1200))
    if len(event["summary"]) > max_summary:
        raise MemoryFabricError("memory summary is too long")
    if not isinstance(event["details"], dict):
        raise MemoryFabricError("memory details must be an object")
    detail_text = json.dumps(event["details"], ensure_ascii=False, sort_keys=True)
    max_details = int((cfg or {}).get("max_details_chars", 12000))
    if len(detail_text) > max_details:
        raise MemoryFabricError("memory details are too large")
    secret_keys = _walk_secret_keys(event["details"])
    if secret_keys:
        raise MemoryFabricError(f"memory event contains secret-like fields: {secret_keys}")
    supersedes = event["supersedes"]
    if not isinstance(supersedes, list) or len(set(supersedes)) != len(supersedes):
        raise MemoryFabricError("supersedes must be a unique list")
    if any(not isinstance(item, str) or not item.startswith("MEM-") for item in supersedes):
        raise MemoryFabricError("invalid supersedes event id")
    if event["event_id"] in supersedes:
        raise MemoryFabricError("event cannot supersede itself")
    if event["confidence"] not in CONFIDENCE:
        raise MemoryFabricError("invalid memory confidence")
    if event["level"] == "L4_OWNER_DIRECTIVE" and event["confidence"] != "owner_confirmed":
        raise MemoryFabricError("L4 owner directives require owner_confirmed confidence")
    if event["sensitivity"] not in SENSITIVITY:
        raise MemoryFabricError("unsupported memory sensitivity")
    if not isinstance(event["tags"], list) or len(set(event["tags"])) != len(event["tags"]):
        raise MemoryFabricError("tags must be a unique list")
    if any(not isinstance(tag, str) or not tag.strip() for tag in event["tags"]):
        raise MemoryFabricError("invalid tag")
    source = event["source"]
    if not isinstance(source, dict) or source.get("type") not in {
        "chat",
        "council",
        "repository",
        "tool",
        "migration",
    }:
        raise MemoryFabricError("invalid memory source")
    if set(source) - {"type", "ref", "commit"}:
        raise MemoryFabricError("unsupported source fields")
    return True


def new_event(
    *,
    scope: str,
    level: str,
    kind: str,
    subject: str,
    summary: str,
    details: dict[str, Any] | None = None,
    supersedes: list[str] | None = None,
    confidence: str = "evidence_backed",
    sensitivity: str = "normal",
    tags: list[str] | None = None,
    source: dict[str, Any] | None = None,
    now: datetime | None = None,
    cfg: dict[str, Any] | None = None,
) -> dict[str, Any]:
    now = now or datetime.now().astimezone()
    event_id = f"MEM-{now:%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:6]}"
    event = {
        "schema_version": "1.0",
        "event_id": event_id,
        "created_at": now.isoformat(timespec="seconds"),
        "scope": scope,
        "level": level,
        "kind": kind,
        "subject": subject,
        "summary": summary,
        "details": details or {},
        "supersedes": supersedes or [],
        "confidence": confidence,
        "sensitivity": sensitivity,
        "tags": tags or [],
        "source": source or {"type": "council"},
    }
    validate_event(event, cfg)
    return event


def event_path(memory_root: Path, event: dict[str, Any]) -> Path:
    day = str(event["created_at"])[:10]
    return memory_root / "events" / day / f"{event['event_id']}.json"


def write_event(memory_root: Path, event: dict[str, Any], cfg: dict[str, Any] | None = None) -> Path:
    validate_event(event, cfg)
    path = event_path(memory_root, event)
    if path.exists():
        raise MemoryFabricError(f"memory event already exists: {event['event_id']}")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(event, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)
    return path


def load_events(memory_root: Path, cfg: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    seen: set[str] = set()
    events_root = memory_root / "events"
    if not events_root.exists():
        return events
    for path in sorted(events_root.rglob("*.json")):
        try:
            event = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise MemoryFabricError(f"invalid event file {path}: {exc}") from exc
        if not isinstance(event, dict):
            raise MemoryFabricError(f"event root must be object: {path}")
        validate_event(event, cfg)
        if event["event_id"] in seen:
            raise MemoryFabricError(f"duplicate memory event id: {event['event_id']}")
        seen.add(event["event_id"])
        events.append(event)
    events.sort(key=lambda item: (_parse_timestamp(item["created_at"]), item["event_id"]))
    return events


def reduce_events(events: list[dict[str, Any]]) -> MemoryReduction:
    by_id = {event["event_id"]: event for event in events}
    if len(by_id) != len(events):
        raise MemoryFabricError("duplicate event ids in reduction input")
    superseded: set[str] = set()
    for event in events:
        for target in event["supersedes"]:
            if target not in by_id:
                raise MemoryFabricError(f"event supersedes unknown id: {target}")
            superseded.add(target)

    active = [event for event in events if event["event_id"] not in superseded]
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for event in active:
        grouped[(event["scope"], event["subject"])].append(event)

    conflicts = [
        MemoryConflict(scope=scope, subject=subject, event_ids=tuple(item["event_id"] for item in items))
        for (scope, subject), items in grouped.items()
        if len(items) > 1
    ]
    by_scope: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in active:
        by_scope[event["scope"]].append(event)
    for scope in by_scope:
        by_scope[scope].sort(key=lambda item: (item["subject"], item["created_at"]))
    return MemoryReduction(
        active=active,
        superseded=superseded,
        conflicts=conflicts,
        by_scope=dict(by_scope),
    )


def _scope_snapshot_path(memory_root: Path, scope: str) -> Path:
    if scope == "global":
        return memory_root / "snapshots" / "GLOBAL.md"
    if scope == "council":
        return memory_root / "snapshots" / "COUNCIL.md"
    prefix, name = scope.split("/", 1)
    folder = "projects" if prefix == "project" else "ventures"
    return memory_root / "snapshots" / folder / f"{name}.md"


def render_snapshot(scope: str, events: list[dict[str, Any]], conflicts: list[MemoryConflict]) -> str:
    title = scope.upper() if "/" not in scope else scope.replace("/", " / ")
    lines = [
        f"# Memory Snapshot — {title}",
        "",
        "> Generated from append-only memory events. Do not edit manually.",
        "",
    ]
    conflict_subjects = {item.subject for item in conflicts if item.scope == scope}
    if not events:
        lines.extend(["No active memory events.", ""])
        return "\n".join(lines)
    for event in events:
        marker = " ⚠ CONFLICT" if event["subject"] in conflict_subjects else ""
        lines.extend(
            [
                f"## {event['subject']}{marker}",
                f"- **Event:** `{event['event_id']}`",
                f"- **Level:** `{event['level']}`",
                f"- **Kind:** `{event['kind']}`",
                f"- **Confidence:** `{event['confidence']}`",
                f"- **Updated:** `{event['created_at']}`",
                f"- **Summary:** {event['summary']}",
            ]
        )
        if event["details"]:
            lines.append("- **Details:**")
            for key, value in sorted(event["details"].items()):
                rendered = (
                    json.dumps(value, ensure_ascii=False, sort_keys=True) if not isinstance(value, str) else value
                )
                lines.append(f"  - `{key}`: {rendered}")
        if event["supersedes"]:
            supersedes = ", ".join(f"`{item}`" for item in event["supersedes"])
            lines.append(f"- **Supersedes:** {supersedes}")
        if event["tags"]:
            lines.append(f"- **Tags:** {', '.join(event['tags'])}")
        lines.append("")
    return "\n".join(lines)


def build_catalog(events: list[dict[str, Any]], reduction: MemoryReduction) -> dict[str, Any]:
    latest = events[-1]["created_at"] if events else None
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "event_count": len(events),
        "active_count": len(reduction.active),
        "superseded_count": len(reduction.superseded),
        "conflict_count": len(reduction.conflicts),
        "latest_event_at": latest,
        "scopes": {
            scope: [
                {
                    "event_id": event["event_id"],
                    "subject": event["subject"],
                    "level": event["level"],
                    "kind": event["kind"],
                    "summary": event["summary"],
                    "created_at": event["created_at"],
                    "confidence": event["confidence"],
                }
                for event in items
            ]
            for scope, items in sorted(reduction.by_scope.items())
        },
        "conflicts": [
            {
                "scope": conflict.scope,
                "subject": conflict.subject,
                "event_ids": list(conflict.event_ids),
            }
            for conflict in reduction.conflicts
        ],
    }


def rebuild_memory(memory_root: Path, cfg: dict[str, Any] | None = None) -> dict[str, Any]:
    events = load_events(memory_root, cfg)
    reduction = reduce_events(events)
    snapshots_root = memory_root / "snapshots"
    snapshots_root.mkdir(parents=True, exist_ok=True)

    expected: set[Path] = set()
    for scope, scope_events in reduction.by_scope.items():
        path = _scope_snapshot_path(memory_root, scope)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            render_snapshot(scope, scope_events, reduction.conflicts).rstrip() + "\n",
            encoding="utf-8",
        )
        expected.add(path.resolve())

    for path in snapshots_root.rglob("*.md"):
        if path.resolve() not in expected:
            path.unlink()

    catalog = build_catalog(events, reduction)
    (memory_root / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return catalog


def build_search_index(memory_root: Path, db_path: Path, cfg: dict[str, Any] | None = None) -> Path:
    events = load_events(memory_root, cfg)
    reduction = reduce_events(events)
    if reduction.conflicts:
        conflict_text = "; ".join(
            f"{item.scope}:{item.subject}={','.join(item.event_ids)}"
            for item in reduction.conflicts
        )
        raise MemoryFabricError(f"cannot build search index with unresolved conflicts: {conflict_text}")
    events = reduction.active
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "CREATE TABLE events (event_id TEXT PRIMARY KEY, scope TEXT, subject TEXT, summary TEXT, details TEXT, tags TEXT, level TEXT, kind TEXT, created_at TEXT)"
        )
        conn.execute(
            "CREATE VIRTUAL TABLE memory_fts USING fts5(event_id UNINDEXED, scope, subject, summary, details, tags)"
        )
        for event in events:
            row = (
                event["event_id"],
                event["scope"],
                event["subject"],
                event["summary"],
                json.dumps(event["details"], ensure_ascii=False, sort_keys=True),
                " ".join(event["tags"]),
                event["level"],
                event["kind"],
                event["created_at"],
            )
            conn.execute("INSERT INTO events VALUES (?,?,?,?,?,?,?,?,?)", row)
            conn.execute(
                "INSERT INTO memory_fts(event_id, scope, subject, summary, details, tags) VALUES (?,?,?,?,?,?)",
                row[:6],
            )
        conn.commit()
    except sqlite3.OperationalError as exc:
        raise MemoryFabricError(f"SQLite FTS5 is unavailable: {exc}") from exc
    finally:
        conn.close()
    return db_path


def _fts_literal_query(query: str) -> str:
    tokens = re.findall(r"\w+", query, flags=re.UNICODE)
    if not tokens:
        raise MemoryFabricError("memory search query has no searchable terms")
    return " AND ".join(f'"{token.replace(chr(34), chr(34) * 2)}"' for token in tokens)


def search_index(db_path: Path, query: str, top_k: int = 12) -> list[dict[str, Any]]:
    if not query.strip():
        raise MemoryFabricError("memory search query is required")
    if not db_path.is_file():
        raise MemoryFabricError("memory search index is missing")
    fts_query = _fts_literal_query(query)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT e.*, bm25(memory_fts) AS rank
            FROM memory_fts
            JOIN events e ON e.event_id = memory_fts.event_id
            WHERE memory_fts MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (fts_query, int(top_k)),
        ).fetchall()
        return [dict(row) for row in rows]
    except sqlite3.OperationalError as exc:
        raise MemoryFabricError(f"memory search failed: {exc}") from exc
    finally:
        conn.close()


def _safe_extract_tar(data: bytes, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=BytesIO(data), mode="r:") as archive:
        root = target.resolve()
        for member in archive.getmembers():
            candidate = (target / member.name).resolve()
            try:
                candidate.relative_to(root)
            except ValueError as exc:
                raise MemoryFabricError("unsafe path in Git memory archive") from exc
        archive.extractall(target, filter="data")


def refresh_from_git(repo_root: Path, cache_root: Path, remote_ref: str = "origin/main") -> str:
    fetch = subprocess.run(
        ["git", "fetch", "origin", "main", "--quiet"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if fetch.returncode != 0:
        raise MemoryFabricError(f"git fetch failed: {fetch.stderr.strip()}")
    sha = subprocess.run(
        ["git", "rev-parse", remote_ref],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if sha.returncode != 0:
        raise MemoryFabricError(f"cannot resolve {remote_ref}: {sha.stderr.strip()}")
    archive = subprocess.run(
        ["git", "archive", "--format=tar", remote_ref, "memory"],
        cwd=repo_root,
        capture_output=True,
        check=False,
    )
    if archive.returncode != 0:
        raise MemoryFabricError("cannot read memory tree from Git")
    if cache_root.exists():
        for path in sorted(cache_root.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
    cache_root.mkdir(parents=True, exist_ok=True)
    _safe_extract_tar(archive.stdout, cache_root)
    return sha.stdout.strip()


def memory_preflight(repo_root: Path, cfg: dict[str, Any], *, fetch: bool = True) -> dict[str, Any]:
    memory_root = repo_root / cfg["memory_root"]
    source_sha = None
    if fetch:
        cache_root = repo_root / cfg["cache_root"]
        source_sha = refresh_from_git(repo_root, cache_root, cfg["canonical_remote"])
        memory_root = cache_root / "memory"
    events = load_events(memory_root, cfg)
    reduction = reduce_events(events)
    if reduction.conflicts and cfg["conflict_policy"] == "FAIL_PREFLIGHT":
        conflict_text = "; ".join(
            f"{item.scope}:{item.subject}={','.join(item.event_ids)}" for item in reduction.conflicts
        )
        raise MemoryFabricError(f"canonical memory conflict: {conflict_text}")
    db_path = repo_root / cfg["local_index"]
    build_search_index(memory_root, db_path, cfg)
    return {
        "source_sha": source_sha,
        "event_count": len(events),
        "active_count": len(reduction.active),
        "conflict_count": len(reduction.conflicts),
        "latest_event_at": events[-1]["created_at"] if events else None,
        "index_path": str(db_path),
    }


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
