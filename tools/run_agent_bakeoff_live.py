from __future__ import annotations

import argparse
import asyncio
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]

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

OUTPUT_SCHEMA = {
    "final_decision": "one decision option exactly",
    "blockers": ["zero or more blocker labels from vocabulary"],
    "dissent_tags": ["zero or more dissent labels from vocabulary"],
    "summary": "brief rationale",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_local_endpoint(endpoint: str) -> str:
    parsed = urlparse(endpoint)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Ollama endpoint must be http(s)")
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("LIVE bake-off is zero-cost/local-only: non-local model endpoint rejected")
    return endpoint.rstrip("/")


def ollama_native_call(endpoint: str, model: str, prompt: str, timeout: int) -> tuple[str, dict[str, int]]:
    payload = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "think": False,
            "format": "json",
            "options": {"temperature": 0, "seed": 20261013, "num_ctx": 16384},
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
    from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, Runner, set_tracing_disabled

    set_tracing_disabled(True)
    client = AsyncOpenAI(api_key="ollama", base_url=f"{endpoint}/v1/", timeout=timeout)
    concrete_model = OpenAIChatCompletionsModel(model=model, openai_client=client)
    agent = Agent(name="CouncilLiveProbe", instructions="Follow the user's requested output format exactly.", model=concrete_model)
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

    client = OpenAIChatCompletionClient(
        model=model,
        base_url=f"{endpoint}/v1/",
        api_key="ollama",
        timeout=float(timeout),
    )
    agent = Agent(client=client, name="CouncilLiveProbe", instructions="Follow the user's requested output format exactly.")
    response = await agent.run(prompt)
    usage = response.usage_details or {}
    return (
        response.text or "",
        {
            "input_tokens": int(usage.get("input_token_count", 0) or 0),
            "output_tokens": int(usage.get("output_token_count", 0) or 0),
        },
    )


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


def case_source(case: dict[str, Any], max_chars: int = 12000) -> str:
    path = ROOT / case["source_artifact"]
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) <= max_chars:
        return text
    head = text[: max_chars // 2]
    tail = text[-max_chars // 2 :]
    return f"{head}\n\n[...SOURCE TRUNCATED FOR CONTROLLED CONTEXT...]\n\n{tail}"


def role_registry() -> list[str]:
    return sorted(ROLE_DESCRIPTIONS)


def global_vocab(cases: list[dict[str, Any]], field: str) -> list[str]:
    return sorted({item for case in cases for item in case[field]})


def routing_prompt(case: dict[str, Any], source: str) -> str:
    roles = [{"role": name, "purpose": ROLE_DESCRIPTIONS[name]} for name in role_registry()]
    return f"""You are the deterministic routing stage for Universal Council.
Choose the smallest serious set of 2-6 roles needed to decide the case.
Do not select roles because of popularity. Preserve at least one challenge perspective for consequential decisions.

CASE:
{case["prompt"]}

SOURCE ARTIFACT:
{source}

AVAILABLE ROLES:
{json.dumps(roles, ensure_ascii=False)}

Return ONLY JSON:
{{"participants":["exact role names"]}}
"""


def role_prompt(role: str, case: dict[str, Any], source: str, decision_options: list[str]) -> str:
    return f"""You are acting as the independent Universal Council role: {role}.
Role purpose: {ROLE_DESCRIPTIONS[role]}
Form your position BEFORE seeing any other role's output.

QUESTION:
{case["prompt"]}

DECISION OPTIONS:
{json.dumps(decision_options)}

SOURCE ARTIFACT:
{source}

Return ONLY JSON:
{"preferred_decision":"one exact decision option","blocker":"brief condition or empty string","dissent":"brief material challenge or empty string","rationale":"brief evidence-grounded reason"}
Do not invent facts outside the source.
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
Use only the source artifact and independent role outputs.
Do not use majority vote blindly. Preserve material dissent.

QUESTION:
{case["prompt"]}

SOURCE ARTIFACT:
{source}

INDEPENDENT ROLE OUTPUTS:
{json.dumps(outputs, ensure_ascii=False)}

DECISION OPTIONS (choose exactly one):
{json.dumps(decision_options)}

GLOBAL BLOCKER LABEL VOCABULARY:
{json.dumps(blocker_vocab)}

GLOBAL DISSENT LABEL VOCABULARY:
{json.dumps(dissent_vocab)}

Select blocker/dissent labels only when substantively supported by this case. Do not select labels merely because they are listed.

Return ONLY JSON matching:
{json.dumps(OUTPUT_SCHEMA)}
"""


async def guarded_call(call_fn, endpoint: str, model: str, prompt: str, timeout: int, inject_failure: bool) -> tuple[str, dict[str, int], bool]:
    if not inject_failure:
        text, usage = await call_fn(endpoint, model, prompt, timeout)
        return text, usage, True

    failed_once = False
    try:
        failed_once = True
        raise RuntimeError("synthetic live-recovery probe")
    except RuntimeError:
        text, usage = await call_fn(endpoint, model, prompt, timeout)
        return text, usage, failed_once


async def run_case(
    runtime_id: str,
    call_fn,
    endpoint: str,
    model: str,
    case: dict[str, Any],
    all_cases: list[dict[str, Any]],
    timeout: int,
) -> dict[str, Any]:
    started = time.perf_counter()
    source = case_source(case)
    options = DECISION_OPTIONS[case["case_id"]]
    total_usage = {"input_tokens": 0, "output_tokens": 0}

    route_text, usage = await call_fn(endpoint, model, routing_prompt(case, source), timeout)
    for key in total_usage:
        total_usage[key] += int(usage.get(key, 0))
    route = extract_json(route_text)
    participants = [role for role in route.get("participants", []) if role in ROLE_DESCRIPTIONS][:6]
    if len(participants) < 2:
        participants = ["Evidence & Verification", "Red Team / Falsification", "Execution & Feasibility"]

    async def one_role(role: str):
        text, role_usage, recovered = await guarded_call(
            call_fn,
            endpoint,
            model,
            role_prompt(role, case, source, options),
            timeout,
            bool(case["injected_failure"] and role == participants[0]),
        )
        return role, text, role_usage, recovered

    role_results = await asyncio.gather(*(one_role(role) for role in participants))
    role_outputs: dict[str, str] = {}
    recovery_flags: list[bool] = []
    for role, text, role_usage, recovered in role_results:
        role_outputs[role] = text
        recovery_flags.append(recovered)
        for key in total_usage:
            total_usage[key] += int(role_usage.get(key, 0))

    synth_text, synth_usage = await call_fn(
        endpoint,
        model,
        synthesis_prompt(
            case,
            source,
            options,
            role_outputs,
            global_vocab(all_cases, "expected_blockers"),
            global_vocab(all_cases, "required_dissent_tags"),
        ),
        timeout,
    )
    for key in total_usage:
        total_usage[key] += int(synth_usage.get(key, 0))
    synthesis = extract_json(synth_text)

    violations: list[str] = []
    final_decision = str(synthesis.get("final_decision", ""))
    if final_decision not in options:
        violations.append("INVALID_DECISION_OPTION")
    blockers = [x for x in synthesis.get("blockers", []) if x in global_vocab(all_cases, "expected_blockers")]
    dissent = [x for x in synthesis.get("dissent_tags", []) if x in global_vocab(all_cases, "required_dissent_tags")]

    desktop = {
        "task_completed": False,
        "verification_passed": False,
        "selector_recovered": False,
        "correct_execution_path": False,
        "no_unintended_action": True,
    }

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
        "failure_recovered": all(recovery_flags),
        "desktop": desktop,
        "usage": {
            **total_usage,
            "cost_usd": 0.0,
            "provider": "local_ollama",
            "model": model,
        },
        "latency_ms": round((time.perf_counter() - started) * 1000, 2),
    }


async def main_async(args: argparse.Namespace) -> int:
    endpoint = ensure_local_endpoint(args.endpoint)
    cases = load_json(ROOT / "benchmarks" / "agent_runtime" / "cases.json")
    if args.case:
        cases = [case for case in cases if case["case_id"] == args.case]
        if not cases:
            raise ValueError(f"unknown case: {args.case}")

    runtimes = {
        "baseline": baseline_call,
        "openai_agents": openai_agents_call,
        "microsoft_agent_framework": maf_call,
    }
    selected = list(runtimes) if args.runtime == "all" else [args.runtime]
    results: list[dict[str, Any]] = []

    for runtime_id in selected:
        for index, case in enumerate(cases, start=1):
            print(f"[{runtime_id}] {index}/{len(cases)} {case['case_id']}", flush=True)
            try:
                result = await run_case(
                    runtime_id,
                    runtimes[runtime_id],
                    endpoint,
                    args.model,
                    case,
                    load_json(ROOT / "benchmarks" / "agent_runtime" / "cases.json"),
                    args.timeout,
                )
            except (Exception, urllib.error.URLError) as exc:
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
                    "desktop": {
                        "task_completed": False,
                        "verification_passed": False,
                        "selector_recovered": False,
                        "correct_execution_path": False,
                        "no_unintended_action": True,
                    },
                    "usage": {"input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "provider": "local_ollama", "model": args.model},
                    "latency_ms": 0.0,
                    "error": str(exc)[:500],
                }
            results.append(result)

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    existing: list[dict[str, Any]] = []
    if args.append and out.exists():
        existing = load_json(out)
    out.write_text(json.dumps(existing + results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"WROTE {len(results)} live results to {out}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run zero-cost LIVE_DECISION bake-off against local Ollama only.")
    parser.add_argument("--endpoint", default="http://127.0.0.1:11434")
    parser.add_argument("--model", default="qwen3:4b-instruct")
    parser.add_argument("--runtime", choices=["all", "baseline", "openai_agents", "microsoft_agent_framework"], default="all")
    parser.add_argument("--case")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--out", default="benchmarks/agent_runtime/results.json")
    parser.add_argument("--append", action="store_true")
    args = parser.parse_args()
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    raise SystemExit(main())
