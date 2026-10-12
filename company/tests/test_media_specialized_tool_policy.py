import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class MediaSpecializedToolPolicyTests(unittest.TestCase):
    def load_policy(self):
        return json.loads(
            (ROOT / "company/config/media_specialized_tool_policy.json").read_text(encoding="utf-8")
        )

    def test_specialized_tool_first_is_governing_policy(self):
        cfg = self.load_policy()
        self.assertEqual(cfg["version"], "1.0")
        self.assertEqual(cfg["policy"], "SPECIALIZED_TOOL_FIRST_CODE_LAST_FOR_CRAFT")
        self.assertIn("python_as_primary_video_editor", cfg["prohibitions"])
        self.assertIn("python_as_primary_audio_mastering_tool", cfg["prohibitions"])
        self.assertIn("generated_code_as_substitute_for_unavailable_nle_or_daw", cfg["prohibitions"])

    def test_public_master_fails_closed_without_professional_finishing(self):
        cfg = self.load_policy()
        self.assertEqual(
            cfg["gates"]["public_final_master"],
            "BLOCK_UNTIL_PRO_AUDIO_AND_NLE_FINISHING_RUNTIME_VERIFIED",
        )
        self.assertEqual(
            cfg["tool_matrix"]["picture_edit_finishing"]["status"],
            "PUBLIC_FINISHING_CAPABILITY_GAP",
        )
        self.assertEqual(
            cfg["tool_matrix"]["audio_edit_mix_master"]["status"],
            "PUBLIC_FINISHING_CAPABILITY_GAP",
        )

    def test_actual_connected_and_desktop_tools_are_recorded(self):
        cfg = self.load_policy()
        desktop = cfg["current_verified_environment"]["yassin_desktop"]
        self.assertTrue(desktop["after_effects_2026"])
        self.assertFalse(desktop["premiere_pro_2026"])
        self.assertFalse(desktop["audition_2026"])
        self.assertFalse(desktop["media_encoder_2026"])

        plugins = cfg["current_verified_environment"]["connected_plugins"]
        for name in {"descript", "runway", "openart", "canva", "figma"}:
            self.assertTrue(plugins[name])

        runway = cfg["current_verified_environment"]["runway_current_workspace"]
        self.assertTrue(runway["authenticated"])
        self.assertTrue(runway["image_models_available"])
        self.assertFalse(runway["video_models_available"])

    def test_code_role_is_orchestration_not_craft(self):
        cfg = self.load_policy()
        for key, tool in cfg["tool_matrix"].items():
            role = tool.get("code_role")
            if role:
                self.assertNotIn("primary", role.lower(), msg=key)


if __name__ == "__main__":
    unittest.main()
