# Command Center Product Studio

Version: 1.0  
Status: PROJECT-LOCAL PRODUCT DESIGN STUDIO  
Parent inspiration: Media Production Cell 2.1 principles  
Scope: Windows Command Center + Android Owner Companion

## Mission

Design, prototype, review and hand off the Living Operations experience as a coherent product system.

This Studio is **not** the media production Studio.

It is a project-local Product Design & Interaction Studio created specifically for Command Center.

## Inherited Studio principles

The project Studio inherits these proven operating principles:

- smallest effective team;
- one persistent coordination/control function;
- phase-routed craft functions;
- explicit stage ownership;
- accepted input before craft begins;
- verified output before handoff;
- downstream functions do not silently repair locked upstream artifacts;
- checkpoint before risky stage exit;
- bounded recovery;
- bounded Human Assistance;
- `UNKNOWN != SUCCESS`;
- Owner gates remain external to Studio craft authority.

It does not inherit media-specific:
- title gate;
- script pipeline;
- narration;
- cinematography;
- sound mix;
- thumbnail packaging;
- public media publication pipeline.

## Operating model

Mode:

**PRODUCT_DESIGN_STUDIO_WITH_GATED_VERTICAL_SLICES**

Principle:

`audit -> experience architecture -> visual/motion system -> component system -> vertical slice -> cross-platform adaptation -> fidelity/QA -> engineering handoff`

Only one function owns a craft artifact at a time.

Other functions may review in parallel, but may not silently edit the owner's locked artifact.

## Functions

### CC-ST-01 — Product Studio Producer

Status:
CONTROL_PLANE_ALWAYS_ACTIVE

Owns:
- schedule;
- dependencies;
- stage open/close;
- review routing;
- artifact registry;
- handoffs;
- return tickets;
- Studio acceptance status.

Does not:
- self-approve craft;
- overwrite discipline specialists;
- grant execution authority.

### CC-ST-02 — Experience Architect

Status:
PHASE_ROUTED_CRAFT

Owns:
- mental model;
- information architecture;
- project-first workspace;
- Home/Today/Projects/Waiting flow;
- context-preserving navigation;
- desktop/mobile task journeys.

### CC-ST-03 — Interaction Choreography Director

Status:
PHASE_ROUTED_CRAFT

Owns:
- Interactive Semantic Objects;
- click/tap/focus behavior;
- no-dead-surface;
- drawer/peek/sheet behavior;
- gesture semantics;
- interaction state transitions.

### CC-ST-04 — Visual Systems Director

Status:
PHASE_ROUTED_CRAFT

Owns:
- Living Operations visual identity;
- semantic color;
- depth;
- composition;
- typography;
- visual hierarchy;
- cross-screen consistency.

### CC-ST-05 — Motion Systems Director

Status:
PHASE_ROUTED_CRAFT

Owns:
- Motion Bible;
- event-backed animation;
- handoff;
- fork;
- recovery;
- Autopilot current;
- completion;
- Reduced Motion equivalents.

### CC-ST-06 — Role Sigil & Iconography Designer

Status:
PHASE_ROUTED_CRAFT

Owns:
- Role Sigil family;
- operational iconography;
- state legibility;
- non-mascot identity.

### CC-ST-07 — Design Systems Engineer

Status:
PHASE_ROUTED_CRAFT

Owns:
- tokens;
- component anatomy;
- component states;
- reuse;
- desktop/mobile semantic parity;
- implementation-ready specs.

### CC-ST-08 — Windows Experience Lead

Status:
PHASE_ROUTED_CRAFT

Owns:
- Windows layout;
- RTL desktop behavior;
- keyboard;
- pointer/focus;
- WPF-feasible motion;
- DPI/resolution adaptation;
- desktop performance design constraints.

Does not own:
runtime execution logic.

### CC-ST-09 — Android Experience Lead

Status:
PHASE_ROUTED_CRAFT

Owns:
- mobile information density;
- Compose-feasible interactions;
- notifications/deep links;
- tap/swipe/long-press mapping;
- media review;
- lifecycle/offline UX;
- haptics.

Does not own:
server-side authorization.

### CC-ST-10 — Prototype & Interaction Engineer

