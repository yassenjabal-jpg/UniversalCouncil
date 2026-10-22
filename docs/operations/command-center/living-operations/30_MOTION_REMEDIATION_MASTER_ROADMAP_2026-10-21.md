# Command Center — Motion System Final Remediation Roadmap
## المرتكز + مشغل المرتكز — الخطة الشاملة لإغلاق مشكلة الحركة نهائيًا

Date: 2026-10-21  
Status: GOVERNING REMEDIATION ROADMAP  
Roadmap ID: `CC-MOTION-REMEDIATION-MASTER-ROADMAP-2026-10-21`  
Owner trigger: visual rejection of the prior P1 motion video  
Working branch: `command-center/motion-visibility-remediation-20261021`  
Current PR: #72 — DRAFT / MUST NOT MERGE YET

---

## 1. Joint Murtakaz + Studio verdict

The problem is not "there are too few animations."

The confirmed failure is a three-layer gap:

1. **Specification gap at implementation time** — the Motion Bible and storyboard specify richer semantic motion than the code implements.
2. **Evidence gap** — the original 6 FPS capture proved state changes but was too weak to prove visible animation quality.
3. **Acceptance gap** — automated green checks were allowed to stand in for human perceptual motion review.

The repair must close all three.

### Final design principle

> **At rest, the product is almost still. When meaningful work changes state, motion makes the change immediately understandable.**

Motion is allowed only for:
- navigation;
- state transition;
- ownership/routing;
- handoff/return;
- decision focus;
- recovery;
- fork/branching;
- verified completion;
- direct interaction feedback.

Decorative-only motion remains forbidden.

---

## 2. Protected truth — never changed by this roadmap

Throughout every wave:

- authoritative delivery stage remains `STAGE_7`;
- Stage 8 remains `NOT_OPENED`;
- runtime authority remains false;
- live execution remains false;
- real-host gates remain evidence-driven;
- UNKNOWN never becomes SUCCESS because of animation;
- prototype motion never becomes runtime truth;
- the approved visual identity and eight canonical screens remain locked;
- no redesign of the product shell is authorized by this roadmap.

---

## 3. Acceptance model — four independent passes required

No motion phase can be accepted from one metric alone.

### A. Semantic completeness
Every required motion maps to:
- a real semantic object;
- an explicit state/event;
- an allowed start state;
- an allowed end state;
- a stop/cancel condition;
- a Reduced Motion equivalent.

### B. Human perceptual legibility
A reviewer must be able to watch the exact-head capture and understand:
- what changed;
- where work moved;
- which object became active;
- whether the flow stopped, returned, recovered, forked, or completed.

Metrics are diagnostic only. They cannot override a visible failure.

### C. Technical quality
Motion must:
- remain bounded;
- use transform/opacity/geometry where practical;
- stay inside the Motion Bible timing classes;
- avoid permanent high-frequency animation;
- avoid layout-jank-heavy width/height animation;
- preserve keyboard/focus behavior;
- preserve responsiveness.

### D. Truth + accessibility
Motion must:
- never fabricate execution, success, recovery or completion;
- preserve all meaning in Reduced Motion;
- preserve text/icon/color/position state;
- not make critical actions gesture-only;
- not rely on color or motion alone.

---

# WAVE 0 — Truth Reset + Acceptance Repair
## Goal: repair the process before adding more animation

### W0.1 — Formal Return + Baseline Freeze
Owner: Studio Producer  
Review: Visual QA + Product Truth

Actions:
- formally retain the owner rejection as a Return Ticket;
- freeze PR #72 as a remediation laboratory, not an accepted solution;
- record current implementation coverage versus Motion Bible;
- mark all unimplemented storyboard motions explicitly;
- preserve the current canonical visual baseline.

Deliverables:
- Return Ticket;
- motion implementation inventory;
- accepted visual baseline reference set.

Gate:
`MOTION_RETURN_BASELINE_LOCK`

### W0.2 — Storyboard-to-Code Coverage Contract
Owner: Motion Systems Director  
Review: Interaction Director + Windows Lead + Product Truth

