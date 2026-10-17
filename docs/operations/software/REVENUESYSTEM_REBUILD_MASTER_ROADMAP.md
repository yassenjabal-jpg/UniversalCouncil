# RevenueSystem 2.0 — Master Rebuild Roadmap
Version: 2.1
Date: 2026-10-17
Status: OWNER-APPROVED / DETAILED EXECUTION PLAN LOCKED

## Detailed execution authority

The detailed execution plan is authoritative for implementation sequencing:
`docs/operations/software/REVENUESYSTEM_2_DETAILED_REBUILD_PLAN.md`

The Art Direction is owner-locked:
`docs/operations/software/REVENUESYSTEM_2_ART_DIRECTION_LOCK.md`

## Governing premise

The current RevenueSystem UI is a behavioral reference only.

RevenueSystem 2.0 is rebuilt around six workspaces:
1. Day Console
2. Reconciliation Studio
3. Finance Ledger
4. Reports Center
5. Data Operations
6. Administration

Login/lock/onboarding are system states.

The old eight-destination sidebar and legacy screen/window boundaries are not implementation requirements.

---

# PHASE A — BEHAVIOR CONTRACT

## A0 Source lock
- pin RevenueSystem main;
- pin governing docs/tests;
- use clean detached analysis/runtime worktree;
- no production DB/LAN inheritance.

Gate: `SOURCE_ENVIRONMENT_LOCK`

## A1 Capability inventory
For every legacy screen/function record:
- business capability;
- inputs;
- outputs;
- persistence;
- audit;
- permissions;
- failure/retry;
- keyboard;
- report/import dependencies.

Gate: `CAPABILITY_MAP_LOCK`

## A2 Golden synthetic data
Build deterministic isolated fixture representing:
- multiple branches/cashiers/POS;
- IQD coarse/change/USD;
- electronic payment;
- match/difference/unmapped cases;
- accounts;
- advances;
- open/closed business days;
- permission variants;
- Arabic long text and large numeric values.

Gate: `GOLDEN_FIXTURE_LOCK`

## A3 Executable invariants
Turn current tests/requirements into compatibility contracts.

Gate: `BEHAVIOR_INVARIANTS_LOCK`

---

# PHASE B — PRODUCT & ARCHITECTURE FOUNDATION

## B0 New shell prototype
Primary GUI: Visual Studio + Blend.

Prototype:
- narrow RTL command rail;
- workspace tabs;
- business context bar;
- workbench;
- optional inspector;
- status bar;
- command palette.

No financial writes.

## B1 Presentation architecture spike
Pilot CommunityToolkit.Mvvm versus minimal hand-written ViewModel pattern.

Target path:
`View → ViewModel/Coordinator → Application Use Case → Adapter → verified service/data`

No View-owned DbContext/SaveChanges.

## B2 Design system
Only:
1. Native Fluent baseline
2. Semantic Tokens
3. Shared Components
4. Feature-local styles

No historical resource dictionary imported wholesale.

## B3 Automation contract
Stable automation identity and focus behavior.

GUI execution:
`OBSERVE → LOCATE → ACT → OBSERVE → VERIFY → CHECKPOINT`

Gate: `PRODUCT_FOUNDATION_LOCK`

---

# PHASE C — FINANCE PILOT

## C1 Finance Ledger read-only pilot
Use Accounts as first real slice.

Build:
- account browser;
- ledger;
- filters;
- KPI/summary;
- inspector;
- workspace tab behavior.

Why:
- real financial semantics;
- lower write risk than revenue/reconciliation;
- validates data adapters and UI architecture.

Gate: `FINANCE_READONLY_PILOT_LOCK`

## C2 Finance write pilot
Add controlled create/edit account action behind application use case.

Verify permissions/audit/concurrency.

Gate: `FINANCE_WRITE_PILOT_LOCK`

If either pilot fails, architecture is revised before scaling.

---

# PHASE D — DAY CONSOLE

## D1 Day overview
Replace standalone Dashboard.

Build:
- day context;
- attention queue;
- branch/cashier completion;
- recovery warnings;
- deep links.

## D2 Cashier selector/work items
Open cashier entry as a work item tab.

## D3 Cashier Workbench
Rebuild from behavior, not old layout.

Preserve:
- denomination arithmetic;
- IQD/change/USD separation;
- save/recovery;
- keyboard contract.

Remove:
- arbitrary layout editor.

## D4 Review & Exceptions
Absorb ReviewToday.

## D5 Close/Reopen
Explicit readiness and reason/permission flow.

Gate: `DAY_CONSOLE_LOCK`

---

# PHASE E — RECONCILIATION STUDIO

## E1 Intake
- import;
- date/scope;
- validation;
- ambiguity;
- mapping readiness.

