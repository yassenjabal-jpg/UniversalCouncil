# RevenueSystem 2.0 — VISUAL_SECTION_1_LOCK
Date: 2026-10-18
Status: **PASS / LOCKED**
Joint verdict: **RevenueSystem Council + RevenueSystem Rebuild Studio**
Governing system: **EDITORIAL FINANCIAL ENGRAVING**

## Scope locked
- RevenueSystem 2.0 Shell / RTL command rail
- Day Console
- Cashier Workbench
- Finance Ledger
- placeholder/unbuilt workspace state
- shared semantic tokens/components
- native guilloché / registration / ledger / seal primitives
- compact 1024×720 behavior

## Exact product candidate
Branch: `rebuild/rs2-editorial-financial-engraving`

Final SHA:
`c7d9e05bd6fe253fa0deafdca81469d210b3938d`

Base:
`416196fa60202e75b035deabf805a92e094700d4`

Draft PR:
**#84 — remains OPEN + DRAFT. No merge authorized.**

## Final bounded visual correction
Final correction commit:
`c7d9e05bd6fe253fa0deafdca81469d210b3938d`

Change was limited to:
`RevenueSystem/RebuildV2/Presentation/Shell/Rrs2ShellWindow.xaml`

Reason:
At the compact 72 px command-rail width, the `FINANCIAL / ENGRAVING` identity footer was visually clipped despite CI #590 passing. The footer was reduced and fitted with native WPF Viewbox scaling so the identity remains legible without increasing rail width or changing financial layout.

No ViewModel, application, domain, persistence, financial rule, database schema, migration, LAN, or production-data code changed.

## Exact-head CI
Workflow: **RevenueSystem Windows CI**
Run: **#591**
Run ID: `39164529605`
Head: `c7d9e05bd6fe253fa0deafdca81469d210b3938d`
Final attempt: **2**
Conclusion: **SUCCESS**

Attempt 1 note:
The first attempt failed only at the Cashier Stage 3 UI gate with `F5 did not complete authoritative financial save`. Because the visual delta contained no financial/write code, the same exact SHA was rerun rather than patched around the failure. Attempt 2 passed the Cashier financial gate and the complete workflow. The failure is retained as evidence and is not erased.

Passed on final attempt:
- Restore / Build
- C# validation
- static validation
- durable tooling validation
- source-sync validation
- SQLite simulations
- Finance parity integration
- Stage10 release gate
- controlled Finance write UI smoke
- Day Console UI smoke
- Cashier Workbench Stage 3 financial UI gate
- artifact publication

## Final artifacts
| Surface | Artifact ID | Digest |
|---|---:|---|
| Cashier Workbench | `12150606515` | `sha256:53c0670cf47e92971382f87fb740e65da913a44abd0788c21ff7924e4b3b5a28` |
| Day Console | `12150895350` | `sha256:005a9a88532c3d153502d4735b3afdeaa7e3b2aec17ea218d3a6ed9caea74147` |
| Finance / RRS2 UI | `12150169095` | `sha256:35cce8315ec76ffd8b8d3b55d1ba1d9c5218924f466879843ec2f9a0de164db9` |
| Isolated UI evidence | `12150303287` | `sha256:cab87354b3a368a20328892b0f4922dd4732bfd416a7a97e2f32e64d4a722fc6` |
| Windows build | `12150830734` | `sha256:1ec9e6fde675eb6a043fd4aacc281bba6023eea8164e85f5e0f244246da31227` |

Final compact UI evidence:
- Cashier: 126 named elements / 0 layout warnings
- Day: 131 named elements / 0 layout warnings
- Finance: 118 named elements / 0 layout warnings
- Isolated legacy evidence: 134 named elements / 0 layout warnings

## Council + Studio Visual Constitution Review
### PASS
1. **Hierarchy** — one dominant operational task remains clear on Day, Cashier and Finance.
2. **Engraving density** — linework is concentrated in shell/header/identity regions and remains quiet around data entry and tables.
3. **Readability** — compact 1024×720 layouts remain legible; the command-rail identity footer is now fully visible.
4. **Rail clarity** — right-side Deep Forest rail retains readable workspace labels and active Cobalt state at compact width.
5. **Brass restraint** — brass remains a micro-annotation, not a dominant surface treatment.
6. **Forest restraint** — Deep Forest is structural rather than a full-screen fill.
7. **No SaaS drift** — the core RRS2 surfaces read as a financial workstation/ledger, not a web dashboard or card wall.
8. **Visual fatigue control** — work surfaces are predominantly Paper Ivory with quiet borders and low decoration.
9. **Data remains hero** — financial totals, denomination entry, readiness and ledger regions dominate over decoration.
10. **Semantic states** — focus/active/verified states combine text/structure with color; color is not the sole carrier.
11. **Currency separation** — Cashier keeps IQD coarse, IQD change and USD visually separate.
12. **Native WPF credibility** — the identity is implemented through XAML/resources/vector brushes/components, without raster skin dependency.

Council verdict: **PASS**
Studio verdict: **PASS**
Combined disposition: **VISUAL_SECTION_1_LOCK**

## Important non-grandfather warning
The isolated Stage10 evidence still reaches the legacy `المطابقة` surface with the older visual language. It is **not visually accepted by this lock** and is not treated as compliant merely because Stage10 passes.

This is a recorded remaining obligation under **VISUAL_SECTION_3_SYSTEM_COMPLETION**:
- migrate every legacy reachable surface to Editorial Financial Engraving; or
- explicitly classify it as a temporary compatibility surface with an approved retirement plan.

Therefore:
- Section 1 is locked for its defined RRS2 core scope.
- Whole-product visual acceptance is **not** complete.
- Final release remains blocked until Sections 2 and 3 are completed.
- 125% / 150% DPI whole-product reacceptance remains a Section 3 final gate.

## Section control
`VISUAL_SECTION_1_CORE_REBASE_LOCK` → **LOCKED / PASS**

`VISUAL_SECTION_2_RECONCILIATION_REPORTS` → **NOT OPENED**

`VISUAL_SECTION_3_SYSTEM_COMPLETION` → **NOT OPENED**

Stop at owner checkpoint. Do not open Section 2 automatically.
