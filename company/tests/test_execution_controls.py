import json
import tempfile
import unittest
from pathlib import Path

from company.runtime.execution_controls import (
    ExecutionControlError,
    ExecutionJournal,
    HostControllerLease,
)


class ExecutionControlsTests(unittest.TestCase):
    def test_controller_lease_acquire_reentrant_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lease.json"
            lease = HostControllerLease(path, ttl_seconds=30)
            lease.acquire("desktop:YASSIN", "operator")
            self.assertTrue(path.exists())
            lease.acquire("desktop:YASSIN", "operator")
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["resource"], "desktop:YASSIN")
            self.assertEqual(payload["holder"], "operator")
            lease.release("desktop:YASSIN", "operator")
            self.assertFalse(path.exists())
            lease.release("desktop:YASSIN", "operator")

    def test_controller_lease_rejects_missing_identity_and_conflicts(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lease.json"
            lease = HostControllerLease(path)
            with self.assertRaises(ExecutionControlError):
                lease.acquire("", "operator")
            with self.assertRaises(ExecutionControlError):
                lease.acquire("desktop:YASSIN", "")
            lease.acquire("desktop:YASSIN", "one")
            other = HostControllerLease(path)
            with self.assertRaises(ExecutionControlError):
                other.acquire("desktop:YASSIN", "two")
            with self.assertRaises(ExecutionControlError):
                lease.release("desktop:YASSIN", "two")
            lease.release("desktop:YASSIN", "one")

    def test_controller_lease_replaces_stale_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lease.json"
            path.write_text(
                json.dumps(
                    {
                        "resource": "desktop:YASSIN",
                        "holder": "stale",
                        "acquired_at": "2000-01-01T00:00:00+00:00",
                        "pid": 1,
                    }
                ),
                encoding="utf-8",
            )
            lease = HostControllerLease(path, ttl_seconds=10)
            lease.acquire("desktop:YASSIN", "fresh")
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["holder"], "fresh")
            lease.release("desktop:YASSIN", "fresh")

    def test_controller_lease_rejects_corrupt_or_naive_timestamps(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lease.json"
            path.write_text("not-json", encoding="utf-8")
            with self.assertRaises(ExecutionControlError):
                HostControllerLease(path).acquire("desktop:YASSIN", "one")

            path.write_text(
                json.dumps(
                    {
                        "resource": "desktop:YASSIN",
                        "holder": "old",
                        "acquired_at": "not-a-time",
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(ExecutionControlError):
                HostControllerLease(path).acquire("desktop:YASSIN", "two")

            path.write_text(
                json.dumps(
                    {
                        "resource": "desktop:YASSIN",
                        "holder": "old",
                        "acquired_at": "2000-01-01T00:00:00",
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(ExecutionControlError):
                HostControllerLease(path).acquire("desktop:YASSIN", "two")

    def test_execution_journal_tracks_pending_and_reconciliation(self):
        with tempfile.TemporaryDirectory() as tmp:
            journal = ExecutionJournal(Path(tmp) / "events.jsonl")
            self.assertEqual(journal.pending_action_ids(), set())
            journal.record_intent(
                task_id="task",
                action_id="a1",
                requester="operator",
                path="gui_semantic_uia",
                risk="T2_LOCAL_STATE_CHANGE",
                authority_operation="desktop_computer_use.control",
            )
            self.assertEqual(journal.pending_action_ids(), {"a1"})
            journal.reconcile(task_id="task", action_id="a1", state="UNKNOWN")
            self.assertEqual(journal.pending_action_ids(), set())
            with self.assertRaises(ExecutionControlError):
                journal.reconcile(task_id="task", action_id="a1", state="FAILED")

    def test_execution_journal_result_clears_intent(self):
        with tempfile.TemporaryDirectory() as tmp:
            journal = ExecutionJournal(Path(tmp) / "events.jsonl")
            journal.record_intent(
                task_id="task",
                action_id="a1",
                requester="operator",
                path="dc_control_plane",
                risk="T0_OBSERVE",
                authority_operation="remote_shell.read",
            )
            journal.record_result(task_id="task", action_id="a1", state="HOST_DISPATCH_REQUIRED")
            self.assertEqual(journal.pending_action_ids(), set())

    def test_execution_journal_rejects_corrupt_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            path.write_text("not-json\n", encoding="utf-8")
            with self.assertRaises(ExecutionControlError):
                ExecutionJournal(path).pending_action_ids()


if __name__ == "__main__":
    unittest.main()
