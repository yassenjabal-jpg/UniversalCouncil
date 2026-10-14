from __future__ import annotations

import json
import unittest
from pathlib import Path

from company.runtime.application_profiles import (
    ApplicationProfileError,
    assess_application_request,
    validate_application_profiles,
)

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "company/config/application_profiles.json").read_text(encoding="utf-8"))


class Phase3R15ApplicationProfileTests(unittest.TestCase):
    def test_only_one_profile_exists_until_value_is_proven(self):
        self.assertTrue(validate_application_profiles(CFG))
        self.assertEqual(list(CFG["profiles"]), ["after_effects"])
        self.assertEqual(CFG["profile_growth_policy"], "PROVE_VALUE_BEFORE_ADDING_ANOTHER")

    def test_after_effects_profile_contains_canonical_fields(self):
        profile = CFG["profiles"]["after_effects"]
        for field in (
            "application",
            "version",
            "task_classes",
            "apis_scripts",
            "semantic_selectors",
            "visual_anchors",
            "known_dialogs",
            "async_states",
            "failure_modes",
            "recovery",
            "verification",
            "unsafe_actions",
            "reusable_routines",
            "checkpoint_format",
        ):
            self.assertIn(field, profile)

    def test_profile_records_current_missing_state_without_inventing_version(self):
        profile = CFG["profiles"]["after_effects"]
        self.assertEqual(profile["application"]["name"], "Adobe After Effects")
        self.assertEqual(profile["application"]["last_observed_status"], "MISSING")
        self.assertIsNone(profile["version"]["last_observed_version"])
        self.assertEqual(profile["version"]["policy"], "DETECT_BEFORE_CONTROL")

    def test_supported_bridge_actions_match_known_runner_contract(self):
        self.assertEqual(
            set(CFG["profiles"]["after_effects"]["apis_scripts"]["supported_actions"]),
            {
                "create_comp",
                "add_image",
                "add_text",
                "add_solid",
                "add_null",
                "add_camera",
                "set_3d",
                "set_parent",
                "set_blend_mode",
                "set_keyframes",
                "save_project",
                "queue_render",
            },
        )

    def test_missing_application_blocks_control_and_proves_profile_value(self):
        result = assess_application_request(
            "after_effects",
            {
                "detected": False,
                "version": None,
                "action": "create_comp",
            },
            CFG,
        )
        self.assertFalse(result["control_allowed"])
        self.assertEqual(result["classification"], "APPLICATION_NOT_DETECTED")
        self.assertEqual(result["next_step"], "detect_or_install")
        self.assertTrue(result["profile_added_value"])

    def test_detected_application_prefers_script_bridge_for_supported_action(self):
        result = assess_application_request(
            "after_effects",
            {
                "detected": True,
                "version": "26.0.0",
                "action": "create_comp",
            },
            CFG,
        )
        self.assertTrue(result["control_allowed"])
        self.assertEqual(result["preferred_task_class"], "structured_application")
        self.assertEqual(result["preferred_route"], "script_or_com")
        self.assertEqual(result["verification"]["receipt_status"], "PASS")
        self.assertEqual(result["checkpoint_format"]["kind"], "project_and_receipt")

    def test_unsupported_action_fails_closed(self):
        with self.assertRaises(ApplicationProfileError):
            assess_application_request(
                "after_effects",
                {
                    "detected": True,
                    "version": "26.0.0",
                    "action": "close_without_save",
                },
                CFG,
            )

    def test_detected_application_requires_observed_version(self):
        with self.assertRaises(ApplicationProfileError):
            assess_application_request(
                "after_effects",
                {
                    "detected": True,
                    "version": None,
                    "action": "create_comp",
                },
                CFG,
            )


if __name__ == "__main__":
    unittest.main()