## E2 Result set
Dense cashier reconciliation grid/list.

## E3 Inspector
Selected cashier:
- summary;
- manual;
- electronic;
- account transfer;
- evidence;
- history.

## E4 Exception queue
Only unresolved:
- differences;
- unmapped;
- invalid;
- approval-required.

## E5 Approval
Separate state transition with effect summary.

Legacy windows replaced by contextual panes/steps after parity:
- ReconciliationDetailsWindow
- AutoLinkPreviewWindow
- MappingWarningWindow
- ReconciliationImportScopeWindow
- CustomerInvoiceTransferWindow portions
- RevenueSettlementWindow portions

Gate: `RECONCILIATION_STUDIO_LOCK`

---

# PHASE F — FINANCE LEDGER COMPLETE

## F1 Advances
Active/pending/settled in one ledger.

## F2 Parties
Financial parties integrated.

## F3 Owners/policies
Account owners, discounts, credit limits, documents.

## F4 Cross-workspace links
Reconciliation transfer opens/pins target account.

Gate: `FINANCE_LEDGER_LOCK`

---

# PHASE G — REPORTS CENTER

Build:
catalog → filters → preview → export/print.

Absorb:
- ReportsView
- ReportsWorkspaceView
- PrintDesignerView as advanced capability
- ReportBranchOrderWindow into options.

Verify source fidelity and report layout rules.

Gate: `REPORTS_CENTER_LOCK`

---

# PHASE H — DATA OPERATIONS

## H1 Master-data query/edit
Move all writes behind application commands.

## H2 Import pipeline
Choose → Preview → Validate → Impact → Confirm → Result.

## H3 Protected maintenance
Replace/reset/destructive operations with permission + impact + transaction + result.

Gate: `DATA_OPERATIONS_LOCK`

---

# PHASE I — ADMINISTRATION

## I1 Users & Roles
Inspector-based user management.

## I2 Database & Connection
Connection/source state.

## I3 Backup & Recovery
Protected infrastructure actions.

## I4 Audit & Diagnostics
Searchable evidence and system health.

## I5 Normal settings
Appearance, density, output defaults.

Gate: `ADMINISTRATION_LOCK`

---

# PHASE J — SESSION & ONBOARDING

Rebuild:
- LoginWindow
- FirstRunAdminWindow
- FirstRunDatabaseChoiceWindow
- lock/change-password flows

They remain system states, not workspaces.

Gate: `SESSION_ONBOARDING_LOCK`

---

# PHASE K — LEGACY UI RETIREMENT

For each old class mark:
- migrated;
- removed intentionally;
- temporary fallback;
- onboarding/system-only.

Delete only after:
- behavior parity;
- route replacement;
- tests;
- isolated runtime evidence.

Priority removal candidates:
- wrapper-only workspaces;
- PendingAdvancesView after runtime confirmation;
- arbitrary revenue layout customization;
- domain modal windows replaced by inspectors/steps.

Gate: `LEGACY_UI_RETIREMENT_LOCK`

---

# PHASE L — PERFORMANCE & RELEASE

Measure:
- startup;
- workspace switch;
- cashier open;
- grid scroll;
- filter/search;
- reconciliation import;
- report generation;
- save latency;
- memory after repeated work-item navigation.

Release requirements:
- full build;
- focused + integration + validation tests;
- isolated GUI/runtime acceptance;
- finance/data clearance;
- permission/security clearance;
- recovery/backup validation in isolated profile;
- installer/rollback evidence.

Gates:
- `REGRESSION_PERFORMANCE_CLEARANCE`
- `RELEASE_CANDIDATE_LOCK`
- `OWNER_RELEASE_APPROVAL`

---

# Studio tool assignment

## GUI primary
- Visual Studio 2026: implementation/debug/test explorer
- Blend: WPF layout/templates/states
- RevenueSystem runtime: operator behavior proof
- YASSIN Control Bridge: semantic GUI automation and verified actions

## DC secondary
- Git/worktrees
- files
- builds/tests
- logs
- metrics
- process control
- evidence collection

## Design/reference
- Figma optional for exploration/reference
- Photoshop/Illustrator only for actual visual assets/branding

---

# Definition of Done per migrated slice

A slice is not complete unless it has:
- source pin;
- capability contract;
- design reference;
- application boundary;
- implementation;
- build;
- tests;
- isolated integration;
- runtime GUI verification;
- keyboard verification where relevant;
- finance/data verification where relevant;
- permissions verification;
- layout/DPI acceptance;
- logs reviewed;
- performance result;
- migration status for the old UI.

A screenshot is not completion.
A build is not completion.
A visual redesign is not completion.
