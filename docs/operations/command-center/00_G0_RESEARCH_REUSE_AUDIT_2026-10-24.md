# UniversalCouncil / المرتكز — G0 Research / Reuse Audit
## RESEARCH / REUSE BEFORE BUILD — 2026-10-24

Status: **G0 EVIDENCE COMPLETE FOR PRESENTATION-2 ARCHITECTURE DECISION**
Source pin: `origin/main@65d92a6abcfbc103fd3da9b444320da300853364`
Working branch: `command-center/g0-research-reuse-gate-20261024`

> Governing law: **SEARCH → STUDY → COMPARE → REUSE → INTEGRATE → ADAPT → BUILD LAST.**

This audit records the evidence required before Presentation 2.0 or motion-native implementation. It does not authorize Stage 8, live provider execution, or merging the existing Motion PR stack.

## 1. Problem statement

The durable backend/governance foundation is valuable, but the current presentation anatomy is hostile to scalable motion-native interaction:

- WPF presentation is concentrated in a very large MainWindow XAML/code-behind surface.
- important visual objects are mostly static glyphs/paths/images rather than first-class stateful components.
- MP4 proved capture/timing/overlay rendering, not that real product objects are stateful, clickable, function-backed and internally animated.
- owner review rejected the result as a slide-show experience.
- the target is a motion-native operational control surface whose motion reflects truthful semantic state.

Protected:
- Company Kernel remains canonical operational truth.
- ApprovedGateway remains the sanctioned controlled-execution boundary.
- Role != Model.
- no silent fallback.
- UNKNOWN != SUCCESS.
- generated output cannot self-promote to canonical.
- frontend and renderers never own product authority.

## 2. Reuse found inside UniversalCouncil

Before creating any new research/reuse subsystem, the existing Technology & Capability Scout was inspected:

- `company/runtime/capability_scout.py`
- `company/config/capability_scouting.json`
- `docs/decisions/ADR-0002-hr-proactive-capability-scouting.md`
- `skills/universal-council/SKILL.md`
- `company/PEOPLE_AND_CAPABILITY.md`

It already supports capability-gap triggers, official-doc research, GitHub/open-source inspection, community research, maintenance/license/security/permission checks, rollback/sandbox criteria, version pinning and downstream governance gates.

**G0 decision: ADAPT.**
Upgrade this existing mechanism into the mandatory G0 gate. Do not create a second G0 engine.

## 3. Presentation decision evidence

### WPF-only rebuild
**Decision: REJECT for the full Presentation 2.0; ADAPT as thin shell.**

Reason:
- mature existing Windows host;
- official WebView2 WPF support;
- keeping the shell avoids premature native migration;
- full WPF rebuild would require more custom vector/motion/interaction infrastructure.

### Immediate WinUI 3 migration
**Decision: REJECT NOW.**

Reason:
- Composition is strong, but shell migration does not solve stateful-vector authoring;
- current WinUI RTL issue history still requires care;
- adds work before proving owner-visible value.

Retain as a later replaceable shell option.

### Avalonia / Uno
**Decision: REJECT for the first wave.**

Reason:
- cross-platform pixel parity is not currently required;
- Android requires semantic parity, not an identical desktop UI;
- current Avalonia issue history includes Arabic/RTL text/caret and Windows accessibility concerns;
- migration precedes the vertical proof.

### WebView2 + local React/TypeScript
**Decision: ADOPT for P1 and Presentation 2.0.**

Evidence:
- officially supported from WPF and WinUI;
- same CoreWebView2 platform under the wrappers;
- typed host/web messaging is available;
- OpenHands demonstrates a React/TypeScript control surface separated from execution authority;
- strong ecosystem for SVG motion, accessibility, graphs, testing and virtualization.

Known risks reviewed:
- WebView2 issue history includes memory, freeze, renderer and crash reports;
- web surface must be treated as untrusted;
- event/lifecycle cleanup is mandatory;
- runtime availability/version must be checked;
- external navigation and generic host-object exposure are forbidden.

## 4. Motion/component adoption matrix

| Need | Candidate | G0 decision | Constraint |
|---|---|---|---|
| Default semantic motion | Motion + SVG | **ADOPT** | no decorative loops |
| Complex stateful vector | Rive React | **PILOT / ADAPT** | selective use; lifecycle/perf proof |
| Finite authored animation | Lottie | **PILOT** | never product-state engine |
| Specialized 2D | SkiaSharp | **ADAPT** | not overlay-only proof |
| Accessibility/keyboard/RTL | React Aria | **ADOPT** | virtualize large collections |
| Long lists/logs | TanStack Virtual | **ADOPT when needed** | UI optimization only |
| Local visual state machine | XState | **ADAPT optional** | never product truth |
| Routes/forks | React Flow / xyflow | **ADAPT** | bounded graph size |
| Auto layout | ELK.js | **PILOT** | license/packaging review |
| Component lab | Storybook | **ADOPT/PILOT** | bounded tooling overhead |
| Browser E2E/evidence | Playwright | **ADOPT** | stable environment baselines |

