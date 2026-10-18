# RevenueSystem 2.0 — Detailed Rebuild Execution Plan
Version: 1.0
Date: 2026-10-17
Status: OWNER-APPROVED DESIGN DIRECTION / IMPLEMENTATION PLAN
RevenueSystem source baseline: `6886fbb6398b67b366faf3ca446dbae54eb1ce4f`
UniversalCouncil baseline: `d807b2a68d88cfe8266145536daefcdc691ca984`

---

# 0. Executive decision

RevenueSystem 2.0 is a **full product rebuild of the presentation/application experience**, not a visual refresh.

The current application remains authoritative only for:
- financial truth;
- persistence and data compatibility;
- permissions/security behavior;
- auditability;
- import/report contracts;
- proven keyboard/operator behavior;
- recovery and reliability behavior.

The current application is **not authoritative** for:
- screen count;
- screen boundaries;
- navigation;
- shell;
- popup strategy;
- layout;
- visual language;
- information architecture.

The approved and sole visual direction is:

**EDITORIAL FINANCIAL ENGRAVING**

Authority:
`docs/operations/software/REVENUESYSTEM_2_ART_DIRECTION_LOCK.md`

It translates secure-financial craft into a modern desktop workstation through guilloché, engraved linework, ledger rules, institutional seals, paper materiality and exact hierarchy—without literal currency/bank/government imitation.

Explicitly rejected:
- any previous RevenueSystem visual direction;
- architectural imagery as UI identity;
- Babylonian/Baghdadi ornament;
- real banknote/bank/government imitation;
- country-specific visual branding;
- casino/luxury/crypto aesthetics;
- generic Fluent/SaaS enterprise styling;
- card-heavy dashboards;
- recreating the old RevenueSystem layout;
- dark-first financial UI;
- web-style page navigation.

---

# 1. Product north star

RevenueSystem 2.0 is:

**A day-centric financial operations environment for high-frequency desktop work.**

The user should feel that they are working inside one coherent financial workstation, not moving between unrelated forms.

Primary operational story:

```
Open financial day
    ↓
See what needs attention
    ↓
Enter cashier revenue
    ↓
Review exceptions
    ↓
Reconcile imported/reference data
    ↓
Resolve manual/electronic/account differences
    ↓
Approve / close
    ↓
Report / audit
```

---

# 2. Target visible product

The old eight top-level destinations are replaced by six workspaces.

## W1 — اليوم / Day Console

Owns:
- active financial day;
- branch/cashier completion;
- attention queue;
- revenue entry launch;
- review/exceptions;
- close/reopen;
- recovery warnings.

## W2 — المطابقة / Reconciliation Studio

Owns:
- import intake;
- validation;
- mapping;
- cashier result set;
- difference investigation;
- manual reconciliation;
- electronic breakdown;
- account transfer;
- evidence/history;
- approval.

## W3 — المالية / Finance Ledger

Owns:
- accounts;
- account statements;
- advances;
- financial parties;
- owners/policies;
- cross-links from reconciliation.

## W4 — التقارير / Reports Center

Owns:
- report catalog;
- filters;
- preview;
- print;
- PDF;
- Excel/export;
- advanced design options.

## W5 — البيانات / Data Operations

Owns:
- branches;
- cashiers;
- POS;
- reference/master data;
- staged imports;
- validation/impact;
- protected maintenance.

## W6 — الإدارة / Administration

Owns:
- users;
- roles;
- permissions;
- connection/database;
- backup/recovery;
- audit;
- diagnostics;
- preferences.

System states, not workspaces:
- Login
- Lock
- First Run
- Database Selection
- Password Change

---

# 3. Target shell

## 3.1 Command Rail

A narrow RTL command rail.

Purpose:
- switch between six workspaces;
- show unread/attention indicators only when actionable.

Rules:
- no wide permanent sidebar;
- no nested navigation tree;
- no duplicate workspace navigation elsewhere.

