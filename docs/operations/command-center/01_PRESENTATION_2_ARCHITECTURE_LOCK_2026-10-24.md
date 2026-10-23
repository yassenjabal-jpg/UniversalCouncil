# UniversalCouncil Command Center — Presentation 2.0 Architecture Lock
## P0 Architecture Decision — 2026-10-24

Status: **P0 LOCK CANDIDATE — IMPLEMENTATION LIMITED TO P1 VERTICAL PROOF**
G0 evidence: `00_G0_RESEARCH_REUSE_AUDIT_2026-10-24.md`
Source baseline: `origin/main@65d92a6abcfbc103fd3da9b444320da300853364`

This lock preserves UniversalCouncil's durable engine and replaces the owner-facing presentation strategy. It does not open Stage 8, enable live provider execution, or merge PRs #72/#80/#81/#82/#83/#84.

---

## 1. Executive decision

Do **not** rewrite UniversalCouncil.

Preserve:
- Company Kernel;
- ApprovedGateway;
- Context Resolver / Context Capsules / Change Envelopes;
- Routing Coordinator;
- Capability Registry;
- Model Broker;
- Role != Model;
- explicit model/provider selection;
- no silent fallback;
- evidence and UNKNOWN_OUTCOME semantics;
- Stage/governance truth;
- MotionKit semantic concepts;
- Reduced Motion semantics.

Rebuild:
- owner-facing presentation/component anatomy;
- interaction model;
- semantic visual-object system;
- frontend state/projection boundary;
- motion evidence acceptance.

Initial implementation architecture:

```text
Windows
┌──────────────────────────────────────────────┐
│ Existing .NET 10 WPF executable             │
│ becomes THIN SHELL                          │
│ - window/lifecycle                          │
│ - WebView2 host                             │
│ - native emergency/fallback surface         │
│ - bounded native dialogs                    │
└───────────────────┬──────────────────────────┘
                    │ secure typed messages
                    ▼
┌──────────────────────────────────────────────┐
│ Presentation 2.0 — local packaged web UI    │
│ React + TypeScript                          │
│ - screens                                   │
│ - semantic components                       │
│ - design tokens                             │
│ - Motion/SVG                                │
│ - optional Rive adapters                    │
│ - bounded React Flow surfaces               │
│ - React Aria accessibility primitives       │
└───────────────────┬──────────────────────────┘
                    │ command/projection DTOs
                    ▼
┌──────────────────────────────────────────────┐
│ Application Boundary / ApprovedGateway      │
│ NO authority moves into the web UI          │
└───────────────────┬──────────────────────────┘
                    ▼
┌──────────────────────────────────────────────┐
│ Company Kernel / durable state / evidence   │
└───────────────────┬──────────────────────────┘
                    ▼
              Tools / Providers
```

The WPF shell is replaceable later. The React presentation must not depend on WPF-specific business logic.

---

## 2. Authority law

Presentation 2.0 is a front door, never an authority owner.

Frontend MAY:
- display read-only authoritative projections;
- maintain ephemeral interaction state;
- send typed command requests;
- display ACCEPTED / REJECTED / UNKNOWN results;
- animate truthful semantic state;
- open inspectors and evidence context.

Frontend MUST NOT:
- call providers directly;
- execute tools directly;
- change grants/budgets/authority;
- determine that an operation succeeded;
- convert UNKNOWN into SUCCESS;
- promote generated/working data to canonical;
- invent runtime activity to make the interface feel alive.

MotionKit MUST NOT:
- create product truth;
- authorize work;
- hide UNKNOWN;
- infer success from renderer completion.

---

## 3. State split

### 3.1 Authoritative projection state
Owned by backend/domain truth.

Examples:
- project/stage;
- active role;
- artifact;
- selected model/provider;
- tool capability;
- job state;
- evidence state;
- verification;
- checkpoint/fork;
- owner decision;
- recovery outcome.

Frontend treats this as immutable revisioned input.

