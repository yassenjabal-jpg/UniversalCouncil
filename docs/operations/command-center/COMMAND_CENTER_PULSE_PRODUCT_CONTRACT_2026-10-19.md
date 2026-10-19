# UniversalCouncil Command Center — Pulse Product Contract
Date: 2026-10-19
Status: OWNER-ADOPTED / DESIGN CONTRACT
Base: Stage 7 owner-device/tailnet lineage
Stage 8: NOT OPENED

## Decision

UniversalCouncil Pulse is adopted as a first-class product capability.

It is not a social feed and it is not a replacement for tasks, approvals, evidence, decisions, project memory, or execution gates.

The product model is:

`Real Work -> Pulse Draft/Update -> Owner/Role View -> Optional Promotion -> Durable Typed Artifact`

## Core concept

Pulse provides three complementary lanes:

1. **Human Pulse** — a role or the Owner intentionally shares a concise update.
2. **Evidence Pulse** — the system drafts a visual update from real artifacts, activity, or trusted evidence.
3. **Idea Pulse** — suggestions, blockers, unknowns, cross-role connections, and improvement ideas.

## Non-negotiable truth rules

- `PULSE_IS_COMMUNICATION_NOT_AUTHORITY`
- `UNKNOWN != SUCCESS`
- A system-generated draft may not silently publish itself.
- Material completion claims must preserve provenance to real evidence.
- A role is not presented as an independent human or independent runtime process unless runtime evidence proves that implementation.
- Promotion from Pulse creates a new typed artifact; it does not silently convert the original post into authority.
- Pulse does not grant shell, GUI, model/provider, filesystem, Adobe, or remote execution authority.
- Stage 7 and Phase 0 gates remain unchanged.

## Pulse types

- Achievement
- Suggestion
- Blocker
- Question
- Unknown
- Handoff
- Before / After
- Wild Card

Visual status rings should communicate type, not popularity:
- green — achievement;
- gold — suggestion;
- red — blocker;
- blue — owner decision/question;
- violet — discovery/unknown.

No likes, follower counts, leaderboards, posting streaks, or productivity scores are part of the accepted design.

## Adopted interaction patterns

### Verified Auto-Story
The system may draft a Pulse from:
- GitHub changes;
- project files;
- approved tool artifacts;
- task transitions;
- Evidence Bus records;
- accepted studio handoffs.

The draft shows the evidence source and remains a draft until explicitly published when publication is material.

### Story -> Action
Any relevant Pulse may offer bounded conversion actions:
- Create Task
- Request Approval
- Create Blocker
- Create Decision
- Attach Evidence
- Create Return Ticket
- Save to Project Memory
- Create Research Question

The destination artifact uses its own normal validation and authority controls.

### Before / After
When both artifact states exist, the Pulse may show visual comparison for:
- UI screens;
- design files;
- script revisions;
- video frames;
- reports;
- source changes.

### Story Baton
Studio handoffs may be visualized as a Pulse chain:
`Department -> Handoff -> Accepted / Returned -> Next Department`

This is presentation only. The canonical studio handoff and return-ticket contracts remain authoritative.

### Story Collision
The system may select two materially different Pulses and ask Synthesis to propose a non-obvious connection.

Every result is labeled:
`PROPOSAL / INFERENCE`

It never becomes a task, decision, or policy without explicit promotion.

### Unknown Story
Roles may publish:
`Something we do not know yet`

Unknowns are encouraged when decision-relevant. They can be promoted into research work without pretending certainty.

### Time Capsule
A useful but premature idea may be deferred with a bounded review date. When reopened, the UI must show:
- original context;
- why it was deferred;
- what has changed;
- whether the old assumption is still valid.

### Wild Card
One optional rotating role may be invited to answer:
`What useful thing has nobody asked for?`

This is discovery, not a posting quota.

### Work Reality Prompt
An optional bounded authenticity prompt may request a current work snapshot.

Rules:
- never required for activity scoring;
- no forced daily participation;
- screen capture is off by default;
- sensitive apps/fields must be excludable;
- credentials, tokens, private chats, and secrets must not be captured or published.

## Expiry and durability

Default ephemeral lifetime: 24 hours.

A Pulse remains durable when:
- pinned;
- promoted to a durable artifact;
- retained by project policy;
- required as handoff/history evidence.

Expired Pulses may remain in audit storage when required, while disappearing from the normal visual feed.

## Owner experience

### Home
The accepted top-level order is:
1. Command composer — “What do you want to accomplish?”
2. Since your last visit
3. Pulse strip
4. Needs your attention
5. Active work

### Project
A project should surface:
1. current stage and owner decision;
2. project Pulse timeline;
3. artifacts/files;
4. approvals and blockers;
5. tools and additions;
6. model/provider controls;
7. evidence and operational truth.

Technical infrastructure must remain available but should not dominate the first-use experience.

## Research inspirations

Useful patterns were compared against:
- Linear Pulse and structured project updates;
- Slack asynchronous Clips;
- Figma Spotlight / follow-a-collaborator behavior;
- Viva Engage Storyline;
- BeReal authenticity prompt mechanics.

UniversalCouncil does not copy those products. It combines selected interaction ideas with evidence provenance, project authority, Council governance, and Studio handoff rules.

## Architecture boundary

This adoption is a UX/product contract only.

It does not authorize:
- WPF code-behind execution logic;
- filesystem mutation from presentation;
- shell/PowerShell authority;
- DB authority;
- HTTP hosting changes;
- Tailscale configuration;
- provider/model dispatch.

Implementation must preserve the accepted Command Center architecture and use services/event projections behind the presentation layer.
