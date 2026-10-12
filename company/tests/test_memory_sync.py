import json
import tempfile
import unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

import tools.memory_sync as memory_sync
from company.runtime.memory_fabric import MemoryFabricError


class MemorySyncTests(unittest.TestCase):
    def test_run_git_success_and_failure(self):
        ok = CompletedProcess(["git"], 0, stdout="ok", stderr="")
        with patch("tools.memory_sync.subprocess.run", return_value=ok):
            self.assertEqual(memory_sync.run_git(["status"], Path(".")), ok)

        fail = CompletedProcess(["git"], 1, stdout="", stderr="bad")
        with patch("tools.memory_sync.subprocess.run", return_value=fail):
            with self.assertRaises(MemoryFabricError):
                memory_sync.run_git(["status"], Path("."))
            self.assertEqual(
                memory_sync.run_git(["status"], Path("."), check=False).returncode,
                1,
            )

    def test_lock_lifecycle_and_duplicate_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            lock = Path(tmp) / "sync.lock"
            fd = memory_sync.acquire_lock(lock)
            self.assertTrue(lock.exists())
            with self.assertRaises(MemoryFabricError):
                memory_sync.acquire_lock(lock)
            memory_sync.release_lock(fd, lock)
            self.assertFalse(lock.exists())

    def test_copy_local_events_new_same_and_immutability_violation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            target = root / "target"
            event = source / "memory/events/2026-10-12/a.json"
            event.parent.mkdir(parents=True)
            event.write_text('{"x":1}', encoding="utf-8")

            self.assertEqual(memory_sync.copy_local_events(source, target), 1)
            copied = target / "memory/events/2026-10-12/a.json"
            self.assertEqual(copied.read_text(encoding="utf-8"), '{"x":1}')
            self.assertEqual(memory_sync.copy_local_events(source, target), 0)

            copied.write_text('{"x":2}', encoding="utf-8")
            with self.assertRaises(MemoryFabricError):
                memory_sync.copy_local_events(source, target)

    def test_copy_local_events_no_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(
                memory_sync.copy_local_events(root / "source", root / "target"),
                0,
            )

    def test_remove_worktree_calls_git_and_cleans_residual(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wt"
            path.mkdir()
            (path / "x").write_text("x", encoding="utf-8")
            with patch("tools.memory_sync.run_git") as run:
                memory_sync.remove_worktree(path)
            run.assert_called_once()
            self.assertFalse(path.exists())

    def test_sync_once_no_changes(self):
        cfg = {
            "autosync": {"remote": "origin", "branch": "main"},
        }
        with tempfile.TemporaryDirectory() as tmp:
            fake_root = Path(tmp)
            worktree_cfg = {
                "version": "1.0",
                "enabled": True,
                "canonical_remote": "origin/main",
                "memory_root": "memory",
                "local_index": ".runtime/m.sqlite",
                "cache_root": ".runtime/cache",
                "autosync": {"enabled": True, "remote": "origin", "branch": "main", "max_push_retries": 3},
                "persistence_levels": ["L2_PROJECT", "L3_CANONICAL", "L4_OWNER_DIRECTIVE"],
                "event_kinds": [
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
                ],
                "confidence_levels": ["owner_confirmed", "verified", "evidence_backed", "proposal"],
                "allowed_sensitivity": ["normal", "private_non_sensitive"],
                "max_summary_chars": 1200,
                "max_details_chars": 12000,
                "search_top_k": 12,
                "conflict_policy": "FAIL_PREFLIGHT",
            }

            def fake_run(args, cwd, check=True):
                if args[:2] == ["worktree", "add"]:
                    wt = Path(args[3])
                    (wt / "company/config").mkdir(parents=True)
                    (wt / "company/config/memory_fabric.json").write_text(json.dumps(worktree_cfg), encoding="utf-8")
                    (wt / "memory/events").mkdir(parents=True)
                    return CompletedProcess(args, 0, stdout="", stderr="")
                if args[:2] == ["status", "--porcelain"]:
                    return CompletedProcess(args, 0, stdout="", stderr="")
                if args[:2] == ["rev-parse", "HEAD"]:
                    return CompletedProcess(args, 0, stdout="abc\n", stderr="")
                return CompletedProcess(args, 0, stdout="", stderr="")

            with (
                patch.object(memory_sync, "ROOT", fake_root),
                patch("tools.memory_sync.run_git", side_effect=fake_run),
                patch("tools.memory_sync.copy_local_events", return_value=0),
                patch("tools.memory_sync.rebuild_memory", return_value={"conflict_count": 0}),
            ):
                result = memory_sync.sync_once(cfg, 1)
            self.assertFalse(result["changed"])
            self.assertEqual(result["remote_head"], "abc")

    def test_sync_once_commit_push_success_and_failure(self):
        cfg = {"autosync": {"remote": "origin", "branch": "main"}}

        def run_case(push_rc):
            with tempfile.TemporaryDirectory() as tmp:
                fake_root = Path(tmp)
                wt_cfg = {
                    "version": "1.0",
                    "enabled": True,
                    "canonical_remote": "origin/main",
                    "memory_root": "memory",
                    "local_index": ".runtime/m.sqlite",
                    "cache_root": ".runtime/cache",
                    "autosync": {"enabled": True, "remote": "origin", "branch": "main", "max_push_retries": 3},
                    "persistence_levels": ["L2_PROJECT", "L3_CANONICAL", "L4_OWNER_DIRECTIVE"],
                    "event_kinds": [
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
                    ],
                    "confidence_levels": ["owner_confirmed", "verified", "evidence_backed", "proposal"],
                    "allowed_sensitivity": ["normal", "private_non_sensitive"],
                    "max_summary_chars": 1200,
                    "max_details_chars": 12000,
                    "search_top_k": 12,
                    "conflict_policy": "FAIL_PREFLIGHT",
                }

                def fake_run(args, cwd, check=True):
                    if args[:2] == ["worktree", "add"]:
                        wt = Path(args[3])
                        (wt / "company/config").mkdir(parents=True)
                        (wt / "company/config/memory_fabric.json").write_text(json.dumps(wt_cfg), encoding="utf-8")
                        return CompletedProcess(args, 0, stdout="", stderr="")
                    if args[:2] == ["status", "--porcelain"]:
                        return CompletedProcess(args, 0, stdout=" M memory/catalog.json\n", stderr="")
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

                with (
                    patch.object(memory_sync, "ROOT", fake_root),
                    patch("tools.memory_sync.run_git", side_effect=fake_run),
                    patch("tools.memory_sync.copy_local_events", return_value=2),
                    patch("tools.memory_sync.rebuild_memory", return_value={"conflict_count": 0}),
                ):
                    return memory_sync.sync_once(cfg, 1)

        success = run_case(0)
        self.assertTrue(success["changed"])
        self.assertFalse(success["push_failed"])
        self.assertEqual(success["copied_events"], 2)

        failure = run_case(1)
        self.assertTrue(failure["push_failed"])
        self.assertIn("push fail", failure["error"])

    def test_sync_once_rejects_conflict(self):
        cfg = {"autosync": {"remote": "origin", "branch": "main"}}
        with tempfile.TemporaryDirectory() as tmp:
            fake_root = Path(tmp)

            def fake_run(args, cwd, check=True):
                if args[:2] == ["worktree", "add"]:
                    worktree = Path(args[3])
                    (worktree / "company/config").mkdir(parents=True)
                    source_cfg = Path(__file__).resolve().parents[2] / "company/config/memory_fabric.json"
                    (worktree / "company/config/memory_fabric.json").write_bytes(source_cfg.read_bytes())
                return CompletedProcess(args, 0, stdout="", stderr="")

            with (
                patch.object(memory_sync, "ROOT", fake_root),
                patch("tools.memory_sync.run_git", side_effect=fake_run),
                patch("tools.memory_sync.copy_local_events", return_value=1),
                patch("tools.memory_sync.rebuild_memory", return_value={"conflict_count": 1}),
            ):
                with self.assertRaises(MemoryFabricError):
                    memory_sync.sync_once(cfg, 1)

    def test_main_success_retry_and_exhaustion(self):
        cfg = {
            "autosync": {
                "enabled": True,
                "remote": "origin",
                "branch": "main",
                "max_push_retries": 2,
            }
        }
        with tempfile.TemporaryDirectory() as tmp:
            fake_root = Path(tmp)
            config = fake_root / "company/config/memory_fabric.json"
            config.parent.mkdir(parents=True)
            config.write_text("{}", encoding="utf-8")

            with (
                patch.object(memory_sync, "ROOT", fake_root),
                patch.object(memory_sync, "CONFIG", config),
                patch("tools.memory_sync.load_config", return_value=cfg),
                patch("tools.memory_sync.sync_once", return_value={"changed": False}),
                patch("tools.memory_sync.run_git"),
                patch("sys.argv", ["memory_sync.py"]),
            ):
                self.assertEqual(memory_sync.main(), 0)

            with (
                patch.object(memory_sync, "ROOT", fake_root),
                patch.object(memory_sync, "CONFIG", config),
                patch("tools.memory_sync.load_config", return_value=cfg),
                patch(
                    "tools.memory_sync.sync_once",
                    side_effect=[
                        {"push_failed": True, "error": "race"},
                        {"changed": True, "push_failed": False},
                    ],
                ),
                patch("tools.memory_sync.run_git"),
                patch("tools.memory_sync.time.sleep"),
                patch("sys.argv", ["memory_sync.py"]),
            ):
                self.assertEqual(memory_sync.main(), 0)

            with (
                patch.object(memory_sync, "ROOT", fake_root),
                patch.object(memory_sync, "CONFIG", config),
                patch("tools.memory_sync.load_config", return_value=cfg),
                patch(
                    "tools.memory_sync.sync_once",
                    return_value={"push_failed": True, "error": "nope"},
                ),
                patch("tools.memory_sync.time.sleep"),
                patch("sys.argv", ["memory_sync.py"]),
            ):
                self.assertEqual(memory_sync.main(), 2)


if __name__ == "__main__":
    unittest.main()