## 3.2 Work Item Tabs

Tabs represent active work, not pages.

Examples:
- اليوم — 17/10
- أحمد كريم — الوارد
- مطابقة — الحلة
- شركة النور
- تقرير الفروقات

Rules:
- preserve unsaved/recovery state;
- switching tabs must not lose edits;
- each tab has stable automation identity;
- duplicate work items are prevented or deliberately versioned.

## 3.3 Business Context Bar

Persistent context where relevant:
- financial date;
- day status;
- branch/scope;
- current user;
- database/connectivity;
- sync/recovery state.

## 3.4 Workbench

The main task surface.

Rules:
- receives most screen area;
- one dominant task region;
- subordinate regions visually recede;
- dense when the task is dense.

## 3.5 Context Inspector

Used for selected:
- cashier;
- account;
- transaction;
- import issue;
- report item.

Rules:
- replaces most domain popups;
- collapsible;
- keyboard focusable;
- preserves selected context.

## 3.6 Status Bar

Shows:
- save state;
- connectivity;
- background jobs;
- recovery;
- contextual shortcut hints.

## 3.7 Command Palette

Searchable actions:
- navigation;
- open cashier/account;
- create report;
- start import;
- run allowed admin action.

It never bypasses permissions.

---

# 4. Art direction — implementation rules

Governing system:
**EDITORIAL FINANCIAL ENGRAVING**

Full authority:
`docs/operations/software/REVENUESYSTEM_2_ART_DIRECTION_LOCK.md`

## 4.1 Visual premise

RevenueSystem should feel like a precision financial instrument whose identity comes from secure-document craft, not from literal money imagery.

Accepted vocabulary:
- Paper Ivory operational field;
- Deep Forest institutional structure;
- Cobalt interaction/focus;
- guilloché/security-print lines;
- ledger rulework;
- original institutional seals;
- subtle paper layering;
- denomination-strip geometry;
- quiet dense tables and inputs.

## 4.2 Palette

- Paper Ivory `#F6F1E8` — 45–60%, dominant work surface
- Deep Forest `#173C32` — 15–25%, rail/verified/structure
- Cobalt `#174FA6` — primary focus/action
- Clear Blue `#2B73C9` — active interaction
- Sky Blue `#8EACD2` — quiet support
- Warm Parchment `#D9C8B1` — document/material support
- Brass Gold `#B58A3E` — 3–7% maximum, micro-accent only
- Charcoal `#151515` — text/anchors
- semantic red — financial difference/risk/destructive only
- semantic amber — review/attention only

## 4.3 Texture/material

Allowed:
- subtle paper warmth;
- guilloché in shell/header/empty/status spaces;
- registration marks in process flows;
- fine ledger lines;
- original RevenueSystem seals;
- minimal layered-paper depth.

Forbidden:
- texture behind editable numbers or dense grids;
- architecture as decoration;
- literal real banknotes;
- national/government symbols;
- real bank branding;
- glass/neon;
- casino/luxury styling;
- giant shadows/rounding;
- fake antique material.

## 4.4 Typography

Display:
- refined contemporary Arabic Naskh influence for major identity/state headings only.

Operational:
- modern Arabic sans;
- compact;
- high-legibility.

Numbers:
- tabular;
- currency-aware;
- sign explicit;
- stable baseline.

## 4.5 Geometry

- 4–8 px default radii;
- 1 px hairline ledger borders;
- square/lightly-rounded desktop controls;
- 4/8/12/16/24/32 spacing scale;
- shadows mostly absent;
- dense rows stay dense.

## 4.6 Shell

- right-side narrow Deep Forest command rail;
- active destination uses Cobalt/Clear Blue;
- top-right Windows controls;
- ivory business context bar;
- work-item tabs;
- main workbench;
- optional inspector;
- compact status bar.

## 4.7 Art-density rule

