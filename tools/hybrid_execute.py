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
    if args.state and args.state.exists():
        state = load_state(args.state)
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
        )
        projected = [project_execution_result(item, **projection_args) for item in result["results"]]
        output_result = {
            "state": result["state"],
            "completed": result["completed"],
            "stopped_at": result["stopped_at"],
            "results": projected,
        }
    else:
        result = executor.execute(
            action_list[0],
            state,
            requester=args.requester,
            task_approved=args.task_approved,
            owner_confirmed=args.owner_confirmed,
        )
        output_result = project_execution_result(result, **projection_args)

    if args.state:
        save_state(state, args.state)

    output = {
        "mode": "EXECUTE",
        "batch": is_batch,
        "planned": [planned_payload(item) for item in planned],
        "result": output_result,
        "shared_state_delta": state.delta(0),
    }
    print(json.dumps(output, indent=2, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (HybridExecutionError, json.JSONDecodeError, OSError) as exc:
        print(f"hybrid execution error: {exc}", file=sys.stderr)
        raise SystemExit(2)