### 3.2 Ephemeral presentation state
May live locally:
- hover;
- focus;
- pressed;
- inspector open;
- selected local tab;
- temporary drag preview;
- viewport/pan;
- disclosure state;
- animation progress.

Ephemeral state can never mutate backend truth by implication.

---

## 4. Typed bridge contract

Use a small versioned message protocol.

Conceptual request:

```text
CommandRequest
  protocolVersion
  requestId
  commandType
  targetId
  expectedRevision
  ownerIntentId
  payload
```

Conceptual result:

```text
CommandResult
  protocolVersion
  requestId
  status = ACCEPTED | REJECTED | UNKNOWN
  resultingRevision?
  reasonCode?
  receiptId?
  evidenceRefs[]
```

Projection:

```text
ProjectionEnvelope
  protocolVersion
  projectionType
  projectionId
  revision
  truthTimestamp
  payload
```

Security rules:
- local packaged origin only;
- block external top-level navigation by default;
- no generic reflection bridge;
- no arbitrary host objects;
- no JavaScript invoking arbitrary C# methods;
- validate every incoming message against an allowlisted schema;
- allowlist command types;
- enforce size limits;
- reject stale `expectedRevision`;
- shell stays non-elevated;
- do not expose credentials/tokens/environment through bridge;
- dispose event handlers/subscriptions deterministically;
- treat renderer/browser crash as presentation failure, never operation failure/success.

---

## 5. WebView2 lifecycle policy

Initial runtime policy:
- use supported Evergreen WebView2 Runtime;
- detect runtime availability/version on startup;
- all Presentation 2.0 application assets are packaged locally;
- no CDN dependency is required for the core interface;
- external links open through an explicit bounded host action, not arbitrary navigation;
- record renderer/process failures;
- support controlled presentation restart without corrupting backend work;
- never couple an active job lease to WebView2 process lifetime.

The owner must be able to lose/restart the UI without changing canonical work truth.

---

## 6. Component architecture

Every significant visual object is a component with:

```text
Semantic identity
+ authoritative state input
+ interaction contract
+ visual representation
+ motion mapping
+ real function
+ Reduced Motion equivalent
+ accessibility representation
```

Core component families:

### StatefulVectorIcon
For small functional icons. Default renderer: SVG + Motion.

### RoleSigil
Role identity plus operational state.
- simple states: SVG + Motion;
- complex authored state machine: optional Rive adapter after pilot proof.

### StateBadge
Explicit state/reason. Never motion-only.

### ReasoningRings
Only shown when real reasoning/model state exists.

### AutopilotCurrent
Truth mappings:
- RUNNING → restrained directional flow;
- WAITING_OWNER → flow reaches owner decision and stops;
- BLOCKED → forward motion stops at blocker;
- RECOVERING → bounded backward cue tied to actual recovery;
- UNKNOWN → no fake busy animation;
- COMPLETE → settle and rest.

### ArtifactObject
Stable artifact identity through handoff/return.

### SemanticRoute
A relationship between real source/destination semantic IDs.

### CheckpointNode
Verified checkpoint, not decorative milestone.

### ForkGraph
Preserves original path and shows A/B/N branches only when canonical fork state exists.

### EvidenceObject
Inspectable source/evidence object.

### ToolStatus
Tool/capability health and verified result.

### DecisionFocusCard
Owner decision with options/evidence/dissent/risk.

### WorkReceiptGatherer
Visual completion consumes actual verified receipt data.

---

## 7. Motion renderer policy

### Tier 1 — SVG + Motion
Default.

Use for:
- icons;
- sigils;
- status rings;
- badges;
- routes;
- progress/current markers;
- checkpoints;
- evidence objects;
- lightweight artifact motion.

### Tier 2 — Rive
Only when complexity justifies:
- internal vector rigs;
- multiple blended visual states;
- reusable artist-authored state machines.

Rive adoption requires the P1 bounded proof to validate:
- mount/unmount stability;
- repeated state changes;
- CPU/GPU/memory;
- keyboard/click wrapper;
- accessible alternate representation;
- Reduced Motion behavior.

