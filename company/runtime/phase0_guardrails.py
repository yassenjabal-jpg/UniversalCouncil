from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any


class Phase0GuardError(ValueError):
    pass


class TrustClass(StrEnum):
    OWNER = "OWNER"
    GOVERNING_CONFIG = "GOVERNING_CONFIG"
    TRUSTED_REVIEW = "TRUSTED_REVIEW"
    UNTRUSTED = "UNTRUSTED"


class ModelFailure(StrEnum):
    RATE_LIMITED = "RATE_LIMITED"
    QUOTA_EXHAUSTED = "QUOTA_EXHAUSTED"
    PROVIDER_OVERLOADED = "PROVIDER_OVERLOADED"
    BILLING_BLOCKED = "BILLING_BLOCKED"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    NETWORK_UNAVAILABLE = "NETWORK_UNAVAILABLE"
    AUTH_FAILED = "AUTH_FAILED"


@dataclass(frozen=True)
class EvidenceEnvelope:
    source_id: str
    trust: TrustClass
    payload: dict[str, Any]
    observed_at: str

    def authority_projection(self) -> dict[str, Any]:
        if self.trust == TrustClass.UNTRUSTED:
            return {
                "source_id": self.source_id,
                "trust": self.trust.value,
                "authority_mutation_allowed": False,
                "routing_mutation_allowed": False,
                "credential_mutation_allowed": False,
            }
        return {
            "source_id": self.source_id,
            "trust": self.trust.value,
            "authority_mutation_allowed": self.trust
            in {
                TrustClass.OWNER,
                TrustClass.GOVERNING_CONFIG,
            },
            "routing_mutation_allowed": self.trust
            in {
                TrustClass.OWNER,
                TrustClass.GOVERNING_CONFIG,
            },
            "credential_mutation_allowed": False,
        }


def promote_memory_candidate(
    evidence: EvidenceEnvelope,
    *,
    reviewer_trust: TrustClass,
    fact: dict[str, Any],
) -> dict[str, Any]:
    if evidence.trust == TrustClass.UNTRUSTED and reviewer_trust not in {
        TrustClass.TRUSTED_REVIEW,
        TrustClass.OWNER,
    }:
        raise Phase0GuardError("untrusted evidence requires trusted review before memory promotion")

    forbidden = {
        "authority",
        "permissions",
        "credentials",
        "api_key",
        "access_token",
        "routing_policy",
        "model_policy",
        "tool_policy",
    }
    if any(str(k).lower() in forbidden for k in fact):
        raise Phase0GuardError("memory candidate may not promote authority/security policy fields")

    return {
        "source_id": evidence.source_id,
        "source_trust": evidence.trust.value,
        "reviewer_trust": reviewer_trust.value,
        "fact": dict(fact),
    }


@dataclass(frozen=True)
class RemoteCommand:
    command_id: str
    nonce: str
    idempotency_key: str
    issued_at: str
    expires_at: str
    target: str
    effects: tuple[str, ...]
    instruction: str
    owner_authorized: bool

    def stable_hash(self) -> str:
        data = {
            "command_id": self.command_id,
            "nonce": self.nonce,
            "idempotency_key": self.idempotency_key,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "target": self.target,
            "effects": list(self.effects),
            "instruction": self.instruction,
            "owner_authorized": self.owner_authorized,
        }
        raw = json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()


class ReplayGuard:
    def __init__(self) -> None:
        self._nonces: set[str] = set()
        self._idempotency: dict[str, str] = {}

    def accept(self, cmd: RemoteCommand, *, now: datetime | None = None) -> str:
        if not cmd.owner_authorized:
            raise Phase0GuardError("remote command requires owner authorization")
        if not cmd.command_id or not cmd.nonce or not cmd.idempotency_key:
            raise Phase0GuardError("remote command requires command_id, nonce and idempotency_key")
        if not cmd.target or not cmd.effects:
            raise Phase0GuardError("remote command requires bounded target and effects")

        now = now or datetime.now(timezone.utc)
        expires = _parse_time(cmd.expires_at)
        issued = _parse_time(cmd.issued_at)
        if expires <= issued:
            raise Phase0GuardError("remote command expiry must be after issue time")
        if now > expires:
            raise Phase0GuardError("remote command expired")

        digest = cmd.stable_hash()
        existing = self._idempotency.get(cmd.idempotency_key)
        if existing is not None:
            if existing != digest:
                raise Phase0GuardError("idempotency key reused with different command")
            return "DUPLICATE_SAME_COMMAND"

        if cmd.nonce in self._nonces:
            raise Phase0GuardError("remote command nonce replay detected")

        self._nonces.add(cmd.nonce)
        self._idempotency[cmd.idempotency_key] = digest
        return "ACCEPTED"


def _parse_time(value: str) -> datetime:
    if not value:
        raise Phase0GuardError("timestamp required")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise Phase0GuardError("timestamp must be timezone-aware")
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class GuiSessionState:
    interactive_session: bool
    desktop_locked: bool
    secure_desktop_or_uac: bool
    controller_available: bool


def require_gui_ready(state: GuiSessionState) -> bool:
    if not state.interactive_session:
        raise Phase0GuardError("GUI execution requires an interactive session")
    if state.desktop_locked:
        raise Phase0GuardError("GUI execution blocked: desktop is locked")
    if state.secure_desktop_or_uac:
        raise Phase0GuardError("GUI execution blocked: secure desktop/UAC is active")
    if not state.controller_available:
        raise Phase0GuardError("GUI execution blocked: controller lease unavailable")
    return True


@dataclass(frozen=True)
class ModelRoutingPolicy:
    selected_model: str
    manual_only: bool = True
    auto_fallback_enabled: bool = False
    approved_fallbacks: tuple[tuple[str, str], ...] = ()


def resolve_model_failure(
    policy: ModelRoutingPolicy,
    failure: ModelFailure,
    *,
    requested_fallback: str | None = None,
) -> dict[str, Any]:
    if not policy.selected_model:
        raise Phase0GuardError("selected_model is required")

    result = {
        "failed_model": policy.selected_model,
        "failure": failure.value,
        "action": "PAUSE_FOR_OWNER",
        "next_model": None,
    }

    if policy.manual_only:
        return result
    if not policy.auto_fallback_enabled or not requested_fallback:
        return result

    if (policy.selected_model, requested_fallback) not in set(policy.approved_fallbacks):
        raise Phase0GuardError("requested fallback is not owner-approved")

    result["action"] = "USE_APPROVED_FALLBACK"
    result["next_model"] = requested_fallback
    return result