Build one authoritative matrix:

`semantic event -> object -> screen -> full motion -> reduced motion -> code path -> evidence step`

Required signature events:
1. Role Activation;
2. Artifact Handoff / Return;
3. Owner Decision Focus;
4. Recovery;
5. Fork;
6. Verified Project Completion.

Secondary required motion:
- screen entry/exit;
- drawer/sheet;
- Filmstrip update;
- Pulse reveal;
- direct interaction feedback.

Gate rule:
100% of required signature events must have an implementation contract before later waves are considered complete.

Gate:
`MOTION_COVERAGE_CONTRACT_LOCK`

### W0.3 — Evidence System Reset
Owner: Prototype & Interaction Engineer  
Review: Visual QA + Murtakaz Evidence

Requirements:
- exact-head WPF capture;
- 30 FPS owner-review capture target;
- CI floor must never be below 20 FPS;
- 1440×900 primary desktop evidence;
- separate Full Motion and Reduced Motion captures;
- no optical-flow/frame interpolation;
- no post-produced animation;
- no concept video as acceptance evidence;
- motion visibility metrics recorded;
- semantic event timestamps recorded;
- raw frames/video hash-bound to candidate SHA.

Critical anti-gaming rule:

**No threshold may be lowered to make a candidate pass after owner-visible rejection.**

Gate:
`MOTION_EVIDENCE_PIPELINE_LOCK`

---

# WAVE 1 — Navigation + Activation Motion
## Goal: make ordinary interaction visibly coherent before signature workflow events

### W1.1 — Eight-Screen Navigation Choreography
Owner: Motion Systems Director + Windows Experience Lead

Scope:
all eight canonical screens.

Implement:
- meaningful entrance/exit direction;
- hierarchy-preserving transitions;
- no generic "everything zooms" template;
- screen-specific movement only where it communicates destination/context;
- no navigation transition longer than its semantic class without justification.

Acceptance:
a screen change must visually read as navigation rather than an instantaneous state swap.

### W1.2 — Role Activation + Routing
Owner: Interaction Choreography Director

Sequence:
`Project Core fixed -> connection route -> relevant Sigil activation -> contextual state`

Rules:
- only participating roles activate;
- no whole-council theater;
- role activation must remain inspectable;
- unknown/idle roles remain quiet.

Acceptance:
the reviewer can identify which role was activated and where routing came from without explanatory narration.

### W1.3 — Decision / Drawer / Focus Motion
Owner: Interaction Director + Experience Architect

Implement:
- drawer/sheet motion;
- Decision Mode hierarchy shift;
- background de-emphasis;
- decision card primary focus;
- evidence/dissent paths remain legible;
- explicit return to project context.

Gate:
`NAVIGATION_ACTIVATION_MOTION_ACCEPTED`

Required evidence:
Full Motion + Reduced Motion capture for W1 exact head.

---

# WAVE 2 — Living Workflow Motion
## Goal: make the product feel operationally alive, not merely animated

### W2.1 — Autopilot Current
Owner: Motion Systems Director  
Review: Durable Autopilot + Product Truth

States:
- READY;
- RUNNING fixture only when explicitly labeled;
- WAITING_OWNER;
- BLOCKED;
- RECOVERING;
- PAUSED;
- COMPLETE;
- UNKNOWN.

Core law:
flow stops when state stops.
No permanent "busy" motion for UNKNOWN.

### W2.2 — Artifact Handoff + Return
Owner: Motion Systems Director + Interaction Director

Canonical sequence:
`source highlight -> artifact detach -> short semantic route -> destination highlight -> accept/return state`

Return sequence:
`RETURN -> reverse route -> source regains artifact -> Return Ticket becomes inspectable`

Acceptance:
the viewer can tell who handed what to whom and whether it was accepted or returned.

### W2.3 — Filmstrip + Pulse + Story-to-Action
Owner: Experience Architect + Interaction Director

Implement:
- new Filmstrip version entry;
- before/after continuity;
- Pulse reveal;
- Pulse-to-task/decision/research semantic transfer;
- source Pulse remains traceable.