### Tier 3 — Lottie
Finite authored sequence only. Not product state machine.

### Skia
Retained for specialized custom 2D/diagram/image tasks when profiling justifies it.
Not accepted as a temporary overlay used to claim the underlying UI is alive.

---

## 8. Accessibility and Arabic RTL

Arabic RTL is primary, not a later localization pass.

Requirements:
- root direction handled explicitly;
- use logical layout properties;
- keyboard navigation for every interactive semantic object;
- visible focus;
- screen-reader name/role/state;
- actionable canvas/Rive visuals have accessible DOM/control equivalents;
- state never communicated by color or motion alone;
- Reduced Motion preserves semantic meaning;
- text/layout tests include Arabic strings and mixed Arabic/Latin IDs;
- large collections are virtualized rather than degrading keyboard/accessibility behavior.

React Aria is the default reuse candidate for interaction primitives, not a bespoke accessibility framework.

---

## 9. MotionKit 2.0 role

Keep the semantic kernel idea; change its product integration.

```text
Product Truth
    ↓
Semantic Event
    ↓
Motion Contract
    ↓
Component Semantic State
    ↓
Renderer Adapter
    ├─ SvgMotion
    ├─ Rive
    ├─ Lottie
    └─ ReducedMotion
```

Minimum motion instance telemetry:

```text
motionInstanceId
semanticObjectId
eventId
truthRevision
sourceState
targetState
renderer
motionMode
startedAt
completedAt
interruptedBy?
```

Renderer completion can never promote business truth.

Existing MP1/MP2 concepts should be restacked/reused later; do not merge the current stacked Motion PRs as-is during this architecture wave.

---

## 10. Graph policy

React Flow may implement bounded owner-visible topology:
- current route;
- participating roles;
- artifact handoff;
- checkpoint/fork;
- small project history relationships.

Do not:
- load the entire organization/history into one graph;
- store canonical state in React Flow;
- route every pointer movement through backend/global state;
- use expensive continuous effects across hundreds of nodes.

Use:
- collapse/progressive disclosure;
- memoized nodes;
- bounded viewport;
- virtualization/alternative list detail where appropriate.

ELK.js may be piloted only if automatic layout is actually required.

---

## 11. Evidence 2.0

Old acceptance anti-pattern:
`changed pixels → green CI → assumed visual success`.

New gate:

### Layer A — semantic contract
Expected source/target state and semantic object ID.

### Layer B — component tests
Every required state has representation and Reduced Motion equivalent.

### Layer C — interaction proof
Interactive-looking object invokes a real function/context.

### Layer D — object/region evidence
Target semantic object visibly changed.

### Layer E — full-screen visual regression
Reference identity, layout, RTL, density.

### Layer F — clean video/live proof
No debug overlays.

### Layer G — owner perceptual acceptance
Owner can reject even when all metrics pass.

Metrics may reject. Metrics may not overrule owner perception.

---

## 12. P1 single vertical proof

No eight-screen build yet.

Target reference:
**02 — Living Project Workspace**

Required proof:

1. local React/TypeScript presentation hosted in the thin WPF shell;
2. one real `RoleSigil`;
3. internal vector motion — not parent-button scaling;
4. Rest;
5. Hover;
6. Focus;
7. Pressed;
8. Active;
9. Disabled or Unknown;
10. click opens real Role Context/Inspector;
11. one truthful status/current indicator;
12. one `ArtifactObject`;
13. one `SemanticRoute` or handoff if supported by truthful fixture/projection;
14. Full Motion;
15. Reduced Motion;
16. Arabic RTL;
17. keyboard operation;
18. accessible name/role/state;
19. repeated mount/state-cycle performance probe;
20. clean owner review video/live app.

P1 must be built with explicit fixture/reference truth if backend live execution is still off. Fixture state must be labeled as reference/test state.

### P1 stop rule
If owner judges the result still resembles static slides with effects:
- STOP;
- do not build more screens;
- return to G0 / architecture diagnosis.

---

## 13. P1 dependency budget

