# المرتكز — المراجعة الشاملة لبرنامج UniversalCouncil Command Center

Date: 2026-10-19  
Review body: **المرتكز**  
Governance unit: **هيئة المرتكز**  
Design/interaction unit: **مشغل المرتكز**  
Review type: FULL PRODUCT / PRE-PROTOTYPE AUDIT  
Scope: repository source + Stage 1–7 contracts + WPF shell + Application/Core/Infrastructure boundaries + Remote Owner/Transport + Living Operations + Pulse + planned Android + planned Autopilot  
Execution authority: UNCHANGED / `BLOCKED_PHASE0`  
Stage 8: NOT OPENED

---

# 1. الحكم التنفيذي

## Verdict

**STRONG FOUNDATION / CONDITIONAL GO FOR NON-AUTHORITATIVE PROTOTYPE AFTER PRE-PROTOTYPE ALIGNMENT**

المرتكز لا يوصي بإعادة بناء الأساس البرمجي من الصفر.

الحدود الحالية بين:
- UI؛
- Host/Application؛
- Infrastructure؛
- execution fabric؛
- remote trust؛
- evidence/truth

مبنية باتجاه صحيح ومحافظ.

لكن البرنامج الحالي وLiving Operations الجديد لم يلتقيا بعد في طبقة واحدة متماسكة.

هناك فرق واضح بين:

### الواقع الحالي
Stage 7 diagnostic/read-only control surface.

وبين:

### المنتج المستهدف
Command-first, Project-first, Living Operations, Autopilot, Pulse, Android Owner, interactive semantic objects.

قبل أول Prototype تفاعلي يجب إغلاق بوابة مواءمة صغيرة تمنع بناء واجهة مستقبلية فوق:
- Orchestration قديم؛
- أسماء قديمة؛
- stage semantics متضاربة؛
- data model غير محدد.

---

# 2. ما تمت مراجعته

## Product/governance
- Command Center roadmap.
- Stage 1 shell contract.
- Stage 2 operational state.
- Stage 3 orchestration.
- Stage 4 execution fabric.
- Stage 5 remote owner gateway.
- Stage 6 authenticated transport.
- Stage 7 owner device + tailnet.
- Phase 0 execution gates.

## Desktop application
- `App.xaml`
- `MainWindow.xaml`
- `MainWindow.xaml.cs`
- `MainWindowViewModel.cs`

## Application/runtime boundaries
- Host composition.
- Operational state services.
- Orchestration service.
- Execution Fabric service.
- Remote Owner service.
- Owner enrollment.
- Remote transport host.
- local execution primitives.

## Project design system
- Pulse.
- Owner Workspace UX v2.
- Living Operations Visual Bible.
- Motion Bible.
- Interaction Choreography.
- Component Anatomy.
- Desktop map.
- Android map.
- Role Sigils.
- State/Motion Matrix.
- Event/Animation map.
- P1 vertical slice.

## Project-local governance
- المرتكز inheritance lock.
- هيئة المرتكز.
- مشغل المرتكز.
- routing/collaboration contracts.

---

# 3. نقاط القوة التي يجب عدم كسرها

## S-01 — Execution fails closed

Current truth:
`live_execution_authorized = false`

The execution service remains SAFE/DISABLED.

This is correct.

Do not weaken this to make a prototype appear functional.

## S-02 — UI does not own execution

The architecture boundary remains:
Presentation -> Host -> Application -> Infrastructure / projections.

The WPF layer must not gain:
- shell;
- filesystem mutation;
- network authority;
- credentials;
- provider dispatch;
- Tailscale control.

This is a critical invariant.

## S-03 — Remote Owner trust boundary is strong

Remote commands require:
- OWNER context;
- device;
- session;
- nonce;
- idempotency key;
- issue/expiry time;
- bounded target;
- bounded effects;
- out-of-band authorization.

`ACCEPTED_COMMAND != EXECUTION_AUTHORITY`

Keep this rule.

## S-04 — Replay protection is correctly treated as durable security state

Persistent nonce/idempotency rules are already present.

This is a strong base for Android Owner actions later.

## S-05 — Model and role are separated

Stage 3 correctly preserves:

`Role != Model`

Selection precedence:
Task Override -> Role Override -> Project Default -> Global Default.

Silent fallback remains forbidden.

This aligns with the Owner's model-control requirement.

## S-06 — UNKNOWN is consistently protected

Execution Fabric, Remote Owner, Pulse and Living Operations all preserve:

`UNKNOWN != SUCCESS`

