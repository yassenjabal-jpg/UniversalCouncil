import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

import tools.memory_sync as memory_sync
from company.runtime.memory_fabric import MemoryFabricError

ROOT = Path(__file__).resolve().parents[2]
BASE_CFG = json.loads((ROOT / "company/config/memory_fabric.json").read_text(encoding="utf-8"))


class MemorySyncQueueTests(unittest.TestCase):
    def test_run_git_success_and_failure(self):
        ok = CompletedProcess(["git"], 0, stdout="ok", stderr="")
        with patch("tools.memory_sync.subprocess.run", return_value=ok):
            self.assertEqual(memory_sync.run_git(["status"], Path(".")), ok)

        fail = CompletedProcess(["git"], 1, stdout="", stderr="bad")
        with patch("tools.memory_sync.subprocess.run", return_value=fail):
            with self.assertRaises(MemoryFabricError):
                memory_sync.run_git(["status"], Path("."))
            self.assertEqual(memory_sync.run_git(["status"], Path("."), check=False).returncode, 1)

    def test_lock_lifecycle_immediate_busy_and_stale_recovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            lock = Path(tmp) / "sync.lock"
            fd = memory_sync.acquire_lock(lock)
            self.assertTrue(lock.exists())
            payload = json.loads(lock.read_text(encoding="utf-8"))
            self.assertEqual(payload["pid"], os.getpid())

            with self.assertRaises(MemoryFabricError):
                memory_sync.acquire_lock(lock, wait_seconds=0, stale_seconds=300)

            memory_sync.release_lock(fd, lock)
            self.assertFalse(lock.exists())

            lock.write_text("stale", encoding="utf-8")
            old = time.time() - 10
            os.utime(lock, (old, old))
            recovered = memory_sync.acquire_lock(lock, wait_seconds=0, stale_seconds=1)
            self.assertTrue(lock.exists())
            memory_sync.release_lock(recovered, lock)

    def test_lock_waits_for_busy_lock_then_succeeds(self):
        with tempfile.TemporaryDirectory() as tmp:
            lock = Path(tmp) / "sync.lock"
            lock.write_text("busy", encoding="utf-8")
            calls = {"count": 0}
            real_sleep = memory_sync.time.sleep

            def fake_sleep(seconds):
                calls["count"] += 1
                lock.unlink(missing_ok=True)
                real_sleep(0)

            with patch("tools.memory_sync.time.sleep", side_effect=fake_sleep):
                fd = memory_sync.acquire_lock(
                    lock,
                    wait_seconds=1,
                    stale_seconds=300,
                    poll_seconds=0.01,
                )
            self.assertGreaterEqual(calls["count"], 1)
            memory_sync.release_lock(fd, lock)

    def test_pending_discovery_copy_idempotency_and_immutability(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pending = root / "pending"
            target = root / "target"
            src = pending / "events/2026-10-12/a.json"
            src.parent.mkdir(parents=True)
            src.write_text('{"x":1}', encoding="utf-8")

            self.assertEqual(memory_sync.pending_event_files(pending), [src])
            included, copied = memory_sync.copy_pending_events(pending, target)
            self.assertEqual(included, [src])
            self.assertEqual(copied, 1)
            dst = target / "memory/events/2026-10-12/a.json"
            self.assertEqual(dst.read_text(encoding="utf-8"), '{"x":1}')

            included, copied = memory_sync.copy_pending_events(pending, target)
            self.assertEqual(included, [src])
            self.assertEqual(copied, 0)

            dst.write_text('{"x":2}', encoding="utf-8")
            with self.assertRaises(MemoryFabricError):
                memory_sync.copy_pending_events(pending, target)

            empty = root / "empty"
            self.assertEqual(memory_sync.pending_event_files(empty), [])

    def test_cleanup_pending_removes_only_processed_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            pending = Path(tmp) / "pending"
            first = pending / "events/2026-10-12/a.json"
            second = pending / "events/2026-10-12/b.json"
            first.parent.mkdir(parents=True)
            first.write_text("a", encoding="utf-8")
            second.write_text("b", encoding="utf-8")

            memory_sync.cleanup_pending([first], pending)
            self.assertFalse(first.exists())
            self.assertTrue(second.exists())

            memory_sync.cleanup_pending([second], pending)
            self.assertFalse(second.exists())
            self.assertFalse((pending / "events/2026-10-12").exists())

    def _fake_worktree_run(self, cfg, push_rc=0, changed=True):
        def fake_run(args, cwd, check=True):
            if args[:2] == ["worktree", "add"]:
                wt = Path(args[3])
                (wt / "company/config").mkdir(parents=True)
                (wt / "company/config/memory_fabric.json").write_text(json.dumps(cfg), encoding="utf-8")
                return CompletedProcess(args, 0, stdout="", stderr="")
            if args[:2] == ["status", "--porcelain"]:
                stdout = " M memory/catalog.json\n" if changed else ""
                return CompletedProcess(args, 0, stdout=stdout, stderr="")
            if args[:2] == ["rev-parse", "HEAD"]:
                return CompletedProcess(args, 0, stdout="commit123\n", stderr="")
            if args and args[0] == "push":
                return CompletedProcess(
                    args,
                    push_rc,
                    stdout="",
                    stderr="push fail" if push_rc else "",
                )
            return CompletedProcess(args, 0, stdout="", stderr="")

        return fake_run

    def test_sync_once_no_changes_processes_already_remote_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_root = Path(tmp)
            pending_file = fake_root / BASE_CFG["pending_root"] / "events/2026-10-12/a.json"
            pending_file.parent.mkdir(parents=True)
            pending_file.write_text("{}", encoding="utf-8")

            with (
                patch.object(memory_sync, "ROOT", fake_root),
                patch(
                    "tools.memory_sync.run_git",
                    side_effect=self._fake_worktree_run(BASE_CFG, changed=False),
                ),
                patch(
                    "tools.memory_sync.copy_pending_events",
                    return_value=([pending_file], 0),
                ),
                patch(
                    "tools.memory_sync.rebuild_memory",
                    return_value={"conflict_count": 0},
                ),
            ):
                result = memory_sync.sync_once(BASE_CFG, 1)

            self.assertFalse(result["changed"])
            self.assertEqual(result["copied_events"], 0)
            self.assertEqual(result["processed_pending"], [str(pending_file)])

    def test_sync_once_push_success_and_failure(self):
        def run_case(push_rc):
            with tempfile.TemporaryDirectory() as tmp:
                fake_root = Path(tmp)
                pending_file = fake_root / BASE_CFG["pending_root"] / "events/x.json"
                pending_file.parent.mkdir(parents=True)
                pending_file.write_text("{}", encoding="utf-8")
                with (
                    patch.object(memory_sync, "ROOT", fake_root),
                    patch(
                        "tools.memory_sync.run_git",
                        side_effect=self._fake_worktree_run(BASE_CFG, push_rc=push_rc),
                    ),
                    patch(
                        "tools.memory_sync.copy_pending_events",
                        return_value=([pending_file], 1),
                    ),
                    patch(
                        "tools.memory_sync.rebuild_memory",
                        return_value={"conflict_count": 0},
                    ),
                ):
                    return memory_sync.sync_once(BASE_CFG, 1), pending_file

        success, pending = run_case(0)
        self.assertTrue(success["changed"])
        self.assertFalse(success["push_failed"])
        self.assertEqual(success["copied_events"], 1)
        self.assertEqual(success["processed_pending"], [str(pending)])

        failure, _ = run_case(1)
        self.assertTrue(failure["push_failed"])
        self.assertIn("push fail", failure["error"])

    def test_sync_once_rejects_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_root = Path(tmp)
            with (
                patch.object(memory_sync, "ROOT", fake_root),
                patch(
                    "tools.memory_sync.run_git",
                    side_effect=self._fake_worktree_run(BASE_CFG),
                ),
                patch(
                    "tools.memory_sync.copy_pending_events",
                    return_value=([], 0),
                ),
                patch(
                    "tools.memory_sync.rebuild_memory",
                    return_value={"conflict_count": 1},
                ),
            ):
                with self.assertRaises(MemoryFabricError):
                    memory_sync.sync_once(BASE_CFG, 1)

    def test_main_cleans_processed_after_success_and_retries_push_race(self):
        processed = [str(Path(".runtime/memory/pending/events/a.json"))]
        first = {"push_failed": True, "error": "race", "processed_pending": processed}
        second = {
            "changed": True,
            "push_failed": False,
            "processed_pending": processed,
        }
        with (
            patch("tools.memory_sync.load_config", return_value=BASE_CFG),
            patch("tools.memory_sync.acquire_lock", return_value=9),
            patch("tools.memory_sync.release_lock") as release,
            patch("tools.memory_sync.sync_once", side_effect=[first, second]),
            patch("tools.memory_sync.cleanup_pending") as cleanup,
            patch("tools.memory_sync.run_git"),
            patch("tools.memory_sync.time.sleep"),
        ):
            self.assertEqual(memory_sync.main(), 0)
        cleanup.assert_called_once()
        release.assert_called_once()

    def test_main_does_not_cleanup_when_retries_exhaust(self):
        failed = {"push_failed": True, "error": "nope", "processed_pending": ["x"]}
        with (
            patch("tools.memory_sync.load_config", return_value=BASE_CFG),
            patch("tools.memory_sync.acquire_lock", return_value=9),
            patch("tools.memory_sync.release_lock"),
            patch("tools.memory_sync.sync_once", return_value=failed),
            patch("tools.memory_sync.cleanup_pending") as cleanup,
            patch("tools.memory_sync.time.sleep"),
        ):
            self.assertEqual(memory_sync.main(), 2)
        cleanup.assert_not_called()


if __name__ == "__main__":
    unittest.main()
