# P1 Remaining Native Reconstruction — Phased Completion Plan

Date: 2026-10-20
Status: ACTIVE
Purpose: finish the remaining canonical screens without repeating long unclosed work intervals or state drift.

## Operating rule

One phase = one bounded deliverable.

A phase may not silently remain at "implemented" after CI succeeds.
Every phase must explicitly move through:

1. BUILDING
2. IMPLEMENTED
3. CI_RENDER_VALIDATION
4. STRUCTURAL_FIDELITY_REVIEW
5. MURTAKAZ_STUDIO_REVIEW
6. CLOSED
7. NEXT_PHASE_OPENED

If CI succeeds, the state file must be closed in the same work sequence before moving on.

No phase may contain more than one primary screen reconstruction.

---

## Phase R1 — Owner Decision Mode

Scope:
- central decision surface;
- why-now / recommendation / dissent / impact;
- participating role identities;
- Evidence Peek;
- approve / request changes / reject / ask / inspect evidence;
- native motion and keyboard/focus behavior.

Acceptance:
- canonical reference remains parent;
- all major geometry preserved;
- no action claims a recorded decision unless runtime confirms it;
- reference / native / blend renders;
- Windows WPF build passes;
- Stage 0 and CodeQL pass.

Exit artifact:
- Owner Decision native screen evidence + state closure.

---

## Phase R2 — Checkpoint / Recovery / Fork

Scope:
- checkpoint timeline;
- selected checkpoint;
- branch A/B;
- branch comparison;
- event log;
- evidence;
- restore / fork / promote / delete action surfaces.

Acceptance:
- restore request never renders as restored before verified event;
- destructive delete remains guarded;
- branch comparison remains visually neutral;
- reference / native / blend evidence;
- WPF build + CI green.

Exit artifact:
- Recovery/Fork native screen evidence + state closure.

---

## Phase R3 — Pulse Visual Project Story

Scope:
- story timeline;
- Before / main story / After;
- five pulse cards;
- truth badges;
- evidence affordance;
- create-task / decision / research semantic actions.

Acceptance:
- no fake verified truth;
- pulse source remains traceable;
- reference / native / blend evidence;
- WPF build + CI green.

Exit artifact:
- Pulse Story native screen evidence + state closure.

---

## Phase R4 — Project Complete / Work Receipt

Scope:
- completion hero;
- seven-stage rail;
- business receipt;
- final artifacts;
- evidence;
- usage summary;
- recovered issues;
- fallbacks;
- checkpoints;
- council decisions;
- next action.

Acceptance:
- completion does not imply runtime success without state evidence;
- all receipt sections visible and interactive;
- reference / native / blend evidence;
- WPF build + CI green.

Exit artifact:
- Work Receipt native screen evidence + state closure.

---

## Phase R5 — Home Micro-Polish

Only Home.

Scope:
- typography;
- icon alignment;
- spacing;
- role medallion details;
- exact rail/dock alignment;
- hover/focus states;
- reduced-motion behavior.

Forbidden:
- macro layout changes;
- new modules;
- product rename;
- Council topology changes.

Acceptance:
- overlay comparison first;
- no structural drift;
- WPF render passes.

---

## Phase R6 — Project Workspace Micro-Polish

Only Living Project Workspace.

Scope:
- spacing;
- card proportions;
- active-role geometry;
- filmstrip;
- decision stack;
- tool/execution panels.

Acceptance:
- overlay comparison;
- no section reorder;
- WPF render passes.

---

## Phase R7 — Software Autopilot Micro-Polish

Only Software Autopilot.

Scope:
- checkpoint/fork geometry;
- diff legibility;
- branch cards;
- recovery actions;
- evidence/tool dock.

Acceptance:
- overlay comparison;
- no recovery truth drift;
- WPF render passes.

---

## Phase R8 — Studio Project Micro-Polish

Only Studio.

Scope:
- stage rail;
- media player;
- timeline;
- QC/tool context;
- handoff;
- active team;
- thumbnail fidelity.

Acceptance:
- overlay comparison;
- no reference bleed;
- media thumbnails retained;
- WPF render passes.

---

## Phase R9 — Cross-Screen Consistency Audit

Scope:
- shared top chrome;
- right navigation;
- Tool Dock;
- spacing rhythm;
- role sigils;
- drawer behavior;
- keyboard/focus;
- reduced motion;
- truth-state semantics.

No screen redesign is allowed here.

Acceptance:
- 8-screen render set generated;
- all references available in reference/native/blend where applicable;
- no structural regressions;
- all CI green.

---

## Phase R10 — Final Al-Murtakaz + Studio Review

Scope:
- final fidelity review of all eight screens;
- confirm interaction additions did not alter canonical visual language;
- confirm truth-state rules;
- confirm no rejected generation became a parent;
- confirm P1 native reconstruction can be closed.

Output:
- APPROVE or RETURN_FOR_CHANGES per screen.
- P1 only closes when all eight screens receive approval.

## Anti-stall rule

If work pauses for any reason, the state must record exactly one of:
- WAITING_FOR_CI
- RETURNED_FOR_CHANGES
- BLOCKED_EXTERNAL_TOOL
- READY_TO_CONTINUE

Never leave a phase at an ambiguous "implemented pending" state after evidence already exists.