Status:
PHASE_ROUTED_CRAFT

Owns:
- non-authoritative interactive prototypes;
- fixture-driven flows;
- motion proof;
- component state demos;
- capture for review.

Prototype state must remain clearly labeled and isolated from runtime truth.

### CC-ST-11 — Accessibility Reviewer

Status:
MANDATORY_CLEARANCE

Owns:
- keyboard;
- focus;
- screen-reader semantics where applicable;
- contrast;
- color-independent meaning;
- touch target size;
- Reduced Motion;
- no gesture-only critical action.

May block Studio acceptance for accessibility failure.

### CC-ST-12 — Visual Fidelity & QA Reviewer

Status:
MANDATORY_CLEARANCE

Owns:
- fidelity to Living Operations;
- generic-SaaS drift detection;
- broken interaction affordance;
- animation consistency;
- screen-state completeness;
- concept-to-implementation comparison.

Cannot approve truth/security.

### CC-ST-13 — Human Assistance Pool

Status:
ON_DEMAND_ASSISTANCE

Used only for the smallest bounded action needed.

Human return must be verified before Studio continues.

## Macro phases

### PS0 — Project Audit
Input:
current product/runtime truth.

Output:
project-specific design problem map.

Gate:
PROJECT_CONTEXT_LOCK

### PS1 — Experience Architecture
Output:
screen hierarchy, task flows, navigation, focus model.

Gate:
EXPERIENCE_ARCHITECTURE_LOCK

### PS2 — Living Visual + Motion System
Output:
Visual Bible, Motion Bible, Sigils, semantic states.

Gate:
VISUAL_MOTION_LOCK

Current project:
Owner direction is already adopted; implementation fidelity remains reviewable.

### PS3 — Component System
Output:
tokens, anatomy, states, interaction map.

Gate:
COMPONENT_SYSTEM_LOCK

### PS4 — Windows Vertical Slice
Output:
Living Project Workspace interactive prototype.

Gate:
WINDOWS_PROTOTYPE_ACCEPTED

### PS5 — Android Companion Vertical Slice
Output:
mobile project/decision/Pulse prototype.

Gate:
ANDROID_PROTOTYPE_ACCEPTED

### PS6 — Cross-Platform Semantics
Output:
shared object/event behavior review.

Gate:
CLIENT_SEMANTIC_PARITY_ACCEPTED

### PS7 — Accessibility + Performance + Fidelity
Output:
clearance evidence.

Gate:
DESIGN_ASSURANCE_ACCEPTED

### PS8 — Engineering Handoff
Output:
implementation packet, component contracts, motion specs, QA fixtures.

Gate:
IMPLEMENTATION_READY

This gate does not grant execution authority.

## Artifact ownership

Each stage has one authoritative craft owner.

Reviewers:
- may annotate;
- may reject;
- may issue Return Ticket;
- may propose change.

They may not silently edit another function's locked artifact.

## Return Ticket

Required fields:
- ticket ID;
- source function;
- detecting reviewer;
- artifact;
- problem;
- evidence/reference;
- requested correction;
- do-not-change boundary;
- acceptance criteria;
- return target.

## Mandatory clearances before Studio acceptance

Every major interactive surface:
- Interaction review;
- Visual QA;
- Accessibility.

Every motion-heavy surface:
- Motion review;
- Reduced Motion review;
- performance review request when risk is material.

Every truth-bearing surface:
Project Council Product Truth review.

Every remote/authority-bearing surface:
Project Council Security/Remote Trust review.

## No decorative craft rule

The Studio must reject:
- clickable-looking dead icons;
- animated objects with no state meaning;
- fake role activity;
- fake tool activity;
- fake completion;
- decorative checkpoints/forks not mapped to real objects;
- copied reference-video character/layout language.

## Android/Windows rule

Share:
- semantic object identity;
- states;
- truth labels;
- events;
- decisions.

Do not force:
- same layout;
- same navigation;
- same animation distance;
- desktop hover concepts on mobile.

## Relationship to parent Studio

The Command Center Product Studio does not alter `company/config/media_venture.json`.

The media Studio remains available for media projects.

This Product Studio may borrow operating principles but owns a separate role registry, pipeline and review gates.

