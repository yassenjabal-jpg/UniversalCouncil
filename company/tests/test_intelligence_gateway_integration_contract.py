import json
import os
import unittest
from pathlib import Path

from company.runtime.agent_reach_provider import AgentReachProvider
from company.runtime.intelligence_models import GatewayStatus, ResearchRequest

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "company/config/intelligence_gateway.local.example.json"
APPROVED = "94f06c1969dfc1834001269d79d3ad0972d9dee6"


def require_live_env():
    launcher = os.environ.get("COUNCIL_AGENT_REACH_LAUNCHER")
    commit = os.environ.get("COUNCIL_AGENT_REACH_COMMIT")
    if not launcher or not commit:
        raise unittest.SkipTest("Agent Reach live probe requires explicit launcher and commit env")
    return launcher, commit


class IntelligenceGatewayIntegrationContract(unittest.TestCase):
    def test_local_example_contains_environment_keys_not_real_private_path(self):
        raw = EXAMPLE.read_text(encoding="utf-8")
        cfg = json.loads(raw)
        self.assertEqual(cfg["launcher_env"], "COUNCIL_AGENT_REACH_LAUNCHER")
        self.assertEqual(cfg["commit_env"], "COUNCIL_AGENT_REACH_COMMIT")
        self.assertNotIn("C:\\Users\\alnaseem", raw)
        self.assertNotIn("/home/", raw)

    def test_local_example_pins_agent_reach_commit(self):
        cfg = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        self.assertEqual(cfg["approved_commit"], APPROVED)
        self.assertTrue(cfg["strict_pin"])

    def test_integration_test_skips_without_launcher_env(self):
        old_launcher = os.environ.pop("COUNCIL_AGENT_REACH_LAUNCHER", None)
        old_commit = os.environ.pop("COUNCIL_AGENT_REACH_COMMIT", None)
        try:
            with self.assertRaises(unittest.SkipTest):
                require_live_env()
        finally:
            if old_launcher is not None:
                os.environ["COUNCIL_AGENT_REACH_LAUNCHER"] = old_launcher
            if old_commit is not None:
                os.environ["COUNCIL_AGENT_REACH_COMMIT"] = old_commit

    def test_live_agent_reach_public_read_probe(self):
        launcher, commit = require_live_env()
        provider = AgentReachProvider(
            launcher,
            APPROVED,
            runtime_commit=commit,
            strict_pin=True,
            timeout_s=30,
        )
        health = provider.health()
        self.assertEqual(health.status.value, "HEALTHY")
        request = ResearchRequest(
            request_id="LIVE-RSS",
            intent="rss_read_public",
            target_url="https://hnrss.org/frontpage",
            max_results=2,
            evidence_purpose="INTEGRATION_TEST",
        )
        result = provider.read(request)
        self.assertEqual(result.status, GatewayStatus.OK)
        self.assertEqual(result.provider, "agent_reach")
        self.assertIsInstance(result.payload, dict)
        self.assertGreaterEqual(len(result.payload.get("entries", [])), 1)


if __name__ == "__main__":
    unittest.main()
