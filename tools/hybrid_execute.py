from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from company.runtime.hybrid_execution import (  # noqa: E402
    CouncilVideoStudioGuiAdapter,
    HybridExecutionError,
    HybridExecutor,
    SharedExecutionState,
    load_config,
    load_state,
    plan_action,
    save_state,
)
from company.runtime.execution_controls import ExecutionControlError, ExecutionJournal  # noqa: E402
from company.runtime.execution_recovery import (  # noqa: E402
    CancellationToken,
    CheckpointError,
    CheckpointStore,
    action_plan_hash,
)
from company.runtime.execution_trace import (  # noqa: E402
    TraceEventType,
    TraceRecorder,
    evaluate_trace,
)
from company.runtime.hybrid_projection import project_execution_result  # noqa: E402
from company.runtime.hybrid_verification import GuiPostStateVerifier  # noqa: E402

CONFIG = ROOT / "company/config/hybrid_execution.json"
TOOL_AUTHORITY = ROOT / "company/config/tool_authority.json"


def planned_payload(planned):
    return {
        "action_id": planned.action_id,
        "path": planned.path.value,
        "risk": planned.risk.value,
        "authority_operation": planned.authority_operation,
        "requires_owner_confirmation": planned.requires_owner_confirmation,
        "requires_verification": planned.requires_verification,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Universal Council hybrid DC+GUI execution prototype")
    parser.add_argument("action", type=Path, help="JSON action specification")
    parser.add_argument("--execute", action="store_true", help="dispatch the planned action")
    parser.add_argument("--task-approved", action="store_true")
    parser.add_argument("--owner-confirmed", action="store_true")
    parser.add_argument("--requester", default="technical_operator")
    parser.add_argument("--state", type=Path)
    parser.add_argument("--reconcile-outcome", choices=["SUCCEEDED", "FAILED", "UNKNOWN"])
    parser.add_argument("--resume", action="store_true", help="resume a batch from its durable checkpoint")
    parser.add_argument("--cancel", action="store_true", help="persist a cancellation request for this task")
    parser.add_argument("--cancel-reason", default="operator requested cancellation")
    parser.add_argument("--clear-cancel", action="store_true", help="clear a prior cancellation request before execution")
    args = parser.parse_args()

    payload = json.loads(args.action.read_text(encoding="utf-8"))
    cfg = load_config(CONFIG)
    authority_registry = json.loads(TOOL_AUTHORITY.read_text(encoding="utf-8"))
    actions = payload.get("actions") if isinstance(payload, dict) else None
    is_batch = isinstance(actions, list)
    action_list = actions if is_batch else [payload]
    planned = [plan_action(action, cfg) for action in action_list]

    if not args.execute:
        print(
            json.dumps(
                {
                    "mode": "PLAN_ONLY",
                    "batch": is_batch,
                    "planned": [planned_payload(item) for item in planned],
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    task_id = payload.get("task_id") if is_batch else payload.get("task_id")
    if not task_id:
        task_id = action_list[0]["id"]
    state_path = args.state or (ROOT / ".runtime" / "hybrid" / f"{task_id}.json")
    journal_path = state_path.with_suffix(state_path.suffix + ".journal.jsonl")
    checkpoint_path = state_path.with_suffix(state_path.suffix + ".checkpoint.json")
    cancel_path = state_path.with_suffix(state_path.suffix + ".cancel.json")
    trace_path = state_path.with_suffix(state_path.suffix + ".trace.jsonl")
    journal = ExecutionJournal(journal_path)
    checkpoint_store = CheckpointStore(checkpoint_path)
    cancellation_token = CancellationToken(cancel_path)
    plan_hash = action_plan_hash(action_list)
    trace = TraceRecorder(
        trace_path,
        trace_id=f"{task_id}:{plan_hash[:16]}",
        task_id=str(task_id),
    )
    trace.record(
        TraceEventType.FRAME,
        {
            "goal": "hybrid execution",
            "action_ids": [str(item["id"]) for item in action_list],
            "resume_requested": bool(args.resume),
            "execute_requested": bool(args.execute),
        },
    )

    if args.cancel and args.clear_cancel:
        raise HybridExecutionError("--cancel and --clear-cancel cannot be used together")
    if args.clear_cancel:
        cancellation_token.clear()
    if args.cancel:
        cancellation_token.cancel(args.cancel_reason)
        trace.record(
            TraceEventType.RECOVERY,
            {
                "action_id": str(action_list[0]["id"]),
                "outcome": "CANCELLED",
                "attempt": 0,
                "reason": args.cancel_reason,
            },
        )
        print(
            json.dumps(
                {
                    "mode": "CANCEL",
                    "task_id": str(task_id),
                    "cancel_path": str(cancel_path),
                    "reason": args.cancel_reason,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    if args.reconcile_outcome:
        if is_batch:
            raise HybridExecutionError("reconciliation requires a single action payload")
        journal.reconcile(
            task_id=str(task_id),
            action_id=str(action_list[0]["id"]),
            state=args.reconcile_outcome,
        )
        trace.record(
            TraceEventType.RECOVERY,
            {
                "action_id": str(action_list[0]["id"]),
                "outcome": "RECONCILED",
                "attempt": 0,
                "reconciled_state": args.reconcile_outcome,
            },
        )
        print(
            json.dumps(
                {
                    "mode": "RECONCILE",
                    "task_id": str(task_id),
                    "action_id": str(action_list[0]["id"]),
                    "state": args.reconcile_outcome,
                    "journal": str(journal_path),
                },
                indent=2,
            )
        )
        return 0

    resume_from = 0
    if args.resume:
        if not is_batch:
            raise HybridExecutionError("--resume requires a batch action payload")
        checkpoint = checkpoint_store.load(task_id=str(task_id), plan_hash=plan_hash)
        state = SharedExecutionState.from_dict(checkpoint["state"])
        resume_from = int(checkpoint["next_action_index"])
    elif state_path.exists():
        state = load_state(state_path)
    else:
        state = SharedExecutionState(task_id=str(task_id))

    gui_adapter = None
    if any(item.path.value.startswith("gui_") for item in planned):
        gui_adapter = CouncilVideoStudioGuiAdapter(cfg)
    verifier = GuiPostStateVerifier(gui_adapter) if gui_adapter is not None else None
    executor = HybridExecutor(
        cfg,
        gui_adapter=gui_adapter,
        verifier=verifier,
        authority_registry=authority_registry,
        journal=journal,
        cancellation_token=cancellation_token,
        trace=trace,
    )
    projection = cfg["result_projection"]
    projection_args = {
        "max_items": int(projection["max_items"]),
        "max_text": int(projection["max_text_chars"]),
    }
    if is_batch:
        result = executor.execute_batch(
            action_list,
            state,
            requester=args.requester,
            task_approved=args.task_approved,
            owner_confirmed=args.owner_confirmed,
            checkpoint_store=checkpoint_store,
            plan_hash=plan_hash,
            resume_from=resume_from,
        )
        projected = [project_execution_result(item, **projection_args) for item in result["results"]]
        output_result = {
            "state": result["state"],
            "completed": result["completed"],
            "stopped_at": result["stopped_at"],
            "results": projected,
        }
    else:
        result = executor.execute_with_recovery(
            action_list[0],
            state,
            requester=args.requester,
            task_approved=args.task_approved,
            owner_confirmed=args.owner_confirmed,
        )
        output_result = project_execution_result(result, **projection_args)

    save_state(state, state_path)

    output = {
        "mode": "EXECUTE",
        "batch": is_batch,
        "planned": [planned_payload(item) for item in planned],
        "result": output_result,
        "shared_state_delta": state.delta(0),
        "state_path": str(state_path),
        "journal_path": str(journal_path),
        "checkpoint_path": str(checkpoint_path),
        "cancel_path": str(cancel_path),
        "trace_path": str(trace_path),
        "resume_from": resume_from,
        "trace_evaluation": evaluate_trace(trace.events()),
    }
    print(json.dumps(output, indent=2, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (HybridExecutionError, ExecutionControlError, CheckpointError, json.JSONDecodeError, OSError) as exc:
        print(f"hybrid execution error: {exc}", file=sys.stderr)
        raise SystemExit(2)
