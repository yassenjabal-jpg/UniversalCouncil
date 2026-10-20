# المرتكز — Agentic Work OS Integration Contract
Date: 2026-10-21
Status: OWNER-DIRECTED / MURTAKAZ PRE-APPROVED / IMPLEMENTATION-GATED
Project: UniversalCouncil Command Center + Android Owner Companion
Canonical base at implementation start: `1702d73eafa2319200164898bdaf0d400d4af524`

## 1. Purpose

This contract adopts the useful architecture extracted from the reviewed Agentic OS reference while preserving the stronger project-local governance already implemented by المرتكز.

It supersedes the unaligned draft architecture introduced in PR #54. The ideas are retained; the stale baseline and duplicated authority are not.

## 2. Highest governing law

Current product governance is:

- **المرتكز** = project-local governing system.
- **هيئة المرتكز** = truth, architecture, security, durability, model/memory/evals and risk review.
- **مشغل المرتكز** = UX, interaction, visual, motion, Windows/Android presentation, accessibility and fidelity.
- Owner remains final authority.
- No material change is adopted, completed, merged, released or used to open a later stage without explicit recorded Murtakaz approval.
- Live execution remains locked.
- Stage 8 remains unopened.

The parent Universal Council and original Media Studio are not replaced or mutated.

## 3. One brain, many front doors

The product has one logical governing brain and multiple clients:

```
Windows ─┐
Android ─┤
Web ─────┤
Chat ────┼─> Murtakaz Command Gateway
Voice ───┘
```

Front doors are presentation/transport surfaces only. They do not own:
- business rules;
- authority;
- model policy;
- project truth;
- execution permissions;
- canonical memory.

Android is a control/supervision surface, not an authority host.

## 4. Gateway is a boundary, not a God Object

The Murtakaz Command Gateway is the logical ingress and coherence boundary.

It owns only:
- principal/session handoff;
- request normalization;
- project-selection guard;
- correlation/request identity;
- orchestration entry;
- result projection.

It delegates to bounded application services:

```
Murtakaz Command Gateway
├─ ContextResolver
├─ AuthorityPolicyService
├─ RoutingCoordinator
├─ SkillResolver
├─ ModelBroker
├─ JobService
├─ ExecutionFabric
├─ VerificationService
└─ ReceiptService
```

No single Gateway class/service should accumulate authentication, retrieval, planning, routing, execution, persistence and verification logic.

Preferred boundary:

`Front Door -> Gateway/Application Facade -> Application Services -> Execution/Data Providers`

## 5. Remote Owner integration

Existing Remote Owner protections are preserved:
- OWNER/device/session identity;
- nonce;
- idempotency;
- issued/expiry time;
- bounded targets/effects;
- replay protection;
- revocation.

Remote Owner, Android, Web, Chat and future Voice are adapters into the same logical Murtakaz authority pipeline.

“One logical gateway” does not require one network process. It requires one consistent authority decision path.

## 6. Mandatory Murtakaz change cycle

Every material product change follows:

```
PROPOSED
-> MURTAKAZ_PRE_REVIEW
-> APPROVE_TO_IMPLEMENT
-> CONTEXT_CAPSULE
-> TYPED_PLAN / CHANGE_ENVELOPE
-> IMPLEMENT
-> VERIFY
-> MURTAKAZ_POST_REVIEW
-> APPROVED_BY_AL_MURTAKAZ
```

Pre-approval authorizes implementation only.

It does not authorize:
- adoption;
- merge;
- release;
- stage transition;
- execution authority.

Any material post-approval mutation reopens review.

## 7. Context Capsule

Each material Job/change receives an immutable Context Capsule.

It binds:
- project;
- exact source revision;
- current checkpoint/lock;
- typed Owner directives;
- canonical source hashes/versions;
- domain-specific precedence;
- allowed scope;
- forbidden scope;
- required skill/version;
- authority policy version;
- risk class;
- expected outputs;
- acceptance tests;
- freshness rules;
- visual parent binding when applicable.

A capsule never mutates in place.

If truth changes during work:
- produce `STALE_CONTEXT`;
- issue a new capsule;
- re-plan.

If canonical sources conflict:
- produce `CONTEXT_CONFLICT`;
- stop;
- resolve explicitly.

## 8. Source authority and prompt-injection boundary

All retrieved text is data by default.

Content from:
- web;
- GitHub;
- files;
- connectors;
- project artifacts;
- model output;
- tool output

cannot grant authority merely because it contains instructions.

Only typed governing records with authority metadata may govern execution.

