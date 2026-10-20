from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from enum import StrEnum
from typing import Any

from company.runtime.tool_authority import validate_registry


class EvidenceSyncError(ValueError):
    pass


class EvidenceState(StrEnum):
    HISTORICAL = "HISTORICAL"
    CURRENT_VERIFIED = "CURRENT_VERIFIED"
    STALE = "STALE"
    REVOKED = "REVOKED"


RECEIPT_REQUIRED = {
    "schema_version",
    "receipt_id",
    "source_project",
    "source_commit",
    "observed_at",
    "capability_id",
    "status",
    "evidence_level",
    "verified_scope",
    "unverified_scope",
    "artifacts",
}

V11_RECEIPT_REQUIRED = {
    "source_repository",
    "component",
    "component_version",
    "host",
    "session_id",
    "expires_at",
    "verifier",
    "verifier_version",
}

FORBIDDEN_AUTHORITY_FIELDS = {
    "classification",
    "authentication_class",
    "effect",
    "approval_policy",
    "allowed_scope",
    "prohibited_scope",
    "enforcement",
}

IMMUTABLE_AUTHORITY_FIELDS = (
    "classification",
    "authentication_class",
    "effect",
    "approval_policy",
    "allowed_scope",
    "prohibited_scope",
    "enforcement",
)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvidenceSyncError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise EvidenceSyncError(f"{path}: JSON root must be an object")
    return data


def validate_sync_config(cfg: dict[str, Any]) -> bool:
    if cfg.get("version") != "1.0":
        raise EvidenceSyncError("evidence sync config must be version 1.0")
    if not isinstance(cfg.get("sources"), list):
        raise EvidenceSyncError("sources must be a list")
    seen: set[str] = set()
    for source in cfg["sources"]:
        if not isinstance(source, dict):
            raise EvidenceSyncError("source must be an object")
        for key in (
            "id",
            "project_id",
            "enabled",
            "receipt_glob",
            "allowed_capability_ids",
            "authority_bindings",
        ):
            if key not in source:
                raise EvidenceSyncError(f"source missing {key}")
        if source["id"] in seen:
            raise EvidenceSyncError(f"duplicate source id: {source['id']}")
        seen.add(source["id"])
        allowed = set(source["allowed_capability_ids"])
        bindings = set(source["authority_bindings"])
        if not bindings.issubset(allowed):
            raise EvidenceSyncError(f"{source['id']}: authority binding not allowlisted")
        repository_identity = source.get("repository_identity")
        if repository_identity is not None and (not isinstance(repository_identity, str) or not repository_identity):
            raise EvidenceSyncError(f"{source['id']}: repository_identity must be a non-empty string")
        component = source.get("component")
        if component is not None and (not isinstance(component, str) or not component):
            raise EvidenceSyncError(f"{source['id']}: component must be a non-empty string")
        expected_host = source.get("expected_host")
        if expected_host is not None and (not isinstance(expected_host, str) or not expected_host):
            raise EvidenceSyncError(f"{source['id']}: expected_host must be a non-empty string")
        max_age = source.get("max_receipt_age_days", 30)
        if not isinstance(max_age, int) or max_age < 1:
            raise EvidenceSyncError(f"{source['id']}: max_receipt_age_days must be a positive integer")
        revoked = source.get("revoked_receipt_ids", [])
        if not isinstance(revoked, list) or not all(isinstance(item, str) and item for item in revoked):
            raise EvidenceSyncError(f"{source['id']}: revoked_receipt_ids must be a string list")
        for capability_id, binding in source["authority_bindings"].items():
            operations = binding.get("operations")
            if not isinstance(operations, list) or not operations:
                raise EvidenceSyncError(f"{source['id']}/{capability_id}: operations must be a non-empty list")
            scoped = binding.get("operation_verified_scope", {})
            if scoped:
                if not isinstance(scoped, dict) or not set(scoped).issubset(set(operations)):
                    raise EvidenceSyncError(
                        f"{source['id']}/{capability_id}: operation_verified_scope must map approved operations"
                    )
                allowed_verified = set(binding.get("allowed_verified_scope", []))
                for operation, scopes in scoped.items():
                    if not isinstance(scopes, list) or not scopes:
                        raise EvidenceSyncError(
                            f"{source['id']}/{capability_id}/{operation}: verified scope must be non-empty"
                        )
                    if not set(scopes).issubset(allowed_verified):
                        raise EvidenceSyncError(
                            f"{source['id']}/{capability_id}/{operation}: operation scope exceeds allowlist"
                        )
    return True


