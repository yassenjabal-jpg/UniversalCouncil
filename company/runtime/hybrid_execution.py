from __future__ import annotations

import json
import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, Protocol

from company.runtime.execution_controls import ExecutionControlError, ExecutionJournal, HostControllerLease
from company.runtime.execution_recovery import (
    CancellationToken,
    CheckpointStore,
    ExecutionWatchdog,
    RecoveryPolicy,
    action_plan_hash,
    decide_recovery,
)
from company.runtime.tool_authority import capability_currentness, get_capability


class HybridExecutionError(ValueError):
    pass


class ExecutionPath(StrEnum):
    NATIVE = "native_api_or_connector"
    DC = "dc_control_plane"
    ROUTINE = "reusable_routine"
    GUI_UIA = "gui_semantic_uia"
    GUI_VISUAL = "gui_visual_assist"


class RiskTier(StrEnum):
    T0 = "T0_OBSERVE"
    T1 = "T1_LOCAL_REVERSIBLE"
    T2 = "T2_LOCAL_STATE_CHANGE"
    T3 = "T3_EXTERNAL_CONSEQUENTIAL"
    T4 = "T4_PROHIBITED_OR_SEPARATELY_GOVERNED"


class ResultState(StrEnum):
    HOST_DISPATCH_REQUIRED = "HOST_DISPATCH_REQUIRED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"
    BLOCKED = "BLOCKED"
    CANCELLED = "CANCELLED"


GUI_OBSERVE_ACTIONS = {
    "status",
    "list_windows",
    "inspect",
    "search",
    "get_value",
    "get_property",
    "screenshot",
}
GUI_CONTROL_ACTIONS = {
    "invoke",
    "set_value",
    "focus",
    "scroll_into_view",
    "wait_for",
    "click",
    "send_keys",
    "drag",
    "hover",
    "record",
}
GUI_STATE_CHANGE_ACTIONS = {"invoke", "set_value", "click", "send_keys", "drag", "record"}
GUI_REVERSIBLE_ACTIONS = {"focus", "scroll_into_view", "wait_for", "hover"}


class Adapter(Protocol):
    def dispatch(self, action: dict[str, Any]) -> dict[str, Any]: ...


class Verifier(Protocol):
    def verify(self, action: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]: ...


@dataclass(frozen=True)
class PlannedAction:
    action_id: str
    path: ExecutionPath
    risk: RiskTier
    authority_operation: str
    requires_owner_confirmation: bool
    requires_verification: bool
    payload: dict[str, Any]


@dataclass
class SharedExecutionState:
    task_id: str
    revision: int = 0
    controller_lease: str | None = None
    last_path: str | None = None
    last_result: str | None = None
    events: list[dict[str, Any]] = field(default_factory=list)

    def _append(self, event: dict[str, Any], max_events: int = 12) -> None:
        self.revision += 1
        self.events.append({"revision": self.revision, **event})
        if len(self.events) > max_events:
            self.events[:] = self.events[-max_events:]

    def acquire_controller(self, holder: str) -> None:
        if not holder:
            raise HybridExecutionError("controller holder is required")
        if self.controller_lease not in (None, holder):
            raise HybridExecutionError(f"desktop controller already leased by {self.controller_lease}")
        if self.controller_lease is None:
            self.controller_lease = holder
            self._append({"type": "controller_acquired", "holder": holder})

    def release_controller(self, holder: str) -> None:
        if self.controller_lease != holder:
            raise HybridExecutionError("controller lease can only be released by its holder")
        self.controller_lease = None
        self._append({"type": "controller_released", "holder": holder})

    def record_result(self, planned: PlannedAction, state: ResultState) -> None:
        self.last_path = planned.path.value
        self.last_result = state.value
        self._append(
            {
                "type": "action_result",
                "action_id": planned.action_id,
                "path": planned.path.value,
                "risk": planned.risk.value,
                "state": state.value,
            }
        )

    def delta(self, since_revision: int) -> dict[str, Any]:
        if since_revision < 0:
            raise HybridExecutionError("since_revision must be >= 0")
        return {
            "task_id": self.task_id,
            "revision": self.revision,
            "controller_lease": self.controller_lease,
            "events": [event for event in self.events if event["revision"] > since_revision],
        }

    def as_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "revision": self.revision,
            "controller_lease": self.controller_lease,
            "last_path": self.last_path,
            "last_result": self.last_result,
            "events": list(self.events),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SharedExecutionState":
        if not isinstance(data, dict) or not data.get("task_id"):
            raise HybridExecutionError("shared state requires task_id")
        state = cls(task_id=str(data["task_id"]))
        state.revision = int(data.get("revision", 0))
        state.controller_lease = data.get("controller_lease")
        state.last_path = data.get("last_path")
        state.last_result = data.get("last_result")
        state.events = list(data.get("events", []))
        return state


