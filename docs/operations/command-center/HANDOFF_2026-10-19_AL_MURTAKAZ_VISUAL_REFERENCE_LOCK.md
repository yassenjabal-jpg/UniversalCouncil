# UniversalCouncil Command Center — MASTER HANDOFF
## المرتكز + Living Operations + Reference-Only Visual Lock

Date: 2026-10-19  
Purpose: Continue in a new conversation from the exact current state without relying on chat memory as source of truth.

---

# 0. SOURCE OF TRUTH — MANDATORY

Use this order:

1. Actual GitHub repository: `yassenjabal-jpg/UniversalCouncil`
2. Actual current SHA of the working branch / PR.
3. Machine-readable state under `state/command-center/`.
4. Governing documents under `docs/operations/command-center/`.
5. CI / GitHub Actions evidence.
6. This HANDOFF only as a continuation map.

Do NOT treat conversation memory, summaries, prior assistant claims, or generated images as proof of implementation.

Before any modification:
- fetch current branch;
- verify exact HEAD;
- verify PR state;
- verify CI on exact HEAD;
- read the Murtakaz approval policy;
- read the visual reference manifest if the change is visual.

---

# 1. REPOSITORY / PR STACK

Repository:
`yassenjabal-jpg/UniversalCouncil`

Main at handoff preparation:
`ea704a311515aeb674f2b8e8a1a7c1ee3abcf68a`

Current working branch:
`command-center/project-local-council-studio-20261019`

Current PR:
**PR #53 — المرتكز: project-local governance and Product Workshop for Command Center**

Stack:
- PR #51 — Owner Workspace v2 / Pulse
  - head at handoff preparation: `9fa24e4c7c4ddd138b2dba740942e466d2982bb2`
  - base: Stage 7 baseline
- PR #52 — Living Operations execution/design package
  - head: `2c56bf85899aa71204a0f10007a67d72315fb542`
  - base: PR #51
- PR #53 — المرتكز + project-local governance + visual locks
  - stacked on PR #52

Stage 7 exact historical baseline:
`7dcf0e7a17040cc70ad07ad87c9ca2709641cd83`

Verified Stage 7 baseline runs:
- Command Center Stage 7 #39234444557 — SUCCESS
- Company Stage 0 #39234444479 — SUCCESS
- CodeQL #39234444439 — SUCCESS

Important:
Stage 7 CI success does NOT prove real-host / Tailscale / phone success.

---

# 2. CURRENT DELIVERY / AUTHORITY STATE

Canonical delivery stage:
**STAGE 7 — Owner Device Enrollment + Private Tailnet**

State:
`OPEN_REAL_HOST_EVIDENCE_PENDING`

Stage 8:
`NOT_OPENED`

Live execution:
`BLOCKED_PHASE0`

`state/command-center/phase0-execution-gates.json` remains authoritative for live-execution authorization.

Do NOT open Stage 8.
Do NOT infer execution authority from UI, prototypes, CI, Tailscale reachability, or Murtakaz approval.

Known real-host/device state:
- YASSIN remote agent previously seen online: true
- Tailscale installation: UNKNOWN
- Tailscale connection: UNKNOWN
- Serve: NOT_CONFIGURED
- YASSIN host probe: false
- owner device enrollment: false
- active owner session: false
- real phone round trip: false
- session revocation round trip: false
- live execution: false

---

# 3. PROJECT-SPECIFIC GOVERNANCE — «المرتكز»

Canonical umbrella:
**المرتكز**

Internal units:

## هيئة المرتكز
Governance / truth / architecture / security / Autopilot / model-memory-evals / risk.

Machine-readable profile:
`state/command-center/project-governance/project-council.json`

## مشغل المرتكز
UX / visual / interaction / motion / Role Sigils / Windows / Android / prototype / accessibility / visual QA.

Machine-readable profile:
`state/command-center/project-governance/product-studio.json`

Canonical identity:
`state/command-center/project-governance/al-murtakaz.json`

The parent Universal Council and Media Studio are READ-ONLY parent systems for this project and must not be modified to specialize Command Center.

---

# 4. MANDATORY MURTAKAZ APPROVAL LAW

Owner directive is active:

**No change, adoption, completion, merge, release, or stage transition may occur without explicit Murtakaz review and approval.**

Policy:
`state/command-center/project-governance/al-murtakaz-approval-policy.json`

