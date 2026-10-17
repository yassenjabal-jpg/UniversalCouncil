# RevenueSystem / «المطابقة» — Deep Rebuild Audit
Date: 2026-10-17
Mode: SOURCE-ONLY + LOCAL STATIC ANALYSIS
RevenueSystem source pin: `6886fbb6398b67b366faf3ca446dbae54eb1ce4f`
UniversalCouncil source pin at session start: `d807b2a68d88cfe8266145536daefcdc691ca984`

## 0. Evidence boundary

This review did **not** launch RevenueSystem, IntegrationTests or UiTests and did not touch production AppData, SQL Server, LAN, backup, restore or migrations.

Evidence used:
- canonical GitHub main;
- a clean detached YASSIN worktree pinned to the exact main SHA;
- static source/XAML analysis;
- governing RevenueSystem docs and tests as source;
- current public WPF/Fluent/MVVM documentation and financial-product UI references.

Runtime behavior remains unclaimed until the isolated runtime profile is opened in the implementation phase.

---

# 1. Executive Council Finding

The program is not merely visually dated.

The current system contains valuable and mature financial/data behavior, but its presentation layer has accumulated large code-behind surfaces, direct data access from Views, many stateful services, and overlapping design-resource layers.

Therefore the recommended rebuild is:

**PARALLEL PRESENTATION REBUILD + APPLICATION FACADE + PROGRESSIVE BOUNDARY EXTRACTION**

Not:
- cosmetic reskin;
- blind full rewrite;
- database rewrite;
- framework migration for fashion;
- direct copy of old XAML into new views.

WPF/.NET 10 stays unless a later evidence-backed spike disproves it.

---

# 2. Repository scale

Pinned source inventory:

- Product/test files in primary project set: 436
- Product C# files analyzed: 232
- XAML files: 50
- View/code-behind source files: 48
- Service files: 110
- ViewModel files: **0**
- EF DbSets: **32**
- EF migrations excluding designers/snapshot: **15**

Test source:
- IntegrationTests: 14 C# files / ~3,577 lines
- ValidationTests: 5 C# files / ~1,018 lines
- UiTests: 1 C# file / ~979 lines

The product already has a meaningful verification corpus. The rebuild should turn that corpus into compatibility contracts, not discard it.

---

# 3. Presentation architecture heat map

| Surface | XAML lines | Code-behind lines | Named controls | Event bindings | Notable coupling | Rebuild priority |
|---|---:|---:|---:|---:|---|---|
| Reconciliation | 1,019 | 1,765 | 61 | 48 | DbContext factory, service construction, 15 Task.Run, dispatcher | CRITICAL |
| Reconciliation Details | 343 | 1,384 | 96 | 26 | DbContext factory, service construction, 25 MessageBox calls | CRITICAL |
| Cashier Entry | 408 | 1,998 | 61 | 23 | DbContext factory, service construction, multiple persistence paths | CRITICAL |
| Data Management | 125 | 1,632 | 66 | 39 | direct DbContext + 6 SaveChangesAsync | CRITICAL |
| Main Shell | 291 | 1,323 | 32 | 18 | navigation/session/state coordination | HIGH |
| Revenue Entry wrapper | 178 | 1,285 | 28 | 16 | direct DbContext + 3 SaveChanges | HIGH |
| Review Today | 151 | 1,370 | 15 | 4 | direct DbContext + service construction | HIGH |
| Pending Advances | 137 | 1,154 | 11 | 5 | direct DbContext | HIGH |
| Advances | 245 | 1,020 | 19 | 9 | direct DbContext | HIGH |
| Dashboard | 381 | 517 | 39 | 7 | DbContext factory + service construction | MEDIUM |
| Account Statement | 200 | 384 | 31 | 12 | no direct DbContext found in the view | GOOD EARLY SLICE |
| Reports workspace | small host + ReportsView | distributed | — | — | more service-oriented than major hotspots | GOOD EARLY/MID SLICE |

Interpretation:
- high line count alone is not a defect;
- the blocker is combined responsibility: visual state + navigation + DB/service coordination + dialogs + persistence + async/threading;
- large views should be split by coherent workflow, not arbitrary file size.

---

# 4. Confirmed architecture boundary findings

## A-01 — Zero ViewModel layer

Static inventory found no ViewModel files.

This does not mean every screen must be rewritten to MVVM immediately. It means a parallel rebuilt UI should not reproduce the old coupling.

Preferred touched-code direction:

`View → ViewModel/Coordinator → Application Use Case → Domain/Data`

## A-02 — Direct persistence from presentation exists

Confirmed examples:
- `DataManagementView.xaml.cs`: direct DbContext lifecycle and six SaveChangesAsync calls.
- `RevenueEntryView.xaml.cs`: direct AppDbContext creation and three SaveChanges calls.
- `RevenueScreenCustomizationWindow.xaml.cs`: direct DbContext and SaveChanges.
- several other Views construct or own AppDbContext factories.

This is a rebuild migration target, not a reason to throw away the existing data layer.

## A-03 — Service construction in Views

Multiple key views directly construct service classes.

The new UI should depend on narrow application use-case interfaces/facades instead.

## A-04 — Stateful/static service pressure

Static mutable candidates exist in:
- DatabaseConfigurationService
- NetworkReliabilityService
- DatabaseMaintenanceBarrier
- RevenueScreenLayoutService
- UiResponsivenessWatchdog
- AutoLockService
- BusinessDateService
- SessionService
- others.

Some are legitimate process-wide state. Each must be classified:
- process singleton by design;
- durable state;
- ambient context;
- accidental global state.

Do not mechanically eliminate all statics.

---

# 5. Design-system audit

