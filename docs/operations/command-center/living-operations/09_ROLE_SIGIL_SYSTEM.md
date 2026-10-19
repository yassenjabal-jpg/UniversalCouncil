# UniversalCouncil Role Sigil System

Status: STUDIO-SUPERVISED COMPONENT IDENTITY CONTRACT

## Purpose

Role Sigils are the primary visual identity for Council/Studio functions inside Living Operations.

They are not mascots, avatars, people, or claims that separate runtime agents exist.

A Sigil is a semantic control that answers:

- what function is active;
- why it is active;
- what state it is in;
- whether it is thinking/reviewing/blocked/completed;
- what context opens when the Owner interacts with it.

## Family grammar

All Sigils share:

- one geometric core;
- one outer semantic ring;
- optional reasoning rings;
- optional truth/blocker badge;
- one label;
- one short role/function subtitle at expanded sizes.

Base visual constraints:

- readable at 20–24px;
- recognizable at 40–48px;
- expressive at 64–80px;
- no face;
- no human portrait;
- no cartoon body;
- no decorative pseudo-personality;
- no color-only identification.

## State layers

Layer 0 — identity glyph  
Layer 1 — operational state ring  
Layer 2 — reasoning depth rings when applicable  
Layer 3 — truth/attention badge  
Layer 4 — transient motion cue when state changes

Supported operational states:

- IDLE
- ACTIVATED
- WORKING
- REVIEWING
- WAITING
- BLOCKED
- COMPLETED
- UNKNOWN

State precedence:

1. BLOCKED
2. UNKNOWN
3. WAITING
4. WORKING / REVIEWING
5. COMPLETED
6. ACTIVATED
7. IDLE

A Sigil cannot show COMPLETED if the backing object is UNKNOWN.

## Core Council Sigils

### Chair / Decision Controller
Concept:
central directional aperture.

Meaning:
frames the decision and routes review.

Primary interaction:
open Decision Orchestration Context.

### Evidence & Research
Concept:
layered lens / concentric verification planes.

Meaning:
evidence gathering, provenance and contradiction search.

Primary interaction:
open Evidence Role Context.

### Red Team
Concept:
split prism / opposing wedge.

Meaning:
falsification, strongest objection and failure testing.

Primary interaction:
open Dissent & Challenge Context.

### Practicality & Execution
Concept:
directed vector through a bounded gate.

Meaning:
feasibility, dependencies and execution path.

Primary interaction:
open Execution Feasibility Context.

### Risk & Consequence
Concept:
contained impact wave inside protective boundary.

Meaning:
downside, severity, likelihood and reversibility.

Primary interaction:
open Risk Context.

### Human / User Advocate
Concept:
human-centered orbit / path around a central point.

Meaning:
workflow burden, usability and operator impact.

Primary interaction:
open User Impact Context.

### Cost-Benefit & Value
Concept:
balanced converging bars / value delta.

Meaning:
cost, time, benefit and opportunity cost.

Primary interaction:
open Value Context.

### Synthesis & Alternatives
Concept:
multiple paths converging without erasing branch history.

Meaning:
candidate alternatives and synthesis.

Primary interaction:
open Alternatives & Synthesis Context.

## Studio Sigils

### Media Producer
Concept:
pipeline controller with bounded stage gates.

Primary interaction:
open Studio Control Context.

### Writing
Concept:
structured line/segment becoming locked script frame.

Primary interaction:
open Writing Stage Context.

### Pre-production
Concept:
grid/shot plan resolving into a sequence.

Primary interaction:
open Pre-production Context.

### Visual Asset Production
Concept:
layer stack resolving into a frame.

Primary interaction:
open Asset Production Context.

### Motion & Compositing
Concept:
keyframe path / connected motion points.

Primary interaction:
open Motion Stage Context.

### Picture Editing
Concept:
timeline cuts / splice geometry.

Primary interaction:
open Edit Stage Context.

### Sound Design & Mix
Concept:
waveform inside a controlled envelope.

Primary interaction:
open Audio Stage Context.

### Thumbnail & Packaging
Concept:
framed image + focus point.

Primary interaction:
open Packaging Context.

### Assurance & Delivery
Concept:
verified output box / seal.

Primary interaction:
open Delivery/QC Context.

## Specialist extension grammar

A specialist may introduce a new Sigil only if:

- its function is materially different;
- it follows the same stroke/shape family;
- it has a documented semantic destination;
- it does not duplicate an existing core function;
- it is added to the machine-readable Sigil registry.

## Semantic color handling

Role identity tint is secondary.

Operational state color is authoritative:

- Blue — active work;
- Green — verified/completed;
- Gold — Owner attention;
- Coral — blocker/risk;
- Violet — reasoning/unknown/discovery;
- Cyan — tool/connection context.

Do not assign 24 unrelated saturated role colors.

## Reasoning rings

Reasoning rings are shown only when:

- a role/task is using a reasoning-capable model;
- the current task has a known reasoning effort.

Fast:
1 ring.

Standard:
2 rings.

Deep:
3 rings.

Max:
4 layered rings or equivalent extended treatment.

Unknown/unsupported:
no fabricated ring depth; show explicit unknown/unsupported state.

## Interaction contract

Desktop:
- hover: role/function tooltip;
- click: Role Context drawer;
- keyboard Enter/Space: same action;
- focus ring required.

Android:
- tap: Role Context sheet;
- long press: quick actions only if same actions exist visibly elsewhere.

Role Context always includes:
- why activated;
- current task;
- state;
- findings;
- strongest dissent if relevant;
- evidence links;
- model/reasoning when applicable;
- recent contributions to this project.

## Motion contract

Activation:
path appears -> state ring activates -> Sigil settles.

Working:
low-frequency ring phase motion only.

Reviewing:
bounded scan/rotation cue, never endless spinner.

Blocked:
working motion stops; blocker badge appears.

Completed:
single verified settle/pulse then static.

Reduced Motion:
all above become direct state changes/fades.

## Studio acceptance

Reject a Sigil if:
- it looks like a mascot;
- it has no semantic destination;
- it implies a human/agent identity unsupported by runtime;
- it requires color to be understood;
- it animates continuously without operational meaning;
- it becomes unreadable below 24px.

