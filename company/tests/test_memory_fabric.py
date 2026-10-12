import copy
import io
import json
import sqlite3
import tarfile
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import MagicMock, patch

from company.runtime.memory_fabric import (
    MemoryFabricError,
    _safe_extract_tar,
    build_catalog,
    build_search_index,
    event_path,
    file_sha256,
    load_config,
    load_events,
    memory_preflight,
    new_event,
    rebuild_memory,
    reduce_events,
    refresh_from_git,
    render_snapshot,
    search_index,
    validate_config,
    validate_event,
    write_event,
)

ROOT = Path(__file__).resolve().parents[2]
BASE_CFG = json.loads((ROOT / "company/config/memory_fabric.json").read_text(encoding="utf-8"))


def make_event(
    event_id="MEM-20261012-120000-abc123",
    *,
    scope="project/demo",
    subject="demo.subject",
    summary="Demo memory",
    supersedes=None,
    level="L3_CANONICAL",
    confidence="verified",
    details=None,
    created_at="2026-10-12T12:00:00+03:00",
):
    return {
        "schema_version": "1.0",
        "event_id": event_id,
        "created_at": created_at,
        "scope": scope,
        "level": level,
        "kind": "decision",
        "subject": subject,
        "summary": summary,
        "details": {"value": "demo"} if details is None else details,
        "supersedes": supersedes or [],
        "confidence": confidence,
        "sensitivity": "normal",
        "tags": ["demo"],
        "source": {"type": "repository", "ref": "test"},
    }