Decoration reduces before functional density reduces.

Highest allowed expression:
- Login identity;
- report framing;
- shell/context headers;
- verified/matched status.

Lowest allowed expression:
- Cashier numeric entry;
- DataGrid;
- account ledger rows;
- reconciliation numeric comparisons.

## 4.8 Motion

Blend/WPF is implementation authority.

Timing:
- focus/hover: 80–140 ms;
- control state: 100–180 ms;
- panel/inspector: 160–240 ms;
- workspace transition: 180–300 ms.

Allowed:
- ledger/page shifts;
- line builds;
- focus trace;
- verification seal resolve;
- restrained panel reveals.

Forbidden:
- continuous animated patterns;
- animated coins/money;
- motion that delays typing or steals focus.

## 4.9 Concept-image corrections

The generated eight-screen set is a visual reference, not product truth.

Do not copy:
- Saudi national emblem/imagery;
- Saudi Riyal examples unless real domain data requires them;
- bank-building artwork;
- palm/country imagery;
- generated fake dates/names/amounts;
- left-side window controls.

Repository/domain contracts own real content.

# 5. Target application boundaries

Conceptual architecture:

```
RevenueSystem.Presentation
    Views
    Components
    Workspaces
    ViewModels / Coordinators
    Navigation / Commands
         ↓
RevenueSystem.Application
    Use Cases
    DTOs / Results
    Orchestration
    Permission-aware commands
         ↓
RevenueSystem.Domain / Existing Verified Services
    Financial calculations
    Reconciliation rules
    Business-day rules
    Accounts / Advances
         ↓
RevenueSystem.Infrastructure
    EF / AppDbContext
    Import parsers
    Reporting
    Files
    Backup / Recovery
```

The final physical project split is decided by the architecture spike; the dependency direction is not negotiable.

Hard rules for new code:
- no `AppDbContext` in View;
- no `SaveChanges` in View;
- no financial rule in View;
- no feature Service construction in View;
- no permission enforcement only in visibility;
- no giant “god ViewModel” replacing giant code-behind;
- no global event bus used as a substitute for clear ownership;
- async I/O must be cancellable where practical;
- UI thread work must be bounded.

---

# 6. Workstreams

The rebuild runs through coordinated workstreams.

## WS-A Product / Workflow
Owns:
- capability map;
- user task flow;
- screen deletion/merge/split decisions;
- workflow acceptance.

## WS-B Art / UI System
Owns:
- Editorial Financial Engraving visual system;
- tokens;
- typography;
- components;
- states;
- motion references;
- Blend validation.

## WS-C Application Architecture
Owns:
- ViewModel/Coordinator pattern;
- use cases;
- dependency direction;
- navigation;
- composition root.

## WS-D Finance & Domain
Owns:
- invariants;
- reconciliation math;
- settlement/account effects;
- currency behavior;
- business-day semantics.

## WS-E Data & Reliability
Owns:
- EF/data boundaries;
- transaction behavior;
- autosave;
- recovery;
- incarnation;
- backup/restore;
- import commit semantics.

## WS-F Security & Audit
Owns:
- permissions;
- session;
- audit evidence;
- sensitive actions;
- approval/reason requirements.

## WS-G QA / Test Architecture
Owns:
- golden fixtures;
- regression;
- parity;
- isolated runtime;
- UI automation;
- failure testing.

## WS-H Performance / Observability
Owns:
- startup;
- memory;
- list/grid responsiveness;
- import/report latency;
- UI responsiveness;
- logs/metrics.

## WS-I Release / Migration
Owns:
- old/new route switching;
- fallback;
- installer;
- upgrade;
- rollback;
- release evidence.

---

# 7. PHASE 0 — Source & execution foundation

## P0.1 Source pin

Actions:
- re-check `origin/main`;
- create clean implementation worktree;
- record branch/head/tree status;
- never implement in the user's unrelated working branch.

