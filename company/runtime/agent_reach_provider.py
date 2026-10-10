import json
import os
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from .intelligence_models import (
    AuthRequirement,
    GatewayResult,
    GatewayStatus,
    ProviderHealth,
    ProviderStatus,
    ResearchRequest,
)

ALLOWED_OPERATIONS = {
    "web_read_public",
    "youtube_metadata_public",
    "youtube_transcript_public",
    "rss_read_public",
    "bilibili_basic_public",
    "doctor_read_only",
}
APPROVED_DOCTOR_CHANNELS = ("web", "youtube", "rss", "bilibili")


def run_argv(argv: list[str], timeout_s: int):
    return subprocess.run(
        argv,
        shell=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout_s,
        check=False,
    )


def _http_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("target_url must be an absolute http(s) URL")
    return value


class AgentReachProvider:
    def __init__(
        self,
        launcher_path: str,
        approved_commit: str,
        *,
        runtime_commit: str | None = None,
        strict_pin: bool = True,
        runner=run_argv,
        timeout_s: int = 30,
    ):
        self.launcher_path = Path(launcher_path)
        self.approved_commit = approved_commit
        self.runtime_commit = runtime_commit or os.environ.get("COUNCIL_AGENT_REACH_COMMIT")
        self.strict_pin = strict_pin
        self.runner = runner
        self.timeout_s = timeout_s

    def _venv_root(self) -> Path:
        parent = self.launcher_path.parent
        if parent.name.lower() in {"scripts", "bin"}:
            return parent.parent
        return parent

    def _tool(self, name: str) -> str:
        root = self._venv_root()
        if os.name == "nt":
            filename = name if name.lower().endswith(".exe") else f"{name}.exe"
            return str(root / "Scripts" / filename)
        return str(root / "bin" / name)

    def can_handle(self, request: ResearchRequest) -> bool:
        return (
            request.intent in ALLOWED_OPERATIONS
            and request.auth_requirement == AuthRequirement.PUBLIC_ONLY
        )

    def build_argv(self, operation: str, request: ResearchRequest) -> list[str]:
        if operation not in ALLOWED_OPERATIONS:
            raise ValueError(f"operation is not allowlisted: {operation}")

        if operation == "doctor_read_only":
            return [str(self.launcher_path), "doctor", "--json"]

        if operation in {"youtube_metadata_public", "youtube_transcript_public"}:
            target = request.target_url or request.query
            if not target:
                raise ValueError("YouTube operation requires target_url or query")
            return [
                self._tool("yt-dlp"),
                "--skip-download",
                "--no-playlist",
                "--dump-single-json",
                target,
            ]

        if operation == "web_read_public":
            target = _http_url(request.target_url or request.query)
            script = (
                "import sys,urllib.request;"
                "u='https://r.jina.ai/'+sys.argv[1];"
                "r=urllib.request.Request(u,headers={'User-Agent':'CouncilGateway/1.0'});"
                "sys.stdout.buffer.write(urllib.request.urlopen(r,timeout=20).read())"
            )
            return [self._tool("python"), "-c", script, target]

        if operation == "rss_read_public":
            target = _http_url(request.target_url or request.query)
            script = (
                "import sys,json,feedparser;"
                "f=feedparser.parse(sys.argv[1]);"
                "n=int(sys.argv[2]);"
                "payload=json.dumps({'title':getattr(f.feed,'title',''),"
                "'entries':[{'title':getattr(e,'title',''),'link':getattr(e,'link','')}"
                " for e in f.entries[:n]]},ensure_ascii=False).encode('utf-8');"
                "sys.stdout.buffer.write(payload)"
            )
            return [self._tool("python"), "-c", script, target, str(request.max_results)]

        if operation == "bilibili_basic_public":
            query = request.query or request.target_url or ""
            if not query:
                raise ValueError("Bilibili operation requires query")
            script = (
                "import sys,urllib.parse,urllib.request;"
                "q=urllib.parse.quote(sys.argv[1]);"
                "u='https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword='+q;"
                "r=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'});"
                "sys.stdout.buffer.write(urllib.request.urlopen(r,timeout=20).read())"
            )
            return [self._tool("python"), "-c", script, query]

        raise ValueError(f"unsupported allowlisted operation: {operation}")

    def health(self) -> ProviderHealth:
        if not self.launcher_path.exists():
            return ProviderHealth(
                provider_id="agent_reach",
                status=ProviderStatus.UNAVAILABLE,
                auth_level=AuthRequirement.PUBLIC_ONLY,
                warnings=("launcher missing",),
            )
        if self.strict_pin and self.runtime_commit != self.approved_commit:
            return ProviderHealth(
                provider_id="agent_reach",
                status=ProviderStatus.BLOCKED,
                auth_level=AuthRequirement.PUBLIC_ONLY,
                identity=self.runtime_commit,
                warnings=("runtime commit does not match approved pin",),
            )

        try:
            completed = self.runner(
                self.build_argv(
                    "doctor_read_only",
                    ResearchRequest(request_id="doctor", intent="doctor_read_only", query="health"),
                ),
                self.timeout_s,
            )
        except Exception as exc:
            return ProviderHealth(
                provider_id="agent_reach",
                status=ProviderStatus.UNAVAILABLE,
                auth_level=AuthRequirement.PUBLIC_ONLY,
                identity=self.runtime_commit,
                warnings=(f"doctor failed: {exc}",),
            )
        if completed.returncode != 0:
            return ProviderHealth(
                provider_id="agent_reach",
                status=ProviderStatus.UNAVAILABLE,
                auth_level=AuthRequirement.PUBLIC_ONLY,
                identity=self.runtime_commit,
                warnings=("doctor returned non-zero",),
            )
        try:
            doctor = json.loads(completed.stdout or "{}")
        except json.JSONDecodeError:
            return ProviderHealth(
                provider_id="agent_reach",
                status=ProviderStatus.UNAVAILABLE,
                auth_level=AuthRequirement.PUBLIC_ONLY,
                identity=self.runtime_commit,
                warnings=("doctor output was not valid JSON",),
            )

        healthy = []
        for name in APPROVED_DOCTOR_CHANNELS:
            item = doctor.get(name, {})
            if item.get("status") == "ok":
                healthy.append((name, item.get("active_backend") or name))
        if not healthy:
            return ProviderHealth(
                provider_id="agent_reach",
                status=ProviderStatus.UNAVAILABLE,
                auth_level=AuthRequirement.PUBLIC_ONLY,
                identity=self.runtime_commit,
                warnings=("no approved public-read channel is healthy",),
            )
        return ProviderHealth(
            provider_id="agent_reach",
            status=ProviderStatus.HEALTHY,
            backend=healthy[0][1],
            auth_level=AuthRequirement.PUBLIC_ONLY,
            identity=self.runtime_commit,
            warnings=tuple(f"{name}:{backend}" for name, backend in healthy[1:]),
        )

    def _fetch_caption(self, info: dict) -> str | None:
        captions = info.get("subtitles") or info.get("automatic_captions") or {}
        if not isinstance(captions, dict) or not captions:
            return None
        entries = captions.get("en")
        if not entries:
            first = next(iter(captions.values()), None)
            entries = first
        if not isinstance(entries, list) or not entries:
            return None
        url = entries[0].get("url") if isinstance(entries[0], dict) else None
        if not url:
            return None
        script = (
            "import sys,urllib.request;"
            "r=urllib.request.Request(sys.argv[1],headers={'User-Agent':'Mozilla/5.0'});"
            "sys.stdout.buffer.write(urllib.request.urlopen(r,timeout=20).read())"
        )
        completed = self.runner([self._tool("python"), "-c", script, _http_url(url)], self.timeout_s)
        if completed.returncode != 0:
            return None
        return completed.stdout

    def read(self, request: ResearchRequest) -> GatewayResult:
        if not self.can_handle(request):
            return GatewayResult(
                status=GatewayStatus.BLOCKED,
                request_id=request.request_id,
                provider="agent_reach",
                message="request is outside Agent Reach public-read allowlist",
            )

        health = self.health()
        if health.status not in {ProviderStatus.HEALTHY, ProviderStatus.DEGRADED}:
            status = GatewayStatus.BLOCKED if health.status == ProviderStatus.BLOCKED else GatewayStatus.UNAVAILABLE
            return GatewayResult(
                status=status,
                request_id=request.request_id,
                provider="agent_reach",
                backend=health.backend,
                message="Agent Reach provider is not available for approved public reads",
                warnings=health.warnings,
            )

        try:
            argv = self.build_argv(request.intent, request)
            completed = self.runner(argv, self.timeout_s)
        except Exception as exc:
            return GatewayResult(
                status=GatewayStatus.PROVIDER_ERROR,
                request_id=request.request_id,
                provider="agent_reach",
                backend=health.backend,
                message=str(exc),
            )
        if completed.returncode != 0:
            return GatewayResult(
                status=GatewayStatus.PROVIDER_ERROR,
                request_id=request.request_id,
                provider="agent_reach",
                backend=health.backend,
                message=completed.stderr or "provider command returned non-zero",
            )

        payload = completed.stdout
        if request.intent in {"youtube_metadata_public", "youtube_transcript_public", "rss_read_public", "bilibili_basic_public", "doctor_read_only"}:
            try:
                payload = json.loads(completed.stdout)
            except (json.JSONDecodeError, TypeError):
                pass

        if request.intent == "youtube_transcript_public" and isinstance(payload, dict):
            transcript = self._fetch_caption(payload)
            payload = {"video": payload, "transcript": transcript}

        return GatewayResult(
            status=GatewayStatus.OK,
            request_id=request.request_id,
            provider="agent_reach",
            backend=health.backend,
            payload=payload,
            limitations=("PUBLIC_ONLY", "NO_EXTERNAL_WRITES"),
        )
