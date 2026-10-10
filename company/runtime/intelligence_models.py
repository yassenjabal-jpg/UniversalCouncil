from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AuthRequirement(str, Enum):
    PUBLIC_ONLY = "PUBLIC_ONLY"
    AUTHENTICATED = "AUTHENTICATED"


class GatewayStatus(str, Enum):
    OK = "OK"
    PARTIAL = "PARTIAL"
    UNAVAILABLE = "UNAVAILABLE"
    BLOCKED = "BLOCKED"
    INVALID_REQUEST = "INVALID_REQUEST"
    PROVIDER_ERROR = "PROVIDER_ERROR"


class ProviderStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class ResearchRequest:
    request_id: str
    intent: str
    query: str = ""
    target_url: str | None = None
    freshness_requirement: str = "CURRENT"
    auth_requirement: AuthRequirement = AuthRequirement.PUBLIC_ONLY
    allowed_provider_classes: tuple[str, ...] = ()
    evidence_purpose: str = "GENERAL"
    max_results: int = 10


@dataclass(frozen=True)
class ProviderHealth:
    provider_id: str
    status: ProviderStatus
    backend: str | None = None
    auth_level: AuthRequirement = AuthRequirement.PUBLIC_ONLY
    verified_at: str | None = None
    identity: str | None = None
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class GatewayResult:
    status: GatewayStatus
    request_id: str
    provider: str | None = None
    backend: str | None = None
    message: str = ""
    payload: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
    limitations: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


def validate_request(request: ResearchRequest) -> list[str]:
    errors: list[str] = []
    if not str(request.request_id).strip():
        errors.append("request_id is required")
    if not str(request.intent).strip():
        errors.append("intent is required")
    if not str(request.query).strip() and not str(request.target_url or "").strip():
        errors.append("query or target_url is required")
    if request.max_results < 1 or request.max_results > 50:
        errors.append("max_results must be between 1 and 50")
    if not isinstance(request.auth_requirement, AuthRequirement):
        errors.append("auth_requirement must be an AuthRequirement")
    return errors
