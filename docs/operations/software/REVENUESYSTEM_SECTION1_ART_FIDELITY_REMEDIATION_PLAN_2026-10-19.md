# RevenueSystem 2.0 — Section 1 Art-Fidelity Remediation Plan
Date: 2026-10-19
Status: **ACTIVE — OWNER DIRECTED**
Scope: **Section 1 only**
Section 2: **BLOCKED / NOT OPENED**
Section 3: **NOT OPENED**

## 0. Purpose

This packet converts the 2026-10-19 Council + Studio reference-fidelity review into an executable correction contract.

The historical Section 1 behavioral/financial/architecture evidence remains valid. Section 1 is reopened only for visual authorship and reference fidelity. No financial/domain persistence behavior is intentionally changed by this packet.

Canonical art direction remains:
**EDITORIAL FINANCIAL ENGRAVING**

Reference set:
the eight owner-supplied concept screens for Day, Cashier, Reconciliation, Finance, Reports, Data, Administration and Login.

This remediation uses the reference images as a visual-grammar target, not literal product truth.

## 1. Non-negotiable preservation

Preserve:
- Native WPF implementation;
- no screenshot skin;
- no real banknote reproduction;
- no Saudi/national/government identity;
- no bank-building/architecture identity;
- actual product currency/domain semantics;
- IQD coarse/change/USD separation;
- keyboard-first behavior;
- virtualization and dense-data practicality;
- existing Application/Domain/Infrastructure boundaries;
- current finance/save/recovery authority;
- isolated runtime only;
- no production DB/AppData/LAN.

No merge to RevenueSystem main is authorized by this packet.

## 2. Visual authority

### RevenueSystem Visual Art Director
Final owner of:
- composition/massing;
- reference interpretation;
- Arabic display hierarchy;
- engraving density;
- seal language;
- screen-specific authored identity.

### WPF Design Systems / Visual Engineering Lead
Owns:
- semantic resources;
- vector engraving;
- reusable seals;
- financial number hierarchy;
- component fidelity;
- DPI/performance-safe implementation.

### UI/UX Interaction Architect
Owns:
- dominant task;
- keyboard-first efficiency;
- workbench/list/inspector balance;
- long-session ergonomics.

### Independent Visual QA / Reference Fidelity Reviewer
Must not act as implementation author for the reviewed slice.
Owns:
- side-by-side screenshot review;
- 2-second hierarchy test;
- prototype/debug-copy rejection;
- reference-family recognition test;
- PASS/REVISE visual verdict.

### Council
Retains independent clearance for:
- architecture;
- finance/domain truth;
- security;
- data integrity;
- regression;
- accessibility;
- performance/reliability.

## 3. Required design-system remediation

### 3.1 Engraving
Replace over-reliance on one repeated sinusoidal motif with a richer native-WPF vocabulary:
- multi-scale guilloché;
- concentric security-line rosettes;
- registration-line accents;
- quiet ledger rules;
- spatial composition instead of wallpaper repetition.

Pattern intensity must still fall to effectively zero inside numeric inputs and dense table cells.

### 3.2 Seal system
Create two levels:
- Hero Seal: 72–90 px for one meaningful state/identity moment;
- Micro Seal: existing compact product verification marks.

Large seal maximum: one meaningful hero seal per workspace.

### 3.3 Typography
Create explicit:
- DisplayHero;
- StateHero;
- FinancialHero;
- FinancialHeroLarge.

Accepted screenshot rule:
prototype/debug English may not dominate any production visual acceptance image.
Latin remains permitted for genuine IDs, POS codes, file types and technical metadata.

### 3.4 Paper layering
Create:
- HeroBand;
- HeroMetric;
- FinancialCommit surface;
- document framing with hairline/double-ledger rules.

No SaaS card wall.

## 4. Shell remediation

Target:
the reference set's institutional right rail + financial-document top context.

Keep:
- narrow right rail;
- top-right Windows controls;
- compact work-item/status bars.

Improve:
- top context engraving must read as a deliberately composed financial-document header;
- rail footer must not look like an engineering debug label;
- logo/identity should remain compact but authored;
- environment/debug information must visually recede relative to operational context.

Acceptance:
- removing the logo temporarily must still leave an identifiable visual system;
- compact 1024×720 must remain operational;
- no rail clipping.

## 5. Day Console art brief

Reference intent:
**Financial Control Room**

Dominant question:
**Is today ready, and what needs attention?**

Required hierarchy:
1. Day readiness/state hero;
2. completion context;
3. branch ledger;
4. attention queue;
5. daily financial totals;
6. open-Cashier action.

Changes:
- ReadinessDisplay becomes the largest semantic text;
- hero seal communicates ready/review state without relying on color alone;
- workspace title recedes;
- amounts use FinancialHero;
- readiness summary must not falsely use a verified treatment when CanClose is false;
- attention queue remains operational, not decorative.

2-second test:
a reviewer must identify "ready/not ready" before reading the workspace name.

## 6. Cashier Workbench art brief

Reference intent:
**Precision Counting Desk**

