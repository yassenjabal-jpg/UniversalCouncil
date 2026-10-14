from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any


class TraceError(ValueError):
    pass


class TraceEventType(StrEnum):
    FRAME = "Frame"
    ROUTE = "Route"
    ROLE = "Role"
    EVIDENCE = "Evidence"
    TOOL = "Tool"
    APPROVAL = "Approval"
    EXECUTION = "Execution"
    RECOVERY = "Recovery"
    VERIFICATION = "Verification"


_ALLOWED_EVENTS = {event.value for event in TraceEventType}
_ROUTE_REQUIRED = {"action_id", "path", "reason", "route_version", "authority"}


class TraceRecorder:
    """Append-only trace of material decision/execution events only."""

    def __init__(self, path: Path, *, trace_id: str, task_id: str):
        if not trace_id or not task_id:
            raise TraceError("trace_id and task_id are required")
        self.path = Path(path)
        self.trace_id = trace_id
        self.task_id = task_id

    def events(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        events: list[dict[str, Any]] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise TraceError("trace contains invalid JSON") from exc
            if not isinstance(event, dict):
                raise TraceError("trace event must be an object")
            events.append(event)
        return events

    def record(self, event_type: TraceEventType | str, data: dict[str, Any]) -> dict[str, Any]:
        event = event_type.value if isinstance(event_type, TraceEventType) else str(event_type)
        if event not in _ALLOWED_EVENTS:
            raise TraceError(f"unsupported trace event: {event}")
        if not isinstance(data, dict):
            raise TraceError("trace data must be an object")
        if event == TraceEventType.ROUTE.value:
            missing = _ROUTE_REQUIRED - set(data)
            if missing or any(data.get(field) in (None, "") for field in _ROUTE_REQUIRED):
                raise TraceError(f"Route event missing explainability fields: {sorted(missing)}")

        existing = self.events()
        seq = int(existing[-1]["seq"]) + 1 if existing else 1
        record = {
            "schema_version": "1.0",
            "trace_id": self.trace_id,
            "task_id": self.task_id,
            "seq": seq,
            "at": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "data": data,
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return record


def _set_prf(expected: set[str], observed: set[str]) -> tuple[float, float, float]:
    if not expected and not observed:
        return 1.0, 1.0, 1.0
    true_positive = len(expected & observed)
    precision = true_positive / len(observed) if observed else 0.0
    recall = true_positive / len(expected) if expected else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def evaluate_trace(
    events: list[dict[str, Any]],
    *,
    expected_decision: str | None = None,
    expected_blockers: list[str] | None = None,
) -> dict[str, Any]:
    ordered = sorted(events, key=lambda item: int(item.get("seq", 0)))
    execution_success_seq: dict[str, int] = {}
    verified_successes: set[str] = set()
    latency_ms = 0.0
    cost_usd = 0.0
    recovery_attempts = 0
    recovery_successes = 0
    rework_actions: set[str] = set()
    operator_burden = 0
    actual_decision: str | None = None
    observed_blockers: set[str] = set()

    for event in ordered:
        event_name = event.get("event")
        data = event.get("data") if isinstance(event.get("data"), dict) else {}
        seq = int(event.get("seq", 0))

        if event_name == TraceEventType.FRAME.value:
            if data.get("actual_decision") is not None:
                actual_decision = str(data["actual_decision"])
            if isinstance(data.get("observed_blockers"), list):
                observed_blockers.update(str(item) for item in data["observed_blockers"])

        elif event_name == TraceEventType.TOOL.value:
            cost_usd += float(data.get("cost_usd", 0.0) or 0.0)

        elif event_name == TraceEventType.APPROVAL.value:
            if data.get("human_required") is True:
                operator_burden += 1

        elif event_name == TraceEventType.EXECUTION.value:
            latency_ms += float(data.get("latency_ms", 0.0) or 0.0)
            action_id = str(data.get("action_id", ""))
            if data.get("state") == "SUCCEEDED" and action_id:
                execution_success_seq[action_id] = seq
            if int(data.get("attempt", 1) or 1) > 1 and action_id:
                rework_actions.add(action_id)

        elif event_name == TraceEventType.RECOVERY.value:
            recovery_attempts += 1
            if data.get("outcome") == "RECOVERED":
                recovery_successes += 1
            if data.get("outcome") == "ESCALATED":
                operator_burden += 1

        elif event_name == TraceEventType.VERIFICATION.value:
            action_id = str(data.get("action_id", ""))
            if (
                action_id
                and data.get("verified") is True
                and action_id in execution_success_seq
                and seq > execution_success_seq[action_id]
            ):
                verified_successes.add(action_id)

    false_successes = set(execution_success_seq) - verified_successes

    correctness: float | None = None
    if expected_decision is not None:
        correctness = 1.0 if actual_decision == expected_decision else 0.0

    blocker_precision: float | None = None
    blocker_recall: float | None = None
    blocker_f1: float | None = None
    if expected_blockers is not None:
        blocker_precision, blocker_recall, blocker_f1 = _set_prf(
            set(str(item) for item in expected_blockers),
            observed_blockers,
        )

    return {
        "correctness": correctness,
        "false_success_count": len(false_successes),
        "false_success_action_ids": sorted(false_successes),
        "verified_success_count": len(verified_successes),
        "blocker_precision": blocker_precision,
        "blocker_recall": blocker_recall,
        "blocker_f1": blocker_f1,
        "recovery_attempts": recovery_attempts,
        "recovery_successes": recovery_successes,
        "latency_ms": latency_ms,
        "cost_usd": cost_usd,
        "rework_count": len(rework_actions),
        "operator_burden": operator_burden,
    }
