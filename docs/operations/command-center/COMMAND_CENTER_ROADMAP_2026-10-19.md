# UniversalCouncil Command Center — Product Roadmap
Date: 2026-10-19
Last reconciled: 2026-10-21
Status: ACTIVE / OWNER-AUTHORIZED / GOVERNANCE-METADATA-RECONCILED
Development method: RevenueSystem 2.0-inspired gated vertical delivery

Authoritative delivery-state note:
- The PHASE 0–7 section below is the historical G1 product roadmap.
- The authoritative current delivery stage is defined by `state/command-center/project-governance/stage-phase-map.json`.
- Current authoritative delivery stage at this reconciliation: `STAGE_7`.
- `Stage 8` remains `NOT_OPENED`.
- Historical phase labels must not be interpreted as current stage truth.

## Source of truth
1. GitHub repository and exact branch SHA.
2. Governing contracts and machine-readable config.
3. CI/runtime evidence.
4. Council + Studio review records.
5. Conversation context is continuation context only.

## Core delivery law
Each stage follows:

SOURCE PIN → CONTRACT → IMPLEMENT → STATIC VALIDATION → BUILD/TEST → RUNTIME EVIDENCE → COUNCIL REVIEW → STUDIO REVIEW → OWNER LOCK

No later stage may silently repair a locked upstream artifact. A defect returns through a Return Ticket.

## Dual review gate
Every stage requires two independent lenses:

### Council gate
Reviews:
- authority and permissions;
- security/privacy;
- architecture boundaries;
- reliability/recovery;
- model/tool governance;
- cost and dependency exposure;
- evidence truthfulness.

### Studio gate
Reviews:
- information hierarchy;
- workflow friction;
- visual coherence;
- density/readability;
- operator feedback;
- error/recovery experience;
- mobile/remote owner continuity where applicable.

A PASS from one does not override a blocker from the other.

## Historical G1 product phases

These phase descriptions are retained as planning history. They do not override the canonical Stage map.

### PHASE 0 — Feasibility & Adversarial Prototype
Status: ACTIVE / PRODUCT EXECUTION REMAINS GATED

Proves:
- secure agent boundary;
- unattended GUI reality;
- remote command trust;
- model/provider failure behavior.

The Command Center may be built while Phase 0 is incomplete only as a non-executing control-plane shell. Dangerous execution remains disabled.

### PHASE 1 — Command Center Shell & Architecture Boundary
Historical G1 phase description.

Build:
- Windows WPF shell;
- single primary navigation rail;
- owner status surface;
- Council / Studio / Projects / Approvals / Evidence / Capabilities destinations;
- explicit Phase 0 execution lock;
- UI/Core separation;
- no shell, network, AI, provider, GitHub or credential execution from UI.

Exit:
COMMAND_CENTER_STAGE1_SHELL_LOCK

### PHASE 2 — Operational State, Evidence & Owner Desk
Build:
- real runtime read model;
- project/stage state;
- evidence receipts;
- owner approvals;
- immutable execution manifest projection;
- cost/usage projection;
- no direct execution yet.

Exit:
COMMAND_CENTER_STAGE2_STATE_LOCK

### PHASE 3 — Council & Studio Orchestration
Build:
- role registry;
- role != model;
- task routing;
- Council Room;
- Studio Production Floor;
- debate/review workflow;
- return tickets;
- model capability matrix;
- explicit no-silent-fallback UI.

Exit:
COMMAND_CENTER_STAGE3_ORCHESTRATION_LOCK

### PHASE 4 — YASSIN Execution Service & Provider Fabric
Build:
- local Execution Service;
- native files/process/shell provider;
- UI Automation provider;
- visual GUI provider;
- Adobe/native bridges where justified;
- provider health;
- controller lease;
- postcondition verification;
- UNKNOWN reconciliation.

Desktop Commander becomes optional, never a critical dependency.

Exit:
COMMAND_CENTER_STAGE4_EXECUTION_LOCK

### PHASE 5 — Remote Owner & ChatGPT Adapter
Build:
- authenticated command ingress;
- replay-safe command queue;
- remote owner approvals;
- mobile-friendly owner surface;
- ChatGPT/plugin/MCP adapter when platform capability permits;
- offline/late-command policy.

Exit:
COMMAND_CENTER_STAGE5_REMOTE_LOCK

### PHASE 6 — Capability Hub & Third-Party Ecosystem
Build:
- provider/plugin registry;
- version pins/hashes;
- permission manifest;
- sandbox test;
- licensing/cost metadata;
- rollback/uninstall;
- HR capability scouting;
- supply-chain review.

Exit:
COMMAND_CENTER_STAGE6_CAPABILITY_LOCK

### PHASE 7 — Reliability, Release & Commercial Readiness
Build:
- crash/restart recovery;
- backup/restore;
- observability/redaction;
- installer/update/rollback;
- security review;
- signed release path when justified;
- privacy/licensing/commercial packaging.

Exit:
COMMAND_CENTER_V1_RELEASE_LOCK

