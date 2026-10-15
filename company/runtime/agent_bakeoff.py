from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


class BakeoffError(ValueError):
    pass


RESULT_MODES = {"MECHANICS_ONLY", "LIVE_DECISION"}
RESULT_STATES = {"COMPLETED", "FAILED", "BLOCKED", "UNKNOWN"}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BakeoffError(f"cannot load JSON {path}: {exc}") from exc


def validate_config(cfg: dict[str, Any]) -> bool:
    if cfg.get("version") != "1.0":
        raise BakeoffError("agent bake-off config must be version 1.0")
    if int(cfg.get("minimum_live_decision_cases", 0)) < 1:
        raise BakeoffError("minimum_live_decision_cases must be positive")
    if float(cfg.get("minimum_mechanics_score", -1)) < 0:
        raise BakeoffError("minimum_mechanics_score must be >= 0")
    desktop_min = float(cfg.get("minimum_desktop_execution_score", -1))
    if desktop_min < 0 or desktop_min > 1:
        raise BakeoffError("minimum_desktop_execution_score must be between 0 and 1")
    required_desktop_case_count = int(cfg.get("required_desktop_case_count", 0))
    if required_desktop_case_count < 1:
        raise BakeoffError("required_desktop_case_count must be positive")
    desktop_case_ids = cfg.get("desktop_required_case_ids")
    if not isinstance(desktop_case_ids, list) or len(desktop_case_ids) != required_desktop_case_count:
        raise BakeoffError("desktop_required_case_ids must match required_desktop_case_count")
    if int(cfg.get("desktop_required_passes", 0)) != required_desktop_case_count:
        raise BakeoffError("desktop_required_passes must equal required_desktop_case_count")
    if cfg.get("require_provenance") is not True:
        raise BakeoffError("require_provenance must be true for live bake-off")
    provenance_keys = cfg.get("required_provenance_keys")
    if not isinstance(provenance_keys, list) or not provenance_keys:
        raise BakeoffError("required_provenance_keys must be a non-empty list")
    required_mechanics = cfg.get("required_mechanics_for_winner")
    if not isinstance(required_mechanics, list) or not required_mechanics:
        raise BakeoffError("required_mechanics_for_winner must be a non-empty list")
    weights = cfg.get("weights")
    if not isinstance(weights, dict) or not weights:
        raise BakeoffError("weights must be a non-empty object")
    if not math.isclose(sum(float(v) for v in weights.values()), 1.0, abs_tol=1e-9):
        raise BakeoffError("weights must sum to 1.0")
    runtimes = cfg.get("runtimes")
    if not isinstance(runtimes, dict) or set(runtimes) < {"baseline", "openai_agents", "microsoft_agent_framework"}:
        raise BakeoffError("baseline, openai_agents and microsoft_agent_framework runtimes are required")
    return True


def validate_case(case: dict[str, Any]) -> bool:
    required = {
        "case_id",
        "source_artifact",
        "prompt",
        "expected_decision",
        "required_roles",
        "forbidden_roles",
        "expected_blockers",
        "required_dissent_tags",
        "desktop_required",
        "injected_failure",
    }
    missing = required - set(case)
    if missing:
        raise BakeoffError(f"case missing fields: {sorted(missing)}")
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]+", str(case["case_id"])):
        raise BakeoffError(f"invalid case_id: {case['case_id']}")
    for field in ("required_roles", "forbidden_roles", "expected_blockers", "required_dissent_tags"):
        if not isinstance(case[field], list):
            raise BakeoffError(f"{case['case_id']}: {field} must be a list")
    return True


def validate_result(result: dict[str, Any]) -> bool:
    required = {
        "runtime_id",
        "case_id",
        "mode",
        "status",
        "final_decision",
        "participants",
        "role_outputs",
        "blockers",
        "dissent_tags",
        "policy_violations",
        "human_override",
        "failure_recovered",
        "desktop",
        "usage",
        "latency_ms",
        "provenance",
    }
    missing = required - set(result)
    if missing:
        raise BakeoffError(f"result missing fields: {sorted(missing)}")
    if result["mode"] not in RESULT_MODES:
        raise BakeoffError(f"unsupported result mode: {result['mode']}")
    if result["status"] not in RESULT_STATES:
        raise BakeoffError(f"unsupported result status: {result['status']}")
    if not isinstance(result["participants"], list):
        raise BakeoffError("participants must be a list")
    if not isinstance(result["role_outputs"], dict):
        raise BakeoffError("role_outputs must be an object")
    if not isinstance(result["blockers"], list) or not isinstance(result["dissent_tags"], list):
        raise BakeoffError("blockers and dissent_tags must be lists")
    if not isinstance(result["policy_violations"], list):
        raise BakeoffError("policy_violations must be a list")
    if not isinstance(result["desktop"], dict) or not isinstance(result["usage"], dict):
        raise BakeoffError("desktop and usage must be objects")
    if not isinstance(result["provenance"], dict):
        raise BakeoffError("provenance must be an object")
    return True


