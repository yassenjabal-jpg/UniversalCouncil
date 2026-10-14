from __future__ import annotations

from typing import Any


class ApplicationProfileError(ValueError):
    pass


_REQUIRED_PROFILE_FIELDS = {
    "application",
    "version",
    "task_classes",
    "apis_scripts",
    "semantic_selectors",
    "visual_anchors",
    "known_dialogs",
    "async_states",
    "failure_modes",
    "recovery",
    "verification",
    "unsafe_actions",
    "reusable_routines",
    "checkpoint_format",
}


def validate_application_profiles(cfg: dict[str, Any]) -> bool:
    if not isinstance(cfg, dict) or cfg.get("status") != "CANDIDATE_SHADOW_ONLY":
        raise ApplicationProfileError("application profiles must remain candidate shadow-only")
    if cfg.get("profile_growth_policy") != "PROVE_VALUE_BEFORE_ADDING_ANOTHER":
        raise ApplicationProfileError("application profile growth must require proven value")
    profiles = cfg.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        raise ApplicationProfileError("at least one application profile is required")

    for profile_id, profile in profiles.items():
        if not isinstance(profile, dict):
            raise ApplicationProfileError(f"{profile_id}: profile must be an object")
        missing = _REQUIRED_PROFILE_FIELDS - set(profile)
        if missing:
            raise ApplicationProfileError(f"{profile_id}: missing fields {sorted(missing)}")
        application = profile["application"]
        if application.get("id") != profile_id:
            raise ApplicationProfileError(f"{profile_id}: application id mismatch")
        version = profile["version"]
        if version.get("policy") != "DETECT_BEFORE_CONTROL":
            raise ApplicationProfileError(f"{profile_id}: version must be detected before control")
        scripts = profile["apis_scripts"]
        actions = scripts.get("supported_actions")
        if not isinstance(actions, list) or not actions or len(actions) != len(set(actions)):
            raise ApplicationProfileError(f"{profile_id}: supported actions must be unique and non-empty")
        if not isinstance(profile["task_classes"], list) or not profile["task_classes"]:
            raise ApplicationProfileError(f"{profile_id}: task_classes are required")
        verification = profile["verification"]
        if verification.get("receipt_status_success") != "PASS":
            raise ApplicationProfileError(f"{profile_id}: PASS receipt verification is required")
        if int(verification.get("timeout_seconds", 0)) <= 0:
            raise ApplicationProfileError(f"{profile_id}: verification timeout must be positive")
        checkpoint = profile["checkpoint_format"]
        if not isinstance(checkpoint, dict) or not checkpoint.get("kind"):
            raise ApplicationProfileError(f"{profile_id}: checkpoint format is required")
    return True


def assess_application_request(
    profile_id: str,
    runtime_observation: dict[str, Any],
    cfg: dict[str, Any],
) -> dict[str, Any]:
    validate_application_profiles(cfg)
    profiles = cfg["profiles"]
    if profile_id not in profiles:
        raise ApplicationProfileError(f"unknown application profile: {profile_id}")
    if not isinstance(runtime_observation, dict):
        raise ApplicationProfileError("runtime observation must be an object")

    profile = profiles[profile_id]
    action = str(runtime_observation.get("action") or "").strip()
    if not action:
        raise ApplicationProfileError("application action is required")

    detected = runtime_observation.get("detected")
    if detected not in {True, False}:
        raise ApplicationProfileError("detected must be explicitly true or false")

    if detected is False:
        return {
            "profile_id": profile_id,
            "control_allowed": False,
            "classification": "APPLICATION_NOT_DETECTED",
            "next_step": profile["recovery"]["application_not_detected"],
            "preferred_task_class": None,
            "preferred_route": None,
            "profile_added_value": True,
            "value_reason": "blocked impossible control before application dispatch",
            "checkpoint_format": profile["checkpoint_format"],
        }

    version = runtime_observation.get("version")
    if not isinstance(version, str) or not version.strip():
        raise ApplicationProfileError("detected application requires an observed version")

    supported = set(profile["apis_scripts"]["supported_actions"])
    if action not in supported:
        raise ApplicationProfileError(f"unsupported application action: {action}")

    return {
        "profile_id": profile_id,
        "control_allowed": True,
        "classification": "APPLICATION_DETECTED",
        "observed_version": version.strip(),
        "preferred_task_class": "structured_application",
        "preferred_route": "script_or_com",
        "supported_action": action,
        "verification": {
            "receipt_status": profile["verification"]["receipt_status_success"],
            "receipt_relative_path": profile["verification"]["receipt_relative_path"],
            "timeout_seconds": profile["verification"]["timeout_seconds"],
        },
        "checkpoint_format": profile["checkpoint_format"],
        "profile_added_value": True,
        "value_reason": "selected structured script bridge with explicit receipt verification",
    }
