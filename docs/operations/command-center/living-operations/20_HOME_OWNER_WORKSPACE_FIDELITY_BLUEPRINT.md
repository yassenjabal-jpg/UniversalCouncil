# P1 — Home / Owner Workspace Fidelity Blueprint

Date: 2026-10-20  
Status: MURTAKAZ-APPROVED BLUEPRINT / VISUAL ARTIFACT PENDING  
Canonical parent: `home_owner_workspace`  
Canonical reference: `references/01-home_owner_workspace.png`  
Reference SHA-256: `7cb7d12f8819576ad4992158f6f0eb098ae3350a3684118ffc43192ea56749eb`

## 1. Purpose

This document converts the canonical Home reference into a bounded implementation blueprint.

It does **not** create a new visual direction.  
It does **not** approve a rendered Home screen.  
It does **not** authorize runtime behavior.

The reference image remains visually authoritative wherever this blueprint is incomplete or ambiguous.

## 2. Reference-observed composition

The Home reference uses a stable multi-rail desktop composition rather than a generic dashboard grid.

### Global frame

Preserve these visible zones and their relative hierarchy:

1. compact top identity/search bar;
2. narrow global navigation rail on the right;
3. wider status/context rail on the left;
4. large central owner workspace;
5. persistent bottom tool dock.

Do not mirror the entire composition merely because the product is Arabic-first. Technical fragments and tool identities may remain LTR where appropriate.

### Top bar

Observed hierarchy:

- UniversalCouncil / Command Center identity at upper left;
- global search centered across the upper frame;
- Owner identity and compact utility controls toward upper right;
- global navigation rail starts at the far right edge.

The top bar is quiet chrome. It must not visually compete with the command composer.

## 3. Owner command hero

The dominant Home question is:

**ماذا تريد أن تنجز؟**

It must remain the strongest textual statement on the screen.

A short supporting sentence may sit nearby, but it must remain subordinate.

The hero background may preserve the reference's very soft localized line/halo treatment. It must not become an independent decorative theme.

## 4. Command Composer

The composer is the highest-priority interactive surface on Home.

Preserve the reference composition:

- large rounded white container;
- primary text-entry region occupying most of the central/right portion;
- blue primary execution action at the far action edge;
- compact option controls below/inside the entry region;
- three routing cards grouped as a distinct adjacent block.

Reference routing cards:

- التنفيذ التلقائي;
- الاستوديو;
- المجلس.

Behavioral contract:

- exactly one routing mode is primary at a time;
- Auto may be the default prototype route;
- model/reasoning/web/tool controls must expose their actual prototype state;
- disabled/unavailable controls must show a reason;
- Start may not imply real execution authority.

The composer must feel like one coherent instrument, not a row of unrelated filter controls.

## 5. Left status/context rail

The left rail is a persistent operational summary, not a secondary navigation menu.

Observed stack:

1. Autopilot state card;
2. active-project count;
3. waiting-task count;
4. important-alert count.

The Autopilot card has the strongest presence in this rail.

Prototype truth rules:

- activity waveform/glow may animate only from an explicit prototype event;
- `UNKNOWN` never renders as healthy/green activity;
- zero-count cards remain visually quieter than active alerts;
- do not add infrastructure diagnostics here.

## 6. Council Pulse

Council Pulse is the first major section beneath the composer.

Preserve:

- one wide horizontal rounded surface;
- section title and compact health/state indicator;
- distinct colored circular role medallions;
- a fine connecting route/path language between medallions;
- concise role labels beneath/near each medallion.

The medallions are identity objects, not avatars.

Every medallion must be interactive:

- click -> Role Context;
- reasoning/state affordance -> Model/Reasoning inspector where applicable.

Static color identifies the role. State badges/animation communicate activity separately.

## 7. Active Work

Active Work follows Council Pulse and is the largest repeated-card area on Home.

Preserve three substantial project cards in the reference row.

Each card contains, in reference order/hierarchy:

- compact state badge;
- project title;
- one-line project description;
- progress indication;
- milestone/task/date context;
- small participating-role medallions;
- explicit open-project action;
- project-specific visual artifact/illustration area.

The three cards may use different restrained pastel identity tints, as in the reference.

Do not normalize them into monochrome KPI tiles.

No project card may claim verified/completed status without prototype truth backing.

## 8. Bottom information row

