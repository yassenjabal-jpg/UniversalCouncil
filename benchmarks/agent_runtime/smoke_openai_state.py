from __future__ import annotations

import asyncio
import json
import threading
from typing import Any

from agents import Agent, RunConfig, Runner, RunState, set_trace_processors, set_tracing_disabled
from agents.decorators import tool
from agents.testing import ScriptedModel, assistant_message, function_call
from agents.tracing import Span, Trace, TracingProcessor


class LocalCollector(TracingProcessor):
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.traces: list[Trace] = []
        self.spans: list[Span[Any]] = []

    def on_trace_start(self, trace: Trace) -> None:
        with self.lock:
            self.traces.append(trace)

    def on_trace_end(self, trace: Trace) -> None:
        return None

    def on_span_start(self, span: Span[Any]) -> None:
        return None

    def on_span_end(self, span: Span[Any]) -> None:
        with self.lock:
            self.spans.append(span)

    def shutdown(self) -> None:
        return None

    def force_flush(self) -> None:
        return None


@tool(needs_approval=True)
async def guarded_action(value: str) -> str:
    """Return an approved synthetic value."""
    return f"approved:{value}"


async def main() -> None:
    collector = LocalCollector()
    set_trace_processors([collector])
    set_tracing_disabled(False)

    model = ScriptedModel(
        [
            [function_call("guarded_action", {"value": "council"}, call_id="call_approval")],
            [assistant_message("state-resume-complete")],
        ]
    )
    agent = Agent(name="StateProbe", model=model, tools=[guarded_action])

    first = await Runner.run(
        agent,
        "Use the guarded action.",
        run_config=RunConfig(trace_include_sensitive_data=False),
    )
    hitl_pause = len(first.interruptions) == 1

    checkpoint_resume = False
    final_output = None
    if hitl_pause:
        serialized = first.to_state().to_json()
        restored = await RunState.from_json(agent, serialized)
        restored_interruptions = restored.get_interruptions()
        if restored_interruptions:
            restored.approve(restored_interruptions[0])
            resumed = await Runner.run(
                agent,
                restored,
                run_config=RunConfig(trace_include_sensitive_data=False),
            )
            final_output = resumed.final_output
            checkpoint_resume = final_output == "state-resume-complete" and not resumed.interruptions

    model.assert_complete()
    exported_spans = [span.export() for span in collector.spans if span.export()]
    trace_capture = bool(collector.traces) and bool(exported_spans)

    receipt = {
        "checkpoint_resume": checkpoint_resume,
        "hitl_pause": hitl_pause,
        "trace_capture": trace_capture,
        "trace_count": len(collector.traces),
        "span_count": len(exported_spans),
        "final_output": final_output,
        "network_trace_export": False,
    }
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
