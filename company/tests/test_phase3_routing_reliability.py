from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from company.runtime.hybrid_execution import (
    ExecutionPath,
    build_routine_fingerprint,
    choose_path,
    eligible_for_routine_graduation,
)

ROOT = Path(__file__).resolve().parents[2]
BASE_CFG = json.loads((ROOT / "company/config/hybrid_execution.json").read_text(encoding="utf-8"))


class Phase3RoutingReliabilityTests(unittest.TestCase):
    def test_f09_host_support_follows_configured_profile_order(self):
        cfg = copy.deepcopy(BASE_CFG)
        cfg["routing_profiles"]["host_support"]["order"] = [
            ExecutionPath.NATIVE.value,
            ExecutionPath.DC.value,
            ExecutionPath.ROUTINE.value,
        ]
        action = {
            "task_class": "host_support",
            "native_available": True,
            "dc_capable": True,
            "routine_available": True,
        }
        self.assertEqual(choose_path(action, cfg), ExecutionPath.NATIVE)

    def test_f09_external_service_uses_its_own_profile(self):
        action = {
            "task_class": "external_service",
            "native_available": True,
            "dc_capable": True,
            "routine_available": True,
        }
        self.assertEqual(choose_path(action, BASE_CFG), ExecutionPath.NATIVE)

    def test_f09_interactive_safety_invariant_survives_profile_configuration(self):
        cfg = copy.deepcopy(BASE_CFG)
        cfg["routing_profiles"]["interactive_app"]["order"] = [
            ExecutionPath.DC.value,
            ExecutionPath.GUI_UIA.value,
            ExecutionPath.GUI_VISUAL.value,
        ]
        with self.assertRaises(ValueError):
            choose_path(
                {
                    "task_class": "interactive_app",
                    "interactive_app": True,
                    "dc_capable": True,
                },
                cfg,
            )

    def _history_item(self, run_id: str, *, app_version: str = "1.0") -> dict:
        return {
            "state": "SUCCEEDED",
            "verified": True,
            "accidental_action": False,
            "run_id": run_id,
            "app_id": "demo-app",
            "app_version": app_version,
            "task_class": "interactive_app",
            "action_schema": "set_value:v1",
            "risk": "T2_LOCAL_STATE_CHANGE",
            "verifier_id": "gui_post_state:v1",
            "environment_id": "YASSIN:win11",
            "authority_policy_id": "tool-authority:1.0",
        }

    def test_f10_minimal_success_rows_no_longer_graduate(self):
        minimal = [
            {"state": "SUCCEEDED", "verified": True},
            {"state": "SUCCEEDED", "verified": True},
            {"state": "SUCCEEDED", "verified": True},
        ]
        self.assertFalse(eligible_for_routine_graduation(minimal, BASE_CFG))

    def test_f10_same_context_three_distinct_verified_runs_can_graduate(self):
        history = [self._history_item(f"run-{index}") for index in range(3)]
        self.assertTrue(eligible_for_routine_graduation(history, BASE_CFG))

    def test_f10_context_drift_blocks_graduation(self):
        history = [
            self._history_item("run-1"),
            self._history_item("run-2"),
            self._history_item("run-3", app_version="2.0"),
        ]
        self.assertFalse(eligible_for_routine_graduation(history, BASE_CFG))

    def test_f10_duplicate_run_ids_do_not_count_as_repeats(self):
        history = [self._history_item("same-run") for _ in range(3)]
        self.assertFalse(eligible_for_routine_graduation(history, BASE_CFG))

    def test_f10_fingerprint_is_stable_and_context_sensitive(self):
        first = self._history_item("run-1")
        second = self._history_item("run-2")
        self.assertEqual(
            build_routine_fingerprint(first, BASE_CFG),
            build_routine_fingerprint(second, BASE_CFG),
        )
        changed = self._history_item("run-3", app_version="2.0")
        self.assertNotEqual(
            build_routine_fingerprint(first, BASE_CFG),
            build_routine_fingerprint(changed, BASE_CFG),
        )


if __name__ == "__main__":
    unittest.main()