def resolve_source_root(source: dict[str, Any], env: dict[str, str] | None = None) -> Path | None:
    env = os.environ if env is None else env
    env_name = source.get("root_env")
    if env_name and env.get(env_name):
        return Path(env[env_name]).expanduser().resolve()
    hint = source.get("root_hint")
    if hint:
        candidate = Path(hint).expanduser()
        if candidate.exists():
            return candidate.resolve()
    return None


def _parse_observed_at(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise EvidenceSyncError("observed_at must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise EvidenceSyncError("observed_at must include a timezone")
    return parsed


def _git_source_bytes(source_root: Path, commit: str, relative_path: str) -> bytes:
    try:
        completed = subprocess.run(
            ["git", "-C", str(source_root), "show", f"{commit}:{relative_path}"],
            check=False,
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise EvidenceSyncError(f"cannot verify source commit artifact: {exc}") from exc
    if completed.returncode != 0:
        raise EvidenceSyncError(f"artifact is not bound to source_commit: {relative_path}")
    return completed.stdout


def _verify_source_commit(source_root: Path, commit: str) -> None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(source_root), "cat-file", "-e", f"{commit}^{{commit}}"],
            check=False,
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise EvidenceSyncError(f"cannot verify source_commit: {exc}") from exc
    if completed.returncode != 0:
        raise EvidenceSyncError("source_commit does not exist in the approved source repository")


def _parse_time(value: str, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise EvidenceSyncError(f"{field} must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise EvidenceSyncError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def receipt_evidence_state(
    receipt: dict[str, Any],
    source: dict[str, Any],
    *,
    as_of: datetime | None = None,
) -> EvidenceState:
    now = as_of or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise EvidenceSyncError("evidence as_of must be timezone-aware")
    now = now.astimezone(timezone.utc)

    if receipt.get("receipt_id") in set(source.get("revoked_receipt_ids", [])):
        return EvidenceState.REVOKED

    observed = _parse_time(str(receipt.get("observed_at", "")), "observed_at")
    max_age_days = int(source.get("max_receipt_age_days", 30))
    default_expiry = observed + timedelta(days=max_age_days)
    expires_raw = receipt.get("expires_at")
    expires = _parse_time(str(expires_raw), "expires_at") if expires_raw else default_expiry
    if expires <= observed or now > expires or now - observed > timedelta(days=max_age_days):
        return EvidenceState.STALE

    if receipt.get("schema_version") != "1.1":
        return EvidenceState.HISTORICAL
    if V11_RECEIPT_REQUIRED - set(receipt):
        return EvidenceState.HISTORICAL
    if any(receipt.get(field) in (None, "") for field in V11_RECEIPT_REQUIRED):
        return EvidenceState.HISTORICAL
    return EvidenceState.CURRENT_VERIFIED


def build_imported_receipt(
    receipt: dict[str, Any],
    source: dict[str, Any],
    *,
    ingested_at: str | None = None,
) -> dict[str, Any]:
    ingested = _parse_time(
        ingested_at or datetime.now(timezone.utc).isoformat(),
        "ingested_at",
    )
    state = receipt_evidence_state(receipt, source, as_of=ingested)
    imported = copy.deepcopy(receipt)
    imported["ingested_at"] = ingested.isoformat()
    imported["evidence_state"] = state.value
    imported["evidence_metadata"] = {
        "source_repository": receipt.get("source_repository") or source.get("repository_identity"),
        "source_commit": receipt.get("source_commit"),
        "component": receipt.get("component") or source.get("component"),
        "component_version": receipt.get("component_version"),
        "host": receipt.get("host"),
        "session_id": receipt.get("session_id"),
        "observed_at": receipt.get("observed_at"),
        "ingested_at": imported["ingested_at"],
        "expires_at": receipt.get("expires_at"),
        "verifier": receipt.get("verifier"),
        "verifier_version": receipt.get("verifier_version"),
        "verified_scope": list(receipt.get("verified_scope", [])),
        "unverified_scope": list(receipt.get("unverified_scope", [])),
    }
    return imported


def validate_receipt(
    receipt: dict[str, Any],
    source: dict[str, Any],
    source_root: Path,
    *,
    as_of: datetime | None = None,
) -> bool:
    missing = RECEIPT_REQUIRED - set(receipt)
    if missing:
        raise EvidenceSyncError(f"receipt missing fields: {sorted(missing)}")
    if FORBIDDEN_AUTHORITY_FIELDS & set(receipt):
        raise EvidenceSyncError("receipt may not contain authority-changing fields")
    if receipt["schema_version"] not in {"1.0", "1.1"}:
        raise EvidenceSyncError("receipt schema_version must be 1.0 or 1.1")
    if receipt["schema_version"] == "1.1":
        missing_v11 = V11_RECEIPT_REQUIRED - set(receipt)
        if missing_v11:
            raise EvidenceSyncError(f"v1.1 receipt missing fields: {sorted(missing_v11)}")
        for field in V11_RECEIPT_REQUIRED:
            if receipt.get(field) in (None, ""):
                raise EvidenceSyncError(f"v1.1 receipt {field} must be non-empty")
        if receipt["source_repository"] != source.get("repository_identity"):
            raise EvidenceSyncError("receipt source_repository mismatch")
        if receipt["component"] != source.get("component"):
            raise EvidenceSyncError("receipt component mismatch")
        expected_host = source.get("expected_host")
        if expected_host and receipt["host"] != expected_host:
            raise EvidenceSyncError("receipt host mismatch")
        expires_at = _parse_time(str(receipt["expires_at"]), "expires_at")
        observed_for_expiry = _parse_time(str(receipt["observed_at"]), "observed_at")
        if expires_at <= observed_for_expiry:
            raise EvidenceSyncError("receipt expires_at must be later than observed_at")
    elif source.get("allow_legacy_historical", True) is not True:
        raise EvidenceSyncError("legacy evidence receipts are disabled for this source")
    if receipt["source_project"] != source["project_id"]:
        raise EvidenceSyncError("receipt source_project mismatch")
    if receipt["capability_id"] not in source["allowed_capability_ids"]:
        raise EvidenceSyncError("receipt capability is not allowlisted")
    if receipt["status"] != "RUNTIME_VERIFIED":
        raise EvidenceSyncError("only RUNTIME_VERIFIED receipts are importable")
    if not re.fullmatch(r"[0-9a-f]{40}", str(receipt["source_commit"])):
        raise EvidenceSyncError("source_commit must be a full lowercase git SHA")
    observed_at = _parse_observed_at(str(receipt["observed_at"])).astimezone(timezone.utc)
    now = as_of or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise EvidenceSyncError("evidence as_of must be timezone-aware")
    now = now.astimezone(timezone.utc)
    if observed_at > now + timedelta(minutes=5):
        raise EvidenceSyncError("observed_at cannot be materially in the future")
    max_age_days = int(source.get("max_receipt_age_days", 30))
    if now - observed_at > timedelta(days=max_age_days):
        raise EvidenceSyncError("receipt evidence is stale")
    evidence_state = receipt_evidence_state(receipt, source, as_of=now)
    if evidence_state == EvidenceState.REVOKED:
        raise EvidenceSyncError("receipt has been revoked")
    if evidence_state == EvidenceState.STALE:
        raise EvidenceSyncError("receipt evidence is stale or expired")
    _verify_source_commit(source_root, str(receipt["source_commit"]))
    if not isinstance(receipt["verified_scope"], list) or not receipt["verified_scope"]:
        raise EvidenceSyncError("verified_scope must be a non-empty list")
    if not isinstance(receipt["unverified_scope"], list):
        raise EvidenceSyncError("unverified_scope must be a list")
    binding = source["authority_bindings"][receipt["capability_id"]]
    allowed_scope = set(binding["allowed_verified_scope"])
    if not set(receipt["verified_scope"]).issubset(allowed_scope):
        raise EvidenceSyncError("receipt overclaims verified_scope")
    if receipt["evidence_level"] not in binding["allowed_evidence_levels"]:
        raise EvidenceSyncError("receipt evidence_level is not allowed")
    if not isinstance(receipt["artifacts"], list) or not receipt["artifacts"]:
        raise EvidenceSyncError("receipt artifacts must be a non-empty list")

    root = source_root.resolve()
    for artifact in receipt["artifacts"]:
        if not isinstance(artifact, dict) or set(artifact) != {"path", "sha256"}:
            raise EvidenceSyncError("artifact must contain only path and sha256")
        target = (root / artifact["path"]).resolve()
        try:
            relative = target.relative_to(root).as_posix()
        except ValueError as exc:
            raise EvidenceSyncError("artifact path escapes source root") from exc
        committed_bytes = _git_source_bytes(root, str(receipt["source_commit"]), relative)
        digest = hashlib.sha256(committed_bytes).hexdigest()
        if digest != artifact["sha256"]:
            raise EvidenceSyncError(f"artifact hash mismatch at source_commit: {artifact['path']}")
    return True


def discover_receipts(source: dict[str, Any], env: dict[str, str] | None = None) -> list[tuple[Path, dict[str, Any]]]:
    root = resolve_source_root(source, env)
    if root is None:
        return []
    receipts: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted(root.glob(source["receipt_glob"])):
        receipt = _load_json(path)
        validate_receipt(receipt, source, root)
        receipts.append((path, receipt))
    return receipts


def latest_by_capability(receipts: list[tuple[Path, dict[str, Any]]]) -> dict[str, tuple[Path, dict[str, Any]]]:
    latest: dict[str, tuple[Path, dict[str, Any]]] = {}
    for item in receipts:
        capability = item[1]["capability_id"]
        current = latest.get(capability)
        if current is None or _parse_observed_at(item[1]["observed_at"]) > _parse_observed_at(
            current[1]["observed_at"]
        ):
            latest[capability] = item
    return latest


def apply_receipt_to_registry(
    registry: dict[str, Any],
    receipt: dict[str, Any],
    source: dict[str, Any],
    imported_receipt_path: str,
) -> dict[str, Any]:
    updated = copy.deepcopy(registry)
    binding = source["authority_bindings"][receipt["capability_id"]]
    state = receipt.get("evidence_state") or receipt_evidence_state(receipt, source).value
    metadata = copy.deepcopy(
        receipt.get("evidence_metadata") or build_imported_receipt(receipt, source)["evidence_metadata"]
    )
    operation_scopes = binding.get("operation_verified_scope", {})

    for operation in binding["operations"]:
        record = next((item for item in updated["capabilities"] if item.get("operation") == operation), None)
        if record is None:
            raise EvidenceSyncError(f"authority operation not found: {operation}")
        before = {field: copy.deepcopy(record[field]) for field in IMMUTABLE_AUTHORITY_FIELDS}

        if operation_scopes:
            allowed_for_operation = set(operation_scopes.get(operation, []))
            scoped = [item for item in receipt["verified_scope"] if item in allowed_for_operation]
        else:
            scoped = list(receipt["verified_scope"])

        previous_historical = copy.deepcopy(record.get("historical_capability"))
        if previous_historical is None and record.get("source_or_pin"):
            previous_historical = {
                "source_commit": record.get("source_or_pin"),
                "observed_at": record.get("last_verified_at"),
                "verified_scope": list(record.get("verified_scope", [])),
                "evidence_receipt": record.get("evidence_receipt"),
            }

        record["evidence_receipt"] = imported_receipt_path
        record["verified_scope"] = scoped

        if state == EvidenceState.CURRENT_VERIFIED.value and scoped:
            record["evidence_level"] = receipt["evidence_level"]
            record["last_verified_at"] = receipt["observed_at"][:10]
            record["source_or_pin"] = receipt["source_commit"]
            record["evidence_state"] = EvidenceState.CURRENT_VERIFIED.value
            record["historical_capability"] = metadata
            record["current_verified_capability"] = metadata
        else:
            record["evidence_state"] = EvidenceState.HISTORICAL.value
            record["historical_capability"] = previous_historical or metadata
            record["current_verified_capability"] = None

        after = {field: record[field] for field in IMMUTABLE_AUTHORITY_FIELDS}
        if before != after:
            raise EvidenceSyncError(f"receipt attempted authority escalation for {operation}")
    return updated


def sync_repository(
    repo_root: Path,
    env: dict[str, str] | None = None,
    apply: bool = False,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    cfg_path = repo_root / "company/config/evidence_sync.json"
    registry_path = repo_root / "company/config/tool_authority.json"
    cfg = _load_json(cfg_path)
    validate_sync_config(cfg)
    registry = _load_json(registry_path)
    validate_registry(registry)
    imported: list[str] = []
    unavailable_sources: list[str] = []
    working_registry = registry

    for source in cfg["sources"]:
        if not source["enabled"]:
            continue
        source_root = resolve_source_root(source, env)
        if source_root is None:
            unavailable_sources.append(source["id"])
            continue
        chosen = latest_by_capability(discover_receipts(source, env))
        for capability_id, (_, receipt) in chosen.items():
            relative = Path(cfg["import_dir"]) / source["id"] / f"{capability_id}.json"
            destination = repo_root / relative
            imported_receipt = build_imported_receipt(receipt, source)
            if apply:
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(
                    json.dumps(imported_receipt, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )
            working_registry = apply_receipt_to_registry(
                working_registry,
                imported_receipt,
                source,
                relative.as_posix(),
            )
            imported.append(relative.as_posix())

    validate_registry(working_registry)
    if apply and working_registry != registry:
        registry_path.write_text(json.dumps(working_registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return {
        "imported": imported,
        "unavailable_sources": unavailable_sources,
        "registry_changed": working_registry != registry,
        "registry": working_registry,
    }


def validate_imported_evidence(
    repo_root: Path,
    sync_cfg: dict[str, Any],
    registry: dict[str, Any],
) -> bool:
    repo_root = repo_root.resolve()
    validate_sync_config(sync_cfg)
    validate_registry(registry)

    operation_bindings: dict[str, tuple[dict[str, Any], str]] = {}
    for source in sync_cfg["sources"]:
        for capability_id, binding in source["authority_bindings"].items():
            for operation in binding["operations"]:
                if operation in operation_bindings:
                    raise EvidenceSyncError(f"operation mapped by multiple evidence sources: {operation}")
                operation_bindings[operation] = (source, capability_id)

    for record in registry["capabilities"]:
        receipt_path = record.get("evidence_receipt")
        if not receipt_path:
            continue
        binding = operation_bindings.get(record["operation"])
        if binding is None:
            raise EvidenceSyncError(f"{record['operation']}: evidence_receipt has no approved source binding")
        source, capability_id = binding
        target = (repo_root / receipt_path).resolve()
        try:
            target.relative_to(repo_root)
        except ValueError as exc:
            raise EvidenceSyncError(f"{record['operation']}: evidence receipt escapes repository") from exc
        if not target.is_file():
            raise EvidenceSyncError(f"{record['operation']}: imported evidence receipt is missing")
        receipt = _load_json(target)
        missing = RECEIPT_REQUIRED - set(receipt)
        if missing:
            raise EvidenceSyncError(f"{record['operation']}: imported receipt missing {sorted(missing)}")
        if FORBIDDEN_AUTHORITY_FIELDS & set(receipt):
            raise EvidenceSyncError(f"{record['operation']}: imported receipt contains authority fields")
        if receipt["source_project"] != source["project_id"]:
            raise EvidenceSyncError(f"{record['operation']}: imported source project mismatch")
        if receipt["capability_id"] != capability_id:
            raise EvidenceSyncError(f"{record['operation']}: imported capability mismatch")
        if receipt["status"] != "RUNTIME_VERIFIED":
            raise EvidenceSyncError(f"{record['operation']}: imported receipt is not runtime verified")
        operation_scopes = source["authority_bindings"][capability_id].get("operation_verified_scope", {})
        expected_scope = (
            [item for item in receipt["verified_scope"] if item in set(operation_scopes.get(record["operation"], []))]
            if operation_scopes
            else list(receipt["verified_scope"])
        )
        if record.get("verified_scope") != expected_scope:
            raise EvidenceSyncError(f"{record['operation']}: verified scope differs from operation binding")

        expected_current = receipt.get("evidence_state") == EvidenceState.CURRENT_VERIFIED.value and bool(
            expected_scope
        )
        if expected_current:
            if record.get("evidence_state") != EvidenceState.CURRENT_VERIFIED.value:
                raise EvidenceSyncError(f"{record['operation']}: current evidence state was not imported")
            if record["source_or_pin"] != receipt["source_commit"]:
                raise EvidenceSyncError(f"{record['operation']}: source pin differs from imported receipt")
            if record["evidence_level"] != receipt["evidence_level"]:
                raise EvidenceSyncError(f"{record['operation']}: evidence level differs from imported receipt")
            if record["last_verified_at"] != receipt["observed_at"][:10]:
                raise EvidenceSyncError(f"{record['operation']}: verification date differs from imported receipt")
            if record.get("current_verified_capability") != receipt.get("evidence_metadata"):
                raise EvidenceSyncError(f"{record['operation']}: current capability metadata differs from receipt")
        else:
            if record.get("evidence_state") != EvidenceState.HISTORICAL.value:
                raise EvidenceSyncError(f"{record['operation']}: unverified operation must remain historical")
            if record.get("current_verified_capability") is not None:
                raise EvidenceSyncError(
                    f"{record['operation']}: historical evidence cannot populate current capability"
                )
    return True
