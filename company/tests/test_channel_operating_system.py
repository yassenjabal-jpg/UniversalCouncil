import copy
import json
import unittest
from pathlib import Path

from company.runtime.channel_operating_system import (
    ChannelOperatingSystemError,
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
            lambda c: c["anti_slop_gate"].__setitem__("required", False),
            lambda c: c["anti_slop_gate"].__setitem__("checks", ["x"]),
            lambda c: c["anti_slop_gate"].__setitem__("fail_action", "IGNORE"),
            lambda c: c.__setitem__("quality_gates", []),
            lambda c: c["roles"].pop("Red Team"),
        ]
        for mutate in mutations:
            cfg = copy.deepcopy(CONFIG)
            mutate(cfg)
            with self.assertRaises(ChannelOperatingSystemError):
                validate_config(cfg)


if __name__ == "__main__":
    unittest.main()
