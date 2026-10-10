from dataclasses import replace

from .capability_scout import build_evidence_channel_gap
from .intelligence_models import (
    AuthRequirement,
    GatewayResult,
    GatewayStatus,
    ProviderStatus,
    ResearchRequest,
    validate_request,
)


def _provider_allowed(request: ResearchRequest, policy: dict, provider_id: str) -> bool:
    provider_class = policy.get("provider_classes", {}).get(provider_id)
    if request.allowed_provider_classes and provider_class not in request.allowed_provider_classes:
        return False
    if provider_id == "agent_reach" and request.auth_requirement != AuthRequirement.PUBLIC_ONLY:
        return False
    return True


def _policy_precheck(request: ResearchRequest, policy: dict) -> GatewayResult | None:
    errors = validate_request(request)
    if errors:
        return GatewayResult(
            status=GatewayStatus.INVALID_REQUEST,
            request_id=request.request_id,
            message="; ".join(errors),
        )
    if request.intent in set(policy.get("blocked_intents", ())):
        return GatewayResult(
            status=GatewayStatus.BLOCKED,
            request_id=request.request_id,
            message=f"intent blocked by policy: {request.intent}",
        )
    if request.intent not in policy.get("routes", {}):
        return GatewayResult(
            status=GatewayStatus.UNAVAILABLE,
            request_id=request.request_id,
            message=f"no configured route for intent: {request.intent}",
        )
    return None


def select_route(
    request: ResearchRequest,
    policy: dict,
    provider_health: dict,
) -> GatewayResult:
    precheck = _policy_precheck(request, policy)
    if precheck is not None:
        return precheck

    route = policy["routes"][request.intent]
    had_auth_block = False
    had_provider_block = False

    for provider_id in route.get("providers", ()):
        if not _provider_allowed(request, policy, provider_id):
            had_auth_block = True
            continue

        health = provider_health.get(provider_id)
        if not health:
            continue

        if provider_id == "agent_reach" and health.auth_level != AuthRequirement.PUBLIC_ONLY:
            had_auth_block = True
            continue

        if health.status == ProviderStatus.BLOCKED:
            had_provider_block = True
            continue
        if health.status == ProviderStatus.UNAVAILABLE:
            continue
        if health.status not in {ProviderStatus.HEALTHY, ProviderStatus.DEGRADED}:
            continue

        return GatewayResult(
            status=GatewayStatus.OK,
            request_id=request.request_id,
            provider=provider_id,
            backend=health.backend,
            message="route selected",
            warnings=health.warnings,
        )

    if had_auth_block or had_provider_block:
        return GatewayResult(
            status=GatewayStatus.BLOCKED,
            request_id=request.request_id,
            message=(
                "eligible provider blocked by auth policy"
                if had_auth_block
                else "eligible provider blocked by provider policy"
            ),
        )
    return GatewayResult(
        status=GatewayStatus.UNAVAILABLE,
        request_id=request.request_id,
        message="no healthy eligible provider",
    )


def _health_one(provider) -> object | None:
    try:
        return provider.health()
    except Exception:
        return None


def _invoke(provider, request: ResearchRequest, provider_id: str, backend: str | None) -> GatewayResult:
    try:
        result = provider.read(request)
    except Exception as exc:
        return GatewayResult(
            status=GatewayStatus.PROVIDER_ERROR,
            request_id=request.request_id,
            provider=provider_id,
            backend=backend,
            message=str(exc),
        )
    if not isinstance(result, GatewayResult):
        return GatewayResult(
            status=GatewayStatus.PROVIDER_ERROR,
            request_id=request.request_id,
            provider=provider_id,
            backend=backend,
            message="provider returned invalid result type",
        )
    if result.provider is None or result.backend is None:
        return replace(
            result,
            provider=result.provider or provider_id,
            backend=result.backend or backend,
        )
    return result


