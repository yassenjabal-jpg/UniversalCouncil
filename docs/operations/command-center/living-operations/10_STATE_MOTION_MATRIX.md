# Living Operations State / Motion Matrix

Status: IMPLEMENTATION MOTION SPECIFICATION

## Purpose

This matrix maps real product state to visual treatment, motion, interaction and stop conditions.

No motion may infer a state that the runtime/evidence layer has not supplied.

## Project

| State | Visual | Motion | Primary action |
|---|---|---|---|
| IDLE | neutral | none | Open project |
| ACTIVE | blue current rail | subtle current flow | Inspect current work |
| WAITING_OWNER | gold stop marker | flow halts at decision | Open Decision |
| BLOCKED | coral blocker | all forward motion stops | Inspect blocker |
| RECOVERING | checkpoint focus | bounded rewind cue | Open Recovery |
| PAUSED | neutral pause marker | no flow | Resume / inspect |
| COMPLETE | green resolved rail | one settle pulse | Open Work Receipt |
| UNKNOWN | violet/neutral explicit unknown | no fake activity | Inspect evidence/state |

## Autopilot

| State | Visual | Motion | Rules |
|---|---|---|---|
| OFF | inactive control | none | no implied automation |
| READY | outlined control | none | can start if allowed |
| RUNNING | blue current | low-frequency flow | current marker clickable |
| WAITING_OWNER | gold | stop | notification may escalate |
| BLOCKED | coral | stop | no retry theater |
| RECOVERING | violet/blue checkpoint | rewind then pause until verified | UNKNOWN != SUCCESS |
| SUSPENDED_RESOURCE_WAIT | violet | static waiting | no fake progress |
| PAUSED | neutral | none | preserve checkpoint |
| COMPLETE | green | completion settle | show receipt |

## Role Sigil

| State | Visual | Motion | Destination |
|---|---|---|---|
| IDLE | muted | none | Role Context |
| ACTIVATED | identity + blue ring | activation draw | Role Context |
| WORKING | blue/violet ring | gentle phase | Live Role Context |
| REVIEWING | violet | bounded scan | Review Context |
| WAITING | gold small marker | no continuous motion | Wait reason |
| BLOCKED | coral badge | stop | Blocker/Dissent |
| COMPLETED | green badge | one settle | Contribution |
| UNKNOWN | violet unknown badge | none | Evidence/unknown reason |

## Artifact

| State | Visual | Motion |
|---|---|---|
| DRAFT | neutral/violet | none |
| CURRENT | blue focus | subtle focus |
| IN_HANDOFF | connected path | M3 handoff travel |
| RETURNED | gold/coral | reverse route |
| VERIFIED | green | single stamp/settle |
| REJECTED | coral | stop; no bounce |
| UNKNOWN | explicit unknown | none |

## Decision

| State | Visual | Motion |
|---|---|---|
| NOT_REQUIRED | absent | none |
| REQUIRED | gold elevated | Decision Mode M4 |
| UNDER_REVIEW | blue/violet | evidence/role paths active |
| APPROVED | green | card resolves to history |
| CHANGES_REQUESTED | gold | route to source |
| REJECTED | coral | card resolves + project state updates |
| EXPIRED/STALE | violet/neutral | none; explicit refresh required |

## Checkpoint

| State | Visual | Motion |
|---|---|---|
| CREATED | small marker | brief appear |
| VERIFIED | green-centered marker | settle |
| SELECTED | blue/violet focus | focus halo |
| RESTORING | violet | bounded rewind route |
| RESTORED | blue -> verified if proven | settle after verification |
| INVALID/INCOMPATIBLE | coral | none |

## Fork / Branch

| State | Visual | Motion |
|---|---|---|
| PROPOSED | dashed branch | none |
| CREATING | growing branch line | M4 |
| ACTIVE | solid branch | subtle current |
| COMPARED | paired focus | no loop |
| SELECTED | green/blue emphasis | settle |
| REJECTED | muted | none |
| UNKNOWN | explicit unknown | none |

## Tool

| State | Visual | Motion |
|---|---|---|
| CONNECTED/READY | neutral + small green/cyan status | none |
| ACTIVE | cyan emphasis | one activation cue |
| WAITING | gold | none |
| BLOCKED | coral | none |
| UNKNOWN | violet/neutral | none |
| DISCONNECTED | muted | none |

Tool activity animation stops immediately when underlying activity ends or becomes unknown.

## Pulse

| Type | Visual | Motion |
|---|---|---|
| Achievement | green ring | ring draws once |
| Suggestion | gold | small reveal |
| Blocker | coral | no loop |
| Question | blue | reveal |
| Unknown | violet | slow static accent |
| Handoff | blue/cyan | bounded baton cue |
| Before/After | paired | transition on user action |
| Wild Card | violet/gold | reveal only |

## Truth badge

VERIFIED:
green, static after one confirmation cue.

EVIDENCE-BACKED:
blue/green, no completion implication.

PROPOSAL:
violet/gold.

UNKNOWN:
violet/neutral.

OWNER-DIRECTIVE:
gold/blue.

No badge flashes continuously.

## Reduced Motion matrix

All M3/M4 travel becomes:
- source highlight;
- crossfade;
- destination highlight;
- final state.

All loops disabled.

All state meaning preserved using:
- text;
- icon;
- color;
- position;
- badge.

## Failure rule

If runtime state and motion state diverge:
- stop animation;
- display UNKNOWN;
- preserve last verified state;
- expose Evidence/State Inspector.

