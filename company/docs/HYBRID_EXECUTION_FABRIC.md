# Hybrid Execution Fabric — Prototype v0.1

Status: IMPLEMENTED_PROTOTYPE
Governance status: does not replace Council role governance.

## Purpose
Reduce latency, token use and fragile visual interaction by combining:
- Remote Desktop Commander / host control for filesystem, process, shell and deterministic machine operations;
- YASSIN Control Bridge for semantic Windows UI Automation and verified GUI interaction;
- shared resumable state;
- independent verification;
- routine graduation for repeated stable work.

The fabric is an execution substrate, not a Council member.

## Core rule
Use the least expensive reliable execution path:

1. native API or application-native automation;
2. DC control plane / deterministic shell and filesystem;
3. reusable routine;
4. semantic GUI / UI Automation;
5. visual assistance.

Raw coordinate control is not enabled in prototype v0.1.
## Separation of responsibilities

### Brain
Council/agent reasoning decides the goal and approved action intent.

### DC Control Plane
Preferred for:
- filesystem reads/writes;
- Git and repository inspection;
- process inspection;
- deterministic shell/script execution;
- logs and artifact verification.

The Python prototype emits a structured HOST_DISPATCH_REQUIRED request because Remote Desktop Commander is a host connector, not a local Python dependency.

### GUI Interaction Plane
Implemented through CouncilVideoStudio's verified YASSIN Control Bridge.

Used when:
- an application function has no safer native/DC path;
- state exists only in the application's UI;
- visual or semantic UI verification is necessary.

State-changing GUI work uses the existing verified-action path.

### Shared State
Task state can be persisted and restored as JSON.
Consumers can request a delta since a previous revision instead of replaying the whole history.
## Action risk tiers

- T0 Observe: read-only inspection.
- T1 Local reversible: navigation/focus and bounded reversible operation.
- T2 Local state change: requires post-state verification.
- T3 External consequential: requires approved task plus explicit Owner confirmation.
- T4 Separately governed/blocked: fails closed in the Hybrid Router.

The router does not create authority. It maps an action to existing Tool Authority operations.

## Single-controller rule
Only one state-changing GUI requester may hold the desktop control lease at a time.

Observers may remain logically separate, but the prototype prevents two GUI controllers from owning the same state object simultaneously.

This is intended to prevent:
- focus races;
- pointer/keyboard contention;
- interleaved actions;
- ambiguous audit ownership.
## Verification rule
A state-changing action is not successful merely because the provider returned without an error.

T2/T3 require verification.

If the action runs but the expected post-state cannot be verified, the result is:

UNKNOWN

UNKNOWN is never silently promoted to SUCCEEDED.

## Hybrid routing examples

A request that can be handled by both DC and GUI chooses DC first.

A request with a known native application automation path chooses the native path before DC.

A stable registered routine is preferred before GUI only when neither a native nor DC deterministic path is available.

GUI observation does not require a desktop control lease.
GUI control does.

## Routine graduation
A repeated workflow becomes eligible for routine extraction only after the configured number of verified successful repetitions with:
- no UNKNOWN result;
- no accidental action.

Default prototype threshold: 3 verified repetitions.
## Token/latency strategy
The fabric is designed to reduce model involvement through:
- plan-first local routing;
- shared-state deltas;
- deterministic DC execution where possible;
- batching deterministic actions outside model reasoning;
- GUI only for the slice that truly needs it;
- routine graduation.

Screenshots should not be the default state transport when semantic or machine-readable state is available.

## CLI
Plan only:

python tools/hybrid_execute.py action.json

Execute:

python tools/hybrid_execute.py action.json --execute --task-approved

External consequential actions additionally require:

--owner-confirmed

Persist/reuse state:

--state .runtime/hybrid/<task>.json

DC actions return HOST_DISPATCH_REQUIRED for the host connector.
GUI actions can execute locally through CouncilVideoStudio when the approved bridge is available.
## Prototype boundaries
This version does not:
- change Council role counts;
- grant new external publish/send authority;
- implement a local Remote Desktop Commander MCP client;
- support raw coordinate control;
- install an RPA suite;
- make native/routine adapters production-ready.

Those remain bake-off or later implementation slices.

## Acceptance conditions for next slice
Before expanding autonomy:
1. full repository tests and coverage gate pass;
2. real DC plan/handoff smoke passes;
3. real GUI observe smoke passes;
4. shared-state persistence passes;
5. controller lease conflict test passes;
6. state-changing test cannot report success without verification;
7. Tool Authority and Council Preflight remain valid.

## Related governing sources
- company/config/hybrid_execution.json
- company/config/tool_authority.json
- company/config/evidence_sync.json
- company/runtime/hybrid_execution.py
- company/tests/test_hybrid_execution.py
- CouncilVideoStudio/docs/YASSIN_CONTROL_BRIDGE.md
## Slice 2 — batching, projection and independent verification

Implemented after prototype v0.1 acceptance:

### Deterministic batching
- up to 6 configured deterministic steps;
- one controller lease across a GUI-control batch;
- immediate stop on any non-SUCCEEDED result;
- no controller lease for non-GUI-control batches.

### Compact result projection
Model-facing output is compact by default.

The projection keeps execution state, authority-relevant metadata, compact host requests, bounded verification results and operation-specific summaries. Raw provider stdout remains local unless explicitly needed.

For list_windows, the projection reduces the payload to:
- total item count;
- process-count summary;
- foreground process/class.

Live YASSIN measurement on 2026-10-12:
- raw: 13,062 bytes;
- projected: 3,026 bytes;
- reduction: 76.8%.

### Independent GUI post-state verifier
State-changing GUI actions may define a separate read-only verification request and expected fields.

The verifier performs a new GUI observation after the action. Provider success alone is insufficient.

A real reversible T2 Notepad test demonstrated:
- mismatched expected post-state -> UNKNOWN and batch stop;
- corrected exact post-state -> SUCCEEDED;
- two-step CHANGED -> ORIGINAL batch succeeded under one controller lease.

Evidence:
company/docs/evidence/HYBRID_EXECUTION_SLICE2_2026-10-12.md