Default candidates:
- React;
- TypeScript;
- WebView2 WPF host;
- Motion;
- React Aria;
- Playwright.

Conditional:
- Rive only for the RoleSigil pilot if SVG/Motion cannot meet the required internal authored behavior;
- React Flow only if the proof genuinely requires graph interaction;
- Storybook if component-state review materially improves speed;
- XState only if local visual state complexity justifies it.

Do not install a dependency merely because it appears in the final architecture. Add it only when the current slice needs it.

---

## 14. PR disposition

No merge during this lock.

- PR #72: **SPLIT / SELECTIVE REUSE** — preserve valuable evidence/session/supervision changes independently.
- PR #80 MP0: **RESTACK concept**.
- PR #81 MP1: **KEEP + REFACTOR** semantic kernel.
- PR #82 MP2: **KEEP + REFACTOR** renderer boundary.
- PR #83 MP3: **ARCHIVE AS LAB / RESEARCH EVIDENCE**.
- PR #84 MP4: **SUPERSEDE as owner-facing direction**; retain capture/timing failure lessons and useful safeguards.

---

## 15. Future Job/Automation boundary

Do not build a bespoke durable Job Engine before an Elsa pilot.

Candidate architecture:

```text
Owner / Automation Trigger
        ↓
UniversalCouncil Application
        ↓
Workflow Runtime (Elsa candidate)
        ↓ requests typed controlled action
ApprovedGateway
        ↓
Company Kernel / Effect Adapter
        ↓
verified external effect
        ↓
Tool Effect Ledger + Evidence + Work Receipt
```

Elsa runtime state is not a substitute for Company Kernel business truth.

Temporal remains a future scale/reliability alternative if operational requirements justify its service footprint.

---

## 16. Migration sequence after P1 acceptance

P2 — Presentation foundation:
- local asset packaging;
- secure bridge;
- projection/command schemas;
- design token package;
- accessibility base;
- test harness.

P3 — component system:
- semantic components and state catalogue;
- Full/Reduced variants;
- reference matching.

P4 — read-only backend projections.

P5 — Screen Wave A:
- Home Owner Workspace;
- Living Project Workspace productionization.

Only after these should the remaining screen waves and durable workflow slices expand.

---

## 17. Hard stop conditions

Stop and return to G0 when:
- repeated trial-and-error starts;
- a new custom engine is proposed despite maintained alternatives;
- frontend begins owning business truth;
- a renderer begins authorizing or faking state;
- RTL/accessibility fails materially;
- WebView2 lifecycle instability threatens long-running use;
- owner sees static slides plus effects;
- capture engineering starts driving product architecture;
- a new dependency lacks license/maintenance/security evidence;
- custom code grows outside UniversalCouncil-specific semantics without justification.

---

## 18. Validation evidence

YASSIN validation on 2026-10-24:

- `python -m unittest company.tests.test_capability_scouting` → **8/8 PASS**.
- `python -m unittest company.tests.test_company_policy_config` → **3/3 PASS**.
- `python -m compileall -q company/runtime/capability_scout.py` → **PASS**.
- `python -m json.tool company/config/capability_scouting.json` → **PASS**.
- `git diff --check` → **PASS**.

Full company suite comparison:

- clean `origin/main@65d92a6`: **489 tests; 1 failure, 6 errors, 1 skipped**.
- G0 branch: **492 tests; 1 failure, 6 errors, 1 skipped**.

The same baseline failures reproduce on clean main:
- invalid published Memory event source;
- expired capability/evidence freshness assertions;
- one shared-controller lease reproduction failure.

Therefore G0 adds three passing tests and **introduces no new full-suite failure**. These baseline defects remain separate remediation work and must themselves pass G0 before modification.

## 19. P0 exit

P0 is complete when:
- G0 governance is enforced and tested;
- G0 research audit is committed;
- this architecture lock is committed;
- targeted policy tests are green;
- full-suite baseline comparison proves no new regression;
- branch/PR evidence exists.

Then the only allowed next product implementation is:
**P1 — one bounded vertical proof.**
