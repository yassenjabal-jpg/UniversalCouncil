from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ExecutionControlError(RuntimeError):
    pass


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class HostControllerLease:
    """Host-shared single-controller lease backed by an atomic lock file."""

    def __init__(self, path: Path | None = None, *, ttl_seconds: int = 120):
        self.path = Path(
            path
            or os.environ.get(
                "UNIVERSAL_COUNCIL_CONTROLLER_LEASE",
                Path(tempfile.gettempdir()) / "universal_council_yassin_controller.lock",
            )
        )
        self.ttl_seconds = max(10, int(ttl_seconds))

    def _read(self) -> dict[str, Any]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ExecutionControlError(f"controller lease is unreadable: {exc}") from exc
        if not isinstance(data, dict):
            raise ExecutionControlError("controller lease payload must be an object")
        return data

    def acquire(self, resource: str, holder: str) -> None:
        if not resource or not holder:
            raise ExecutionControlError("controller resource and holder are required")
        self.path.parent.mkdir(parents=True, exist_ok=True)

        for attempt in range(2):
            now = _utc_now()
            payload = {
                "resource": resource,
                "holder": holder,
                "acquired_at": now.isoformat(),
                "pid": os.getpid(),
            }
            try:
                fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            except FileExistsError:
                current = self._read()
                if current.get("resource") == resource and current.get("holder") == holder:
                    return
                try:
                    acquired_at = datetime.fromisoformat(str(current.get("acquired_at", "")))
                except ValueError as exc:
                    raise ExecutionControlError("controller lease has invalid acquired_at") from exc
                if acquired_at.tzinfo is None:
                    raise ExecutionControlError("controller lease acquired_at must be timezone-aware")
                age = (now - acquired_at.astimezone(timezone.utc)).total_seconds()
                if age > self.ttl_seconds and attempt == 0:
                    try:
                        self.path.unlink()
                    except OSError as exc:
                        raise ExecutionControlError(f"cannot clear stale controller lease: {exc}") from exc
                    continue
                raise ExecutionControlError(
                    f"desktop controller already leased by {current.get('holder', 'unknown')}"
                )
            else:
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    json.dump(payload, handle, ensure_ascii=False, sort_keys=True)
                    handle.flush()
                    os.fsync(handle.fileno())
                return

        raise ExecutionControlError("could not acquire controller lease")

    def release(self, resource: str, holder: str) -> None:
        if not self.path.exists():
            return
        current = self._read()
        if current.get("resource") != resource or current.get("holder") != holder:
            raise ExecutionControlError("controller lease can only be released by its holder")
        self.path.unlink()


class ExecutionJournal:
    """Durable append-only intent/result journal for dispatch reconciliation."""

    def __init__(self, path: Path):
        self.path = Path(path)

    def _append(self, event: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "recorded_at": _utc_now().isoformat(),
            **event,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())

    def record_intent(
        self,
        *,
        task_id: str,
        action_id: str,
        requester: str,
        path: str,
        risk: str,
        authority_operation: str,
    ) -> None:
        self._append(
            {
                "type": "intent",
                "task_id": task_id,
                "action_id": action_id,
                "requester": requester,
                "path": path,
                "risk": risk,
                "authority_operation": authority_operation,
            }
        )

    def record_result(self, *, task_id: str, action_id: str, state: str) -> None:
        self._append(
            {
                "type": "result",
                "task_id": task_id,
                "action_id": action_id,
                "state": state,
            }
        )

    def pending_action_ids(self) -> set[str]:
        if not self.path.exists():
            return set()
        pending: set[str] = set()
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ExecutionControlError("execution journal contains invalid JSON") from exc
            if event.get("type") == "intent" and event.get("action_id"):
                pending.add(str(event["action_id"]))
            elif event.get("type") == "result" and event.get("action_id"):
                pending.discard(str(event["action_id"]))
        return pending

    def reconcile(self, *, task_id: str, action_id: str, state: str) -> None:
        if action_id not in self.pending_action_ids():
            raise ExecutionControlError("action is not pending reconciliation")
        self.record_result(task_id=task_id, action_id=action_id, state=state)