This must remain a product-wide law.

## S-07 — Living Operations has a mature truth-aware visual grammar

The design system already defines:
- semantic colors;
- truth badges;
- event-backed animation;
- Reduced Motion;
- Interactive Semantic Objects;
- Project Filmstrip;
- checkpoint/fork/recovery;
- Decision Mode;
- Evidence Peek.

This is strong enough to prototype.

## S-08 — Parent Council/Studio isolation is now explicit

The project-local governance is an overlay.

The parent systems remain untouched.

This is the correct long-term maintenance model.

---

# 4. P0 findings — يجب إغلاقها قبل P1 Prototype

## MRTKZ-001 — Orchestration source mismatch

Severity:
P0 / ARCHITECTURE + PRODUCT TRUTH

Current:
`state/command-center/orchestration-catalog.json` still projects:
- Universal Council general roles;
- Media Studio writing/pre-production/production pipeline.

The current WPF also renders these as:
- المجلس;
- الاستوديو;
- SERIAL PRODUCTION.

Problem:

The project has now adopted:
- هيئة المرتكز;
- مشغل المرتكز.

If P1 continues to read the old catalog, the new product will visually claim project-local governance while the underlying projection still describes unrelated generic/media structures.

Required:

Create a **project-local Murtakaz orchestration projection** generated from:
- project-council.json;
- product-studio.json;
- inheritance-lock.json;
- review routing matrix.

It must:
- record source blob SHAs;
- fail on drift;
- remain read-only;
- not mutate parent roles;
- preserve Role != Model.

Do not delete the historical Stage 3 catalog.

Outcome:
**BLOCKER FOR P1 GOVERNANCE SURFACES**

---

## MRTKZ-002 — Current WPF violates the future No Dead Surface law

Severity:
P0 / UX

Source observation:

`RailButtonStyle` sets:
`IsHitTestVisible=False`

MainWindow rail visually presents buttons for:
- overview;
- Council;
- Studio;
- projects;
- approvals;
- remote owner;
- evidence;
- secure transport.

They have no Command/Click behavior.

Current Stage 1 design deliberately made them noninteractive, which was truthful for that stage.

Problem:

Living Operations now defines:
**No Dead Surface**.

Therefore the existing shell may remain historical Stage 7 UI, but it cannot be used as the P1 shell without replacement.

Required:

P1 must introduce real:
- navigation commands;
- selected route state;
- focus/keyboard behavior;
- disabled-with-reason only where genuinely unavailable.

Outcome:
**BLOCKER FOR P1 UI REUSE**
Not a defect in historical Stage 1 intent.

---

## MRTKZ-003 — Stage taxonomy drift

Severity:
P0 / GOVERNANCE

The original roadmap defines:
- PHASE 7 = Reliability, Release & Commercial Readiness.

Actual current Command Center Stage 7 is:
- Owner Device Enrollment + Tailnet Round Trip.

There is also explicit language:
- Stage 8 NOT OPENED.

Problem:

"Phase", "Stage" and roadmap numbering now represent different evolutions of the project.

This creates risk for:
- UI labels;
- gate logic;
- future PR naming;
- Owner approvals;
- automation.

Required:

Publish a canonical stage map:

`Product Roadmap Generation 1`
vs
`Command Center Delivery Stages 1–7`
vs
`Future Stage 8+`

No new stage may be opened until naming is reconciled.

Outcome:
**BLOCKER FOR NEW STAGE OPENING**
P1 design prototype may proceed after documentation alignment.

---

## MRTKZ-004 — Stage 7 CI state projection is stale/inconsistent

Severity:
P0 / TRUTH

Current `owner-device-tailnet.json` says:

`stage7_ci_foundation_passed = false`

But exact-head Stage 7 SHA:
`7dcf0e7a17040cc70ad07ad87c9ca2709641cd83`

has verified GitHub runs:
- Command Center Stage 7 #39234444557 = SUCCESS
- Company Stage 0 #39234444479 = SUCCESS
- CodeQL #39234444439 = SUCCESS

This does NOT prove:
- YASSIN host probe;
- Tailscale;
- phone round-trip;
- session revocation.

But the CI field itself is stale.

Required:

Repair the projection-generation rule so repository state distinguishes:
- CI FOUNDATION PASS;
- REAL HOST EVIDENCE PENDING.

Do not manually flip unrelated host gates.

Outcome:
**TRUTH BLOCKER**

---

## MRTKZ-005 — No canonical durable Project Store yet