Theme directory contains 10 XAML dictionaries:
- LightTheme
- DarkTheme
- DashboardResources
- FoundationTokens
- ModernControls
- OperationalRedesign
- ReferenceDesign
- RevenueUiSystem
- UnifiedComponents
- UnifiedDesign

Excluding the expected Light/Dark palette duplication:
- non-palette resource dictionaries: 8
- unique non-palette keys: 109
- keys duplicated across non-palette dictionaries: **54**

Examples:
- `PrimaryActionButtonStyle`: 4 dictionaries
- `BadgeBorderStyle`: 3
- `UnifiedCardStyle`: 3
- `UnifiedPageHeaderCard`: 3
- `UiPrimaryButton`: 2
- multiple spacing/corner tokens repeated in 2–3 layers

## Council interpretation

This explains why previous UI work could be technically applied while appearing visually modest or inconsistent.

The problem is not only screen XAML. The application has multiple generations of visual language loaded or preserved in parallel.

## Rebuild requirement

New UI design resources must use exactly four conceptual layers:

1. **Native Fluent baseline**
2. **Semantic Tokens**
3. **Reusable Components**
4. **Feature-local styles only when truly local**

No historical style dictionary may be imported wholesale.

---

# 6. Domain/data assets worth preserving

The data model is already substantial: 32 DbSets cover:
- reconciliation imports/rows/mappings;
- import batches;
- audit log/integrity;
- users/security;
- settlement documents;
- manual reconciliation and versions/attachments;
- electronic postings;
- special accounts/invoices/payments;
- account owners;
- financial parties;
- branches/POS/cashiers;
- business-day lifecycle/snapshots/transitions;
- denominations/revenue entries;
- advances.

The services inventory contains explicit components for:
- financial invariants/calculation;
- crash recovery;
- business-day workflow;
- reconciliation and manual reconciliation;
- import safety and concurrency;
- customer accounts;
- audit integrity;
- DB incarnation/maintenance barrier;
- permissions/security;
- report rendering/export/print;
- operational diagnostics;
- test runtime isolation.

These are **rebuild assets**, but each is reused only after contract tests prove the required behavior.

---

# 7. Financial invariants that must become executable contracts

Before a feature migrates:
- IQD coarse, IQD change and USD remain separate.
- conversion to IQD occurs only where matching/comparison contracts allow it.
- signed/negative spreadsheet values remain valid.
- no double posting on retry/double click.
- cashier + branch + POS + business day identity is preserved.
- account transfers remain auditable.
- bank electronic amounts remain attributable per cashier.
- discount source/default/override/reason semantics remain intact.
- legacy settlements remain compatible where required.
- business-day close/reopen rules remain explicit and logged.
- autosave/recovery cannot resurrect state against a different database incarnation.
- output reports must be source-faithful, not merely visually correct.

---

# 8. Workflow findings

## Daily Revenue
The keyboard contract is a major product advantage and must become a first-class interaction specification, not a side effect of handlers.

Keep:
- Enter / Shift+Enter
- PageUp/PageDown
- Home/End
- Ctrl+Z/Ctrl+Y
- Insert
- F5
- Esc
- Delete / Ctrl+Delete
- arithmetic denomination input

New UI should expose shortcuts in tooltips/help without slowing expert use.

## Reconciliation
This is the highest-risk/highest-value redesign.

Current screen scale proves it has accumulated too many responsibilities in one visual/code-behind surface.

Rebuild around:
1. context + import state;
2. difference scoreboard;
3. primary result list/table;
4. focused details panel;
5. manual matching/e-payment/account-transfer subflows;
6. explicit approval state.

Do not place every subflow permanently on the same visual plane.

## Accounts
The current master-detail direction is already structurally useful and is a good early rebuild slice.

## Reports
Keep report selection, dynamic filters, preview and output actions separated.
Do not let PDF/Excel/Print implementations leak into View logic.

## Data Management
Current direct persistence makes this a priority for application-command extraction before visual redesign.

---

# 9. Test architecture findings

The project has useful tests but several harnesses are concentrated in large Program files.

Rebuild direction:
- preserve old tests as compatibility evidence;
- add feature-scoped test classes for new use cases/ViewModels;
- keep isolated integration DB tests;
- keep UI Automation selectors stable and semantic;
- add screenshot/layout acceptance only as a UI complement, never a replacement for behavior tests;
- add explicit parity tests where old and new implementations can be evaluated against the same synthetic fixture.

Required proof for every migrated slice:
1. contract/unit;
2. isolated integration;
3. runtime GUI;
4. finance/data invariant checks;
5. regression against preserved old behavior.

---

# 10. What must NOT be copied into the rebuild

- giant feature code-behind classes;
- View-owned SaveChanges;
- duplicated resource dictionaries;
- hard-coded fixed widths as the primary responsive strategy;
- hidden success assumptions from async dispatch;
- duplicate MessageBox-heavy workflow branching;
- multiple responsibilities inside the same visual plane;
- static/global state without classification;
- old UI layout simply because it already has tests.

---

# 11. What should be copied or adapted

- explicit financial policies and tests;
- import parsers after contract verification;
- reconciliation calculation behavior;
- audit/security rules;
- database safety/recovery mechanisms;
- report business semantics;
- keyboard workflow semantics;
- source-sync/recovery concepts;
- isolated test mechanisms;
- exact historical-data compatibility requirements.

---

# 12. Council decision

**REBUILD IS JUSTIFIED. FULL BUSINESS-LOGIC REWRITE IS NOT.**

The rebuilt application should be visually new and internally cleaner while progressively consuming verified legacy capabilities through narrow contracts.

Primary risk is no longer “can we draw a better UI?”
Primary risk is “can we prevent financial/data behavior from being silently changed while replacing the presentation architecture?”

That risk is manageable through the new Studio gates.
