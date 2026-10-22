import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "projection_under_test", REPO / "tools/build_command_center_murtakaz_projection.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ProvenanceChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="murtakaz-provenance-test-")
        self.root = Path(self.temp.name)
        for relative in module.SOURCES:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((REPO / relative).read_bytes())
        self.git("init", "-q")
        self.git("config", "user.name", "Local Test")
        self.git("config", "user.email", "local-test@example.invalid")
        self.git("config", "core.autocrlf", "false")
        self.git("add", ".")
        self.git("commit", "-qm", "fixture baseline")
        self.baseline = self.git("rev-parse", "HEAD")
        self.original_root = module.ROOT
        module.ROOT = self.root

    def tearDown(self):
        module.ROOT = self.original_root
        self.temp.cleanup()

    def git(self, *command):
        return subprocess.check_output(["git", *command], cwd=self.root, text=True).strip()

    def mutate(self):
        path = self.root / module.SOURCES[0]
        data = json.loads(path.read_bytes())
        data["test_only_changed_field"] = "changed"
        path.write_text(json.dumps(data), encoding="utf-8")

    def test_clean_data_and_source_hashes_share_exact_commit(self):
        projection = module.build()
        for source in projection["source_files"]:
            expected = self.git("rev-parse", f"{self.baseline}:{source['path']}")
            self.assertEqual(expected, source["blob_sha"])
        self.assertEqual("al-murtakaz", projection["identity"]["id"])
        self.assertFalse(projection["authority"]["execution_authority"])
        self.assertFalse(projection["authority"]["stage8_opened"])

    def test_dirty_governing_source_is_rejected(self):
        self.mutate()
        with self.assertRaisesRegex(SystemExit, "uncommitted governing sources"):
            module.build()

    def test_staged_governing_source_is_rejected(self):
        self.mutate()
        self.git("add", module.SOURCES[0])
        with self.assertRaisesRegex(SystemExit, "uncommitted governing sources"):
            module.build()

    def test_staged_drift_with_restored_worktree_is_rejected(self):
        original = (self.root / module.SOURCES[0]).read_bytes()
        self.mutate()
        self.git("add", module.SOURCES[0])
        (self.root / module.SOURCES[0]).write_bytes(original)
        self.assertTrue(self.git("diff", "--cached", "--name-only"))
        with self.assertRaisesRegex(SystemExit, "uncommitted governing sources"):
            module.build()

    def test_unrelated_staged_work_is_allowed(self):
        (self.root / "unrelated.txt").write_text("unrelated", encoding="utf-8")
        self.git("add", "unrelated.txt")
        self.assertEqual("NO_LIVE_TASK", module.build()["runtime"]["task_state"])

    def test_unrelated_work_does_not_block_projection(self):
        (self.root / "unrelated.txt").write_text("unrelated", encoding="utf-8")
        self.assertEqual("NO_LIVE_TASK", module.build()["runtime"]["task_state"])

    def test_projection_reads_one_captured_commit_when_head_moves(self):
        original = subprocess.check_output
        moved = False

        def intercepted(command, *positional, **keyword):
            nonlocal moved
            if command[:3] == ["git", "cat-file", "blob"] and not moved:
                moved = True
                self.mutate()
                self.git("add", module.SOURCES[0])
                self.git("commit", "-qm", "move head during snapshot")
            return original(command, *positional, **keyword)

        with patch.object(subprocess, "check_output", side_effect=intercepted):
            projection = module.build()
        self.assertNotEqual(self.baseline, self.git("rev-parse", "HEAD"))
        for source in projection["source_files"]:
            self.assertEqual(self.git("rev-parse", f"{self.baseline}:{source['path']}"), source["blob_sha"])

    def test_missing_tracked_governing_source_is_rejected(self):
        (self.root / module.SOURCES[0]).unlink()
        with self.assertRaisesRegex(SystemExit, "uncommitted governing sources"):
            module.build()

    def test_invalid_committed_json_is_rejected(self):
        (self.root / module.SOURCES[0]).write_text("{invalid", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-qm", "invalid fixture")
        with self.assertRaises(json.JSONDecodeError):
            module.build()

    def test_failed_check_does_not_overwrite_projection(self):
        target = self.root / "projection.json"
        target.write_text("sentinel", encoding="utf-8")
        self.mutate()
        with patch.object(module, "OUTPUT", target), self.assertRaises(SystemExit):
            module.main()
        self.assertEqual("sentinel", target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(argv=["Test-Murtakaz-Provenance.py"], verbosity=2)
