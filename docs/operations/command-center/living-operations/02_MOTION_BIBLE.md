# Living Operations Motion Bible

Status: STUDIO MOTION CONTRACT

## Mission

Motion communicates operational truth.

The governing rule is:

**Animation is navigation + state + feedback.**

If an animation does not explain:
- what changed;
- where an object moved;
- who owns work;
- what is active;
- whether an action succeeded;
- whether recovery occurred;
- or what can be inspected next;

it should normally be removed.

## Timing classes

### M1 — Micro
120–180ms

Use:
- press;
- hover/focus;
- chip state;
- tooltip;
- small badge transition.

### M2 — Component
200–300ms

Use:
- drawer;
- evidence peek;
- card expand/collapse;
- tab/section transition.

### M3 — Workflow
350–600ms

Use:
- artifact handoff;
- task promotion;
- stage transition;
- role activation routing.

### M4 — Project Event
500–800ms

Use:
- checkpoint recovery;
- fork split;
- Decision Mode focus transition;
- project completion transition.

Routine interaction should not exceed these ranges without an explicit reason.

## Easing

Motion character:
- fast start;
- smooth landing;
- minimal overshoot.

Semantic easing names:
- `standard-out`
- `standard-in-out`
- `gentle-spring` for very limited role/object settling
- `linear-progress` only for real continuous progress indicators

Do not use:
- repeated bounce;
- wobble;
- endless spinning;
- decorative parallax.

## Motion object law

Motion must correspond to a real object/event ID where the animation represents work.

Examples:
- moving artifact uses an artifact/handoff identity;
- branch split uses an actual fork/checkpoint identity;
- verified completion consumes a verified state;
- recovery rewind consumes a recovery event.

The UI must not invent activity.

## Autopilot current

Autopilot is represented as a quiet living rail.

Past:
- stable;
- verified markers where applicable.

Current:
- restrained pulse/current indicator;
- semantic blue unless current state changes.

Future:
- muted.

States:
- RUNNING — slow current flow;
- WAITING_OWNER — current stops at gold decision marker;
- BLOCKED — flow stops at coral blocker;
- RECOVERING — controlled backward cue to checkpoint then forward resume only after state confirms;
- SUSPENDED_RESOURCE_WAIT — no fake forward motion;
- COMPLETE — rail resolves and rests.

## Reasoning visualization

Reasoning rings are state visualization, not a productivity meter.

- Fast — one ring;
- Standard — two rings;
- Deep — three layered rings;
- Max — extended layered treatment only where provider/model supports it.

On click/tap, the rings resolve to the Model/Reasoning inspector.

Do not animate reasoning forever at a high frame rate. Use low-frequency subtle phase movement.

## Role activation

When routing activates roles:
1. Project Core remains fixed.
2. connection path appears;
3. relevant Sigils gain active state;
4. unrelated Sigils remain muted or absent.

Do not animate an entire council if only three roles are active.

## Handoff

Canonical visual story:
1. source stage verified/checkpointed;
2. artifact object detaches from source;
3. artifact follows a short semantic route;
4. destination highlights;
5. acceptance or return result appears.

If destination rejects:
- artifact does not vanish;
- state changes to RETURN;
- route visually returns to source;
- Return Ticket becomes inspectable.

## Story -> Action

When Pulse converts to task/decision/research:
- the visual object morphs/transfers toward the destination surface;
- destination confirms creation;
- the original Pulse remains in context as the source.

## Recovery

Recovery is not an error flash.

Sequence:
1. current work de-emphasizes;
2. last verified checkpoint becomes focus;
3. bounded rewind path indicates restoration;
4. new current state begins only after restored state is verified.

Never animate a recovery success before verification.

## Fork

Fork is a signature UniversalCouncil motion.

Sequence:
1. checkpoint selected;
2. source rail pauses;
3. branch line grows into A/B (or requested N);
4. each branch receives explicit identity and state;
5. original remains preserved.

Default is branch creation, not destructive history rewrite.

## Decision Mode

When Owner decision is required:
- background hierarchy lowers;
- Decision Card moves to primary depth;
- activated role/evidence paths remain visible;
- destructive/reject effects are not dramatized with alarming animation beyond semantic need.

After decision:
- card resolves into history;
- project flow resumes only if runtime state says it can.

## Project Complete

No confetti storm.

Completion:
- remaining verified stages settle;
- final artifacts gather into Work Receipt;
- current motion stops;
- one restrained completion pulse;
- `PROJECT COMPLETE` / localized equivalent appears;
- next recommended action becomes primary.

## Desktop interaction motion

Hover:
- 120–150ms outline/tonal response.

Click:
- immediate press response, then state transition.

Drawers:
- prefer horizontal/edge reveal consistent with RTL layout.

Avoid animating layout-heavy width/height when transform/opacity can communicate the same action.

## Android motion

Mobile uses:
- shared-element-like transition from notification/thumbnail to content;
- tap transitions;
- sheet/drawer movement;
- swipe between Pulse items;
- subtle haptic for material approve/blocker/complete/handoff accepted.

Do not reproduce desktop hover concepts on touch.

## Reduced Motion

Reduced Motion removes:
- route drawing animation;
- spring;
- pulsing loops;
- shared-element travel;
- rewind flourish.

It retains:
- state change;
- labels;
- color + icon;
- direct fade;
- clear before/after.

No operational meaning may depend on motion.

## Performance budget

Target:
- 60fps for primary interaction where hardware allows;
- no permanent high-frequency canvas animation;
- virtualize long Filmstrip/Pulse/timelines;
- cache thumbnails;
- use video proxies;
- avoid expensive live blur/shadow animation;
- prefer transform + opacity.

The Studio must reject motion that materially degrades responsiveness.

