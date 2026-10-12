from __future__ import annotations

import json
from collections import Counter
from typing import Any


DEFAULT_MAX_ITEMS = 6
DEFAULT_MAX_TEXT = 320


def _clip(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"...<{len(text) - limit} chars omitted>"


def _project_json(value: Any, *, max_items: int, max_text: int) -> Any:
    if isinstance(value, list):
        projected = [_project_json(item, max_items=max_items, max_text=max_text) for item in value[:max_items]]
        if len(value) > max_items:
            projected.append({"omitted_items": len(value) - max_items})
        return projected
    if isinstance(value, dict):
        preferred = {}
        for key in (
            "state",
            "action",
            "returncode",
            "processName",
            "className",
            "isForeground",
            "elementId",
            "text",
            "value",
            "name",
            "automationId",
            "selector",
            "capture_path",
        ):
            if key in value:
                preferred[key] = _project_json(value[key], max_items=max_items, max_text=max_text)
        if preferred:
            return preferred
        keys = list(value)[:max_items]
        result = {key: _project_json(value[key], max_items=max_items, max_text=max_text) for key in keys}
        if len(value) > max_items:
            result["_omitted_keys"] = len(value) - max_items
        return result
    if isinstance(value, str):
        return _clip(value, max_text)
    return value


def project_text_payload(
    text: str, *, max_items: int = DEFAULT_MAX_ITEMS, max_text: int = DEFAULT_MAX_TEXT
) -> dict[str, Any]:
    stripped = text.strip()
    if not stripped:
        return {"kind": "empty"}
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        return {
            "kind": "text",
            "chars": len(text),
            "preview": _clip(text, max_text),
        }
    if isinstance(parsed, list):
        return {
            "kind": "json_list",
            "items": len(parsed),
            "sample": _project_json(parsed, max_items=max_items, max_text=max_text),
        }
    return {
        "kind": "json",
        "value": _project_json(parsed, max_items=max_items, max_text=max_text),
    }


def _project_window_list(text: str, *, max_items: int) -> dict[str, Any] | None:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, list):
        return None

    names = [item.get("processName") for item in parsed if isinstance(item, dict) and item.get("processName")]
    process_counts = dict(Counter(names).most_common(max_items))
    foreground = next(
        (
            {
                "processName": item.get("processName"),
                "className": item.get("className"),
            }
            for item in parsed
            if isinstance(item, dict) and item.get("isForeground")
        ),
        None,
    )
    return {
        "kind": "window_list",
        "items": len(parsed),
        "process_counts": process_counts,
        "foreground": foreground,
    }


def project_provider_result(
    result: dict[str, Any],
    *,
    max_items: int = DEFAULT_MAX_ITEMS,
    max_text: int = DEFAULT_MAX_TEXT,
) -> dict[str, Any]:
    projected: dict[str, Any] = {}
    for key in ("state", "plane", "returncode", "stderr"):
        if key in result and result[key] not in (None, ""):
            projected[key] = _project_json(result[key], max_items=max_items, max_text=max_text)

    bridge = result.get("bridge_result")
    if isinstance(bridge, dict):
        action = bridge.get("action")
        if isinstance(action, dict):
            projected["bridge"] = {
                "action": action.get("action"),
                "returncode": action.get("returncode"),
                "capture_path": action.get("capture_path"),
            }
            stdout = action.get("stdout")
            if isinstance(stdout, str):
                if action.get("action") == "list_windows":
                    window_summary = _project_window_list(stdout, max_items=max_items)
                else:
                    window_summary = None
                projected["bridge"]["stdout"] = window_summary or project_text_payload(
                    stdout,
                    max_items=max_items,
                    max_text=max_text,
                )
            stderr = action.get("stderr")
            if stderr:
                projected["bridge"]["stderr"] = _clip(str(stderr), max_text)

    host_request = result.get("host_request")
    if isinstance(host_request, dict):
        projected["host_request"] = {
            "operation": host_request.get("operation"),
            "payload": _project_json(
                host_request.get("payload"),
                max_items=max_items,
                max_text=max_text,
            ),
        }

    if not projected:
        projected = _project_json(result, max_items=max_items, max_text=max_text)
    return projected


def project_execution_result(
    execution: dict[str, Any],
    *,
    max_items: int = DEFAULT_MAX_ITEMS,
    max_text: int = DEFAULT_MAX_TEXT,
) -> dict[str, Any]:
    output: dict[str, Any] = {"state": execution.get("state")}
    if execution.get("reason"):
        output["reason"] = _clip(str(execution["reason"]), max_text)
    result = execution.get("result")
    if isinstance(result, dict):
        output["result"] = project_provider_result(result, max_items=max_items, max_text=max_text)
    verification = execution.get("verification")
    if isinstance(verification, dict):
        output["verification"] = _project_json(verification, max_items=max_items, max_text=max_text)
    return output