def load_cases(path: Path) -> list[dict[str, Any]]:
    data = load_json(path)
    if not isinstance(data, list) or not data:
        raise BakeoffError("case file must contain a non-empty list")
    seen: set[str] = set()
    for case in data:
        if not isinstance(case, dict):
            raise BakeoffError("each case must be an object")
        validate_case(case)
        if case["case_id"] in seen:
            raise BakeoffError(f"duplicate case_id: {case['case_id']}")
        seen.add(case["case_id"])
    return data


def _set_prf(expected: list[str], actual: list[str]) -> tuple[float, float, float]:
    expected_set = set(expected)
    actual_set = set(actual)
    if not expected_set and not actual_set:
        return 1.0, 1.0, 1.0
    true_positive = len(expected_set & actual_set)
    precision = true_positive / len(actual_set) if actual_set else 0.0
    recall = true_positive / len(expected_set) if expected_set else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[\w-]+", text.casefold(), flags=re.UNICODE) if len(token) > 2}


def duplicate_content_ratio(role_outputs: dict[str, str]) -> float:
    values = [(role, _tokens(text)) for role, text in role_outputs.items() if str(text).strip()]
    if len(values) < 2:
        return 0.0
    similarities: list[float] = []
    for index, (_, left) in enumerate(values):
        for _, right in values[index + 1 :]:
            union = left | right
            similarities.append(len(left & right) / len(union) if union else 0.0)
    return sum(similarities) / len(similarities) if similarities else 0.0


def unique_contribution_score(role_outputs: dict[str, str]) -> float:
    values = [(role, _tokens(text)) for role, text in role_outputs.items() if str(text).strip()]
    if not values:
        return 0.0
    scores: list[float] = []
    for index, (_, current) in enumerate(values):
        others: set[str] = set()
        for other_index, (_, other) in enumerate(values):
            if other_index != index:
                others |= other
        scores.append(len(current - others) / len(current) if current else 0.0)
    return sum(scores) / len(scores)


