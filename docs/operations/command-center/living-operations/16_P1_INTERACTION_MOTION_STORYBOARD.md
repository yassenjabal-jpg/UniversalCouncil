# P1 — Interaction + Motion Storyboard

Status: MURTAKAZ-SUPERVISED WORKING STORYBOARD
Phase: VISUAL / INTERACTION
Runtime: PROTOTYPE FIXTURES ONLY

## Sequence A — Owner starts work

### Frame A1
Home at rest.

Focus:
Command Composer.

Motion:
quiet; no fake project activity.

### Frame A2
Owner presses Start.

Motion:
M1 press -> M2 route preview.

Interactive:
route preview can inspect:
- mode;
- model;
- reasoning;
- attachments.

### Frame A3
Prototype project is created.

Motion:
Command Composer contracts into project identity and Project Workspace becomes primary.

Do not show Autopilot RUNNING until prototype emits its explicit event.

## Sequence B — Project comes alive

### Frame B1
Project Core appears.

Autopilot:
RUNNING.

Three roles activate:
- Evidence.
- UX/Human.
- Red Team.

Motion:
Project Core -> route lines -> Sigils.

### Frame B2
Reasoning rings appear only for roles with known prototype reasoning state.

Click each:
open contextual drawer.

### Frame B3
Evidence artifact arrives.

Filmstrip:
new frame enters.

Truth:
EVIDENCE-BACKED, not VERIFIED.

Evidence badge click:
Evidence Peek.

## Sequence C — Handoff

Artifact moves:
Evidence -> UX.

Motion:
source highlight
-> object detaches
-> short route
-> destination accepts.

During final state:
artifact remains clickable.

If returned:
route reverses and Return Ticket appears.

## Sequence D — Red Team return

Filmstrip:
Before
→ UX Revision
→ Red Team Return.

Red Team Sigil:
REVIEWING.

Then BLOCKER or RETURN state.

No aggressive alarm animation.

Click:
strongest objection + evidence.

## Sequence E — Owner Decision

Autopilot:
WAITING_OWNER.

Current rail stops.

Decision Surface rises.

Background project remains visible but de-emphasized.

Owner can inspect:
- recommendation;
- dissent;
- evidence;
- consequences.

Action:
Request Changes.

Motion:
decision resolves into history.

Autopilot remains stopped until separate state event resumes it.

## Sequence F — Recovery

Prototype tool failure.

Autopilot:
RECOVERING.

Motion:
1. current flow stops;
2. last verified checkpoint receives focus;
3. bounded rewind;
4. restored state remains pending;
5. only VERIFIED restored event resumes flow.

If verification fails:
UNKNOWN / HOLD.

## Sequence G — Fork

Owner opens Checkpoint Inspector.

Action:
Create Fork.

Motion:
single project line splits:
- Branch A — Privacy First;
- Branch B — Automation Rich.

Each branch:
- artifact preview;
- test/quality state;
- truth badge.

Compare mode:
A and B move into paired visual focus.

No branch is selected by visual weight before decision.

## Sequence H — Completion

Selected branch reaches prototype completion.

Required event:
PROJECT_COMPLETED_VERIFIED.

Motion:
- rail resolves;
- final artifacts gather;
- active motion settles;
- Work Receipt appears.

No confetti.

Work Receipt includes:
- requested;
- completed;
- artifacts;
- evidence;
- models/reasoning;
- tools;
- time/usage if known;
- recovered issues;
- checkpoints;
- decisions;
- next action.

## Android paired storyboard

### Mobile M1 — Notification
"مشروع X يحتاج قرارك"

Tap:
refresh exact semantic object before rendering.

### Mobile M2 — Decision
Decision card with preview and dissent.

Tap Evidence:
bottom sheet.

### Mobile M3 — Media/Artifact review
Preview first.

Feedback:
comment / voice / marker.

### Mobile M4 — Autopilot
compact current state.

Actions:
Pause / Review Activity / Stop & Preserve.

No unrestricted host command.

## Reduced Motion storyboard

Replace:
- route drawing;
- artifact travel;
- rewind;
- fork growth;

with:
- source focus;
- crossfade;
- destination focus;
- final state.

No meaning is lost.

## Murtakaz review points

Each sequence must be reviewed for:

### هيئة المرتكز
- truth;
- authority;
- evidence;
- durability;
- security;
- human impact.

### مشغل المرتكز
- composition;
- interaction;
- motion;
- visual identity;
- accessibility;
- platform fit.

No sequence becomes locked without:
APPROVED_BY_AL_MURTAKAZ
