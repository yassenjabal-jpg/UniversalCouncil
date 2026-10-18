# RevenueSystem 2.0 — G8 Day Console Council Review Packet

Date: 2026-10-18  
Status: **PENDING_FINAL_CI**  
Gate: `G8_DAY_CONSOLE_OVERVIEW_LOCK`

## Source pin

RevenueSystem branch: `rebuild/rs2-day-console-overview`  
RevenueSystem candidate: `1561e2a839949c3106d67467f7370e819c36d985`  
Stacked base: `rebuild/rs2-finance-write-pilot @ f1855a17498cdbdf2404d47c9073dbe6e989fb12`  
PR: RevenueSystem5 #82

UniversalCouncil project authority:
`feat/revenuesystem-rebuild-studio-20261017`

## Slice scope

- Day overview
- branch/cashier completion
- attention queue
- read-only close readiness projection
- recovery draft indicator
- deep links to implemented workspaces
- no day mutation from opening/refreshing the workspace

## Review sequence

This review follows the RevenueSystem Rebuild Studio contract:

`GUI Implementation → Local Build → Focused Validation → Runtime/GUI Acceptance → Domain Clearance → Regression → Handoff Lock`

The gate remains open until the final GitHub Windows CI run on the exact candidate SHA succeeds.

## Architecture Boundary Audit

Verdict: **PASS SOURCE BOUNDARY / FINAL RUNTIME HOLD**

Evidence:
- RebuildV2 Presentation contains no `AppDbContext`.
- RebuildV2 Presentation contains no `SaveChanges`.
- `DayConsoleViewModel` depends on `IDayConsoleReadUseCase`.
- EF Core queries live in `Infrastructure/Day/DayConsoleReadAdapter.cs`.
- Day read path uses async EF operations.
- Day workspace code-behind remains presentation-only.
- opening or refreshing Day Console does not call `EnsureDay` or mutating `CheckClose`.
- recovery projection reads compatible drafts without invoking quarantine/move behavior.

No newly introduced material presentation/data boundary violation is confirmed.

## Finance & Data Guardian

Verdict: **PASS**

Authoritative comparison was made against `BusinessDayWorkflowService.CheckCloseCore`.

Day close readiness remains aligned with the current financial-domain contract:
- day must be ReadyToClose;
- required roster must be frozen;
- no required cashier may be missing;
- no entry may remain NeedsReview;
- revenue amounts/denominations must be valid.

Reconciliation differences, electronic mapping issues and account credit warnings remain Attention items. They are not promoted into invented close blockers because the authoritative domain service does not currently define them as such.

Money remains separated as:
- coarse IQD;
- change IQD;
- USD cents.

Credit exposure attention continues to use `FinancialInvariantService.CalculateAccountExposure` and includes electronic postings.

## UI/UX & Human Error Review

Verdict: **PASS AFTER RETURN TICKETS / FINAL GUI HOLD**

Two misleading presentation defects were detected during review and returned to their source owners:

### RT-G8-01 — completion semantics

Problem:
`NeedsReview` entries were counted under a property and labels presented as “completed”.

Correction:
- CompletedCount now counts only `DayCashierState.Completed`.
- NeedsReview remains a separate count.
- NotStarted remains missing.
- the isolated UI fixture now requires a 1/3 completion display for one Completed + one NeedsReview + one Missing cashier.
- inspector/status copy now says “مكتمل/حسابات مكتملة”.

### RT-G8-02 — Finance write editor leaked into read capability

Problem:
The Day CI flow switches through Finance. In read-only Finance mode, the account editor visual tree could remain visible and static copy claimed CONTROLLED WRITE, producing strict-layout overlaps and misleading capability state.

Correction:
- Finance editor visibility now fails closed with `FallbackValue=Collapsed` and `TargetNullValue=Collapsed`.
- Finance eyebrow and badge are bound to actual READ/WRITE capability.
- UI smoke fails explicitly if the editor is visible without write capability.
- Day smoke returns to Day Console before final visual capture.

The strict layout audit is not weakened or bypassed.

## QA / Red Team

Verdict: **SOURCE PASS / FINAL CI HOLD**

Local source-only evidence on YASSIN at candidate SHA:
- solution Build: PASS
- warnings: 0
- errors: 0
- `rrs2_foundation_validate.py`: **44/44 PASS**
- `rrs2_day_console_validate.py`: **40/40 PASS**

The preceding CI candidate `857cc164` proved:
- build/validation/static gates: PASS
- SQLite simulations: PASS
- Finance parity integration: PASS
- Stage10 release gate: PASS
- controlled Finance write UI smoke: PASS
- Day functional runtime assertions: PASS
- Day refresh did not capture a missing roster
- native Day state loaded and exposed 5 attention items

That CI failed only at strict final visual audit after switching into Finance, which produced RT-G8-02. The defect has been corrected in candidate `1561e2a`.

## Performance / Observability

Verdict: **NO NEW BLOCKER**

- Day data path is async EF Core.
- no synchronous DB access was added to Presentation.
- no product performance threshold is invented at G8.
- Stage10 and CI regression evidence remain required for final closure.

## Security / Audit

Verdict: **PASS**

- Day Console itself is read-only.
- no production DB/LAN is authorized or used for the rebuild gate.
- prototype/runtime verification is isolated.
- read-only Finance capability no longer exposes write-editor UI.
- no permission check is replaced by visibility-only enforcement.

## Dissent record

Material dissent was preserved and resolved rather than averaged away:

1. six-workspace validator double-counted conditional Day construction — validator corrected.
2. NeedsReview was visually counted as completed — semantics corrected and regression-locked.
3. Finance write surface appeared during read mode in Day smoke — fail-closed visibility and truthful capability copy added.
4. proposal to make reconciliation/credit alerts close blockers was rejected after comparison with the authoritative `BusinessDayWorkflowService`; doing so would have changed domain semantics without authority.

## Pending evidence

GitHub Windows CI on exact candidate:
- run number: **496**
- run id: **39114230627**
- head: `1561e2a839949c3106d67467f7370e819c36d985`
- status at packet creation: **IN PROGRESS**

Required before lock:
- full CI success;
- controlled Finance write UI smoke pass;
- Day Console strict UI smoke pass;
- zero strict layout warnings for final Day capture;
- evidence artifact upload.

## Gate decision

**PENDING_FINAL_CI**

No transition to Phase 6 is authorized by this packet until the pending evidence is green.

When the required evidence succeeds, this packet may be promoted to:

`G8_DAY_CONSOLE_OVERVIEW_LOCK = PASS`

and the next authorized slice becomes:

`PHASE_6_CASHIER_WORKBENCH / G9_CASHIER_WORKBENCH_LOCK`.