Rules:
- retrieved text cannot grant permission;
- tool output cannot rewrite policy;
- model output cannot self-promote to canonical;
- instructions and evidence/data are represented separately;
- external content is treated as untrusted until classified.

## 9. Owner directives and Change-of-Truth

Owner remains final authority, but material directives are normalized into typed records.

A material directive records:
- id;
- scope;
- date;
- affected artifacts;
- status;
- supersedes chain;
- whether it changes locked truth.

Chat text does not silently overwrite a lock.

If a directive intentionally changes:
- visual reference;
- authority;
- security policy;
- canonical architecture;
- model/fallback semantics;
- durable data semantics;

it passes a Change-of-Truth gate and creates a new canonical version.

History is superseded, not rewritten.

## 10. Multi-stage routing

Routing is not one opaque AI choice.

Logical stages:

1. Intent.
2. Project/Context.
3. Authority/Risk.
4. Skill.
5. Reasoning Path.
6. Model.
7. Execution.
8. Verification.

The LLM may propose a classification.

Deterministic policy decides whether that proposal is authorized.

Every material Work Receipt records route decisions and reasons.

## 11. Reasoning path

The system may choose:
- deterministic/no-AI rule;
- single role/agent reasoning;
- Murtakaz governance review;
- Murtakaz Arena for authority/security/durability/high-risk work.

A more capable model never gains more authority.

## 12. Model Broker

Role != Model remains absolute.

Selection order:
`Task Override -> Role Override -> Project Default -> Global Default`

Selection considers:
- Owner preference;
- capability;
- context;
- latency;
- cost;
- quality floor;
- availability;
- privacy;
- explicit fallback policy.

Silent fallback is forbidden.

Unsupported reasoning/model levels are shown truthfully rather than silently downgraded.

## 13. Skill Registry

Material repeated work becomes a governed Skill, not a remembered prompt pattern.

A Skill defines:
- id/version;
- purpose;
- typed inputs/outputs;
- tools;
- model capability;
- preconditions;
- ordered steps;
- postconditions;
- risk;
- authority;
- verification;
- evidence;
- rollback/failure policy;
- approval gate.

Graduation:

`Repeated Task -> Candidate Procedure -> Skill Contract -> Tests -> Shadow Runs -> Verified Runs -> Reliability Threshold -> Automation Candidate -> Authority Review -> Automation`

A run count alone never authorizes automation.

## 14. Automation

Actions such as:
- publish;
- send;
- spend;
- delete;
- merge;
- permission changes;
- private-data exposure;
- irreversible external effects

remain Owner-gated or separately governed.

Scheduled/event triggers do not bypass normal authority.

A trigger creates a normal request entering the same gateway/policy path.

## 15. Job Engine

Long work becomes a first-class durable Job.

Unified states:

```
QUEUED
PLANNING
WAITING_FOR_APPROVAL
EXECUTING
VERIFYING
BLOCKED
FAILED
UNKNOWN
STALE_CONTEXT
CONTEXT_CONFLICT
SUCCEEDED
```

`UNKNOWN != SUCCEEDED`.

`STALE_CONTEXT` requires a new capsule/re-plan.

`CONTEXT_CONFLICT` requires explicit truth resolution.

Real durable Job execution remains future implementation; the contract exists now so UI and later runtime cannot invent incompatible semantics.

## 16. Capability Registry

Capability health is per operation, not a single provider green light.

Record:
- provider;
- operation;
- version/hash;
- health;
- auth state;
- effect READ/WRITE/EXECUTE;
- risk;
- latency/cost;
- verified timestamp;
- TTL/freshness;
- host/environment;
- evidence level;
- fallback eligibility;
- failure reason.

A provider may be healthy for read and blocked for execute.

## 17. Execution Fabric

Existing Hybrid Execution policy remains authoritative.

Interactive desktop:
1. semantic UI Automation;
2. visual GUI assistance;
3. explicitly bounded physical input;
4. DC only as approved support/recovery fallback.

External services:
prefer native connector/API when stronger and safer.

Execution providers never decide authority.

Provider success is not task success.

## 18. Verification Core

Material state change:

`PRE-STATE -> ACTION -> POST-STATE -> INDEPENDENT VERIFICATION -> RECEIPT`

Verification may use:
- file/hash;
- UI state;
- build/test;
- screenshots;
- API readback;
- artifact existence;
- branch/SHA;
- domain acceptance.

A success claim without sufficient evidence becomes UNKNOWN/FAILED/BLOCKED according to the failure class.

## 19. Project knowledge zones

Each project distinguishes:

- SOURCE
- CANONICAL
- WORKING
- OUTPUT
- ARCHIVE

