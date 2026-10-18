# RevenueSystem 2.0 — Phase 6 Cashier Workbench Pre-Open Contract

Date: 2026-10-18  
Status: **PREPARED_NOT_OPEN**  
Prerequisite: `G8_DAY_CONSOLE_OVERVIEW_LOCK = PASS`  
Planned gate: `G9_CASHIER_WORKBENCH_LOCK`

This packet is source archaeology and acceptance preparation only. It does not open Phase 6 and does not authorize product changes before G8 closes.

## North-star operator loop

`select cashier → enter/verify → durable draft/save state → next cashier`

The legacy CashierEntry layout is not an implementation target. Existing behavior, financial semantics and durability evidence are the reference.

## Authoritative behavior to preserve

### Financial write boundary

Authoritative service:
`CashierRevenueEntryService`

Preserve:
- `EnterRevenue` authorization at the commit boundary;
- serializable transaction;
- `BusinessDayWorkflowService.EnsureWritable`;
- operational-day identity;
- concurrency guard on loaded row/version;
- historical cashier/branch/POS/account-kind snapshot;
- separate `CoarseTotalIQD`;
- separate `ChangeTotalIQD`;
- separate `UsdTotalCents`;
- denomination rows for 25,000 / 10,000 / 5,000 / 50,000;
- no presentation-owned financial persistence.

### Expression behavior

Authoritative helpers:
- `ArithmeticExpressionEvaluator`
- `InlineRevenueCalculator`

Denomination count fields:
- whole non-negative note counts;
- addition/subtraction expressions such as `80+2`;
- no decimal physical-note counts;
- no multiplication/division in note-count fields.

Change:
- arithmetic expression;
- non-negative integer IQD.

USD:
- independent expression;
- whole-dollar policy except permitted historical compatibility;
- persistence in cents.

Direct coarse entry:
- non-negative IQD integer;
- mutually exclusive with denomination detail for persisted coarse composition.

### Durability / recovery

Authoritative recovery:
`CashierCrashRecoveryService`

Preserve:
- local durable journal outside accounting data;
- atomic same-volume replacement + flush-to-disk;
- database-incarnation binding;
- cashier/day identity;
- baseline row/version;
- edit revision;
- incompatible/corrupt draft quarantine behavior at the infrastructure boundary;
- no navigation if the newest edit is neither financially committed nor durably journaled;
- committed recovery draft cleared only for the matching committed revision;
- if an older revision commits while typing continues, newer edits remain dirty and are re-journaled.

### Concurrency

Preserve:
- stale row/version cannot overwrite newer financial state;
- navigation while save is in flight is permitted only with durable latest edit;
- completion of a previous cashier save never applies its identity/version to the newly selected cashier.

## Keyboard contract

Required behavior:

- Enter → next logical field
- Shift+Enter → previous logical field
- PageUp/PageDown → previous/next cashier
- Home/End → previous/next branch in cashier scope
- Insert → toggle direct coarse mode
- F5 → explicit save
- Delete → reset current numeric field
- Ctrl+Delete → clear current cashier workflow under the existing safety contract
- Escape → restore/revert current field according to saved baseline
- Ctrl+Z / Ctrl+Y → native undo/redo
- modified text-editing keys not explicitly owned by the workbench remain native
- mouse access remains available for every primary action

Arrow-key spatial movement from the old UI is behavior evidence, not automatically a global requirement; it must be evaluated against the new workbench focus model.

## Existing executable evidence to reuse

Current tests already prove important contracts:
- inline totals preserve denomination/change/USD arithmetic;
- invalid physical counts cannot reach persistence;
- concurrent flushes serialize into one financial commit;
- committed draft clears;
- invalid expression retains exact recoverable draft;
- recovered edit can commit against its baseline;
- stale edit cannot overwrite newer revision;
- failed financial write is not blindly retried by later typing;
- unsafe handoff fails when neither save nor draft is durable;
- edits made during an older in-flight save remain dirty;
- compact cashier presentation keeps primary controls reachable.

Phase 6 must migrate these tests toward the new RebuildV2 application/presentation path rather than deleting the evidence.

## Architecture target

Preferred direction:

`CashierWorkbenchView → CashierWorkbenchViewModel/Coordinator → Application contracts → Infrastructure adapters → existing verified services/data`

Hard boundaries:
- no `AppDbContext` in Presentation;
- no `SaveChanges` in Presentation;
- no `CashierRevenueEntryService` construction in View;
- no duplicated financial formulas in ViewModel;
- no recovery-file mutation in View;
- no giant ViewModel absorbing roster + persistence + reconciliation + dialogs + navigation;
- no global mutable state used to coordinate cashier sessions.

## Proposed sub-slices

### P6.0 — contracts and deterministic fixture
- cashier work-item identity;
- context DTO;
- revenue draft DTO/state;
- read/query contract;
- expression/calculation seam;
- journal seam;
- save command contract;
- golden synthetic cashier set.

### P6.1 — read-only workbench
- cashier identity;
- branch/POS/shift/day;
- existing persisted totals;
- denomination view;
- read-only day state;
- next/previous context.

### P6.2 — editing + calculations
- denomination expressions;
- direct coarse;
- change;
- USD;
- immediate validation;
- dirty/edit-revision model;
- no DB write yet.

### P6.3 — durability + navigation handoff
- durable journal before navigation;
- recovery conflict state;
- latest-edit handoff;
- closed-day behavior.

### P6.4 — controlled financial save
- authoritative save service behind application boundary;
- permission;
- concurrency;
- failure/retry;
- exact revision acknowledgement;
- no duplicate writes.

### P6.5 — keyboard/GUI acceptance
- full shortcut matrix;
- 1280×720 and CI compact stress viewport;
- long Arabic names;
- large amounts;
- invalid/partial expressions;
- read-only/closed day;
- in-flight save/navigation.

## Async write architecture decision to make at Slice Open

The current authoritative service is synchronous while the new Presentation boundary must not block the WPF dispatcher.

Allowed candidates for council review:
1. Infrastructure adapter that executes the existing authoritative service off-dispatcher as a migration seam, explicitly recording non-interruptible cancellation debt.
2. add a native async authoritative service path while retaining one financial rule implementation and legacy compatibility.

Forbidden:
- copy/rewrite the save formula in the new UI merely to obtain async syntax.

The final choice must be decided by Architecture + Finance/Data + Reliability before P6.4.

## Removed legacy constraint

Do not reproduce:
- arbitrary `InteractiveLayoutEditor` / cashier-screen freeform layout customization.

The new product may later expose bounded density/column preferences, but not arbitrary layout states in G9.

## G9 mandatory evidence

Before `G9_CASHIER_WORKBENCH_LOCK`:
- source boundary audit;
- financial parity tests;
- recovery/incarnation tests;
- concurrency tests;
- latest-edit durability;
- no-loss navigation handoff;
- full keyboard contract;
- strict GUI audit;
- supported viewport/DPI evidence applicable to the slice;
- permissions;
- logs/error states;
- regression against Finance + Day;
- council handoff packet.

## Gate state

**NOT OPEN.**  
Open Phase 6 only after G8 has a green exact-SHA CI and formal council lock.
