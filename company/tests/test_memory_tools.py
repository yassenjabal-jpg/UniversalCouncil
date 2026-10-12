import json
import tempfile
import unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

import tools.memory_preflight as memory_preflight_tool
import tools.memory_rebuild as memory_rebuild_tool
import tools.memory_search as memory_search_tool
import tools.memory_write as memory_write_tool
from company.runtime.memory_fabric import MemoryFabricError

ROOT = Path(__file__).resolve().parents[2]
BASE_CFG = json.loads((ROOT / "company/config/memory_fabric.json").read_text(encoding="utf-8"))


class MemoryToolTests(unittest.TestCase):
    def test_rebuild_main_success_conflict_and_error(self):
        with (
            patch("tools.memory_rebuild.load_config", return_value={"memory_root": "memory"}),
            patch(
                "tools.memory_rebuild.rebuild_memory",
                return_value={"conflict_count": 0, "event_count": 1},
            ),
        ):
            self.assertEqual(memory_rebuild_tool.main(), 0)

        with (
            patch("tools.memory_rebuild.load_config", return_value={"memory_root": "memory"}),
            patch(
                "tools.memory_rebuild.rebuild_memory",
                return_value={"conflict_count": 1, "event_count": 2},
            ),
        ):
            self.assertEqual(memory_rebuild_tool.main(), 3)

        with patch("tools.memory_rebuild.load_config", side_effect=MemoryFabricError("bad")):
            self.assertEqual(memory_rebuild_tool.main(), 2)

    def test_preflight_main_success_local_and_error(self):
        cfg = {"memory_root": "memory"}
        with (
            patch("sys.argv", ["memory_preflight.py", "--no-fetch"]),
            patch("tools.memory_preflight.load_config", return_value=cfg),
            patch(
                "tools.memory_preflight.memory_preflight",
                return_value={"event_count": 1},
            ) as preflight,
        ):
            self.assertEqual(memory_preflight_tool.main(), 0)
            self.assertFalse(preflight.call_args.kwargs["fetch"])

        with (
            patch("sys.argv", ["memory_preflight.py"]),
            patch("tools.memory_preflight.load_config", return_value=cfg),
            patch(
                "tools.memory_preflight.memory_preflight",
                return_value={"event_count": 1},
            ) as preflight,
        ):
            self.assertEqual(memory_preflight_tool.main(), 0)
            self.assertTrue(preflight.call_args.kwargs["fetch"])

        with (
            patch("sys.argv", ["memory_preflight.py"]),
            patch("tools.memory_preflight.load_config", side_effect=MemoryFabricError("bad")),
        ):
            self.assertEqual(memory_preflight_tool.main(), 2)

    def test_search_main_success_and_error(self):
        cfg = {"local_index": ".runtime/m.sqlite", "search_top_k": 12}
        with (
            patch("sys.argv", ["memory_search.py", "youtube", "--top", "3", "--no-fetch"]),
            patch("tools.memory_search.load_config", return_value=cfg),
            patch("tools.memory_search.memory_preflight") as preflight,
            patch("tools.memory_search.search_index", return_value=[{"event_id": "MEM-x"}]) as search,
        ):
            self.assertEqual(memory_search_tool.main(), 0)
            self.assertFalse(preflight.call_args.kwargs["fetch"])
            self.assertEqual(search.call_args.kwargs["top_k"], 3)

        with (
            patch("sys.argv", ["memory_search.py", "youtube"]),
            patch("tools.memory_search.load_config", return_value=cfg),
            patch("tools.memory_search.memory_preflight", side_effect=MemoryFabricError("bad")),
        ):
            self.assertEqual(memory_search_tool.main(), 2)

    def test_validate_against_canonical_and_pending_passes_and_rejects_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = dict(BASE_CFG)
            cfg["cache_root"] = ".runtime/cache"
            cfg["pending_root"] = ".runtime/pending"
            canonical = root / cfg["cache_root"] / "memory"
            pending = root / cfg["pending_root"]
            (canonical / "events").mkdir(parents=True)
            (pending / "events").mkdir(parents=True)

            event = {
                "event_id": "MEM-new",
                "scope": "project/demo",
                "subject": "demo.state",
                "supersedes": [],
            }
            with (
                patch.object(memory_write_tool, "ROOT", root),
                patch("tools.memory_write.memory_preflight"),
                patch("tools.memory_write.load_events", side_effect=[[], []]),
                patch(
                    "tools.memory_write.reduce_events",
                    return_value=type("R", (), {"conflicts": []})(),
                ),
            ):
                memory_write_tool._validate_against_canonical_and_pending(cfg, event)

            conflict = type(
                "C",
                (),
                {
                    "scope": "project/demo",
                    "subject": "demo.state",
                    "event_ids": ("MEM-a", "MEM-b"),
                },
            )()
            with (
                patch.object(memory_write_tool, "ROOT", root),
                patch("tools.memory_write.memory_preflight"),
                patch("tools.memory_write.load_events", side_effect=[[], []]),
                patch(
                    "tools.memory_write.reduce_events",
                    return_value=type("R", (), {"conflicts": [conflict]})(),
                ),
            ):
                with self.assertRaises(MemoryFabricError):
                    memory_write_tool._validate_against_canonical_and_pending(cfg, event)

    def _write_case(self, *, no_sync=False, sync_rc=0):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        spec = root / "spec.json"
        spec.write_text(
            json.dumps(
                {
                    "scope": "project/demo",
                    "level": "L3_CANONICAL",
                    "kind": "status",
                    "subject": "demo.state",
                    "summary": "Ready",
                    "confidence": "verified",
                    "source": {"type": "tool"},
                }
            ),
            encoding="utf-8",
        )
        cfg = dict(BASE_CFG)
        cfg["pending_root"] = ".runtime/pending"
        fake_event = {
            "event_id": "MEM-test",
            "created_at": "2026-10-12T12:00:00+03:00",
        }
        pending_path = root / cfg["pending_root"] / "events/2026-10-12/MEM-test.json"
        pending_path.parent.mkdir(parents=True)
        pending_path.write_text("{}", encoding="utf-8")
        argv = ["memory_write.py", str(spec)]
        if no_sync:
            argv.append("--no-sync")
        proc = CompletedProcess(
            ["python"],
            sync_rc,
            stdout="SYNCED" if sync_rc == 0 else "",
            stderr="sync failed" if sync_rc else "",
        )
        return temp, root, spec, cfg, fake_event, pending_path, argv, proc

    def test_write_main_no_sync_queues_without_touching_canonical_tree(self):
        temp, root, _, cfg, fake_event, pending_path, argv, _ = self._write_case(no_sync=True)
        with temp:
            with (
                patch.object(memory_write_tool, "ROOT", root),
                patch("sys.argv", argv),
                patch("tools.memory_write.load_config", return_value=cfg),
                patch("tools.memory_write.new_event", return_value=fake_event),
                patch("tools.memory_write._validate_against_canonical_and_pending"),
                patch("tools.memory_write.write_event", return_value=pending_path),
            ):
                self.assertEqual(memory_write_tool.main(), 0)
            self.assertFalse((root / "memory/events").exists())

    def test_write_main_sync_success_and_failure_keeps_failed_event_queued(self):
        temp, root, _, cfg, fake_event, pending_path, argv, ok_proc = self._write_case()
        with temp:
            with (
                patch.object(memory_write_tool, "ROOT", root),
                patch("sys.argv", argv),
                patch("tools.memory_write.load_config", return_value=cfg),
                patch("tools.memory_write.new_event", return_value=fake_event),
                patch("tools.memory_write._validate_against_canonical_and_pending"),
                patch("tools.memory_write.write_event", return_value=pending_path),
                patch("tools.memory_write.subprocess.run", return_value=ok_proc),
            ):
                self.assertEqual(memory_write_tool.main(), 0)

        temp, root, _, cfg, fake_event, pending_path, argv, bad_proc = self._write_case(sync_rc=2)
        with temp:
            with (
                patch.object(memory_write_tool, "ROOT", root),
                patch("sys.argv", argv),
                patch("tools.memory_write.load_config", return_value=cfg),
                patch("tools.memory_write.new_event", return_value=fake_event),
                patch("tools.memory_write._validate_against_canonical_and_pending"),
                patch("tools.memory_write.write_event", return_value=pending_path),
                patch("tools.memory_write.subprocess.run", return_value=bad_proc),
            ):
                self.assertEqual(memory_write_tool.main(), 2)
            self.assertTrue(pending_path.exists())

    def test_write_main_input_and_validation_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = root / "spec.json"
            cfg = dict(BASE_CFG)

            spec.write_text("[]", encoding="utf-8")
            with (
                patch.object(memory_write_tool, "ROOT", root),
                patch("sys.argv", ["memory_write.py", str(spec), "--no-sync"]),
                patch("tools.memory_write.load_config", return_value=cfg),
            ):
                self.assertEqual(memory_write_tool.main(), 2)

            spec.write_text("{", encoding="utf-8")
            with (
                patch.object(memory_write_tool, "ROOT", root),
                patch("sys.argv", ["memory_write.py", str(spec), "--no-sync"]),
                patch("tools.memory_write.load_config", return_value=cfg),
            ):
                self.assertEqual(memory_write_tool.main(), 2)

            spec.write_text("{}", encoding="utf-8")
            with (
                patch.object(memory_write_tool, "ROOT", root),
                patch("sys.argv", ["memory_write.py", str(spec), "--no-sync"]),
                patch("tools.memory_write.load_config", return_value=cfg),
                patch(
                    "tools.memory_write.new_event",
                    side_effect=MemoryFabricError("bad event"),
                ),
            ):
                self.assertEqual(memory_write_tool.main(), 2)


if __name__ == "__main__":
    unittest.main()
