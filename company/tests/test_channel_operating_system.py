import copy
import json
import unittest
from pathlib import Path

from company.runtime.channel_operating_system import (
    ChannelOperatingSystemError,
    REQUIRED_AUDIO_STEMS,
    REQUIRED_PRODUCTION_ROLES,
    REQUIRED_WORKFLOW,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[2]
CONFIG = json.loads((ROOT / "company" / "config" / "channel_operating_system.json").read_text(encoding="utf-8"))


class ChannelOperatingSystemTests(unittest.TestCase):
    def test_current_config_is_valid(self):
        self.assertTrue(validate_config(copy.deepcopy(CONFIG)))

    def test_topic_weights_total_100(self):
        self.assertEqual(sum(CONFIG["topic_scoring"]["fields"].values()), 100)

    def test_workflow_is_exact_and_ordered(self):
        self.assertEqual(CONFIG["workflow"], REQUIRED_WORKFLOW)
        self.assertLess(
            CONFIG["workflow"].index("audio_spotting_and_sonic_concept"),
            CONFIG["workflow"].index("reference_frame_assignment"),
        )
        self.assertLess(
            CONFIG["workflow"].index("picture_lock"),
            CONFIG["workflow"].index("music_sound_design"),
        )
        self.assertLess(
            CONFIG["workflow"].index("mix_master"),
            CONFIG["workflow"].index("audiovisual_sync_qc"),
        )

    def test_audio_roles_are_distinct_and_required(self):
        roles = set(CONFIG["roles"])
        self.assertTrue(REQUIRED_PRODUCTION_ROLES.issubset(roles))
        self.assertIn("Music Supervisor & Sound Designer", roles)
        self.assertIn("Dialogue & Mix Engineer", roles)
        self.assertNotEqual(
            CONFIG["roles"]["Music Supervisor & Sound Designer"],
            CONFIG["roles"]["Dialogue & Mix Engineer"],
        )

    def test_audio_contract(self):
        audio = CONFIG["audio_system"]
        self.assertTrue(audio["spotting_required_before_reference_frame_lock"])
        self.assertTrue(audio["picture_lock_required_before_final_sound_design"])
        self.assertTrue(audio["post_picture_lock_timing_change_requires_audio_reconform"])
        self.assertEqual(set(audio["mandatory_stems"]), REQUIRED_AUDIO_STEMS)
        targets = audio["mix_targets_internal_not_platform_requirements"]
        self.assertEqual(targets["program_integrated_lufs_target"], "-14 LUFS ±1")
        self.assertEqual(targets["true_peak_ceiling"], "-1 dBTP")

    def test_fail_closed_on_governance_drift(self):
        mutations = [
            lambda c: c.__setitem__("version", "2"),
            lambda c: c.__setitem__("channel_model", "single_niche"),
            lambda c: c.__setitem__("visual_system", "other"),
            lambda c: c.__setitem__("publication_authority", "AUTO"),
            lambda c: c["portfolio_balance"].__setitem__("initial_window_videos", 5),
            lambda c: c["portfolio_balance"].__setitem__("max_same_family_in_window", 3),
            lambda c: c["portfolio_balance"].__setitem__("minimum_distinct_families_in_initial_window", 3),
            lambda c: c["portfolio_balance"].__setitem__("relax_only_after_first_party_audience_evidence", False),
            lambda c: c["trend_radar"].__setitem__("sources", []),
            lambda c: c["trend_radar"].__setitem__("evergreen_reframe_required", False),
            lambda c: c["topic_scoring"]["fields"].__setitem__("cross_platform_velocity", 14),
            lambda c: c["topic_scoring"]["gates"].__setitem__("minimum_total", 50),
            lambda c: c["topic_scoring"]["gates"].__setitem__("require_one_sentence_question", False),
            lambda c: c["topic_scoring"]["gates"].__setitem__(
                "reject_if_only_trending_without_durable_question", False
            ),
            lambda c: c.__setitem__("workflow", c["workflow"][:-1]),
            lambda c: c["script_schema"].__setitem__("required_columns", ["narration"]),
            lambda c: c["frame_bible"].__setitem__(
                "canonical_frame_types", c["frame_bible"]["canonical_frame_types"][:-1]
            ),
            lambda c: c["frame_bible"]["composition_rules"].__setitem__("editable_language_layers", False),
            lambda c: c["transition_system"].__setitem__("canonical", ["cut"]),
            lambda c: c["transition_system"].__setitem__("forbidden_default", []),
            lambda c: c["audio_system"].__setitem__("principle", "sound added after picture"),
            lambda c: c["audio_system"].__setitem__("spotting_required_before_reference_frame_lock", False),
            lambda c: c["audio_system"].__setitem__("picture_lock_required_before_final_sound_design", False),
            lambda c: c["audio_system"].__setitem__("post_picture_lock_timing_change_requires_audio_reconform", False),
            lambda c: c["audio_system"].__setitem__("music_states", ["one"]),
            lambda c: c["audio_system"].__setitem__("cue_sheet_required_fields", ["cue_id"]),
            lambda c: c["audio_system"].__setitem__("av_beat_map_required_fields", ["beat_id"]),
            lambda c: c["audio_system"].__setitem__("mandatory_stems", ["FULL master"]),
            lambda c: c["audio_system"]["mix_targets_internal_not_platform_requirements"].__setitem__(
                "program_integrated_lufs_target", "-8 LUFS"
            ),
            lambda c: c["audio_system"]["mix_targets_internal_not_platform_requirements"].__setitem__(
                "true_peak_ceiling", "0 dBTP"
            ),
            lambda c: c["audio_system"].__setitem__("anti_patterns", []),
            lambda c: c["anti_slop_gate"].__setitem__("required", False),
            lambda c: c["anti_slop_gate"].__setitem__("checks", ["x"]),
            lambda c: c["anti_slop_gate"].__setitem__("fail_action", "IGNORE"),
            lambda c: c.__setitem__("quality_gates", []),
            lambda c: c["roles"].pop("Music Supervisor & Sound Designer"),
        ]
        for mutate in mutations:
            cfg = copy.deepcopy(CONFIG)
            mutate(cfg)
            with self.assertRaises(ChannelOperatingSystemError):
                validate_config(cfg)


if __name__ == "__main__":
    unittest.main()
