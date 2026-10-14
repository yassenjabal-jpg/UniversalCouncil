import copy
import json
import unittest
from pathlib import Path

from company.runtime.lean_video_production import ProductionWorkflowError, validate_production_config

ROOT = Path(__file__).resolve().parents[2]


class MediaSpecializedToolPolicyTests(unittest.TestCase):
    def setUp(self):
        self.cfg = json.loads((ROOT / "company/config/media_specialized_tool_policy.json").read_text(encoding="utf-8"))
        self.channel = json.loads((ROOT / self.cfg["governing_workflow"]).read_text(encoding="utf-8"))

    def test_exactly_three_gates_and_two_native_editors(self):
        cfg = self.cfg
        self.assertEqual(cfg["version"], "2.0")
        self.assertEqual(cfg["quality_gates"], ["Preproduction Lock", "Rough Cut Review", "Final QC"])
        self.assertEqual(cfg["quality_gates"], self.channel["quality_gates"])
        self.assertEqual(cfg["editing_routes"], self.channel["production_system"]["editing_routes"])
        for name in [
            "motion_graphics_compositing",
            "dialogue_cleanup_text_edit",
            "picture_edit_finishing",
            "audio_edit_mix_master",
            "captions_transcript",
            "render_export",
        ]:
            with self.subTest(stage=name):
                tool = cfg["tool_matrix"][name]
                self.assertEqual(tool["preferred"], ["Descript"])
                self.assertEqual(tool["backup"], ["Adobe After Effects 2026 native automation"])
                self.assertEqual(tool["status"], "DELIVERY_PENDING_SYSTEM_PILOT")
        self.assertFalse(cfg["editing_routes"]["gui_retry_loops"])
        self.assertEqual(cfg["editing_routes"]["max_routes"], 2)

    def test_route_and_gate_mutations_are_rejected_by_governing_runtime(self):
        for field, replacement in [
            ("max_routes", 3),
            ("gui_retry_loops", True),
            ("max_backup_activations", 2),
            ("backup_requires_current_probe", False),
            ("max_primary_diagnosis_minutes", 60),
            ("tertiary", {"tool": "Another editor"}),
        ]:
            with self.subTest(field=field):
                cfg = copy.deepcopy(self.channel)
                cfg["production_system"]["editing_routes"][field] = replacement
                with self.assertRaises(ProductionWorkflowError):
                    validate_production_config(cfg)
        cfg = copy.deepcopy(self.channel)
        cfg["quality_gates"].append("Per Frame Review")
        with self.assertRaises(ProductionWorkflowError):
            validate_production_config(cfg)

    def test_connectivity_does_not_claim_delivery_quality(self):
        routes = self.cfg["editing_routes"]
        self.assertEqual(routes["primary"]["connection_status"], "LIVE_VERIFIED")
        self.assertEqual(routes["primary"]["delivery_status"], "UNVERIFIED_PENDING_SYSTEM_PILOT")
        self.assertEqual(routes["backup"]["connection_status"], "REVERIFY_ON_ACTIVATION")
        self.assertEqual(routes["backup"]["delivery_status"], "HISTORICAL_5_SECOND_BENCHMARK_ONLY")
        for name in ["primary", "backup"]:
            self.assertTrue((ROOT / routes[name]["evidence"]).is_file())
        self.assertIn("historical", self.cfg["current_verified_environment"]["historical_environment_note"])
        self.assertFalse(self.cfg["current_verified_environment"]["runway_current_workspace"]["video_models_available"])
        self.assertEqual(self.cfg["tool_matrix"]["ai_video_generation"]["status"], "PARTIAL_CAPABILITY")

    def test_generation_protections_are_embedded_in_preproduction(self):
        still = self.cfg["tool_matrix"]["still_image_generation"]
        for field in [
            "generation_brief_required",
            "creative_prompt_rewrite_by_executor_forbidden",
            "context_isolation_required",
            "multi_panel_thumbnail_output_forbidden",
        ]:
            self.assertIs(still[field], True)
        for field in [
            "official_thumbnail_concepts_per_episode",
            "generated_thumbnail_assets_per_episode",
            "generation_jobs_per_episode_thumbnail_stage",
        ]:
            self.assertEqual(still[field], 1)
        for kind in ["still_image_generation", "ai_video_generation"]:
            self.assertEqual(self.cfg["tool_matrix"][kind]["approval_scope"], "ASSET_PACK_PREPRODUCTION_LOCK")
        self.assertNotIn("gates", self.cfg)
        self.assertNotIn("current_motion_state", self.cfg)

    def test_public_master_requires_actual_qc_and_publish_remains_blocked(self):
        constraints = self.cfg["execution_constraints"]
        self.assertEqual(constraints["automatic_publish"], "BLOCK")
        self.assertEqual(constraints["generation_without_preproduction_lock"], "BLOCK")
        self.assertEqual(constraints["thumbnail_multiple_concepts_or_assets"], "BLOCK")
        self.assertEqual(constraints["gui_retry_loops"], "FORBIDDEN")
        self.assertEqual(
            constraints["public_final_master"], "REQUIRES_EXACT_EXPORT_FINAL_QC_NOT_SEPARATE_NLE_DAW_BRANDS"
        )

    def test_code_orchestrates_and_does_not_replace_craft(self):
        for prohibition in [
            "python_as_primary_video_editor",
            "python_as_primary_audio_mastering_tool",
            "python_as_primary_motion_design_tool",
            "ffmpeg_as_primary_creative_editor",
            "generated_code_as_substitute_for_unavailable_nle_or_daw",
        ]:
            self.assertIn(prohibition, self.cfg["prohibitions"])
        for stage, tool in self.cfg["tool_matrix"].items():
            if "code_role" in tool:
                self.assertNotIn("primary", tool["code_role"].lower(), msg=stage)
        self.assertTrue(self.cfg["exception_rule"]["owner_approval_required"])
        self.assertTrue(self.cfg["exception_rule"]["must_be_time_bounded"])
        self.assertTrue(self.cfg["exception_rule"]["must_not_become_default"])


if __name__ == "__main__":
    unittest.main()