class MemoryFabricTests(unittest.TestCase):
    def test_config_validation_and_loading(self):
        self.assertTrue(validate_config(BASE_CFG))
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "cfg.json"
            p.write_text(json.dumps(BASE_CFG), encoding="utf-8")
            self.assertEqual(load_config(p)["version"], "1.0")
            p.write_text("{", encoding="utf-8")
            with self.assertRaises(MemoryFabricError):
                load_config(p)

        mutations = [
            lambda c: c.__setitem__("version", "2.0"),
            lambda c: c.__setitem__("enabled", False),
            lambda c: c.__setitem__("conflict_policy", "GUESS"),
            lambda c: c.__setitem__("persistence_levels", ["L2_PROJECT"]),
            lambda c: c.__setitem__("event_kinds", ["decision"]),
            lambda c: c["autosync"].__setitem__("enabled", False),
            lambda c: c["autosync"].__setitem__("max_push_retries", 0),
        ]
        for mutate in mutations:
            cfg = copy.deepcopy(BASE_CFG)
            mutate(cfg)
            with self.subTest(cfg=cfg):
                with self.assertRaises(MemoryFabricError):
                    validate_config(cfg)

    def test_event_validation_happy_path_and_owner_directive(self):
        event = make_event()
        self.assertTrue(validate_event(event, BASE_CFG))
        owner = make_event(
            "MEM-20261012-120001-abc124",
            level="L4_OWNER_DIRECTIVE",
            confidence="owner_confirmed",
        )
        self.assertTrue(validate_event(owner, BASE_CFG))

    def test_event_validation_rejects_bad_shapes(self):
        base = make_event()
        variants = []

        missing = copy.deepcopy(base)
        missing.pop("summary")
        variants.append(missing)

        extra = copy.deepcopy(base)
        extra["extra"] = True
        variants.append(extra)

        changes = [
            ("schema_version", "2.0"),
            ("event_id", "bad"),
            ("created_at", "not-a-date"),
            ("created_at", "2026-10-12T12:00:00"),
            ("scope", "bad/scope"),
            ("level", "L9"),
            ("kind", "unknown"),
            ("subject", ""),
            ("subject", "x" * 161),
            ("summary", ""),
            ("summary", "x" * 1201),
            ("details", "bad"),
            ("supersedes", ["MEM-x", "MEM-x"]),
            ("supersedes", ["bad"]),
            ("confidence", "guess"),
            ("sensitivity", "secret"),
            ("tags", ["x", "x"]),
            ("tags", [""]),
            ("source", {"type": "bad"}),
            ("source", {"type": "chat", "bad": "x"}),
        ]
        for key, value in changes:
            item = copy.deepcopy(base)
            item[key] = value
            variants.append(item)

        self_supersede = copy.deepcopy(base)
        self_supersede["supersedes"] = [self_supersede["event_id"]]
        variants.append(self_supersede)

        bad_owner = copy.deepcopy(base)
        bad_owner["level"] = "L4_OWNER_DIRECTIVE"
        bad_owner["confidence"] = "verified"
        variants.append(bad_owner)

        secret = copy.deepcopy(base)
        secret["details"] = {"nested": [{"api_key": "do-not-store"}]}
        variants.append(secret)

        huge_details = copy.deepcopy(base)
        huge_details["details"] = {"blob": "x" * 13000}
        variants.append(huge_details)

        for item in variants:
            with self.subTest(item=item.get("event_id"), change=item):
                with self.assertRaises(MemoryFabricError):
                    validate_event(item, BASE_CFG)

    def test_new_event_write_path_load_and_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            memory = Path(tmp) / "memory"
            fixed = datetime(2026, 10, 12, 15, 0, tzinfo=timezone.utc)
            event = new_event(
                scope="project/demo",
                level="L3_CANONICAL",
                kind="status",
                subject="demo.state",
                summary="Current demo state",
                details={"state": "ready"},
                confidence="verified",
                tags=["demo"],
                source={"type": "tool", "ref": "unit"},
                now=fixed,
                cfg=BASE_CFG,
            )
            self.assertTrue(event["event_id"].startswith("MEM-20261012-150000-"))
            path = write_event(memory, event, BASE_CFG)
            self.assertEqual(path, event_path(memory, event))
            self.assertEqual(len(file_sha256(path)), 64)
            loaded = load_events(memory, BASE_CFG)
            self.assertEqual(loaded[0]["event_id"], event["event_id"])
            with self.assertRaises(MemoryFabricError):
                write_event(memory, event, BASE_CFG)

    def test_load_events_empty_invalid_and_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            memory = Path(tmp) / "memory"
            self.assertEqual(load_events(memory, BASE_CFG), [])
            events = memory / "events/2026-10-12"
            events.mkdir(parents=True)
            bad = events / "bad.json"
            bad.write_text("{", encoding="utf-8")
            with self.assertRaises(MemoryFabricError):
                load_events(memory, BASE_CFG)
            bad.unlink()
            arr = events / "array.json"
            arr.write_text("[]", encoding="utf-8")
            with self.assertRaises(MemoryFabricError):
                load_events(memory, BASE_CFG)
            arr.unlink()

            event = make_event()
            (events / "a.json").write_text(json.dumps(event), encoding="utf-8")
            (events / "b.json").write_text(json.dumps(event), encoding="utf-8")
            with self.assertRaises(MemoryFabricError):
                load_events(memory, BASE_CFG)

    def test_reduction_supersedes_conflicts_and_unknown_target(self):
        old = make_event()
        new = make_event(
            "MEM-20261012-120100-def456",
            summary="Updated",
            supersedes=[old["event_id"]],
            created_at="2026-10-12T12:01:00+03:00",
        )
        reduced = reduce_events([old, new])
        self.assertEqual([x["event_id"] for x in reduced.active], [new["event_id"]])
        self.assertEqual(reduced.superseded, {old["event_id"]})
        self.assertFalse(reduced.conflicts)

        conflict = make_event(
            "MEM-20261012-120200-fed654",
            summary="Competing",
            created_at="2026-10-12T12:02:00+03:00",
        )
        reduced = reduce_events([old, conflict])
        self.assertEqual(len(reduced.conflicts), 1)

        with self.assertRaises(MemoryFabricError):
            reduce_events([old, copy.deepcopy(old)])

        unknown = copy.deepcopy(new)
        unknown["supersedes"] = ["MEM-20261012-000000-zzzzzz"]
        with self.assertRaises(MemoryFabricError):
            reduce_events([old, unknown])

    def test_render_catalog_rebuild_and_stale_snapshot_cleanup(self):
        with tempfile.TemporaryDirectory() as tmp:
            memory = Path(tmp) / "memory"
            event = make_event(details={"alpha": 1, "text": "hello"})
            write_event(memory, event, BASE_CFG)
            stale = memory / "snapshots/stale.md"
            stale.parent.mkdir(parents=True)
            stale.write_text("stale", encoding="utf-8")

            catalog = rebuild_memory(memory, BASE_CFG)
            self.assertEqual(catalog["event_count"], 1)
            self.assertEqual(catalog["active_count"], 1)
            self.assertFalse(stale.exists())
            snapshot = memory / "snapshots/projects/demo.md"
            text = snapshot.read_text(encoding="utf-8")
            self.assertIn("demo.subject", text)
            self.assertIn("hello", text)
            self.assertTrue((memory / "catalog.json").is_file())

            empty = render_snapshot("global", [], [])
            self.assertIn("No active memory events", empty)
            reduced = reduce_events([event])
            direct = build_catalog([event], reduced)
            self.assertEqual(direct["scopes"]["project/demo"][0]["event_id"], event["event_id"])

    def test_rebuild_snapshot_paths_and_minimal_render(self):
        with tempfile.TemporaryDirectory() as tmp:
            memory = Path(tmp) / "memory"
            global_event = make_event(
                "MEM-20261012-120010-aaa111",
                scope="global",
                subject="global.rule",
                details={},
            )
            global_event["tags"] = []
            council_event = make_event(
                "MEM-20261012-120020-bbb222",
                scope="council",
                subject="council.rule",
                created_at="2026-10-12T12:00:20+03:00",
            )
            venture_event = make_event(
                "MEM-20261012-120030-ccc333",
                scope="venture/media",
                subject="venture.rule",
                created_at="2026-10-12T12:00:30+03:00",
            )
            for event in (global_event, council_event, venture_event):
                write_event(memory, event, BASE_CFG)
            rebuild_memory(memory, BASE_CFG)
            self.assertTrue((memory / "snapshots/GLOBAL.md").is_file())
            self.assertTrue((memory / "snapshots/COUNCIL.md").is_file())
            self.assertTrue((memory / "snapshots/ventures/media.md").is_file())
            text = (memory / "snapshots/GLOBAL.md").read_text(encoding="utf-8")
            self.assertNotIn("Details:", text)
            self.assertNotIn("Tags:", text)

    def test_render_marks_conflict_and_supersedes_and_tags(self):
        one = make_event()
        two = make_event(
            "MEM-20261012-120100-def456",
            summary="Other",
            created_at="2026-10-12T12:01:00+03:00",
        )
        reduced = reduce_events([one, two])
        text = render_snapshot("project/demo", reduced.active, reduced.conflicts)
        self.assertIn("CONFLICT", text)
        self.assertIn("demo", text)

        newer = make_event(
            "MEM-20261012-120200-fed654",
            summary="New",
            supersedes=[one["event_id"]],
            created_at="2026-10-12T12:02:00+03:00",
        )
        text = render_snapshot("project/demo", [newer], [])
        self.assertIn("Supersedes", text)

    def test_build_search_index_wraps_sqlite_operational_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            memory = root / "memory"
            write_event(memory, make_event(), BASE_CFG)
            conn = MagicMock()
            conn.execute.side_effect = sqlite3.OperationalError("fts unavailable")
            with patch("company.runtime.memory_fabric.sqlite3.connect", return_value=conn):
                with self.assertRaises(MemoryFabricError):
                    build_search_index(memory, root / "bad.sqlite", BASE_CFG)
            conn.close.assert_called_once()

    def test_search_index_and_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            memory = root / "memory"
            write_event(
                memory,
                make_event(summary="YouTube channel strategy", details={"market": "Arabic"}),
                BASE_CFG,
            )
            db = build_search_index(memory, root / "memory.sqlite", BASE_CFG)
            rows = search_index(db, "YouTube", 5)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["subject"], "demo.subject")

            dotted = search_index(db, "demo.subject", 5)
            self.assertEqual(len(dotted), 1)
            self.assertEqual(dotted[0]["subject"], "demo.subject")

            punctuated = search_index(db, "YouTube/Arabic", 5)
            self.assertEqual(len(punctuated), 1)

            with self.assertRaises(MemoryFabricError):
                search_index(db, "")
            with self.assertRaises(MemoryFabricError):
                search_index(root / "missing.sqlite", "x")
            with self.assertRaises(MemoryFabricError):
                search_index(db, '"')

    def test_safe_tar_extract_and_traversal_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            good_buf = io.BytesIO()
            with tarfile.open(fileobj=good_buf, mode="w") as tar:
                data = b"{}"
                info = tarfile.TarInfo("memory/catalog.json")
                info.size = len(data)
                tar.addfile(info, io.BytesIO(data))
            _safe_extract_tar(good_buf.getvalue(), root / "good")
            self.assertTrue((root / "good/memory/catalog.json").is_file())

            bad_buf = io.BytesIO()
            with tarfile.open(fileobj=bad_buf, mode="w") as tar:
                data = b"x"
                info = tarfile.TarInfo("../escape.txt")
                info.size = 1
                tar.addfile(info, io.BytesIO(data))
            with self.assertRaises(MemoryFabricError):
                _safe_extract_tar(bad_buf.getvalue(), root / "bad")

    def test_refresh_from_git_failure_paths_and_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            cache = root / "cache"
            repo.mkdir()

            fail = CompletedProcess(["git"], 1, stdout="", stderr="fail")
            with patch("company.runtime.memory_fabric.subprocess.run", return_value=fail):
                with self.assertRaises(MemoryFabricError):
                    refresh_from_git(repo, cache)

            ok_fetch = CompletedProcess(["git"], 0, stdout="", stderr="")
            bad_sha = CompletedProcess(["git"], 1, stdout="", stderr="sha")
            with patch(
                "company.runtime.memory_fabric.subprocess.run",
                side_effect=[ok_fetch, bad_sha],
            ):
                with self.assertRaises(MemoryFabricError):
                    refresh_from_git(repo, cache)

            ok_sha = CompletedProcess(["git"], 0, stdout="abc123\n", stderr="")
            bad_archive = CompletedProcess(["git"], 1, stdout=b"", stderr=b"archive")
            with patch(
                "company.runtime.memory_fabric.subprocess.run",
                side_effect=[ok_fetch, ok_sha, bad_archive],
            ):
                with self.assertRaises(MemoryFabricError):
                    refresh_from_git(repo, cache)

            buf = io.BytesIO()
            with tarfile.open(fileobj=buf, mode="w") as tar:
                payload = b"# memory"
                info = tarfile.TarInfo("memory/README.md")
                info.size = len(payload)
                tar.addfile(info, io.BytesIO(payload))
            good_archive = CompletedProcess(["git"], 0, stdout=buf.getvalue(), stderr=b"")
            cache.mkdir()
            (cache / "old.txt").write_text("old", encoding="utf-8")
            (cache / "empty-dir").mkdir()
            with patch(
                "company.runtime.memory_fabric.subprocess.run",
                side_effect=[ok_fetch, ok_sha, good_archive],
            ):
                result = refresh_from_git(repo, cache)
            self.assertEqual(result, "abc123")
            self.assertFalse((cache / "old.txt").exists())
            self.assertTrue((cache / "memory/README.md").exists())

    def test_memory_preflight_local_success_conflict_and_fetch_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            memory = root / "memory"
            cfg = copy.deepcopy(BASE_CFG)
            cfg["memory_root"] = "memory"
            cfg["local_index"] = ".runtime/memory.sqlite"
            cfg["cache_root"] = ".runtime/cache"

            write_event(memory, make_event(), cfg)
            result = memory_preflight(root, cfg, fetch=False)
            self.assertEqual(result["active_count"], 1)
            self.assertEqual(result["conflict_count"], 0)
            self.assertTrue((root / cfg["local_index"]).is_file())

            write_event(
                memory,
                make_event(
                    "MEM-20261012-120100-def456",
                    summary="conflict",
                    created_at="2026-10-12T12:01:00+03:00",
                ),
                cfg,
            )
            with self.assertRaises(MemoryFabricError):
                memory_preflight(root, cfg, fetch=False)

            cache_memory = root / cfg["cache_root"] / "memory"
            for path in list((root / cfg["cache_root"]).rglob("*"))[::-1]:
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    path.rmdir()
            write_event(cache_memory, make_event(), cfg)
            with patch(
                "company.runtime.memory_fabric.refresh_from_git",
                return_value="remote-sha",
            ):
                fetched = memory_preflight(root, cfg, fetch=True)
            self.assertEqual(fetched["source_sha"], "remote-sha")


if __name__ == "__main__":
    unittest.main()
