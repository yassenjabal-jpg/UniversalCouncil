from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable
from typing import Any

from agent_framework import (
    Agent,
    ChatResponse,
    ChatResponseUpdate,
    Content,
    InMemoryCheckpointStorage,
    Message,
    ResponseStream,
    step,
    workflow,
)
from agent_framework.orchestrations import AgentRequestInfoResponse, SequentialBuilder
from agent_framework.observability import enable_instrumentation
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import set_tracer_provider


class ScriptedChatClient:
    def __init__(self, text: str) -> None:
        self.text = text
        self.call_count = 0
        self.additional_properties: dict[str, Any] = {}

    def get_response(
        self,
        messages,
        *,
        stream: bool = False,
        options: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Awaitable[ChatResponse] | ResponseStream[ChatResponseUpdate, ChatResponse]:
        if stream:

            async def _stream():
                self.call_count += 1
                yield ChatResponseUpdate(contents=[Content.from_text(self.text)], role="assistant")

            def _finalize(updates):
                return ChatResponse.from_updates(updates, output_format_type=(options or {}).get("response_format"))

            return ResponseStream(_stream(), finalizer=_finalize)

        async def _get() -> ChatResponse:
            self.call_count += 1
            return ChatResponse(messages=Message(role="assistant", contents=[self.text]))

        return _get()


checkpoint_storage = InMemoryCheckpointStorage()
fetch_calls = 0
transform_calls = 0


@step
async def fetch(value: str) -> str:
    global fetch_calls
    fetch_calls += 1
    return f"fetched:{value}"


@step
async def transform(value: str) -> str:
    global transform_calls
    transform_calls += 1
    return f"transformed:{value}"


@workflow
async def checkpoint_flow(value: str) -> str:
    first = await fetch(value)
    return await transform(first)


async def test_checkpoint() -> bool:
    instance = checkpoint_flow.build(checkpoint_storage=checkpoint_storage)
    first = await instance.run("council")
    if not first.get_outputs():
        return False
    before = (fetch_calls, transform_calls)
    latest = await checkpoint_storage.get_latest(workflow_name="checkpoint_flow")
    if latest is None:
        return False
    second = await instance.run(checkpoint_id=latest.checkpoint_id)
    after = (fetch_calls, transform_calls)
    return bool(second.get_outputs()) and before == after


async def test_hitl() -> bool:
    drafter_client = ScriptedChatClient("draft")
    editor_client = ScriptedChatClient("edited")
    drafter = Agent(client=drafter_client, name="drafter", instructions="Draft.")
    editor = Agent(client=editor_client, name="editor", instructions="Edit.")
    flow = SequentialBuilder(participants=[drafter, editor]).with_request_info(agents=["editor"]).build()

    request_id = None
    async for event in flow.run("synthetic document", stream=True):
        if event.type == "request_info":
            request_id = event.request_id
            break

    if not request_id:
        return False

    output_seen = False
    responses = {request_id: AgentRequestInfoResponse.approve()}
    async for event in flow.run(stream=True, responses=responses):
        if event.type == "output":
            output_seen = True
    return output_seen


async def main() -> None:
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    set_tracer_provider(provider)
    enable_instrumentation()

    checkpoint_resume = await test_checkpoint()
    hitl_pause = await test_hitl()
    spans = exporter.get_finished_spans()
    trace_capture = len(spans) > 0

    receipt = {
        "checkpoint_resume": checkpoint_resume,
        "hitl_pause": hitl_pause,
        "trace_capture": trace_capture,
        "span_count": len(spans),
        "network_trace_export": False,
    }
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
