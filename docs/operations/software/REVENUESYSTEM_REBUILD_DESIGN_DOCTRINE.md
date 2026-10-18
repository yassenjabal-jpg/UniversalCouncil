# RevenueSystem 2.0 — Rebuild Design Doctrine
Version: 1.0
Date: 2026-10-17
Authority: Owner decision + Council radical rebuild review

## Prime directive

**BUILD THE BEST PRODUCT FOR THE WORK, NOT THE BEST VERSION OF THE OLD UI.**

The old application may answer:
- what must happen;
- what must be calculated;
- what must be stored;
- what must be audited;
- what must be permitted.

It does **not** answer:
- how many screens exist;
- where navigation lives;
- whether a workflow is a page/window/pane;
- what a dashboard looks like;
- what the visual hierarchy should be.

---

## Product model

RevenueSystem 2.0 is a:
**Day-centric Financial Operations Workspace**

Not:
- a set of CRUD pages;
- a dashboard with links;
- a collection of WPF windows;
- a web-style SaaS shell.

---

## Six workspaces

1. **اليوم — Day Console**
2. **المطابقة — Reconciliation Studio**
3. **المالية — Finance Ledger**
4. **التقارير — Reports Center**
5. **البيانات — Data Operations**
6. **الإدارة — Administration**

Login/lock/onboarding are system states, not workspaces.

---

## Interaction primitives

Prefer:
- workspace;
- tab;
- inspector;
- side sheet;
- inline step;
- queue;
- command palette;
- command bar;
- status bar.

Use modal only when blocking is semantically required.

---

## Shell rule

No wide permanent navigation sidebar is required.

Default:
- narrow RTL command rail;
- workspace tabs;
- context bar;
- main workbench;
- optional inspector;
- status bar.

---

## Visual rule

The sole governing RevenueSystem visual language is:

# **EDITORIAL FINANCIAL ENGRAVING**

Authority:
`docs/operations/software/REVENUESYSTEM_2_ART_DIRECTION_LOCK.md`

RevenueSystem 2.0 must visually communicate:
- precision;
- trust;
- control;
- density;
- state;
- secure-financial craft;
- authored desktop identity.

The visual language is inspired by the craft of secure financial documents:
- guilloché;
- engraved linework;
- ledger rules;
- registration marks;
- institutional seals;
- paper layering;
- denomination-strip geometry.

It does **not** use literal pictures of money as identity.

Canonical palette:
- Paper Ivory `#F6F1E8` — dominant work surface;
- Deep Forest `#173C32` — institutional structure / verified states;
- Cobalt `#174FA6` — primary interaction/focus;
- Clear Blue `#2B73C9` — active interaction;
- Sky Blue `#8EACD2` — quiet interactive support;
- Warm Parchment `#D9C8B1` — paper/material support;
- Brass Gold `#B58A3E` — restrained micro-accent only;
- Charcoal `#151515` — text/anchors;
- semantic red — difference/risk/destructive only.

Composition:
- narrow RTL command rail;
- work-item tabs;
- business context bar;
- one dominant workbench region;
- optional context inspector;
- compact status bar;
- dense operational surfaces stay quiet;
- artistic expression increases only in shell/context/status/report framing.

Materiality:
- subtle financial-paper warmth;
- security-print patterns only in non-data areas;
- precise ledger borders;
- one meaningful institutional seal at most;
- restrained depth through layering, not large shadows.

Typography:
- refined modern Arabic display treatment for identity/headings;
- modern Arabic sans for operational controls/data;
- tabular financial numerals;
- explicit currency/sign/context.

Explicitly forbidden:
- real dollar portraits or large literal banknotes;
- real bank logos;
- national/government emblems;
- bank buildings or architecture as identity;
- Babylonian/Baghdadi ornament;
- Saudi/country-specific visual branding;
- casino/luxury wealth styling;
- crypto aesthetics;
- dark-green-everywhere treatment;
- gold-everywhere treatment;
- generic SaaS card walls;
- glassmorphism;
- neon/cyberpunk;
- fake antique paper;
- huge rounded cards;
- web-product hero sections;
- decorative charts with no operational purpose.

Concept images created on 2026-10-18 define the approved visual grammar only. Any generated country/currency/architecture drift in those images is explicitly non-authoritative.

### Universal application rule

Editorial Financial Engraving applies to **all RevenueSystem presentation surfaces: past, present and future**.

There is no grandfather clause for:
- previously implemented RevenueSystem 2.0 screens;
- legacy screens still reachable;
- previously accepted visual prototypes;
- dialogs/popups/system states;
- shared controls.

Previously passed finance/data/architecture/behavior gates retain their evidence, but visual acceptance must be rerun after each existing surface is migrated to the current visual constitution.

# Finance rule

Money values are first-class visual objects.

They must have:
- predictable alignment;
- currency identity;
- sign clarity;
- comparison clarity;
- source/context clarity.

Color never carries financial meaning alone.

---

## Keyboard rule

Keyboard-first is an architecture requirement.

Commands need:
- stable shortcut;
- focus behavior;
- discoverability;
- conflict rules;
- automation identity.

---

## Design-system rule

Only four style layers:
1. native Fluent baseline;
2. semantic tokens;
3. shared components;
4. feature-local styles.

No public style key duplicated across multiple non-theme dictionaries.

---

## Architecture rule

New View code may not:
- open AppDbContext;
- call SaveChanges;
- implement financial rules;
- instantiate feature services;
- infer permissions as the only authorization check.

---

## Removal rule

A legacy screen is not preserved because:
- it exists;
- it has tests;
- users know where it is;
- recreating it is easier.

It is preserved only if its **capability** remains necessary.

---

## Migration rule

Every old UI class must end in exactly one state:
- migrated;
- intentionally removed;
- temporary compatibility fallback;
- system-only/onboarding.

No orphan screen survives by accident.

---

## Proof rule

A visually excellent workspace is still rejected if:
- financial parity fails;
- persistence differs;
- keyboard efficiency regresses materially;
- permission boundaries weaken;
- recovery becomes ambiguous;
- performance is unacceptable.

Likewise, a perfectly compatible slice is rejected if it reproduces poor workflow merely for parity.

---

## North-star test

For every proposed screen ask:

> If the old UI had never existed, would we still design it this way today?

If the answer is no, redesign it.
