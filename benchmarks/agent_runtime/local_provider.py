from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENDPOINT = "http://127.0.0.1:11434/api/chat"


class LocalProviderError(RuntimeError):
    pass


def require_yassin_local_endpoint(endpoint: str) -> None:
    if (os.environ.get("COMPUTERNAME") or "").strip().upper() != "YASSIN":
        raise LocalProviderError("local provider probe is restricted to YASSIN")
    parsed = urlparse(endpoint)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise LocalProviderError("local provider probe rejects non-local endpoints")


def ollama_chat(
    model: str,
    messages: list[dict[str, str]],
    endpoint: str = DEFAULT_ENDPOINT,
    *,
    timeout: int = 180,
    temperature: float = 0.0,
) -> dict[str, Any]:
    require_yassin_local_endpoint(endpoint)
    payload = json.dumps(
        {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise LocalProviderError(f"local Ollama request failed: {exc}") from exc
    data["_latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
    return data


def provider_probe(model: str, endpoint: str) -> dict[str, Any]:
    response = ollama_chat(
        model,
        [
            {
                "role": "system",
                "content": (
                    "Return only JSON with keys status and cost_usd. "
                    "Set status to LOCAL_PROVIDER_READY and cost_usd to 0."
                ),
            },
            {"role": "user", "content": "Probe the zero-cost local provider."},
        ],
        endpoint,
        timeout=120,
    )
    message = response.get("message", {}).get("content", "")
    return {
        "provider": "ollama_local",
        "model": model,
        "endpoint": endpoint,
        "latency_ms": response.get("_latency_ms", 0),
        "prompt_eval_count": int(response.get("prompt_eval_count", 0) or 0),
        "eval_count": int(response.get("eval_count", 0) or 0),
        "reported_content": message,
        "cost_usd": 0.0,
        "network_paid_api": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Zero-cost local provider probe for the Council live bake-off.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--out", default="benchmarks/agent_runtime/local_provider_receipt.json")
    args = parser.parse_args()

    try:
        receipt = provider_probe(args.model, args.endpoint)
    except LocalProviderError as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc), "cost_usd": 0.0}, indent=2))
        return 3

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
