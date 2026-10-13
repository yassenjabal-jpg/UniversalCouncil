from __future__ import annotations

import json
from typing import Any

from company.runtime.hybrid_execution import Adapter, HybridExecutionError, ResultState


def _extract_bridge_stdout(result: dict[str, Any]) -> str:
    bridge = result.get("bridge_result")
    if not isinstance(bridge, dict):
        raise HybridExecutionError("verification bridge result is missing")
    action = bridge.get("action")
    if not isinstance(action, dict):
        raise HybridExecutionError("verification action result is missing")
    stdout = action.get("stdout")
    if not isinstance(stdout, str):
        raise HybridExecutionError("verification stdout is missing")
    return stdout


class GuiPostStateVerifier:
    def __init__(self, gui_adapter: Adapter):
        self.gui_adapter = gui_adapter

    def verify(self, action: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
        spec = action.get("verify")
        if not isinstance(spec, dict):
            return {"verified": False, "mode": "missing_verify_spec"}

        request = spec.get("request")
        expect = spec.get("expect")
        if not isinstance(request, dict) or not isinstance(expect, dict) or not expect:
            return {"verified": False, "mode": "invalid_verify_spec"}

        probe = self.gui_adapter.dispatch({"gui_request": request})
        if probe.get("state") != ResultState.SUCCEEDED.value:
            return {
                "verified": False,
                "mode": "gui_post_state_probe_failed",
                "probe_state": probe.get("state"),
            }

        try:
            payload = json.loads(_extract_bridge_stdout(probe))
        except (json.JSONDecodeError, HybridExecutionError) as exc:
            return {
                "verified": False,
                "mode": "gui_post_state_unreadable",
                "error": str(exc),
            }

        checks: dict[str, Any] = {}
        verified = True
        for key, expected in expect.items():
            actual = payload.get(key) if isinstance(payload, dict) else None
            match = actual == expected
            checks[key] = {
                "match": match,
                "expected": expected,
                "actual": actual,
            }
            verified = verified and match

        return {
            "verified": verified,
            "mode": "independent_gui_post_state",
            "checks": checks,
        }