def save_state(state: SharedExecutionState, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state.as_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_state(path: Path) -> SharedExecutionState:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HybridExecutionError(f"cannot load shared execution state: {exc}") from exc
    return SharedExecutionState.from_dict(data)


def load_config(path: Path) -> dict[str, Any]:
    try:
        cfg = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HybridExecutionError(f"cannot load hybrid execution config: {exc}") from exc
    validate_config(cfg)
    return cfg


def validate_config(cfg: dict[str, Any]) -> bool:
    if cfg.get("version") != "0.2":
        raise HybridExecutionError("hybrid execution config must be version 0.2")
    if cfg.get("primary_plane") != "GUI" or cfg.get("secondary_plane") != "DC":
        raise HybridExecutionError("hybrid v0.2 requires GUI primary and DC secondary")
    expected_order = [
        ExecutionPath.GUI_UIA.value,
        ExecutionPath.GUI_VISUAL.value,
        ExecutionPath.DC.value,
        ExecutionPath.NATIVE.value,
        ExecutionPath.ROUTINE.value,
    ]
    if cfg.get("execution_order") != expected_order:
        raise HybridExecutionError("execution_order must preserve the GUI-primary hybrid ladder")

    profiles = cfg.get("routing_profiles", {})
    interactive = profiles.get("interactive_app", {})
    if interactive.get("order") != [
        ExecutionPath.GUI_UIA.value,
        ExecutionPath.GUI_VISUAL.value,
        ExecutionPath.DC.value,
    ]:
        raise HybridExecutionError("interactive_app routing must be GUI-first with DC fallback")
    if interactive.get("dc_fallback_requires_explicit_opt_in") is not True:
        raise HybridExecutionError("interactive DC fallback must require explicit opt-in")
    if interactive.get("dc_must_not_bypass_gui_when_gui_available") is not True:
        raise HybridExecutionError("DC must not bypass an available GUI path")

    gui_cfg = cfg.get("gui_interaction_plane", {})
    if gui_cfg.get("role") != "PRIMARY_INTERACTION_PLANE":
        raise HybridExecutionError("GUI must be the primary interaction plane")
    if gui_cfg.get("semantic_first") is not True or gui_cfg.get("visual_fallback") is not True:
        raise HybridExecutionError("GUI plane must use semantic-first with visual fallback")
    if gui_cfg.get("raw_coordinates_enabled") is not False:
        raise HybridExecutionError("raw coordinates must remain disabled by default")

    dc_cfg = cfg.get("dc_control_plane", {})
    if dc_cfg.get("role") != "SECONDARY_SUPPORT_PLANE":
        raise HybridExecutionError("DC must remain the secondary support plane")

    if cfg.get("shared_state", {}).get("single_physical_controller") is not True:
        raise HybridExecutionError("single physical controller must be enforced")
    if cfg.get("verification", {}).get("unknown_is_never_success") is not True:
        raise HybridExecutionError("unknown outcome must never be treated as success")
    projection = cfg.get("result_projection", {})
    if projection.get("enabled") is not True:
        raise HybridExecutionError("compact result projection must remain enabled")
    if projection.get("raw_output_default") is not False:
        raise HybridExecutionError("raw output must remain opt-in")
    if int(projection.get("max_items", 0)) < 1 or int(projection.get("max_text_chars", 0)) < 64:
        raise HybridExecutionError("result projection bounds are too small")
    if cfg.get("automation_graduation", {}).get("verified_repeats_required", 0) < 2:
        raise HybridExecutionError("automation graduation requires repeated verification")
    recovery = cfg.get("recovery", {})
    if int(recovery.get("max_retries", -1)) < 0:
        raise HybridExecutionError("recovery max_retries must be >= 0")
    no_progress = float(recovery.get("no_progress_seconds", 0))
    stalled = float(recovery.get("stalled_seconds", 0))
    if no_progress <= 0 or stalled <= no_progress:
        raise HybridExecutionError("recovery stalled_seconds must exceed positive no_progress_seconds")
    if float(recovery.get("poll_interval_seconds", 0)) <= 0:
        raise HybridExecutionError("recovery poll_interval_seconds must be > 0")
    if recovery.get("unknown_requires_reconciliation") is not True:
        raise HybridExecutionError("UNKNOWN outcomes must require reconciliation")
    if recovery.get("replay_completed_action_default") is not False:
        raise HybridExecutionError("completed action replay must remain opt-in")
    return True


def classify_risk(action: dict[str, Any]) -> RiskTier:
    if action.get("policy_blocked"):
        return RiskTier.T4
    if action.get("external_consequence"):
        return RiskTier.T3
    if action.get("effect", "READ") == "READ":
        return RiskTier.T0
    if action.get("local_state_change"):
        return RiskTier.T2
    return RiskTier.T1


def _gui_authority(action_name: str) -> str:
    if action_name in GUI_OBSERVE_ACTIONS:
        return "desktop_computer_use.observe"
    if action_name in GUI_CONTROL_ACTIONS:
        return "desktop_computer_use.control"
    raise HybridExecutionError(f"unsupported GUI bridge action: {action_name}")


def choose_path(action: dict[str, Any]) -> ExecutionPath:
    """Route interactive application work through GUI before any DC fallback.

    Hybrid v0.2 treats Desktop Commander as a support plane. A GUI request is
    authoritative for interactive work even when DC/native/routine paths also
    exist. Interactive applications may fall back to DC only when the action
    explicitly opts in to that recovery path.
    """

    gui_request = action.get("gui_request")
    has_gui_request = isinstance(gui_request, dict) and bool(gui_request.get("action"))

    if action.get("visual_only"):
        if has_gui_request:
            return ExecutionPath.GUI_VISUAL
        raise HybridExecutionError("visual GUI path requires gui_request")

    if has_gui_request:
        return ExecutionPath.GUI_UIA

    if action.get("interactive_app"):
        if action.get("dc_capable") and action.get("allow_dc_fallback") is True:
            return ExecutionPath.DC
        raise HybridExecutionError("interactive application work requires GUI; DC fallback must be explicitly approved")

    if action.get("task_class") == "external_service" and action.get("native_available"):
        return ExecutionPath.NATIVE
    if action.get("dc_capable"):
        return ExecutionPath.DC
    if action.get("native_available"):
        return ExecutionPath.NATIVE
    if action.get("routine_available"):
        return ExecutionPath.ROUTINE
    raise HybridExecutionError("no approved execution path is available")


def _normalize_action_for_path(
    action: dict[str, Any],
    path: ExecutionPath,
    cfg: dict[str, Any],
) -> dict[str, Any]:
    normalized = dict(action)
    if path in {ExecutionPath.GUI_UIA, ExecutionPath.GUI_VISUAL}:
        request = normalized.get("gui_request") or {}
        gui_action = str(request.get("action", ""))
        if gui_action in GUI_OBSERVE_ACTIONS:
            trusted_effect = "READ"
            trusted_state_change = False
        elif gui_action in GUI_STATE_CHANGE_ACTIONS:
            trusted_effect = "WRITE"
            trusted_state_change = True
        elif gui_action in GUI_REVERSIBLE_ACTIONS:
            trusted_effect = "EXECUTE"
            trusted_state_change = False
        else:
            raise HybridExecutionError(f"unsupported GUI bridge action: {gui_action}")

        supplied_effect = normalized.get("effect")
        if supplied_effect is not None and supplied_effect != trusted_effect:
            raise HybridExecutionError(
                f"GUI action {gui_action} effect mismatch: expected {trusted_effect}, got {supplied_effect}"
            )
        if normalized.get("local_state_change") is False and trusted_state_change:
            raise HybridExecutionError(f"GUI action {gui_action} cannot downgrade local_state_change")
        normalized["effect"] = trusted_effect
        normalized["local_state_change"] = trusted_state_change
        normalized.setdefault(
            "authority_target",
            cfg.get("gui_interaction_plane", {}).get("authority_target", "YASSIN"),
        )
        normalized.setdefault("authority_scope", "yassin_desktop")
    elif path == ExecutionPath.DC:
        if normalized.get("effect") not in {"READ", "WRITE", "EXECUTE"}:
            raise HybridExecutionError("DC action requires an explicit trusted effect")
        normalized.setdefault(
            "authority_target",
            cfg.get("dc_control_plane", {}).get("authority_target", "YASSIN"),
        )
        normalized.setdefault("authority_scope", "yassin_host")
    return normalized


def plan_action(action: dict[str, Any], cfg: dict[str, Any]) -> PlannedAction:
    if not isinstance(action, dict) or not action.get("id"):
        raise HybridExecutionError("action requires a stable id")
    validate_config(cfg)
    path = choose_path(action)
    normalized = _normalize_action_for_path(action, path, cfg)
    risk = classify_risk(normalized)
    if risk == RiskTier.T4:
        raise HybridExecutionError("action is blocked by governing policy")

    if path == ExecutionPath.DC:
        authority = "remote_shell.read" if normalized["effect"] == "READ" else "remote_shell.execute"
    elif path in {ExecutionPath.GUI_UIA, ExecutionPath.GUI_VISUAL}:
        gui_request = normalized.get("gui_request") or {}
        gui_action = gui_request.get("action", "screenshot")
        authority = _gui_authority(str(gui_action))
    else:
        authority = str(normalized.get("authority_operation") or "")
        if not authority:
            raise HybridExecutionError(f"{path.value} requires authority_operation")

    requires_verification = risk in {RiskTier.T2, RiskTier.T3} or bool(normalized.get("verify"))
    return PlannedAction(
        action_id=str(normalized["id"]),
        path=path,
        risk=risk,
        authority_operation=authority,
        requires_owner_confirmation=risk == RiskTier.T3,
        requires_verification=requires_verification,
        payload=normalized,
    )


def authorize(planned: PlannedAction, *, task_approved: bool, owner_confirmed: bool = False) -> bool:
    if planned.risk == RiskTier.T0:
        return True
    if not task_approved:
        return False
    if planned.risk == RiskTier.T3 and not owner_confirmed:
        return False
    return True


def _authority_target(payload: dict[str, Any]) -> str | None:
    for key in ("authority_target", "target_repo", "target", "resource"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def enforce_tool_authority(
    planned: PlannedAction,
    registry: dict[str, Any],
    *,
    principal: str | None = None,
) -> dict[str, Any]:
    try:
        record = get_capability(registry, planned.authority_operation)
    except ValueError as exc:
        raise HybridExecutionError(f"unknown authority operation: {planned.authority_operation}") from exc
    if record["classification"] in {"BLOCKED", "UNAVAILABLE", "ADMIN_BLOCKED"}:
        raise HybridExecutionError(f"authority is not executable: {planned.authority_operation}")
    if record["approval_policy"] == "BLOCKED":
        raise HybridExecutionError(f"authority is blocked: {planned.authority_operation}")

    currentness = capability_currentness(record)
    if not currentness["current"]:
        raise HybridExecutionError(
            f"authority evidence is not current: {planned.authority_operation} ({currentness['reason']})"
        )

    allowed_targets = record.get("allowed_targets")
    if allowed_targets:
        target = _authority_target(planned.payload)
        if target is None:
            raise HybridExecutionError(f"authority target is required: {planned.authority_operation}")
        if target not in allowed_targets:
            raise HybridExecutionError(
                f"authority target is outside allowed scope: {planned.authority_operation} -> {target}"
            )

    allowed_principals = record.get("allowed_principals")
    if allowed_principals:
        if not principal:
            raise HybridExecutionError(f"authority principal is required: {planned.authority_operation}")
        if principal not in allowed_principals:
            raise HybridExecutionError(
                f"authority principal is not allowed: {planned.authority_operation} -> {principal}"
            )

    allowed_action_scopes = record.get("allowed_action_scopes")
    if allowed_action_scopes:
        scope = planned.payload.get("authority_scope")
        if not isinstance(scope, str) or not scope.strip():
            raise HybridExecutionError(f"authority scope is required: {planned.authority_operation}")
        if scope not in allowed_action_scopes:
            raise HybridExecutionError(f"authority scope is not allowed: {planned.authority_operation} -> {scope}")
    return record


class DcHostAdapter:
    def dispatch(self, action: dict[str, Any]) -> dict[str, Any]:
        operation = "remote_shell.read" if action.get("effect", "READ") == "READ" else "remote_shell.execute"
        return {
            "state": ResultState.HOST_DISPATCH_REQUIRED.value,
            "plane": "DC",
            "host_request": {
                "operation": operation,
                "payload": action.get("dc_request", action),
            },
        }


class CouncilVideoStudioGuiAdapter:
    def __init__(self, cfg: dict[str, Any], env: dict[str, str] | None = None):
        env = os.environ if env is None else env
        gui_cfg = cfg["gui_interaction_plane"]
        root = env.get(gui_cfg.get("root_env", ""))
        if not root:
            hint = gui_cfg.get("root_hint")
            root = hint if hint and Path(hint).exists() else None
        if not root:
            raise HybridExecutionError("CouncilVideoStudio root is unavailable")
        self.root = Path(root).resolve()
        self.timeout_seconds = int(gui_cfg.get("action_timeout_seconds", 30))
        recovery_cfg = cfg.get("recovery", {})
        self.recovery_policy = RecoveryPolicy(
            max_retries=int(recovery_cfg.get("max_retries", 0)),
            poll_interval_seconds=float(recovery_cfg.get("poll_interval_seconds", 0.25)),
            no_progress_seconds=float(recovery_cfg.get("no_progress_seconds", 5)),
            stalled_seconds=float(recovery_cfg.get("stalled_seconds", 15)),
        )
        self.script = self.root / gui_cfg["verified_action_relative"]
        if not self.script.is_file():
            raise HybridExecutionError("verified_action.py is unavailable")

    def dispatch(self, action: dict[str, Any]) -> dict[str, Any]:
        request = action.get("gui_request")
        if not isinstance(request, dict):
            raise HybridExecutionError("gui_request must be an object")
        with tempfile.NamedTemporaryFile(
            "w", suffix=".json", prefix="council_hybrid_", encoding="utf-8", delete=False, dir=self.root
        ) as handle:
            json.dump(request, handle, ensure_ascii=False)
            request_path = Path(handle.name)
        try:
            proc = subprocess.run(
                [os.fspath(Path(os.sys.executable)), os.fspath(self.script), os.fspath(request_path)],
                cwd=self.root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
                timeout=self.timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            watchdog = ExecutionWatchdog(self.recovery_policy, started_at=0.0)
            watchdog.observe({"stdout": "", "stderr": ""}, busy=False, now=0.0)
            observation = watchdog.observe(
                {
                    "stdout": str(exc.stdout or "").strip(),
                    "stderr": str(exc.stderr or "").strip(),
                },
                busy=False,
                now=float(self.timeout_seconds),
            )
            decision = decide_recovery(
                observation.state,
                attempts=0,
                policy=self.recovery_policy,
            )
            return {
                "state": ResultState.UNKNOWN.value,
                "plane": "GUI",
                "reason": "gui_no_progress_timeout",
                "timeout_seconds": self.timeout_seconds,
                "liveness": observation.state.value,
                "unchanged_seconds": observation.unchanged_seconds,
                "recovery_decision": decision.value,
                "recovery_sequence": ["NO_PROGRESS", "DIAGNOSE", decision.value],
                "stdout": str(exc.stdout or "").strip(),
                "stderr": str(exc.stderr or "").strip(),
            }
        finally:
            request_path.unlink(missing_ok=True)

        if proc.returncode != 0:
            return {
                "state": ResultState.FAILED.value,
                "plane": "GUI",
                "returncode": proc.returncode,
                "stdout": proc.stdout.strip(),
                "stderr": proc.stderr.strip(),
            }
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            raise HybridExecutionError("GUI bridge returned non-JSON output") from exc
        return {"state": ResultState.SUCCEEDED.value, "plane": "GUI", "bridge_result": payload}


class PassthroughVerifier:
    def verify(self, action: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
        verification = result.get("verification")
        if isinstance(verification, dict) and verification.get("independent") is True:
            return verification
        if isinstance(verification, dict):
            return {"verified": False, "mode": "provider_verification_not_independent"}
        return {"verified": False, "mode": "missing_independent_postcondition"}


class HybridExecutor:
    def __init__(
        self,
        cfg: dict[str, Any],
        *,
        dc_adapter: Adapter | None = None,
        gui_adapter: Adapter | None = None,
        native_adapter: Adapter | None = None,
        routine_adapter: Adapter | None = None,
        verifier: Verifier | None = None,
        authority_registry: dict[str, Any] | None = None,
        controller_lease: HostControllerLease | None = None,
        journal: ExecutionJournal | None = None,
        cancellation_token: CancellationToken | None = None,
    ):
        validate_config(cfg)
        self.cfg = cfg
        self.dc_adapter = dc_adapter or DcHostAdapter()
        self.gui_adapter = gui_adapter
        self.native_adapter = native_adapter
        self.routine_adapter = routine_adapter
        self.verifier = verifier or PassthroughVerifier()
        self.authority_registry = authority_registry
        self.controller_lease = controller_lease or HostControllerLease()
        self.journal = journal
        self.cancellation_token = cancellation_token

    def _adapter_for(self, path: ExecutionPath) -> Adapter:
        if path == ExecutionPath.DC:
            return self.dc_adapter
        if path in {ExecutionPath.GUI_UIA, ExecutionPath.GUI_VISUAL}:
            if self.gui_adapter is None:
                raise HybridExecutionError("GUI adapter is unavailable")
            return self.gui_adapter
        if path == ExecutionPath.NATIVE:
            if self.native_adapter is None:
                raise HybridExecutionError("native adapter is unavailable")
            return self.native_adapter
        if path == ExecutionPath.ROUTINE:
            if self.routine_adapter is None:
                raise HybridExecutionError("routine adapter is unavailable")
            return self.routine_adapter
        raise HybridExecutionError(f"no adapter for {path}")

    def _journal_result(self, state: SharedExecutionState, planned: PlannedAction, result_state: ResultState) -> None:
        if self.journal is not None:
            self.journal.record_result(
                task_id=state.task_id,
                action_id=planned.action_id,
                state=result_state.value,
            )

    def execute(
        self,
        action: dict[str, Any],
        state: SharedExecutionState,
        *,
        requester: str,
        task_approved: bool,
        owner_confirmed: bool = False,
        retain_controller: bool = False,
    ) -> dict[str, Any]:
        planned = plan_action(action, self.cfg)
        if not requester:
            state.record_result(planned, ResultState.BLOCKED)
            return {"state": ResultState.BLOCKED.value, "planned": planned, "reason": "requester identity is required"}
        if self.authority_registry is None:
            state.record_result(planned, ResultState.BLOCKED)
            return {
                "state": ResultState.BLOCKED.value,
                "planned": planned,
                "reason": "tool authority registry is required",
            }

        try:
            authority_record = enforce_tool_authority(
                planned,
                self.authority_registry,
                principal=requester,
            )
        except HybridExecutionError as exc:
            state.record_result(planned, ResultState.BLOCKED)
            return {
                "state": ResultState.BLOCKED.value,
                "planned": planned,
                "reason": str(exc),
            }
        if authority_record["approval_policy"] in {"OWNER_EXPLICIT", "ASK_BEFORE_WRITE"} and not task_approved:
            state.record_result(planned, ResultState.BLOCKED)
            return {
                "state": ResultState.BLOCKED.value,
                "planned": planned,
                "reason": f"approval required by tool authority: {planned.authority_operation}",
            }
        if not authorize(planned, task_approved=task_approved, owner_confirmed=owner_confirmed):
            state.record_result(planned, ResultState.BLOCKED)
            return {"state": ResultState.BLOCKED.value, "planned": planned}

        if self.cancellation_token is not None and self.cancellation_token.is_cancelled():
            state.record_result(planned, ResultState.CANCELLED)
            return {
                "state": ResultState.CANCELLED.value,
                "planned": planned,
                "reason": self.cancellation_token.reason() or "execution cancelled",
            }

        if self.journal is not None:
            if planned.action_id in self.journal.pending_action_ids(task_id=state.task_id):
                state.record_result(planned, ResultState.UNKNOWN)
                return {
                    "state": ResultState.UNKNOWN.value,
                    "planned": planned,
                    "reason": "pending prior intent requires reconciliation",
                }
            previous = self.journal.last_result_state(state.task_id, planned.action_id)
            if (
                previous == ResultState.SUCCEEDED.value
                and planned.payload.get("allow_replay") is not True
            ):
                state.record_result(planned, ResultState.BLOCKED)
                return {
                    "state": ResultState.BLOCKED.value,
                    "planned": planned,
                    "reason": "completed action replay is blocked; use a new action id or explicit allow_replay",
                }

        controls_desktop = (
            planned.path in {ExecutionPath.GUI_UIA, ExecutionPath.GUI_VISUAL}
            and planned.authority_operation == "desktop_computer_use.control"
        )
        controller_host = str(planned.payload.get("authority_target", "YASSIN"))
        controller_resource = f"desktop:{controller_host}"
        lease_token = None
        if controls_desktop:
            state_acquired = False
            try:
                state.acquire_controller(requester)
                state_acquired = True
                lease_token = self.controller_lease.acquire(
                    controller_resource,
                    requester,
                    host=controller_host,
                    session_id=state.task_id,
                )
            except (ExecutionControlError, HybridExecutionError) as exc:
                if state_acquired and state.controller_lease == requester:
                    state.release_controller(requester)
                state.record_result(planned, ResultState.BLOCKED)
                return {
                    "state": ResultState.BLOCKED.value,
                    "planned": planned,
                    "reason": str(exc),
                }
        try:
            if self.journal is not None:
                self.journal.record_intent(
                    task_id=state.task_id,
                    action_id=planned.action_id,
                    requester=requester,
                    path=planned.path.value,
                    risk=planned.risk.value,
                    authority_operation=planned.authority_operation,
                )

            if controls_desktop and lease_token is not None:
                self.controller_lease.assert_current(lease_token)
            result = self._adapter_for(planned.path).dispatch(planned.payload)
            raw_state = result.get("state")
            if raw_state == ResultState.HOST_DISPATCH_REQUIRED.value:
                state.record_result(planned, ResultState.HOST_DISPATCH_REQUIRED)
                self._journal_result(state, planned, ResultState.HOST_DISPATCH_REQUIRED)
                return {"state": raw_state, "planned": planned, "result": result}
            if raw_state == ResultState.UNKNOWN.value:
                state.record_result(planned, ResultState.UNKNOWN)
                self._journal_result(state, planned, ResultState.UNKNOWN)
                return {"state": ResultState.UNKNOWN.value, "planned": planned, "result": result}
            if raw_state != ResultState.SUCCEEDED.value:
                state.record_result(planned, ResultState.FAILED)
                self._journal_result(state, planned, ResultState.FAILED)
                return {"state": ResultState.FAILED.value, "planned": planned, "result": result}

            if planned.requires_verification:
                verification = self.verifier.verify(planned.payload, result)
                if not verification.get("verified"):
                    state.record_result(planned, ResultState.UNKNOWN)
                    self._journal_result(state, planned, ResultState.UNKNOWN)
                    return {
                        "state": ResultState.UNKNOWN.value,
                        "planned": planned,
                        "result": result,
                        "verification": verification,
                    }
            else:
                verification = {"verified": True, "mode": "not_required"}

            state.record_result(planned, ResultState.SUCCEEDED)
            self._journal_result(state, planned, ResultState.SUCCEEDED)
            return {
                "state": ResultState.SUCCEEDED.value,
                "planned": planned,
                "result": result,
                "verification": verification,
            }
        finally:
            if controls_desktop and not retain_controller and state.controller_lease == requester:
                state.release_controller(requester)
                if lease_token is not None:
                    self.controller_lease.release(lease_token)

    def execute_with_recovery(
        self,
        action: dict[str, Any],
        state: SharedExecutionState,
        *,
        requester: str,
        task_approved: bool,
        owner_confirmed: bool = False,
        retain_controller: bool = False,
    ) -> dict[str, Any]:
        configured_max = int(self.cfg.get("recovery", {}).get("max_retries", 0))
        requested_max = int(action.get("max_retries", 0) or 0)
        retry_limit = min(max(0, requested_max), configured_max)
        attempts = 0

        while True:
            result = self.execute(
                action,
                state,
                requester=requester,
                task_approved=task_approved,
                owner_confirmed=owner_confirmed,
                retain_controller=retain_controller,
            )
            result["attempts"] = attempts + 1
            if result["state"] != ResultState.FAILED.value:
                return result
            provider = result.get("result")
            safe_to_retry = isinstance(provider, dict) and provider.get("safe_to_retry") is True
            if (
                attempts >= retry_limit
                or action.get("retry_safe") is not True
                or not safe_to_retry
            ):
                return result
            attempts += 1

    def execute_batch(
        self,
        actions: list[dict[str, Any]],
        state: SharedExecutionState,
        *,
        requester: str,
        task_approved: bool,
        owner_confirmed: bool = False,
        checkpoint_store: CheckpointStore | None = None,
        plan_hash: str | None = None,
        resume_from: int = 0,
    ) -> dict[str, Any]:
        if not isinstance(actions, list) or not actions:
            raise HybridExecutionError("batch requires at least one action")
        maximum = int(self.cfg["batching"]["max_deterministic_steps"])
        if len(actions) > maximum:
            raise HybridExecutionError(f"batch exceeds max deterministic steps: {maximum}")

        if resume_from < 0 or resume_from > len(actions):
            raise HybridExecutionError("resume_from is outside the batch action range")
        actual_plan_hash = action_plan_hash(actions)
        if plan_hash is not None and plan_hash != actual_plan_hash:
            raise HybridExecutionError("batch plan hash mismatch")
        effective_plan_hash = plan_hash or actual_plan_hash

        completed_ids = self.journal.completed_action_ids(state.task_id) if self.journal is not None else set()
        expected_resumed = {str(action["id"]) for action in actions[:resume_from]}
        if resume_from and not expected_resumed.issubset(completed_ids):
            raise HybridExecutionError("resume checkpoint is not backed by successful journal results")
        if resume_from == len(actions):
            return {
                "state": ResultState.SUCCEEDED.value,
                "completed": len(actions),
                "stopped_at": None,
                "results": [],
                "resumed_from": resume_from,
            }

        planned = [plan_action(action, self.cfg) for action in actions]
        controlling = next(
            (
                item
                for item in planned[resume_from:]
                if item.path in {ExecutionPath.GUI_UIA, ExecutionPath.GUI_VISUAL}
                and item.authority_operation == "desktop_computer_use.control"
            ),
            None,
        )
        controls_desktop = controlling is not None
        controller_host = str(controlling.payload.get("authority_target", "YASSIN")) if controlling is not None else ""
        controller_resource = f"desktop:{controller_host}" if controller_host else ""
        batch_lease_token = None
        if controls_desktop:
            state_acquired = False
            try:
                state.acquire_controller(requester)
                state_acquired = True
                batch_lease_token = self.controller_lease.acquire(
                    controller_resource,
                    requester,
                    host=controller_host,
                    session_id=state.task_id,
                )
            except (ExecutionControlError, HybridExecutionError) as exc:
                if state_acquired and state.controller_lease == requester:
                    state.release_controller(requester)
                return {
                    "state": ResultState.BLOCKED.value,
                    "completed": 0,
                    "stopped_at": 0,
                    "results": [],
                    "reason": str(exc),
                }

        results: list[dict[str, Any]] = []
        try:
            for index in range(resume_from, len(actions)):
                action = actions[index]
                if self.cancellation_token is not None and self.cancellation_token.is_cancelled():
                    state.record_result(planned[index], ResultState.CANCELLED)
                    return {
                        "state": ResultState.CANCELLED.value,
                        "completed": index,
                        "stopped_at": index,
                        "results": results,
                        "reason": self.cancellation_token.reason() or "execution cancelled",
                    }

                result = self.execute_with_recovery(
                    action,
                    state,
                    requester=requester,
                    task_approved=task_approved,
                    owner_confirmed=owner_confirmed,
                    retain_controller=controls_desktop,
                )
                results.append(result)
                if result["state"] != ResultState.SUCCEEDED.value:
                    return {
                        "state": result["state"],
                        "completed": index,
                        "stopped_at": index,
                        "results": results,
                    }

                completed_ids.add(str(action["id"]))
                if checkpoint_store is not None:
                    ordered_completed = [
                        str(candidate["id"])
                        for candidate in actions[: index + 1]
                        if str(candidate["id"]) in completed_ids
                    ]
                    checkpoint_store.save(
                        task_id=state.task_id,
                        plan_hash=effective_plan_hash,
                        next_action_index=index + 1,
                        completed_action_ids=ordered_completed,
                        state=state.as_dict(),
                        completed=index + 1 == len(actions),
                    )

            return {
                "state": ResultState.SUCCEEDED.value,
                "completed": len(actions),
                "stopped_at": None,
                "results": results,
                "resumed_from": resume_from,
            }
        finally:
            if controls_desktop and state.controller_lease == requester:
                state.release_controller(requester)
                if batch_lease_token is not None:
                    self.controller_lease.release(batch_lease_token)


def eligible_for_routine_graduation(history: list[dict[str, Any]], cfg: dict[str, Any]) -> bool:
    threshold = int(cfg["automation_graduation"]["verified_repeats_required"])
    successful = [
        item
        for item in history
        if item.get("state") == ResultState.SUCCEEDED.value
        and item.get("verified") is True
        and item.get("accidental_action") is not True
    ]
    unknowns = sum(item.get("state") == ResultState.UNKNOWN.value for item in history)
    accidental = sum(item.get("accidental_action") is True for item in history)
    return (
        len(successful) >= threshold
        and unknowns <= int(cfg["automation_graduation"]["max_unknown_results"])
        and accidental <= int(cfg["automation_graduation"]["max_accidental_actions"])
    )
