# RevenueSystem Rebuild Studio — Operating Contract

**Status:** PROJECT-SCOPED CANDIDATE  
**Date:** 2026-10-17  
**Product:** RevenueSystem / «المطابقة»

## 1. Mission

إعادة إنتاج «المطابقة» كبرنامج WPF/.NET عالي الاعتمادية، مع واجهة جديدة فعليًا، مع الحفاظ على السلوك المالي والبياني المطلوب أو تحسينه فقط من خلال قرار صريح ومختبر.

هذه الخلية لا تستبدل RevenueSystem Council. هي طبقة تنفيذ project-scoped تستعمل المجلس كجهة حوكمة مستقلة.

## 2. Core Law

**GUI PRIMARY / DC SECONDARY / SPECIALIZED TOOL FIRST / VERIFIED HANDOFFS**

1. التطبيق التفاعلي يُدار من واجهته الفعلية.
2. DC يدعم الملفات، Git، العمليات، الاختبارات، السجلات، artifacts والاسترداد.
3. كل مرحلة حرفية لها برنامج GUI أساسي واحد.
4. أي state change مهم يحتاج postcondition verification.
5. UNKNOWN لا يصبح SUCCESS.
6. لا ينتقل العمل downstream قبل قبول handoff.
7. أي خلل upstream يعود إلى مصدره عبر Return Ticket.
8. لا توجد أداة؟ CAPABILITY_GAP، وليس بديلًا منخفض الجودة.
9. لا install / credentials / purchase / production access بدون authority مناسبة.

## 2.1 Visual Authority

الاتجاه البصري الوحيد المسموح لـRevenueSystem هو:

**EDITORIAL FINANCIAL ENGRAVING**

المرجع الحاكم:
`docs/operations/software/REVENUESYSTEM_2_ART_DIRECTION_LOCK.md`

قواعد التنفيذ:
- الصور الثماني المولدة بتاريخ 2026-10-18 هي visual grammar reference وليست screenshots يجب نسخها حرفيًا.
- أي generated drift مثل شعارات/رموز دولة، عملة غير مطلوبة، مبانٍ مصرفية، أو قيم تجريبية لا يدخل المنتج.
- لا يجوز الرجوع لأي RevenueSystem visual direction سابق.
- كل شاشة جديدة يجب أن تمر Visual QA against the Art Direction Lock قبل handoff.
- التنفيذ يكون عبر WPF tokens/components/vector geometry، وليس screenshot skin.

## 3. Control Plane

### Rebuild Producer / Chair
يمتلك:
- فتح/إغلاق المراحل.
- source/environment pin.
- dependency map.
- handoff acceptance workflow.
- checkpointing.
- recovery coordination.
- Human Assistance coordination.
- capability gap routing.

لا يملك:
- تغيير semantics المالية منفردًا.
- تجاوز blockers.
- إعلان نجاح بلا evidence.
- تحرير artifacts الحرفية بدل مالك المرحلة.

## 4. Macro Phases

### Phase A — Discovery & Contract

**A01 Source Pin**
- GitHub current main SHA.
- branch/worktree state.
- governing files.
- current tests.
- current product map.

Primary tool: GitHub + DC host support.

**A02 Behavior Archaeology**
- map current workflows.
- identify preserved behavior.
- identify defects not to reproduce.
- map financial/data/security invariants.
- distinguish requirement from accident.

Primary interactive program when runtime inspection is authorized: RevenueSystem application itself.
Support: source/tests through GitHub/DC.

**A03 Product Contract**
Outputs:
- workflow inventory.
- data/finance invariants.
- feature acceptance matrix.
- defect exclusion list.
- migration/preservation policy.

Exit: **BEHAVIOR_INVARIANTS_LOCK**

---

### Phase B — Design & Prebuild

**B01 UX System**
Primary program: Figma reference when used; implementation-oriented validation in Blend.
Outputs:
- design tokens.
- shell/navigation.
- RTL/keyboard model.
- dense financial workspaces.
- components/states.
- visual acceptance references.

**B02 WPF Implementation Architecture**
Primary program: Visual Studio 2026.
Outputs:
- solution/project boundaries.
- DI/service ownership.
- state/navigation model.
- async/threading rules.
- error/recovery model.

**B03 Data & Reliability Design**
Primary program: Visual Studio 2026.
Outputs:
- DB boundaries.
- migrations/compatibility.
- autosave/recovery.
- import transaction model.
- backup/restore boundaries.
- logging/diagnostics.

**B04 Test Architecture**
Primary program: Visual Studio 2026.
Outputs:
- unit/validation/integration/UI split.
- disposable local DB policy.
- synthetic fixtures.
- UI automation selectors.
- performance baselines.

**B05 Build Plan**
- vertical slices.
- owners.
- dependencies.
- acceptance criteria.
- rollback.
- migration strategy.

Exit: **UX_ARCHITECTURE_READY_LOCK**

---

### Phase C — Production & Verification

