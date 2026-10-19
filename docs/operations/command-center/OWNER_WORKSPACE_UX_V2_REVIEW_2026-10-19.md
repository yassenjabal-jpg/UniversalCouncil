# UniversalCouncil Command Center — Owner Workspace UX Review v2
Date: 2026-10-19
Status: POST-PULSE COUNCIL + STUDIO REVIEW
Pulse contract: COMMAND_CENTER_PULSE_PRODUCT_CONTRACT_2026-10-19.md
Stage 8: NOT OPENED

## Review question

After adopting UniversalCouncil Pulse, can the Owner:
1. know what to do immediately;
2. understand what changed without reading every update;
3. identify decisions/blockers;
4. enter a project and continue real work;
5. see tools, models, providers, evidence, and system truth without having infrastructure dominate the experience?

## Joint verdict

`UX_V2_DIRECTION_ACCEPTED_WITH_RESTRUCTURE`

The previous Stage 7 surface remains useful as an advanced system truth view, but it must not be the primary Owner workspace.

The product mental model becomes:

`START -> UNDERSTAND -> DECIDE -> WORK -> VERIFY`

Pulse belongs mainly in UNDERSTAND and can promote items into DECIDE/WORK.

---

# Council review

## Human / User Advocate

Finding:
The Owner should never need to know the internal architecture before completing the first task.

Required changes:
- first screen must contain one unmistakable primary action;
- show human language before system codes;
- every empty state must explain what the user can do next;
- disabled actions must explain why and what unlocks them;
- do not require reading the entire Pulse feed.

New proposal:
**Since You Were Away** — a three-part delta:
- what changed;
- why it matters;
- what needs you.

## Practicality & Execution

Finding:
Pulse adds value only if updates can become real work with minimal friction.

Required changes:
- Story -> Action available directly on relevant cards;
- no dead navigation;
- every primary surface has one dominant next action;
- technical configuration moves to a system drawer/page.

New proposal:
**One-click Work Receipt** after any material completion:
`Requested -> Done -> Changed -> Evidence -> Cost/Usage -> Next`

## Evidence & Research

Finding:
Visual updates can create false confidence if provenance is hidden.

Required changes:
Every material Pulse/card receives a truth badge:
- VERIFIED
- EVIDENCE-BACKED
- PROPOSAL
- UNKNOWN
- OWNER-DIRECTIVE

New proposal:
**Evidence Peek** — hover/click a truth badge to see the minimum provenance without leaving the current workflow.

## Red Team

Finding:
A beautiful social feed can become noise, status theater, or fabricated activity.

Required changes:
- no likes/followers/streaks;
- duplicate suppression;
- quiet low-value updates;
- no automatic completion claims;
- no avatar/persona language implying independent humans/processes.

New proposal:
**Noise Budget** — each project has a visible low/medium/high interruption policy. Only decision-changing items may break Quiet Mode.

## Risk & Consequence

Finding:
Screen capture and generated visual updates may expose secrets.

Required changes:
- capture off by default;
- app/window exclusion;
- local review before publication;
- redaction;
- no credential/token capture.

New proposal:
**Private Draft Shelf** — auto-generated Pulses remain private drafts until explicitly published or promoted.

## Synthesis

Finding:
The strongest UX is not a feed-centric product. It is an Owner workspace with Pulse as a contextual layer.

New proposal:
**Three lenses** that recompose the same data:
- TODAY
- PROJECT
- SYSTEM

The user does not navigate architecture; the application changes emphasis based on intent.

---

# Studio review

## Media Producer

Finding:
The Project screen should remain the richest operational surface.

New proposal:
**Project Filmstrip** — a horizontal Pulse strip directly beneath the project stage tracker showing:
- last accepted handoff;
- current work;
- latest visual change;
- blocker;
- next owner decision.

## Editorial / Showrunner

Finding:
Updates must tell a story, not just report events.

New proposal:
Each important project update uses:
`What changed -> Why -> What happens next`

This becomes the canonical human-readable update format.

