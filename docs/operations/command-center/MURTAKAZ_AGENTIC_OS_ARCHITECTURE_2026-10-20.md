# Murtakaz Agentic Work OS — Architecture Adoption
Date: 2026-10-20
Status: OWNER-ADOPTED / IMPLEMENTATION-GATED
Scope: UniversalCouncil Command Center only

## 1. Decision
Adopt the Agentic Work OS architecture derived from the reviewed reference video, but adapt it to the existing UniversalCouncil governance, execution, evidence and risk model.

This document does not copy the reference product UI or Obsidian-centered storage. It adopts the architectural ideas that materially strengthen the Command Center.

## 2. Governing product shape
The Command Center shall be built as one governed brain with multiple front doors.

Front doors:
- Windows desktop application.
- Android owner surface.
- Web owner surface where justified.
- Chat/ChatGPT adapter.
- Voice ingress/egress as a later optional provider.

No front door owns business logic, model choice, tool authority or project truth.

All requests pass through the same Murtakaz Command Gateway.

## 3. Canonical architecture

Front Doors
-> Murtakaz Command Gateway
-> Orchestration Core
-> Council / Single Agent / Deterministic Rule
-> Execution Fabric
-> Verification Core
-> Data Fabric

Cross-cutting registries:
- Skill Registry.
- Capability Registry.
- Model Broker.
- Job Engine.
- Automation Engine.
- Authority/Policy Engine.
- Evidence/Audit Ledger.

## 4. Murtakaz Command Gateway
The gateway is the only supported command ingress.

Required responsibilities:
1. authenticate principal/session;
2. normalize request;
3. resolve project and current checkpoint;
4. load a bounded immutable Context Capsule;
5. classify intent;
6. evaluate authority and risk;
7. select deterministic/no-AI vs single-agent vs Council path;
8. resolve Skill when available;
9. select model through Model Broker;
10. select execution route through Execution Fabric;
11. require approval when policy says so;
12. collect verification and evidence;
13. write immutable Work Receipt;
14. return result without fabricating success.

The gateway must fail closed on missing project context, missing authority, stale critical source pins or unresolved canonical conflicts.

## 5. Multi-stage routing
Routing is not one opaque LLM decision. It is a sequence of explicit typed decisions:

1. Intent Router.
2. Project/Context Router.
3. Authority & Risk Router.
4. Skill Router.
5. Reasoning Path Router: deterministic rule / single agent / Council.
6. Model Router.
7. Tool/Execution Router.
8. Verification Router.

Each stage records its reason and selected source/version in the Work Receipt.

The LLM may propose classifications, but policy and authority checks remain deterministic and machine-enforced.

## 6. Model Broker
A role is not a model.

Selection precedence:
Task Override -> Role Override -> Project Default -> Global Default.

Model choice shall consider:
- owner preference;
- required capability;
- context length;
- latency;
- cost ceiling;
- quality floor;
- availability;
- privacy/provider policy;
- explicit fallback policy.

Silent model fallback is forbidden.
A stronger model never gains additional authority.

## 7. Skill Backbone
Repeated work becomes a governed Skill, not an accumulating prompt convention.

Every Skill must define:
- id and version;
- purpose;
- typed inputs;
- typed outputs;
- allowed tools;
- model capability requirements;
- preconditions;
- ordered execution steps;
- postconditions;
- risk tier;
- authority requirements;
- verification steps;
- evidence requirements;
- rollback/failure policy;
- owner approval gate if applicable.

A Skill is not eligible for automation merely because it worked several times.

Graduation path:
Repeated Task
-> Candidate Procedure
-> Skill Contract
-> Tests
-> Shadow Runs
-> Verified Runs
-> Reliability Threshold
-> Automation Candidate
-> Authority Review
-> Automation.

Any skill that can publish, send, spend, delete, merge, alter permissions, expose private data or cause irreversible external state remains owner-gated unless separately governed.

## 8. Job Engine
Long work is a first-class Job, independent of an open chat session.

States:
QUEUED
-> PLANNING
-> WAITING_FOR_APPROVAL when applicable
-> EXECUTING
-> VERIFYING
-> SUCCEEDED / FAILED / UNKNOWN / BLOCKED.

Every Job records:
- project/checkpoint;
- immutable Context Capsule id;
- requested outcome;
- plan version;
- selected skill/model/providers;
- evidence;
- checkpoints;
- retries;
- return tickets;
- final Work Receipt.

Jobs may resume after process/app restart only from a verified checkpoint.

## 9. Capability Registry
The system must never rely on remembered capability availability.

Each provider/capability records:
- provider id;
- version/hash;
- health;
- authentication state;
- read/write/execute effect;
- supported operations;
- risk classification;
- latency/cost metadata;
- last verification timestamp;
- environment/host;
- fallback eligibility.

Examples:
GitHub, Drive, Browser, Windows UI Automation, Visual GUI, filesystem, shell, Photoshop, After Effects, Premiere, Desktop Commander, web research, model providers.

