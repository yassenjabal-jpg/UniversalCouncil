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


def acquire_lock(
    lock: Path,
    *,
    wait_seconds: float = 0.0,
    stale_seconds: float = 300.0,
    poll_seconds: float = 0.1,
) -> int:
    lock.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + wait_seconds
    while True:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            payload = json.dumps({"pid": os.getpid(), "created_at": time.time()}).encode("utf-8")
            os.write(fd, payload)
            return fd
        except FileExistsError:
            try:
                age = time.time() - lock.stat().st_mtime
            except FileNotFoundError:
                continue
            if age > stale_seconds:
                lock.unlink(missing_ok=True)
                continue
            if time.monotonic() >= deadline:
                raise MemoryFabricError("memory sync lock wait timed out")
            time.sleep(poll_seconds)


def release_lock(fd: int, lock: Path) -> None:
    os.close(fd)
    lock.unlink(missing_ok=True)


def pending_event_files(pending_root: Path) -> list[Path]:
    events_root = pending_root / "events"
    if not events_root.exists():
        return []
    return sorted(path for path in events_root.rglob("*.json") if path.is_file())


def copy_pending_events(
    pending_root: Path,
    target_root: Path,
) -> tuple[list[Path], int]:
    source = pending_root / "events"
    target = target_root / "memory/events"
    included: list[Path] = []
    copied = 0
    for src in pending_event_files(pending_root):
        rel = src.relative_to(source)
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            if dst.read_bytes() != src.read_bytes():
                raise MemoryFabricError(f"event immutability violation for {rel}")
        else:
            shutil.copy2(src, dst)
            copied += 1
        included.append(src)
    return included, copied


def cleanup_pending(paths: list[Path], pending_root: Path) -> None:
    for path in paths:
        path.unlink(missing_ok=True)
    events_root = pending_root / "events"
    if not events_root.exists():
        return
    for directory in sorted(
        (path for path in events_root.rglob("*") if path.is_dir()),
        reverse=True,
    ):
        try:
            directory.rmdir()
        except OSError:
            pass


def remove_worktree(path: Path) -> None:
    if path.exists():
        run_git(["worktree", "remove", "--force", str(path)], ROOT, check=False)
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)


def sync_once(cfg: dict, attempt: int) -> dict:
    autosync = cfg["autosync"]
    remote = autosync["remote"]
    branch = autosync["branch"]
    pending_root = ROOT / cfg["pending_root"]
    run_git(["fetch", remote, branch, "--quiet"], ROOT)

    worktree = ROOT / ".runtime/memory/sync" / f"attempt-{attempt}-{uuid.uuid4().hex[:8]}"
    worktree.parent.mkdir(parents=True, exist_ok=True)
    remove_worktree(worktree)
    run_git(["worktree", "add", "--detach", str(worktree), f"{remote}/{branch}"], ROOT)
    try:
        processed, copied = copy_pending_events(pending_root, worktree)
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
                "processed_pending": [str(path) for path in processed],
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
                "processed_pending": [str(path) for path in processed],
                "commit": commit,
                "push_failed": True,
                "error": pushed.stderr.strip() or pushed.stdout.strip(),
            }
        return {
            "changed": True,
            "copied_events": copied,
            "processed_pending": [str(path) for path in processed],
            "commit": commit,
            "push_failed": False,
        }
    finally:
        remove_worktree(worktree)


def main() -> int:
    try:
        cfg = load_config(CONFIG)
        lock = ROOT / ".runtime/memory/memory-sync.lock"
        autosync = cfg["autosync"]
        fd = acquire_lock(
            lock,
            wait_seconds=float(autosync["lock_wait_seconds"]),
            stale_seconds=float(autosync["lock_stale_seconds"]),
        )
        try:
            attempts = int(autosync["max_push_retries"])
            last = None
            for attempt in range(1, attempts + 1):
                last = sync_once(cfg, attempt)
                if not last.get("push_failed"):
                    cleanup_pending(
                        [Path(path) for path in last.get("processed_pending", [])],
                        ROOT / cfg["pending_root"],
                    )
                    run_git(["fetch", autosync["remote"], autosync["branch"], "--quiet"], ROOT)
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