Deliverable:
`RRS_SOURCE_LOCK.json`

Gate:
`G0_SOURCE_ENVIRONMENT_LOCK`

## P0.2 Isolated runtime

Create a profile that cannot touch:
- production DB;
- live LAN;
- production AppData;
- production backups;
- live user secrets.

Use:
- disposable local database;
- dedicated AppData root;
- synthetic files;
- isolated test user/session.

Deliverable:
`RRS_ISOLATED_RUNTIME_CONTRACT.md`

## P0.3 Baseline measurement

Measure current app in isolated profile:
- startup;
- navigation;
- cashier open;
- save;
- reconciliation import;
- report generation;
- repeated navigation memory.

No target thresholds are invented before baseline.

Deliverable:
`RRS_BASELINE_PERFORMANCE.json`

Exit:
**environment can safely build/run/test without production exposure.**

---

# 8. PHASE 1 — Behavior contract

## P1.1 Capability inventory

For every current capability:
- actor;
- trigger;
- input;
- output;
- write effects;
- audit;
- permission;
- retries;
- failures;
- keyboard;
- reports/imports touched.

Every old UI class receives a disposition:
- MIGRATE
- MERGE
- SPLIT
- REMOVE
- SYSTEM_STATE
- TEMP_FALLBACK

## P1.2 Financial invariants

Lock:
- IQD coarse/change/USD separation;
- conversion boundaries;
- signed spreadsheet values;
- no duplicate posting;
- cashier/branch/POS/day identity;
- account transfer traceability;
- electronic bank attribution;
- discounts/overrides/reasons;
- business-day close/reopen rules;
- recovery DB-incarnation binding;
- report source fidelity.

## P1.3 Golden synthetic dataset

Must include:
- five branches;
- ~45 representative cashiers;
- multiple POS;
- positive/negative amounts;
- IQD/change/USD;
- Rafidain/SWITCH;
- matched/difference/unmapped;
- transfers;
- advances;
- open/closed days;
- permission roles;
- recovery draft;
- long Arabic names;
- very large values;
- empty states;
- invalid imports.

## P1.4 Executable parity

Convert invariants into:
- unit tests;
- application tests;
- integration tests;
- import fixtures;
- report fixtures.

Gates:
- `G1_CAPABILITY_MAP_LOCK`
- `G2_GOLDEN_FIXTURE_LOCK`
- `G3_BEHAVIOR_INVARIANTS_LOCK`

No new high-risk write workflow begins before G3.

---

# 9. PHASE 2 — Design system & interaction foundation

## P2.1 Art lock

Status:
**APPROVED**

Create visual tokens for:
- surfaces;
- typography;
- spacing;
- radii;
- borders;
- elevation;
- focus;
- success/warning/difference;
- tables;
- inspectors;
- commands.

## P2.2 WPF token architecture

Four layers only:
1. native WPF/Fluent behavior baseline;
2. semantic tokens;
3. shared components;
4. feature-local styles.

No duplicate public key across non-theme dictionaries.

## P2.3 Core components

Build and validate:
- AppShell;
- CommandRail;
- WorkItemTabs;
- BusinessContextBar;
- StatusBar;
- CommandPalette;
- Inspector;
- EditorialSectionHeader;
- FinancialNumber;
- CurrencyAmount;
- StateBadge;
- DifferenceIndicator;
- DenseDataGrid;
- FilterBar;
- AttentionQueue;
- InlineForm;
- SideSheet;
- SafeConfirm;
- EmptyState;
- Skeleton/Busy state.

## P2.4 Accessibility / DPI matrix

Validate:
- 1280×720
- 1366×768
- 1600×900
- 1920×1080
- 125% DPI
- 150% DPI
- keyboard only
- high text density
- long Arabic labels.

## P2.5 Motion prototype

Cinetic pilot:
**Day Console → Open Cashier → Cashier Workbench → return**

