# المرتكز — UX Impact Audit بعد اعتماد Agentic Work OS
Date: 2026-10-21
Status: MURTAKAZ PRE-APPROVED / UX IMPACT AUDIT
Scope: eight canonical Command Center reference screens
Canonical baseline: `91aa5604fea04d6ddb9cc89769e5afa139e817d6`

## 1. الهدف

هذا التدقيق يحدد أثر المعمارية الجديدة على تجربة المستخدم بدون إعادة تصميم الهوية أو كسر المراجع البصرية الثمانية.

القرارات المسموحة لكل شاشة:
- `KEEP` — البنية الحالية تبقى.
- `MODIFY` — تعديل سلوك/محتوى داخل نفس البنية.
- `ADD_STATE` — إضافة حالة صادقة يجب أن يفهمها المستخدم.
- `ADD_INTERACTION` — إضافة مسار تفاعل وظيفي.
- `NO_CHANGE` — لا تعديل مطلوب في ذلك الجانب.

هذا التدقيق لا يصرح بإنشاء أي Visual جديد.

## 2. الحكم التنفيذي

### النتيجة العامة

**KEEP VISUAL SYSTEM / MODIFY UX STATE SEMANTICS**

لا توجد حاجة إلى:
- هوية جديدة؛
- palette جديدة؛
- top-level navigation جديد؛
- dashboard جديد؛
- إعادة ترتيب جذرية للشاشات الثماني.

توجد حاجة واضحة إلى:
- لغة حالات موحدة؛
- Owner-attention rules؛
- Context/Verification states؛
- progressive disclosure؛
- typed decisions؛
- Work Receipt provenance؛
- semantic parity بين Windows وAndroid.

## 3. مبادئ حاكمة قبل مراجعة كل شاشة

1. تعقيد `Gateway / Router / Registry / Broker` لا يظهر كتعقيد بصري في Home.
2. كل Job يملك حالة رئيسية واحدة صادقة.
3. الحالات التقنية الثانوية تظهر كـoverlay/chip/context detail، لا كأنها حالات نجاح منفصلة.
4. `UNKNOWN` لا تعرض أبدًا كنجاح.
5. `SUCCEEDED` تعني أن post-condition verification مر، لا أن الأداة قالت “تم”.
6. `STALE_CONTEXT` تختلف عن `FAILED`: العمل قد يكون صحيحًا لكن بني على حقيقة أصبحت قديمة.
7. `CONTEXT_CONFLICT` تختلف عن `BLOCKED`: السبب هو تضارب مصادر الحقيقة وليس عطل أداة.
8. Owner interruption لا يحدث لكل انتقال داخلي؛ فقط عندما يوجد قرار مادي مطلوب.
9. لا progress percentage بدون denominator حقيقي.
10. لا “Connected / Live / Ready” بدون evidence حديث.
11. أي control يبدو تفاعليًا يجب أن يعمل أو يشرح لماذا هو disabled.
12. الثماني صور المرجعية تبقى المصدر البصري الوحيد.

---

# 4. الشاشة 1 — Home / Owner Workspace

Canonical parent:
`01-home_owner_workspace.png`

SHA-256:
`7cb7d12f8819576ad4992158f6f0eb098ae3350a3684118ffc43192ea56749eb`

Reference regions preserved:
- top bar;
- right global nav;
- left status rail;
- owner hero;
- command composer;
- Council/Murtakaz pulse;
- Active Work;
- bottom owner row;
- tool dock.

## Decision

`KEEP + MODIFY + ADD_STATE + ADD_INTERACTION`

## KEEP

Preserve:
- command-first hierarchy;
- dominant Composer;
- current rails;
- Active Work placement;
- Since You Were Away;
- Needs Your Decision;
- Recent Results;
- bottom tool dock.

Do not add:
- Router dashboard;
- Capability matrix;
- provider grid;
- infrastructure KPIs.

## MODIFY

Active Work cards must stop using vague “working” semantics and project the canonical Job state.

Home summary language becomes outcome-oriented:
- what is happening;
- whether Owner action is needed;
- whether current truth is verified;
- what is next.

## ADD_STATE

Home needs compact projections for:
- WAITING_FOR_APPROVAL;
- BLOCKED;
- UNKNOWN;
- STALE_CONTEXT;
- CONTEXT_CONFLICT;
- VERIFYING;
- SUCCEEDED.

Only one primary state is visually dominant per work item.

## ADD_INTERACTION

State chip/card opens first-level explanation:
- “لماذا هذه الحالة؟”
- “ما الذي تغيّر؟”
- “ما المطلوب مني؟”
- “ما الدليل؟”

