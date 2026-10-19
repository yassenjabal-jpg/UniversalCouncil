# Command Center — Stage 3 Council & Studio Orchestration Contract
Date: 2026-10-19
Status: OPEN / OWNER-AUTHORIZED
Branch: command-center/stage3-orchestration
Parent product SHA: 448c5b7ce8bff6b9ec3875106922528036695b6c
Parent lock: COMMAND_CENTER_STAGE2_STATE_LOCK

## Mission

Turn the Council and Studio from static navigation destinations into a real, testable planning/orchestration layer while preserving the execution barrier.

Stage 3 provides:
- canonical role registry projection;
- deterministic Council activation/routing;
- Studio phase/department/gate projection;
- formal return-ticket contract;
- model-control policy;
- read-only Council Room and Studio Production Floor surfaces.

Stage 3 does **not** call an LLM, execute a tool, mutate GitHub, control Windows, or write Owner approvals.

## Canonical sources

The Stage 3 catalog must be generated from repository truth, not duplicated by hand.

Sources:
- config/roles.json
- company/config/council_role_contracts.json
- company/config/council_routing_candidate.json
- company/config/channel_operating_system.json
- company/config/media_venture.json

The generated catalog records the Git blob SHA for every source. CI regenerates the catalog and fails on drift.

## Role != Model

A role is:
Role Contract + Authority + Inputs + Outputs + Routing + Tools Policy.

A model is an interchangeable reasoning engine.

Rules:
1. roles may not embed a forced model;
2. model selection is Owner-controlled;
3. routing selects roles, never a hidden model;
4. silent fallback is forbidden;
5. a stronger model never gains additional authority;
6. Stage 3 has no connected model provider.

Selection precedence reserved for later provider integration:
Task Override -> Role Override -> Project Default -> Global Default.

## Council planning

Council planning is deterministic in Stage 3.

Minimum rules:
- chair is always activated for material decisions;
- domain specialists are activated only from explicit domain input;
- evidence activates for HIGH uncertainty or HIGH freshness;
- red team activates for MATERIAL+ materiality or MEDIUM+ uncertainty;
- risk activates for MEDIUM+ risk;
- human/execution/value functional roles activate only from explicit task flags;
- no free-text keyword authority routing;
- synthesis is a protocol stage, not a self-authorizing role.

Planning output is advisory/read-only and cannot dispatch execution.

## Studio planning

The Studio catalog must preserve:
- writing -> pre-production -> production sequence;
- Owner Title Lock;
- Script Lock;
- Production Ready Lock;
- one active craft department at a time;
- one primary program per stage;
- accepted handoff before next department;
- downstream direct repair forbidden;
- formal return ticket to source;
- Producer as control plane, not craft executor;
- Human Assistance as bounded/on-demand.

## Truthfulness

If there is no live task, the UI says:
NO LIVE TASK

It must not fabricate:
- active agents;
- current model calls;
- active craft departments;
- running jobs;
- costs;
- provider health;
- completion percentages.

## Security boundary

Stage 3 may read generated repository projections only.

Presentation may not:
- read governance files directly;
- call Python;
- call an LLM/provider;
- execute tools;
- change role authority;
- write routing/config;
- write approvals.

## Acceptance

Stage 3 locks only when:
1. catalog regeneration is deterministic and drift-checked;
2. source Git blob digests are recorded;
3. Council planner passes adversarial role/authority tests;
4. model policy rejects silent fallback;
5. malformed or authority-inflated catalogs fail closed;
6. Studio serial-production/return-ticket invariants are present;
7. Presentation stays behind Host/Application boundaries;
8. exact-head Windows CI passes;
9. exact-size UI evidence passes Studio review;
10. Council architecture/security/risk review passes.

Exit:
COMMAND_CENTER_STAGE3_ORCHESTRATION_LOCK
