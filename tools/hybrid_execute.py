from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
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

CONFIG = ROOT / "company/config/hybrid_execution.json"
TOOL_AUTHORITY = ROOT / "company/config/tool_authority.json"


def planned_payload(planned):
    data = asdict(planned)
    data["path"] = planned.path.value
    data["risk"] = planned.risk.value
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Universal Council hybrid DC+GUI execution prototype")
    parser.add_argument("action", type=Path, help="JSON action specification")
    parser.add_argument("--execute", action="store_true", help="dispatch the planned action")
    parser.add_argument("--task-approved", action="store_true")
    parser.add_argument("--owner-confirmed", action="store_true")
    parser.add_argument("--requester", default="technical_operator")
    parser.add_argument("--state", type=Path)
    args = parser.parse_args()

    action = json.loads(args.action.read_text(encoding="utf-8"))
    cfg = load_config(CONFIG)
    authority_registry = json.loads(TOOL_AUTHORITY.read_text(encoding="utf-8"))
    planned = plan_action(action, cfg)

    if not args.execute:
        print(json.dumps({"mode": "PLAN_ONLY", "planned": planned_payload(planned)}, indent=2, ensure_ascii=False))
        return 0

    if args.state and args.state.exists():
        state = load_state(args.state)
    else:
        state = SharedExecutionState(task_id=str(action.get("task_id") or action["id"]))

    gui_adapter = None
    if planned.path.value.startswith("gui_"):
        gui_adapter = CouncilVideoStudioGuiAdapter(cfg)
    executor = HybridExecutor(
        cfg,
        gui_adapter=gui_adapter,
        authority_registry=authority_registry,
    )
    result = executor.execute(
        action,
        state,
        requester=args.requester,
        task_approved=args.task_approved,
        owner_confirmed=args.owner_confirmed,
    )
    if args.state:
        save_state(state, args.state)

    output = {
        "mode": "EXECUTE",
        "planned": planned_payload(planned),
        "state": result["state"],
        "result": {key: value for key, value in result.items() if key not in {"planned"}},
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