Purpose:
- evaluate continuity;
- tab behavior;
- inspector behavior;
- visual motion grammar.

It is not runtime proof.

Gate:
`G4_DESIGN_SYSTEM_LOCK`

---

# 10. PHASE 3 — Architecture foundation

## P3.1 MVVM/Coordinator spike

Compare:
- CommunityToolkit.Mvvm;
- minimal custom pattern.

Measure:
- boilerplate;
- command behavior;
- async;
- validation;
- testability;
- navigation;
- state restoration.

Decision artifact:
`RRS_PRESENTATION_PATTERN_DECISION.md`

## P3.2 Application facade

Introduce task-oriented interfaces.

Examples:
- `OpenFinancialDayQuery`
- `GetDayAttentionQuery`
- `OpenCashierEntryQuery`
- `SaveCashierRevenueCommand`
- `ImportReconciliationCommand`
- `ResolveReconciliationDifferenceCommand`
- `ApproveReconciliationCommand`
- `GetAccountLedgerQuery`

Names are provisional; responsibilities are the contract.

## P3.3 Navigation/state

Implement:
- workspace router;
- work-item identity;
- dirty state;
- recovery handoff;
- close guards;
- deep link command;
- permission-aware commands.

## P3.4 UI automation identity

Every interactive shared component gets:
- stable AutomationId;
- semantic Name;
- state Value where appropriate.

Gate:
`G5_ARCHITECTURE_FOUNDATION_LOCK`

---

# 11. PHASE 4 — Finance Ledger pilot

The first production slice deliberately avoids cashier/reconciliation writes.

## P4.1 Read-only Accounts

Build:
- Account Browser;
- search/filter;
- account header;
- ledger;
- inspector;
- transaction details;
- documents.

Validate:
- large ledgers;
- long Arabic names;
- positive/negative balances;
- keyboard navigation;
- workspace tabs.

## P4.2 Controlled Account edit

Only after read-only passes.

Move account writes behind use case.

Verify:
- permission;
- audit;
- validation;
- concurrency;
- failure recovery.

Gates:
- `G6_FINANCE_READ_PILOT_LOCK`
- `G7_FINANCE_WRITE_PILOT_LOCK`

Architecture may be revised here before scaling.

---

# 12. PHASE 5 — Day Console

## P5.1 Day overview

Replace Dashboard as a standalone concept.

Display:
- active day;
- branch/cashier completion;
- attention only;
- readiness;
- recovery;
- deep actions.

No analytics-for-decoration.

## P5.2 Attention Queue

Types:
- not started;
- incomplete;
- recovery draft;
- reconciliation difference;
- electronic issue;
- account/limit issue;
- close blocker.

Selecting an item opens the actual work item.

## P5.3 Day readiness

Readiness is derived from explicit rules.

It must never imply “safe to close” when blockers exist.

Gate:
`G8_DAY_CONSOLE_OVERVIEW_LOCK`

---

# 13. PHASE 6 — Cashier Workbench

Highest operator-efficiency slice.

## P6.1 Context

Lock/display:
- cashier;
- branch;
- POS;
- shift;
- business day;
- save/recovery state.

## P6.2 IQD entry

Support:
- denomination fields;
- arithmetic expressions;
- direct Iraqi total where allowed;
- live totals;
- validation.

## P6.3 Change

Separate visual/financial region.

## P6.4 USD

Separate visual/financial region.

No accidental mixing with IQD.

## P6.5 Keyboard contract

Explicit tests for:
- Enter
- Shift+Enter
- PageUp/PageDown
- Home/End
- Ctrl+Z/Ctrl+Y where supported
- Insert
- F5
- Esc
- Delete
- Ctrl+Delete
- text editing modifiers not stolen.

## P6.6 Save/recovery

Must prove:
- latest edit durability;
- dirty state;
- navigation handoff;
- DB-incarnation compatibility;
- failure/retry;
- no duplicate writes.

