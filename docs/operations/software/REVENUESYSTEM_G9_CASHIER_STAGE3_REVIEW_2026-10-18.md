# RevenueSystem 2.0 — G9 Cashier Workbench Stage 3 Council Review

Date: 2026-10-18  
Stage: `STAGE_3_FINANCIAL_SAVE_G9_LOCK`  
Status: **PENDING_FINAL_CI / COUNCIL LOCK**  
Product branch: `rebuild/rs2-cashier-workbench`  
Stage 2 baseline: `88d7eb8ed41b803c10c26dc6e9c70b752aceb77f`

## Authority chain

Financial commit path is now:

`CashierWorkbenchWorkspace → CashierWorkbenchViewModel → ICashierWorkbenchCommitCoordinator → ICashierWorkbenchWriteUseCase → CashierWorkbenchWriteAdapter → CashierRevenueEntryService`

The existing `CashierRevenueEntryService` remains authoritative for:
- EnterRevenue permission enforcement;
- business-day writable guard;
- serializable financial transaction;
- optimistic version/stale-row checks;
- historical cashier/branch/POS snapshots;
- denomination persistence;
- audit context and accounting persistence.

No duplicate financial save implementation was introduced.

## Stage 3 guarantees under review

- F5 performs authoritative financial save.
- valid edits autosave after recovery durability.
- invalid partial expressions remain recovery-only and never enter accounting.
- accounting save is serialized.
- synchronous authoritative transaction executes off the WPF dispatcher.
- cancellation is honored before admission, not during the admitted transaction.
- failed financial writes are not blindly retried by subsequent typing.
- stale writes surface an explicit conflict and preserve the durable local draft.
- reload after conflict reads the current baseline and exposes the saved draft as a conflict recovery decision.
- if a newer edit appears while an older revision is saving, Application coordinator rebases the latest durable draft onto the newly committed version and saves it next.
- recovery is deleted only after the latest known revision commits.
- recovery cleanup re-checks for a newer edit so cleanup cannot erase the latest journal.
- coarse IQD / change IQD / USD cents remain separate.

## Architecture Boundary Audit

Current direction: **PASS CANDIDATE**

Confirmed design intent:
- Application write contracts contain no WPF or EF dependency.
- Application coordinator owns financial sequencing/rebase.
- Infrastructure adapter owns the legacy authoritative service seam.
- Presentation contains no `AppDbContext`, `SaveChanges`, or direct `CashierRevenueEntryService`.
- WPF code-behind stays presentation-thin.
- no schema/migration change.
- no production DB/LAN/AppData access.

## Deterministic latest-edit acceptance

A protected validation test deliberately pauses revision 1 while revision 2 is staged. It requires:
- save order = r1 then r2;
- max concurrent financial writes = 1;
- r2 baseline version = result version from r1;
- rebased r2 is durably re-journaled;
- recovery cleanup occurs only after latest commit.

File:
`RevenueSystem.ValidationTests/CashierWorkbenchStage3Validation.cs`

## GUI acceptance contract

The isolated Cashier Stage 3 UI smoke must prove:
- FINANCIAL SAVE capability badge;
- F5 updates the accounting row;
- autosave updates a later valid edit without F5;
- forced external Version bump causes stale-write conflict;
- stale write does not overwrite external data;
- reload exposes baseline-conflict recovery;
- explicit restore/retry commits preserved latest draft;
- invalid partial work survives PageUp/PageDown but is not forced into accounting;
- Enter / Shift+Enter / PageUp / PageDown / Home / End / Insert / F5 / Delete / Ctrl+Delete / Escape / Ctrl+Z remain valid;
- final strict 1024×720 layout audit has zero warnings;
- Finance and Day regressions remain green.

## Pending

Final exact SHA, Windows CI run, artifact IDs, strict UI metrics, delta review and final Council verdict will be appended only after the candidate is green.

## Gate

`G9_CASHIER_WORKBENCH_LOCK = PENDING`

No merge to main is authorized by this document.