Unhealthy or expired capabilities are not silently treated as available.

## 10. Execution Fabric
Preserve the existing GUI-primary / DC-secondary hybrid policy.

For interactive desktop applications:
1. semantic UI automation;
2. visual GUI assistance;
3. bounded physical input;
4. DC only as explicit recovery/support fallback.

For external services:
native API/connector is preferred when it is stronger and safer.

Execution providers do not decide authority.
Provider success is not equivalent to task success.

## 11. Verification Core
Every material state change uses:
PRE-STATE -> ACTION -> POST-STATE -> INDEPENDENT VERIFICATION -> RECEIPT.

Result states:
SUCCEEDED
FAILED
UNKNOWN
BLOCKED.

UNKNOWN must never be rendered or stored as SUCCEEDED.

Verification strategy is typed by task:
- file/hash checks;
- UI state;
- build/test;
- screenshot/visual evidence;
- API readback;
- artifact existence;
- branch/SHA verification;
- domain-specific acceptance tests.

## 12. Project Data Fabric
Do not use one Markdown vault as the product database.

Use four logical stores:

### Structured State DB
projects, stages, roles, jobs, approvals, provider health, execution state, policy projections.

### Knowledge Store
governance, research, decisions, accepted project knowledge, searchable project memory.

### Artifact Store
images, videos, source files, builds, reports, design files, screenshots and generated assets.

### Immutable Event/Audit Ledger
who requested what, route decisions, model/tool selections, approvals, mutations, evidence and final outcomes.

Markdown may be an interchange/readable representation, not the only source of truth.

## 13. Project knowledge zones
Each project must distinguish:

SOURCE
- owner-provided or externally retrieved material.

CANONICAL
- explicitly accepted project truth.

WORKING
- temporary analysis, drafts and in-progress artifacts.

OUTPUT
- generated deliverables.

ARCHIVE
- superseded but retained history.

Critical rule:
No AI-generated OUTPUT or WORKING artifact may silently promote itself into CANONICAL.

Promotion requires an explicit gate with provenance.

## 14. Project Knowledge Map
Every project exposes a compact machine-readable entry point:

PROJECT_MANIFEST
CURRENT_STATE
CANONICAL_DECISIONS
ACTIVE_WORK
RELEVANT_SKILLS
RECENT_EVENTS
BLOCKERS
OWNER_DIRECTIVES.

The Context Resolver reads this map first, then retrieves only the minimum source material required for the task.

The default is bounded retrieval, not sending the full project history to every model call.

## 15. Operational HUD
The Home/Owner surfaces should expose truthful operational state, not decorative metrics:

- Murtakaz state.
- Council readiness.
- running workers/jobs.
- device connectivity.
- GUI bridge health.
- DC health.
- provider/model availability.
- approvals waiting.
- blockers/failures.
- active project/checkpoint.

No fabricated percentages, live agents or costs.

## 16. Android / remote owner model
Android is a command and supervision surface, not an independent brain.

It sends text/voice/actions to the Gateway and receives:
- results;
- job progress;
- approval requests;
- screenshots/artifacts;
- evidence links;
- alerts.

Execution remains on governed hosts/services.

## 17. Voice
Voice is providerized:
STT -> Gateway -> Murtakaz -> TTS.

Voice is not a foundation dependency and must not delay routing, skills, memory, jobs or authority work.

## 18. Knowledge graph
Graph visualization is optional and secondary.
It may visualize projects, decisions, skills, dependencies and evidence, but it is not itself the memory or authority layer.

## 19. Explicitly rejected reference-system choices
- Obsidian as the core product runtime.
- Markdown as the sole database.
- a single three-tier router as the complete routing model.
- automation purely after an arbitrary number of successful runs.
- embedding business logic in each UI/front door.
- allowing a model to choose and invoke arbitrary tools without policy enforcement.
- treating an attractive HUD as proof of runtime truth.

## 20. Integration with current Command Center
Existing components remain authoritative where stronger:
- Stage contracts and locks.
- Council/Studio dual review.
- role != model.
- no-silent-fallback.
- exact-head/SHA evidence.
- Hybrid Execution Fabric.
- Tool Authority.
- evidence receipts.
- UNKNOWN semantics.
- return tickets.

This architecture is an additive product-level control plane above them, not a rewrite of proven governance/execution controls.

## 21. Implementation ordering
Foundation order:
A. Anti-Drift Contract and architecture invariants.
B. Murtakaz Command Gateway.
C. Project Context Resolver + Context Capsule.
D. Multi-stage Router.
E. Capability Registry + Model Broker.
F. Skill Registry.
G. Job Engine.
H. Verification/Work Receipt integration.
I. Automation Engine.
J. front-door integrations and voice/graph extras.

No later step may bypass an earlier authority/truth contract.

## 22. Adoption status
Architecture: OWNER-ADOPTED.
Implementation: staged and review-gated.
Main-branch merge: prohibited until Council + Studio + required validation gates pass.