## Visual / Motion

Finding:
Before/After is more useful than isolated screenshots.

New proposal:
**Compare Mode** for design/video/UI/script versions with:
- before;
- after;
- change reason;
- linked artifact;
- approval action.

## Production craft

Finding:
Opening files and tools is a major part of real work and should not be buried.

New proposal:
**Tool Dock** — a compact, persistent expandable strip that exposes all installed/connected additions:
- GitHub;
- Photoshop;
- After Effects;
- Premiere Pro;
- YASSIN Host;
- Tailscale;
- Model Router;
- Providers;
- Memory Fabric;
- Evidence Bus;
- Remote Owner;
- Approvals;
- Notifications;
- Plugins/Connectors.

The dock shows only truthful states such as Connected / Ready / Unknown / Blocked.

## Assurance

Finding:
Approvals and evidence must be visually distinct from chat/comments.

New proposal:
**Decision Stack** — one dedicated Owner queue for:
- approvals;
- blockers;
- questions;
- title locks;
- publish gates;
- model/provider failure choices.

---

# New UX architecture

## 1. Home — Owner Workspace

Priority order:
1. Command Composer
2. Since You Were Away
3. Needs Your Decision
4. Pulse Strip
5. Active Work
6. Recent Results

Do not lead with:
- Tailnet;
- transport;
- phase gates;
- evidence counters;
- provider internals.

Those remain accessible under SYSTEM.

### Command Composer
Natural-language entry:
`What do you want to accomplish?`

Controls:
- Council / Studio / Auto;
- Task model override;
- attach files;
- start task.

## 2. Today

A new lightweight mode rather than another complicated dashboard.

Shows:
- 3 most important changes;
- decisions waiting;
- active project milestones;
- one Wild Card idea;
- one unresolved Unknown if material.

Target:
Owner understands the day in under 30 seconds.

## 3. Projects

Project workspace becomes the strongest screen.

Top:
- title;
- project health;
- current stage;
- primary decision/action.

Then:
- Project Filmstrip / Pulses;
- current artifacts;
- stage deliverables;
- decisions/blockers;
- comments;
- tools used by this project;
- model/provider routing;
- evidence.

## 4. Tasks

Task list is operational, not decorative.

Every row answers:
- what;
- who/which role owns it;
- project;
- state;
- why it matters;
- next action.

## 5. Waiting for You

Dedicated Owner Decision Stack.

Cards are intentionally large and low-density.
One decision per card.

Actions:
- approve;
- request changes;
- reject;
- ask question;
- inspect evidence.

## 6. Council

Do not present roles as separate human agents unless runtime proves it.

Show:
- role registry;
- active review;
- why each role was activated;
- findings/dissent;
- linked evidence;
- resulting decision.

## 7. Studio

Show pipeline rather than organization chart.

`Writing -> Pre-production -> Production`

For each active project:
- current department/stage;
- accepted input;
- output;
- QC;
- next handoff;
- return ticket if blocked.

## 8. Results

Results are Work Receipts, not a generic activity log.

Each result:
- request;
- outcome;
- artifact;
- evidence;
- decisions;
- cost/usage when available;
- next recommended action.

## 9. System

All advanced operational truth lives here:
- tools/additions inventory;
- models/providers;
- Memory Fabric;
- Evidence Bus;
- Remote Owner;
- YASSIN;
- Tailscale/transport;
- execution gates;
- health;
- logs.

This is where the old Stage 7 dashboard concept remains valuable.

---

# New interaction proposals after Pulse adoption

## A. Since You Were Away Replay

On application open:
`You were away for 7h 14m — 11 updates collapsed into 4 meaningful changes.`

The Owner can replay them chronologically or jump only to decisions.

## B. Ask This

Every meaningful card/artifact/Pulse gets:
`Ask about this`

Examples:
- Why did the Council reject this?
- What changed between these versions?
- What evidence supports this claim?
- What happens if I reject it?

The question inherits the object's project/evidence context.

## C. Decision Rewind

