from __future__ import annotations

import argparse
import asyncio
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]

from company.runtime.agent_bakeoff_baseline import route_v03  # noqa: E402
from company.runtime.agent_bakeoff_provenance import (  # noqa: E402
    ProvenanceError,
    build_manifest,
    result_provenance,
    validate_manifest,
    write_manifest,
)

DECISION_OPTIONS: dict[str, list[str]] = {
    "c01_restructure_v04": ["KEEP_V0_3", "ADOPT_V0_4_NOW", "PROVISIONAL_RESTRUCTURE_CANDIDATE"],
    "c02_gui_primary_hybrid": ["GUI_PRIMARY_DC_SECONDARY", "DC_PRIMARY_GUI_SECONDARY", "NATIVE_ONLY"],
    "c03_capability_evidence_sync": ["REJECT_EVIDENCE_SYNC", "ADOPT_BOUNDED_EVIDENCE_SYNC", "FULL_AUTHORITY_SYNC"],
    "c04_after_effects_runtime_status": ["UNVERIFIED", "VERIFIED_BOUNDED_RUNTIME_EVIDENCE", "FULL_PRODUCTION_CERTIFIED"],
    "c05_media_final_launch": ["NO_GO", "GO_WITH_CONDITIONS", "UNCONDITIONAL_GO"],
    "c06_channel_operating_system": ["REJECT_CHANNEL_OS", "GO_ADOPT_CHANNEL_OPERATING_SYSTEM", "DEFER_INDEFINITELY"],
    "c07_audio_sync_structure": ["KEEP_GENERIC_AUDIO", "ADOPT_MEDIA_PRODUCTION_CELL_V1_1", "OUTSOURCE_ALL_AUDIO"],
    "c08_youtube_studio_benchmark": ["REJECT", "ADOPT", "COPY_REFERENCE_STUDIOS"],
    "c09_work_environment_hardening": ["REJECT", "GO_FOR_SANDBOX_PILOT", "ADOPT_IMMEDIATELY"],
    "c10_intelligence_gateway": ["BLOCK_GATEWAY", "NATIVE_FIRST_PUBLIC_READ_ONLY_GATEWAY", "BROWSER_FIRST_WRITE_ENABLED_GATEWAY"],
    "c11_capability_scouting": ["NO_PROACTIVE_SCOUTING", "PROACTIVE_READ_ONLY_SCOUTING_OWNER_GATED_ADOPTION", "HR_FULL_INSTALL_AUTHORITY"],
    "c12_governance_hardening": ["REJECT_GOVERNANCE_HARDENING", "ACCEPT_GOVERNANCE_HARDENING", "REMOVE_OWNER_GATES"],
    "c13_memory_fabric": ["CHAT_MEMORY_CANONICAL", "IMPLEMENTED_GITHUB_CANONICAL_MEMORY", "UNVERSIONED_LOCAL_MEMORY"],
    "c14_specialized_tool_policy": ["CODE_FIRST_FOR_ALL_MEDIA", "SPECIALIZED_TOOL_FIRST_CODE_LAST_FOR_CRAFT", "NO_CODE_ALLOWED"],
    "c15_market_reality_gate": ["PROJECT_FIRST_REASONING_ALLOWED", "REQUIRE_MARKET_REALITY_BEFORE_PROJECT_CANDIDATE", "GLOBAL_MARKET_ONLY"],
    "c16_branch_hygiene": ["DELETE_OLD_BRANCHES_BY_AGE", "DELETE_ONLY_PROVEN_MERGED_OR_SUPERSEDED_BRANCHES", "DELETE_ALL_NON_MAIN"],
}

