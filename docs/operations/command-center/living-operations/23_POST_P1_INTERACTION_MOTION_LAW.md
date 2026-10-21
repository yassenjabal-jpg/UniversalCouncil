# Post-P1 Interaction + Motion Law

Status: MURTAKAZ GOVERNING HARDENING
Stage: STAGE_7
P1: COMPLETE

## Core law

A visual affordance is a promise.

If an element looks clickable, tappable, pressable, draggable or otherwise interactive, it MUST do one of the following:

1. navigate to a real governed surface;
2. open a real inspector/details/evidence/context surface;
3. change a real local UI state;
4. capture or preview an explicit owner intent without pretending the intent was executed;
5. be visibly unavailable/disabled with a truthful reason.

A primary action MUST NOT exist only to play an animation, pulse, highlight or show a generic "pressed" message.

## Motion law

Every implemented animation must have exactly one or more declared purposes:

- NAVIGATION — preserves spatial/context continuity;
- STATE — makes a state change legible;
- FEEDBACK — confirms a completed local UI interaction.

Decorative-only motion is rejected.

Motion never creates operational truth. UNKNOWN remains UNKNOWN. Success motion requires verified success state.

## Current approved motion map

| Motion | Purpose | Reduced Motion |
|---|---|---|
| Screen reference/native transition | NAVIGATION | direct state swap / restrained fade |
| Context drawer enter/exit | NAVIGATION + STATE | instant open/close |
| Role button pulse | FEEDBACK | static selected state |
| Role activation ring | STATE + FEEDBACK | static emphasis |
| Secondary activation ring | FEEDBACK | static emphasis |
| Notice fade | FEEDBACK | immediate hide after feedback interval |

## Primary action rule while Stage 8 is closed

Actions such as Start, Approve, Request Changes, Reject, Restore, Fork, Promote or destructive operations may NOT imply runtime execution.

While runtime authority is false, those controls must perform a truthful function such as:

- Execution Readiness inspection;
- Owner Intent Preview;
- Recovery Intent Preview;
- Evidence inspection;
- governed navigation.

The surface must explicitly state that no live command was dispatched.

## Accessibility

- Keyboard and pointer must reach the same semantic result.
- Focus returns after drawers close.
- Reduced Motion preserves all meaning.
- No essential meaning depends on animation.
- Disabled/unavailable state must be explicit in text, icon or state label.

## Acceptance

Al-Murtakaz may approve a screen only when:

- clickable-looking elements are functionally mapped;
- feedback-only primary actions are absent;
- animations have a declared purpose;
- motion durations remain within the Motion Bible classes;
- Reduced Motion preserves the same semantic outcome.
