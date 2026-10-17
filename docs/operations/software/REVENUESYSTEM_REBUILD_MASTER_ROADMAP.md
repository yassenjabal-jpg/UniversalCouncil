# RevenueSystem / «المطابقة» — Master Rebuild Roadmap
Version: 1.0
Date: 2026-10-17
Status: COUNCIL-APPROVED PLAN CANDIDATE — NO PRODUCT IMPLEMENTATION YET

## Strategy

Rebuild the product experience and presentation architecture without blindly rewriting the validated financial/data engine.

Method:
**Parallel Presentation Rebuild + Application Facade + Progressive Boundary Extraction**

The existing program remains the behavior oracle until each migrated vertical slice passes parity.

---

# MACRO PHASE A — DISCOVERY & CONTRACT

## A0 — Source Freeze
Primary: GitHub + DC

Deliver:
- current main SHA;
- exact worktree;
- project/test inventory;
- governing requirements map;
- historical requirement conflict list.

Gate:
**G0 SOURCE_ENVIRONMENT_LOCK**

Current pin:
`6886fbb6398b67b366faf3ca446dbae54eb1ce4f`

## A1 — Feature Behavior Matrix
Council owners:
Requirements + Finance + Data + QA + operator-workflow

For every feature record:
- input;
- output;
- side effects;
- permission;
- persistence;
- audit;
- failure behavior;
- keyboard;
- reports affected;
- restore/retry behavior.

Features:
1. shell/session/day
2. dashboard
3. daily revenue
4. review day
5. reconciliation
6. manual reconciliation
7. electronic payment
8. account transfer
9. account statement
10. advances
11. imports
12. reports
13. data management
14. users/permissions
15. DB/network/system
16. backup/recovery
17. printing/export
18. installer/update

## A2 — Golden Synthetic Dataset
No production data.

Create deterministic fixture containing:
- 5 branches;
- representative cashiers/POS/shifts;
- positive and negative amounts;
- IQD coarse/change/USD;
- Rafidain/SWITCH;
- matched/unmatched/over/under cases;
- account transfer;
- advance;
- closed/open business days;
- permission variants;
- long Arabic names;
- large amounts;
- empty states.

This dataset becomes the comparison input for old/new behavior.

## A3 — Compatibility Contract
Convert existing tests and requirements into a named parity suite.

No screen can migrate without:
- inputs defined;
- expected financial outputs;
- expected persistence;
- expected keyboard behavior;
- expected failure/retry behavior.

Gate:
**G1 BEHAVIOR_INVARIANTS_LOCK**

---

# MACRO PHASE B — DESIGN & PREBUILD

## B0 — Architecture Spike

### Candidate architecture

```
WPF View
  ↓ binding/commands
Feature ViewModel / Coordinator
  ↓
Application Facade / Use Case
  ↓
Existing Verified Service Adapter  ← temporary migration seam
  ↓
Domain + EF/Data/Import/Report infrastructure
```

New UI must not create DbContext.

### Why this seam
It allows the new program to consume proven behavior before the entire legacy service layer is refactored.

## B1 — MVVM Prototype
Primary GUI: Visual Studio 2026

Prototype one non-critical feature:
**Account Statement read-only path**

Compare:
- plain hand-written ViewModel;
- CommunityToolkit.Mvvm.

Acceptance:
- clean unit testing;
- no hidden global messenger dependency;
- simple async commands;
- designer works;
- no measurable startup penalty.

## B2 — Native Fluent Prototype
Primary GUI: Blend + Visual Studio

Create:
- light/dark shell;
- RTL navigation;
- command bar;
- financial KPI strip;
- DataGrid;
- master-detail;
- dialog;
- status badge;
- focus states.

Use built-in WPF Fluent first.

Optional:
WPF UI targeted control spike only if native control gap appears.

## B3 — New Design System

Exactly these layers:

### 1. Native
WPF Fluent baseline.

### 2. Tokens
- spacing;
- typography;
- radii;
- semantic brushes;
- financial number styles;
- focus;
- density;
- motion durations.

### 3. Components
- Button variants;
- FinancialNumber;
- CurrencyAmount;
- StatusBadge;
- FilterBar;
- CommandBar;
- MetricStrip;
- FinancialDataGrid;
- EmptyState;
- LoadingState;
- InlineValidation;
- SideDetailPane;
- ConfirmActionDialog.

### 4. Feature-local
Only styles that cannot be shared.

No duplicate public keys.

## B4 — Navigation / Shell Contract

Right-side RTL rail:
- daily operations;
- matching & finance;
- analysis;
- administration.

Top context bar:
- business date;
- day state;
- DB/source state;
- current user;
- theme;
- pending/recovery indicator.

Content shell:
- page identity;
- primary action group;
- optional compact filters;
- main work surface;
- contextual details pane.

