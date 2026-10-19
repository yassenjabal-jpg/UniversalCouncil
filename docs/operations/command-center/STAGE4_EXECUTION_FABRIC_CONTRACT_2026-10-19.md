# Command Center — Stage 4 YASSIN Execution Service & Provider Fabric Contract
Date: 2026-10-19
Status: OPEN / OWNER-AUTHORIZED
Branch: command-center/stage4-execution-fabric
Parent product SHA: 2073b0ff5800156e6d908efc43493715c83f22bc
Parent lock: COMMAND_CENTER_STAGE3_ORCHESTRATION_LOCK

## Mission

Build the execution boundary as a real local service and provider fabric without granting live execution authority.

Stage 4 creates:
- execution manifest contracts;
- provider registry projection;
- YASSIN target identity contract;
- controller-lease abstraction;
- append-only execution journal abstraction;
- postcondition/receipt contract;
- standalone Execution Service executable;
- SAFE/DISABLED service mode;
- read-only Execution Fabric surface in Command Center.

## Live-execution rule

Stage 4 is not permission to control YASSIN.

Live dispatch remains disabled while any Phase 0 gate is not PASS.

Pinned Phase 0 evidence:
- branch: phase0/feasibility-adversarial-prototype
- head: 63a4a446bc1e87f5352915f1e86c463de82e9b81
- status blob: 454f07f73a631627eae2eff2f8c229c8eb270ee1

Current gates:
- G0-A IN_TEST
- G0-B BLOCKED_BY_PROVIDER_LIMIT
- G0-C IN_TEST
- G0-D IN_TEST

Therefore:
LIVE_EXECUTION_AUTHORIZED = false

## Provider strategy

Desktop Commander is not the permanent execution backbone.

It remains a legacy/reference provider only.

Preferred long-term hierarchy:
1. native host tooling;
2. semantic UI Automation;
3. app-native API/script/COM;
4. visual grounding;
5. bounded physical input;
6. legacy DC path only when explicitly authorized and available.

A provider being installed or historically observed does not make it active.

## Service commands allowed in Stage 4

The standalone service may expose:
- status
- validate-manifest
- inspect-provider-registry
- validate-receipt

It must not expose:
- execute
- run-shell
- click
- type
- invoke-provider
- send-model-request

## Execution manifest

Required:
- manifest_id
- task_id
- requester
- target_host
- authority_operation
- action_kind
- effect
- risk_tier
- expected_postcondition
- verification_method
- approval_ref
- expires_at
- idempotency_key

Rules:
- target_host must equal YASSIN for this product stage;
- requester must be explicit;
- approval_ref may be informational but is never sufficient to enable dispatch;
- effect/risk cannot be caller-downgraded;
- expiration must be explicit;
- no secret/credential payloads;
- manifest validation never means execution approval.

## Receipt states

Allowed:
- PLANNED
- VALIDATED
- BLOCKED
- UNKNOWN
- FAILED
- POSTCONDITION_VERIFIED

Stage 4 service may produce VALIDATED or BLOCKED for synthetic validation.

It may not claim POSTCONDITION_VERIFIED from a provider because no provider dispatch exists.

UNKNOWN != SUCCESS.

## Lease and journal

Controller lease:
- one controller per host resource;
- fencing token required;
- stale holder cannot release current lease;
- bounded TTL;
- no silent takeover of a live lease.

Execution journal:
- append-only intent/result records;
- unresolved intent remains pending;
- UNKNOWN remains pending until reconciliation;
- no replay by default.

## Architecture boundary

Presentation -> Host -> Application -> Infrastructure -> Execution Fabric projections/local primitives

ExecutionService is a separate executable.

Presentation must never:
- start processes;
- dispatch providers;
- open sockets;
- read credentials;
- acquire controller lease;
- write journal;
- perform GUI actions.

## Acceptance

Stage 4 locks only when:
1. live dispatch is structurally disabled;
2. Phase 0 gate projection is pinned and visible;
3. provider registry is generated from canonical repository policy;
4. DC is classified legacy/reference, not mandatory backbone;
5. manifest validation is fail-closed;
6. lease/journal synthetic tests pass;
7. UNKNOWN cannot become success;
8. no execute command exists in the service CLI;
9. Stage 2 + Stage 3 regression suites pass;
10. exact-head Windows CI passes;
11. CodeQL passes;
12. UI evidence passes Council/Studio review.

Exit:
COMMAND_CENTER_STAGE4_EXECUTION_FABRIC_LOCK
