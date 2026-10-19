# Living Operations Interaction Choreography

Status: INTERACTIVE SEMANTIC OBJECT CONTRACT

## Core law

**Every visible interactive object must have Meaning + Action.**

The UI may not use apparent buttons, clickable-looking Sigils, animated icons, cards, rails or thumbnails as decoration only.

## Interaction states

Every interactive component defines:
- rest;
- hover/focus (desktop);
- pressed;
- selected/active;
- disabled + reason;
- loading/awaiting truthful response;
- error/unknown;
- success where verified.

## Desktop interaction model

Primary:
- click = inspect/select/action;
- double-click is avoided as a required path;
- hover = preview/tooltip only;
- keyboard focus = equal to pointer access;
- right-click/context menu only for secondary expert actions.

Context preservation:
- use right-side/edge inspector, popover or contextual drawer for first-level inspection;
- full navigation only for sustained work.

## Android model

- tap = open/select;
- long press = quick actions where discoverable and never the only path;
- swipe = Pulse navigation or explicitly signposted approve/reject only where accidental action risk is low;
- critical actions require explicit button confirmation;
- back always returns to preserved project context.

## Semantic object routing table

### Role Sigil
Click/tap:
- open Role Context.

Role Context includes:
- why activated;
- current assignment;
- current state;
- findings;
- dissent;
- linked evidence;
- recent project contributions;
- reasoning/model state when relevant.

Actions:
- Ask about this role's finding;
- Open evidence;
- Open full review;
- change model/reasoning only when policy/authority permits.

### Reasoning Rings
Click/tap:
- open Model & Reasoning inspector.

Show:
- provider/model;
- effort level;
- why this level;
- task scope;
- fallback chain;
- usage/cost where available;
- supported alternative levels.

### Artifact
Click/tap:
- open Artifact Viewer.

Actions depend on artifact:
- preview;
- compare;
- open source tool;
- show provenance;
- promote;
- comment;
- request change;
- download when available.

### Filmstrip Frame
Click/tap:
- open Version Inspector.

Show:
- visual/media/code state;
- timestamp;
- source role/tool;
- reason for change;
- previous/next;
- evidence;
- approval/return state.

Actions:
- Compare;
- Ask;
- Open artifact;
- Fork from here if this frame maps to valid checkpoint/version;
- Restore only through a governed recovery action.

### Checkpoint
Click/tap:
- Checkpoint Inspector.

Show:
- checkpoint ID;
- created time;
- verified state;
- artifact versions;
- expected next action;
- related evidence.

Actions:
- Compare current;
- Create fork;
- View state;
- Request recovery if authority allows.

### Branch
Click/tap:
- Branch Workspace.

Show:
- branch purpose;
- parent checkpoint;
- model/reasoning;
- changed artifacts;
- test/QC;
- evidence;
- branch status.

### Autopilot Current Marker
Click/tap:
- Live Execution Detail.

Show:
- current stage;
- current task;
- active role;
- model + reasoning;
- active tool;
- last checkpoint;
- elapsed time;
- recovery/fallback summary;
- next planned step.

Actions:
- Pause;
- Stop & Preserve;
- Review activity;
- adjust permitted project policy.

### Tool icon
Click/tap:
- Tool Inspector.

Show:
- Ready / Active / Connected / Unknown / Blocked;
- last verified timestamp;
- current project;
- current artifact;
- recent outputs;
- evidence.

Actions:
- Open related artifact;
- open tool only if an implemented, authorized action exists;
- view diagnostics.

### Pulse
Click/tap:
- Pulse Detail.

Show:
- artifact/media first;
- What changed;
- Why;
- What happens next;
- truth badge;
- evidence;
- related task/project.

Actions:
- Approve where appropriate;
- Comment;
- Ask;
- Create Task;
- Create Decision;
- Research;
- Open Project.

### Decision Card
Click/tap:
- enter Decision Context.

Show:
- question;
- why now;
- Council recommendation;
- strongest dissent;
- evidence;
- approve impact;
- reject impact;
- uncertainty.

Actions:
- Approve;
- Request Changes;
- Reject;
- Ask;
- Inspect Evidence.

### Truth Badge
Click/tap:
- Evidence Peek.

No badge is decorative.

### Workflow Stage Node
Click/tap:
- Stage Detail.

Show:
- entry condition;
- current/last artifact;
- owner role;
- QC;
- checkpoint;
- handoff;
- next stage.

### Notification
Tap:
- deep link to exact semantic object and state, not generic Home.

## No dead surface test

For every design review, reviewers must ask:
1. Does it look clickable?
2. If yes, what exact action/context does it open?
3. Is that behavior implemented?
4. If not implemented, is it truthfully disabled?
5. Does it preserve context?
6. Does keyboard/touch equivalent exist?

A failure blocks visual acceptance.

## Destructive/irreversible interactions

Do not place destructive actions on gesture-only paths.

Require:
- explicit label;
- consequence summary;
- authoritative server-side validation;
- idempotency/nonce rules where applicable.

Android approval is not itself an authorization boundary.

## Empty/blocked states

Every blocked element explains:
- why;
- current truth state;
- what unlocks it;
- whether Owner action is required.

Do not leave dead empty panels.