### Rive failure-first evidence
Recent runtime history includes fixes for canvas backing-store release on unmount and React strict-mode/zero-size canvas behavior. Community issue history includes repeated-remount lag reports.

Rule: simple icons remain SVG/Motion; Rive is for genuinely complex authored state machines only.

### React Flow failure-first evidence
Issue/discussion history includes:
- very-large-graph lag;
- virtualization/spatial-query work;
- large minimap degradation;
- memory/re-render concerns.

Rule: use for bounded owner-visible routes/forks/checkpoints. Never use it as the durable project store or a 10k-node global canvas.

## 5. Testing/evidence reuse

### Playwright — ADOPT
Use for:
- component/screen interaction;
- semantic object assertions;
- Reduced Motion paths;
- screenshots and reproducible browser-side evidence.

### Storybook — ADOPT/PILOT
Use as the isolated component-state catalogue before eight-screen expansion.

Evidence law:
- global pixel-change metrics may reject obvious failures;
- metrics may never approve owner motion quality;
- semantic object IDs, region/object evidence, real interaction and owner perceptual review are mandatory.

## 6. Future Job Engine / Automation G0

G0 applies to backend workflow work too.

### Elsa Workflows
**Decision: PILOT / ADAPT.**

Useful existing capabilities:
- embeddable .NET runtime;
- long-running persistence;
- bookmarks / pause / resume;
- human/external-event waiting;
- execution logs and incidents;
- cancellation/resume;
- SQLite suitability for a local single-instance deployment;
- optional scheduler/distributed scale-up paths.

Authority boundary:
- Elsa may orchestrate workflow timing/state.
- Elsa may not authorize controlled external effects.
- controlled operations still converge through Application services / ApprovedGateway.
- Company Kernel remains canonical for grants, budgets, obligations and evidence.
- Tool Effect Ledger remains UniversalCouncil-owned.

### Temporal
**Decision: RESEARCH / reserve scale-up option.**

Strength: durable event history/replay.
Cost: separate Temporal Service/Cloud adds operational complexity for the current Windows-first local product.

### Durable Task / Dapr Workflow / Hangfire
**Decision: REJECT as immediate primary foundation; retain as references.**

## 7. Similar-product patterns

### OpenHands
Borrow:
- React/TypeScript control surface;
- backend owns actual execution;
- browser client cannot self-authorize effects;
- automation separated from interactive UI.

### Temporal-style systems
Borrow:
- inspectable history;
- failure location;
- replay/recovery thinking.

### n8n / Dify / Langflow
Borrow:
- run visibility;
- model/tool catalog patterns;
- workflow inspection.

Do not copy:
- generic node-dashboard visuals;
- licensing assumptions;
- authority models.

## 8. Final G0 decisions

| Area | Decision |
|---|---|
| G0 enforcement | **ADAPT existing Technology & Capability Scout** |
| Windows shell | **ADAPT current WPF into thin shell** |
| Main presentation | **ADOPT local React + TypeScript + WebView2** |
| Default motion | **ADOPT Motion + SVG** |
| Complex stateful vectors | **PILOT Rive React** |
| Finite authored animation | **PILOT Lottie** |
| Specialized custom 2D | **ADAPT SkiaSharp** |
| Accessibility/RTL primitives | **ADOPT React Aria** |
| Long-list virtualization | **ADOPT TanStack Virtual when required** |
| Local visual-state coordination | **ADAPT XState optionally** |
| Routes/forks | **ADAPT React Flow** |
| Auto layout | **PILOT ELK.js only if needed** |
| E2E/visual interaction evidence | **ADOPT Playwright** |
| Component laboratory | **ADOPT/PILOT Storybook** |
| Durable Job/Automation runtime | **PILOT/ADAPT Elsa Workflows** |
| Immediate WinUI migration | **REJECT NOW** |
| Immediate Avalonia/Uno migration | **REJECT NOW** |
| Full WPF presentation rebuild | **REJECT** |

## 9. Custom-code budget

Build only UniversalCouncil-specific semantics/integration:
- typed .NET ↔ presentation message contracts;
- projections/commands;
- ApprovedGateway-facing adapters;
- design tokens/components derived from the eight canonical references;
- MotionKit semantic adapters;
- object-level motion/evidence telemetry;
- project-specific Work Receipt / Evidence / Decision views.

Do not build:
- vector engine;
- generic animation timeline engine;
- graph engine;
- accessibility framework;
- generic virtualization;
- generic browser automation;
- generic durable workflow engine before Elsa pilot outcome;
- capture stack as a prerequisite to the product proof.

## 10. G0 exit

Presentation 2.0 may advance to P0 because:
- official/runtime options were reviewed;
- open-source candidates were compared;
- practitioner/issue failure modes were inspected;
- existing internal overlap was found;
- custom-build scope was reduced;
- replacement/rollback boundaries are explicit.

Next gate: **P0 — Presentation 2.0 Architecture Lock**.

No eight-screen rollout may begin before the single P1 vertical proof is owner-accepted.
