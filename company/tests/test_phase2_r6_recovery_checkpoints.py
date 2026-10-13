from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

from company.runtime.execution_controls import ExecutionJournal
from company.runtime.hybrid_execution import HybridExecutor, ResultState, SharedExecutionState
from company.runtime.execution_recovery import (
    CancellationToken,
    CheckpointError,
    CheckpointStore,
    ExecutionWatchdog,
    LivenessState,
    RecoveryDecision,
    RecoveryPolicy,
    action_plan_hash,
    decide_recovery,
)


BASE_CFG = json.loads((ROOT / "company/config/hybrid_execution.json").read_text(encoding="utf-8"))
BASE_REGISTRY = json.loads((ROOT / "company/config/tool_authority.json").read_text(encoding="utf-8"))


class SequenceAdapter:
    def __init__(self, results):
        self.results = list(results)
        self.calls = []

    def dispatch(self, action):
        self.calls.append(dict(action))
        return dict(self.results.pop(0))


class Phase2R6RecoveryCheckpointTests(unittest.TestCase):
    def test_watchdog_classifies_progress_busy_no_progress_and_stalled(self):
        policy = RecoveryPolicy(
            max_retries=2,
            poll_interval_seconds=0.1,
            no_progress_seconds=5,
            stalled_seconds=15,
        )
        watchdog = ExecutionWatchdog(policy, started_at=100.0)

        first = watchdog.observe({"frame": 1}, busy=False, now=100.0)
        self.assertEqual(first.state, LivenessState.PROGRESS)

        busy = watchdog.observe({"frame": 1}, busy=True, now=102.0)
        self.assertEqual(busy.state, LivenessState.BUSY)

        no_progress = watchdog.observe({"frame": 1}, busy=False, now=106.0)
        self.assertEqual(no_progress.state, LivenessState.NO_PROGRESS)

        stalled = watchdog.observe({"frame": 1}, busy=False, now=116.0)
        self.assertEqual(stalled.state, LivenessState.STALLED)

        progressed = watchdog.observe({"frame": 2}, busy=False, now=117.0)
        self.assertEqual(progressed.state, LivenessState.PROGRESS)
        self.assertEqual(progressed.unchanged_seconds, 0)

    def test_recovery_decisions_are_bounded(self):
        policy = RecoveryPolicy(max_retries=2, no_progress_seconds=5, stalled_seconds=15)
        self.assertEqual(decide_recovery(LivenessState.PROGRESS, attempts=0, policy=policy), RecoveryDecision.CONTINUE)
        self.assertEqual(decide_recovery(LivenessState.BUSY, attempts=0, policy=policy), RecoveryDecision.CONTINUE)
        self.assertEqual(
            decide_recovery(LivenessState.NO_PROGRESS, attempts=0, policy=policy),
            RecoveryDecision.DIAGNOSE,
        )
        self.assertEqual(
            decide_recovery(LivenessState.STALLED, attempts=0, policy=policy),
            RecoveryDecision.RECOVER,
        )
        self.assertEqual(
            decide_recovery(LivenessState.STALLED, attempts=2, policy=policy),
            RecoveryDecision.ESCALATE,
        )

    def test_cancellation_token_is_durable(self):
        with tempfile.TemporaryDirectory() as tmp:
            token = CancellationToken(Path(tmp) / "cancel.json")
            self.assertFalse(token.is_cancelled())
            token.cancel("operator requested stop")
            self.assertTrue(token.is_cancelled())
            self.assertEqual(token.reason(), "operator requested stop")
            token.clear()
            self.assertFalse(token.is_cancelled())

    def test_checkpoint_roundtrip_and_plan_mismatch_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = CheckpointStore(Path(tmp) / "checkpoint.json")
            actions = [{"id": "a"}, {"id": "b"}]
            plan_hash = action_plan_hash(actions)
            store.save(
                task_id="task-1",
                plan_hash=plan_hash,
                next_action_index=1,
                completed_action_ids=["a"],
                state={"revision": 3},
                completed=False,
            )
            checkpoint = store.load(task_id="task-1", plan_hash=plan_hash)
            self.assertEqual(checkpoint["next_action_index"], 1)
            self.assertEqual(checkpoint["completed_action_ids"], ["a"])

            with self.assertRaises(CheckpointError):
                store.load(task_id="task-1", plan_hash=action_plan_hash([{"id": "other"}]))
            with self.assertRaises(CheckpointError):
                store.load(task_id="other-task", plan_hash=plan_hash)

    def test_unknown_result_remains_pending_until_reconciled(self):
        with tempfile.TemporaryDirectory() as tmp:
            journal = ExecutionJournal(Path(tmp) / "journal.jsonl")
            journal.record_intent(
                task_id="task",
                action_id="a1",
                requester="operator",
                path="gui_semantic_uia",
                risk="T2_LOCAL_STATE_CHANGE",
                authority_operation="desktop_computer_use.control",
            )
            journal.record_result(task_id="task", action_id="a1", state="UNKNOWN")
            self.assertIn("a1", journal.pending_action_ids(task_id="task"))
            journal.reconcile(task_id="task", action_id="a1", state="SUCCEEDED")
            self.assertNotIn("a1", journal.pending_action_ids(task_id="task"))
            self.assertEqual(journal.last_result_state("task", "a1"), "SUCCEEDED")

    def test_successful_result_is_durable_for_replay_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            journal = ExecutionJournal(Path(tmp) / "journal.jsonl")
            journal.record_intent(
                task_id="task",
                action_id="a1",
                requester="operator",
                path="native_api_or_connector",
                risk="T0_OBSERVE",
                authority_operation="github.read",
            )
            journal.record_result(task_id="task", action_id="a1", state="SUCCEEDED")
            self.assertEqual(journal.last_result_state("task", "a1"), "SUCCEEDED")
            self.assertEqual(journal.completed_action_ids("task"), {"a1"})

    def test_unknown_execution_is_not_replayed_without_reconciliation(self):
        with tempfile.TemporaryDirectory() as tmp:
            journal = ExecutionJournal(Path(tmp) / "journal.jsonl")
            adapter = SequenceAdapter(
                [
                    {"state": ResultState.UNKNOWN.value, "reason": "provider uncertain"},
                    {"state": ResultState.SUCCEEDED.value},
                ]
            )
            executor = HybridExecutor(
                BASE_CFG,
                native_adapter=adapter,
                authority_registry=BASE_REGISTRY,
                journal=journal,
            )
            action = {
                "id": "uncertain",
                "native_available": True,
                "authority_operation": "github.read",
            }
            first = executor.execute(
                action,
                SharedExecutionState("task-unknown"),
                requester="technical_operator",
                task_approved=True,
            )
            self.assertEqual(first["state"], ResultState.UNKNOWN.value)
            second = executor.execute(
                action,
                SharedExecutionState("task-unknown"),
                requester="technical_operator",
                task_approved=True,
            )
            self.assertEqual(second["state"], ResultState.UNKNOWN.value)
            self.assertEqual(len(adapter.calls), 1)

    def test_bounded_retry_requires_both_action_and_provider_safety(self):
        adapter = SequenceAdapter(
            [
                {"state": ResultState.FAILED.value, "safe_to_retry": True},
                {"state": ResultState.SUCCEEDED.value},
            ]
        )
        executor = HybridExecutor(
            BASE_CFG,
            native_adapter=adapter,
            authority_registry=BASE_REGISTRY,
        )
        action = {
            "id": "safe-retry",
            "native_available": True,
            "authority_operation": "github.read",
            "retry_safe": True,
            "max_retries": 5,
        }
        result = executor.execute_with_recovery(
            action,
            SharedExecutionState("retry-task"),
            requester="technical_operator",
            task_approved=True,
        )
        self.assertEqual(result["state"], ResultState.SUCCEEDED.value)
        self.assertEqual(result["attempts"], 2)
        self.assertEqual(len(adapter.calls), 2)

        unsafe_adapter = SequenceAdapter(
            [
                {"state": ResultState.FAILED.value, "safe_to_retry": False},
                {"state": ResultState.SUCCEEDED.value},
            ]
        )
        unsafe_executor = HybridExecutor(
            BASE_CFG,
            native_adapter=unsafe_adapter,
            authority_registry=BASE_REGISTRY,
        )
        unsafe = unsafe_executor.execute_with_recovery(
            action,
            SharedExecutionState("unsafe-retry-task"),
            requester="technical_operator",
            task_approved=True,
        )
        self.assertEqual(unsafe["state"], ResultState.FAILED.value)
        self.assertEqual(len(unsafe_adapter.calls), 1)

    def test_checkpoint_resume_continues_after_last_verified_action(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            journal = ExecutionJournal(root / "journal.jsonl")
            store = CheckpointStore(root / "checkpoint.json")
            actions = [
                {"id": "a", "native_available": True, "authority_operation": "github.read"},
                {"id": "b", "native_available": True, "authority_operation": "github.read"},
            ]
            plan_hash = action_plan_hash(actions)

            first_adapter = SequenceAdapter(
                [
                    {"state": ResultState.SUCCEEDED.value},
                    {"state": ResultState.FAILED.value},
                ]
            )
            first_executor = HybridExecutor(
                BASE_CFG,
                native_adapter=first_adapter,
                authority_registry=BASE_REGISTRY,
                journal=journal,
            )
            first_state = SharedExecutionState("resume-task")
            first = first_executor.execute_batch(
                actions,
                first_state,
                requester="technical_operator",
                task_approved=True,
                checkpoint_store=store,
                plan_hash=plan_hash,
            )
            self.assertEqual(first["state"], ResultState.FAILED.value)
            checkpoint = store.load(task_id="resume-task", plan_hash=plan_hash)
            self.assertEqual(checkpoint["next_action_index"], 1)
            self.assertEqual(checkpoint["completed_action_ids"], ["a"])

            resumed_state = SharedExecutionState.from_dict(checkpoint["state"])
            second_adapter = SequenceAdapter([{"state": ResultState.SUCCEEDED.value}])
            second_executor = HybridExecutor(
                BASE_CFG,
                native_adapter=second_adapter,
                authority_registry=BASE_REGISTRY,
                journal=journal,
            )
            second = second_executor.execute_batch(
                actions,
                resumed_state,
                requester="technical_operator",
                task_approved=True,
                checkpoint_store=store,
                plan_hash=plan_hash,
                resume_from=checkpoint["next_action_index"],
            )
            self.assertEqual(second["state"], ResultState.SUCCEEDED.value)
            self.assertEqual(second["completed"], 2)
            self.assertEqual(len(second_adapter.calls), 1)
            final_checkpoint = store.load(task_id="resume-task", plan_hash=plan_hash)
            self.assertTrue(final_checkpoint["completed"])
            self.assertEqual(final_checkpoint["completed_action_ids"], ["a", "b"])

    def test_cancelled_batch_stops_before_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            token = CancellationToken(Path(tmp) / "cancel.json")
            token.cancel("operator stop")
            adapter = SequenceAdapter([{"state": ResultState.SUCCEEDED.value}])
            executor = HybridExecutor(
                BASE_CFG,
                native_adapter=adapter,
                authority_registry=BASE_REGISTRY,
                cancellation_token=token,
            )
            result = executor.execute_batch(
                [{"id": "a", "native_available": True, "authority_operation": "github.read"}],
                SharedExecutionState("cancel-task"),
                requester="technical_operator",
                task_approved=True,
            )
            self.assertEqual(result["state"], ResultState.CANCELLED.value)
            self.assertEqual(adapter.calls, [])


if __name__ == "__main__":
    unittest.main()
