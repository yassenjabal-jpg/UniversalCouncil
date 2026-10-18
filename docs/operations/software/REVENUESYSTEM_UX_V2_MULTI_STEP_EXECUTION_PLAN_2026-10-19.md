# RevenueSystem 2.0 — UX v2 Balanced Content-First Multi-Step Execution Plan
Date: 2026-10-19
Status: OWNER DIRECTED / ACTIVE
Product branch: rebuild/rs2-editorial-financial-engraving
Rule: one step open at a time. Every step ends with Council + Studio review before the next step may open.

## Governing direction
- UX model: BALANCED CONTENT-FIRST
- Visual identity: EDITORIAL FINANCIAL ENGRAVING
- Work type: COMPOSITION REBASE, not identity restart
- Main merge: forbidden without explicit owner instruction
- Section 2: blocked until Section 1 re-lock

## STEP 1 — SHELL & CHROME
Scope:
- remove duplicate work-item/page title strip;
- consolidate into one compact context ribbon;
- top persistent chrome <= 58px at 1024x720;
- bottom persistent bar <= 24px;
- preserve rail/navigation/command palette;
- reclaim vertical space for actual work.

Exit evidence:
- source SHA;
- Windows build/static checks;
- representative Finance + Day runtime screenshots;
- compact 1024x720 layout warnings = 0 for affected surfaces;
- UX v2 chrome-ratio assessment;
- Council review;
- Studio Art Director review;
- Independent Visual QA verdict.

Gate:
STEP_1_COUNCIL_STUDIO_PASS

## STEP 2 — CASHIER CONTENT-FIRST
Scope:
- compact cashier identity/context;
- coarse IQD / change / USD totals move upward;
- denomination matrix becomes primary productive object;
- save/recovery state remains unmistakable but subordinate to counting;
- preserve keyboard, focus, autosave, F5, recovery and financial truth;
- high-frequency local hero <= 78px unless UX evidence justifies an exception.

Exit evidence:
- focused Cashier functional validation;
- representative synthetic runtime;
- compact screenshot;
- keyboard completion proof;
- state-recognition proof;
- layout warnings = 0;
- Council + Studio review.

Gate:
STEP_2_COUNCIL_STUDIO_PASS

## STEP 3 — DAY + FINANCE CONTENT-FIRST
Day:
- readiness is the hero;
- page title cannot dominate readiness;
- branch/attention content moves upward.

Finance:
- account identity + status + KPIs become one compact dossier;
- ledger begins materially higher;
- remove stacked internal title layers;
- preserve transaction density.

Exit evidence:
- Finance + Day regressions;
- representative synthetic screenshots;
- UX scorecard;
- Council + Studio review.

Gate:
STEP_3_COUNCIL_STUDIO_PASS

## STEP 4 — INTEGRATION / VISUAL ACCEPTANCE / SECTION 1 RELOCK
Scope:
- screenshot matrix compact/standard/125%/150%/long Arabic/relevant states;
- side-by-side reference review;
- UX v2 scorecard;
- Art Director clearance;
- Independent Visual QA clearance;
- architecture/finance/security/performance/accessibility regression review;
- final Section 1 re-lock document with exact SHA/CI/artifacts.

Gate:
VISUAL_SECTION_1_ART_FIDELITY_RELOCK

## Step transition rule
A later step MUST NOT open when the previous step verdict is REVISE.
If REVISE:
- correction remains inside the current step;
- rerun evidence;
- repeat Council + Studio review;
- only PASS opens next step.

## Owner visibility
Review findings are reported to the owner after each step.
Any material direction change beyond the approved BALANCED CONTENT-FIRST model returns to the owner before implementation.
