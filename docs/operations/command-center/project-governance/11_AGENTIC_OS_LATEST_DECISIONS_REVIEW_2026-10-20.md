# المرتكز — مراجعة القرارات المعمارية الأخيرة
Date: 2026-10-20
Status: FORMAL PROJECT-LOCAL REVIEW
Review scope: PR #54 + Agentic Work OS adoption + Context Drift Prevention + architecture invariants
Canonical review baseline: `command-center/project-local-council-studio-20261019`
Baseline SHA: `1702d73eafa2319200164898bdaf0d400d4af524`

## Executive verdict

**CONDITIONAL ACCEPT / RETURN FOR ALIGNMENT BEFORE MERGE**

The architectural direction is accepted in principle.

The review does NOT authorize merging PR #54 in its current form.

Primary reason:
PR #54 was created from `command-center/living-operations-execution-package-20261019` at SHA `2c56bf85899aa71204a0f10007a67d72315fb542`, while the project-local Murtakaz branch is 259 commits ahead and already contains stronger project-local governance, visual-lock, approval and anti-drift controls.

This is a concrete example of the exact context-drift class the new architecture is intended to prevent.

Required disposition:
- preserve the architectural decisions;
- do not merge the old-baseline PR;
- re-apply the accepted deltas on top of the latest project-local baseline;
- reconcile overlaps rather than creating parallel sources of truth.

---

# A. مراجعة المرتكز

## MRTKZ-R01 — Baseline drift
Severity: BLOCKING

Finding:
The new architecture branch is based on a stale product baseline.

Evidence:
- architecture PR base: `2c56bf8...`
- current project-local baseline: `1702d73...`
- project-local branch is 259 commits ahead.

Risk:
A correct new contract can accidentally omit or contradict later project-local rules.

Decision:
**BLOCK MERGE. REBASE/RE-APPLY ON CURRENT PROJECT-LOCAL BASELINE.**

## MRTKZ-R02 — Project-local identity must govern terminology
Severity: BLOCKING

Finding:
The new documents use generic terms such as "Council + Studio" and "Council / Single Agent".

Current project-local law defines:
- المرتكز = complete local system;
- هيئة المرتكز = governance/review;
- مشغل المرتكز = design/interaction/prototype.

The generic Universal Council and original Media Studio must not be confused with these local units.

Required:
Use project-local terminology for current Command Center governance. Historical references may retain old names.

## MRTKZ-R03 — Mandatory Murtakaz approval cycle is missing from the new top-level architecture
Severity: BLOCKING

Current law:
No product change may be considered approved/completed/merge-ready/stage-ready without explicit recorded Murtakaz approval.

The Agentic OS architecture must incorporate:
REQUEST
-> MURTAKAZ PRE-REVIEW
-> CONTEXT CAPSULE / PLAN
-> IMPLEMENT
-> VERIFY
-> MURTAKAZ POST-REVIEW
-> OWNER/merge gate as applicable.

Council/workshop reviews are inputs to Murtakaz approval, not replacements for it.

## MRTKZ-R04 — Do not create a second visual anti-drift authority
Severity: BLOCKING

The new generic Visual Context Capsule rules are directionally correct.

However the current project already has stronger canonical controls:
- `18_REFERENCE_ONLY_VISUAL_LOCK.md`
- `23_VISUAL_PRODUCTION_HARD_GATE.md`
- canonical eight-reference manifest;
- direct reference-byte binding;
- pre-render receipt;
- single-screen law;
- generated-image quarantine;
- object inventory gate.

Required:
The new Anti-Drift architecture must reference and inherit these controls.
It must not create a parallel weaker visual truth source.

## MRTKZ-R05 — Source hierarchy requires domain-aware precedence
Severity: BLOCKING

The new contract lists repository/asset sources above owner directives.

The existing visual lock defines:
1. approved reference images;
2. explicit Owner visual directive;
3. interaction/motion contracts;
4. component/design-token docs;
5. generated exploration.

These are not actually contradictory if directives are first converted into typed canonical records, but this must be explicit.

Required:
- Owner chat text alone does not silently override locked truth.
- A new Owner directive creates a versioned directive record.
- If it intentionally changes a lock/reference, it triggers a Change-of-Truth gate.
- Domain-specific precedence is compiled into the Context Capsule.

## MRTKZ-R06 — Result-state mismatch
Severity: BLOCKING

Agentic architecture Job states currently end with:
SUCCEEDED / FAILED / UNKNOWN / BLOCKED.

Architecture invariants also define:
STALE_CONTEXT / CONTEXT_CONFLICT.

Required:
Unify one typed result/state model and define which are terminal vs resumable.

Recommended:
- BLOCKED
- FAILED
- UNKNOWN
- STALE_CONTEXT
- CONTEXT_CONFLICT
- WAITING_FOR_APPROVAL
- SUCCEEDED

## MRTKZ-R07 — Invariant applicability is missing
Severity: BLOCKING

All 24 invariants are currently BLOCKING globally.

Problem:
Several require systems that do not exist yet, such as Job Engine/Context Capsule enforcement.

