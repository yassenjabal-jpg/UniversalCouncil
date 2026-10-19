# Command Center Project Council <-> Product Studio Collaboration

Status: PROJECT-LOCAL COLLABORATION CONTRACT

## Separation of responsibility

### Project Council
Owns:
- decision quality;
- truth/evidence;
- architecture/feasibility;
- security;
- human impact;
- durable workflow review;
- cross-platform semantic review;
- model/memory policy review;
- blockers and alternatives.

### Product Studio
Owns:
- UX architecture;
- interaction choreography;
- visual system;
- motion;
- Sigils/iconography;
- components;
- prototypes;
- platform adaptation;
- design fidelity.

### Owner
Owns:
- final project direction;
- locked art-direction changes;
- authority expansion;
- material privacy tradeoffs;
- irreversible/external actions;
- governance replacement.

## Working loop

`Requirement/Problem`
-> Project Council frame
-> Studio brief
-> Studio craft
-> Studio internal review
-> Project Council domain clearances
-> Studio revision if needed
-> Owner gate where required
-> accepted artifact
-> engineering handoff

## No silent cross-edit

Council reviewers do not directly rewrite a locked Studio craft artifact.

They issue:
- finding;
- blocker;
- Return Ticket;
- alternative;
- acceptance condition.

Studio does not silently weaken:
- truth;
- security;
- architecture;
- authority;
- accessibility blocker.

## Conflict resolution

### Craft disagreement
Visual/interaction disagreement without material risk:
Studio lead recommendation.

### User-impact disagreement
Human/UX reviewer has evidence-backed blocker scope.

### Truth disagreement
Product Truth reviewer can block unsupported claim/state.

### Security/authority disagreement
Security/Remote Trust can block within domain.

### Architecture disagreement
Architecture/Execution can block boundary violation.

### Residual tradeoff
Escalate to Owner with:
- recommendation;
- strongest dissent;
- evidence;
- downstream consequence.

## Review modes by change

### Minor craft
Examples:
- spacing;
- copy polish;
- local icon geometry.

Review:
Studio only, LIGHT.

### Interaction/component change
Examples:
- new drawer;
- new Sigil action;
- Filmstrip behavior.

Review:
Studio + UX + Product Truth as needed.

### Motion semantics
Review:
Motion Studio + Interaction + Product Truth.
Add Performance/Accessibility when material.

### Windows architecture-sensitive UI
Review:
Windows Lead + Architecture/Execution + UX.

### Android remote/decision behavior
Review:
Android Lead + Security/Remote Trust + Cross-platform semantics.

### Autopilot/recovery UI
Review:
Durable Autopilot + Product Truth + UX + Motion.

### Model/reasoning/fallback controls
Review:
AI Runtime/Model/Memory + UX + Product Truth.
Security/Value on demand.

### Art-direction change
ARENA + Studio + Owner.

## Shared artifacts

Shared project objects:
- Project Core;
- Role Sigils;
- Artifact;
- Filmstrip frame;
- Checkpoint;
- Branch;
- Decision;
- Truth Badge;
- Tool state;
- Autopilot state;
- Pulse;
- Work Receipt.

Council validates meaning/truth.

Studio validates presentation/interaction.

Neither may change the authoritative runtime state.

## Review output

Every material review records:
- artifact/screen/component;
- scope;
- activated roles;
- Studio owner;
- findings;
- blockers;
- motion/interaction notes;
- evidence;
- acceptance criteria;
- outcome:
  - ACCEPT
  - ACCEPT_WITH_MINOR_FIXES
  - RETURN_TO_STUDIO
  - OWNER_DECISION_REQUIRED

## Anti-bureaucracy

Do not activate the full Project Council for every visual change.

Use the smallest set capable of changing the decision.

Studio may batch small visual polish items into one review.