## B5 — Responsive Matrix

Required:
- 1280×720 compact
- 1366×768 compact/default
- 1600×900
- 1920×1080
- 125%/150% DPI
- light/dark
- long Arabic text

Use adaptive layout, not only fixed widths.

## B6 — UI Automation Contract

All interactive controls:
- stable AutomationId or semantic name;
- keyboard path;
- expected state property.

YASSIN Control Bridge:
`OBSERVE → LOCATE → ACT → OBSERVE → VERIFY → CHECKPOINT`

Gate:
**G2 UX_ARCHITECTURE_READY_LOCK**

---

# MACRO PHASE C — PRODUCTION & VERIFICATION

Each vertical slice:
1. Slice Contract
2. Visual design in Blend/Figma reference where useful
3. GUI implementation in Visual Studio/Blend
4. application facade/adapters
5. focused source tests
6. build
7. isolated runtime launch
8. GUI smoke
9. financial/data clearance
10. performance/layout check
11. old-vs-new parity
12. handoff lock

No downstream slice silently repairs upstream work.

---

# C1 — New Shell + Design System

Scope:
- window chrome;
- navigation;
- top context;
- theme;
- page host;
- notifications;
- standard dialogs;
- global shortcut routing.

Do not migrate financial logic yet.

Acceptance:
- 1280/1366/1920;
- RTL;
- light/dark;
- focus;
- Alt+1..8;
- no overlapping resource keys;
- startup baseline.

Gate:
**SHELL_LOCK**

---

# C2 — Account Statement (Pilot Vertical Slice)

Why first:
- moderate complexity;
- current view has relatively low direct persistence coupling;
- exercises list/detail/filter/KPI patterns;
- financial enough to test formatting but lower risk than reconciliation.

Build:
- account list;
- search/filter;
- account detail;
- KPI strip;
- statement grid;
- date filter;
- edit/create command routing.

Goal:
prove architecture, GUI workflow and test method.

Gate:
**PILOT_SLICE_LOCK**

If this slice fails, do not scale architecture to other screens.

---

# C3 — Dashboard

Redesign as operational briefing, not decorative cards.

Show:
- workday state;
- unresolved cashiers/branches;
- reconciliation exceptions;
- accounts needing attention;
- import/recovery warnings;
- recent operational actions.

Use drill-through links, not duplicate business logic.

---

# C4 — Daily Revenue / Cashier Entry

Highest operator-efficiency slice.

### Layout
Permanent cashier context header:
- cashier;
- branch;
- POS;
- shift;
- workday;
- save/recovery state.

Main entry matrix:
- denomination;
- expression;
- quantity/result;
- subtotal.

Separate:
- IQD coarse
- IQD change
- USD

Persistent summary:
- totals;
- saved state;
- anomaly hint.

### Keyboard acceptance
All preserved shortcuts become explicit tests.

### Architecture extraction
Old CashierEntry 1,998-line code-behind is not ported.
Move:
- input/navigation state → ViewModel/coordinator;
- save → application command;
- calculations → existing calculator/invariant service;
- draft/recovery → dedicated application service.

Gate:
**DAILY_REVENUE_LOCK**

---

# C5 — Review Today

Purpose:
exception-first operational review.

Primary model:
branch/cashier completion and anomalies.

Do not duplicate revenue-entry UI.

Actions should deep-link to exact cashier/issue.

---

# C6 — Reconciliation Core

This is the largest migration.

Do not rebuild 1,019-line XAML as another single page.

## Reconciliation layout

### Region 1 — Context & Import
- selected date/branch/scope
- source file/import state
- mapping completeness
- import/recalculate actions

### Region 2 — Reconciliation Score
Four persistent figures:
- Reference
- Program/Recorded
- Adjustments
- Difference

### Region 3 — Results
Toggle:
- cards for operational scanning
- table for dense audit

Filters:
- search
- state
- branch
- advanced overflow

### Region 4 — Detail Pane
Open on selected cashier without losing list position.

Tabs/sections:
- summary
- manual reconciliation
- electronic payments
- account transfer
- history/evidence

### Region 5 — Approval
Separate from import and editing.
Show effect summary before commit.

## Architecture
Create:
- ReconciliationWorkspaceViewModel
- ReconciliationQueryUseCase
- ReconciliationCommandUseCase
- detail sub-viewmodels
- immutable/display DTOs

Existing ReconciliationService remains behind adapter until parity.

Gate:
**RECONCILIATION_CORE_LOCK**

---

# C7 — Reconciliation Detail / Manual / Electronic / Transfer

Decompose the existing 96-control details window.

Prefer one contextual detail pane.
Use modal only when:
- destructive confirmation;
- reason entry;
- cross-workspace selection needing isolation.

Manual reconciliation equation stays visually persistent.

