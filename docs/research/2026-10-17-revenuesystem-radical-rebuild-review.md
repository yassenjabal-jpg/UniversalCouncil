# RevenueSystem 2.0 — Radical Rebuild Council Review
Date: 2026-10-17
Status: COUNCIL REVIEW COMPLETE — PRODUCT IMPLEMENTATION NOT STARTED
RevenueSystem source pin: `6886fbb6398b67b366faf3ca446dbae54eb1ce4f`
Review profile: SOURCE-ONLY / STATIC / NO PROD DB / NO LAN / NO RUNTIME CLAIMS

## Governing owner decision

The current RevenueSystem UI is **not** an implementation template for RevenueSystem 2.0.

The owner has authorized:
- deleting screens;
- merging screens;
- splitting screens;
- creating new screens/workspaces;
- changing navigation;
- changing shell;
- changing workflow presentation;
- removing low-value UI features;
- replacing modal-heavy interaction with contextual workspaces;
- redesigning the information architecture from first principles.

What remains authoritative:
1. financial truth;
2. persistence/data integrity;
3. security/permission semantics;
4. auditability;
5. keyboard/operator efficiency where it is proven useful;
6. externally visible report/import/output behavior that the business still needs.

The current UI is now **behavioral evidence only**.

---

# 1. Source findings

Pinned main analysis found:

| Area | Current source |
|---|---:|
| Product C# files | 232 |
| XAML files | 50 |
| View/code-behind source group | 48 |
| XAML screen/window classes | 38 |
| Service files | 110 |
| ViewModel files | 0 |
| EF DbSets | 32 |
| EF migrations | 15 |
| Current top-level navigation destinations | 8 |
| Permission flags | 30 |

Current top-level destinations:
1. Dashboard
2. Daily Revenue
3. Reconciliation
4. Advances
5. Account Statement
6. Reports
7. Data Management
8. System & Settings

Council finding: these eight destinations reflect historical feature growth, not the optimal product model.

---

# 2. Current presentation complexity

Key hotspots:

| Surface | XAML | code-behind incl. partials | Named controls | events | direct DbContext refs | SaveChanges in View |
|---|---:|---:|---:|---:|---:|---:|
| CashierEntryView | 408 | 2,434 | 61 | 23 | 6 | 0 |
| ReconciliationView | 1,019 | 1,765 | 61 | 48 | 3 | 0 |
| ReconciliationDetailsWindow | 343 | 1,384 | 96 | 26 | 4 | 0 |
| DataManagementView | 125 | 2,154 | 66 | 39 | 9 | 6 |
| ReviewTodayView | 151 | 1,370 | 15 | 4 | 2 | 0 |
| RevenueEntryView | 178 | 1,285 | 28 | 16 | 4 | 3 |
| AdvancesView | 245 | 1,020 | 19 | 9 | 2 | 0 |
| MainWindow | 291 | 1,323 | 32 | 18 | 2 | 0 |
| DashboardView | 381 | 562 | 39 | 7 | 3 | 0 |
| AccountStatementView | 200 | 384 | 31 | 12 | 0 | 0 |

Interpretation:
- the current problem is not “large XAML” alone;
- the UI often owns orchestration, persistence context, navigation, dialogs, concurrency and state;
- copying the old screen boundaries into new XAML would preserve the same architecture problem.

---

# 3. Current wrapper/workspace structure

Current source already contains intermediate wrappers:

- `RevenueWorkspaceView` → entry/review
- `ReportsWorkspaceView` → reports/designer
- `DataManagementWorkspaceView` → master-data/import
- `SystemWorkspaceView` → settings/users/audit/connection

These wrappers prove the old “one sidebar item = one screen” model has already begun collapsing internally.

Council decision:
**Do not carry these wrapper classes into 2.0 as product concepts.**
They are migration scaffolding, not final information architecture.

---

# 4. Reachability / redundancy finding

`PendingAdvancesView` has **0 external source references** in the pinned product source.

The active pending-advances path is routed through `AdvancesView.ShowPendingTab()`.

Decision:
- treat `PendingAdvancesView` as dead/legacy UI candidate;
- do not reproduce it in 2.0;
- verify with tests/runtime before physical source deletion.

This is an example of the new rule:
**absence of business need beats historical screen preservation.**

---

# 5. Council positions

## Architecture
Position:
Do not perform a big-bang rewrite of financial/data logic.