Preserve three distinct lower panels:

- منذ آخر زيارة;
- يحتاج قرارك;
- النتائج الأخيرة.

They are separate owner concerns and must not be merged into one feed.

### Since You Were Away

Purpose:
compact chronological updates.

Visual priority:
secondary to Active Work.

### Needs Your Decision

Purpose:
surface owner-blocking decisions.

Each row must show enough context to understand:

- what needs review;
- which project;
- why it matters now;
- the primary review action.

This panel receives stronger urgency than ordinary updates but must not overpower the composer.

### Recent Results

Purpose:
surface completed/verified outputs.

Truth labels are explicit. Green is used only where the prototype event/state supports verified completion.

## 9. Right global navigation rail

Preserve the reference-locked order:

1. الرئيسية;
2. المشاريع;
3. المجلس;
4. الاستوديو;
5. المعرفة;
6. الأدوات;
7. التقارير;
8. الإعدادات as the lower anchor.

The active destination receives the strongest blue emphasis.

Do not add Today / Tasks / Waiting / Results as new top-level rail items without a separately reviewed delta.

## 10. Bottom Tool Dock

Preserve a persistent horizontal dock.

Reference characteristics:

- grouped tool identities;
- compact app/tool chips;
- current/active tool state distinct from merely available tools;
- "all tools" access at the edge;
- strong tool brands/icons may remain visible where legally/technically appropriate.

Tool readiness is semantic:

- Active;
- Ready;
- Unavailable;
- Unknown.

Unknown must never look connected/ready.

## 11. Visual language lock for Home

Use only properties directly supported by the canonical reference family:

- warm off-white canvas;
- white rounded panels;
- fine cool-gray borders;
- soft low-elevation shadows;
- dark navy primary text;
- bright blue primary actions;
- restrained pastel panel/card tints;
- violet/blue/green/cyan/amber/red role medallions;
- localized soft halos;
- fine curved/dotted connector paths where the reference uses them.

Do not flatten the screen into a monochrome admin UI.

Do not increase saturation coverage beyond the reference.

Do not introduce a named decorative style, scenic motif, or unrelated visual identity.

## 12. Density and hierarchy

Home is intentionally information-rich, but hierarchy prevents it from feeling dense.

Priority order:

1. owner question;
2. command composer;
3. Council Pulse;
4. Active Work;
5. Needs Your Decision;
6. Since You Were Away / Recent Results;
7. persistent rails and tool dock.

The rails should remain readable but visually recessive.

## 13. Interaction states required in the first artifact

The first rendered Home artifact must visibly account for:

- default/idle Home;
- one selected composer routing mode;
- at least one active prototype project;
- no-owner-action-needed Autopilot state or an explicitly labeled alternative prototype state;
- hover/focus treatment for a project card;
- selected right-rail navigation item;
- active vs available tool distinction;
- visible keyboard focus example;
- explicit disabled/unknown example where applicable.

No animation timing is approved by this still-image blueprint.

## 14. Responsive review targets

Primary fidelity review:
- desktop composition matching the canonical reference aspect and density.

Secondary checks:
- 1366×768;
- 125% DPI;
- 150% DPI.

Do not redesign the composition for these targets; first preserve semantic hierarchy and avoid clipping/overlap.

Android is reviewed separately and does not inherit this desktop geometry.

## 15. Artifact acceptance checklist

A rendered Home candidate is eligible for Murtakaz review only if all are true:

- actual canonical Home reference was attached to the visual production step;
- parent SHA-256 matches the manifest;
- no rejected generated design was used as a source;
- the five-zone frame is preserved;
- command composer remains dominant;
- Council Pulse remains a wide role strip;
- three Active Work cards remain a major row;
- lower three-panel owner summary remains visible;
- role medallions match the reference language;
- right rail and bottom tool dock remain present;
- no generic SaaS/KPI-grid drift;
- no fake runtime success;
- side-by-side comparison evidence exists.

## 16. Next state

This blueprint authorizes production of exactly one bounded visual job:

`P1-HOME-ARTIFACT-001`

Allowed delta:
implementation cleanup needed to turn the canonical Home reference into a reviewable product artifact without changing its visual identity, composition family, role-medallion language, or owner-workflow hierarchy.

The Home screen itself remains:

`VISUAL_ARTIFACT_PENDING / MURTAKAZ_DECISION_PENDING`
