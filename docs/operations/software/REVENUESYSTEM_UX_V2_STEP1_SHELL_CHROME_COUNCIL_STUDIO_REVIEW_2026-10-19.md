# RevenueSystem 2.0 — UX v2 Step 1 Council + Studio Review
Date: 2026-10-19
Step: 1 — SHELL & CHROME
Product head reviewed: `63b8ed0b179d920e63cdb1796a88300a4a974c27`
CI: RevenueSystem Windows CI #604 / run 39176574159
Scope verdict: PASS
Next-step authorization: STEP_2_MAY_OPEN
Main merge: NOT AUTHORIZED
Section 2: REMAINS BLOCKED

## Implemented change

Step 1 implemented the approved UX v2 Balanced Content-First shell skeleton:

- removed the dedicated 42px WorkItemTabs/page-title row;
- merged active workspace title/subtitle into the main operational context;
- changed persistent top shell context from 62px to 56px;
- changed persistent bottom status bar from 30px to 24px;
- kept right command rail and command palette;
- moved workspace content immediately below the single context ribbon;
- moved command palette top offset to match the compact ribbon;
- added a static regression gate that rejects reintroduction of a separate WorkItemTabs strip.

## Measured UX result at 1024x720

Before Step 1:
- top context = 62px
- duplicate work-item strip = 42px
- bottom status = 30px
- persistent shell chrome = 134px

After Step 1:
- single top context ribbon = 56px
- duplicate work-item strip = 0px
- bottom status = 24px
- persistent shell chrome = 80px

Result:
- reclaimed vertical task space = 54px
- persistent shell chrome reduction = 40.3%
- reclaimed share of 720px viewport = 7.5%
- shell chrome ratio fell from ~18.6% to ~11.1% of viewport height (not counting native Windows title chrome).

UX v2 hard-budget result:
- top persistent app chrome <= 58px: PASS (56px)
- bottom persistent app chrome <= 24px: PASS (24px)
- duplicate page-title strip forbidden: PASS
- reclaimed space returned to workspace: PASS

## CI / implementation health

PASS:
- build solution;
- C# validation;
- current static validation;
- new `UX v2 shell uses a single compact context ribbon` static gate;
- durable development tooling;
- source sync tooling;
- SQLite simulations;
- Finance parity integration;
- Stage10;
- controlled Finance write UI smoke;
- Day Console UI smoke.

Representative screenshots:
- Finance artifact 12154940426
  - digest: sha256:74a452a14e9a66097844e82246e5c20213f0b40230e058c0b797de4492199bcb
  - layout warnings: 0
- Day artifact 12154248141
  - digest: sha256:1d8046cfb61ab59d13ad47666d04dfa5aae08351d08f0b5a927fa9dd8e275979
  - layout warnings: 0

Overall CI conclusion is FAILURE because the already-known Cashier F5/UI-state defect remains:
`coarse=2050000; change=150; usd=1500; state=فشل الحفظ • F5 لإعادة المحاولة`.

The persisted financial values are correct. The visible failure state after successful persistence predates Step 1 and is not caused by shell chrome changes. It is explicitly carried into Step 2, where Cashier is the active scope.

## Chief Operator Experience & UX Authority v2 review

### PASS

The shell now follows:
**Windows title → one operational context ribbon → workspace**

This resolves the owner's original duplicate-title-bar complaint at shell level.

Positive findings:
- workspace begins materially higher;
- active workspace identity remains visible without a dedicated page strip;
- operational date/day state remains visible;
- user/environment context remains available;
- Finance and Day core task areas visibly gained height;
- no additional decorative surface was inserted to consume the reclaimed space.

Remaining UX work is intentionally screen-local:
- Cashier hero is still too tall and is Step 2 scope;
- Day readiness hero remains large and is Step 3 scope;
- Finance account dossier + internal ledger header remain vertically layered and are Step 3 scope.

UX conclusion:
**STEP 1 PASS. Do not reintroduce a separate page-title row.**

## Visual Art Director review

### PASS WITH RESTRAINT NOTE

The single ribbon preserves Editorial Financial Engraving:
- guilloché remains visible but subdued;
- ivory / forest / cobalt relationship remains intact;
- the removed strip did not remove product identity;
- visual identity now relies more on composition and typography rather than stacked rectangles.

Art note for later steps:
Do not compensate for the removed strip by making workspace heroes larger or more decorative.

## WPF Design Systems / Visual Engineering review

### PASS

- one XAML shell composition changed;
- no raster skin;
- no financial/business calculation changed;
- no data/persistence dependency added to Presentation;
- compact behavior remains native WPF;
- static validator now protects the single-ribbon architecture.

## Independent Visual QA / Reference Fidelity

### PASS FOR STEP 1

At a two-second read:
- the top of the screen is less fragmented;
- the active workspace/context reads as one system;
- Finance and Day screenshots remain recognizably part of Editorial Financial Engraving;
- 0 layout warnings in both affected representative screens.

The step does not claim final reference-fidelity acceptance for the workspace-local heroes.

## Council checks

Finance/domain:
PASS — no financial logic changed.

Architecture:
PASS — XAML shell composition + static validation only.

Security/data:
PASS — no production data/LAN behavior touched.

Performance:
PASS — one persistent UI row was removed; visual-tree complexity did not increase.

Accessibility/interaction:
PASS FOR STEP — active context remains text-readable and keyboard command palette remains exposed.

QA:
PASS FOR STEP with known pre-existing Cashier defect carried to Step 2.

## Joint decision

**STEP_1_COUNCIL_STUDIO_PASS**

Step 1 is closed.

Step 2 — CASHIER CONTENT-FIRST may open.

Conditions for Step 2:
1. preserve the Step 1 single-ribbon shell;
2. do not increase persistent chrome;
3. high-frequency Cashier identity/header target <= 78px;
4. counting totals + denomination matrix become the primary visual object;
5. resolve or correctly classify the current F5 success/state inconsistency;
6. finish with another Council + Studio review before Step 3.
