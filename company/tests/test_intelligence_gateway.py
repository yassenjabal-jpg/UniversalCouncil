import copy
import json
import unittest
from pathlib import Path

from company.runtime.intelligence_gateway import route_request, select_route
from company.runtime.intelligence_models import (
    AuthRequirement,
    GatewayResult,
    GatewayStatus,
    ProviderHealth,
    ProviderStatus,
    ResearchRequest,
)

ROOT = Path(__file__).resolve().parents[2]
POLICY = json.loads((ROOT / "company/config/intelligence_gateway.json").read_text(encoding="utf-8"))


def health(provider_id, status=ProviderStatus.HEALTHY, backend=None):
    return ProviderHealth(
        provider_id=provider_id,
        status=status,
        backend=backend or provider_id,
        auth_level=AuthRequirement.PUBLIC_ONLY,
        identity="approved",
    )


class StubProvider:
    def __init__(self, provider_id, result=None, exc=None, status=ProviderStatus.HEALTHY):
        self.provider_id = provider_id
        self._result = result
        self._exc = exc
        self._health = health(provider_id, status)

    def health(self):
        return self._health

    def read(self, request):
        if self._exc:
            raise self._exc
        return self._result or GatewayResult(
            status=GatewayStatus.OK,
            request_id=request.request_id,
            provider=self.provider_id,
            backend=self.provider_id,
            payload={"ok": True},
        )


class IntelligenceGatewayRouting(unittest.TestCase):
    def test_native_github_outranks_agent_reach(self):
        req = ResearchRequest(request_id="R1", intent="github", query="repo")
        result = select_route(
            req,
            POLICY,
            {
                "native_github": health("native_github"),
                "agent_reach": health("agent_reach"),
            },
        )
        self.assertEqual(result.status, GatewayStatus.OK)
        self.assertEqual(result.provider, "native_github")

    def test_youtube_transcript_selects_agent_reach_when_healthy(self):
        req = ResearchRequest(request_id="R2", intent="youtube_transcript_public", query="video")
        result = select_route(req, POLICY, {"agent_reach": health("agent_reach", backend="yt-dlp")})
        self.assertEqual(result.provider, "agent_reach")
        self.assertEqual(result.backend, "yt-dlp")

    def test_rss_public_selects_agent_reach(self):
        req = ResearchRequest(request_id="R3", intent="rss_read_public", target_url="https://example.com/feed")
        result = select_route(req, POLICY, {"agent_reach": health("agent_reach", backend="feedparser")})
        self.assertEqual(result.status, GatewayStatus.OK)
        self.assertEqual(result.provider, "agent_reach")

    def test_private_drive_never_routes_to_agent_reach(self):
        req = ResearchRequest(
            request_id="R4",
            intent="private_drive",
            query="quarterly plan",
            auth_requirement=AuthRequirement.AUTHENTICATED,
        )
        result = select_route(
            req,
            POLICY,
            {
                "native_drive": health("native_drive"),
                "agent_reach": health("agent_reach"),
            },
        )
        self.assertEqual(result.provider, "native_drive")

    def test_instagram_authenticated_is_blocked_even_when_provider_healthy(self):
        req = ResearchRequest(
            request_id="R5",
            intent="instagram_authenticated",
            query="trend",
            auth_requirement=AuthRequirement.AUTHENTICATED,
        )
        result = select_route(req, POLICY, {"agent_reach": health("agent_reach")})
        self.assertEqual(result.status, GatewayStatus.BLOCKED)
        self.assertIsNone(result.provider)

    def test_unhealthy_agent_reach_returns_unavailable(self):
        req = ResearchRequest(request_id="R6", intent="youtube_transcript_public", query="video")
        result = select_route(
            req,
            POLICY,
            {"agent_reach": health("agent_reach", ProviderStatus.UNAVAILABLE)},
        )
        self.assertEqual(result.status, GatewayStatus.UNAVAILABLE)

    def test_provider_failure_does_not_silently_change_evidence_source(self):
        policy = copy.deepcopy(POLICY)
        policy["routes"]["web_read_public"]["fallbacks"] = []
        req = ResearchRequest(request_id="R7", intent="web_read_public", target_url="https://example.com")
        providers = {
            "native_web": StubProvider("native_web", exc=RuntimeError("boom")),
            "agent_reach": StubProvider("agent_reach"),
        }
        result = route_request(req, policy, providers)
        self.assertEqual(result.status, GatewayStatus.PROVIDER_ERROR)
        self.assertEqual(result.provider, "native_web")
        self.assertNotIn("fallback_from", result.metadata)

    def test_explicit_same_risk_fallback_is_recorded_when_configured(self):
        policy = copy.deepcopy(POLICY)
        req = ResearchRequest(request_id="R8", intent="web_read_public", target_url="https://example.com")
        providers = {
            "native_web": StubProvider("native_web", exc=RuntimeError("boom")),
            "agent_reach": StubProvider("agent_reach"),
        }
        result = route_request(req, policy, providers)
        self.assertEqual(result.status, GatewayStatus.OK)
        self.assertEqual(result.provider, "agent_reach")
        self.assertEqual(result.metadata["fallback_from"], "native_web")
        self.assertIn("boom", result.metadata["fallback_reason"])


if __name__ == "__main__":
    unittest.main()