Severity:
P0 / AUTOPILOT

Current Command Center primarily consumes repository projection JSON.

Living Operations requires durable objects:
- project;
- task;
- artifact;
- decision;
- checkpoint;
- branch;
- Work Receipt;
- Pulse;
- model selection;
- tool effects.

A repository projection is not sufficient as a live durable project engine.

Required before real Autopilot:
define a canonical Project Store with:
- stable IDs;
- schema/version;
- event/history relationship;
- concurrency;
- crash recovery;
- migration;
- retention;
- backup/restore;
- incarnation/version binding.

P1 Prototype may use explicitly isolated fixtures.

Outcome:
**NOT A BLOCKER FOR FIXTURE P1**
**BLOCKER FOR REAL AUTOPILOT**

---

## MRTKZ-006 — Durable Autopilot is designed, not implemented

Severity:
P0 for real autonomous execution.

Missing runtime primitives include:
- durable orchestration lifecycle;
- Project Flight Recorder;
- Tool Effect Ledger;
- project checkpoints;
- replay/fork runtime;
- loop detection;
- budget counters;
- suspended-resource wait;
- project-level resume after process restart.

Existing execution journal/lease concepts are valuable but do not yet equal a full project durable engine.

Required:

Separate:
`Action durability`
from
`Project durability`.

Outcome:
**BLOCKER FOR REAL AUTOPILOT**
Not a blocker for non-authoritative visual prototype.

---

## MRTKZ-007 — Shared Windows/Android event protocol remains design-only

Severity:
P0 for connected Android.

Current:
`living-operations-event-map.json` is a visual contract.

It does not yet define a production transport/schema implementation.

Required:
- event envelope schema;
- sequence/version;
- object identity;
- snapshot;
- delta;
- reconnect reconciliation;
- duplicate suppression;
- stale event behavior;
- backward/forward compatibility.

The runtime emits facts.
Clients render motion.

Outcome:
**BLOCKER FOR REAL CROSS-PLATFORM LIVE STATE**

---

# 5. P1 findings — يجب أن تدخل Roadmap قبل الإنتاج

## MRTKZ-008 — Android Owner is not implemented

Current:
design contracts only.

Tailscale/phone state remains unproven.

Requirement:
Do not render Android as Connected/Ready until:
- enrollment;
- session;
- private route;
- deep link;
- phone round-trip;
- revocation
are evidenced.

---

## MRTKZ-009 — Owner Notification Broker is missing

The desired behavior requires:
- important push;
- critical escalation;
- Visual Digest;
- deep link to decision/artifact.

Need separate components:
1. notification event producer;
2. broker;
3. push provider adapter;
4. privacy redactor;
5. device registration;
6. escalation policy.

Push delivery must never itself grant authority.

---

## MRTKZ-010 — Model/Reasoning controls have no live provider capability source

Current model provider connection is not live.

Living UI requires:
- provider;
- model;
- supported reasoning levels;
- current usage;
- fallback availability;
- limits;
- failure reason.

Required:
capability registry per provider/model.

If Max is unsupported:
do not silently downgrade.

---

## MRTKZ-011 — Pulse is an adopted contract, not a live event product yet

Pulse policy is strong.

Missing runtime:
- draft storage;
- provenance binding;
- expiration;
- publish;
- duplicate suppression;
- digest;
- promotion to typed artifact;
- Android sync.

Until implemented:
do not show fabricated active stories.

---

## MRTKZ-012 — Flight Recorder / tracing / evals need formal integration

Adopted direction requires:
- execution trace;
- model/tool spans;
- prompts/role version;
- outcome;
- evidence;
- cost;
- latency;
- retries;
- fallback.

This should be separate from human-friendly Pulse.

---

## MRTKZ-013 — Tool Effect Ledger is required for irreversible/replay-risk operations

Need states such as:
- INTENT_RECORDED;
- STARTED;
- COMPLETED_VERIFIED;
- FAILED;
- UNKNOWN_AFTER_CRASH.

On unknown:
VERIFY FIRST.
Do not blindly replay.

---

## MRTKZ-014 — Sandbox/isolated workspace missing for software Autopilot

Software changes should prefer:
- isolated worktree;
- sandbox/container where practical;
- tests;
- evidence;
- review;
before affecting canonical project state.

GUI creative software remains a separate execution class.

---

## MRTKZ-015 — Rehearsal/Shadow mode should precede Full Autopilot

Before live autonomous work:
show:
- intended stages;
- tools;
- effects;
- estimated model/provider use;
- irreversible gates;
- expected Owner interruptions.

