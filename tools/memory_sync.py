from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from company.runtime.memory_fabric import (  # noqa: E402
    MemoryFabricError,
    load_config,
    rebuild_memory,
)

CONFIG = ROOT / "company/config/memory_fabric.json"


def run_git(args: list[str], cwd: Path, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if check and proc.returncode != 0:
        raise MemoryFabricError(f"git {' '.join(args)} failed: {proc.stderr.strip() or proc.stdout.strip()}")
    return proc


def acquire_lock(lock: Path) -> int:
    lock.parent.mkdir(parents=True, exist_ok=True)
    try:
        return os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise MemoryFabricError("memory sync is already running") from exc


def release_lock(fd: int, lock: Path) -> None:
    os.close(fd)
    lock.unlink(missing_ok=True)


def copy_local_events(source_root: Path, target_root: Path) -> int:
    source = source_root / "memory/events"
    target = target_root / "memory/events"
    if not source.exists():
        return 0
    copied = 0
    for src in source.rglob("*.json"):
        rel = src.relative_to(source)
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            if dst.read_bytes() != src.read_bytes():
                raise MemoryFabricError(f"event immutability violation for {rel}")
            continue
        shutil.copy2(src, dst)
        copied += 1
    return copied


def remove_worktree(path: Path) -> None:
    if path.exists():
        run_git(["worktree", "remove", "--force", str(path)], ROOT, check=False)
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)


def sync_once(cfg: dict, attempt: int) -> dict:
    autosync = cfg["autosync"]
    remote = autosync["remote"]
    branch = autosync["branch"]
    run_git(["fetch", remote, branch, "--quiet"], ROOT)

    worktree = ROOT / ".runtime/memory/sync" / f"attempt-{attempt}-{uuid.uuid4().hex[:8]}"
    worktree.parent.mkdir(parents=True, exist_ok=True)
    remove_worktree(worktree)
    run_git(["worktree", "add", "--detach", str(worktree), f"{remote}/{branch}"], ROOT)
    try:
        copied = copy_local_events(ROOT, worktree)
        worktree_cfg = load_config(worktree / "company/config/memory_fabric.json")
        catalog = rebuild_memory(worktree / worktree_cfg["memory_root"], worktree_cfg)
        if catalog["conflict_count"]:
            raise MemoryFabricError("memory sync detected canonical conflicts")

        run_git(["add", "memory/events", "memory/snapshots", "memory/catalog.json"], worktree)
        status = run_git(["status", "--porcelain"], worktree).stdout.strip()
        if not status:
            return {
                "changed": False,
                "copied_events": copied,
                "remote_head": run_git(["rev-parse", "HEAD"], worktree).stdout.strip(),
            }

        run_git(
            [
                "-c",
                "user.name=Universal Memory Fabric",
                "-c",
                "user.email=memory-fabric@users.noreply.github.com",
                "commit",
                "-m",
                f"memory: autosync {copied} event(s)",
            ],
            worktree,
        )
        commit = run_git(["rev-parse", "HEAD"], worktree).stdout.strip()
        pushed = run_git(["push", remote, f"HEAD:{branch}"], worktree, check=False)
        if pushed.returncode != 0:
            return {
                "changed": True,
                "copied_events": copied,
                "commit": commit,
                "push_failed": True,
                "error": pushed.stderr.strip() or pushed.stdout.strip(),
            }
        return {
            "changed": True,
            "copied_events": copied,
            "commit": commit,
            "push_failed": False,
        }
    finally:
        remove_worktree(worktree)


def main() -> int:
    try:
        cfg = load_config(CONFIG)
        lock = ROOT / ".runtime/memory/memory-sync.lock"
        fd = acquire_lock(lock)
        try:
            attempts = int(cfg["autosync"]["max_push_retries"])
            last = None
            for attempt in range(1, attempts + 1):
                last = sync_once(cfg, attempt)
                if not last.get("push_failed"):
                    run_git(["fetch", cfg["autosync"]["remote"], cfg["autosync"]["branch"], "--quiet"], ROOT)
                    print(json.dumps({"status": "SYNCED", "attempt": attempt, **last}, indent=2))
                    return 0
                if attempt < attempts:
                    time.sleep(0.25 * attempt)
            raise MemoryFabricError(f"GitHub autosync exhausted retries: {last.get('error') if last else 'unknown'}")
        finally:
            release_lock(fd, lock)
    except MemoryFabricError as exc:
        print(f"MEMORY_SYNC_ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