Approve:
- new presentation/application layer;
- progressive extraction;
- adapters around verified existing services;
- no DbContext ownership in new Views;
- no direct SaveChanges in new Views.

Reject:
- “copy old code-behind then clean it later”;
- new giant ViewModels replacing giant code-behind;
- framework migration with no business benefit.

## UI/UX
Position:
Destroy the old information architecture as a constraint.

Approve:
- workspace tabs;
- narrow navigation rail;
- contextual inspector;
- command palette;
- detail panes;
- progressive disclosure;
- task-centric flows.

Reject:
- mandatory wide sidebar;
- dashboard-first design;
- permanent cards for all metrics;
- modal window for every edit/details action.

## Workflow Efficiency
Position:
Organize the product around the operator's work cycle, not historical modules.

Primary cycle:
**Open day → enter cash → review exceptions → reconcile → resolve financial exceptions → approve/close → report/audit.**

The UI should make this path continuous.

## Finance
Position:
Screen boundaries are irrelevant to financial correctness.

Hard requirements:
- currency separation;
- reconciliation equation fidelity;
- approval with/without difference rules;
- discount/credit-limit override rules;
- account posting integrity;
- no duplicate posting;
- day identity;
- audit trail.

## Data
Position:
Keep schema/data compatibility first.

No migration is justified merely because a screen changed.

Data-management writes must move behind use-case/application commands.

## Security
Position:
Permission checks belong to use cases/services, not only hidden buttons.

The current 30 permission flags remain behavioral requirements until deliberately revised.

## Interaction / Keyboard
Position:
Keyboard-first does not imply old layouts.

Preserve productive shortcuts where validated, but redesign focus zones, command routing and discoverability.

## I/O / Reports
Position:
Imports become staged workflows.
Reports become one report center.
Export/print are output capabilities, not separate UX concepts.

## Performance
Position:
Avoid a full Visual-Studio-style docking framework in v1 of the rebuild.

Approve:
- workspace tabs;
- optional split view;
- one contextual inspector;
- virtualization;
- deferred details.

Do not create arbitrary user docking until measured need exists.

## QA / Red Team
Position:
Every removed screen must map to either:
1. removed business capability, explicitly owner-approved; or
2. migrated capability with parity evidence.

No “we merged it” claim without use-case mapping.

---

# 6. New product topology

The Council recommends reducing the visible product from **8 top-level destinations to 6 workspaces**.

## Workspace 1 — اليوم / Day Console

Purpose:
Own the operational business day.

Absorbs:
- DashboardView
- RevenueWorkspaceView
- RevenueEntryView
- ReviewTodayView
- day close/reopen portions
- operational attention relevant to the selected day

Contains modes:
- Overview / Attention
- Revenue Entry
- Review & Exceptions
- Close / Reopen

Cashier entry opens as a work item inside this workspace, not as a separate top-level destination.

## Workspace 2 — المطابقة / Reconciliation Studio

Purpose:
Own all reconciliation work from import to approval.

Absorbs:
- ReconciliationView
- ReconciliationDetailsWindow
- AutoLinkPreviewWindow
- MappingWarningWindow
- ReconciliationImportScopeWindow
- CustomerInvoiceTransferWindow portions
- RevenueSettlementWindow portions
- reconciliation documents/profile/mapping flows

Major regions:
- import/context;
- result set;
- selected-cashier inspector;
- manual/electronic/account resolution;
- evidence/history;
- approval.

## Workspace 3 — المالية / Finance Ledger

Purpose:
Own durable financial counterparties and ledgers.

Absorbs:
- AccountStatementView
- CustomerAccountEditorWindow
- AccountOwnersWindow
- AdvancesView
- FinancialPartiesWindow
- active pending-advance behavior

Sections:
- Accounts
- Advances
- Financial Parties
- Owners / Policy

This is where account/advance state is managed outside a specific reconciliation action.

## Workspace 4 — التقارير / Reports Center

Purpose:
Own report discovery, preview and output.

Absorbs:
- ReportsView
- ReportsWorkspaceView
- PrintDesignerView
- ReportBranchOrderWindow

Layout:
catalog → filter context → preview → export/print.

Advanced designer is hidden behind an advanced action, not the default workflow.

## Workspace 5 — البيانات / Data Operations

Purpose:
Own master data and bulk data change.