No side effects in rehearsal.

---

## MRTKZ-016 — Trigger Engine is not yet specified as runtime

Needed triggers:
- schedule;
- GitHub event;
- file/artifact;
- provider quota restored;
- project state;
- analytics available.

Each trigger must enter through normal authority/policy checks.

---

## MRTKZ-017 — Role/Prompt Version Registry needs project binding

The project should version:
- role contract;
- instructions;
- skill set;
- model preference;
- reasoning policy;
- evaluation score.

A role update must be comparable and rollbackable.

---

## MRTKZ-018 — Memory scopes need explicit project integration

Required scopes:
- canonical/global;
- Command Center project;
- role;
- task;
- scratch;
- durable learning.

Prototype fixture data must never enter durable memory.

---

## MRTKZ-019 — Android security lifecycle needs a session-renewal design

Current Owner session maximum:
60 minutes.

This is a good security limit.

But the mobile product needs:
- safe renewal;
- revoked-device behavior;
- notification delivery separate from command bearer;
- offline/stale review behavior.

Do not solve this with a long-lived universal bearer token.

---

## MRTKZ-020 — Critical mobile actions should be typed commands

For:
- approve;
- reject;
- pause;
- resume;
- switch fallback;
- publish/deploy gate

prefer typed semantic intent over ambiguous free-text instruction.

Free-text remains useful for:
- Ask;
- comment;
- requested change explanation.

---

## MRTKZ-021 — Media preview/storage contract is missing

Android requires:
- thumbnail;
- proxy video;
- image preview;
- before/after;
- optional full stream.

Need:
- size limits;
- cache policy;
- retention;
- encryption/storage;
- redaction;
- deletion;
- project access boundary.

---

## MRTKZ-022 — Accessibility needs executable acceptance, not only design rules

Living Operations already requires:
- keyboard;
- focus;
- non-color state;
- Reduced Motion;
- Android target size.

Add future test/capture evidence for:
- tab order;
- screen-reader/accessibility labels where feasible;
- high DPI;
- 1366×768;
- 125/150%;
- Reduced Motion parity.

---

## MRTKZ-023 — Motion performance must become measurable

Set a real benchmark later:
- frame responsiveness;
- maximum active animated objects;
- Filmstrip virtualization;
- thumbnail cache;
- video proxy;
- no high-frequency background loops.

Visual beauty cannot override responsiveness.

---

## MRTKZ-024 — Tool Dock truth source needs one canonical registry

Tool Dock should not assemble state from decorative configuration.

Each tool needs:
- installed/known;
- connected;
- authorized;
- active;
- blocked;
- unknown;
- last verified.

Examples currently include providers that are:
DESIGN_ONLY, NOT_CONNECTED, BLOCKED or OBSERVE_ONLY.

The UI must show those exact truths.

---

# 6. Interface review

## Current WPF

Verdict:
**HISTORICALLY CORRECT FOR STAGE 7 / NOT SUITABLE AS FINAL PRODUCT SHELL**

Reasons:
- status-first;
- Stage 7 specific;
- long diagnostic page;
- rail is intentionally noninteractive;
- generic Council/Studio presentation;
- no command composer;
- no Project-first hierarchy;
- no Pulse;
- no Decision Stack;
- no Filmstrip;
- no real interactive Sigils;
- no motion system.

Recommendation:

Do not "skin" this page into Living Operations.

Use P1 as a new vertical slice while preserving the current surface as:
`System / Legacy Stage Evidence`
or equivalent advanced diagnostics.

---

# 7. Living Operations review

Verdict:
**ACCEPT**

Strengths:
- highly distinctive;
- animation has operational meaning;
- project is primary;
- semantic colors;
- Interactive Semantic Objects;
- Reduced Motion;
- evidence-aware;
- Android semantics intentionally differ from desktop layout.

Conditions:
- never animate nonexistent activity;
- no role animation unless role state exists;
- no verified stamp without evidence;
- no decorative tool readiness;
- no fork/recovery visual that outruns runtime truth.

---

# 8. Autopilot review

Verdict:
**APPROVE ARCHITECTURE DIRECTION / RUNTIME NOT READY**

Correct concepts:
- No Project Timeout;
- bounded Action Timeout;
- durable resume;
- Autonomy Envelope;
- pre-approved fallback;
- Supervisor;
- budgets;
- recovery;
- Owner escalation;
- INTERNAL COMPLETE before external effect by default.