Dominant question:
**What is this cashier's current entered money, and what field do I type next?**

Required hierarchy:
1. cashier/branch/POS/day identity;
2. IQD coarse / IQD change / USD totals;
3. denomination entry matrix;
4. direct entry/change;
5. USD/notes;
6. save/recovery;
7. roster/navigation.

Changes:
- roster width reduced so it cannot compete with the editor;
- totals move to FinancialHero scale;
- numeric input size increased cautiously;
- denomination tags gain authored document-strip treatment;
- editor receives more width than notes/save;
- financial-save region receives institutional verified treatment;
- English prototype copy replaced with Arabic operational language.

Constraints:
- no real note images;
- no texture inside input;
- no change to keyboard contract;
- no change to authoritative save/recovery behavior.

2-second test:
the eye must land on totals + denomination matrix, not the roster.

## 7. Finance Ledger art brief

Reference intent:
**Private Institutional Ledger**

Dominant question:
**What account is selected, what is its current financial state, and what happened?**

Required hierarchy:
1. institutional account identity header;
2. account state/seal;
3. financial summary;
4. transaction ledger;
5. account browser;
6. controlled editor.

Changes:
- header becomes HeroBand;
- account name becomes DisplayHero;
- state receives a meaningful seal;
- capability remains data-bound;
- PilotEyebrow/PilotBadge remain driven by ViewModel capability but display Arabic production-facing copy;
- KPI financial values gain stronger hierarchy;
- Ledger and Account Index prototype English labels are removed from accepted surface.

Constraints:
- account browser remains usable at compact width;
- transaction ledger remains dominant;
- no new finance calculation in Presentation.

2-second test:
a reviewer must identify the account and current ledger state before noticing filters.

## 8. Architecture Boundary Audit contract

For every product delta in this remediation:
- Views/XAML may own composition;
- Presentation ViewModel may own presentation strings/state only;
- no new AppDbContext;
- no SaveChanges;
- no financial calculations;
- no copied business rules;
- no new static global mutable visual state.

Boundary verdict must distinguish:
- new violations;
- unchanged legacy debt;
- presentation-only changes.

## 9. Validator evolution

Static validation must measure the new visual contract rather than freeze old style-key names.

Required static assertions:
- HeroBand primitives exist;
- HeroSeal exists;
- FinancialHero type exists;
- Cashier denomination hero tag exists;
- Finance capability copy remains data-bound;
- no prototype/debug visual copy on accepted core screens;
- no external raster skin dependency;
- no duplicate RRS2 public resource keys.

CI success remains implementation-health evidence, not final visual acceptance.

## 10. Runtime evidence

Required exact-head isolated evidence:
- full solution build;
- current validation suite;
- current static suite;
- finance parity integration;
- Stage10;
- Finance write UI smoke;
- Day UI smoke;
- Cashier Stage 3 financial UI gate.

Required screenshots:
- Day;
- Cashier;
- Finance.

First mandatory viewport:
- 1024×720 compact stress.

Before final whole-product lock, also require:
- standard viewport;
- 125% DPI;
- 150% DPI;
- long Arabic names;
- representative financial values.

## 11. Screenshot content rule

A visual-acceptance screenshot must contain enough representative synthetic data to judge:
- hierarchy;
- numeric scale;
- table density;
- selection;
- semantic state.

An empty/pilot-looking screen may prove a route launches but cannot by itself prove art fidelity.

## 12. Side-by-side gate

Each screenshot must be reviewed against its corresponding owner reference.

Score:
- composition/massing;
- Arabic hierarchy;
- seal language;
- engraving/material depth;
- financial hierarchy;
- dense-data ergonomics;
- domain truth;
- WPF credibility;
- product-specific authored identity.

Do not average away a critical miss.

Automatic REVISE if:
- task hero is wrong;
- debug/pilot copy dominates;
- large semantic seal required by the brief is absent;
- decoration enters numeric/grid cells;
- the screen reads as generic WPF/SaaS;
- reference family is not recognizable without logo;
- domain truth is sacrificed for visual copying.

## 13. Current implementation packet

First remediation product commit:
`e34734559d4fb3fb94dada9f4f3a4eac89d0007e`

Validator-aligned follow-up candidate:
`3c728703a00fd7bcb317e1d282737df6a1b0883c`

CI:
RevenueSystem Windows CI #593 — pending at document creation.

## 14. Exit criteria

Section 1 may be re-locked only when:
1. exact candidate SHA is fixed;
2. CI succeeds;
3. screenshots are downloaded and inspected directly;
4. Day passes its reference brief;
5. Cashier passes its reference brief;
6. Finance passes its reference brief;
7. Art Director = PASS;
8. independent Visual QA = PASS;
9. UI/UX = PASS;
10. Architecture Boundary Audit = PASS;
11. Council finance/data/security/regression = PASS;
12. known visual debt is explicitly listed;
13. Section 2 remains unopened until the re-lock record is committed.

Exit lock:
**VISUAL_SECTION_1_ART_FIDELITY_RELOCK**