Routes:
- WAITING_FOR_APPROVAL -> Decision Mode.
- STALE_CONTEXT -> Context Change detail / re-plan action.
- CONTEXT_CONFLICT -> Truth Conflict detail.
- UNKNOWN -> Evidence/Verification detail.
- SUCCEEDED -> Work Receipt.

## Owner interruption rule

Home must not interrupt for:
- QUEUED;
- PLANNING;
- ordinary EXECUTING;
- VERIFYING.

It may elevate:
- WAITING_FOR_APPROVAL;
- material CONTEXT_CONFLICT;
- material UNKNOWN;
- BLOCKED when Owner can actually unlock it.

---

# 5. الشاشة 2 — Living Project Workspace

Canonical parent:
`02-living_project_workspace.png`

SHA-256:
`6f412a1f11e9e9f32df810194dbd4df1c42b973be9dcfb80354f10fb1cf3b799`

Required regions remain:
- project header;
- project context;
- Autopilot past/current/future rail;
- active roles;
- Filmstrip;
- Decision Stack;
- active tools;
- execution info;
- tool dock.

## Decision

`KEEP + MODIFY + ADD_STATE + ADD_INTERACTION`

## MODIFY

Autopilot Rail becomes the primary detailed projection of Job truth.

It must distinguish:
- lifecycle;
- context freshness;
- approval/review;
- verification.

Do not compress all of them into one colored badge.

## ADD_STATE

Project Workspace needs:
- exact current Job state;
- last verified checkpoint;
- context freshness;
- approval state;
- verification state;
- fallback-used marker only when real;
- active tool health only when current evidence exists.

## ADD_INTERACTION

Clicking state opens a Context/Job drawer with:
- current step;
- source revision;
- capsule id;
- last verified event;
- why route was chosen;
- what unlocks a block;
- evidence.

“Why this route?” is progressive disclosure, not a permanent panel.

Pause/Resume is enabled only when actual runtime and policy support it.

---

# 6. الشاشة 3 — Software Autopilot Project

Canonical parent:
`03-software_autopilot_project.png`

SHA-256:
`cb2c26d0d54a0a0c6aef3d03cc65737d3a27084fe8228112b719379d7ab966ec`

Required regions preserved:
- project header;
- model/branch status;
- checkpoint timeline;
- recovery control;
- diff compare;
- Branch A/B scorecards;
- Owner branch choice;
- history filmstrip;
- tool dock.

## Decision

`KEEP + MODIFY + ADD_STATE + ADD_INTERACTION`

## MODIFY

Branch status must be tied to:
- exact head;
- capsule source revision;
- latest verified build/test state.

“Branch exists” is not equivalent to “candidate verified”.

## ADD_STATE

Software mode must expose:
- VERIFYING after build/test/action;
- STALE_CONTEXT when HEAD/base materially moves beyond the pinned capsule;
- UNKNOWN after a crash or ambiguous external effect;
- CONTEXT_CONFLICT when canonical branch/base/policy truth conflicts;
- WAITING_FOR_APPROVAL at merge or material decision gates.

## ADD_INTERACTION

For STALE_CONTEXT:
- Compare pinned SHA vs latest SHA.
- Preserve current working result.
- Re-plan on latest.
- Create governed fork when appropriate.

For UNKNOWN:
- Verify first.
- Do not blindly replay.

For merge:
- Approval is intent/gate only.
- Actual merge result must be read back and verified.

---

# 7. الشاشة 4 — Studio Project

Canonical parent:
`04-studio_project.png`

SHA-256:
`e2f012f6207006a5068152027ccbef8cd55f866b25e60899a113937ebe523664`

Required regions preserved:
- five-stage pipeline;
- project info;
- central player;
- current output;
- main tool;
- model info;
- versions;
- QC;
- timeline/waveform;
- review ticket;
- handoff;
- active team;
- next handoff;
- tool dock.

## Decision

`KEEP + MODIFY + ADD_STATE + ADD_INTERACTION`

## MODIFY

Pipeline stage and Job state are separate concepts.

Example:
“Production” may be the current pipeline stage while Job state is:
- EXECUTING;
- WAITING_FOR_APPROVAL;
- VERIFYING;
- RETURNED_FOR_CHANGES overlay;
- BLOCKED.

Do not show “Production complete” merely because a tool render finished.

## ADD_STATE

Studio work needs:
- current Job truth;
- current handoff state;
- QC verification state;
- STALE_CONTEXT if script/reference/source changed;
- CONTEXT_CONFLICT if two canonical creative sources conflict;
- UNKNOWN if render/export outcome cannot be verified.