Official mode:
**VERTICAL SLICES WITH SERIAL ARTIFACT OWNERSHIP AND FEEDBACK GATES**

Parallel thinking/review is allowed. Parallel conflicting edits to the same locked artifact are not.

Each slice follows:

1. Slice Open
2. GUI Implementation
3. Local Build
4. Focused Tests
5. Runtime Launch
6. GUI Acceptance
7. Domain Clearance
8. Regression
9. Handoff Lock

#### Suggested slice order

1. Application Shell + Design System
2. Daily Revenue Entry
3. Reconciliation / Matching
4. Accounts + Transfers
5. Advances
6. Imports / Data Management
7. Reports / Print / Export
8. Recovery / Backup / Operational-Day lifecycle
9. Performance / Observability
10. Installer / Release

Order may change only through an explicit dependency decision.

## 5. Tool Map

### Visual Studio Community 2026
Use for:
- code authoring.
- solution navigation.
- debugger.
- diagnostics.
- test explorer when GUI execution is useful.
- refactoring.
- project/package configuration.

### Blend for Visual Studio
Use for:
- WPF XAML visual layout.
- styles/templates.
- visual states.
- design-time inspection.
- spacing/alignment/component composition.

### RevenueSystem Runtime
Use for:
- real operator workflow acceptance.
- keyboard/focus behavior.
- visual density.
- dialogs/popups.
- failure/recovery behavior.
- screenshots and smoke evidence.

### Photoshop / Illustrator
Use only when needed for:
- icons.
- logos.
- splash/branding assets.
- raster/vector assets.
They do not replace WPF UI implementation.

### YASSIN Control Bridge
Primary generic GUI automation:
1. WinApp UIA semantic actions.
2. visual/physical bounded actions.
3. pywinauto fallback.
4. raw coordinates only when no semantic path exists.

### Desktop Commander
Secondary support plane:
- Git.
- files.
- build.
- tests.
- logs.
- process checks.
- artifacts.
- recovery.
- scripts for repeatable QA.

## 6. GUI Action Contract

For every consequential GUI action:

`OBSERVE → LOCATE → ACT → OBSERVE → VERIFY → CHECKPOINT`

Required evidence may include:
- semantic property/value.
- before/after screenshot.
- created/changed artifact.
- build/test result.
- runtime state.
- log/exception absence or expected error handling.

Provider text alone is never enough.

## 7. Handoff Packet

Every slice/stage handoff records:
- project and source SHA.
- stage/slice ID.
- source owner.
- target owner.
- changed artifacts.
- accepted requirements.
- preserved invariants.
- tests executed.
- runtime evidence.
- GUI evidence.
- known limitations.
- unresolved unknowns.
- rollback checkpoint.
- acceptance result.

Results:
- ACCEPTED
- REJECTED_RETURN_TO_SOURCE
- HOLD_CAPABILITY_GAP
- HOLD_OWNER_DECISION
- UNKNOWN_RECONCILIATION_REQUIRED

## 8. Return Ticket

A downstream reviewer does not silently repair upstream locked work.

Ticket fields:
- source stage.
- detecting stage.
- artifact.
- defect.
- evidence.
- requested correction.
- do-not-change boundary.
- acceptance criterion.
- resume handoff.

## 9. Finance/Data Clearance

Any slice that touches money/persistence must independently verify:
- IQD coarse/change/USD separation.
- signed/negative values.
- no double posting.
- cashier/branch/day/account identity.
- reconciliation conversion only where contract allows.
- transaction/retry idempotency.
- recovery/autosave semantics.
- report source fidelity.

Visual success never substitutes for these checks.

## 10. Runtime Profile

The rebuild requires an explicit **isolated local runtime profile**:
- disposable/synthetic local data.
- no production DB.
- no production AppData inheritance.
- no live LAN/server.
- safe local test identity.
- deterministic reset.

Runtime execution is allowed only inside that isolated profile after its contract is established.

## 11. Human Assistance

Trigger only when:
- credential/login is required.
- physical access is required.
- missing application/tool blocks work.
- GUI recovery is exhausted.
- an irreversible decision is required.
- specialist judgment is genuinely needed.

Request the smallest human action possible.

If the same assistance cause repeats 3 times:
open Capability Review.

## 12. Capability Gap Protocol

A gap record includes:
- missing capability.
- blocked stage.
- current tools tried.
- why they are insufficient.
- candidate tool(s).
- cost/license.
- permissions/security.
- install path.
- sandbox test.
- success metric.
- rollback/uninstall.
- owner decision requirement.

No quota exists for new tools; zero-install is preferred when current tools are sufficient.

## 13. Completion Definition

A slice is not DONE unless applicable evidence exists for:
- source change.
- build.
- focused tests.
- integration/validation tests.
- runtime app launch.
- GUI acceptance.
- financial/data clearance.
- logs/exceptions review.
- regression check.
- handoff record.

A rebuild phase is not DONE merely because the UI looks new.
