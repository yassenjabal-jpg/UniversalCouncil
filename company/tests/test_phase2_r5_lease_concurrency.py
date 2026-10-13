from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from company.runtime.execution_controls import ExecutionControlError, HostControllerLease


class Phase2R5LeaseConcurrencyTests(unittest.TestCase):
    def test_lease_is_bound_to_resource_host_session_and_returns_fencing_token(self):
        with tempfile.TemporaryDirectory() as tmp:
            lease = HostControllerLease(Path(tmp) / "controller.lock")
            token = lease.acquire(
                "desktop:YASSIN",
                "technical_operator",
                host="YASSIN",
                session_id="task-1",
            )
            self.assertGreater(token.fencing_token, 0)
            self.assertEqual(token.resource, "desktop:YASSIN")
            self.assertEqual(token.host, "YASSIN")
            self.assertEqual(token.session_id, "task-1")
            self.assertEqual(token.holder, "technical_operator")

            payload = json.loads(lease.path.read_text(encoding="utf-8"))
            self.assertEqual(payload["fencing_token"], token.fencing_token)
            self.assertEqual(payload["host"], "YASSIN")
            self.assertEqual(payload["session_id"], "task-1")
            lease.release(token)

    def test_fencing_token_increases_across_clean_reacquisition(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "controller.lock"
            lease = HostControllerLease(path)
            first = lease.acquire(
                "desktop:YASSIN",
                "technical_operator",
                host="YASSIN",
                session_id="task-1",
            )
            lease.release(first)
            second = lease.acquire(
                "desktop:YASSIN",
                "technical_operator",
                host="YASSIN",
                session_id="task-2",
            )
            self.assertGreater(second.fencing_token, first.fencing_token)
            lease.release(second)

    def test_same_holder_different_session_is_not_reentrant(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "controller.lock"
            lease = HostControllerLease(path)
            first = lease.acquire(
                "desktop:YASSIN",
                "technical_operator",
                host="YASSIN",
                session_id="task-1",
            )
            with self.assertRaises(ExecutionControlError):
                lease.acquire(
                    "desktop:YASSIN",
                    "technical_operator",
                    host="YASSIN",
                    session_id="task-2",
                )
            lease.release(first)

    def test_stale_token_cannot_release_new_lease(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "controller.lock"
            lease = HostControllerLease(path, ttl_seconds=10)
            first = lease.acquire(
                "desktop:YASSIN",
                "technical_operator",
                host="YASSIN",
                session_id="task-1",
            )
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["acquired_at"] = "2000-01-01T00:00:00+00:00"
            path.write_text(json.dumps(payload), encoding="utf-8")

            second = lease.acquire(
                "desktop:YASSIN",
                "technical_operator",
                host="YASSIN",
                session_id="task-2",
            )
            self.assertGreater(second.fencing_token, first.fencing_token)
            with self.assertRaises(ExecutionControlError):
                lease.release(first)
            lease.release(second)

    def test_assert_current_rejects_stale_fencing_token(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "controller.lock"
            lease = HostControllerLease(path, ttl_seconds=10)
            first = lease.acquire(
                "desktop:YASSIN",
                "technical_operator",
                host="YASSIN",
                session_id="task-1",
            )
            self.assertTrue(lease.assert_current(first))

            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["acquired_at"] = "2000-01-01T00:00:00+00:00"
            path.write_text(json.dumps(payload), encoding="utf-8")
            second = lease.acquire(
                "desktop:YASSIN",
                "technical_operator",
                host="YASSIN",
                session_id="task-2",
            )
            with self.assertRaises(ExecutionControlError):
                lease.assert_current(first)
            self.assertTrue(lease.assert_current(second))
            lease.release(second)


if __name__ == "__main__":
    unittest.main()