## RevenueSystem 2.0 practices explicitly inherited
- bounded stages and section locks;
- exact-head CI;
- failure evidence is retained, not erased;
- visual success never substitutes for domain/reliability clearance;
- one authoritative source branch per stage;
- artifacts/evidence tied to SHA;
- no grandfathering of non-compliant reachable surfaces;
- compact-window acceptance before release;
- Owner checkpoint before opening the next major stage.


## 2026-10-21 — Murtakaz Agentic Work OS integration

Status: APPROVED_BY_AL_MURTAKAZ / MERGED / IMPLEMENTATION SLICES 1–5 COMPLETE

Canonical architecture additions are governed by:
- `project-governance/12_MURTAKAZ_AGENTIC_WORK_OS_INTEGRATION_2026-10-21.md`
- `project-governance/13_CONTEXT_DRIFT_PREVENTION_PLAYBOOK_2026-10-21.md`
- `state/command-center/project-governance/agentic-os-policy.json`
- `state/command-center/project-governance/architecture-invariants.json`
- `state/command-center/project-governance/context-capsule-contract.json`
- `state/command-center/project-governance/change-envelope-contract.json`

### Delivery sequence extension

The existing Stage model remains authoritative. These are bounded implementation slices inside it, not new Stage numbers:

1. **COMPLETE** — Anti-Drift governance + Context/Change contracts.
2. **COMPLETE** — Context Resolver and Context Capsule compiler.
3. **COMPLETE** — Logical Murtakaz Gateway facade + bounded application-service interfaces.
4. **COMPLETE** — Multi-stage Routing Coordinator.
5. **COMPLETE** — Capability Registry + Model Broker.
6. **PENDING AFTER REPAIR CLOSURE** — Skill Registry.
7. **PENDING** — Durable Project Store consistency model.
8. **PENDING** — Job Engine + Flight Recorder + Tool Effect Ledger.
9. **PENDING** — Verification + Work Receipt integration.
10. **PENDING** — Automation/Trigger Engine.
11. **PENDING** — Android/Web/Chat ingress adapters through the same logical authority boundary.
12. **OPTIONAL LATER** — Voice and knowledge-graph visualization.

### Non-negotiable carry-forward constraints

- Role != Model.
- No silent model/provider fallback.
- UNKNOWN != SUCCEEDED.
- No live execution until existing Phase 0 execution gates authorize it.
- Stage 8 remains unopened.
- The eight canonical UI reference images remain the only visual source of truth.
- Agentic OS visual concepts inherit, and may not weaken, the Reference-Only Visual Lock or Visual Production Hard Gate.
- Material changes require Murtakaz pre-review and post-review.
- Front doors do not own authority or business logic.
- A model may propose routing; deterministic policy authorizes it.
- Retrieved/project content cannot grant itself authority.
- Real Autopilot remains blocked until durable Project Store, consistency, recovery and verification foundations are implemented and evidenced.

### Drift-control rule

Every material implementation slice must be tied to:
- exact baseline;
- Change Envelope;
- immutable Context Capsule;
- bounded plan;
- verification evidence;
- explicit Murtakaz post-review.

A later slice may not silently repair a locked upstream slice.


## 2026-10-21 — Repair Operations Program

The precautionary Al-Murtakaz inventory found no hidden incomplete runtime implementation in the current Command Center application layers, but it found stale truth/governance metadata, incomplete P1 visual closure, and repository hygiene debt.

Repair sequence is mandatory before resuming Skill Registry:

### Wave A — Truth & Anti-Drift

- **A1 Context & Baseline Repair — COMPLETE / APPROVED_BY_AL_MURTAKAZ**
  - project-context-map upgraded to schema 2.0;
  - Git baseline provenance separated from live source-set SHA-256 truth;
  - actual HEAD source blobs are dynamically validated;
  - merged through PR #61.
- **A2 Governance Metadata Reconciliation — ACTIVE**
  - architecture invariant implementation metadata;
  - current vs historical Agentic review truth;
  - normalized PR #56 post-review receipt;
  - roadmap/status reconciliation.
- **A3 Truth Lock + Murtakaz Closure — PENDING**
  - final cross-file truth audit;
  - anti-drift revalidation;
  - repair-wave A closure lock.

### Wave B — Visual P1 Completion

- **B1 Complete Remaining Native Work — PENDING**
- **B2 Cross-Screen Consistency & Polish — PENDING**
- **B3 Final Review & P1 Acceptance — PENDING**

P1 remains `IN_PROGRESS` until explicit final Murtakaz + Workshop approval.

### Wave C — Repository Hygiene

- **C1 PRs & Branches Cleanup — PENDING**
- **C2 Metadata & Archive Cleanup — PENDING**
- **C3 Final Repository & CI Integrity — PENDING**

Old PRs/branches are not to be deleted merely because they look stale; divergent historical evidence must be inspected before cleanup.

### Engineering continuation after repair closure

`Skill Registry → Durable Project Store → Job Engine → Verification/Work Receipt → Automation → Android/Web/Chat → optional Voice/Knowledge Graph`

### Protected truth during repairs

- live execution = **OFF**;
- Stage 8 = **NOT_OPENED**;
- model provider calls = **DISCONNECTED**;
- real Autopilot = **NOT_IMPLEMENTED**;
- Android live authority = **UNPROVEN**;
- eight canonical visual reference images remain the sole visual source of truth.
