# Universal Council Agent Runtime Bake-off — Phase 1 Mechanics

Date: 2026-10-13
Branch: experiment/agent-runtime-bakeoff-20261013
Base: origin/main@344bdb62f0bbaf621971177020f7026ca92399d2
Status: MECHANICS PASS / LIVE DECISION PHASE BLOCKED / NO WINNER

## Purpose

Implement the sandbox bake-off required by the 2026-10-12 Council restructuring arena without allowing framework popularity, mocked answers, or documentation claims to select a runtime.

The comparison candidates in Phase 1 are:
- current Universal Council v0.3 protocol baseline;
- OpenAI Agents SDK;
- Microsoft Agent Framework.

## Hard honesty boundary

Deterministic test doubles prove orchestration mechanics only. They do not prove model reasoning quality and do not count as LIVE_DECISION cases.

The evaluator requires at least 12 LIVE_DECISION historical cases, all required mechanics, and zero policy violations before any runtime can become a winner.

No model provider was available on YASSIN during this run:
- Ollama: not installed;
- OPENAI_API_KEY: absent;
- AZURE_OPENAI_API_KEY: absent;
- FOUNDRY_PROJECT_ENDPOINT / FOUNDRY_MODEL: absent.

No model was downloaded, no paid API was called, and no credential was created.

## Historical benchmark set

The harness contains 16 source-linked historical cases covering:
- Council v0.4 restructuring;
- GUI-primary hybrid execution;
- capability evidence sync;
- After Effects runtime evidence;
- media launch;
- channel operating system;
- audio-production role split;
- YouTube studio benchmark adoption;
- work-environment hardening;
- Intelligence Gateway;
- proactive capability scouting;
- governance hardening;
- Universal Memory Fabric;
- specialized media tool policy;
- Market Reality gate;
- branch hygiene.

Every source artifact must exist or repository validation fails.

## Measured mechanics

| Mechanic | v0.3 baseline | OpenAI Agents SDK | Microsoft Agent Framework |
| --- | --- | --- | --- |
| Framework/runtime import | PASS | PASS | PASS |
| Independent agent instances / isolated run state | NOT IMPLEMENTED | PASS | PASS |
| Parallel first positions | NOT IMPLEMENTED | PASS | PASS |
| Fan-in | NOT IMPLEMENTED | PASS | PASS |
| Failure injection | NOT IMPLEMENTED | PASS | PASS |
| Recovery after injected failure | NOT IMPLEMENTED | PASS | PASS |
| Checkpoint / serialized resume | NOT IMPLEMENTED | PASS | PASS |
| Human-in-the-loop pause | protocol-only | PASS | PASS |
| Usage capture | NOT IMPLEMENTED | PASS | PASS |
| Local trace capture | NOT IMPLEMENTED | PASS — 1 trace / 8 spans | PASS — 27 spans |

OpenAI mechanics used openai-agents 0.23.1 with the SDK's deterministic ScriptedModel testing surface. The approval probe serialized RunState, restored it, approved the pending guarded tool call, and resumed to the expected final output.

Microsoft mechanics used agent-framework-core 1.19.0 and agent-framework-orchestrations 1.3.1. The checkpoint probe restored stored step results without re-executing the saved steps. The HITL probe paused after a selected agent with with_request_info and resumed after an approval response. Tracing used an in-memory OpenTelemetry exporter only.

## Repository verification

Completed successfully:
- Python compile for the new bake-off runtime and smoke files;
- bake-off config/case validation;
- 10 dedicated bake-off unit tests;
- Universal Council invariant validator;
- full company test suite: 288 tests ran successfully; test runner reported OK with 1 skipped.

Expected negative-path memory error strings appeared during the full suite, but the suite exited successfully; these are assertions of fail-closed behavior, not failures.

## Current decision

NO_WINNER.

Reason:
- both candidate runtimes pass the mechanics gate;
- neither has executed the required LIVE_DECISION case set;
- the current baseline is retained as governance/runtime fallback until a candidate wins with measured decision evidence;
- v0.4 remains a candidate and is not promoted to governing structure by Phase 1.

## Next gate

Run the same 12–20 historical cases through:
1. current protocol baseline;
2. OpenAI Agents SDK;
3. Microsoft Agent Framework;

using the same model or otherwise controlled provider conditions, and record:
- final decision correctness against source-linked historical outcomes;
- blockers;
- routing;
- dissent preservation;
- unique contribution and duplication;
- policy violations;
- desktop task completion and verification;
- recovery;
- latency;
- tokens and cost.

No live phase should start merely by discovering a paid credential. Provider choice and spend must remain explicit and bounded.
