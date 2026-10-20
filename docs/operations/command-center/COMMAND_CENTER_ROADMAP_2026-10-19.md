# UniversalCouncil Command Center — Product Roadmap
Date: 2026-10-19
Status: ACTIVE / OWNER-AUTHORIZED
Development method: RevenueSystem 2.0-inspired gated vertical delivery

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

## Product phases

### PHASE 0 — Feasibility & Adversarial Prototype
Status: ACTIVE / PRODUCT EXECUTION REMAINS GATED

Proves:
- secure agent boundary;
- unattended GUI reality;
- remote command trust;
- model/provider failure behavior.

The Command Center may be built while Phase 0 is incomplete only as a non-executing control-plane shell. Dangerous execution remains disabled.

### PHASE 1 — Command Center Shell & Architecture Boundary
Current phase.

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


## Architecture amendment — 2026-10-20

Owner adoption:
- Murtakaz Agentic Work OS architecture is adopted as the product-level control plane.
- Context Drift Prevention Contract is a blocking quality contract for all later stages.
- Machine-readable architecture invariants are part of stage acceptance.

Governing additions:
- `docs/operations/command-center/MURTAKAZ_AGENTIC_OS_ARCHITECTURE_2026-10-20.md`
- `docs/operations/command-center/CONTEXT_DRIFT_PREVENTION_CONTRACT_2026-10-20.md`
- `state/command-center/architecture-invariants.json`

The implementation sequence is extended with these foundations:
1. Anti-Drift enforcement and Context Capsule.
2. Murtakaz Command Gateway.
3. Project Context Resolver and Project Knowledge Map.
4. Multi-stage routing.
5. Capability Registry and Model Broker.
6. Skill Registry.
7. Job Engine.
8. Verification/Work Receipt integration.
9. Automation Engine.
10. Front-door integrations.

These are additive to the existing phase model. They do not waive or replace Stage locks, Council/Studio review, Hybrid Execution, Tool Authority, exact-head evidence, Return Tickets, or Owner checkpoints.

No stage may lock if a blocking invariant in `architecture-invariants.json` fails.
