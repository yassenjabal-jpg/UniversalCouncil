# Agent Runtime Bake-off

Status: IMPLEMENTED HARNESS / MECHANICS PHASE IN PROGRESS

This benchmark compares the current Universal Council protocol baseline with candidate orchestration runtimes without allowing framework popularity to decide architecture.

## Hard honesty rule

A runtime cannot win from deterministic or mocked mechanics tests.

MECHANICS_ONLY proves framework wiring only. It never counts as decision correctness.

A winner requires at least the configured number of LIVE_DECISION historical cases, the mechanics threshold, and zero policy violations.

## Dataset

cases.json contains source-linked historical cases from the UniversalCouncil repository. Each case records the source artifact, governing question, expected decision label, role routing, blocker expectations, preserved dissent, desktop requirements and failure-injection requirements.

## Candidate runtimes

- baseline: current Council v0.3 protocol and deterministic repository controls.
- openai_agents: OpenAI Agents SDK pinned in the isolated bake-off environment.
- microsoft_agent_framework: Microsoft Agent Framework pinned in the isolated bake-off environment.

## Mechanics smoke

The smoke programs use deterministic local test doubles and do not call a model provider:
- smoke_openai_agents.py
- smoke_maf.py

They test isolated first positions, concurrency, fan-in, failure injection and bounded recovery. Unmeasured features remain false rather than being inferred from documentation.

## Live phase

The live phase must use the same case packet for every runtime. Results must record final decision, participants, role outputs, blockers, preserved dissent, policy violations, human override, recovery, desktop verification, latency, token usage and cost.

The evaluator intentionally returns NO_WINNER until the live-decision gate passes.
