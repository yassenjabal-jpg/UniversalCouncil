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

        with patch(
            "tools.memory_rebuild.load_config",
            side_effect=MemoryFabricError("bad"),
        ):
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
            patch(
                "tools.memory_preflight.load_config",
                side_effect=MemoryFabricError("bad"),
            ),
        ):
            self.assertEqual(memory_preflight_tool.main(), 2)

    def test_search_main_success_and_error(self):
        cfg = {"local_index": ".runtime/m.sqlite", "search_top_k": 12}
        with (
            patch("sys.argv", ["memory_search.py", "youtube", "--top", "3", "--no-fetch"]),
            patch("tools.memory_search.load_config", return_value=cfg),
            patch("tools.memory_search.memory_preflight") as preflight,
            patch(
                "tools.memory_search.search_index",
                return_value=[{"event_id": "MEM-x"}],
            ) as search,
        ):
            self.assertEqual(memory_search_tool.main(), 0)
            self.assertFalse(preflight.call_args.kwargs["fetch"])
            self.assertEqual(search.call_args.kwargs["top_k"], 3)

        with (
            patch("sys.argv", ["memory_search.py", "youtube"]),
            patch("tools.memory_search.load_config", return_value=cfg),
            patch(
                "tools.memory_search.memory_preflight",
                side_effect=MemoryFabricError("bad"),
            ),
        ):
            self.assertEqual(memory_search_tool.main(), 2)

    def test_write_main_no_sync_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
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
            cfg = {"memory_root": "memory"}
            fake_event = {"event_id": "MEM-test"}
            fake_path = root / "memory/events/x.json"
            fake_path.parent.mkdir(parents=True)
            fake_path.write_text("{}", encoding="utf-8")
            with (
                patch.object(memory_write_tool, "ROOT", root),
                patch("sys.argv", ["memory_write.py", str(spec), "--no-sync"]),
                patch("tools.memory_write.load_config", return_value=cfg),
                patch("tools.memory_write.new_event", return_value=fake_event),
                patch("tools.memory_write.write_event", return_value=fake_path),
                patch(
                    "tools.memory_write.rebuild_memory",
                    return_value={"conflict_count": 0},
                ),
            ):
                self.assertEqual(memory_write_tool.main(), 0)

    def test_write_main_sync_success_and_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = root / "spec.json"
            spec.write_text("{}", encoding="utf-8")
            cfg = {"memory_root": "memory"}
            fake_event = {"event_id": "MEM-test"}
            fake_path = root / "memory/events/x.json"
            fake_path.parent.mkdir(parents=True)
            fake_path.write_text("{}", encoding="utf-8")

            ok_proc = CompletedProcess(["python"], 0, stdout="SYNCED", stderr="")
            with (
                patch.object(memory_write_tool, "ROOT", root),
                patch("sys.argv", ["memory_write.py", str(spec)]),
                patch("tools.memory_write.load_config", return_value=cfg),
                patch("tools.memory_write.new_event", return_value=fake_event),
                patch("tools.memory_write.write_event", return_value=fake_path),
                patch("tools.memory_write.rebuild_memory", return_value={"conflict_count": 0}),
                patch("tools.memory_write.subprocess.run", return_value=ok_proc),
            ):
                self.assertEqual(memory_write_tool.main(), 0)

            bad_proc = CompletedProcess(["python"], 2, stdout="", stderr="sync failed")
            with (
                patch.object(memory_write_tool, "ROOT", root),
                patch("sys.argv", ["memory_write.py", str(spec)]),
                patch("tools.memory_write.load_config", return_value=cfg),
                patch("tools.memory_write.new_event", return_value=fake_event),
                patch("tools.memory_write.write_event", return_value=fake_path),
                patch("tools.memory_write.rebuild_memory", return_value={"conflict_count": 0}),
                patch("tools.memory_write.subprocess.run", return_value=bad_proc),
            ):
                self.assertEqual(memory_write_tool.main(), 2)

    def test_write_main_conflict_rolls_back_and_input_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = root / "spec.json"
            spec.write_text("{}", encoding="utf-8")
            cfg = {"memory_root": "memory"}
            fake_event = {"event_id": "MEM-test"}
            fake_path = root / "memory/events/x.json"
            fake_path.parent.mkdir(parents=True)
            fake_path.write_text("{}", encoding="utf-8")

            with (
                patch.object(memory_write_tool, "ROOT", root),
                patch("sys.argv", ["memory_write.py", str(spec), "--no-sync"]),
                patch("tools.memory_write.load_config", return_value=cfg),
                patch("tools.memory_write.new_event", return_value=fake_event),
                patch("tools.memory_write.write_event", return_value=fake_path),
                patch(
                    "tools.memory_write.rebuild_memory",
                    side_effect=[{"conflict_count": 1}, {"conflict_count": 0}],
                ),
            ):
                self.assertEqual(memory_write_tool.main(), 2)
                self.assertFalse(fake_path.exists())

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


if __name__ == "__main__":
    unittest.main()