## ADD_INTERACTION

Handoff/Return Ticket shows:
- source artifact/version;
- reason;
- reviewer;
- required change;
- whether upstream lock must reopen.

No downstream department silently repairs a locked upstream source.

---

# 8. الشاشة 5 — Owner Decision Mode

Canonical parent:
`05-owner_decision_mode.png`

SHA-256:
`6351f755874fd9cec7cad4d8136d6c84eb8c3e8111a1d9ba219054f6d2488eeb`

Required regions preserved:
- de-emphasized project context;
- central decision surface;
- recommendation;
- why now;
- strongest dissent;
- evidence;
- approve/reject impact;
- evidence peek;
- five Owner actions;
- member ring.

## Decision

`KEEP + MODIFY + ADD_STATE + ADD_INTERACTION`

## MODIFY

Every decision must declare a typed reason, e.g.:
- APPROVAL_REQUIRED;
- CHANGE_OF_TRUTH;
- CONTEXT_CONFLICT;
- AUTHORITY_EXPANSION;
- DESTRUCTIVE_EFFECT;
- PRIVACY_TRADEOFF;
- MODEL_FALLBACK_CHOICE.

This prevents generic “Approve?” dialogs.

## ADD_STATE

Decision surface must show:
- what is waiting;
- why Owner is needed;
- what remains unchanged if no action is taken;
- whether execution is safely paused;
- exact affected project/artifact.

## ADD_INTERACTION

For CONTEXT_CONFLICT:
- compare sources;
- inspect provenance;
- choose/resolve through typed action;
- allow “Ask” without losing decision context.

Approve/Reject is not the final project result.
After Owner action, the project waits for downstream verified state transition.

---

# 9. الشاشة 6 — Checkpoint / Recovery / Fork

Canonical parent:
`06-checkpoint_recovery_fork.png`

SHA-256:
`7b1ceb447bebb3e9d488749e1beb4f82bf03fb078e58a2035c3ed2a58fe69076`

Required regions preserved:
- header;
- checkpoint timeline;
- selected checkpoint;
- branch A/B;
- details;
- comparison;
- event log;
- evidence extracts;
- available actions.

## Decision

`KEEP + MODIFY + ADD_STATE + ADD_INTERACTION`

## MODIFY

Recovery state must not visually imply restored success before verification.

`RECOVERING` is a control/execution overlay, not a terminal success state.

## ADD_STATE

Need explicit distinction:
- PAUSED overlay;
- RECOVERING overlay;
- VERIFYING;
- UNKNOWN / HOLD;
- STALE_CONTEXT;
- CONTEXT_CONFLICT;
- SUCCEEDED only after recovery verification.

## ADD_INTERACTION

Actions:
- inspect checkpoint;
- compare;
- create fork;
- preserve current state;
- request governed recovery;
- re-plan from newer context.

Destructive restore remains non-default.

UNKNOWN requires Verify First.

---

# 10. الشاشة 7 — Pulse / Visual Project Story

Canonical parent:
`07-pulse_visual_project_story.png`

SHA-256:
`f92ff13312e11ac6e52914a8cb595e0c870027f45ea8161aadaf72217cb483ed`

Required regions preserved:
- project selector;
- story timeline;
- before/current/after story;
- evidence cards;
- truth badges;
- per-card actions;
- persistent rails.

## Decision

`KEEP + MODIFY + ADD_STATE + ADD_INTERACTION`

## MODIFY

Pulse is a meaningful-event surface, not a live log.

Do not emit story cards for:
- every router hop;
- every model call;
- every tool heartbeat;
- decorative “AI activity”.

## ADD_STATE / EVENT TYPES

Meaningful event candidates:
- WAITING_FOR_APPROVAL;
- MATERIAL_BLOCKED;
- STALE_CONTEXT;
- CONTEXT_CONFLICT;
- RETURNED_FOR_CHANGES;
- RECOVERY_VERIFIED;
- MILESTONE_VERIFIED;
- PROJECT_COMPLETED_VERIFIED.

## ADD_INTERACTION

Every Pulse state event links back to:
- originating Job;
- project;
- decision if any;
- evidence;
- affected artifact/version.

Pulse cannot become a parallel source of truth; it is a projection.

---

# 11. الشاشة 8 — Project Complete / Work Receipt

Canonical parent:
`08-project_complete_work_receipt.png`

SHA-256:
`f8db7163bc4e5396cd2d58563cf2d513504cef7863da299851142ce554e22b7f`