Absorbs:
- DataManagementView
- DataManagementWorkspaceView
- ExcelImportView
- master-data import/replace/reset flows
- protected destructive data operations

Sections:
- Branches
- Cashiers
- POS
- Accounts/reference entities as appropriate
- Import Pipeline
- Maintenance

Import pattern:
Choose → Preview → Validate → Impact → Confirm → Result.

## Workspace 6 — الإدارة / Administration

Purpose:
Own system configuration and governance.

Absorbs:
- SettingsView
- SystemWorkspaceView
- ConnectionSettingsView
- UsersManagementView
- UserEditWindow
- AuditLogView
- backup/restore
- diagnostics
- permissions

Sections:
- Users & Roles
- Database & Connection
- Backup & Recovery
- Appearance & Output Defaults
- Audit
- Diagnostics

---

# 7. Global shell redesign

The Council rejects the current permanent wide sidebar as a mandatory 2.0 structure.

Recommended shell:

## A. Narrow right command rail
Approximately 52–60 px.
Contains six workspace icons.
Expands temporarily or via command palette, not permanently consuming space.

## B. Workspace tab strip
Allows several work items to remain open:
- Day / cashier Ahmed
- Reconciliation / branch Hillah
- Account / Company X
- Report / Differences

Tabs are product work items, not browser tabs.

## C. Business Context Bar
Persistent when relevant:
- financial date;
- branch/scope;
- day state;
- database/source state;
- current user.

## D. Workbench
Primary task region.

## E. Context Inspector
Optional right/left contextual pane depending RTL composition.
Used for selected cashier/account/import/report details.

## F. Status Bar
Small:
- save state;
- background work;
- connectivity;
- recovery;
- keyboard hints when relevant.

## G. Command Palette
Keyboard-first command search for:
- navigate;
- open cashier;
- open account;
- import;
- create report;
- execute allowed admin action.

No command palette action bypasses permissions.

---

# 8. Screen-by-screen disposition matrix

| Current UI class | 2.0 decision | Destination | Notes |
|---|---|---|---|
| DashboardView | DELETE standalone UI | Day Console | attention + day summary become Day Console mode |
| RevenueWorkspaceView | DELETE wrapper | Day Console | wrapper has no independent product value |
| RevenueEntryView | REBUILD / SPLIT | Day Console | cashier list/context + entry launch; remove View-owned persistence |
| CashierEntryView | REBUILD FROM BEHAVIOR | Day Console work item | preserve keyboard and save/recovery contracts, not layout |
| ReviewTodayView | MERGE | Day Console | becomes Review & Exceptions / Close mode |
| ReconciliationView | SPLIT / REBUILD | Reconciliation Studio | old 1,019-line screen is not a target layout |
| ReconciliationDetailsWindow | DELETE as window | Reconciliation Inspector | detail becomes contextual pane/sub-workspaces |
| AutoLinkPreviewWindow | MERGE | Reconciliation Mapping | inline preview |
| MappingWarningWindow | MERGE | Reconciliation Issues | inline issue resolver |
| ReconciliationImportScopeWindow | MERGE | Reconciliation Import step | staged import scope |
| RevenueSettlementWindow | MERGE / SPLIT | Reconciliation + Finance actions | convert into contextual financial resolution |
| CustomerInvoiceTransferWindow | MERGE | Reconciliation Inspector / Finance | account transfer action |
| AccountStatementView | REBUILD | Finance Ledger / Accounts | good behavior pilot, new shell |
| CustomerAccountEditorWindow | MERGE | Finance Account Inspector | inline/create sheet where necessary |
| AccountOwnersWindow | MERGE | Finance / Owners | no standalone window |
| AdvancesView | REBUILD | Finance Ledger / Advances | retain ledger behavior |
| PendingAdvancesView | REMOVE candidate | Finance / Advances | source currently unreachable |
| FinancialPartiesWindow | MERGE | Finance / Parties | no standalone window |
| ReportsWorkspaceView | DELETE wrapper | Reports Center | no product value as wrapper |
| ReportsView | REBUILD | Reports Center | report catalog + filters + preview |
| PrintDesignerView | KEEP capability, MOVE | Reports / Advanced | not primary UI |
| ReportBranchOrderWindow | MERGE | Report options | inline/report settings sheet |
| DataManagementWorkspaceView | DELETE wrapper | Data Operations | direct module navigation |
| DataManagementView | SPLIT / REBUILD | Data Operations | eliminate View-owned SaveChanges |
| ExcelImportView | MERGE / REBUILD | Data Import Pipeline | staged transaction-aware process |
| DestructiveConfirmationWindow | REPLACE with shared component | Shared Safety UX | destructive confirmation remains |
| SettingsView | SPLIT | Administration | backup/settings/diagnostics separated by task |
| SystemWorkspaceView | DELETE wrapper | Administration | module owns sections directly |
| ConnectionSettingsView | MERGE / REBUILD | Admin / DB & Connection | source/connection/recovery state |
| UsersManagementView | MERGE | Admin / Users | inspector-based |
| UserEditWindow | DELETE as window | Admin User Inspector | create/edit inside module |
| AuditLogView | MERGE | Admin / Audit | filter + evidence pane |
| ChangePasswordWindow | KEEP compact secure action, REDESIGN | User/session menu | modal is acceptable here |
| LoginWindow | REBUILD | Session Gate | not a product workspace |
| FirstRunAdminWindow | REBUILD | Onboarding | wizard step |
| FirstRunDatabaseChoiceWindow | REBUILD | Onboarding | data source step |
| ReasonDialogWindow | REPLACE shared action sheet | Shared Safety UX | short modal justified |
| OperationalOrderWindow | MERGE | Global Work Queue / action panel | remove generic standalone window if behavior permits |
| RevenueScreenCustomizationWindow | REMOVE feature candidate | — | arbitrary layout editing conflicts with coherent design system unless owner later proves need |

