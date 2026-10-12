import json
import unittest
from pathlib import Path

from company.runtime.media_controls import (
    REQUIRED_MEDIA_FUNCTIONS,
    REQUIRED_PILOT_METRICS,
    MediaControlError,
    validate_media_pilot_record,
    validate_media_scale_request,
    validate_media_team,
)

ROOT = Path(__file__).resolve().parents[2]


class MediaCapabilityTests(unittest.TestCase):
    def load_config(self):
        return json.loads((ROOT / "company/config/media_venture.json").read_text(encoding="utf-8"))

    def base_metrics(self):
        return sorted(REQUIRED_PILOT_METRICS)

    def test_required_media_functions_exist(self):
        cfg = self.load_config()
        self.assertTrue(validate_media_team(cfg))
        ids = {x["id"] for x in cfg["production_functions"]}
        self.assertEqual(ids, REQUIRED_MEDIA_FUNCTIONS)

    def test_audio_roles_are_distinct_and_active(self):
        cfg = self.load_config()
        by_id = {x["id"]: x for x in cfg["production_functions"]}
        self.assertEqual(by_id["music_sound_supervisor"]["default_status"], "ACTIVE_FOR_MEDIA_PILOT")
        self.assertEqual(by_id["dialogue_mix_engineer"]["default_status"], "ACTIVE_FOR_MEDIA_PILOT")
        self.assertNotEqual(
            set(by_id["music_sound_supervisor"]["owns"]),
            set(by_id["dialogue_mix_engineer"]["owns"]),
        )
        self.assertEqual(by_id["localization_producer"]["default_status"], "ON_DEMAND")
        self.assertIn(
            "music_sound_supervisor_does_not_self_approve_final_mix_qc",
            cfg["function_independence_rules"],
        )
        self.assertIn(
            "owner_voice_approval_is_separate_from_technical_mix_approval",
            cfg["function_independence_rules"],
        )

    def test_media_toolchain_is_bounded_and_honest(self):
        cfg = self.load_config()
        self.assertFalse(cfg["live_publish_authority"])
        self.assertEqual(cfg["media_toolchain"]["platform_publishing"], "CAPABILITY_GAP")
        self.assertEqual(cfg["media_toolchain"]["ai_video_generation"], "NEEDS_RUNTIME_VERIFICATION")
        self.assertEqual(cfg["media_toolchain"]["video_editing"], "PARTIAL_RUNTIME_VERIFIED")
        self.assertEqual(cfg["media_toolchain"]["after_effects_motion_assembly"], "RUNTIME_VERIFIED")
        self.assertEqual(
            cfg["media_toolchain"]["music_supervision"],
            "PROCESS_DEFINED_SPECIALIZED_TOOL_REQUIRED",
        )
        self.assertEqual(
            cfg["media_toolchain"]["mix_mastering"],
            "PUBLIC_FINISHING_CAPABILITY_GAP",
        )
        self.assertEqual(cfg["media_toolchain"]["dialogue_cleanup"], "CONNECTED_DESCRIPT_AVAILABLE")
        self.assertEqual(
            cfg["media_toolchain"]["picture_edit_finishing"],
            "PUBLIC_FINISHING_CAPABILITY_GAP",
        )
        self.assertEqual(
            cfg["media_toolchain"]["runway_video_generation"],
            "BLOCKED_BY_CURRENT_PLAN_NO_VIDEO_MODELS",
        )
        ae = cfg["runtime_evidence"]["after_effects_2026"]
        self.assertEqual(ae["status"], "RUNTIME_VERIFIED")
        self.assertEqual(ae["host"], "YASSIN")
        self.assertEqual(ae["cli_probe"], "PASS")
        self.assertEqual(ae["execution_receipt"], "PASS_COMPLETED")

    def test_after_effects_runtime_evidence_is_durable_and_bounded(self):
        cfg = self.load_config()
        ae = cfg["runtime_evidence"]["after_effects_2026"]
        evidence = ROOT / ae["evidence_document"]
        self.assertTrue(evidence.exists())
        body = evidence.read_text(encoding="utf-8")
        self.assertIn("PARTIAL_RUNTIME_VERIFIED", body)
        self.assertIn("AE_CLI_PROBE=PASS", body)
        self.assertIn("PASS", body)
        self.assertIn("Premiere Pro end-to-end editing", body)
        self.assertEqual(
            ae["control_bridge_commit"],
            "42544d3a7bfb0fcced63962c45a40dcafd692572",
        )

    def test_scale_is_forbidden_before_three_videos(self):
        record = {
            "videos_completed": 2,
            "metrics": self.base_metrics(),
            "hr_review_status": "KEEP",
            "scale_decision": "SCALE_CANDIDATE",
        }
        with self.assertRaises(MediaControlError):
            validate_media_scale_request(record)

    def test_three_video_pilot_requires_audio_and_cost_quality_metrics(self):
        record = {
            "videos_completed": 3,
            "metrics": ["production_time_per_video"],
            "hr_review_status": "KEEP",
            "scale_decision": "HOLD",
        }
        with self.assertRaises(MediaControlError):
            validate_media_pilot_record(record)

        record["metrics"] = self.base_metrics()
        self.assertTrue(validate_media_pilot_record(record))

    def test_published_pilot_requires_audience_metrics(self):
        base = {
            "videos_completed": 3,
            "metrics": self.base_metrics(),
            "hr_review_status": "KEEP",
            "scale_decision": "CONTINUE_PILOT",
        }
        with self.assertRaises(MediaControlError):
            validate_media_pilot_record(base, published=True)

        base["metrics"] += [
            "ctr",
            "first_30_second_retention",
            "average_percentage_viewed",
            "watch_time",
            "subscribers_per_video",
            "returning_viewers",
        ]
        self.assertTrue(validate_media_pilot_record(base, published=True))

    def test_valid_scale_candidate_passes_after_pilot(self):
        record = {
            "videos_completed": 3,
            "metrics": self.base_metrics(),
            "hr_review_status": "KEEP",
            "scale_decision": "SCALE_CANDIDATE",
        }
        self.assertTrue(validate_media_scale_request(record))


if __name__ == "__main__":
    unittest.main()
