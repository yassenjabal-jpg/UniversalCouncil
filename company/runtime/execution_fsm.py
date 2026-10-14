from __future__ import annotations

from enum import StrEnum
from typing import Any, Callable


class ExecutionFSMError(ValueError):
    pass


class FSMState(StrEnum):
    START = "START"
    OBSERVE = "OBSERVE"
    PLAN = "PLAN"
    ACT = "ACT"
    VERIFY = "VERIFY"
    DIAGNOSE = "DIAGNOSE"
    RECOVER = "RECOVER"
    CHECKPOINT = "CHECKPOINT"
    COMPLETE = "COMPLETE"
    ESCALATE = "ESCALATE"


def validate_fsm_config(cfg: dict[str, Any]) -> bool:
    if not isinstance(cfg, dict) or cfg.get("status") != "CANDIDATE_SHADOW_ONLY":
        raise ExecutionFSMError("execution FSM must remain candidate shadow-only")
    if cfg.get("verification_required") is not True:
        raise ExecutionFSMError("verification must be required")
    if cfg.get("checkpoint_required") is not True:
        raise ExecutionFSMError("checkpoint must be required")
    expected_success = ["OBSERVE", "PLAN", "ACT", "VERIFY", "CHECKPOINT", "COMPLETE"]
    expected_failure = ["DIAGNOSE", "RECOVER", "VERIFY"]
    if cfg.get("success_path") != expected_success:
        raise ExecutionFSMError("success path does not match canonical R16 sequence")
    if cfg.get("failure_path") != expected_failure:
        raise ExecutionFSMError("failure path does not match canonical R16 sequence")
    if int(cfg.get("max_recovery_attempts", -1)) < 0:
        raise ExecutionFSMError("max_recovery_attempts must be >= 0")
    transitions = cfg.get("transitions")
    if not isinstance(transitions, dict):
        raise ExecutionFSMError("transitions are required")
    return True


def validate_transition(current: FSMState, nxt: FSMState, cfg: dict[str, Any]) -> bool:
    validate_fsm_config(cfg)
    allowed = cfg["transitions"].get(current.value, [])
    if nxt.value not in allowed:
        raise ExecutionFSMError(f"illegal transition {current.value} -> {nxt.value}")
    return True


def _validate_plan(plan: dict[str, Any]) -> None:
    if not isinstance(plan, dict):
        raise ExecutionFSMError("planner must return an object")
    for field in ("route", "route_reason", "route_version", "authority"):
        if plan.get(field) in (None, ""):
            raise ExecutionFSMError(f"plan missing {field}")
    authority = plan["authority"]
    if not isinstance(authority, dict) or not authority:
        raise ExecutionFSMError("plan authority must be a non-empty object")
    for field in ("operation", "target", "scope"):
        if not str(authority.get(field) or "").strip():
            raise ExecutionFSMError(f"plan authority missing {field}")


def run_execution_fsm(
    *,
    observer: Callable[[], dict[str, Any]],
    planner: Callable[[dict[str, Any]], dict[str, Any]],
    actor: Callable[[dict[str, Any]], dict[str, Any]],
    verifier: Callable[[dict[str, Any]], dict[str, Any]],
    diagnoser: Callable[[dict[str, Any]], dict[str, Any]],
    recoverer: Callable[[dict[str, Any]], dict[str, Any]],
    checkpointer: Callable[[dict[str, Any]], dict[str, Any]],
    cfg: dict[str, Any],
) -> dict[str, Any]:
    validate_fsm_config(cfg)
    history: list[str] = []
    current = FSMState.START
    recovery_attempts = 0
    verified = False
    checkpointed = False

    def move(nxt: FSMState) -> None:
        nonlocal current
        validate_transition(current, nxt, cfg)
        current = nxt
        history.append(nxt.value)

    move(FSMState.OBSERVE)
    observation = observer()
    if not isinstance(observation, dict):
        raise ExecutionFSMError("observer must return an object")

    move(FSMState.PLAN)
    plan = planner(observation)
    _validate_plan(plan)

    move(FSMState.ACT)
    execution_result = actor(plan)
    if not isinstance(execution_result, dict):
        raise ExecutionFSMError("actor must return an object")

    def finish_checkpoint(verification: dict[str, Any]) -> dict[str, Any]:
        nonlocal checkpointed
        move(FSMState.CHECKPOINT)
        checkpoint = checkpointer(verification)
        if not isinstance(checkpoint, dict) or checkpoint.get("durable") is not True:
            return {
                "status": "CHECKPOINT_FAILED",
                "final_state": current.value,
                "history": history,
                "verified": True,
                "checkpointed": False,
                "recovery_attempts": recovery_attempts,
                "plan": plan,
            }
        checkpointed = True
        move(FSMState.COMPLETE)
        return {
            "status": "VERIFIED_SUCCESS",
            "final_state": current.value,
            "history": history,
            "verified": True,
            "checkpointed": True,
            "recovery_attempts": recovery_attempts,
            "plan": plan,
            "checkpoint": checkpoint,
        }

    state = str(execution_result.get("state") or "").upper()
    if state == "SUCCEEDED":
        move(FSMState.VERIFY)
        verification = verifier(execution_result)
        if not isinstance(verification, dict):
            raise ExecutionFSMError("verifier must return an object")
        verified = verification.get("verified") is True
        if verified:
            return finish_checkpoint(verification)
        move(FSMState.DIAGNOSE)
        diagnosis_input = execution_result
    else:
        move(FSMState.DIAGNOSE)
        diagnosis_input = execution_result

    while True:
        diagnosis = diagnoser(diagnosis_input)
        if not isinstance(diagnosis, dict):
            raise ExecutionFSMError("diagnoser must return an object")

        if recovery_attempts >= int(cfg["max_recovery_attempts"]):
            move(FSMState.ESCALATE)
            return {
                "status": "ESCALATED",
                "final_state": current.value,
                "history": history,
                "verified": False,
                "checkpointed": False,
                "recovery_attempts": recovery_attempts,
                "plan": plan,
                "last_diagnosis": diagnosis,
            }

        move(FSMState.RECOVER)
        recovery_attempts += 1
        recovered = recoverer(diagnosis)
        if not isinstance(recovered, dict):
            raise ExecutionFSMError("recoverer must return an object")

        move(FSMState.VERIFY)
        verification = verifier(recovered)
        if not isinstance(verification, dict):
            raise ExecutionFSMError("verifier must return an object")
        verified = verification.get("verified") is True
        if verified:
            return finish_checkpoint(verification)

        move(FSMState.DIAGNOSE)
        diagnosis_input = recovered