Electronic:
Rafidain/SWITCH breakdown.

Transfer:
account, invoice/reference, amount, optional fields, effect preview.

Gate:
**RECONCILIATION_FINANCE_LOCK**

---

# C8 — Advances

Build a ledger-oriented workspace:
- active/pending/history;
- giver/receiver;
- currency;
- sequence/reference;
- status;
- quick filters.

Do not mix IQD/USD totals.

---

# C9 — Reports / Print / Export

Pattern:
report catalog → dynamic filter bar → preview → output actions.

Separate renderer/export/print from UI.

Performance:
cancelable background generation with visible state.

Verify:
- portrait;
- one-page rules;
- Arabic;
- no cents where required;
- branch totals;
- source fidelity.

---

# C10 — Data Management / Imports

Before UI migration:
extract all direct SaveChanges from View to application commands.

Workspace:
- branches;
- cashiers;
- POS;
- financial parties;
- accounts/reference data;
- import.

For destructive/replace import:
preview → validation → effect summary → confirmation → transaction → result.

Gate:
**DATA_MANAGEMENT_LOCK**

---

# C11 — System / Security / Recovery

Areas:
- users/permissions;
- DB/source configuration;
- backup/restore;
- theme/printing;
- audit/diagnostics;
- recovery state.

Never mix routine appearance settings with destructive DB operations.

Sensitive actions get a separate high-risk visual treatment and reason/permission gates.

---

# C12 — Performance and Reliability Hardening

Measure:
- startup;
- navigation;
- first load per workspace;
- large grid scroll;
- search/filter latency;
- reconciliation import;
- report generation;
- save latency;
- memory after repeated navigation.

WPF rules:
- virtualization;
- recycling;
- defer hidden detail;
- avoid nested ScrollViewer around grids;
- reduce visual-tree depth;
- no unnecessary shadows/blur on dense surfaces.

Gate:
**G7 REGRESSION_PERFORMANCE_CLEARANCE**

---

# C13 — Migration / Release

The old executable remains available until:
- every required feature has a locked new slice;
- parity suite passes;
- migration schema compatibility passes;
- backup/restore path validated in isolated profile;
- installer clean-machine test passes.

Then:
- release candidate;
- owner acceptance;
- versioned migration plan;
- rollback package.

Gates:
**G8 RELEASE_CANDIDATE_LOCK**
**G9 OWNER_RELEASE_APPROVAL**

---

# 4. Tool assignment under the new Studio method

## Visual Studio Community 2026
Primary:
- architecture;
- C#;
- ViewModels/use cases;
- debug;
- test explorer.

## Blend for Visual Studio
Primary:
- WPF layout;
- templates;
- visual states;
- sizing/alignment;
- design-time inspection.

## RevenueSystem old/new runtime
Primary:
- behavior comparison;
- operator smoke;
- keyboard;
- layout/focus;
- failure states.

## Figma
Optional reference/design exploration.
Not implementation proof.

## Photoshop / Illustrator
Only for brand/icon assets.
Never for functional screen implementation.

## Desktop Commander
Secondary:
- Git;
- files;
- build/tests;
- logs;
- metrics;
- artifacts;
- recovery.

## YASSIN Control Bridge
Primary desktop interaction automation:
- Visual Studio;
- Blend;
- app runtime.

---

# 5. Council checkpoints per slice

Required voices are activated by impact.

Always:
- Architecture
- Requirements/Impact
- QA

Add:
- Finance for money
- Data for persistence
- Interaction for keyboard
- UI/UX for visual changes
- I/O for import/report/export
- Security for permissions/credentials
- Performance for large data/latency
- Release for installer/environment

No ceremonial full-council round when it cannot change the decision.

---

# 6. Definition of Done

A rebuilt slice is DONE only with:
- source pin;
- acceptance contract;
- visual reference;
- implementation;
- build PASS;
- focused tests PASS;
- isolated integration PASS;
- runtime launch PASS;
- GUI automation/smoke PASS;
- keyboard PASS where relevant;
- finance/data PASS where relevant;
- layout matrix PASS;
- logs reviewed;
- performance budget PASS or recorded;
- handoff accepted.

A screenshot alone is never completion.
A build alone is never completion.
A council vote alone is never completion.

---

# 7. First implementation packet after plan approval

**RRS-P0 — Architecture & Visual Foundation Spike**

Deliverables:
1. isolated runtime profile contract;
2. native Fluent shell prototype;
3. CommunityToolkit.Mvvm pilot comparison;
4. optional WPF UI targeted control spike;
5. single non-palette token/component dictionary prototype;
6. Account Statement pilot wireframe in Blend;
7. GUI automation selector convention;
8. baseline performance measurements;
9. go/no-go decision for architecture.

No database migration.
No production LAN.
No replacement of current app.
No release.

This is the safest first execution step.
