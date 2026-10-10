import unittest

from company.runtime.intelligence_models import (
    AuthRequirement,
    GatewayResult,
    GatewayStatus,
    ProviderHealth,
    ProviderStatus,
    ResearchRequest,
    validate_request,
)


class IntelligenceModels(unittest.TestCase):
    def test_missing_auth_defaults_to_public_only(self):
        req = ResearchRequest(request_id="R1", intent="rss_read_public", query="ai")
        self.assertEqual(req.auth_requirement, AuthRequirement.PUBLIC_ONLY)

    def test_invalid_request_without_query_or_target_url_is_rejected(self):
        req = ResearchRequest(request_id="R1", intent="rss_read_public")
        errors = validate_request(req)
        self.assertIn("query or target_url is required", errors)

    def test_max_results_must_be_positive_and_bounded(self):
        zero = ResearchRequest(request_id="R1", intent="rss_read_public", query="x", max_results=0)
        high = ResearchRequest(request_id="R2", intent="rss_read_public", query="x", max_results=51)
        self.assertIn("max_results must be between 1 and 50", validate_request(zero))
        self.assertIn("max_results must be between 1 and 50", validate_request(high))
        ok = ResearchRequest(request_id="R3", intent="rss_read_public", query="x", max_results=50)
        self.assertEqual(validate_request(ok), [])

    def test_provider_health_has_explicit_status_backend_and_identity(self):
        h = ProviderHealth(
            provider_id="agent_reach",
            status=ProviderStatus.HEALTHY,
            backend="yt-dlp",
            auth_level=AuthRequirement.PUBLIC_ONLY,
            verified_at="2026-10-11T00:00:00+00:00",
            identity="94f06c",
        )
        self.assertEqual(h.status, ProviderStatus.HEALTHY)
        self.assertEqual(h.backend, "yt-dlp")
        self.assertEqual(h.identity, "94f06c")

    def test_gateway_result_state_is_closed_enum(self):
        result = GatewayResult(status=GatewayStatus.BLOCKED, request_id="R1", message="policy block")
        self.assertEqual(result.status.value, "BLOCKED")
        with self.assertRaises(ValueError):
            GatewayStatus("SOMETHING_NEW")


if __name__ == "__main__":
    unittest.main()
