from __future__ import annotations

import copy
import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from company.runtime.tool_authority import validate_registry


class EvidenceSyncError(ValueError):
    pass


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


def validate_receipt(receipt: dict[str, Any], source: dict[str, Any], source_root: Path) -> bool:
    missing = RECEIPT_REQUIRED - set(receipt)
    if missing:
        raise EvidenceSyncError(f"receipt missing fields: {sorted(missing)}")
    if FORBIDDEN_AUTHORITY_FIELDS & set(receipt):
        raise EvidenceSyncError("receipt may not contain authority-changing fields")
    if receipt["schema_version"] != "1.0":
        raise EvidenceSyncError("receipt schema_version must be 1.0")
    if receipt["source_project"] != source["project_id"]:
        raise EvidenceSyncError("receipt source_project mismatch")
    if receipt["capability_id"] not in source["allowed_capability_ids"]:
        raise EvidenceSyncError("receipt capability is not allowlisted")
    if receipt["status"] != "RUNTIME_VERIFIED":
        raise EvidenceSyncError("only RUNTIME_VERIFIED receipts are importable")
    if not re.fullmatch(r"[0-9a-f]{40}", str(receipt["source_commit"])):
        raise EvidenceSyncError("source_commit must be a full lowercase git SHA")
    _parse_observed_at(str(receipt["observed_at"]))
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
            target.relative_to(root)
        except ValueError as exc:
            raise EvidenceSyncError("artifact path escapes source root") from exc
        if not target.is_file():
            raise EvidenceSyncError(f"artifact missing: {artifact['path']}")
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        if digest != artifact["sha256"]:
            raise EvidenceSyncError(f"artifact hash mismatch: {artifact['path']}")
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
    for operation in binding["operations"]:
        record = next((item for item in updated["capabilities"] if item.get("operation") == operation), None)
        if record is None:
            raise EvidenceSyncError(f"authority operation not found: {operation}")
        before = {field: copy.deepcopy(record[field]) for field in IMMUTABLE_AUTHORITY_FIELDS}
        record["evidence_level"] = receipt["evidence_level"]
        record["last_verified_at"] = receipt["observed_at"][:10]
        record["source_or_pin"] = receipt["source_commit"]
        record["evidence_receipt"] = imported_receipt_path
        record["verified_scope"] = list(receipt["verified_scope"])
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
            if apply:
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            working_registry = apply_receipt_to_registry(
                working_registry,
                receipt,
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
        if record["source_or_pin"] != receipt["source_commit"]:
            raise EvidenceSyncError(f"{record['operation']}: source pin differs from imported receipt")
        if record["evidence_level"] != receipt["evidence_level"]:
            raise EvidenceSyncError(f"{record['operation']}: evidence level differs from imported receipt")
        if record["last_verified_at"] != receipt["observed_at"][:10]:
            raise EvidenceSyncError(f"{record['operation']}: verification date differs from imported receipt")
    return True
