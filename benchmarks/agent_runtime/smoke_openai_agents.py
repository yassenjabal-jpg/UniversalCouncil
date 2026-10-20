from __future__ import annotations

import asyncio
import json
import time

from agents import Agent, RunConfig, Runner
from agents.testing import ModelStep, ScriptedModel, assistant_message


async def run_role(name: str, text: str, delay: float = 0.2) -> tuple[str, str, bool]:
    async def responder(_call):
        await asyncio.sleep(delay)
        return {"output": [assistant_message(text)]}

    model = ScriptedModel([ModelStep.respond(responder)])
    agent = Agent(name=name, model=model, instructions=f"Independent first position for {name}.")
    result = await Runner.run(
        agent,
        "Evaluate the case independently before seeing peers.",
        run_config=RunConfig(tracing_disabled=True),
    )
    model.assert_complete()
    usage_present = result.context_wrapper.usage is not None
    return name, str(result.final_output), usage_present


async def main() -> None:
    started = time.perf_counter()
    outputs = await asyncio.gather(
        run_role("Evidence", "Evidence position"),
        run_role("RedTeam", "Red-team position"),
        run_role("Human", "Human-impact position"),
    )
    elapsed = time.perf_counter() - started
    parallel = elapsed < 0.45
    isolated = len({text for _, text, _ in outputs}) == 3
    usage_capture = all(item[2] for item in outputs)

    failure_injection = False
    failing = ScriptedModel([ModelStep.raise_error(RuntimeError("injected failure"))])
    failing_agent = Agent(name="FailureProbe", model=failing)
    try:
        await Runner.run(
            failing_agent,
            "Trigger the injected failure.",
            run_config=RunConfig(tracing_disabled=True),
        )
    except RuntimeError:
        failure_injection = True

    recovery = ScriptedModel([[assistant_message("recovered")]])
    recovery_agent = Agent(name="RecoveryProbe", model=recovery)
    recovered = await Runner.run(
        recovery_agent,
        "Recover after failure.",
        run_config=RunConfig(tracing_disabled=True),
    )
    recovery.assert_complete()
    failure_recovery = recovered.final_output == "recovered"

    receipt = {
        "framework_import": True,
        "isolated_roles": isolated,
        "parallel_first_positions": parallel,
        "fan_in": len(outputs) == 3,
        "failure_injection": failure_injection,
        "failure_recovery": failure_recovery,
        "checkpoint_resume": False,
        "hitl_pause": False,
        "usage_capture": usage_capture,
        "trace_capture": False,
        "notes": {
            "elapsed_seconds": round(elapsed, 4),
            "tracing_disabled_for_deterministic_smoke": True,
            "live_model_used": False,
        },
    }
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