def _attempt_fallback(
    request: ResearchRequest,
    policy: dict,
    providers: dict[str, object],
    route: dict,
    *,
    from_provider: str | None,
    reason: str,
) -> GatewayResult | None:
    for fallback_id in route.get("fallbacks", ()):
        if fallback_id == from_provider:
            continue
        if not _provider_allowed(request, policy, fallback_id):
            continue

        fallback = providers.get(fallback_id)
        if fallback is None:
            continue

        fallback_health = _health_one(fallback)
        if fallback_health is None:
            continue

        fallback_policy = dict(policy)
        fallback_policy["routes"] = dict(policy.get("routes", {}))
        fallback_policy["routes"][request.intent] = {
            "providers": [fallback_id],
            "fallbacks": [],
        }
        eligible = select_route(
            request,
            fallback_policy,
            {fallback_id: fallback_health},
        )
        if eligible.status != GatewayStatus.OK:
            continue

        fallback_result = _invoke(
            fallback,
            request,
            fallback_id,
            eligible.backend,
        )
        if fallback_result.status not in {GatewayStatus.OK, GatewayStatus.PARTIAL}:
            continue

        metadata = dict(fallback_result.metadata)
        metadata["fallback_from"] = from_provider
        metadata["fallback_reason"] = reason
        return replace(fallback_result, metadata=metadata)

    return None


def route_request(
    request: ResearchRequest,
    policy: dict,
    providers: dict[str, object],
) -> GatewayResult:
    precheck = _policy_precheck(request, policy)
    if precheck is not None:
        return precheck

    route = policy["routes"][request.intent]
    health_map = {}
    for provider_id in route.get("providers", ()):
        if not _provider_allowed(request, policy, provider_id):
            continue
        provider = providers.get(provider_id)
        if provider is None:
            continue
        health = _health_one(provider)
        if health is not None:
            health_map[provider_id] = health

    selected = select_route(request, policy, health_map)
    if selected.status != GatewayStatus.OK or not selected.provider:
        if selected.status == GatewayStatus.UNAVAILABLE and route.get("fallbacks"):
            primary_id = next(iter(route.get("providers", ())), None)
            fallback = _attempt_fallback(
                request,
                policy,
                providers,
                route,
                from_provider=primary_id,
                reason="primary health unavailable",
            )
            if fallback is not None:
                return fallback
        return selected

    provider = providers.get(selected.provider)
    if provider is None:
        return GatewayResult(
            status=GatewayStatus.UNAVAILABLE,
            request_id=request.request_id,
            provider=selected.provider,
            backend=selected.backend,
            message="selected provider is not registered",
        )

    primary = _invoke(provider, request, selected.provider, selected.backend)
    if primary.status not in {GatewayStatus.PROVIDER_ERROR, GatewayStatus.UNAVAILABLE}:
        return primary

    fallback = _attempt_fallback(
        request,
        policy,
        providers,
        route,
        from_provider=selected.provider,
        reason=primary.message or primary.status.value,
    )
    return fallback or primary


_MATERIAL_EVIDENCE_PURPOSES = {
    "DECISION_HINGE",
    "MATERIAL_DECISION",
    "COMMERCIAL_VALIDATION",
    "SECURITY_REVIEW",
    "LEGAL_REVIEW",
    "HIGH_STAKES",
}


def capability_gap_from_gateway(
    request: ResearchRequest,
    result: GatewayResult,
) -> dict | None:
    if result.status not in {GatewayStatus.BLOCKED, GatewayStatus.UNAVAILABLE}:
        return None
    purpose = str(request.evidence_purpose or "").strip().upper()
    if purpose not in _MATERIAL_EVIDENCE_PURPOSES:
        return None
    summary = (
        f"Research evidence channel '{request.intent}' is "
        f"{result.status.value.lower()} for purpose '{purpose}'."
    )
    return build_evidence_channel_gap(
        f"INTEL-{request.request_id}",
        summary,
        impact_metric="evidence_coverage",
    )
