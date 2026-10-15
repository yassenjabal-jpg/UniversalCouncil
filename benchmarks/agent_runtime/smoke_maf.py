from __future__ import annotations

import asyncio
import json
import time
from collections.abc import Awaitable
from typing import Any

from agent_framework import Agent, ChatResponse, Message
from agent_framework.orchestrations import ConcurrentBuilder


class ScriptedChatClient:
    def __init__(self, text: str, delay: float = 0.2, fail_once: bool = False) -> None:
        self.text = text
        self.delay = delay
        self.fail_once = fail_once
        self.call_count = 0
        self.additional_properties: dict[str, Any] = {}

    def get_response(
        self,
        messages,
        *,
        stream: bool = False,
        options: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Awaitable[ChatResponse]:
        if stream:
            raise NotImplementedError("streaming not required for smoke")

        async def _get() -> ChatResponse:
            self.call_count += 1
            await asyncio.sleep(self.delay)
            if self.fail_once and self.call_count == 1:
                raise RuntimeError("injected failure")
            return ChatResponse(
                messages=Message(role="assistant", contents=[self.text]),
                usage_details={
                    "input_token_count": 5,
                    "output_token_count": 3,
                    "total_token_count": 8,
                },
            )

        return _get()


async def run_concurrent(clients: list[ScriptedChatClient]):
    agents = [
        Agent(client=client, instructions=f"Independent first position {index}.", name=f"role-{index}")
        for index, client in enumerate(clients, start=1)
    ]
    workflow = ConcurrentBuilder(participants=agents).build()
    return await workflow.run("Evaluate independently before seeing peer outputs.")


async def main() -> None:
    clients = [
        ScriptedChatClient("Evidence position"),
        ScriptedChatClient("Red-team position"),
        ScriptedChatClient("Human-impact position"),
    ]
    started = time.perf_counter()
    events = await run_concurrent(clients)
    elapsed = time.perf_counter() - started
    outputs = events.get_outputs()

    parallel = elapsed < 0.45
    isolated = all(client.call_count == 1 for client in clients)
    fan_in = len(outputs) >= 1
    usage_client = ScriptedChatClient("usage probe", delay=0)
    usage_agent = Agent(client=usage_client, instructions="Return the probe.", name="usage-probe")
    usage_response = await usage_agent.run("measure usage")
    usage_capture = bool(
        usage_response.usage_details and int(usage_response.usage_details.get("total_token_count", 0) or 0) > 0
    )

    failure_injection = False
    try:
        await run_concurrent(
            [
                ScriptedChatClient("A"),
                ScriptedChatClient("B", fail_once=True),
                ScriptedChatClient("C"),
            ]
        )
    except RuntimeError:
        failure_injection = True

    recovered_events = await run_concurrent(
        [
            ScriptedChatClient("A recovered", delay=0),
            ScriptedChatClient("B recovered", delay=0),
            ScriptedChatClient("C recovered", delay=0),
        ]
    )
    failure_recovery = bool(recovered_events.get_outputs())

    receipt = {
        "framework_import": True,
        "isolated_roles": isolated,
        "parallel_first_positions": parallel,
        "fan_in": fan_in,
        "failure_injection": failure_injection,
        "failure_recovery": failure_recovery,
        "checkpoint_resume": False,
        "hitl_pause": False,
        "usage_capture": usage_capture,
        "trace_capture": False,
        "notes": {
            "elapsed_seconds": round(elapsed, 4),
            "live_model_used": False,
            "checkpoint_and_hitl_reserved_for_next_mechanics_slice": True,
        },
    }
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
