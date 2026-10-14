from __future__ import annotations

from typing import Any


class ContributionLedgerError(ValueError):
    pass


def validate_contribution_config(cfg: dict[str, Any]) -> bool:
    if not isinstance(cfg, dict) or cfg.get("status") != "CANDIDATE_SHADOW_ONLY":
        raise ContributionLedgerError("contribution ledger must remain candidate shadow-only")
    if cfg.get("use_as_voting_weights") is not False:
        raise ContributionLedgerError("contribution metrics must never become voting weights")
    metrics = cfg.get("metrics")
    if not isinstance(metrics, list) or not metrics or len(metrics) != len(set(metrics)):
        raise ContributionLedgerError("metrics must be a unique non-empty list")
    recommendations = set(cfg.get("recommendations", []))
    expected = {"KEEP","NARROW","MERGE","ON_DEMAND","IMPROVEMENT_TRIAL","REMOVE"}
    if recommendations != expected:
        raise ContributionLedgerError("recommendation set does not match canonical R12 outcomes")
    if int(cfg.get("minimum_observations", 0)) < 3:
        raise ContributionLedgerError("minimum_observations must be at least 3")
    if int(cfg.get("remove_minimum_observations", 0)) < int(cfg["minimum_observations"]):
        raise ContributionLedgerError("removal requires at least the normal observation window")
    if cfg.get("removal_requires_owner_review") is not True:
        raise ContributionLedgerError("REMOVE must require Owner review")
    return True


def _validate_observation(observation: dict[str, Any], metrics: list[str]) -> None:
    if not isinstance(observation, dict):
        raise ContributionLedgerError("observation must be an object")
    if set(observation) != set(metrics):
        extra = sorted(set(observation) - set(metrics))
        missing = sorted(set(metrics) - set(observation))
        raise ContributionLedgerError(f"observation metric mismatch; extra={extra}, missing={missing}")
    for metric in metrics:
        value = observation[metric]
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ContributionLedgerError(f"{metric} must be numeric")
        if value < 0:
            raise ContributionLedgerError(f"{metric} cannot be negative")


def evaluate_role_contribution(
    role_id: str,
    observations: list[dict[str, Any]],
    cfg: dict[str, Any],
) -> dict[str, Any]:
    validate_contribution_config(cfg)
    if not role_id.strip():
        raise ContributionLedgerError("role_id is required")
    if not isinstance(observations, list) or not observations:
        raise ContributionLedgerError("at least one observation is required")

    metrics = list(cfg["metrics"])
    for observation in observations:
        _validate_observation(observation, metrics)

    totals = {
        metric: sum(float(observation[metric]) for observation in observations)
        for metric in metrics
    }
    n = len(observations)
    contribution_total = sum(
        totals[name]
        for name in (
            "unique_evidence",
            "unique_objection",
            "option_added",
            "test_changed",
            "decision_changed",
        )
    )
    duplicate_total = totals["duplicate_reasoning"]
    blocker_errors = totals["false_blocker"] + totals["missed_blocker"]
    human_override = totals["human_override"]

    reasons: list[str] = []
    recommendation = "KEEP"

    if n < int(cfg["minimum_observations"]):
        recommendation = "IMPROVEMENT_TRIAL"
        reasons.append("insufficient_observations")
    else:
        duplicate_ratio = duplicate_total / max(1.0, duplicate_total + contribution_total)
        blocker_error_rate = blocker_errors / max(
            1.0,
            blocker_errors + totals["unique_objection"] + totals["unique_evidence"],
        )
        low_contribution = contribution_total / max(1.0, float(n))

        if (
            n >= int(cfg["remove_minimum_observations"])
            and contribution_total == 0
            and duplicate_total >= n
            and blocker_errors >= n
        ):
            recommendation = "REMOVE"
            reasons.extend(["low_unique_contribution", "duplicate_reasoning", "persistent_blocker_errors"])
        elif blocker_error_rate >= float(cfg["thresholds"]["blocker_error_rate_for_trial"]):
            recommendation = "IMPROVEMENT_TRIAL"
            reasons.append("blocker_quality")
        elif duplicate_ratio >= float(cfg["thresholds"]["duplication_ratio_for_narrow"]):
            recommendation = "NARROW"
            reasons.append("duplicate_reasoning")
            if contribution_total == 0:
                reasons.append("low_unique_contribution")
        elif low_contribution < float(cfg["thresholds"]["low_contribution_ratio"]):
            recommendation = "ON_DEMAND"
            reasons.append("low_unique_contribution")
        else:
            recommendation = "KEEP"
            reasons.append("sustained_unique_contribution")

        if human_override > 0 and recommendation == "KEEP":
            reasons.append("human_override_observed")

    return {
        "role_id": role_id,
        "observation_count": n,
        "totals": totals,
        "recommendation": recommendation,
        "reasons": reasons,
        "requires_owner_review": recommendation == "REMOVE",
        "use_as_voting_weight": False,
    }
