# RevenueSystem 2.0 — G9 Cashier Workbench Stage 2 Council Review

Date: 2026-10-18  
Stage: `STAGE_2_EDITING_KEYBOARD_RECOVERY`  
Status: **PENDING_FINAL_CI**  
Product branch: `rebuild/rs2-cashier-workbench`  
Candidate: `88d7eb8ed41b803c10c26dc6e9c70b752aceb77f`  
Stage 1 baseline: `90476f0186f1e44739d5545271621fc8d0f622f9`  
Target parent gate: `G9_CASHIER_WORKBENCH_LOCK`

## Stage boundary

Stage 2 adds local editing, operational keyboard behavior and durable recovery only.

It does **not** authorize:
- `CashierRevenueEntryService.Save`;
- accounting database writes;
- financial autosave;
- production DB/LAN/AppData;
- G9 final lock.

## Implemented behavior

- denomination expressions for 25,000 / 10,000 / 5,000 / 50,000;
- direct coarse IQD mode;
- change expression;
- USD expression;
- notes;
- immediate evaluation through the existing authoritative calculation path;
- dirty/EditRevision state;
- durable local draft revision;
- 180 ms recovery-journal debounce;
- latest-draft durability before cashier/branch/day navigation;
- same-session durable drafts restore automatically;
- prior-session recovery remains explicit restore/discard;
- baseline conflicts remain visible;
- two-step Ctrl+Delete local clear;
- F5 means durable local draft only;
- no accounting write.

## Keyboard contract

Stage 2 routes:
- Enter → next field;
- Shift+Enter → previous field;
- PageUp/PageDown → previous/next cashier;
- Home/End → branch navigation when text editing does not own focus;
- native Home/End caret behavior remains intact inside TextBox;
- Insert → direct/denomination mode;
- F5 → persist recovery draft only;
- Delete → clear focused numeric field;
- Ctrl+Delete → two-step clear of local draft;
- Escape → revert focused field to loaded baseline;
- Ctrl+Z/Ctrl+Y → native text editing, never consumed by navigation.

## Architecture Boundary Audit

Result: **PASS WITH STAGE-3 EXTRACTION CONDITION**

Confirmed:
- Presentation contains no `AppDbContext`;
- Presentation contains no `SaveChanges`;
- Presentation contains no `CashierRevenueEntryService`;
- application editing contracts are WPF/data-service free;
- calculation adapter reuses `InlineRevenueCalculator.BuildRequest`;
- recovery adapter reuses `CashierCrashRecoveryService`;
- recovery remains database-incarnation bound;
- synchronous legacy recovery I/O is behind an Infrastructure async seam;
- WPF code-behind remains thin; keyboard routing was extracted into `CashierWorkbenchKeyboardRouter`;
- six-workspace topology remains unchanged; Cashier is a Day work item.

Architecture debt:
`CashierWorkbenchViewModel` is now a substantial work-item coordinator. This is acceptable for Stage 2 because it owns UI/edit state and delegates calculation/durability, but **Stage 3 must not place authoritative financial save logic into this ViewModel**. The financial write path must enter through an Application write contract/coordinator and Infrastructure adapter.

## Finance/Data clearance

- coarse IQD, change IQD and USD cents remain separate;
- denomination physical counts still use the legacy restricted count evaluator;
- local editing uses a frozen business-day roster when available;
- a later master-data disable does not rewrite the frozen day roster;
- no local draft mutates RevenueEntry, RevenueDenomination or BusinessDay;
- Stage 3 remains the only phase allowed to introduce authoritative accounting writes.

## QA evidence already encoded

Dedicated isolated GUI acceptance verifies:
- LOCAL DRAFT / NO ACCOUNTING WRITE mode;
- frozen-roster provenance;
- Insert mode toggle;
- denomination/change/USD evaluation;
- F5 durable draft;
- accounting RevenueEntry remains unchanged after F5;
- PageUp/PageDown and same-session restoration;
- Enter/Shift+Enter;
- native Home/End within text and branch Home/End outside text;
- prior-session recovery decision and restore;
- Escape/Delete;
- native Ctrl+Z;
- two-step Ctrl+Delete;
- Day return/reopen;
- Finance and Day regression remain in the same Windows CI workflow.

## Delta

Stage 1 → Stage 2 changes are confined to:
- RRS2 Application/Revenue editing contracts;
- RRS2 Infrastructure/Revenue evaluator + journal;
- RRS2 Presentation Cashier work item and shell status copy;
- RRS2 validators/UI tests;
- Windows CI gate label.

No schema, migration, production configuration or financial write service is changed.

## Pending evidence

GitHub Windows CI on exact candidate:
- run: **#546**
- run id: **39124422760**
- required conclusion: SUCCESS;
- required Stage10: PASS;
- required Finance regression: PASS;
- required Day regression: PASS;
- required Cashier Stage 2 UI smoke: PASS;
- required strict final Cashier capture: zero layout warnings.

## Gate decision

**PENDING_FINAL_CI**

Stage 3 remains blocked.