Gate:
`LIVING_WORKFLOW_MOTION_ACCEPTED`

---

# WAVE 3 — Signature UniversalCouncil Motion
## Goal: implement the motions that visually define the product

### W3.1 — Recovery
Owner: Motion Systems Director  
Review: Durable Autopilot + Product Truth + UX

Sequence:
1. current flow stops;
2. current work de-emphasizes;
3. last verified checkpoint receives focus;
4. bounded rewind cue;
5. restored state remains pending;
6. only verified restore may settle as success.

Forbidden:
- error flash standing in for recovery;
- success animation before verification.

### W3.2 — Fork / Branch
Owner: Motion Systems Director + Interaction Director

Sequence:
1. checkpoint selected;
2. source rail pauses;
3. branch line grows;
4. A/B identities appear;
5. original remains visible;
6. compare mode establishes equal visual weight;
7. selection settles only after explicit decision.

Fork is a signature motion and must not look like a decorative flourish.

### W3.3 — Verified Completion + Work Receipt
Owner: Motion Systems Director + Visual Systems Director

Sequence:
1. remaining verified stages settle;
2. artifacts gather;
3. active motion stops;
4. Work Receipt becomes primary;
5. one restrained completion cue;
6. next action appears.

Forbidden:
- confetti;
- celebration loops;
- completion before verified event.

Gate:
`SIGNATURE_MOTION_ACCEPTED`

Owner visual review is mandatory at this gate.

---

# WAVE 4 — Reduced Motion + Performance + Platform Assurance
## Goal: make motion safe, accessible and technically sustainable

### W4.1 — Reduced Motion Semantic Parity
Owner: Accessibility Reviewer + Motion Director

Replace travel with:
- source focus;
- direct crossfade;
- destination focus;
- explicit final state.

Required:
every M3/M4 motion has a Reduced Motion equivalent.

### W4.2 — Windows Performance + Input Assurance
Owner: Windows Experience Lead + Design Systems Engineer

Check:
- primary interaction target: 60 FPS where target hardware allows;
- no permanent high-frequency canvas animation;
- no layout-jank-heavy motion;
- no focus loss;
- keyboard parity;
- DPI/resolution behavior;
- cancellation/interruption safety.

Real YASSIN performance evidence remains pending until Stage 7 host access exists.

### W4.3 — Android Semantic Parity
Owner: Android Experience Lead + Cross-platform review

Share:
- object/event identity;
- state meaning;
- truth labels;
- decision semantics.

Do not force identical:
- distances;
- hover behavior;
- desktop composition.

Gate:
`MOTION_ACCESSIBILITY_PERFORMANCE_PARITY_ACCEPTED`

---

# WAVE 5 — Evidence + Anti-False-Positive Hardening
## Goal: make it impossible to "pass" motion that the owner cannot actually see

### W5.1 — Exact-Head Motion Capture
Owner: Prototype Engineer

Evidence set:
- Full Motion 30 FPS target;
- Reduced Motion 30 FPS target;
- screen/event timeline;
- SHA256 manifests;
- candidate SHA;
- no editing/interpolation;
- optional diagnostic overlay stored separately from clean capture.

### W5.2 — Automated Motion Diagnostics
Owner: Prototype Engineer + Visual QA

Measure:
- changed-frame count;
- longest continuous motion run;
- number of independent motion events;
- event-to-frame coverage;
- storyboard-to-code coverage;
- full/reduced semantic parity;
- forbidden unbounded patterns.

Important:
metrics may reject.
Metrics may **not alone approve**.

### W5.3 — Human Perceptual Review
Owners:
- Motion Systems Director;
- Interaction Director;
- Visual QA;
- Owner.

Review protocol:
1. watch clean video once without implementation notes;
2. identify what changed at each signature event;
3. check whether motion explains operational meaning;
4. check whether any animation feels decorative;
5. compare Full vs Reduced Motion;
6. reject if the product still feels like static slides with effects.

Owner-visible rejection overrides numeric pass.

