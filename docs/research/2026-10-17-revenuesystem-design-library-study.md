# RevenueSystem Rebuild — External Design & Library Study
Date: 2026-10-17
Status: COUNCIL RESEARCH INPUT — NOT YET IMPLEMENTATION AUTHORITY

## 1. Research question

Which current Windows/WPF design approaches, libraries and financial-product patterns can materially improve «المطابقة» without creating unnecessary dependency, performance or migration risk?

---

# 2. Platform decision

## Keep WPF / .NET 10

Current product already targets `net10.0-windows`.

Microsoft WPF now includes an official Fluent theme for .NET 9+ with:
- light/dark modes;
- system accent support;
- modern Windows visual language.

.NET 10 continues improving Fluent control coverage and WPF performance.

### Council decision
**KEEP WPF / .NET 10.**

A move to WinUI/Avalonia/web is rejected for this rebuild unless a later specific blocker appears.

Reason:
- no product requirement demands cross-platform;
- current financial/data/test assets are WPF/.NET aligned;
- migration would multiply risk without solving the current architectural problem.

References:
- https://learn.microsoft.com/en-us/dotnet/desktop/wpf/whats-new/net90
- https://learn.microsoft.com/en-us/dotnet/desktop/wpf/whats-new/net100
- https://learn.microsoft.com/en-us/dotnet/desktop/wpf/controls/styles-and-templates

---

# 3. Design language

## Fluent 2 as design inspiration
Use:
- 4px spacing foundation;
- clear hierarchy through spacing rather than excessive borders/cards;
- responsive/adaptive regions;
- progressive disclosure;
- native-feeling Windows behavior;
- logical action grouping.

Do not copy web Fluent components literally into WPF.

Reference:
https://fluent2.microsoft.design/

### RevenueSystem adaptation
The product is denser than a consumer app.

Adopt:
- compact financial density;
- strong table/list hierarchy;
- restrained surfaces;
- one strong primary action per task context;
- semantic success/warning/danger;
- persistent work context.

Reject:
- oversized hero cards;
- decorative whitespace that reduces working area;
- motion-heavy consumer UI;
- card-on-card-on-card layouts.

---

# 4. Financial reconciliation reference study

## QuickBooks
Useful pattern:
- ending balance / cleared balance / difference is visually central;
- success target is an explicit zero difference;
- filters are secondary to the reconciliation state;
- reconciliation can be saved/resumed.

Adaptation to «المطابقة»:
- place Expected / Recorded / Adjustments / Final Difference in one compact score strip;
- the difference must remain visible while the operator filters or opens detail;
- approval should be visually downstream from the difference, not mixed with import controls.

References:
- Intuit reconciliation learning material and current training.

## Xero
Useful pattern:
- matching is transaction-centric;
- search by reference/name/amount is close to candidate rows;
- selected items show their contribution to the target total;
- a clear total-match state appears near the final action.

Adaptation:
- manual matching panel should continuously show:
  reference amount
  + selected/manual/electronic/account adjustments
  = compared amount
  → difference

Do not copy Xero visual styling; borrow the information model.

---

# 5. UI library study

## A. Native WPF Fluent theme
Status: **RECOMMENDED BASELINE**

Pros:
- shipped with platform;
- matches Windows 11;
- light/dark/system theme;
- minimal dependency;
- compatible with existing WPF controls.

Cons:
- not a full enterprise component suite;
- custom navigation/financial controls still required.

Decision:
**Use as the base theme in prototype.**

---

## B. CommunityToolkit.Mvvm
Status: **RECOMMENDED FOR ARCHITECTURE SPIKE**

Microsoft-maintained, framework-agnostic, supports WPF.

Useful:
- ObservableObject;
- ObservableProperty source generation;
- RelayCommand / AsyncRelayCommand;
- weak messenger when justified.

Decision:
Use in rebuilt presentation layer if the spike confirms clean interoperability with existing services and test strategy.

Rule:
Do not use Messenger as a global event bus to recreate hidden coupling.

Reference:
https://learn.microsoft.com/dotnet/communitytoolkit/mvvm/

---

## C. WPF UI (lepoco/wpfui)
Status: **OPTIONAL TARGETED SPIKE**

MIT; active; provides Fluent-oriented navigation, NumberBox, dialogs, snackbar and Windows 11 behaviors.

Potential value:
- NavigationView-like shell;
- NumberBox;
- standardized dialogs/notifications.