def score_case(case: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    validate_case(case)
    validate_result(result)
    if case["case_id"] != result["case_id"]:
        raise BakeoffError("case/result id mismatch")

    participants = set(result["participants"])
    required_roles = set(case["required_roles"])
    forbidden_roles = set(case["forbidden_roles"])
    required_hit = len(required_roles & participants)
    routing_denominator = max(1, len(required_roles) + len(forbidden_roles & participants))
    routing_accuracy = required_hit / routing_denominator

    blocker_precision, blocker_recall, blocker_f1 = _set_prf(case["expected_blockers"], result["blockers"])
    _, dissent_recall, _ = _set_prf(case["required_dissent_tags"], result["dissent_tags"])

    live = result["mode"] == "LIVE_DECISION"
    decision_correct = None
    if live:
        decision_correct = result["final_decision"] == case["expected_decision"]

    desktop = result["desktop"]
    desktop_keys = (
        "task_completed",
        "verification_passed",
        "selector_recovered",
        "correct_execution_path",
        "no_unintended_action",
    )
    desktop_required = bool(case["desktop_required"])
    desktop_pass = None
    desktop_score = None
    if desktop_required:
        desktop_pass = all(desktop.get(key) is True for key in desktop_keys)
        desktop_score = 1.0 if desktop_pass else 0.0

    recovery_score = 1.0
    if case["injected_failure"]:
        recovery_score = 1.0 if result["failure_recovered"] is True else 0.0

    completion_score = 1.0 if result["status"] == "COMPLETED" else 0.0
    policy_score = 1.0 if not result["policy_violations"] else 0.0
    duplicate_ratio = duplicate_content_ratio(result["role_outputs"])
    contribution_score = unique_contribution_score(result["role_outputs"])

    return {
        "case_id": case["case_id"],
        "runtime_id": result["runtime_id"],
        "mode": result["mode"],
        "completion": completion_score,
        "decision_correct": decision_correct,
        "routing_accuracy": routing_accuracy,
        "blocker_precision": blocker_precision,
        "blocker_recall": blocker_recall,
        "blocker_f1": blocker_f1,
        "dissent_preservation": dissent_recall,
        "policy_compliance": policy_score,
        "failure_recovery": recovery_score,
        "desktop_required": desktop_required,
        "desktop_execution": desktop_score,
        "desktop_pass": desktop_pass,
        "unique_contribution": contribution_score,
        "duplicate_content_ratio": duplicate_ratio,
        "human_override": bool(result["human_override"]),
        "latency_ms": float(result["latency_ms"]),
        "input_tokens": int(result["usage"].get("input_tokens", 0)),
        "output_tokens": int(result["usage"].get("output_tokens", 0)),
        "cost_usd": float(result["usage"].get("cost_usd", 0.0)),
    }


def score_mechanics(receipt: dict[str, Any]) -> float:
    checks = (
        "framework_import",
        "isolated_roles",
        "parallel_first_positions",
        "fan_in",
        "failure_injection",
        "failure_recovery",
        "checkpoint_resume",
        "hitl_pause",
        "usage_capture",
        "trace_capture",
    )
    measured = [1.0 if receipt.get(key) is True else 0.0 for key in checks]
    return sum(measured) / len(measured)


def aggregate_runtime(
    runtime_id: str,
    case_scores: list[dict[str, Any]],
    mechanics_receipt: dict[str, Any] | None,
    cfg: dict[str, Any],
) -> dict[str, Any]:
    if not case_scores:
        raise BakeoffError(f"no case scores for runtime {runtime_id}")

    def avg(field: str) -> float | None:
        values = [float(score[field]) for score in case_scores if score.get(field) is not None]
        return sum(values) / len(values) if values else None

    live_scores = [score for score in case_scores if score["mode"] == "LIVE_DECISION"]
    decision_values = [1.0 if score["decision_correct"] else 0.0 for score in live_scores]

    mechanics_receipt = mechanics_receipt or {}
    mechanics = score_mechanics(mechanics_receipt)
    required_mechanics = cfg["required_mechanics_for_winner"]
    hard_mechanics_pass = all(mechanics_receipt.get(name) is True for name in required_mechanics)
    desktop_scores = [score for score in case_scores if score["desktop_required"]]
    desktop_required_count = len(desktop_scores)
    desktop_pass_count = sum(1 for score in desktop_scores if score["desktop_pass"] is True)
    desktop_execution = (
        desktop_pass_count / desktop_required_count if desktop_required_count else 0.0
    )

    metrics = {
        "decision_correctness": sum(decision_values) / len(decision_values) if decision_values else None,
        "blocker_f1": avg("blocker_f1"),
        "routing_accuracy": avg("routing_accuracy"),
        "dissent_preservation": avg("dissent_preservation"),
        "policy_compliance": avg("policy_compliance"),
        "runtime_native_recovery": 1.0 if mechanics_receipt.get("failure_recovery") is True else 0.0,
        "harness_recovery_diagnostic": avg("failure_recovery"),
        "desktop_execution": desktop_execution,
        "unique_contribution": avg("unique_contribution"),
        "non_duplication": 1.0 - avg("duplicate_content_ratio"),
        "completion": avg("completion"),
        "mechanics": mechanics,
    }

    weights = cfg["weights"]
    weighted = 0.0
    weight_used = 0.0
    for name, weight in weights.items():
        value = metrics.get(name)
        if value is None:
            continue
        weighted += float(weight) * float(value)
        weight_used += float(weight)
    normalized_score = weighted / weight_used if weight_used else 0.0

    live_count = len(live_scores)
    eligible = (
        live_count >= int(cfg["minimum_live_decision_cases"])
        and mechanics >= float(cfg["minimum_mechanics_score"])
        and hard_mechanics_pass
        and metrics["policy_compliance"] == 1.0
        and metrics["completion"] == 1.0
        and desktop_required_count == int(cfg["required_desktop_case_count"])
        and desktop_pass_count == desktop_required_count
        and metrics["desktop_execution"] >= float(cfg["minimum_desktop_execution_score"])
    )
    return {
        "runtime_id": runtime_id,
        "eligible_for_winner": eligible,
        "hard_mechanics_pass": hard_mechanics_pass,
        "live_decision_cases": live_count,
        "total_cases": len(case_scores),
        "mechanics_score": mechanics,
        "desktop_cases_total": desktop_required_count,
        "desktop_cases_passed": desktop_pass_count,
        "desktop_gate": {
            "required": desktop_required_count,
            "passed": desktop_pass_count,
            "pass": (
                desktop_required_count == int(cfg["required_desktop_case_count"])
                and desktop_pass_count == desktop_required_count
            ),
        },
        "score": normalized_score,
        "metrics": metrics,
        "latency_ms_total": sum(score["latency_ms"] for score in case_scores),
        "input_tokens_total": sum(score["input_tokens"] for score in case_scores),
        "output_tokens_total": sum(score["output_tokens"] for score in case_scores),
        "cost_usd_total": sum(score["cost_usd"] for score in case_scores),
    }


def select_winner(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    eligible = [summary for summary in summaries if summary["eligible_for_winner"]]
    if not eligible:
        return {
            "state": "NO_WINNER",
            "reason": "No runtime satisfied live-decision, mechanics, and policy gates.",
            "winner": None,
        }
    ranked = sorted(
        eligible,
        key=lambda item: (
            float(item["score"]),
            -float(item["cost_usd_total"]),
            -float(item["latency_ms_total"]),
        ),
        reverse=True,
    )
    return {"state": "WINNER_SELECTED", "winner": ranked[0]["runtime_id"], "reason": "All hard gates passed."}


def validate_live_provenance(
    results: list[dict[str, Any]],
    manifest: dict[str, Any],
    cfg: dict[str, Any],
) -> bool:
    if str(manifest.get("runner_id", "")).upper() != str(cfg.get("required_runner_id", "")).upper():
        raise BakeoffError("live manifest runner does not match required_runner_id")
    if float(manifest.get("financial_cost_usd", -1)) > float(cfg.get("maximum_cost_usd", 0)):
        raise BakeoffError("live manifest exceeds maximum_cost_usd")
    manifest_id = manifest.get("manifest_id")
    if not manifest_id:
        raise BakeoffError("live manifest_id is required")

    expected_cases = set(manifest.get("selected_case_ids", []))
    if not expected_cases:
        raise BakeoffError("live manifest selected_case_ids is empty")

    live_results = [result for result in results if result.get("mode") == "LIVE_DECISION"]
    for result in live_results:
        provenance = result.get("provenance")
        if not isinstance(provenance, dict):
            raise BakeoffError(f"{result.get('runtime_id')}/{result.get('case_id')}: live provenance is required")
        if provenance.get("manifest_id") != manifest_id:
            raise BakeoffError(f"{result.get('runtime_id')}/{result.get('case_id')}: stale or foreign manifest_id")
        for key in cfg["required_provenance_keys"]:
            if provenance.get(key) != manifest.get(key):
                raise BakeoffError(
                    f"{result.get('runtime_id')}/{result.get('case_id')}: provenance mismatch for {key}"
                )
        if provenance.get("runner_id") != cfg.get("required_runner_id"):
            raise BakeoffError(f"{result.get('runtime_id')}/{result.get('case_id')}: result was not produced on YASSIN")
        if float(result.get("usage", {}).get("cost_usd", -1)) > float(cfg.get("maximum_cost_usd", 0)):
            raise BakeoffError(f"{result.get('runtime_id')}/{result.get('case_id')}: non-zero cost result rejected")

    by_runtime: dict[str, list[str]] = defaultdict(list)
    for result in live_results:
        by_runtime[str(result["runtime_id"])].append(str(result["case_id"]))
    expected_runtimes = set(cfg["runtimes"])
    if set(by_runtime) != expected_runtimes:
        raise BakeoffError(
            f"live result runtimes {sorted(by_runtime)} do not match expected {sorted(expected_runtimes)}"
        )
    for runtime_id, case_ids in by_runtime.items():
        if len(case_ids) != len(set(case_ids)):
            raise BakeoffError(f"{runtime_id}: duplicate live case results")
        if set(case_ids) != expected_cases:
            raise BakeoffError(f"{runtime_id}: live result set does not match manifest selected_case_ids")
    return True


def evaluate(
    cases: list[dict[str, Any]],
    results: list[dict[str, Any]],
    mechanics: dict[str, dict[str, Any]],
    cfg: dict[str, Any],
    manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    validate_config(cfg)
    has_live = any(result.get("mode") == "LIVE_DECISION" for result in results)
    if has_live:
        if manifest is None:
            raise BakeoffError("LIVE_DECISION evaluation requires a YASSIN provenance manifest")
        validate_live_provenance(results, manifest, cfg)

    case_map = {case["case_id"]: case for case in cases}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for result in results:
        validate_result(result)
        case = case_map.get(result["case_id"])
        if case is None:
            raise BakeoffError(f"unknown case_id in result: {result['case_id']}")
        grouped[result["runtime_id"]].append(score_case(case, result))

    summaries = [
        aggregate_runtime(runtime_id, scores, mechanics.get(runtime_id), cfg)
        for runtime_id, scores in sorted(grouped.items())
    ]
    decision = select_winner(summaries)
    if manifest is not None and manifest.get("stage") != "full":
        decision = {
            "state": "NO_WINNER",
            "reason": (
                f"Stage {manifest.get('stage')} is a preflight stage; "
                "only a full YASSIN run may select a winner."
            ),
            "winner": None,
        }
    return {
        "schema_version": "1.0",
        "case_count": len(cases),
        "manifest_id": manifest.get("manifest_id") if manifest else None,
        "runtime_summaries": summaries,
        "decision": decision,
    }