---

# 9. Features proposed for removal or reduction

## 9.1 Arbitrary revenue-screen layout customization
Current:
- `RevenueScreenCustomizationWindow`
- `RevenueScreenLayoutService`
- `InteractiveLayoutEditor`

Council recommendation:
**Do not carry arbitrary screen-layout editing into the initial 2.0 product.**

Reason:
- creates unbounded layout states;
- complicates automation and support;
- conflicts with a coherent adaptive design system;
- creates persistence and regression surface with little proven business value.

Replace with:
- Compact / Comfortable density;
- column visibility/preferences where justified;
- saved filters;
- possibly user-specific table column order.

## 9.2 Legacy duplicate pending-advances UI
Remove after runtime/reachability proof.

## 9.3 Modal proliferation
Most domain windows become:
- inspector;
- inline step;
- side sheet;
- work item tab.

Keep modal only for:
- destructive confirmation;
- reason/approval;
- credential/session gate;
- very small bounded decisions.

---

# 10. Day Console redesign in detail

The old Dashboard is removed as a destination.

Opening the program after authentication lands on:
**Day Console for the active financial day.**

It has a continuous operational narrative:

### Header
- financial day;
- status;
- scope/branch;
- connectivity;
- recovery state.

### Attention Queue
Only actionable exceptions:
- incomplete cashier;
- unsaved/recovery draft;
- reconciliation difference;
- pending close condition;
- import warning.

### Revenue Grid
Branch → cashier completion model.
Open a cashier as a work item.

### Review mode
Aggregated totals and exceptions.

### Close mode
Explicit readiness checklist:
- missing cashiers;
- unresolved blockers;
- reconciliation state where required;
- close reason/approval rules.

This replaces the psychological split between:
Dashboard → Revenue → Review Today.

---

# 11. Cashier Workbench redesign

The cashier screen becomes a focused workbench.

It retains:
- cashier/branch/POS/shift/day identity;
- denomination arithmetic;
- IQD/change/USD separation;
- direct amount where allowed;
- save state;
- recovery state;
- keyboard behavior;
- settlement/reconciliation links.

It removes:
- unrelated navigation;
- arbitrary layout-editing affordances;
- hidden state transitions.

Proposed structure:
1. identity/context strip;
2. entry grid;
3. totals/validation strip;
4. recovery/save status;
5. contextual actions.

The operator should be able to complete normal entry without mouse use.

---

# 12. Reconciliation Studio redesign in detail

Reconciliation is treated as a product inside the product.

## Stage 1 — Intake
- source file;
- date/scope;
- validation;
- ambiguity resolution;
- mapping readiness.

## Stage 2 — Result set
One row per cashier/context.
Primary columns are configurable but stable.

## Stage 3 — Selected item inspector
Tabs:
- Summary
- Manual
- Electronic
- Account Transfer
- Evidence
- History

## Stage 4 — Exception queue
Quick sequence through only:
- differences;
- unmapped;
- validation failures;
- required approvals.

