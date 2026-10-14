from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from company.runtime.hybrid_execution import HybridExecutor, ResultState, SharedExecutionState
from company.runtime.execution_trace import (
    TraceError,
    TraceEventType,
    TraceRecorder,
    evaluate_trace,
)


ROOT = Path(__file__).resolve().parents[2]
BASE_CFG = json.loads((ROOT / "company/config/hybrid_execution.json").read_text(encoding="utf-8"))
BASE_REGISTRY = json.loads((ROOT / "company/config/tool_authority.json").read_text(encoding="utf-8"))


class MockAdapter:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def dispatch(self, action):
        self.calls.append(dict(action))
        return dict(self.result)


class Phase2R8TraceEvaluationTests(unittest.TestCase):
    def test_trace_accepts_only_important_event_types_and_keeps_sequence(self):
        with tempfile.TemporaryDirectory() as tmp:
            recorder = TraceRecorder(
                Path(tmp) / "trace.jsonl",
                trace_id="trace-1",
                task_id="task-1",
            )
            recorder.record(TraceEventType.FRAME, {"goal": "inspect"})
            recorder.record(
                TraceEventType.ROUTE,
                {
                    "action_id": "a1",
                    "path": "gui_semantic_uia",
                    "reason": "interactive semantic request",
                    "route_version": "hybrid-0.2",
                    "authority": "desktop_computer_use.observe",
                },
            )
            events = recorder.events()
            self.assertEqual([event["seq"] for event in events], [1, 2])
            self.assertEqual(events[1]["event"], "Route")

            with self.assertRaises(TraceError):
                recorder.record("DebugNoise", {"x": 1})

    def test_route_event_requires_explainability_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            recorder = TraceRecorder(Path(tmp) / "trace.jsonl", trace_id="t", task_id="task")
            with self.assertRaises(TraceError):
                recorder.record(
                    TraceEventType.ROUTE,
                    {"action_id": "a1", "path": "gui_semantic_uia"},
                )

    def test_evaluator_detects_false_success_and_verification(self):
        events = [
            {"seq": 1, "event": "Execution", "data": {"action_id": "a", "state": "SUCCEEDED", "latency_ms": 10}},
            {"seq": 2, "event": "Execution", "data": {"action_id": "b", "state": "SUCCEEDED", "latency_ms": 20}},
            {"seq": 3, "event": "Verification", "data": {"action_id": "b", "verified": True}},
        ]
        report = evaluate_trace(events)
        self.assertEqual(report["false_success_count"], 1)
        self.assertEqual(report["verified_success_count"], 1)
        self.assertEqual(report["latency_ms"], 30)

    def test_evaluator_measures_recovery_rework_cost_and_operator_burden(self):
        events = [
            {"seq": 1, "event": "Tool", "data": {"cost_usd": 0.25}},
            {"seq": 2, "event": "Approval", "data": {"human_required": True, "approved": True}},
            {"seq": 3, "event": "Recovery", "data": {"action_id": "a", "outcome": "RECOVERED", "attempt": 2}},
            {"seq": 4, "event": "Execution", "data": {"action_id": "a", "state": "SUCCEEDED", "attempt": 2}},
            {"seq": 5, "event": "Verification", "data": {"action_id": "a", "verified": True}},
            {"seq": 6, "event": "Recovery", "data": {"action_id": "b", "outcome": "ESCALATED", "attempt": 2}},
        ]
        report = evaluate_trace(events)
        self.assertEqual(report["recovery_attempts"], 2)
        self.assertEqual(report["recovery_successes"], 1)
        self.assertEqual(report["rework_count"], 1)
        self.assertEqual(report["cost_usd"], 0.25)
        self.assertEqual(report["operator_burden"], 2)

    def test_evaluator_scores_correctness_and_blocker_quality_when_ground_truth_supplied(self):
        events = [
            {
                "seq": 1,
                "event": "Frame",
                "data": {"actual_decision": "KEEP", "observed_blockers": ["B1", "B2"]},
            }
        ]
        report = evaluate_trace(
            events,
            expected_decision="KEEP",
            expected_blockers=["B1", "B3"],
        )
        self.assertEqual(report["correctness"], 1.0)
        self.assertAlmostEqual(report["blocker_precision"], 0.5)
        self.assertAlmostEqual(report["blocker_recall"], 0.5)
        self.assertAlmostEqual(report["blocker_f1"], 0.5)

    def test_trace_constructor_and_payload_validation_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trace.jsonl"
            with self.assertRaises(TraceError):
                TraceRecorder(path, trace_id="", task_id="task")
            with self.assertRaises(TraceError):
                TraceRecorder(path, trace_id="trace", task_id="")
            recorder = TraceRecorder(path, trace_id="trace", task_id="task")
            with self.assertRaises(TraceError):
                recorder.record(TraceEventType.FRAME, "not-a-dict")

    def test_trace_reader_rejects_corrupt_and_non_object_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trace.jsonl"
            recorder = TraceRecorder(path, trace_id="trace", task_id="task")
            path.write_text("{", encoding="utf-8")
            with self.assertRaises(TraceError):
                recorder.events()
            path.write_text("[]\n", encoding="utf-8")
            with self.assertRaises(TraceError):
                recorder.events()

    def test_empty_blocker_sets_score_perfectly(self):
        report = evaluate_trace(
            [{"seq": 1, "event": "Frame", "data": {"actual_decision": "KEEP", "observed_blockers": []}}],
            expected_decision="KEEP",
            expected_blockers=[],
        )
        self.assertEqual(report["blocker_precision"], 1.0)
        self.assertEqual(report["blocker_recall"], 1.0)
        self.assertEqual(report["blocker_f1"], 1.0)

    def test_hybrid_executor_emits_explainable_material_trace(self):
        with tempfile.TemporaryDirectory() as tmp:
            recorder = TraceRecorder(
                Path(tmp) / "trace.jsonl",
                trace_id="trace-hybrid",
                task_id="trace-task",
            )
            adapter = MockAdapter({"state": ResultState.SUCCEEDED.value})
            executor = HybridExecutor(
                BASE_CFG,
                native_adapter=adapter,
                authority_registry=BASE_REGISTRY,
                trace=recorder,
            )
            result = executor.execute(
                {
                    "id": "read",
                    "native_available": True,
                    "authority_operation": "github.read",
                },
                SharedExecutionState("trace-task"),
                requester="technical_operator",
                task_approved=True,
            )
            self.assertEqual(result["state"], ResultState.SUCCEEDED.value)
            events = recorder.events()
            names = [event["event"] for event in events]
            for expected in ("Frame", "Route", "Role", "Evidence", "Tool", "Approval", "Execution", "Verification"):
                self.assertIn(expected, names)
            canonical = ["Frame", "Route", "Role", "Evidence", "Tool", "Approval", "Execution", "Verification"]
            positions = [names.index(name) for name in canonical]
            self.assertEqual(positions, sorted(positions))
            route = next(event for event in events if event["event"] == "Route")
            self.assertTrue(route["data"]["reason"])
            self.assertTrue(route["data"]["route_version"])
            self.assertEqual(route["data"]["authority"], "github.read")
            report = evaluate_trace(events)
            self.assertEqual(report["false_success_count"], 0)
            self.assertEqual(report["verified_success_count"], 1)


if __name__ == "__main__":
    unittest.main()