Gate:
`OWNER_VISIBLE_MOTION_EVIDENCE_ACCEPTED`

---

# WAVE 6 — Final System Lock + Integration
## Goal: close the defect permanently and prevent regression

### W6.1 — Eight-Screen Regression Audit
Review:
- all 8 canonical screens;
- all clickable surfaces;
- all signature events;
- no-dead-surface law;
- no visual identity drift;
- no truth inflation;
- Full/Reduced parity.

### W6.2 — Joint Murtakaz + Studio Final Review
Required clearances:
- Motion;
- Interaction;
- Visual QA;
- Accessibility;
- Product Truth;
- Durable Autopilot for recovery/autopilot;
- Architecture/Windows where performance is material.

Outcome must be:
`APPROVED_BY_AL_MURTAKAZ`

No lesser status may merge.

### W6.3 — Merge + Permanent Regression Gates
Actions:
- merge only exact-head approved tree;
- verify merge tree equals candidate tree;
- update Motion Bible implementation coverage;
- retain motion visibility tests in Stage 0/P1 gates;
- retain human owner-review requirement for future signature-motion changes;
- close Return Ticket only after merge evidence;
- preserve Stage 7 / Stage 8 truth.

Final gate:
`MOTION_SYSTEM_LOCKED`

---

## 4. Responsibility map

| Concern | Craft owner | Required reviewer |
|---|---|---|
| Navigation/focus | Experience Architect | UX / Visual QA |
| Click/tap behavior | Interaction Director | UX / Product Truth |
| Visual identity | Visual Systems Director | Visual QA |
| Motion language | Motion Systems Director | Interaction / Accessibility |
| WPF implementation | Windows Lead | Architecture / QA |
| Prototype capture | Prototype Engineer | Visual QA / Evidence |
| Reduced Motion | Accessibility Reviewer | Motion / UX |
| Recovery/Autopilot | Motion Director | Durable Autopilot / Product Truth |
| Truth-bearing animation | Studio | Product Truth |
| Final acceptance | Al-Murtakaz | Owner final authority |

---

## 5. Permanent anti-regression laws

1. **Storyboard != implementation.** Coverage must be proven.
2. **State change != animation quality.** Video proof is required.
3. **Metrics != human acceptance.** Metrics can reject but cannot overrule visible failure.
4. **No threshold gaming.** Do not lower acceptance thresholds to rescue a candidate.
5. **No filler motion.** Added motion must map to a semantic event/object.
6. **At-rest quietness.** Idle/unknown surfaces do not continuously animate.
7. **Truth before motion.** Animation never creates success/active/connected truth.
8. **Reduced Motion parity is mandatory.**
9. **Exact-head evidence only.**
10. **No post-produced acceptance evidence.**
11. **Owner visual rejection reopens the gate automatically.**
12. **No merge of a motion-heavy change without Motion + Visual QA + Accessibility review.**

---

## 6. Current position

Current PR #72 is classified as:

`WAVE_0 / IMPLEMENTATION_EXPERIMENT — NOT FINAL`

Current known result:
- Stage 0: PASS;
- CodeQL: PASS;
- Stage 7: PASS;
- Reference UI: PASS;
- WPF recorder: produced evidence;
- prior exact-head P1 final evidence gate: FAIL;
- owner motion acceptance: FAIL / reopened.

Therefore:

**Do not merge PR #72 until this roadmap reaches Wave 6.**

---

## 7. Definition of done

The motion problem is considered permanently solved only when all are true:

- all six signature motion families are implemented;
- all six are event/object backed;
- all eight canonical screens preserve visual fidelity;
- Full Motion is clearly visible in an exact-head owner-review video;
- Reduced Motion preserves all operational meaning;
- automated diagnostics pass without lowered thresholds;
- performance/focus/input checks pass;
- Product Truth finds no fabricated activity;
- Owner accepts the visual result;
- Al-Murtakaz issues final approval;
- exact approved candidate tree is merged;
- permanent regression gates remain active.

Until then, motion status remains:

`RETURN_TO_STUDIO / REMEDIATION_ACTIVE`.
