# Owner Motion Intent Clarification — In-Screen Living Elements

Date: 2026-10-22  
Authority: Owner clarification  
Project: UniversalCouncil / Command Center / Al-Murtakaz  
Applies to: Motion Remediation, PR #72 and all later motion acceptance

## Owner clarification

The intended animation target is **not primarily screen-to-screen transition choreography**.

The intended target is **purposeful motion inside the screen itself**, especially:

- icons;
- vector/sigil elements;
- state indicators;
- routing lines;
- badges/chips;
- progress/current markers;
- interactive controls;
- semantic illustrations attached to real UI state.

The supplied owner video is a **motion-behavior reference only**.

Reference fingerprint:

`sha256:64ecb6d501aec1fd3dbead54d3330db447539bfc508a8442839cb969c150b00f`

It MUST NOT be used as a visual-style reference.

Forbidden derivation from the reference video:
- colors;
- layout;
- typography;
- iconography;
- composition;
- branding;
- visual density;
- visual identity.

The Command Center's existing locked visual identity remains authoritative.

## Correction to current interpretation

The existing W1.1 navigation work proved useful infrastructure:

- exact-head capture;
- real-host WGC;
- timing discipline;
- Full/Reduced Motion evidence;
- navigation continuity.

However, **navigation transitions alone do not satisfy the Owner's motion objective**.

Therefore:

`W1.1 navigation evidence = recorder/navigation baseline, not final owner motion acceptance`.

## Governing motion priority

Priority order is now:

1. **IN-SCREEN SEMANTIC MOTION**
2. direct interaction feedback
3. state visualization
4. object/role/artifact motion
5. navigation continuity
6. decorative motion — normally rejected

## Required in-screen motion families

### 1. Role / Sigil life

Examples:
- participating role Sigil activates;
- active/inactive/unknown state changes are visible;
- reasoning rings phase subtly only when semantically active;
- unrelated roles stay quiet.

Motion must map to real role/state identity.

### 2. Route / connection motion

Examples:
- route grows only when routing occurs;
- route settles after destination activation;
- route reverses only on a real return event;
- decorative routing paths must not pretend to be active work.

### 3. Status / current indicators

Examples:
- RUNNING uses restrained current/pulse;
- WAITING_OWNER visibly pauses at the owner decision state;
- BLOCKED stops forward motion;
- COMPLETE settles and stops.

No fake progress.

### 4. Interactive icon/vector feedback

Examples:
- hover/focus response;
- press response;
- selected/active state;
- expand/collapse affordance;
- inspect/open affordance.

If an icon/vector looks interactive, its motion must lead to a real function,
inspector, state change, or truthful preview.

### 5. Artifact / semantic object motion

Examples:
- artifact detaches from source;
- follows a short semantic route;
- destination acknowledges arrival;
- returned artifact visibly returns;
- identity is preserved through the movement.

### 6. Micro-state motion

Examples:
- badge transition;
- chip state;
- verification mark;
- blocker state;
- evidence-ready state;
- notice/focus cue.

Use Motion Bible M1/M2 timing classes unless a stronger semantic class is
explicitly justified.

## Anti-decoration law

The goal is not to make everything constantly move.

Allowed:
- purposeful idle/current cues at low frequency;
- state-linked motion;
- direct manipulation feedback;
- semantic activation;
- inspectable object motion.

Rejected:
- endless bounce;
- random wobble;
- decorative spinning;
- parallax for spectacle;
- motion that exists only to make the screen look busy;
- motion that implies runtime activity not backed by state.

## Eight-screen acceptance change

For each of the eight canonical screens, the motion review must now include an
**in-screen motion inventory**:

`element -> semantic trigger -> motion -> function/result -> reduced-motion equivalent`

A screen does not pass because its entry/exit transition looks good.

It passes only when its important stateful/interactable elements have truthful,
purposeful motion where motion materially improves comprehension or feedback.

## Reduced Motion

Reduced Motion keeps the same semantic outcome while removing:
- route drawing travel;
- pulses;
- springs;
- long vector travel;
- flourish.

It retains:
- state;
- icon/label;
- direct fade;
- focus;
- before/after clarity.

## Immediate roadmap consequence

Before W1.1 can be proposed for Owner acceptance:

1. reclassify existing navigation/WGC result as infrastructure + navigation baseline;
2. inventory icon/vector/stateful elements across all eight screens;
3. design in-screen motion behavior for those elements;
4. implement event-backed/state-backed motion;
5. prove click/inspect/function mapping for interactive-looking elements;
6. capture Full + Reduced Motion evidence showing the elements moving inside the
   screen, not only transitions between screens;
7. route through Product Workshop, Visual QA, Accessibility and Al-Murtakaz;
8. present the resulting videos to the Owner.

Stage 7 remains authoritative. Stage 8 stays closed. Runtime authority remains
false. W1.2 must not be treated as accepted merely because navigation evidence
passes.
