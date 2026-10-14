import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from company.runtime.execution_controls import (
    ExecutionControlError,
    ExecutionJournal,
    HostControllerLease,
    LeaseToken,
)


class ExecutionControlsTests(unittest.TestCase):
    def test_controller_lease_acquire_reentrant_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lease.json"
            lease = HostControllerLease(path, ttl_seconds=30)
            first = lease.acquire(
                "desktop:YASSIN",
                "operator",
                host="YASSIN",
                session_id="task-1",
            )
            self.assertTrue(path.exists())
            second = lease.acquire(
                "desktop:YASSIN",
                "operator",
                host="YASSIN",
                session_id="task-1",
            )
            self.assertEqual(first, second)
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["resource"], "desktop:YASSIN")
            self.assertEqual(payload["holder"], "operator")
            self.assertEqual(payload["host"], "YASSIN")
            self.assertEqual(payload["session_id"], "task-1")
            lease.release(first)
            self.assertFalse(path.exists())
            lease.release(first)

    def test_controller_lease_rejects_missing_identity_and_conflicts(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lease.json"
            lease = HostControllerLease(path)
            for kwargs in (
                {"resource": "", "holder": "operator", "host": "YASSIN", "session_id": "task"},
                {"resource": "desktop:YASSIN", "holder": "", "host": "YASSIN", "session_id": "task"},
                {"resource": "desktop:YASSIN", "holder": "operator", "host": "", "session_id": "task"},
                {"resource": "desktop:YASSIN", "holder": "operator", "host": "YASSIN", "session_id": ""},
            ):
                with self.subTest(kwargs=kwargs):
                    with self.assertRaises(ExecutionControlError):
                        lease.acquire(**kwargs)

            first = lease.acquire(
                "desktop:YASSIN",
                "one",
                host="YASSIN",
                session_id="task-1",
            )
            other = HostControllerLease(path)
            with self.assertRaises(ExecutionControlError):
                other.acquire(
                    "desktop:YASSIN",
                    "two",
                    host="YASSIN",
                    session_id="task-2",
                )
            lease.release(first)

    def test_controller_lease_replaces_stale_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lease.json"
            lease = HostControllerLease(path, ttl_seconds=10)
            old = lease.acquire(
                "desktop:YASSIN",
                "stale",
                host="YASSIN",
                session_id="old-task",
            )
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["acquired_at"] = "2000-01-01T00:00:00+00:00"
            path.write_text(json.dumps(payload), encoding="utf-8")

            fresh = lease.acquire(
                "desktop:YASSIN",
                "fresh",
                host="YASSIN",
                session_id="fresh-task",
            )
            self.assertGreater(fresh.fencing_token, old.fencing_token)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["holder"], "fresh")
            lease.release(fresh)

    def test_controller_lease_rejects_corrupt_or_naive_timestamps(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lease.json"
            path.write_text("not-json", encoding="utf-8")
            with self.assertRaises(ExecutionControlError):
                HostControllerLease(path).acquire(
                    "desktop:YASSIN",
                    "one",
                    host="YASSIN",
                    session_id="task-1",
                )

            path.write_text(
                json.dumps(
                    {
                        "resource": "desktop:YASSIN",
                        "holder": "old",
                        "host": "YASSIN",
                        "session_id": "old-task",
                        "fencing_token": 1,
                        "acquired_at": "not-a-time",
                        "pid": 1,
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(ExecutionControlError):
                HostControllerLease(path).acquire(
                    "desktop:YASSIN",
                    "two",
                    host="YASSIN",
                    session_id="task-2",
                )

            path.write_text(
                json.dumps(
                    {
                        "resource": "desktop:YASSIN",
                        "holder": "old",
                        "host": "YASSIN",
                        "session_id": "old-task",
                        "fencing_token": 1,
                        "acquired_at": "2000-01-01T00:00:00",
                        "pid": 1,
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(ExecutionControlError):
                HostControllerLease(path).acquire(
                    "desktop:YASSIN",
                    "two",
                    host="YASSIN",
                    session_id="task-2",
                )

    def test_controller_lease_default_env_path_and_unreadable_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            lease_path = Path(tmp) / "env-lease.json"
            with patch.dict(os.environ, {"UNIVERSAL_COUNCIL_CONTROLLER_LEASE": str(lease_path)}):
                lease = HostControllerLease()
                token = lease.acquire(
                    "desktop:YASSIN",
                    "env-holder",
                    host="YASSIN",
                    session_id="env-task",
                )
                self.assertEqual(lease.path, lease_path)
                lease.release(token)

            object_path = Path(tmp) / "object.json"
            object_path.write_text("[]", encoding="utf-8")
            with self.assertRaises(ExecutionControlError):
                HostControllerLease(object_path).acquire(
                    "desktop:YASSIN",
                    "holder",
                    host="YASSIN",
                    session_id="task",
                )

    def test_controller_lease_rejects_invalid_fencing_counter(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lease.json"
            lease = HostControllerLease(path)
            lease.counter_path.write_text("not-an-integer", encoding="utf-8")
            with self.assertRaises(ExecutionControlError):
                lease.acquire(
                    "desktop:YASSIN",
                    "holder",
                    host="YASSIN",
                    session_id="task",
                )
            self.assertFalse(path.exists())

    def test_controller_lease_rejects_negative_counter_and_malformed_tokens(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lease.json"
            lease = HostControllerLease(path)
            lease.counter_path.write_text("-1", encoding="utf-8")
            with self.assertRaises(ExecutionControlError):
                lease.acquire(
                    "desktop:YASSIN",
                    "holder",
                    host="YASSIN",
                    session_id="task",
                )

            malformed_payloads = [
                {},
                {
                    "resource": "desktop:YASSIN",
                    "holder": "holder",
                    "host": "YASSIN",
                    "session_id": "task",
                    "fencing_token": "bad",
                    "acquired_at": "2026-10-13T00:00:00+00:00",
                    "pid": 1,
                },
                {
                    "resource": "desktop:YASSIN",
                    "holder": "holder",
                    "host": "YASSIN",
                    "session_id": "task",
                    "fencing_token": 0,
                    "acquired_at": "2026-10-13T00:00:00+00:00",
                    "pid": 1,
                },
            ]
            for payload in malformed_payloads:
                path.write_text(json.dumps(payload), encoding="utf-8")
                with self.subTest(payload=payload):
                    with self.assertRaises(ExecutionControlError):
                        lease.assert_current(
                            LeaseToken(
                                resource="desktop:YASSIN",
                                holder="holder",
                                host="YASSIN",
                                session_id="task",
                                fencing_token=1,
                                acquired_at="2026-10-13T00:00:00+00:00",
                                pid=1,
                            )
                        )

    def test_controller_lease_persist_counter_failure_cleans_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lease.json"
            lease = HostControllerLease(path)
            with patch("company.runtime.execution_controls.os.replace", side_effect=OSError("denied")):
                with self.assertRaises(ExecutionControlError):
                    lease.acquire(
                        "desktop:YASSIN",
                        "holder",
                        host="YASSIN",
                        session_id="task",
                    )
            self.assertFalse(path.exists())

    def test_stale_cleanup_and_release_os_errors_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lease.json"
            lease = HostControllerLease(path, ttl_seconds=10)
            token = lease.acquire(
                "desktop:YASSIN",
                "holder",
                host="YASSIN",
                session_id="task",
            )
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["acquired_at"] = "2000-01-01T00:00:00+00:00"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with patch.object(Path, "unlink", side_effect=OSError("denied")):
                with self.assertRaises(ExecutionControlError):
                    lease.acquire(
                        "desktop:YASSIN",
                        "other",
                        host="YASSIN",
                        session_id="task-2",
                    )

            path.write_text(
                json.dumps(
                    {
                        "resource": token.resource,
                        "holder": token.holder,
                        "host": token.host,
                        "session_id": token.session_id,
                        "fencing_token": token.fencing_token,
                        "acquired_at": token.acquired_at,
                        "pid": token.pid,
                    }
                ),
                encoding="utf-8",
            )
            with patch.object(Path, "unlink", side_effect=OSError("denied")):
                with self.assertRaises(ExecutionControlError):
                    lease.release(token)

    def test_assert_current_detects_expired_matching_token(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lease.json"
            lease = HostControllerLease(path, ttl_seconds=10)
            lease.acquire(
                "desktop:YASSIN",
                "holder",
                host="YASSIN",
                session_id="task",
            )
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["acquired_at"] = "2000-01-01T00:00:00+00:00"
            path.write_text(json.dumps(payload), encoding="utf-8")
            matching = lease._token_from_payload(payload)
            with self.assertRaises(ExecutionControlError):
                lease.assert_current(matching)

    def test_execution_journal_filters_non_dict_other_task_and_missing_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            path.write_text("[]\n", encoding="utf-8")
            with self.assertRaises(ExecutionControlError):
                ExecutionJournal(path).pending_action_ids()

            events = [
                {"type": "intent", "task_id": "other", "action_id": "x"},
                {"type": "intent", "task_id": "task"},
                {"type": "result", "task_id": "task", "action_id": "done", "state": "SUCCEEDED"},
                {"type": "result", "task_id": "other", "action_id": "ignore", "state": "SUCCEEDED"},
            ]
            path.write_text(
                "\n".join(json.dumps(item) for item in events) + "\n",
                encoding="utf-8",
            )
            journal = ExecutionJournal(path)
            self.assertEqual(journal.pending_action_ids(task_id="task"), set())
            self.assertEqual(journal.completed_action_ids("task"), {"done"})

    def test_execution_journal_ignores_blank_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            path.write_text(
                "\n" + json.dumps({"type": "intent", "action_id": "a1"}) + "\n\n",
                encoding="utf-8",
            )
            self.assertEqual(ExecutionJournal(path).pending_action_ids(), {"a1"})

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
            self.assertEqual(journal.pending_action_ids(task_id="task"), {"a1"})
            journal.reconcile(task_id="task", action_id="a1", state="FAILED")
            self.assertEqual(journal.pending_action_ids(task_id="task"), set())
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