Required regions preserved:
- completion hero;
- receipt header;
- stage rail;
- business receipt;
- final outputs;
- evidence;
- usage;
- issues recovered;
- fallbacks;
- checkpoints;
- decisions;
- next action;
- tool dock.

## Decision

`KEEP + MODIFY + ADD_STATE + ADD_INTERACTION`

## MODIFY

Completion hero is legal only for verified success.

A raw tool “success” or model claim does not unlock this screen’s completion treatment.

## ADD_STATE / TRUTH FIELDS

Work Receipt should expose, progressively:
- final result state;
- exact project/artifact revision;
- Context Capsule id;
- Skill/version when used;
- model/provider/reasoning;
- fallback use;
- tools/effects;
- verification summary;
- checkpoints;
- approvals/decisions;
- unresolved unknowns, if any;
- cost/usage only where known.

Sensitive values are redacted.

## ADD_INTERACTION

Owner can:
- open artifact;
- inspect evidence;
- expand technical trace;
- start follow-up;
- archive.

Publish/deploy remains a separately governed action.

If terminal result is FAILED/UNKNOWN/BLOCKED, a receipt may exist, but it must use a non-completion variant. It cannot reuse the verified-success hero.

---

# 12. Cross-screen UX consequences

## A. One primary Job state

Every Job exposes exactly one primary state from the UX State Contract.

Secondary dimensions may appear as overlays:
- PAUSED;
- RECOVERING;
- RETURNED_FOR_CHANGES;
- MURTAKAZ_REVIEW_REQUIRED;
- FALLBACK_USED.

They cannot replace the truth of the primary state.

## B. Progressive disclosure

Level 1:
- state;
- what it means;
- Owner action if needed.

Level 2:
- why;
- current stage;
- source/checkpoint;
- evidence summary.

Level 3:
- model/provider;
- routing;
- capsule;
- policy;
- full trace.

Home normally stays at Level 1.
Project drawers reach Level 2.
System/Evidence/Work Receipt may reach Level 3.

## C. Owner-attention hierarchy

Highest:
- CONTEXT_CONFLICT requiring Owner;
- destructive/authority/privacy decision;
- WAITING_FOR_APPROVAL for material action.

High:
- material UNKNOWN;
- BLOCKED when Owner can unlock.

Normal:
- STALE_CONTEXT when safe deterministic re-plan is permitted.
- FAILED when no immediate Owner action is required.

Quiet:
- QUEUED;
- PLANNING;
- EXECUTING;
- VERIFYING;
- SUCCEEDED after notification policy handles it.

## D. No fake progress

Forbidden:
- invented completion percentages;
- “agent thinking 73%”;
- fabricated remaining time;
- fake worker count;
- green provider status from stale evidence.

Allowed:
- stage-based progress when stage count is real;
- elapsed time;
- verified checkpoint count;
- known completed steps.

---

# 13. Android impact

Android does not receive a different truth vocabulary.

The existing labels:
- RUNNING;
- WAITING_OWNER;
- BLOCKED;
- RECOVERING;
- PAUSED;
- COMPLETE

become UI projections of the canonical state model rather than an independent state machine.

Examples:
- RUNNING <- EXECUTING.
- WAITING_OWNER <- WAITING_FOR_APPROVAL or Owner-required CONTEXT_CONFLICT.
- RECOVERING <- EXECUTING + RECOVERING overlay.
- PAUSED <- current primary state + PAUSED control overlay.
- COMPLETE <- SUCCEEDED only.
- UNKNOWN remains explicitly UNKNOWN and is never projected as COMPLETE.

The server/gateway revalidates all critical actions.

---

# 14. What does NOT change

No change to:
- eight reference images;
- navigation rail count;
- visual language;
- card geometry;
- role sigils;
- typography direction;
- decorative system;
- product brand;
- motion personality.

No new technical dashboard is added to Home.

---

# 15. Implementation recommendation

After this audit is accepted:

1. lock the UX State Contract;
2. build Context Resolver;
3. build Context Capsule Compiler;
4. expose only the state fields required by this UX contract;
5. later update the native reference shell screen-by-screen with bounded deltas;
6. every visual implementation still goes through the existing Visual Production Hard Gate.

---

# 16. Murtakaz preliminary disposition

### هيئة المرتكز
Direction: **ACCEPTABLE**
Conditions:
- machine-readable UX State Contract;
- UNKNOWN and Context states stay fail-closed;
- no execution claims added.

### مشغل المرتكز
Direction: **ACCEPTABLE**
Conditions:
- preserve all eight references;
- use progressive disclosure;
- do not turn Home into System/Diagnostics;
- do not introduce new visual language.

Final adoption remains pending exact-head validation and post-review.
