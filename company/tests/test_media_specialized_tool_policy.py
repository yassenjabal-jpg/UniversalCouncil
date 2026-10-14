import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class MediaSpecializedToolPolicyTests(unittest.TestCase):
    def load_policy(self):
        return json.loads((ROOT / "company/config/media_specialized_tool_policy.json").read_text(encoding="utf-8"))

    def test_specialized_tool_first_is_governing_policy(self):
        cfg = self.load_policy()
        self.assertEqual(cfg["version"], "1.4")
        self.assertEqual(cfg["policy"], "SPECIALIZED_TOOL_FIRST_CODE_LAST_FOR_CRAFT")
        self.assertIn("python_as_primary_video_editor", cfg["prohibitions"])
        self.assertIn("python_as_primary_audio_mastering_tool", cfg["prohibitions"])
        self.assertIn("generated_code_as_substitute_for_unavailable_nle_or_daw", cfg["prohibitions"])
        still = cfg["tool_matrix"]["still_image_generation"]
        self.assertTrue(still["generation_brief_required"])
        self.assertTrue(still["anti_slop_approval_required"])
        self.assertTrue(still["creative_prompt_rewrite_by_executor_forbidden"])
        self.assertEqual(still["official_thumbnail_concepts_per_episode"], 1)
        self.assertEqual(still["generated_thumbnail_assets_per_episode"], 1)
        self.assertEqual(still["generation_jobs_per_episode_thumbnail_stage"], 1)
        self.assertTrue(still["context_isolation_required"])
        self.assertTrue(still["multi_panel_thumbnail_output_forbidden"])
        self.assertEqual(cfg["gates"]["thumbnail_generation_multiple_concepts_or_assets"], "BLOCK")
        self.assertEqual(cfg["gates"]["thumbnail_generation_multi_panel_output"], "BLOCK")
        video = cfg["tool_matrix"]["ai_video_generation"]
        self.assertTrue(video["generation_brief_required"])
        self.assertTrue(video["anti_slop_approval_required"])
        self.assertEqual(cfg["gates"]["visual_generation_without_approved_brief"], "BLOCK")
        self.assertEqual(cfg["gates"]["visual_generation_without_anti_slop_approval"], "BLOCK")

    def test_visual_tool_qualification_prefers_quality_over_credits(self):
        cfg = self.load_policy()
        qualification = cfg["tool_qualification"]
        self.assertTrue(qualification["required_before_primary_visual_generator_lock"])
        self.assertEqual(qualification["comparison_contract"], "SAME_FRAME_SAME_BRIEF")
        self.assertGreaterEqual(qualification["minimum_viable_candidates"], 2)
        self.assertEqual(sum(qualification["weights"].values()), 100)
        self.assertGreaterEqual(
            qualification["weights"]["prompt_fidelity"] + qualification["weights"]["style_consistency"],
            50,
        )
        self.assertTrue(qualification["remaining_credits_must_not_select_primary_tool"])
        self.assertEqual(qualification["primary_tool_state"], "QUALIFIED_PRIMARY")
        self.assertEqual(qualification["backup_tool_state"], "QUALIFIED_BACKUP")
        self.assertEqual(qualification["primary_tool"], "runway:nano-banana-2-lite")
        self.assertEqual(qualification["backup_tool"], "runway:nano-banana-pro")
        self.assertGreater(qualification["primary_score"], qualification["backup_score"])
        self.assertTrue(qualification["qualification_artifact"])
        self.assertEqual(cfg["gates"]["visual_system_lock_without_tool_qualification"], "BLOCK")
        self.assertEqual(cfg["gates"]["full_length_episode_before_p2_visual_pilot"], "BLOCK")

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