Core lifecycle:

`PROPOSED`
→ `MURTAKAZ_REVIEW_REQUIRED`
→ `MURTAKAZ_REVIEWING`
→ one of:
- `APPROVED_BY_AL_MURTAKAZ`
- `RETURNED_FOR_CHANGES`
- `BLOCKED_BY_AL_MURTAKAZ`
- `OWNER_DECISION_REQUIRED`

Before material implementation:
`APPROVE_TO_IMPLEMENT` is required.

After implementation:
final acceptance is still required.

Implicit approval is forbidden.

A material change after approval invalidates the prior approval and reopens review.

Murtakaz approval:
- does not grant execution authority;
- does not open Stage 8;
- does not override truth/security hard blockers;
- does not replace Owner final authority.

---

# 5. LIVING OPERATIONS — CURRENT DESIGN SYSTEM

Adopted design system:
**Living Operations Visual System**

Identity:
**Alive + Intelligent + Evidence-Driven + Interactive + Distinctly UniversalCouncil**

Core design laws:
- Project-first.
- Arabic RTL first.
- No Dead Surface.
- Interactive Semantic Objects.
- Animation = navigation + state + feedback.
- `UNKNOWN != SUCCESS`.
- Reduced Motion is first-class.
- Desktop and Android share semantics, not layout.
- Role Sigils are abstract operational marks, not human characters/mascots.
- Tool/state visuals must reflect real/prototype state, never decorative readiness.

Key visual/interaction systems:
- Role Sigils
- reasoning rings
- Autopilot Rail / Current
- Project Filmstrip
- Decision Mode
- Evidence Peek
- Checkpoint / Recovery / Fork
- Tool Dock
- Pulse
- Work Receipt

Important files:
- `docs/operations/command-center/living-operations/00_IMPLEMENTATION_PACKAGE.md`
- `01_VISUAL_BIBLE.md`
- `02_MOTION_BIBLE.md`
- `03_INTERACTION_CHOREOGRAPHY.md`
- `04_COMPONENT_ANATOMY.md`
- `05_DESKTOP_SCREEN_MAP.md`
- `06_ANDROID_OWNER_SCREEN_MAP.md`
- `09_ROLE_SIGIL_SYSTEM.md`
- `10_STATE_MOTION_MATRIX.md`
- `11_EVENT_ANIMATION_MAPPING.md`
- `12_NAVIGATION_INTERACTION_FLOW_MAPS.md`
- `14_P1_VERTICAL_SLICE_SPEC.md`
- `15_P1_VISUAL_DIRECTION_LOCK.md`
- `16_P1_INTERACTION_MOTION_STORYBOARD.md`
- `17_P1_SCREEN_REVIEW_MATRIX.md`
- `18_REFERENCE_ONLY_VISUAL_LOCK.md`

---

# 6. CRITICAL VISUAL SOURCE-OF-TRUTH RULE

This is the most important continuation rule for the next conversation.

## ONLY THE EIGHT APPROVED REFERENCE IMAGES ARE VISUAL SOURCE OF TRUTH.

Manifest:
`state/command-center/living-operations-reference-manifest.json`

Canonical set:
1. Home / Owner Workspace
2. Living Project Workspace
3. Software Autopilot Project
4. Studio Project
5. Owner Decision Mode
6. Checkpoint / Recovery / Fork
7. Pulse / Visual Project Story
8. Project Complete / Work Receipt

Rules:
- Reference first.
- Delta second.
- No visual reinvention.
- Do not generate a new art direction from prose.
- Do not invent a new palette/layout/card system.
- Prefer continuation/editing from an approved reference when creating a state/variant of an existing screen.
- New visuals are automatically `MURTAKAZ_REVIEW_REQUIRED`.

### If the eight reference images are not visible/available in the new conversation

DO NOT generate replacements from text.

Retrieve the canonical reference files from available conversation/library sources if possible, or ask the Owner to attach the approved references.

Do not proceed visually from memory alone.

---

# 7. EXPLICIT OWNER DIRECTIVE — REJECT ALL RECENT DESIGNS

**DO NOT ADOPT ANY OF THE RECENT GENERATED DESIGNS AFTER THE EIGHT CANONICAL REFERENCE IMAGES.**

They are:
`REJECTED_VISUAL_DRIFT`