WORKING and OUTPUT never silently promote to CANONICAL.

Promotion requires:
- provenance;
- review;
- explicit acceptance gate.

## 20. Project Knowledge Map

Every project should expose a compact machine-readable entry:

- PROJECT_MANIFEST
- CURRENT_STATE
- CANONICAL_DECISIONS
- ACTIVE_WORK
- RELEVANT_SKILLS
- RECENT_EVENTS
- BLOCKERS
- OWNER_DIRECTIVES

Context Resolver reads this first, then retrieves the minimum required canonical context.

It does not dump all conversation/project history into every model call.

## 21. Visual direction — inheritance, not replacement

The Agentic OS architecture creates **no new visual system**.

The only visual source of truth remains the eight pinned canonical reference images.

Agentic UI concepts must fit the existing system.

Existing stronger controls remain supreme:
- `18_REFERENCE_ONLY_VISUAL_LOCK.md`
- `23_VISUAL_PRODUCTION_HARD_GATE.md`
- reference manifest;
- actual reference bytes;
- hash verification;
- preflight registration;
- reference-binding receipt;
- one-screen law;
- object inventory;
- generated-image quarantine;
- side-by-side comparison;
- governance + workshop review.

A generic “Visual Context Capsule” is only a wrapper around those existing controls. It may never weaken them.

## 22. Owner experience

Internal architecture must not dominate the product.

Owner mental model remains:

`START -> UNDERSTAND -> DECIDE -> WORK -> VERIFY`

Primary surfaces:
- Command Composer;
- Active Work;
- Decision Stack;
- Project Workspace;
- Work Receipt.

Routing stages, model/provider internals and capability details use progressive disclosure under System/Evidence/Ask This.

The Operational HUD is secondary and truthful, not the Home page’s primary concept.

## 23. Approval fatigue

Anti-drift must not turn into constant interruption.

Policy distinguishes:
- safe deterministic transitions within granted authority;
- material change;
- Change-of-Truth;
- external consequential effect;
- destructive/irreversible effect.

Only the latter classes demand Owner interruption when policy says so.

Decision Stack and Quiet Mode remain the preferred UX.

## 24. Cross-platform truth

Windows and Android may differ in layout.

They must agree on:
- project state;
- checkpoint;
- approval;
- artifact/version;
- truth state;
- Job result.

Critical mobile actions should use typed semantic commands and be re-authorized server-side.

## 25. Data Fabric

Logical stores:
1. Structured State DB.
2. Knowledge Store.
3. Artifact Store.
4. Audit/Event Ledger.

Before real Autopilot, define:
- stable IDs;
- schema versions;
- event ordering;
- idempotent writes;
- transaction/outbox or equivalent;
- partial-write recovery;
- backup/restore;
- incarnation binding.

Markdown is a readable/interchange form, not the sole product database.

## 26. Audit privacy

Traceability does not justify permanent secret storage.

Before live audit runtime:
- redact before append;
- classify privacy;
- prefer references over raw sensitive payload;
- never persist passwords/tokens in immutable ledger;
- define retention and secure lifecycle for referenced artifacts.

## 27. Independent review

High-risk/high-drift work cannot self-approve.

Use:
- separate reviewer context;
- deterministic validators where possible;
- Murtakaz governance + workshop as applicable.

A different model alone is not proof of reviewer independence.

## 28. Architecture invariants

Invariants are scoped by applicability.

Each rule declares:
- when it starts applying;
- change classes;
- enforcement type;
- implementation state;
- validator.

This avoids two bad outcomes:
- pretending future runtime exists merely to pass CI;
- failing all current work because future capability contracts are not yet implemented.

Truth/authority rules applicable now remain blocking now.

## 29. Delivery order

Recommended implementation sequence:

A. Governance/Anti-Drift contracts — current change.
B. Context Resolver + Context Capsule compiler.
C. Logical Gateway facade and service interfaces.
D. Routing Coordinator.
E. Capability Registry + Model Broker.
F. Skill Registry.
G. durable Project Store contract.
H. Job Engine + Flight Recorder/Tool Effect Ledger.
I. Verification + Work Receipt integration.
J. Automation/Trigger Engine.
K. Android/Web/Chat adapters.
L. optional Voice and graph visualization.

Each step is a bounded vertical slice with pre/post Murtakaz review.

## 30. Current truth after this contract

This contract does NOT claim:
- live execution;
- real durable Autopilot;
- connected Android;
- connected model providers;
- working Job Engine;
- Stage 8.

It defines the architecture those capabilities must obey when implemented.
