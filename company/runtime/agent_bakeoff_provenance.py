from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ProvenanceError(ValueError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git_head(root: Path) -> str:
    try:
        return (
            subprocess.check_output(
                ["git", "-C", str(root), "rev-parse", "HEAD"],
                text=True,
                stderr=subprocess.DEVNULL,
            )
            .strip()
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ProvenanceError(f"cannot resolve git HEAD: {exc}") from exc


def detected_runner_id() -> str:
    return (os.environ.get("COMPUTERNAME") or platform.node() or "").strip().upper()


def require_yassin_runner() -> str:
    runner = detected_runner_id()
    if runner != "YASSIN":
        raise ProvenanceError(f"live bake-off is restricted to YASSIN; detected runner={runner or 'UNKNOWN'}")
    return runner


def package_versions() -> dict[str, str]:
    names = (
        "openai-agents",
        "agent-framework-core",
        "agent-framework-orchestrations",
        "agent-framework-openai",
    )
    versions: dict[str, str] = {}
    for name in names:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "NOT_INSTALLED"
    return versions


def ollama_model_digest(endpoint: str, model: str, timeout: int = 10) -> str:
    with urllib.request.urlopen(f"{endpoint.rstrip('/')}/api/tags", timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    for item in payload.get("models", []):
        if item.get("name") == model or item.get("model") == model:
            digest = str(item.get("digest") or "").strip()
            if digest:
                return digest
    raise ProvenanceError(f"model digest not found for {model}")


def build_manifest(
    root: Path,
    *,
    endpoint: str,
    model: str,
    stage: str,
    selected_case_ids: list[str],
) -> dict[str, Any]:
    runner_id = require_yassin_runner()
    config = root / "company" / "config" / "agent_bakeoff.json"
    cases = root / "benchmarks" / "agent_runtime" / "cases.json"
    live_runner = root / "tools" / "run_agent_bakeoff_live.py"
    evaluator = root / "company" / "runtime" / "agent_bakeoff.py"
    return {
        "schema_version": "1.0",
        "runner_id": runner_id,
        "execution_host": runner_id,
        "source_head": git_head(root),
        "config_sha256": sha256_file(config),
        "cases_sha256": sha256_file(cases),
        "live_runner_sha256": sha256_file(live_runner),
        "evaluator_sha256": sha256_file(evaluator),
        "model": model,
        "model_digest": ollama_model_digest(endpoint, model),
        "endpoint": endpoint,
        "stage": stage,
        "selected_case_ids": list(selected_case_ids),
        "framework_versions": package_versions(),
        "cost_usd": 0.0,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def manifest_id(manifest: dict[str, Any]) -> str:
    stable = {
        key: manifest[key]
        for key in (
            "schema_version",
            "runner_id",
            "source_head",
            "config_sha256",
            "cases_sha256",
            "live_runner_sha256",
            "evaluator_sha256",
            "model",
            "model_digest",
            "stage",
            "selected_case_ids",
            "framework_versions",
            "cost_usd",
        )
    }
    return sha256_bytes(json.dumps(stable, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def validate_manifest(manifest: dict[str, Any], root: Path) -> bool:
    required = {
        "schema_version",
        "runner_id",
        "source_head",
        "config_sha256",
        "cases_sha256",
        "live_runner_sha256",
        "evaluator_sha256",
        "model",
        "model_digest",
        "endpoint",
        "stage",
        "selected_case_ids",
        "framework_versions",
        "cost_usd",
        "created_at_utc",
        "manifest_id",
    }
    missing = required - set(manifest)
    if missing:
        raise ProvenanceError(f"manifest missing fields: {sorted(missing)}")
    if manifest["schema_version"] != "1.0":
        raise ProvenanceError("unsupported manifest schema")
    if str(manifest["runner_id"]).upper() != "YASSIN":
        raise ProvenanceError("manifest runner must be YASSIN")
    if float(manifest["cost_usd"]) != 0.0:
        raise ProvenanceError("manifest cost_usd must be zero")
    if manifest["config_sha256"] != sha256_file(root / "company" / "config" / "agent_bakeoff.json"):
        raise ProvenanceError("manifest config hash does not match current config")
    if manifest["cases_sha256"] != sha256_file(root / "benchmarks" / "agent_runtime" / "cases.json"):
        raise ProvenanceError("manifest cases hash does not match current cases")
    if manifest["live_runner_sha256"] != sha256_file(root / "tools" / "run_agent_bakeoff_live.py"):
        raise ProvenanceError("manifest live runner hash does not match current runner")
    if manifest["evaluator_sha256"] != sha256_file(root / "company" / "runtime" / "agent_bakeoff.py"):
        raise ProvenanceError("manifest evaluator hash does not match current evaluator")
    expected_id = manifest_id({k: v for k, v in manifest.items() if k != "manifest_id"})
    if manifest["manifest_id"] != expected_id:
        raise ProvenanceError("manifest_id mismatch")
    return True


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    payload = dict(manifest)
    payload["manifest_id"] = manifest_id(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