Risk:
- overlap with native Fluent theme and our custom semantic design layer;
- possible unnecessary framework ownership over shell/navigation.

Decision:
Do **not** adopt globally by default.
Prototype only the controls that solve a measurable gap.

Reference:
https://github.com/lepoco/wpfui

---

## D. MaterialDesignInXamlToolkit
Status: **NOT DEFAULT**

Mature and active WPF toolkit.

Strengths:
- broad control styling;
- icon pack;
- dialogs/cards/themes.

Why not default:
- Material visual language is not the target;
- adding another theme layer conflicts with the goal of eliminating overlapping dictionaries.

May be reconsidered only for a specific isolated control gap.

---

## E. MahApps.Metro
Status: **NOT DEFAULT**

Mature WPF toolkit with window chrome, theming and dialogs.

Why not default:
- overlaps native Fluent/window shell;
- would add another global visual framework while the current problem already includes layered styling.

---

## F. Commercial WPF suites
Status: **NO CURRENT NEED**

Do not introduce DevExpress/Telerik/etc. merely to get a better DataGrid.

First optimize native WPF:
- UI virtualization;
- recycling;
- async data retrieval;
- smaller visual trees;
- measured templates.

Only open a paid-tool request if a real feature/performance gap survives profiling.

---

# 6. WPF performance implications

Microsoft guidance emphasizes:
- UI virtualization for large lists;
- container recycling;
- careful templates;
- iterative measurement.

RevenueSystem implications:
- preserve DataGrid row/column virtualization;
- avoid wrapping large data grids inside ScrollViewer that disables virtualization;
- virtualize result/card collections;
- do not render hidden complex panels for every cashier row;
- defer details until selected;
- measure load, scroll and filter latency before/after each slice.

Reference:
https://learn.microsoft.com/dotnet/desktop/wpf/advanced/optimizing-performance-controls

---

# 7. Keyboard/accessibility research

Microsoft guidance treats keyboard navigation as a primary model and requires visible focus, logical traversal and keyboard alternatives to pointer actions.

RevenueSystem should go beyond minimum accessibility because keyboard speed is a core operator requirement.

Adopt:
- visible focus ring in light/dark/high contrast;
- semantic AutomationProperties.Name;
- predictable Tab order;
- pane-level navigation strategy;
- explicit shortcut registry;
- no clickable non-Control element without keyboard equivalent;
- no color-only financial meaning.

Reference:
https://learn.microsoft.com/windows/apps/design/accessibility/keyboard-accessibility

---

# 8. Design references selected by the Council

Use these as concept references, not templates to copy:

1. **WPF Gallery / Windows Fluent**
   - shell simplicity;
   - native surface;
   - navigation hierarchy.

2. **QuickBooks Reconciliation**
   - difference-first hierarchy;
   - state before detail;
   - filter/tool separation.

3. **Xero Reconciliation**
   - candidate matching close to amounts;
   - selected-item contribution;
   - explicit matched-total feedback.

4. **Existing RevenueSystem operator contract**
   - RTL;
   - keyboard-first;
   - dense financial data;
   - Iraqi currency semantics;
   - branch/cashier/day context.

The final design should look like none of these individually.

---

# 9. Recommended visual direction

Working name:
**Fluent Financial Operations**

Characteristics:
- Windows-native, not web-dashboard cosplay;
- right-side RTL navigation;
- quiet neutral surfaces;
- compact 4px-based spacing;
- 40px default control target, 36px compact mode;
- 12–14px dense table text depending on DPI;
- 44–48px list rows where touch is not primary;
- one accent color;
- success/warning/danger used only for state;
- financial numbers aligned consistently;
- optional detail pane rather than modal proliferation;
- limited elevation;
- borders and spacing define structure more than colored cards.

---

# 10. Library adoption gate

No library is adopted by research alone.

For each candidate:
1. create isolated prototype;
2. build on YASSIN;
3. open through GUI;
4. test light/dark/RTL;
5. test keyboard/focus;
6. test DataGrid/control performance;
7. inspect package transitive dependencies;
8. compare implementation complexity;
9. record uninstall/rollback;
10. Council accepts/rejects.

Current recommendation:
- Native Fluent: **SPIKE FIRST**
- CommunityToolkit.Mvvm: **SPIKE FIRST**
- WPF UI: **OPTIONAL CONTROL-LEVEL SPIKE**
- MaterialDesign: **DEFER/REJECT DEFAULT**
- MahApps: **DEFER/REJECT DEFAULT**
- Commercial suite: **NO REQUEST**