Without applicability/effective-stage metadata, early safe stages could become impossible to lock or validators could pass only by pretending capabilities exist.

Required per invariant:
- applies_from_stage/capability;
- applies_to_change_classes;
- enforcement = DOC / STATIC / CI / RUNTIME;
- implementation_state;
- validator id;
- waiver policy = normally none for authority/truth rules.

## MRTKZ-R08 — Strong approval of core direction
Accepted without reversal:
- one governed brain, multiple front doors;
- no business logic in front doors;
- multi-stage explicit routing;
- role != model;
- no silent fallback;
- Skill contracts;
- Job Engine concept;
- Capability Registry;
- Project Data Fabric separation;
- OUTPUT/WORKING cannot self-promote to CANONICAL;
- verification before success;
- immutable traceability principle;
- Android as control/supervision surface, not independent brain.

---

# B. مراجعة هيئة المرتكز / Council lens

## GOV-R01 — Gateway is becoming a God Object
Severity: BLOCKING ARCHITECTURE

The gateway is assigned authentication, normalization, context, risk, routing, skills, models, execution selection, approval, evidence and receipt writing.

Required boundary:
Front Door
-> Command Gateway / Facade
-> Application orchestration services
   - ContextResolver
   - AuthorityPolicy
   - RoutingCoordinator
   - SkillResolver
   - ModelBroker
   - JobService
   - VerificationService
   - ReceiptService
-> Infrastructure providers.

The gateway owns ingress/coherence, not every implementation responsibility.

Architecture Boundary Audit direction:
`View/Client -> Application/Gateway -> Orchestration Services -> Execution/Data`.

## GOV-R02 — Remote Owner Gateway must become an ingress adapter, not a competing authority path
Severity: BLOCKING SECURITY

Existing Remote Owner trust already has:
- OWNER/device/session;
- nonce;
- idempotency;
- issue/expiry;
- bounded target/effects;
- replay protection.

Required:
Remote transport and Chat/Android/Web adapters terminate into the same logical Murtakaz Gateway authorization path.

"One gateway" means one logical authority boundary, not necessarily one process or one network endpoint.

## GOV-R03 — Prompt/data injection boundary must be explicit
Severity: BLOCKING SECURITY

Context retrieved from:
- documents;
- GitHub;
- web;
- plugins;
- project files;
- model output
must be treated as untrusted data unless it is a signed/typed governing record.

Required:
- instruction/data separation;
- authority metadata on each context item;
- retrieved content cannot grant permissions;
- tool output cannot rewrite policy;
- malicious text in artifacts cannot become router instructions.

## GOV-R04 — Immutable ledger must not become immutable secret storage
Severity: BLOCKING PRIVACY

Audit immutability is approved as a principle, but receipts/logs must not permanently store:
- passwords;
- tokens;
- raw credentials;
- unnecessary private payload;
- unrestricted screenshots.

Required:
redaction/tokenization before append, payload references where possible, retention rules, privacy classes and secure deletion for referenced sensitive artifacts.

## GOV-R05 — Data Fabric needs consistency rules
Severity: P1 ARCHITECTURE

Four logical stores are accepted, but cross-store consistency is unspecified.

Required before real Autopilot:
- stable object ids;
- schema versions;
- event ordering;
- idempotent writes;
- transaction/outbox or equivalent consistency strategy;
- recovery after partial persistence;
- backup/restore/incarnation binding.

This aligns with the existing Murtakaz finding that a canonical durable Project Store is still missing.

## GOV-R06 — Reviewer independence must be enforceable
Severity: P1 QUALITY

The adversarial-review concept is accepted.

For high-drift/high-risk work:
- executor cannot self-approve;
- independent deterministic validator should be used where possible;
- review role/context is separate;
- model diversity may be used when valuable, but a different model is not by itself proof of independence;
- final authority remains policy/evidence based.

## GOV-R07 — Capability health must be operation-specific and freshness-bound
Severity: P1 RELIABILITY

A provider may be healthy for read but not execute.

Registry entries should include per-operation:
- verified capability;
- freshness/TTL;
- environment/host;
- evidence level;
- auth/effect;
- failure reason.

Do not reduce this to one green/red provider badge.

## GOV-R08 — Automation graduation is accepted
Strong PASS:
Do not automate solely from N successful repetitions.

Require:
tests + shadow + verified runs + risk/authority review.

Irreversible/external actions remain gated.

---

# C. مراجعة مشغل المرتكز / Studio lens

## STUDIO-R01 — Internal complexity must stay out of the Owner's primary workflow
Severity: BLOCKING UX

Eight routing stages, registries and ledgers are implementation architecture.

They must not turn Home into infrastructure UI.

Retain the accepted Owner mental model:
START -> UNDERSTAND -> DECIDE -> WORK -> VERIFY.

Primary experience remains:
Command Composer -> Active Work -> Decision Stack -> Project -> Work Receipt.

Detailed routing lives under Evidence/System/Ask This.

## STUDIO-R02 — Operational HUD must be subordinate
Severity: P1 UX

