import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CFG = ROOT / "company/config/intelligence_gateway.json"


class IntelligenceGatewayPolicy(unittest.TestCase):
    def _cfg(self):
        return json.loads(CFG.read_text(encoding="utf-8"))

    def test_gateway_defaults_to_public_read_only(self):
        cfg = self._cfg()
        self.assertEqual(cfg["version"], "1.0")
        self.assertEqual(cfg["default_mode"], "READ_ONLY")
        self.assertEqual(cfg["default_auth_requirement"], "PUBLIC_ONLY")

    def test_native_connectors_outrank_agent_reach_for_overlapping_intents(self):
        cfg = self._cfg()
        self.assertEqual(cfg["routes"]["github"]["providers"][0], "native_github")
        self.assertEqual(cfg["routes"]["general_web_search"]["providers"][0], "native_web")
        self.assertEqual(cfg["routes"]["private_drive"]["providers"], ["native_drive"])

    def test_authenticated_social_channels_are_blocked(self):
        cfg = self._cfg()
        expected = {
            "instagram_authenticated",
            "facebook_authenticated",
            "reddit_authenticated",
            "x_authenticated",
            "linkedin_authenticated",
            "xiaohongshu_authenticated",
        }
        self.assertTrue(expected.issubset(set(cfg["blocked_intents"])))

    def test_agent_reach_allowlist_contains_only_public_read_operations(self):
        cfg = self._cfg()
        ops = set(cfg["agent_reach"]["allowed_operations"])
        self.assertEqual(
            ops,
            {
                "web_read_public",
                "youtube_metadata_public",
                "youtube_transcript_public",
                "rss_read_public",
                "bilibili_basic_public",
                "doctor_read_only",
            },
        )
        forbidden = {"install", "configure", "opencli", "publish", "message"}
        self.assertTrue(forbidden.isdisjoint(ops))

    def test_strict_pin_matches_approved_agent_reach_commit(self):
        cfg = self._cfg()
        self.assertTrue(cfg["agent_reach"]["strict_pin"])
        self.assertEqual(
            cfg["agent_reach"]["approved_commit"],
            "94f06c1969dfc1834001269d79d3ad0972d9dee6",
        )
        self.assertEqual(cfg["agent_reach"]["launcher_env"], "COUNCIL_AGENT_REACH_LAUNCHER")
        self.assertEqual(cfg["agent_reach"]["commit_env"], "COUNCIL_AGENT_REACH_COMMIT")

    def test_validator_rejects_gateway_policy_drift(self):
        from tools import validate_config as validator

        bad = self._cfg()
        bad["default_mode"] = "WRITE"
        with self.assertRaises(AssertionError):
            validator.validate_intelligence_gateway(bad)


if __name__ == "__main__":
    unittest.main()
