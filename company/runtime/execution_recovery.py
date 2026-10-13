from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any


class CheckpointError(RuntimeError):
    pass


class LivenessState(StrEnum):
    PROGRESS = "PROGRESS"
    BUSY = "BUSY"
    NO_PROGRESS = "NO_PROGRESS"
    STALLED = "STALLED"


class RecoveryDecision(StrEnum):
    CONTINUE = "CONTINUE"
    DIAGNOSE = "DIAGNOSE"
    RECOVER = "RECOVER"
    ESCALATE = "ESCALATE"


@dataclass(frozen=True)
class RecoveryPolicy:
    max_retries: int = 2
    poll_interval_seconds: float = 0.25
    no_progress_seconds: float = 5.0
    stalled_seconds: float = 15.0

    def __post_init__(self) -> None:
        if self.max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        if self.poll_interval_seconds <= 0:
            raise ValueError("poll_interval_seconds must be > 0")
        if self.no_progress_seconds <= 0:
            raise ValueError("no_progress_seconds must be > 0")
        if self.stalled_seconds <= self.no_progress_seconds:
            raise ValueError("stalled_seconds must be greater than no_progress_seconds")


@dataclass(frozen=True)
class WatchdogObservation:
    state: LivenessState
    unchanged_seconds: float
    fingerprint: str


class ExecutionWatchdog:
    def __init__(self, policy: RecoveryPolicy, *, started_at: float = 0.0):
        self.policy = policy
        self.started_at = float(started_at)
        self._last_fingerprint: str | None = None
        self._last_progress_at = float(started_at)

    @staticmethod
    def _fingerprint(snapshot: Any) -> str:
        encoded = json.dumps(snapshot, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def observe(self, snapshot: Any, *, busy: bool, now: float) -> WatchdogObservation:
        fingerprint = self._fingerprint(snapshot)
        current = float(now)
        if self._last_fingerprint is None or fingerprint != self._last_fingerprint:
            self._last_fingerprint = fingerprint
            self._last_progress_at = current
            return WatchdogObservation(LivenessState.PROGRESS, 0.0, fingerprint)

        unchanged = max(0.0, current - self._last_progress_at)
        if unchanged >= self.policy.stalled_seconds:
            state = LivenessState.STALLED
        elif unchanged >= self.policy.no_progress_seconds:
            state = LivenessState.NO_PROGRESS
        else:
            state = LivenessState.BUSY if busy else LivenessState.BUSY
        return WatchdogObservation(state, unchanged, fingerprint)


def decide_recovery(
    liveness: LivenessState,
    *,
    attempts: int,
    policy: RecoveryPolicy,
) -> RecoveryDecision:
    if liveness in {LivenessState.PROGRESS, LivenessState.BUSY}:
        return RecoveryDecision.CONTINUE
    if liveness == LivenessState.NO_PROGRESS:
        return RecoveryDecision.DIAGNOSE
    if attempts < policy.max_retries:
        return RecoveryDecision.RECOVER
    return RecoveryDecision.ESCALATE


class CancellationToken:
    def __init__(self, path: Path):
        self.path = Path(path)

    def cancel(self, reason: str) -> None:
        if not reason.strip():
            raise ValueError("cancellation reason is required")
        payload = {
            "cancelled": True,
            "reason": reason.strip(),
            "cancelled_at": datetime.now(timezone.utc).isoformat(),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, raw_path = tempfile.mkstemp(
            prefix=self.path.name + ".",
            suffix=".tmp",
            dir=self.path.parent,
            text=True,
        )
        temp = Path(raw_path)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, sort_keys=True)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp, self.path)
        except OSError:
            temp.unlink(missing_ok=True)
            raise

    def _read(self) -> dict[str, Any] | None:
        if not self.path.exists():
            return None
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CheckpointError(f"cancellation token is unreadable: {exc}") from exc
        if not isinstance(payload, dict):
            raise CheckpointError("cancellation token payload must be an object")
        return payload

    def is_cancelled(self) -> bool:
        payload = self._read()
        return bool(payload and payload.get("cancelled") is True)

    def reason(self) -> str | None:
        payload = self._read()
        if not payload or payload.get("cancelled") is not True:
            return None
        reason = payload.get("reason")
        return str(reason) if reason is not None else None

    def clear(self) -> None:
        self.path.unlink(missing_ok=True)


def action_plan_hash(actions: list[dict[str, Any]]) -> str:
    encoded = json.dumps(actions, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class CheckpointStore:
    SCHEMA_VERSION = "1.0"

    def __init__(self, path: Path):
        self.path = Path(path)

    def save(
        self,
        *,
        task_id: str,
        plan_hash: str,
        next_action_index: int,
        completed_action_ids: list[str],
        state: dict[str, Any],
        completed: bool,
    ) -> None:
        if not task_id or not plan_hash:
            raise CheckpointError("checkpoint task_id and plan_hash are required")
        if next_action_index < 0:
            raise CheckpointError("next_action_index must be >= 0")
        if len(completed_action_ids) != len(set(completed_action_ids)):
            raise CheckpointError("completed_action_ids must be unique")
        payload = {
            "schema_version": self.SCHEMA_VERSION,
            "task_id": task_id,
            "plan_hash": plan_hash,
            "next_action_index": int(next_action_index),
            "completed_action_ids": list(completed_action_ids),
            "state": state,
            "completed": bool(completed),
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, raw_path = tempfile.mkstemp(
            prefix=self.path.name + ".",
            suffix=".tmp",
            dir=self.path.parent,
            text=True,
        )
        temp = Path(raw_path)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, sort_keys=True)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp, self.path)
        except OSError as exc:
            temp.unlink(missing_ok=True)
            raise CheckpointError(f"cannot persist checkpoint: {exc}") from exc

    def load(self, *, task_id: str, plan_hash: str) -> dict[str, Any]:
        if not self.path.exists():
            raise CheckpointError("checkpoint does not exist")
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CheckpointError(f"checkpoint is unreadable: {exc}") from exc
        if not isinstance(payload, dict) or payload.get("schema_version") != self.SCHEMA_VERSION:
            raise CheckpointError("unsupported or malformed checkpoint")
        if payload.get("task_id") != task_id:
            raise CheckpointError("checkpoint task_id mismatch")
        if payload.get("plan_hash") != plan_hash:
            raise CheckpointError("checkpoint plan hash mismatch")
        if not isinstance(payload.get("completed_action_ids"), list):
            raise CheckpointError("checkpoint completed_action_ids must be a list")
        next_index = payload.get("next_action_index")
        if not isinstance(next_index, int) or next_index < 0:
            raise CheckpointError("checkpoint next_action_index is invalid")
        if not isinstance(payload.get("state"), dict):
            raise CheckpointError("checkpoint state must be an object")
        return payload

    def clear(self) -> None:
        self.path.unlink(missing_ok=True)
