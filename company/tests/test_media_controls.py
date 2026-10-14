import json
import unittest
from pathlib import Path

from company.runtime.media_controls import (
    REQUIRED_MEDIA_FUNCTIONS,
    REQUIRED_PILOT_METRICS,
    STUDIO_DEPARTMENTS,
    MediaControlError,
    validate_media_pilot_record,
    validate_media_scale_request,
    validate_media_team,
    validate_studio_model,
)

ROOT = Path(__file__).resolve().parents[2]


class MediaCapabilityTests(unittest.TestCase):
    def load_config(self):
        return json.loads((ROOT / "company/config/media_venture.json").read_text(encoding="utf-8"))

    def base_metrics(self):
        return sorted(REQUIRED_PILOT_METRICS)

    def test_lean_team_has_five_authorities_and_mandatory_craft_specialists(self):
        cfg = self.load_config()
        self.assertTrue(validate_media_team(cfg))
        self.assertEqual({f["id"] for f in cfg["production_functions"]}, REQUIRED_MEDIA_FUNCTIONS)
        self.assertEqual(sum(f["default_status"] == "STAGE_AUTHORITY" for f in cfg["production_functions"]), 5)
        self.assertEqual(
            sum(f["default_status"] == "MANDATORY_CRAFT_CONTRIBUTOR" for f in cfg["production_functions"]),
            6,
        )
        self.assertEqual(
            sum(f["default_status"] == "CONDITIONAL_CRAFT_CONTRIBUTOR" for f in cfg["production_functions"]),
            1,
        )
        self.assertEqual(
            cfg["craft_contributor_contract_pointer"],
            "company/config/channel_operating_system.json#production_system.craft_contributor_contract",
        )
        self.assertEqual(cfg["operating_identity"]["name_ar"], "الاستوديو")
        self.assertEqual(cfg["operating_identity"]["name_en"], "The Studio")
        self.assertEqual(cfg["studio_departments"], STUDIO_DEPARTMENTS)
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
            lambda c: next(f for f in c["production_functions"] if f["id"] == "script_voice_director").update(
                default_status="ON_DEMAND"
            ),
            lambda c: next(f for f in c["production_functions"] if f["id"] == "localization_producer").update(
                default_status="ON_DEMAND"
            ),
            lambda c: c.update(craft_contributor_contract_pointer="wrong"),
            lambda c: c["operating_identity"].update(name_en="Council"),
            lambda c: c.update(studio_departments={}),
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

    def test_studio_operating_model_has_five_departments_episode_pod_and_three_gates(self):
        model = json.loads((ROOT / "company/config/studio_operating_model.json").read_text(encoding="utf-8"))
        self.assertTrue(validate_studio_model(model))
        self.assertEqual(model["identity"]["name_ar"], "الاستوديو")
        self.assertIn("technical_operations", model["shared_studio_services"])
        self.assertEqual(
            model["shared_studio_services"]["technical_operations"]["roles"],
            ["Technical Operator"],
        )
        self.assertEqual(
            [stage["id"] for stage in model["production_flow"]],
            [
                "research_script",
                "visual_direction",
                "asset_pack",
                "edit_motion",
                "final_qc",
            ],
        )
        self.assertEqual(
            [gate["technical_id"] for gate in model["gates"]],
            [
                "Preproduction Lock",
                "Rough Cut Review",
                "Final QC",
            ],
        )

        mutations = [
            lambda m: m["identity"].update(name_en="Council"),
            lambda m: m["departments"].pop("post_production"),
            lambda m: m.update(shared_studio_services={}),
            lambda m: m["episode_pod"].update(required_core=[]),
            lambda m: m["production_flow"].append({"id": "extra_stage"}),
            lambda m: m["gates"].append({"technical_id": "Fourth Gate", "placement": "after_export"}),
            lambda m: m.update(doctrine=[]),
        ]
        for mutate in mutations:
            candidate = json.loads(json.dumps(model))
            mutate(candidate)
            with self.assertRaises(MediaControlError):
                validate_studio_model(candidate)

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
