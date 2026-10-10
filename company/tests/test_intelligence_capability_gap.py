import unittest

from company.runtime.intelligence_gateway import capability_gap_from_gateway
from company.runtime.intelligence_models import (
    GatewayResult,
    GatewayStatus,
    ResearchRequest,
)


class IntelligenceCapabilityGap(unittest.TestCase):
    def test_material_blocked_channel_creates_evidence_channel_gap(self):
        req = ResearchRequest(
            request_id="R1",
            intent="instagram_authenticated",
            query="trend",
            evidence_purpose="DECISION_HINGE",
        )
        result = GatewayResult(
            status=GatewayStatus.BLOCKED,
            request_id="R1",
            message="auth required",
        )
        gap = capability_gap_from_gateway(req, result)
        self.assertIsNotNone(gap)
        self.assertEqual(gap["signal_type"], "EVIDENCE_CHANNEL_GAP")
        self.assertEqual(gap["status"], "GAP_OPEN")

    def test_non_material_block_does_not_create_gap(self):
        req = ResearchRequest(
            request_id="R2",
            intent="instagram_authenticated",
            query="trend",
            evidence_purpose="GENERAL",
        )
        result = GatewayResult(
            status=GatewayStatus.BLOCKED,
            request_id="R2",
            message="auth required",
        )
        self.assertIsNone(capability_gap_from_gateway(req, result))

    def test_gap_never_installs_or_requests_credentials(self):
        req = ResearchRequest(
            request_id="R3",
            intent="reddit_authenticated",
            query="customer objections",
            evidence_purpose="MATERIAL_DECISION",
        )
        result = GatewayResult(
            status=GatewayStatus.BLOCKED,
            request_id="R3",
            message="blocked by policy",
        )
        gap = capability_gap_from_gateway(req, result)
        serialized = repr(gap).lower()
        self.assertNotIn("install_tool", serialized)
        self.assertNotIn("connect_credentials", serialized)
        self.assertNotIn("authenticate_account", serialized)

    def test_repeated_unavailable_provider_can_open_gap_without_changing_route(self):
        req = ResearchRequest(
            request_id="R4",
            intent="youtube_transcript_public",
            query="video",
            evidence_purpose="COMMERCIAL_VALIDATION",
        )
        result = GatewayResult(
            status=GatewayStatus.UNAVAILABLE,
            request_id="R4",
            provider="agent_reach",
            message="provider unavailable",
        )
        gap = capability_gap_from_gateway(req, result)
        self.assertIsNotNone(gap)
        self.assertEqual(result.status, GatewayStatus.UNAVAILABLE)
        self.assertEqual(result.provider, "agent_reach")


if __name__ == "__main__":
    unittest.main()