Gate:
`G9_CASHIER_WORKBENCH_LOCK`

---

# 14. PHASE 7 — Review, exceptions and close/reopen

## P7.1 Review mode

Absorb current Review Today capability.

Provide:
- branch totals;
- cashier totals;
- coarse/change/USD separation;
- anomaly list;
- missing/incomplete work.

## P7.2 Close flow

Before close:
- readiness checklist;
- blockers;
- permission;
- reason if required;
- resulting state.

## P7.3 Reopen

Requires:
- permission;
- reason;
- audit;
- visible day-state transition.

Gate:
`G10_DAY_LIFECYCLE_LOCK`

---

# 15. PHASE 8 — Reconciliation Studio

Largest migration.

## P8.1 Intake

Command:
Import.

Stages:
- select source;
- discover sheets;
- date/scope;
- validation;
- ambiguity;
- mapping readiness.

No silent “first valid sheet” behavior.

## P8.2 Result set

Dense grid:
- cashier;
- POS;
- reference;
- cash;
- electronic;
- adjustments;
- account;
- difference;
- state.

## P8.3 Inspector

Tabs:
- Summary
- Manual
- Electronic
- Account
- Evidence
- History

## P8.4 Manual resolution

Fields:
- type;
- amount;
- reason;
- notes;
- audit.

Difference updates live.

## P8.5 Electronic

Per cashier:
- Rafidain;
- SWITCH;
- imported transactions;
- add/remove allowed invoice behavior.

## P8.6 Account transfer

Show:
- account;
- invoice/reference;
- amount;
- discount;
- net;
- permission/limit override;
- resulting difference.

## P8.7 Exception queue

Navigate only unresolved:
- difference;
- unmapped;
- invalid;
- approval required.

## P8.8 Approval

Separate action.

Before commit:
- matched count;
- differences;
- overrides;
- financial effect;
- permission.

Tests:
- double-click/retry idempotency;
- signed values;
- account/electronic effects;
- audit;
- approval states.

Gate:
`G11_RECONCILIATION_STUDIO_LOCK`

---

# 16. PHASE 9 — Finance Ledger completion

## P9.1 Advances

One ledger:
- active;
- pending;
- settled;
- IQD;
- USD;
- giver/receiver;
- history;
- payments;
- documents.

## P9.2 Parties

Manage financial parties without separate modal workflow.

## P9.3 Owners / policies

Accounts:
- owners;
- discount;
- credit limits;
- override permissions;
- documents.

## P9.4 Cross-workspace linking

From reconciliation:
- open target account;
- preserve originating context;
- return to matching item.

Gate:
`G12_FINANCE_LEDGER_LOCK`

---

# 17. PHASE 10 — Reports Center

## P10.1 Catalog

Reports grouped by task, not by historical window.

Required examples:
- مراجعة وارد يوم;
- ملخص النقدي والإلكتروني;
- فروقات المطابقة;
- account statement;
- advances.

## P10.2 Filter contract

Filters are report-specific.

## P10.3 Preview

A4/portrait/branch rules remain faithful to source.

## P10.4 Export/print

Verify:
- PDF;
- Excel if required;
- print;
- no USD cents where specified;
- branch totals;
- data source fidelity.

## P10.5 Advanced design

Print designer is an advanced capability, not default surface.

Gate:
`G13_REPORTS_CENTER_LOCK`

---

# 18. PHASE 11 — Data Operations

## P11.1 Master data

Branches/Cashiers/POS.

All writes leave View code.

## P11.2 Import Pipeline

Exactly:
`Choose → Preview → Validate → Impact → Confirm → Result`

## P11.3 Transaction safety

Before commit show:
- new;
- updated;
- ignored;
- warning;
- error;
- destructive effect.

## P11.4 Protected maintenance

Reset/replace/delete operations require:
- permission;
- impact;
- explicit confirmation;
- transaction;
- audit;
- result.

