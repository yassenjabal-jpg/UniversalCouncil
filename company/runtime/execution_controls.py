from __future__ import annotations

import json
import os
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ExecutionControlError(RuntimeError):
    pass


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class LeaseToken:
    resource: str
    holder: str
    host: str
    session_id: str
    fencing_token: int
    acquired_at: str
    pid: int


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
        self.counter_path = self.path.with_suffix(self.path.suffix + ".fence")
        self.ttl_seconds = max(10, int(ttl_seconds))

    def _read(self) -> dict[str, Any]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ExecutionControlError(f"controller lease is unreadable: {exc}") from exc
        if not isinstance(data, dict):
            raise ExecutionControlError("controller lease payload must be an object")
        return data

    def _read_counter(self) -> int:
        if not self.counter_path.exists():
            return 0
        try:
            value = int(self.counter_path.read_text(encoding="utf-8").strip())
        except (OSError, ValueError) as exc:
            raise ExecutionControlError(f"fencing counter is unreadable: {exc}") from exc
        if value < 0:
            raise ExecutionControlError("fencing counter cannot be negative")
        return value

    def _next_fencing_token(self) -> int:
        previous = self._read_counter()
        token = max(previous + 1, time.time_ns())
        self.counter_path.parent.mkdir(parents=True, exist_ok=True)
        fd, raw_path = tempfile.mkstemp(
            prefix=self.counter_path.name + ".",
            suffix=".tmp",
            dir=self.counter_path.parent,
            text=True,
        )
        temp_path = Path(raw_path)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(str(token))
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, self.counter_path)
        except OSError as exc:
            temp_path.unlink(missing_ok=True)
            raise ExecutionControlError(f"cannot persist fencing counter: {exc}") from exc
        return token

    def _age_seconds(self, payload: dict[str, Any], *, now: datetime | None = None) -> float:
        try:
            acquired_at = datetime.fromisoformat(str(payload.get("acquired_at", "")))
        except ValueError as exc:
            raise ExecutionControlError("controller lease has invalid acquired_at") from exc
        if acquired_at.tzinfo is None:
            raise ExecutionControlError("controller lease acquired_at must be timezone-aware")
        current = now or _utc_now()
        return (current - acquired_at.astimezone(timezone.utc)).total_seconds()

    @staticmethod
    def _token_from_payload(payload: dict[str, Any]) -> LeaseToken:
        required = ("resource", "holder", "host", "session_id", "fencing_token", "acquired_at", "pid")
        if any(payload.get(key) in (None, "") for key in required):
            raise ExecutionControlError("controller lease is missing identity or fencing fields")
        try:
            fencing_token = int(payload["fencing_token"])
            pid = int(payload["pid"])
        except (TypeError, ValueError) as exc:
            raise ExecutionControlError("controller lease fencing_token/pid must be integers") from exc
        if fencing_token <= 0:
            raise ExecutionControlError("controller lease fencing_token must be positive")
        return LeaseToken(
            resource=str(payload["resource"]),
            holder=str(payload["holder"]),
            host=str(payload["host"]),
            session_id=str(payload["session_id"]),
            fencing_token=fencing_token,
            acquired_at=str(payload["acquired_at"]),
            pid=pid,
        )

    @staticmethod
    def _same_identity(
        payload: dict[str, Any],
        *,
        resource: str,
        holder: str,
        host: str,
        session_id: str,
    ) -> bool:
        return (
            payload.get("resource") == resource
            and payload.get("holder") == holder
            and payload.get("host") == host
            and payload.get("session_id") == session_id
        )

    def acquire(self, resource: str, holder: str, *, host: str, session_id: str) -> LeaseToken:
        if not resource or not holder or not host or not session_id:
            raise ExecutionControlError("controller resource, holder, host, and session_id are required")
        self.path.parent.mkdir(parents=True, exist_ok=True)

        for _ in range(6):
            now = _utc_now()
            try:
                fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            except FileExistsError:
                try:
                    current = self._read()
                except ExecutionControlError:
                    if not self.path.exists():
                        continue
                    raise

                age = self._age_seconds(current, now=now)
                if age <= self.ttl_seconds and self._same_identity(
                    current,
                    resource=resource,
                    holder=holder,
                    host=host,
                    session_id=session_id,
                ):
                    return self._token_from_payload(current)

                if age > self.ttl_seconds:
                    try:
                        self.path.unlink()
                    except FileNotFoundError:
                        continue
                    except OSError as exc:
                        raise ExecutionControlError(f"cannot clear stale controller lease: {exc}") from exc
                    continue

                raise ExecutionControlError(
                    "desktop controller already leased by "
                    f"{current.get('holder', 'unknown')}@{current.get('host', 'unknown')}"
                    f"/{current.get('session_id', 'unknown')}"
                )
            else:
                try:
                    fencing_token = self._next_fencing_token()
                    payload = {
                        "resource": resource,
                        "holder": holder,
                        "host": host,
                        "session_id": session_id,
                        "fencing_token": fencing_token,
                        "acquired_at": now.isoformat(),
                        "pid": os.getpid(),
                    }
                    with os.fdopen(fd, "w", encoding="utf-8") as handle:
                        json.dump(payload, handle, ensure_ascii=False, sort_keys=True)
                        handle.flush()
                        os.fsync(handle.fileno())
                except Exception:
                    try:
                        os.close(fd)
                    except OSError:
                        pass
                    self.path.unlink(missing_ok=True)
                    raise
                return self._token_from_payload(payload)

        raise ExecutionControlError("could not acquire controller lease after bounded contention retries")

    def assert_current(self, token: LeaseToken) -> bool:
        current = self._read()
        actual = self._token_from_payload(current)
        if actual != token:
            raise ExecutionControlError("controller fencing token is stale or lease identity changed")
        if self._age_seconds(current) > self.ttl_seconds:
            raise ExecutionControlError("controller lease has expired")
        return True

    def release(self, token: LeaseToken) -> None:
        if not self.path.exists():
            return
        current = self._token_from_payload(self._read())
        if current != token:
            raise ExecutionControlError("controller lease can only be released by the current fenced holder")
        try:
            self.path.unlink()
        except FileNotFoundError:
            return
        except OSError as exc:
            raise ExecutionControlError(f"cannot release controller lease: {exc}") from exc


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
