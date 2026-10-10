import hashlib
import json
from typing import Any

from .intelligence_models import GatewayResult, ResearchRequest

_ALLOWED_LABELS = {
    "VERIFIED FACT",
    "AUTHORITATIVE EXTERNAL",
    "CORROBORATED COMMUNITY",
    "COMMUNITY LEAD",
    "INFERENCE",
    "OPINION",
    "ASSUMPTION",
    "UNKNOWN",
}


def hash_materialized_content(content: bytes | str | Any) -> str:
    if isinstance(content, bytes):
        payload = content
    elif isinstance(content, str):
        payload = content.encode("utf-8")
    else:
        payload = json.dumps(
            content,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _trusted_label(source_type: str, requested_label: str | None) -> str:
    label = requested_label if requested_label in _ALLOWED_LABELS else "UNKNOWN"
    if source_type.upper().startswith("COMMUNITY"):
        if label not in {"COMMUNITY LEAD", "CORROBORATED COMMUNITY"}:
            return "COMMUNITY LEAD"
    return label


def normalize_evidence(
    request: ResearchRequest,
    provider_result: GatewayResult,
    *,
    retrieved_at: str,
) -> dict:
    metadata = dict(provider_result.metadata or {})
    source_type = str(metadata.get("source_type") or "UNKNOWN")
    source_locator = str(
        metadata.get("source_locator")
        or request.target_url
        or request.query
        or ""
    )
    auth_level = str(
        metadata.get("auth_level")
        or request.auth_requirement.value
    )
    evidence_label = _trusted_label(
        source_type,
        metadata.get("evidence_label"),
    )
    content_hash = (
        hash_materialized_content(provider_result.payload)
        if provider_result.payload is not None
        else None
    )
    seed = "|".join(
        [
            request.request_id,
            str(provider_result.provider or ""),
            str(provider_result.backend or ""),
            source_locator,
            retrieved_at,
            content_hash or "",
        ]
    )
    evidence_id = hashlib.sha256(seed.encode("utf-8")).hexdigest()

    envelope = {
        "evidence_id": evidence_id,
        "request_id": request.request_id,
        "provider": provider_result.provider,
        "backend": provider_result.backend,
        "source_type": source_type,
        "source_locator": source_locator,
        "retrieved_at": retrieved_at,
        "auth_level": auth_level,
        "freshness": request.freshness_requirement,
        "content_summary": provider_result.payload,
        "raw_reference": metadata.get("raw_reference"),
        "content_hash": content_hash,
        "evidence_label": evidence_label,
        "limitations": list(provider_result.limitations),
        "warnings": list(provider_result.warnings),
    }
    if "fallback_from" in metadata:
        envelope["fallback_from"] = metadata["fallback_from"]
    if "fallback_reason" in metadata:
        envelope["fallback_reason"] = metadata["fallback_reason"]
    return envelope