ROLE_DESCRIPTIONS = {
    "Evidence & Verification": "Verify source claims, provenance, freshness, and evidence boundaries.",
    "Red Team / Falsification": "Attack assumptions, seek failure modes, preserve serious dissent.",
    "Execution & Feasibility": "Judge implementability, operational constraints, recovery, and delivery risk.",
    "Risk & Assurance": "Check safety, security, governance, irreversible actions, and blocker conditions.",
    "Human & Adoption": "Assess user burden, usability, adoption, and human override needs.",
    "Value & Economics": "Assess cost, value, opportunity cost, and economic justification.",
    "Software & Systems": "Assess software architecture, runtime behavior, interfaces, and maintainability.",
    "Media & Content": "Assess production quality, creative workflow, audience fit, and media craft.",
    "Customer Skeptic": "Challenge whether the target customer truly needs, values, and will adopt the proposal.",
    "Business & Operations": "Assess operating model, process fit, execution ownership, and practical business constraints.",
}

TRANSIENT_ERROR_NAMES = {
    "TimeoutError",
    "APITimeoutError",
    "ReadTimeout",
    "ConnectTimeout",
    "ConnectionError",
    "APIConnectionError",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temp.replace(path)


def ensure_local_endpoint(endpoint: str) -> str:
    parsed = urlparse(endpoint)
    if parsed.scheme != "http":
        raise ValueError("YASSIN live bake-off requires local http Ollama")
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("YASSIN live bake-off rejects non-local model endpoints")
    return endpoint.rstrip("/")


def require_yassin_environment() -> None:
    detected = (os.environ.get("COMPUTERNAME") or "").strip().upper()
    if detected != "YASSIN":
        raise RuntimeError(f"LIVE bake-off is YASSIN-only; detected {detected or 'UNKNOWN'}")


def ollama_native_call(endpoint: str, model: str, prompt: str, timeout: int) -> tuple[str, dict[str, int]]:
    payload = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "think": False,
            "format": "json",
            "keep_alive": "30m",
            "options": {"temperature": 0, "seed": 20261013, "num_ctx": 12288},
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        f"{endpoint}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))
    return (
        str(data["message"]["content"]),
        {
            "input_tokens": int(data.get("prompt_eval_count", 0) or 0),
            "output_tokens": int(data.get("eval_count", 0) or 0),
        },
    )


async def baseline_call(endpoint: str, model: str, prompt: str, timeout: int) -> tuple[str, dict[str, int]]:
    return await asyncio.to_thread(ollama_native_call, endpoint, model, prompt, timeout)


async def openai_agents_call(endpoint: str, model: str, prompt: str, timeout: int) -> tuple[str, dict[str, int]]:
    from agents import Agent, AsyncOpenAI, ModelSettings, OpenAIChatCompletionsModel, RunConfig, Runner, set_tracing_disabled

    set_tracing_disabled(True)
    client = AsyncOpenAI(api_key="ollama", base_url=f"{endpoint}/v1/", timeout=timeout, max_retries=0)
    concrete_model = OpenAIChatCompletionsModel(model=model, openai_client=client)
    agent = Agent(
        name="CouncilLiveProbe",
        instructions="Follow the user's requested output format exactly.",
        model=concrete_model,
        model_settings=ModelSettings(temperature=0.0, extra_args={"seed": 20261013}),
    )
    result = await Runner.run(agent, prompt, run_config=RunConfig(tracing_disabled=True))
    usage = result.context_wrapper.usage
    return (
        str(result.final_output),
        {
            "input_tokens": int(getattr(usage, "input_tokens", 0) or 0),
            "output_tokens": int(getattr(usage, "output_tokens", 0) or 0),
        },
    )


async def maf_call(endpoint: str, model: str, prompt: str, timeout: int) -> tuple[str, dict[str, int]]:
    from agent_framework import Agent
    from agent_framework.openai import OpenAIChatCompletionClient

    del timeout
    client = OpenAIChatCompletionClient(model=model, base_url=f"{endpoint}/v1/", api_key="ollama")
    agent = Agent(
        client=client,
        name="CouncilLiveProbe",
        instructions="Follow the user's requested output format exactly.",
        default_options={"temperature": 0.0, "seed": 20261013},
    )
    response = await agent.run(prompt)
    usage = response.usage_details or {}
    return (
        response.text or "",
        {
            "input_tokens": int(usage.get("input_token_count", 0) or 0),
            "output_tokens": int(usage.get("output_token_count", 0) or 0),
        },
    )


def is_transient(exc: Exception) -> bool:
    return isinstance(exc, (TimeoutError, urllib.error.URLError)) or type(exc).__name__ in TRANSIENT_ERROR_NAMES


async def call_with_retry(call_fn, endpoint: str, model: str, prompt: str, timeout: int, retries: int = 2):
    attempt = 0
    while True:
        try:
            return await call_fn(endpoint, model, prompt, timeout)
        except Exception as exc:
            if not is_transient(exc) or attempt >= retries:
                raise
            attempt += 1
            await asyncio.sleep(min(2**attempt, 4))


def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        value = json.loads(text)
        if isinstance(value, dict):
            return value
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        value = json.loads(text[start : end + 1])
        if isinstance(value, dict):
            return value
    raise ValueError("model did not return a JSON object")


def packet_map() -> dict[str, dict[str, Any]]:
    path = ROOT / "benchmarks" / "agent_runtime" / "case_packets.json"
    if not path.is_file():
        raise RuntimeError("case_packets.json missing; build masked packets before LIVE execution")
    packets = load_json(path)
    return {packet["case_id"]: packet for packet in packets}


def global_vocab(cases: list[dict[str, Any]], field: str) -> list[str]:
    return sorted({item for case in cases for item in case[field]})


def routing_prompt(case: dict[str, Any], source: str) -> str:
    roles = [{"role": name, "purpose": purpose} for name, purpose in sorted(ROLE_DESCRIPTIONS.items())]
    return f"""You are the routing stage for Universal Council.
Choose the smallest serious set of 2-7 roles needed to decide the case.
Preserve at least one challenge perspective for a consequential decision.

CASE:
{case["prompt"]}

ANSWER-MASKED SOURCE PACKET:
{source}

AVAILABLE ROLES:
{json.dumps(roles, ensure_ascii=False)}

Return ONLY JSON:
{{"participants":["exact role names"]}}
"""


def role_prompt(role: str, case: dict[str, Any], source: str, decision_options: list[str]) -> str:
    return f"""You are acting as the independent Universal Council role: {role}.
Role purpose: {ROLE_DESCRIPTIONS[role]}
Form your position before seeing any other role output.

QUESTION:
{case["prompt"]}

DECISION OPTIONS:
{json.dumps(decision_options)}

ANSWER-MASKED SOURCE PACKET:
{source}

Return ONLY JSON:
{{"preferred_decision":"one exact decision option","blocker":"brief condition or empty string","dissent":"brief material challenge or empty string","rationale":"brief evidence-grounded reason"}}
"""


def synthesis_prompt(
    case: dict[str, Any],
    source: str,
    decision_options: list[str],
    outputs: dict[str, str],
    blocker_vocab: list[str],
    dissent_vocab: list[str],
) -> str:
    return f"""You are the Universal Council synthesis stage.
Use only the answer-masked source packet and independent role outputs.
Do not use majority vote blindly. Preserve material dissent.

QUESTION:
{case["prompt"]}

ANSWER-MASKED SOURCE PACKET:
{source}

INDEPENDENT ROLE OUTPUTS:
{json.dumps(outputs, ensure_ascii=False)}

DECISION OPTIONS:
{json.dumps(decision_options)}

BLOCKER LABEL VOCABULARY:
{json.dumps(blocker_vocab)}

DISSENT LABEL VOCABULARY:
{json.dumps(dissent_vocab)}

Return ONLY JSON:
{{"final_decision":"one exact decision option","blockers":[],"dissent_tags":[],"summary":"brief rationale"}}
"""


def baseline_prompt(
    case: dict[str, Any],
    source: str,
    participants: list[str],
    decision_options: list[str],
    blocker_vocab: list[str],
    dissent_vocab: list[str],
) -> str:
    return f"""You are executing Universal Council v0.3 in one structured model call.
The listed roles are governance perspectives, NOT independent agents. Consider each perspective sequentially,
preserve serious disagreement, then synthesize one decision.

QUESTION:
{case["prompt"]}

V0.3 ROUTED PERSPECTIVES:
{json.dumps(participants)}

ANSWER-MASKED SOURCE PACKET:
{source}

DECISION OPTIONS:
{json.dumps(decision_options)}

BLOCKER LABEL VOCABULARY:
{json.dumps(blocker_vocab)}

DISSENT LABEL VOCABULARY:
{json.dumps(dissent_vocab)}

Return ONLY JSON:
{{"role_positions":{{"exact role name":"brief independent-looking perspective"}},"final_decision":"one exact decision option","blockers":[],"dissent_tags":[],"summary":"brief rationale"}}
"""


def normalize_result_fields(
    *,
    runtime_id: str,
    case: dict[str, Any],
    participants: list[str],
    role_outputs: dict[str, str],
    synthesis: dict[str, Any],
    usage: dict[str, int],
    latency_ms: float,
    provenance: dict[str, Any],
    harness_recovered: bool,
) -> dict[str, Any]:
    options = DECISION_OPTIONS[case["case_id"]]
    violations: list[str] = []
    final_decision = str(synthesis.get("final_decision", ""))
    if final_decision not in options:
        violations.append("INVALID_DECISION_OPTION")

    all_cases = load_json(ROOT / "benchmarks" / "agent_runtime" / "cases.json")
    blocker_vocab = set(global_vocab(all_cases, "expected_blockers"))
    dissent_vocab = set(global_vocab(all_cases, "required_dissent_tags"))
    blockers = [item for item in synthesis.get("blockers", []) if item in blocker_vocab]
    dissent = [item for item in synthesis.get("dissent_tags", []) if item in dissent_vocab]

    return {
        "runtime_id": runtime_id,
        "case_id": case["case_id"],
        "mode": "LIVE_DECISION",
        "status": "COMPLETED" if not violations else "FAILED",
        "final_decision": final_decision,
        "participants": participants,
        "role_outputs": role_outputs,
        "blockers": blockers,
        "dissent_tags": dissent,
        "policy_violations": violations,
        "human_override": False,
        "failure_recovered": harness_recovered,
        "harness_recovered": harness_recovered,
        "desktop": {
            "task_completed": False,
            "verification_passed": False,
            "selector_recovered": False,
            "correct_execution_path": False,
            "no_unintended_action": True,
        },
        "usage": {
            **usage,
            "cost_usd": 0.0,
            "provider": "local_ollama",
        },
        "latency_ms": round(latency_ms, 2),
        "provenance": provenance,
    }


async def run_baseline_case(endpoint: str, model: str, case: dict[str, Any], source: str, timeout: int, provenance: dict[str, Any]):
    started = time.perf_counter()
    all_cases = load_json(ROOT / "benchmarks" / "agent_runtime" / "cases.json")
    participants = route_v03(ROOT, case["prompt"], source)
    prompt = baseline_prompt(
        case,
        source,
        participants,
        DECISION_OPTIONS[case["case_id"]],
        global_vocab(all_cases, "expected_blockers"),
        global_vocab(all_cases, "required_dissent_tags"),
    )
    text, usage = await call_with_retry(baseline_call, endpoint, model, prompt, timeout)
    synthesis = extract_json(text)
    raw_positions = synthesis.get("role_positions", {})
    role_outputs = {
        role: str(raw_positions.get(role, ""))
        for role in participants
    }
    return normalize_result_fields(
        runtime_id="baseline",
        case=case,
        participants=participants,
        role_outputs=role_outputs,
        synthesis=synthesis,
        usage=usage,
        latency_ms=(time.perf_counter() - started) * 1000,
        provenance=provenance,
        harness_recovered=True,
    )


async def run_candidate_case(
    runtime_id: str,
    call_fn,
    endpoint: str,
    model: str,
    case: dict[str, Any],
    source: str,
    timeout: int,
    provenance: dict[str, Any],
):
    started = time.perf_counter()
    all_cases = load_json(ROOT / "benchmarks" / "agent_runtime" / "cases.json")
    total_usage = {"input_tokens": 0, "output_tokens": 0}

    route_text, usage = await call_with_retry(call_fn, endpoint, model, routing_prompt(case, source), timeout)
    for key in total_usage:
        total_usage[key] += int(usage.get(key, 0))
    route = extract_json(route_text)
    participants = [role for role in route.get("participants", []) if role in ROLE_DESCRIPTIONS][:7]
    if len(participants) < 2:
        participants = ["Evidence & Verification", "Red Team / Falsification", "Execution & Feasibility"]

    async def one_role(role: str):
        text, role_usage = await call_with_retry(
            call_fn,
            endpoint,
            model,
            role_prompt(role, case, source, DECISION_OPTIONS[case["case_id"]]),
            timeout,
        )
        return role, text, role_usage

    role_results = await asyncio.gather(*(one_role(role) for role in participants))
    role_outputs: dict[str, str] = {}
    for role, text, role_usage in role_results:
        role_outputs[role] = text
        for key in total_usage:
            total_usage[key] += int(role_usage.get(key, 0))

    synth_text, synth_usage = await call_with_retry(
        call_fn,
        endpoint,
        model,
        synthesis_prompt(
            case,
            source,
            DECISION_OPTIONS[case["case_id"]],
            role_outputs,
            global_vocab(all_cases, "expected_blockers"),
            global_vocab(all_cases, "required_dissent_tags"),
        ),
        timeout,
    )
    for key in total_usage:
        total_usage[key] += int(synth_usage.get(key, 0))
    synthesis = extract_json(synth_text)

    return normalize_result_fields(
        runtime_id=runtime_id,
        case=case,
        participants=participants,
        role_outputs=role_outputs,
        synthesis=synthesis,
        usage=total_usage,
        latency_ms=(time.perf_counter() - started) * 1000,
        provenance=provenance,
        harness_recovered=True,
    )


def stage_case_ids(config: dict[str, Any], stage: str, all_case_ids: list[str]) -> list[str]:
    definition = config["live_stages"][stage]
    if definition == "ALL_16":
        return list(all_case_ids)
    return list(definition)


def load_existing(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    data = load_json(path)
    if not isinstance(data, list):
        raise ValueError("existing results file must be a list")
    return data


def completed_keys(results: list[dict[str, Any]], experiment_id: str) -> set[tuple[str, str]]:
    return {
        (str(item.get("runtime_id")), str(item.get("case_id")))
        for item in results
        if item.get("status") == "COMPLETED"
        and item.get("provenance", {}).get("experiment_id") == experiment_id
    }


async def warm_model(endpoint: str, model: str, timeout: int) -> None:
    await asyncio.to_thread(
        ollama_native_call,
        endpoint,
        model,
        'Return only {"status":"WARM"}.',
        timeout,
    )


async def main_async(args: argparse.Namespace) -> int:
    require_yassin_environment()
    endpoint = ensure_local_endpoint(args.endpoint)

    config = load_json(ROOT / "company" / "config" / "agent_bakeoff.json")
    cases = load_json(ROOT / "benchmarks" / "agent_runtime" / "cases.json")
    packets = packet_map()
    all_case_ids = [case["case_id"] for case in cases]
    selected_ids = stage_case_ids(config, args.stage, all_case_ids)
    selected_cases = [case for case in cases if case["case_id"] in selected_ids]
    if [case["case_id"] for case in selected_cases] != selected_ids:
        raise ValueError("stage case order does not match cases.json")

    await warm_model(endpoint, args.model, min(args.timeout, 120))

    manifest = build_manifest(
        ROOT,
        endpoint=endpoint,
        model=args.model,
        stage=args.stage,
        selected_case_ids=selected_ids,
    )
    manifest_path = ROOT / args.manifest
    write_manifest(manifest_path, manifest)
    validate_manifest(manifest, ROOT)
    provenance = result_provenance(manifest)

    runtimes = {
        "openai_agents": openai_agents_call,
        "microsoft_agent_framework": maf_call,
    }
    selected_runtimes = ["baseline", *runtimes] if args.runtime == "all" else [args.runtime]

    out = ROOT / args.out
    existing = load_existing(out) if args.resume else []
    done = completed_keys(existing, manifest["experiment_id"])
    results = list(existing)

    for runtime_id in selected_runtimes:
        for index, case in enumerate(selected_cases, start=1):
            key = (runtime_id, case["case_id"])
            if key in done:
                print(f"SKIP completed {runtime_id}:{case['case_id']}", flush=True)
                continue

            print(f"[{args.stage}] [{runtime_id}] {index}/{len(selected_cases)} {case['case_id']}", flush=True)
            source = str(packets[case["case_id"]]["model_context"])
            try:
                if runtime_id == "baseline":
                    result = await run_baseline_case(endpoint, args.model, case, source, args.timeout, provenance)
                else:
                    result = await run_candidate_case(
                        runtime_id,
                        runtimes[runtime_id],
                        endpoint,
                        args.model,
                        case,
                        source,
                        args.timeout,
                        provenance,
                    )
            except Exception as exc:
                result = {
                    "runtime_id": runtime_id,
                    "case_id": case["case_id"],
                    "mode": "LIVE_DECISION",
                    "status": "FAILED",
                    "final_decision": "",
                    "participants": [],
                    "role_outputs": {},
                    "blockers": [],
                    "dissent_tags": [],
                    "policy_violations": [f"RUNTIME_ERROR:{type(exc).__name__}"],
                    "human_override": False,
                    "failure_recovered": False,
                    "harness_recovered": False,
                    "desktop": {
                        "task_completed": False,
                        "verification_passed": False,
                        "selector_recovered": False,
                        "correct_execution_path": False,
                        "no_unintended_action": True,
                    },
                    "usage": {
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "cost_usd": 0.0,
                        "provider": "local_ollama",
                    },
                    "latency_ms": 0.0,
                    "provenance": provenance,
                    "error": str(exc)[:500],
                }

            results = [
                item for item in results
                if not (
                    item.get("runtime_id") == runtime_id
                    and item.get("case_id") == case["case_id"]
                    and item.get("provenance", {}).get("experiment_id") == manifest["experiment_id"]
                )
            ]
            results.append(result)
            atomic_write_json(out, results)

            if result["status"] != "COMPLETED":
                print(f"FAIL-CLOSED {runtime_id}:{case['case_id']} {result.get('error', result['policy_violations'])}")
                return 4

    print(json.dumps({
        "status": "STAGE_COMPLETE",
        "stage": args.stage,
        "experiment_id": manifest["experiment_id"],
        "results_file": str(out.relative_to(ROOT)),
        "cost_usd": 0.0,
    }, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run staged, resumable, YASSIN-only zero-cost LIVE_DECISION bake-off.")
    parser.add_argument("--endpoint", default="http://127.0.0.1:11434")
    parser.add_argument("--model", default="qwen3:4b-instruct")
    parser.add_argument("--stage", choices=["canary", "representative", "full"], default="canary")
    parser.add_argument("--runtime", choices=["all", "baseline", "openai_agents", "microsoft_agent_framework"], default="all")
    parser.add_argument("--timeout", type=int, default=150)
    parser.add_argument("--out", default="benchmarks/agent_runtime/results.json")
    parser.add_argument("--manifest", default="benchmarks/agent_runtime/experiment_manifest.json")
    parser.add_argument("--resume", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()
    try:
        return asyncio.run(main_async(args))
    except (ProvenanceError, RuntimeError, ValueError) as exc:
        print(f"LIVE_BAKEOFF_BLOCKED: {exc}")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