## Stage 5 — Approval
Approval is a separate state transition.
It is never visually adjacent to import by accident.

This absorbs most of the current popup graph.

---

# 13. Finance Ledger redesign in detail

Current accounts, advances and financial parties are close business concepts but fragmented by historical screens.

Finance Ledger provides:

## Accounts
- account browser;
- ledger;
- invoices/payments;
- credit/discount policy;
- documents.

## Advances
- active;
- pending;
- settled/history;
- giver/receiver;
- currency/reference.

## Parties
- people/companies/entities used by finance workflows.

Cross-links:
- reconciliation transfer → opens/pins target account;
- advance party → opens party details;
- report → opens filtered ledger.

This reduces context switching.

---

# 14. Data Operations redesign in detail

Current `DataManagementView` is one of the strongest architecture boundaries to replace because it directly persists from presentation.

New rule:
**No master-data write from View code.**

Use cases:
- Create/update branch;
- Create/update cashier;
- POS management;
- import preview;
- import validate;
- import commit;
- replace;
- reset/protected maintenance.

Every bulk/destructive action:
Preview → Impact → Permission → Confirmation → Transaction → Result.

---

# 15. Administration redesign in detail

System features are separated by operational risk.

## Normal settings
- theme/density;
- report defaults;
- user preferences.

## Governance
- users;
- roles;
- permissions;
- audit.

## Infrastructure
- database/source;
- connection status;
- backups;
- restore;
- health/diagnostics.

Destructive infrastructure actions are not visually mixed with ordinary appearance settings.

---

# 16. Permission model mapping

The current 30 AppPermission flags are not mapped 1:1 to navigation.

A workspace may appear while individual commands remain unavailable.

Examples:
- Finance Ledger can open read-only while ManageSpecialAccounts is absent.
- Reconciliation can allow review but not approve-with-difference.
- Administration can expose audit without user management.
- Reports Center can show allowed reports while sensitive reports remain filtered.

This is cleaner than hiding entire product areas because one sub-action is forbidden.

---

# 17. New architecture boundary

Target presentation path:

```
Shell / Workspace
    ↓
Feature ViewModel or Coordinator
    ↓
Application Use Case / Facade
    ↓
Domain Service Adapter
    ↓
Existing verified Service / EF infrastructure
```

Rules:
- View never constructs AppDbContext.
- View never calls SaveChanges.
- View does not instantiate domain services.
- permission checks remain in authoritative service/use-case paths;
- ViewModel does not become a “god object”;
- use cases are task-oriented, not table-oriented.

No mandatory DI framework decision yet.
Composition strategy is decided by spike evidence.

---

# 18. Migration method

Do not build a second complete app in isolation and switch on one day.

Use progressive parallel migration.

For each workspace:
1. define behavior contract;
2. build new use cases/adapters;
3. build new UI;
4. run synthetic parity;
5. isolated runtime;
6. operator/keyboard acceptance;
7. finance/data clearance;
8. switch route to new workspace;
9. retain old route behind temporary fallback;
10. remove old UI only after closure.

---

# 19. Recommended implementation order

1. Shell + workspace system
2. Account/Finance read-only pilot
3. Day Console
4. Cashier Workbench
5. Review/Close
6. Reconciliation Studio
7. Reconciliation financial resolution
8. Finance Advances/Parties
9. Reports Center
10. Data Operations
11. Administration
12. Onboarding/session modernization
13. dead UI deletion
14. performance/reliability hardening
15. release migration

Why Finance read-only first:
- exercises real financial data;
- lower write risk;
- tests master/detail/ledger/filters;
- validates architecture before high-risk cashier/reconciliation migration.

---

# 20. Council final verdict

**The current UI architecture should not be preserved.**

Preserve:
- behavioral truth;
- financial rules;
- data compatibility;
- permissions;
- audit;
- proven keyboard workflows;
- import/report contracts.

Rebuild:
- shell;
- navigation;
- screen topology;
- interaction model;
- information hierarchy;
- visual system;
- application/presentation boundaries.

Delete:
- wrapper-only screens after migration;
- unreachable UI;
- arbitrary layout customization unless later justified;
- most domain-specific modal windows.

The target is not “RevenueSystem v5 with a new theme.”

The target is:
**RevenueSystem 2.0 — a day-centric, workspace-based financial operations environment.**