Before a high-impact approval, show:
- what led here;
- alternatives rejected;
- dissent;
- downstream impact.

This prevents approvals detached from context.

## D. Focus Lens

Workspace toggle:
- Owner;
- Council;
- Studio;
- Evidence;
- All.

The underlying data does not change; only emphasis/filtering changes.

## E. Project Filmstrip

Pulse becomes a visual filmstrip of the project story.

Clicking a frame opens:
- artifact;
- before/after;
- discussion;
- evidence;
- decision action.

## F. Idea Greenhouse

Deferred suggestions do not disappear.

Each idea has:
- why deferred;
- reopen trigger/date;
- linked evidence;
- current relevance.

Time Capsule Pulses feed this surface.

## G. Collision Lab

The Owner may intentionally select two Pulses and choose:
`Find a useful connection`

Output is always a proposal and can be promoted into:
- experiment;
- task;
- research question;
- project idea.

## H. Follow the Work

When a compatible tool/runtime later supports it, a user may follow a bounded live artifact/view similar to a presenter/follow mode.

It must not imply unrestricted screen access.

## I. Quiet Mode

Modes:
- Focus;
- Normal;
- Review.

Focus:
only blockers and Owner decisions interrupt.

Normal:
meaningful Pulses appear without interruption.

Review:
show full project timeline and evidence.

## J. Contribution Trail

Role profile shows useful contribution history:
- findings;
- suggestions adopted;
- blockers caught;
- artifacts/reviews;
- evidence links.

It does NOT show productivity ranking, post count, or social popularity.

## K. No Dead Surface Rule

Any UI element that looks actionable must be:
- actionable;
- truthfully disabled with reason;
- or visually non-interactive.

The Stage 7 rail-button problem is explicitly prohibited in the redesigned product.

## L. Universal Command Palette

`Ctrl+K` searches and acts across:
- projects;
- tasks;
- files;
- tools;
- roles;
- Pulses;
- approvals;
- settings.

Examples:
- Open project X
- Ask Council to review Y
- Show blockers
- Switch model for current task
- Open Photoshop artifact
- Show YASSIN status

---

# First-use journey

A new Owner should be able to complete this path without documentation:

1. Open application.
2. See “What do you want to accomplish?”
3. Enter a request.
4. Review a short routing/plan preview.
5. Start.
6. Watch Active Work.
7. Receive a Pulse when meaningful progress occurs.
8. Respond to a Decision Stack card if needed.
9. Open the project workspace.
10. Receive a Work Receipt at completion.

Acceptance target:
**First useful task starts in <= 60 seconds without understanding internal architecture.**

---

# Visual direction constraints retained

- no architecture-themed decorative identity;
- compact/narrow sidebar;
- project screen remains information-rich;
- all additions/tools are visible through Tool Dock/System inventory;
- technical truth remains available but subordinate to Owner workflow;
- Arabic RTL first;
- restrained art direction; product utility beats decoration.

---

# Architecture Boundary Audit

Verdict:
`PASS_DESIGN_BOUNDARY_WITH_IMPLEMENTATION_CONSTRAINTS`

This review introduces no authority or persistence implementation.

Implementation must keep:
- WPF = presentation;
- commands/use-cases = application layer;
- evidence/files/providers = service/infrastructure boundaries;
- no shell/DB/filesystem/network configuration from XAML or code-behind;
- no static global UX state used as execution authority.

---

# Recommended implementation sequence

UX-1 — Application shell + real navigation + no-dead-surface rule

UX-2 — Home Owner Workspace + Command Composer + Since You Were Away

UX-3 — Projects workspace + Project Filmstrip + artifacts + Decision Stack

UX-4 — Pulse core presentation + drafts + filters + Story -> Action

UX-5 — Tool Dock + models/providers + truthful operational states

UX-6 — Council/Studio role and pipeline views

UX-7 — Work Receipts + Results + evidence peek

UX-8 — Advanced patterns: Collision Lab, Time Capsule, Follow the Work

No Stage 8 execution authority is opened by this sequence.
