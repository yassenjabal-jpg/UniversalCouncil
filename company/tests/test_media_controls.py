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

    def test_lean_team_has_five_authorities_and_on_demand_specialists(self):
        cfg = self.load_config()
        self.assertTrue(validate_media_team(cfg))
        self.assertEqual({f["id"] for f in cfg["production_functions"]}, REQUIRED_MEDIA_FUNCTIONS)
        self.assertEqual(sum(f["default_status"] == "STAGE_AUTHORITY" for f in cfg["production_functions"]), 5)
        self.assertFalse(cfg["pilot"]["blocks_episode_production"])
        self.assertEqual(cfg["system_pilot"]["count"], 1)

    def test_team_contract_rejects_bureaucracy_false_proof_and_missing_authority(self):
        mutations = [
            lambda c: c.update(version="old"),
            lambda c: c["production_functions"].pop(),
            lambda c: c["production_functions"].append(dict(c["production_functions"][0])),
            lambda c: c["production_functions"][0].update(default_status="ON_DEMAND"),
            lambda c: next(f for f in c["production_functions"] if f["id"] == "independent_fact_checker").update(
                default_status="STAGE_AUTHORITY"
            ),
            lambda c: c.update(function_independence_rules=[]),
            lambda c: c.update(production_workflow_config="other.json"),
            lambda c: c.update(visual_production_system={"pilot_ladder": ["P0"]}),
            lambda c: c["system_pilot"].update(count=2),
            lambda c: c.update(live_publish_authority=True),
            lambda c: c["pilot"].update(blocks_episode_production=True),
            lambda c: c["pilot"].update(required_before_scale=False),
            lambda c: c["pilot"].update(video_count=2),
            lambda c: c["media_toolchain"].update(video_editing="DESCRIPT_PRIMARY"),
            lambda c: c["media_toolchain"].update(after_effects_motion_assembly="BACKUP_ONLY"),
            lambda c: c["media_toolchain"].update(descript_editing="PRIMARY_DELIVERY"),
        ]
        for key in self.load_config()["visual_generation_brief_capability"]:
            if key in {
                "permanent_role",
                "final_approver",
                "approval_scope",
                "preproduction_lock_required",
                "no_prompt_no_generation",
                "tool_creative_rewrite_forbidden",
                "one_generated_thumbnail_asset_per_episode",
                "multi_panel_thumbnail_output_forbidden",
            }:
                mutations.append(lambda c, key=key: c["visual_generation_brief_capability"].pop(key))
        for mutate in mutations:
            cfg = self.load_config()
            mutate(cfg)
            with self.assertRaises(MediaControlError):
                validate_media_team(cfg)

    def test_benchmark_metrics_are_required_before_scale(self):
        for metric in {
            "schedule_variance",
            "milestone_slips",
            "script_revision_rounds",
            "fact_check_defects_caught_prelock",
            "visual_story_case_rework",
            "thumbnail_variants_produced",
            "production_readiness_failures",
            "edit_rework_after_script_lock",
            "generation_brief_rework_rounds",
            "prompt_drift_defects",
        }:
            self.assertIn(metric, REQUIRED_PILOT_METRICS)

    def test_scale_is_forbidden_before_three_videos(self):
        record = {
            "videos_completed": 2,
            "metrics": self.base_metrics(),
            "hr_review_status": "KEEP",
            "scale_decision": "SCALE_CANDIDATE",
        }
        with self.assertRaises(MediaControlError):
            validate_media_scale_request(record)

    def test_three_video_pilot_requires_all_professional_metrics(self):
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

    def test_pilot_record_invalid_statuses_and_missing_fields_fail_closed(self):
        base = {
            "videos_completed": 3,
            "metrics": self.base_metrics(),
            "hr_review_status": "KEEP",
            "scale_decision": "HOLD",
        }

        missing = dict(base)
        missing.pop("metrics")
        with self.assertRaises(MediaControlError):
            validate_media_pilot_record(missing)

        invalid_hr = dict(base)
        invalid_hr["hr_review_status"] = "SELF_APPROVED"
        with self.assertRaises(MediaControlError):
            validate_media_pilot_record(invalid_hr)

        invalid_scale = dict(base)
        invalid_scale["scale_decision"] = "AUTO_SCALE"
        with self.assertRaises(MediaControlError):
            validate_media_pilot_record(invalid_scale)

        with self.assertRaises(MediaControlError):
            validate_media_scale_request(base)


if __name__ == "__main__":
    unittest.main()