They are NOT:
- alternate approved themes;
- reusable reference material;
- component sources;
- palette sources;
- layout sources;
- Murtakaz-approved visual artifacts.

The manifest currently records rejected generations including:

- `f75c9844-03fb-4c7b-857b-95babf3e4269`
- `176cb805-72ec-4b9f-b8f8-1f311f7d54ab`
- `7a9017af-197a-4fed-8665-57ea317f2bd9`
- `b3607b06-5137-4d4b-8126-43b9a4e64f68`
- `bd25818f-6f59-4407-bec0-af476378df58`
- `0289c00b-59de-422f-9532-5ed20d7b817a`

Do not reuse visual elements from these simply because they are polished.

Examples of rejected drift:
- gold/blue luxury dashboard restyling;
- decorative scenic backgrounds or theme overlays not present in the canonical references;
- human portrait avatars replacing abstract Sigils;
- generic SaaS/dashboard composition;
- new visual identity invented from textual prompts;
- unrelated decorative ribbons/orbs used as the product identity.

---

# 8. CURRENT VISUAL PHASE STATUS

State:
`state/command-center/living-operations-p1-visual-phase.json`

Current:
`P1_VISUAL_DIRECTION = IN_PROGRESS`

Scope:
`VISUAL_INTERACTION_MOTION_ONLY`

No runtime authority.

Five flagship surfaces still require real reference-faithful visual artifacts and Murtakaz review:

1. Home / Owner Workspace
2. Living Project Workspace
3. Owner Decision Mode
4. Recovery / Checkpoint / Fork
5. Project Complete / Work Receipt

Review tracker:
`state/command-center/living-operations-p1-screen-review.json`

At handoff preparation, all five remain:
`VISUAL_ARTIFACT_PENDING`
and
`murtakaz_decision = PENDING`

Shared motion:
pending final artifact review.

Android semantic pair:
pending final artifact review.

Do not mark P1 complete until explicit:
`APPROVED_BY_AL_MURTAKAZ`

---

# 9. INTERACTIVITY REQUIREMENT

The Owner explicitly requires full interactivity.

Every visually actionable object must:
- perform an action;
- open context;
- navigate to related information;
- or be explicitly disabled with a reason.

Examples:

Role Sigil click:
- why active;
- current task;
- findings;
- dissent;
- evidence;
- model/reasoning;
- recent contribution.

Reasoning rings click:
- provider/model;
- effort;
- task scope;
- fallback;
- capability state.

Checkpoint click:
- state;
- evidence;
- compare;
- fork.

Autopilot current click:
- current stage/task;
- role;
- model/reasoning;
- tool;
- elapsed time;
- last checkpoint;
- recovery/fallback.

Tool icon click:
- actual tool state;
- current artifact;
- last verified timestamp;
- recent output;
- diagnostics.

Filmstrip frame click:
- version;
- source;
- reason;
- evidence;
- compare;
- artifact;
- fork when valid.

Pulse click:
- what changed;
- why;
- evidence;
- related task;
- next action.

No decorative clickable-looking objects.

---

# 10. CURRENT WPF / PRODUCT SURFACE

The existing WPF Stage 7 surface is historically correct as a status/diagnostic shell.

It is NOT the final Living Operations surface.

Known issue:
the old rail was intentionally non-interactive for the earlier stage and cannot satisfy No Dead Surface.

Do not simply re-skin the old Stage 7 dashboard.

Future direction:
- existing technical/status surface should become advanced `System / Diagnostics`;
- the new product surface should be Command-first and Project-first.

Do not add execution logic into WPF presentation/code-behind to make the prototype appear functional.

---

# 11. PRE-PROTOTYPE ALIGNMENT — COMPLETE

Lock:
`AL_MURTAKAZ_P1_ALIGNMENT_LOCK`

Status:
PASS.

Completed:
- project-local Murtakaz orchestration projection;
- canonical Stage/Phase map;
- Stage 7 CI vs real-host truth separation.

P1 non-authoritative prototype:
GO.

This still does not authorize real Autopilot, phone control, Tailscale success, or live execution.

---

# 12. REAL AUTOPILOT — NOT IMPLEMENTED YET

Approved architecture direction exists, but real durable Autopilot remains future implementation.