Must add:
- Project Store;
- Flight Recorder;
- Tool Effect Ledger;
- durable scheduler;
- recovery policy;
- typed Owner gates;
- trigger engine;
- rehearsal mode.

---

# 9. Android review

Verdict:
**STRONG PRODUCT FIT / NOT YET CONNECTED**

Correct product role:
- monitor;
- preview;
- decide;
- respond.

Do not make it:
- mini Windows app;
- unrestricted remote desktop;
- authority host.

Priority mobile surfaces:
1. Home.
2. Pulse.
3. Projects.
4. Decisions.
5. More/System.
6. Media Review.
7. Autopilot Detail.
8. Evidence.

---

# 10. Remote Owner / Tailnet review

Verdict:
**SECURITY DIRECTION PASS / REAL-HOST EVIDENCE STILL PENDING**

Known current truth:
- device enrolled: false;
- active session: false;
- phone round trip: false;
- Tailscale installation: UNKNOWN;
- Tailscale connection: UNKNOWN;
- Serve: NOT_CONFIGURED;
- real host transport deployment: false;
- live execution: false.

Do not use concept UI to imply otherwise.

---

# 11. Model policy review

Verdict:
**PASS DIRECTION**

Keep four independent controls:

1. Model.
2. Reasoning Effort.
3. Autonomy.
4. Fallback.

Do not merge them.

Required future provider capability mapping:
`FAST / STANDARD / DEEP / MAX`
-> provider/model-specific supported effort.

No silent coercion.

---

# 12. المرتكز governance review

Verdict:
**PASS**

The local overlay is justified.

Names:
- المرتكز;
- هيئة المرتكز;
- مشغل المرتكز.

Parent systems remain untouched.

However, runtime/project projections must later consume the local profiles where project-specific governance is shown.

---

# 13. Pre-Prototype Gate

Before P1 starts, close these alignment items:

### MP-01 — Murtakaz naming lock
Status:
DONE by project-local identity contract.

### MP-02 — Murtakaz orchestration projection spec
Status:
REQUIRED.

### MP-03 — Canonical Stage/Phase map
Status:
REQUIRED.

### MP-04 — Stage 7 CI projection truth repair plan
Status:
REQUIRED.

### MP-05 — P1 fixture isolation
Status:
SPECIFIED; CI guard should be added before/with P1.

### MP-06 — No Dead Surface prototype requirement
Status:
SPECIFIED.

## Gate decision

`P1_NON_AUTHORITATIVE_PROTOTYPE = CONDITIONAL_GO`

Start only after MP-02, MP-03 and MP-04 are documented/validated.

This is intentionally much lighter than implementing real Autopilot first.

---

# 14. Recommended implementation order after the gate

1. Generate Murtakaz project orchestration projection.
2. Reconcile Stage/Phase naming.
3. Repair Stage 7 CI-vs-host projection semantics.
4. P1 Windows Living Project Workspace prototype.
5. المرتكز review of P1.
6. Android companion prototype.
7. Cross-platform semantic event proof.
8. Project Store contract.
9. Durable Autopilot engine foundations.
10. Flight Recorder + Tool Effect Ledger.
11. Notification Broker.
12. Provider/model/reasoning capability registry.
13. Pulse runtime.
14. Evals/role-version registry.
15. Sandbox/rehearsal/trigger engine.
16. real host + phone evidence gates.
17. only then consider later authority/release stages.

---

# 15. Things explicitly NOT recommended

The المرتكز rejects:

- rewriting parent Universal Council for this project;
- rewriting Media Studio for this project;
- opening Stage 8 because the UI looks ready;
- connecting live execution to make the prototype impressive;
- showing Tailscale/phone as connected without evidence;
- using the old WPF rail as if it were functional navigation;
- implementing every screen at once;
- making animations before semantic events;
- creating one giant "AI agent" with implicit authority;
- allowing silent model fallback;
- treating Android approval as server authorization;
- using long-lived bearer credentials to simplify mobile UX;
- storing project truth only in conversation history.

---

# 16. Final statement

The current program has a strong secure skeleton and a much stronger product direction than the Stage 1–7 shell visually suggests.

The central task is now **alignment**, not invention.

The program should move from:

`read-only staged control surface`

to:

`durable project operating system with truthful living UI`

without losing the safety properties already achieved.

The المرتكز recommends:

**PRESERVE THE BACKEND BOUNDARIES. REPLACE THE PRODUCT SURFACE. ADD DURABLE PROJECT STATE BEFORE REAL AUTOPILOT.**

