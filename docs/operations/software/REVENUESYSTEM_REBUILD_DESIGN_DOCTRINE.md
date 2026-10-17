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

The application must visually communicate:
- precision;
- speed;
- trust;
- density;
- state;
- authored visual identity.

### Studio cultural identity lock

RevenueSystem 2.0 must inherit the Studio's governing visual DNA:

**Editorial Renaissance Motion — adapted for desktop financial software.**

Canonical palette:
- Paper Ivory `#F6F1E8` — dominant application ground;
- Cobalt `#174FA6` — primary structural/accent color;
- Clear Blue `#2B73C9` — active/interactive emphasis;
- Sky Blue `#8EACD2` — secondary structure and quiet states;
- Warm Parchment `#D9C8B1` — subtle surface warmth, dividers, inactive editorial material;
- Brass Gold `#B58A3E` — restrained annotation/high-value accent only;
- Deep Forest `#173C32` — verified/success/financially healthy states;
- Charcoal `#151515` — text and visual anchors; never a dominant background.

Typography adaptation:
- Arabic display/headings: refined editorial Naskh or Naskh-influenced display treatment where legibility permits;
- Arabic body/data UI: contemporary sans optimized for dense financial use;
- Latin display: restrained editorial serif only in non-data identity moments;
- Latin/data body: neutral modern sans.

Material language:
- subtle paper/ivory warmth;
- very light print/paper grain where it does not reduce text/data clarity;
- cobalt rules and structural lines;
- brass micro-annotations;
- layered editorial panels rather than generic SaaS cards;
- no fake parchment, ornamental historical borders, or decorative classical imagery inside transactional UI.

Composition adaptation:
- use negative space deliberately in shell, empty states, onboarding and inspector headers;
- dense tables remain dense where work requires it;
- one dominant task focal point per workspace;
- avoid equal visual weight for every panel;
- hierarchy should feel editorial rather than dashboard-like.

Motion adaptation:
- object/panel wipes;
- page-shift transitions;
- line-drawing/reveal motion;
- subtle foreground occlusion;
- cobalt reset moments where appropriate;
- motion follows task meaning and state change;
- never animate every element simultaneously.

The Studio's video-specific imagery (classical figures, botanical/scientific cutouts, archival collage) is **not** copied into routine financial screens. The shared identity comes from palette, composition, typography, materiality, annotation language and motion grammar.

Explicitly rejected:
- Baghdad/Babylonian motifs added merely for local flavor;
- generic Windows-blue enterprise styling;
- decorative dashboard cards;
- excessive rounding;
- excessive shadows;
- empty “premium” whitespace;
- hero sections;
- web-product patterns without desktop value.

---

## Finance rule

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