Missing/required foundations include:
- canonical durable Project Store;
- Project Flight Recorder;
- Tool Effect Ledger;
- project-level checkpoint/recovery/fork/replay;
- loop/no-progress detection;
- budgets;
- durable resume after restart;
- Rehearsal / Shadow Mode;
- Trigger Engine;
- isolated software workspaces/sandboxes;
- role/prompt version registry;
- continuous evals;
- memory-scope integration.

Do not visually imply these are real runtime capabilities unless implemented and evidenced.

---

# 13. ANDROID OWNER — DESIGN DIRECTION ONLY

Android is a companion/control-intent surface, not a remote-desktop replacement and not an authority host.

Primary mobile jobs:
- monitor;
- preview;
- decide;
- respond;
- review evidence;
- controlled Autopilot intent.

Android real connection remains unproven.

Do not show:
CONNECTED / READY / LIVE
without real evidence.

Server/gateway must revalidate authorization for mobile actions.

---

# 14. MODEL / REASONING CONTROL — OWNER LOCK

Never hard-code one model for the Council/Studio/Murtakaz.

Role != Model.

Owner controls:
- globally;
- per project;
- per role;
- per task.

Precedence:
Task Override → Role Override → Project Default → Global Default.

Reasoning UI:
- Fast
- Standard
- Deep
- Max
- Auto

No silent fallback.
Unsupported Max must not silently downgrade unless Owner policy explicitly allows it.

UI must expose model + reasoning truthfully.

---

# 15. NEXT WORK — EXACT CONTINUATION

The next conversation should NOT start by inventing another visual.

It should:

1. Verify PR #53 exact HEAD and CI.
2. Read:
   - Murtakaz approval policy;
   - reference-only visual lock;
   - reference manifest;
   - P1 screen review matrix.
3. Load/inspect the eight approved reference images.
4. Ignore/reject every recent non-reference design.
5. Continue the visual phase screen-by-screen.
6. For each screen:
   - choose its canonical reference parent;
   - define only the required delta;
   - create/edit from the reference;
   - submit to Murtakaz review;
   - do not advance until accepted.
7. Do not open Stage 8.
8. Do not enable live execution.

Recommended first target:
**Home / Owner Workspace**, but only by editing/continuing the approved Home reference — not by generating a new theme from text.

---

# 16. DO NOT DO

- Do not adopt any recent generated design.
- Do not reuse any recent restyled dashboard that diverges from the canonical references.
- Do not create a new visual identity.
- Do not introduce decorative art, scenic motifs or background themes that are not directly observable in the canonical references.
- Do not use human role avatars instead of Sigils.
- Do not treat polished output as approved output.
- Do not claim a screen is final before Murtakaz approval.
- Do not modify parent Universal Council or Media Studio for this project.
- Do not open Stage 8.
- Do not claim Tailscale/phone/YASSIN host success without evidence.
- Do not claim real Autopilot exists.
- Do not move execution authority into UI.
- Do not silently fallback models/reasoning.
- Do not let prototype fixtures enter runtime/evidence truth.

---

# 17. START PROMPT FOR NEW CHAT

Use this instruction when continuing:

> اقرأ الملف `docs/operations/command-center/HANDOFF_2026-10-19_AL_MURTAKAZ_VISUAL_REFERENCE_LOCK.md` كاملًا واعتبره عقد الاستمرار، ثم تحقق من GitHub الفعلي قبل أي عمل. لا تعتمد أي تصميم تم توليده بعد الصور المرجعية الثماني؛ كلها مرفوضة. الصور المرجعية الثماني فقط هي مصدر الحقيقة البصري. استكمل مرحلة Living Operations البصرية من حيث توقفت، شاشةً شاشة، تحت قاعدة الموافقة الإلزامية للمرتكز، ولا تبدأ Stage 8 ولا التنفيذ الحقيقي.

---

# 18. FINAL CONTINUATION STATE

- المرتكز: ACTIVE
- mandatory Murtakaz approval: ACTIVE
- Living Operations: ADOPTED DESIGN SYSTEM
- reference-only visual lock: ACTIVE
- recent generated designs: REJECTED / NOT ADOPTED
- P1 visual direction: IN_PROGRESS
- five flagship screens: PENDING
- Android visual pair: PENDING
- Stage 7: OPEN / real-host evidence pending
- Stage 8: NOT OPENED
- execution authority: BLOCKED_PHASE0
- next work: reference-faithful visual continuation only
