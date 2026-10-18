# RevenueSystem 2.0 — Editorial Financial Engraving Native Rebase Review
Date: 2026-10-18
Status: **PENDING FINAL CI / VISUAL ACCEPTANCE**
Joint reviewers: RevenueSystem Council + RevenueSystem Rebuild Studio

## Product candidate

Branch:
`rebuild/rs2-editorial-financial-engraving`

Base:
`416196fa60202e75b035deabf805a92e094700d4` — G9 Cashier Workbench lock

Candidate:
`a15595dfff193ad99037ab6ea7f4d2d1d59525dc`

Draft PR:
**#84**

## Owner directive

Implement the owner-locked **Editorial Financial Engraving** system natively inside WPF, without depending on external design applications or screenshot skins.

This visual system applies to all RevenueSystem presentation surfaces. Existing functional/financial evidence remains valid, but no previously completed UI is visually grandfathered.

## Native implementation

Implemented entirely in source:

- semantic palette rebalance;
- Deep Forest institutional structure;
- Cobalt interaction/focus;
- Paper Ivory / document surfaces;
- Brass micro-annotation only;
- semantic amber/red/recovery brushes;
- restrained 4/6/10 px radii;
- financial tabular numeral token;
- native guilloché field via `DrawingBrush` / vector geometry;
- native registration field;
- native command-rail engraving;
- ledger-panel hierarchy;
- verified/review/risk/recovery surfaces;
- original abstract seal primitives;
- denomination-strip primitives;
- dense DataGrid financial header treatment;
- keyboard-focus treatment;
- responsive 72/82 px command rail.

No PNG/JPG/WebP skin is introduced.

## Current surfaces rebased

- RevenueSystem 2.0 Shell
- Day Console
- Cashier Workbench
- Finance Ledger
- placeholder/unbuilt workspace state so it no longer shows an older visual language

Future workspaces inherit the same source-level design system.

## Architecture Boundary Audit — source-only

Candidate delta is confined to Presentation/Themes + one static validator.

The only C# presentation change is the responsive command-rail width in `Rrs2ShellWindow.xaml.cs`.

Confirmed:
- no `AppDbContext` introduced;
- no `SaveChanges` introduced;
- no domain/application/service dependency introduced;
- no financial rule changed;
- no ViewModel changed;
- no schema or migration changed;
- no production DB/LAN/AppData access;
- shell code-behind remains within the existing presentation-only line budget.

Verdict:
**PASS CANDIDATE — pending exact-head CI and GUI evidence.**

## Static design-system evidence

- 4 RRS2 theme dictionaries
- 111 unique public resource keys
- 0 duplicate resource keys
- theme dependency chain:
  `SemanticTokens → FinancialEngraving → SharedComponents → Feature`
- external raster-skin dependency: forbidden by validator
- legacy RevenueSystem art-direction strings: forbidden in RebuildV2 Presentation

## Exact-head gates required

Before locking the visual rebase:
- solution build PASS;
- C# validation PASS;
- RRS2 static validation PASS;
- existing SQLite/integration regression PASS;
- Stage10 PASS;
- Finance UI regression PASS;
- Day Console UI regression PASS;
- Cashier Stage 3 financial UI regression PASS;
- strict compact visual audit PASS;
- artifact/screenshot inspection;
- zero material layout regression.

## Release rule

This PR remains draft and stacked. No merge to main is authorized by this review.