Gate:
`G14_DATA_OPERATIONS_LOCK`

---

# 19. PHASE 12 — Administration & system states

## P12.1 Users and permissions

- list/search;
- effective permissions;
- custom mask;
- role;
- status;
- edit inspector.

## P12.2 Database & connection

- source;
- connection state;
- health;
- no secret leakage.

## P12.3 Backup/recovery

- backup;
- restore;
- maintenance barrier;
- session invalidation;
- DB incarnation rotation;
- rollback behavior.

## P12.4 Audit

Search/filter evidence.

## P12.5 Diagnostics

Operator-readable health information.

## P12.6 Login/onboarding

Rebuild:
- Login;
- First Run;
- Database choice;
- change password;
- lock/switch session.

Gate:
`G15_ADMIN_SESSION_LOCK`

---

# 20. PHASE 13 — Legacy UI retirement

For every old XAML class create a retirement record.

Example statuses:
- `DashboardView → MIGRATED_INTO_DAY_CONSOLE`
- `RevenueWorkspaceView → REMOVE_WRAPPER`
- `ReviewTodayView → MIGRATED_INTO_DAY_CONSOLE`
- `ReconciliationDetailsWindow → REPLACED_BY_INSPECTOR`
- `PendingAdvancesView → REMOVE_AFTER_RUNTIME_CONFIRMATION`
- `RevenueScreenCustomizationWindow → INTENTIONALLY_REMOVED`

Physical deletion only after:
- new route live;
- behavior tests pass;
- runtime acceptance;
- no remaining external reference;
- fallback window closed.

Gate:
`G16_LEGACY_UI_RETIREMENT_LOCK`

---

# 21. PHASE 14 — Performance, reliability and release

## P14.1 Performance

Compare against P0 baseline.

Measure:
- startup;
- workspace switch;
- cashier switch;
- grid scrolling;
- account search;
- reconciliation import;
- report preview;
- save latency;
- memory under repeated work.

Targets are locked from measured baseline, not guessed.

## P14.2 Failure drills

Test:
- DB unavailable;
- interrupted save;
- invalid import;
- corrupted draft;
- stale recovery;
- permission change;
- restore;
- app restart;
- long-running report/import cancellation.

## P14.3 Full regression

Run:
- unit;
- validation;
- integration;
- isolated UI;
- golden report/import fixtures.

## P14.4 Release

Evidence:
- installer;
- clean install;
- upgrade;
- first run;
- rollback;
- new DB;
- existing compatible DB;
- release notes.

Gates:
- `G17_REGRESSION_PERFORMANCE_CLEARANCE`
- `G18_RELEASE_CANDIDATE_LOCK`
- `G19_OWNER_RELEASE_APPROVAL`

---

# 22. Test pyramid

## Unit
For:
- calculations;
- validation;
- parsers;
- state reducers;
- formatting independent of UI.

## Application tests
For:
- use cases;
- permissions;
- result/error semantics;
- idempotency.

## Integration
For:
- EF;
- transactions;
- import;
- recovery;
- backup/restore;
- account posting.

## UI automation
For:
- navigation;
- keyboard;
- focus;
- inspector;
- tab lifecycle;
- critical commands.

## Visual acceptance
For:
- resolution/DPI;
- RTL;
- long Arabic;
- table alignment;
- Art Direction Lock.

No screenshot-only test replaces behavioral tests.

---

# 23. UX acceptance matrix

Every major workspace must pass:

### Identity
- Studio visual DNA visible without architecture imagery;
- not generic SaaS/Fluent;
- not old RevenueSystem.

### Task efficiency
- primary task obvious;
- no unnecessary popup;
- no navigation round trip for contextual detail.

### Keyboard
- normal path can be executed without mouse where required;
- native text editing preserved.

### Financial clarity
- signs;
- currency;
- source;
- difference;
- resulting state.

