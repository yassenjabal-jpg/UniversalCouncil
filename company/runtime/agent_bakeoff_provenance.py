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
        return subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
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


def manifest_id(manifest: dict[str, Any]) -> str:
    stable = {
        key: manifest[key]
        for key in (
            "schema_version",
            "runner_id",
            "source_sha",
            "config_sha256",
            "cases_sha256",
            "packets_sha256",
            "runner_sha256",
            "evaluator_sha256",
            "requirements_sha256",
            "model",
            "model_digest",
            "stage",
            "selected_case_ids",
            "framework_versions",
            "financial_cost_usd",
        )
    }
    return sha256_bytes(json.dumps(stable, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def build_manifest(
    root: Path,
    *,
    endpoint: str,
    model: str,
    stage: str,
    selected_case_ids: list[str],
) -> dict[str, Any]:
    runner_id = require_yassin_runner()
    files = {
        "config_sha256": root / "company" / "config" / "agent_bakeoff.json",
        "cases_sha256": root / "benchmarks" / "agent_runtime" / "cases.json",
        "packets_sha256": root / "benchmarks" / "agent_runtime" / "case_packets.json",
        "runner_sha256": root / "tools" / "run_agent_bakeoff_live.py",
        "evaluator_sha256": root / "company" / "runtime" / "agent_bakeoff.py",
        "requirements_sha256": root / "benchmarks" / "agent_runtime" / "requirements.txt",
    }
    missing = [str(path.relative_to(root)) for path in files.values() if not path.is_file()]
    if missing:
        raise ProvenanceError(f"cannot build manifest; missing files: {missing}")

    payload: dict[str, Any] = {
        "schema_version": "1.1",
        "runner_id": runner_id,
        "execution_host": runner_id,
        "source_sha": git_head(root),
        **{key: sha256_file(path) for key, path in files.items()},
        "model": model,
        "model_digest": ollama_model_digest(endpoint, model),
        "endpoint": endpoint.rstrip("/"),
        "stage": stage,
        "selected_case_ids": list(selected_case_ids),
        "framework_versions": package_versions(),
        "financial_cost_usd": 0.0,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    identity = manifest_id(payload)
    payload["manifest_id"] = identity
    payload["experiment_id"] = identity
    return payload


def result_provenance(manifest: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "experiment_id",
        "source_sha",
        "config_sha256",
        "cases_sha256",
        "packets_sha256",
        "runner_sha256",
        "evaluator_sha256",
        "requirements_sha256",
        "model",
        "model_digest",
        "execution_host",
        "financial_cost_usd",
    )
    return {key: manifest[key] for key in keys}


def validate_manifest(manifest: dict[str, Any], root: Path) -> bool:
    required = {
        "schema_version",
        "runner_id",
        "execution_host",
        "source_sha",
        "config_sha256",
        "cases_sha256",
        "packets_sha256",
        "runner_sha256",
        "evaluator_sha256",
        "requirements_sha256",
        "model",
        "model_digest",
        "endpoint",
        "stage",
        "selected_case_ids",
        "framework_versions",
        "financial_cost_usd",
        "created_at_utc",
        "manifest_id",
        "experiment_id",
    }
    missing = required - set(manifest)
    if missing:
        raise ProvenanceError(f"manifest missing fields: {sorted(missing)}")
    if manifest["schema_version"] != "1.1":
        raise ProvenanceError("unsupported manifest schema")
    if str(manifest["runner_id"]).upper() != "YASSIN" or str(manifest["execution_host"]).upper() != "YASSIN":
        raise ProvenanceError("manifest runner/execution_host must be YASSIN")
    if float(manifest["financial_cost_usd"]) != 0.0:
        raise ProvenanceError("manifest financial_cost_usd must be zero")
    if manifest["source_sha"] != git_head(root):
        raise ProvenanceError("manifest source SHA does not match current HEAD")

    expected_files = {
        "config_sha256": root / "company" / "config" / "agent_bakeoff.json",
        "cases_sha256": root / "benchmarks" / "agent_runtime" / "cases.json",
        "packets_sha256": root / "benchmarks" / "agent_runtime" / "case_packets.json",
        "runner_sha256": root / "tools" / "run_agent_bakeoff_live.py",
        "evaluator_sha256": root / "company" / "runtime" / "agent_bakeoff.py",
        "requirements_sha256": root / "benchmarks" / "agent_runtime" / "requirements.txt",
    }
    for key, path in expected_files.items():
        if manifest[key] != sha256_file(path):
            raise ProvenanceError(f"manifest {key} does not match current file")

    expected_id = manifest_id(manifest)
    if manifest["manifest_id"] != expected_id or manifest["experiment_id"] != expected_id:
        raise ProvenanceError("manifest identity mismatch")
    return True


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
