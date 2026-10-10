from dataclasses import replace

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


def select_route(
    request: ResearchRequest,
    policy: dict,
    provider_health: dict,
) -> GatewayResult:
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

    route = policy.get("routes", {}).get(request.intent)
    if not route:
        return GatewayResult(
            status=GatewayStatus.UNAVAILABLE,
            request_id=request.request_id,
            message=f"no configured route for intent: {request.intent}",
        )

    had_auth_block = False
    for provider_id in route.get("providers", ()):
        if not _provider_allowed(request, policy, provider_id):
            had_auth_block = True
            continue
        health = provider_health.get(provider_id)
        if not health:
            continue
        if health.status in {ProviderStatus.BLOCKED, ProviderStatus.UNAVAILABLE}:
            continue
        if health.status not in {ProviderStatus.HEALTHY, ProviderStatus.DEGRADED}:
            continue
        warnings = health.warnings
        return GatewayResult(
            status=GatewayStatus.OK,
            request_id=request.request_id,
            provider=provider_id,
            backend=health.backend,
            message="route selected",
            warnings=warnings,
        )

    status = GatewayStatus.BLOCKED if had_auth_block else GatewayStatus.UNAVAILABLE
    message = "eligible provider blocked by auth policy" if had_auth_block else "no healthy eligible provider"
    return GatewayResult(status=status, request_id=request.request_id, message=message)


def _provider_health_map(providers: dict[str, object]) -> dict:
    result = {}
    for provider_id, provider in providers.items():
        try:
            result[provider_id] = provider.health()
        except Exception:
            continue
    return result


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


def route_request(
    request: ResearchRequest,
    policy: dict,
    providers: dict[str, object],
) -> GatewayResult:
    health_map = _provider_health_map(providers)
    selected = select_route(request, policy, health_map)
    if selected.status != GatewayStatus.OK or not selected.provider:
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

    route = policy.get("routes", {}).get(request.intent, {})
    for fallback_id in route.get("fallbacks", ()):
        if fallback_id == selected.provider:
            continue
        fallback = providers.get(fallback_id)
        if fallback is None:
            continue
        fallback_health = health_map.get(fallback_id)
        if fallback_health is None:
            try:
                fallback_health = fallback.health()
            except Exception:
                continue
        fallback_policy = dict(policy)
        fallback_policy["routes"] = dict(policy.get("routes", {}))
        fallback_policy["routes"][request.intent] = {
            "providers": [fallback_id],
            "fallbacks": [],
        }
        eligible = select_route(request, fallback_policy, {fallback_id: fallback_health})
        if eligible.status != GatewayStatus.OK:
            continue
        fallback_result = _invoke(fallback, request, fallback_id, eligible.backend)
        if fallback_result.status in {GatewayStatus.OK, GatewayStatus.PARTIAL}:
            metadata = dict(fallback_result.metadata)
            metadata["fallback_from"] = selected.provider
            metadata["fallback_reason"] = primary.message or primary.status.value
            return replace(fallback_result, metadata=metadata)

    return primary