### State
- saving;
- dirty;
- loading;
- error;
- recovery;
- permission;
- offline/connection.

### Density
- 1366×768 remains practical;
- 1920×1080 uses space intelligently.

---

# 24. Migration control strategy

Use workspace-level migration switches.

Example:
```
UseNewFinanceLedger
UseNewDayConsole
UseNewCashierWorkbench
UseNewReconciliationStudio
UseNewReportsCenter
UseNewDataOperations
UseNewAdministration
```

Rules:
- switch exists only during migration;
- old/new never write competing state simultaneously;
- fallback is explicit;
- switch removed after retirement lock.

---

# 25. Branch/worktree strategy

Implementation branch pattern:
`rebuild/rs2-<phase>-<slice>`

Rules:
- one active implementation worktree for the slice;
- no editing the owner's unrelated branch;
- frequent checkpoint commits;
- each gate has a tagged/easily identifiable commit;
- merge only after gate evidence.

---

# 26. Handoff packet per slice

Every slice records:
- source SHA;
- branch;
- worktree;
- capability contract;
- art reference;
- architecture change;
- files changed;
- tests;
- runtime evidence;
- keyboard evidence;
- finance/data clearance;
- permissions;
- performance;
- known gaps;
- rollback;
- old UI migration state;
- result: ACCEPT / RETURN / HOLD.

---

# 27. Stop / return rules

Return upstream when:
- visual design violates Art Direction Lock;
- a use case requires View-owned persistence;
- finance parity fails;
- keyboard contract regresses;
- import/report source fidelity changes unexpectedly;
- performance degrades without explanation;
- a workaround bypasses permission/audit;
- UI animation interferes with task completion.

Do not “fix downstream” a bad upstream contract.

---

# 28. First execution packet after this plan

## RRS-P0 — Foundation Build Packet

### Step 1
Create clean RevenueSystem implementation worktree from:
`6886fbb6398b67b366faf3ca446dbae54eb1ce4f`

### Step 2
Create/verify isolated runtime contract.

### Step 3
Record current performance baseline.

### Step 4
Create new 2.0 design-system namespace/resources without importing old style dictionaries.

### Step 5
Build new empty Shell in Blend/Visual Studio:
- command rail;
- tabs;
- context bar;
- workbench;
- inspector host;
- status bar.

### Step 6
Implement Art Direction tokens:
- ivory;
- cobalt;
- clear/sky blue;
- parchment;
- brass;
- forest;
- charcoal;
- semantic red.

### Step 7
Build shared typography/numeric styles.

### Step 8
Prototype Finance Ledger read-only workspace.

### Step 9
Run MVVM pattern comparison.

### Step 10
Add AutomationIds/selectors.

### Step 11
Build and run in isolated profile.

### Step 12
Council review:
- Art
- UI/UX
- Architecture
- QA
- Workflow Efficiency

### P0 exit decision
- GO: scale to Finance Ledger pilot;
- REVISE: modify foundation;
- NO-GO: discard architecture prototype without touching production behavior.

No DB migration.
No production LAN.
No production data.
No replacement of current executable during P0.

---

# 29. Definition of RevenueSystem 2.0 complete

RevenueSystem 2.0 is complete only when:

1. all six workspaces pass their gates;
2. all retained financial capabilities are mapped and verified;
3. every old UI class has a retirement disposition;
4. no new View directly persists data;
5. permissions remain authoritative;
6. recovery/backup restore behavior is proven;
7. imports and reports pass golden fixtures;
8. keyboard acceptance passes;
9. Art Direction Lock passes across the product;
10. performance clearance passes;
11. installer/upgrade/rollback pass;
12. Owner release approval is explicit.

The product is **not complete** because it looks finished.
The product is **not complete** because it builds.
The product is **not complete** because one workflow works.

It is complete when the rebuilt visual/interaction system and the verified financial system operate as one coherent product.