Provider/model/device health is valuable, but Home must not lead with infrastructure.

Use:
- compact truthful summary;
- blockers that affect current work;
- deeper capability details under System / Tool Dock.

## STUDIO-R03 — Visual direction is already locked
Severity: BLOCKING VISUAL

No new visual language is authorized by the Agentic OS architecture.

The only visual source of truth remains the eight canonical reference images and their manifest.

New architecture concepts must be fitted into that visual system.

No new:
- dashboard theme;
- palette;
- role avatar treatment;
- decorative identity;
- architecture-themed art direction.

## STUDIO-R04 — Visual Capsule must integrate the existing production hard gate
Severity: BLOCKING VISUAL

A canonical UI visual Job must inherit:
- actual parent reference bytes;
- reference SHA;
- one-screen parent;
- object inventory;
- preflight registration;
- reference-binding receipt;
- allowed delta;
- direct reference-capable production mode;
- output hash;
- side-by-side evidence;
- Murtakaz governance + workshop review.

A generic "side-by-side review" alone is not sufficient.

## STUDIO-R05 — Progressive disclosure is mandatory
Severity: P1 UX

Context Capsule, Skill version, model route, provider chain and verification evidence should be available but not all simultaneously dominant.

Expose:
- simple state first;
- explanation on demand;
- full evidence deeper.

## STUDIO-R06 — Approval fatigue must be prevented
Severity: P1 UX

The Anti-Drift system must not interrupt the Owner for every low-risk internal transition.

Use policy-based approvals:
- deterministic safe transitions may proceed within explicit authority;
- owner decisions interrupt only when required by risk/change-of-truth/external consequence;
- all approvals remain inspectable in history.

Quiet Mode/Decision Stack remain the preferred interaction pattern.

## STUDIO-R07 — Cross-platform semantics accepted
PASS:
Android/Desktop may differ in layout but must show the same:
- project state;
- checkpoint;
- approval;
- artifact/version;
- truth state;
- Job result.

## STUDIO-R08 — No Dead Surface remains mandatory
PASS WITH IMPLEMENTATION GATE:
Every actionable-looking object must work, navigate, expose context, or be truthfully disabled with reason.

---

# D. Combined risk register

## P0 blockers before architecture merge
1. Re-apply/rebase on latest project-local Murtakaz baseline.
2. Replace generic Council/Studio governance wording with project-local Murtakaz hierarchy where applicable.
3. Incorporate mandatory Murtakaz pre/post approval cycle.
4. Inherit existing reference-only visual lock + Visual Production Hard Gate instead of duplicating them.
5. Reconcile source precedence with versioned Owner directives.
6. Split Gateway responsibilities into bounded application services.
7. Unify Job/result state schema.
8. Add applicability/enforcement metadata to architecture invariants.
9. Route Remote Owner/Android/Web/Chat transports through one logical authority gateway while retaining replay/idempotency protections.
10. Add explicit prompt/data-injection and audit-redaction boundaries.

## P1 requirements before real autonomous execution
- durable Project Store consistency model;
- operation-specific capability freshness;
- reviewer independence;
- Job restart/incarnation binding;
- Work Receipt privacy policy;
- risk-tiered approval UX;
- performance/latency budgets for multi-stage routing.

---

# E. Architecture decisions accepted by all three reviewers

The following are retained:
- one governed brain / many front doors;
- Murtakaz Command Gateway as logical authority boundary;
- bounded Context Capsule;
- explicit multi-stage routing;
- AI proposes, deterministic policy authorizes;
- Model Broker with Owner-controlled overrides;
- Role != Model;
- no silent model/provider fallback;
- governed Skill Registry;
- Job Engine for long work;
- Capability Registry;
- Hybrid GUI-primary execution;
- independent post-state verification;
- Project Data Fabric;
- SOURCE/CANONICAL/WORKING/OUTPUT/ARCHIVE separation;
- generated output cannot auto-promote to canonical;
- Project Knowledge Map;
- Android as companion/control-intent surface;
- voice and knowledge graph remain optional later layers;
- automation only after reliability + authority review.

---

# F. Final joint disposition

### المرتكز
**RETURN FOR ALIGNMENT — architecture direction accepted.**

### هيئة المرتكز
**CONDITIONAL ACCEPT — P0 architecture/security corrections required.**

### مشغل المرتكز
**CONDITIONAL ACCEPT — preserve canonical visual system and simplify Owner-facing complexity.**

### Architecture Boundary Audit
**RETURN FOR BOUNDARY EXTRACTION — do not implement Gateway as a monolith.**

## Merge status

PR #54:
**DO NOT MERGE IN CURRENT FORM.**

Recommended continuation:
Create a clean architecture integration branch from exact project-local SHA `1702d73eafa2319200164898bdaf0d400d4af524`, port the accepted contracts, resolve P0 findings, regenerate machine-readable policy, run project-local validators, then submit the revised package to Murtakaz pre/post review.

No change in:
- Phase 0 live-execution lock;
- Stage 8 status;
- canonical eight visual references;
- real Android/live Autopilot truth.
