import json
import sys
import tempfile
import unittest
from pathlib import Path
from subprocess import CompletedProcess

from company.runtime.agent_reach_provider import AgentReachProvider, run_argv
from company.runtime.intelligence_models import (
    AuthRequirement,
    ProviderHealth,
    ProviderStatus,
    ResearchRequest,
)


APPROVED = "94f06c1969dfc1834001269d79d3ad0972d9dee6"


class FakeRunner:
    def __init__(self, stdout="{}", returncode=0):
        self.stdout = stdout
        self.returncode = returncode
        self.calls = []

    def __call__(self, argv, timeout_s):
        self.calls.append((list(argv), timeout_s))
        return CompletedProcess(argv, self.returncode, stdout=self.stdout, stderr="")


class AgentReachProviderSecurity(unittest.TestCase):
    def _launcher(self):
        handle = tempfile.NamedTemporaryFile(delete=False, suffix=".cmd")
        handle.close()
        self.addCleanup(lambda: Path(handle.name).unlink(missing_ok=True))
        return handle.name

    def test_provider_has_no_write_method(self):
        provider = AgentReachProvider(self._launcher(), APPROVED, runtime_commit=APPROVED, runner=FakeRunner())
        self.assertFalse(hasattr(provider, "write"))

    def test_only_allowlisted_operations_build_argv(self):
        provider = AgentReachProvider(self._launcher(), APPROVED, runtime_commit=APPROVED, runner=FakeRunner())
        req = ResearchRequest(
            request_id="R1",
            intent="youtube_metadata_public",
            target_url="https://www.youtube.com/watch?v=test",
        )
        argv = provider.build_argv("youtube_metadata_public", req)
        self.assertIn("--dump-single-json", argv)
        self.assertEqual(argv[-1], req.target_url)

    def test_shell_metacharacters_remain_single_argument_data(self):
        runner = FakeRunner()
        provider = AgentReachProvider(self._launcher(), APPROVED, runtime_commit=APPROVED, runner=runner)
        hostile = '"; Remove-Item *; #'
        req = ResearchRequest(request_id="R2", intent="youtube_metadata_public", query=hostile)
        argv = provider.build_argv("youtube_metadata_public", req)
        self.assertEqual(argv[-1], hostile)
        self.assertEqual(argv.count(hostile), 1)

    def test_unknown_operation_is_rejected_before_runner(self):
        runner = FakeRunner()
        provider = AgentReachProvider(self._launcher(), APPROVED, runtime_commit=APPROVED, runner=runner)
        req = ResearchRequest(request_id="R3", intent="rss_read_public", query="x")
        with self.assertRaises(ValueError):
            provider.build_argv("arbitrary_shell", req)
        self.assertEqual(runner.calls, [])

    def test_configure_install_and_opencli_are_rejected(self):
        provider = AgentReachProvider(self._launcher(), APPROVED, runtime_commit=APPROVED, runner=FakeRunner())
        req = ResearchRequest(request_id="R4", intent="rss_read_public", query="x")
        for op in ("configure", "install", "opencli"):
            with self.assertRaises(ValueError):
                provider.build_argv(op, req)

    def test_strict_pin_mismatch_blocks_provider(self):
        runner = FakeRunner()
        provider = AgentReachProvider(
            self._launcher(),
            APPROVED,
            runtime_commit="wrong",
            strict_pin=True,
            runner=runner,
        )
        h = provider.health()
        self.assertEqual(h.status, ProviderStatus.BLOCKED)
        self.assertEqual(runner.calls, [])

    def test_missing_launcher_is_unavailable(self):
        provider = AgentReachProvider(
            "Z:/definitely/missing/agent-reach-safe.cmd",
            APPROVED,
            runtime_commit=APPROVED,
            runner=FakeRunner(),
        )
        self.assertEqual(provider.health().status, ProviderStatus.UNAVAILABLE)

    def test_doctor_health_parsing_never_enables_blocked_channel(self):
        payload = json.dumps({
            "instagram": {"status": "ok", "active_backend": "OpenCLI"},
            "facebook": {"status": "ok", "active_backend": "OpenCLI"},
            "youtube": {"status": "off", "active_backend": None},
            "rss": {"status": "off", "active_backend": None},
            "web": {"status": "off", "active_backend": None},
            "bilibili": {"status": "off", "active_backend": None},
        })
        provider = AgentReachProvider(
            self._launcher(),
            APPROVED,
            runtime_commit=APPROVED,
            runner=FakeRunner(payload),
        )
        h = provider.health()
        self.assertEqual(h.status, ProviderStatus.UNAVAILABLE)
        self.assertNotEqual(h.backend, "OpenCLI")

    def test_authenticated_request_is_not_handleable(self):
        provider = AgentReachProvider(self._launcher(), APPROVED, runtime_commit=APPROVED, runner=FakeRunner())
        req = ResearchRequest(
            request_id="R5",
            intent="youtube_metadata_public",
            query="x",
            auth_requirement=AuthRequirement.AUTHENTICATED,
        )
        self.assertFalse(provider.can_handle(req))

    def test_runner_decodes_utf8_independently_of_windows_codepage(self):
        expected = "اختبار"
        code = "import sys;sys.stdout.buffer.write('اختبار'.encode('utf-8'))"
        completed = run_argv([sys.executable, "-c", code], 10)
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, expected)

    def test_public_python_argv_uses_binary_stdout(self):
        provider = AgentReachProvider(self._launcher(), APPROVED, runtime_commit=APPROVED, runner=FakeRunner())
        requests = [
            ("web_read_public", ResearchRequest(request_id="W", intent="web_read_public", target_url="https://example.com")),
            ("rss_read_public", ResearchRequest(request_id="R", intent="rss_read_public", target_url="https://example.com/feed")),
            ("bilibili_basic_public", ResearchRequest(request_id="B", intent="bilibili_basic_public", query="اختبار")),
        ]
        for operation, request in requests:
            argv = provider.build_argv(operation, request)
            self.assertIn("stdout.buffer.write", argv[2], operation)


    def test_operation_result_uses_actual_backend_provenance(self):
        provider = AgentReachProvider(self._launcher(), APPROVED, runtime_commit=APPROVED, runner=FakeRunner("{}"))
        provider.health = lambda: ProviderHealth(
            provider_id="agent_reach",
            status=ProviderStatus.HEALTHY,
            backend="Agent Reach public-read",
            auth_level=AuthRequirement.PUBLIC_ONLY,
            identity=APPROVED,
        )
        cases = [
            ("youtube_metadata_public", "https://www.youtube.com/watch?v=test", "yt-dlp"),
            ("rss_read_public", "https://example.com/feed", "feedparser"),
            ("web_read_public", "https://example.com", "Jina Reader"),
        ]
        for intent, target, expected_backend in cases:
            req = ResearchRequest(request_id=intent, intent=intent, target_url=target)
            result = provider.read(req)
            self.assertEqual(result.backend, expected_backend, intent)

    def test_health_records_verification_timestamp(self):
        payload = json.dumps({"web": {"status": "ok", "active_backend": "Jina Reader"}})
        provider = AgentReachProvider(
            self._launcher(),
            APPROVED,
            runtime_commit=APPROVED,
            runner=FakeRunner(payload),
        )
        self.assertIsNotNone(provider.health().verified_at)

    def test_health_reuses_recent_verified_snapshot(self):
        payload = json.dumps({"web": {"status": "ok", "active_backend": "Jina Reader"}})
        runner = FakeRunner(payload)
        provider = AgentReachProvider(
            self._launcher(),
            APPROVED,
            runtime_commit=APPROVED,
            runner=runner,
            health_ttl_s=60,
        )
        first = provider.health()
        second = provider.health()
        self.assertEqual(first, second)
        self.assertEqual(len(runner.calls), 1)

    def test_public_read_rejects_local_network_targets(self):
        provider = AgentReachProvider(self._launcher(), APPROVED, runtime_commit=APPROVED, runner=FakeRunner())
        for intent in ("web_read_public", "rss_read_public"):
            for target in ("http://127.0.0.1:8080/x", "http://localhost/x", "http://[::1]/x"):
                req = ResearchRequest(request_id=intent, intent=intent, target_url=target)
                with self.assertRaises(ValueError, msg=f"{intent} {target}"):
                    provider.build_argv(intent, req)

    def test_youtube_url_rejects_local_network_target(self):
        provider = AgentReachProvider(self._launcher(), APPROVED, runtime_commit=APPROVED, runner=FakeRunner())
        req = ResearchRequest(
            request_id="YT-LOCAL",
            intent="youtube_metadata_public",
            target_url="http://127.0.0.1:8080/video",
        )
        with self.assertRaises(ValueError):
            provider.build_argv("youtube_metadata_public", req)


if __name__ == "__main__":
    unittest.main()
