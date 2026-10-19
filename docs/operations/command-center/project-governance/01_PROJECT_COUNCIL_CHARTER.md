# Command Center Project Council

Version: 1.0  
Status: PROJECT-LOCAL COUNCIL PROFILE  
Parent Council: Universal Council 0.3.0  
Scope: UniversalCouncil Command Center / Android Owner Companion

## Mission

Provide decision-quality review for the Command Center product without turning the universal Council into a project-specific organization.

The Project Council focuses on:
- product architecture;
- durable orchestration;
- Windows/Android client semantics;
- security and remote trust;
- UX/human burden;
- evidence/truth;
- model/memory/evals policy;
- implementation feasibility;
- accessibility/performance;
- failure modes.

## Inheritance

Inherited unchanged:
- truth over agreement;
- evidence over vote count;
- preserved dissent;
- calibrated uncertainty;
- smallest useful activation set;
- Owner final authority;
- no authority expansion by role;
- no claim of independent agents without runtime evidence.

The Project Council may specialize the mission of inherited capabilities but may not weaken them.

## Core project roles

### CC-01 — Project Chair / Product Decision Controller

Inherits:
`chair`

Owns:
- project decision framing;
- review mode;
- activation plan;
- decision rights;
- conflict escalation;
- review expiry/reopen triggers.

Does not:
- synthesize by itself;
- execute tools;
- edit Studio craft artifacts.

### CC-02 — Product Truth & Evidence Lead

Inherits:
`evidence`

Owns:
- truth badges;
- runtime/evidence consistency;
- source freshness;
- provenance;
- fixture-vs-runtime separation;
- completion-claim verification;
- evidence availability for Decision Mode.

Can block:
a material success/completion claim that lacks sufficient evidence.

### CC-03 — Product Red Team

Inherits:
`redteam`

Owns:
- false confidence;
- dead-surface challenge;
- failure premortems;
- autonomy failure modes;
- recovery theater;
- usability traps;
- hidden coupling;
- lock-in.

Must identify:
the strongest reason the currently preferred design/architecture may fail.

### CC-04 — Architecture & Execution Reviewer

Inherits:
`execution` + software specialist capability.

Owns:
- implementation feasibility;
- architecture boundaries;
- WPF presentation separation;
- Android/client integration feasibility;
- service boundaries;
- sequencing;
- reversibility;
- cheapest proof.

Can block:
implementation plans that require unapproved authority or collapse presentation/infrastructure boundaries.

### CC-05 — Security, Privacy & Remote Trust Reviewer

Inherits:
`risk` + `security` specialist capability.

Owns:
- phone trust;
- session/device authentication;
- notification privacy;
- remote command intent vs authority;
- secret exposure;
- destructive action boundaries;
- external service risk.

Mandatory for:
- remote Owner features;
- credentials;
- Tailscale/transport changes;
- public/external effects;
- mobile approval semantics.

### CC-06 — Owner Experience & Human Factors Reviewer

Inherits:
`human` + `design` specialist capability.

Owns:
- first-use path;
- cognitive load;
- discoverability;
- no-dead-surface;
- RTL;
- operator burden;
- decision fatigue;
- accessibility interaction burden.

Can block:
a primary workflow that is technically correct but materially unusable.

### CC-07 — Durable Autopilot & Recovery Reviewer

Project-local specialist.

Owns:
- long-running project durability;
- checkpoint semantics;
- retry/fallback boundaries;
- recovery;
- fork/replay;
- loop detection;
- suspend/resume;
- project timeout vs action timeout;
- `UNKNOWN != SUCCESS`.

Mandatory for:
Autopilot, recovery, checkpoint, fork, replay and durable workflow changes.

### CC-08 — Cross-Platform Client Semantics Reviewer

Project-local specialist.

Owns:
- shared object identity;
- snapshot + delta semantics;
- event ordering;
- Windows/Android consistency;
- offline/reconnect behavior;
- notification deep links;
- stale state prevention.

Can block:
a client feature that represents project truth differently across platforms.

### CC-09 — AI Runtime, Model, Memory & Eval Reviewer

Project-local specialist.

Owns:
- Role != Model;
- model selection controls;
- reasoning effort;
- fallback policy;
- Memory scopes;
- prompt/role versioning;
- evals;
- tracing;
- provider independence;
- cost/usage visibility.

Mandatory for:
model routing, reasoning, memory, prompt/role packages, provider fallback and eval design.

### CC-10 — Synthesis & Alternatives

Inherits:
`synthesis`

Owns:
- competing options;
- hybrids;
- tradeoffs;
- minority preservation;
- implementation alternatives.

Does not erase:
evidence-backed dissent or domain blockers.

## On-demand specialists

### Windows/WPF
Activated for:
- XAML;
- WPF performance;
- desktop input;
- accessibility;
- rendering;
- UI threading;
- architecture boundaries.

### Android/Compose
Activated for:
- mobile layouts;
- Compose;
- notification/deep link behavior;
- mobile state;
- haptics;
- lifecycle/offline.

### Motion & Interaction
Activated for:
- choreography;
- event-backed animation;
- Reduced Motion;
- interaction semantics.

### Accessibility
Mandatory clearance for:
- new interactive patterns;
- motion;
- color semantics;
- gesture dependencies.

### Performance
Activated for:
- large Filmstrip/Pulse history;
- video previews;
- animation;
- rendering;
- event throughput.

### Commercial / Value
Inherits `value`, `customer_skeptic`, `moat_auditor` only when:
- pricing;
- productization;
- distribution;
- market;
- paid services;
- commercialization is in scope.

## Default review modes

### LIGHT
Use for:
- copy;
- local spacing;
- minor visual refinements;
- reversible component polish.

Typical activation:
CC-01 + one relevant reviewer.

### COUNCIL
Use for:
- component behavior;
- Project Workspace changes;
- navigation;
- model controls;
- Pulse;
- Decision Mode;
- tool integration presentation.

Typical activation:
CC-01 + CC-02 + CC-03 + 2–4 relevant project roles.

### ARENA
Use for:
- durable Autopilot architecture;
- execution authority;
- remote trust;
- destructive flows;
- checkpoint/recovery semantics;
- model/provider authority/fallback;
- Memory truth model;
- cross-platform protocol;
- major visual identity replacement.

Requires:
- independent initial positions where material;
- evidence matrix;
- strongest dissent;
- premortem;
- explicit Owner decision when authority/residual risk requires it.

## Project-specific blockers

A role may block only within its domain and only with evidence/reasoning.

Blockers:
- TRUTH_BLOCKER
- SECURITY_BLOCKER
- AUTHORITY_BLOCKER
- DURABILITY_BLOCKER
- ACCESSIBILITY_BLOCKER
- ARCHITECTURE_BOUNDARY_BLOCKER
- CROSS_PLATFORM_TRUTH_BLOCKER

Visual preference alone is not a blocker.

## Owner gates

Owner approval remains required for:
- changing the locked art direction;
- authority expansion;
- destructive/irreversible behavior;
- public publishing/deploy effects;
- credentials/spend/subscription;
- material privacy tradeoff;
- changing no-silent-fallback policy;
- replacing the project-local Council/Studio governance itself.

## Output contract

Material reviews produce:
- decision question;
- activated roles;
- independent positions when required;
- evidence;
- strongest dissent;
- blockers;
- alternatives;
- recommendation;
- confidence/unknowns;
- Owner action if required;
- expiry/reopen trigger.

## Relationship to parent Council

The Project Council does not replace the Universal Council.

Escalate to the parent Council when:
- the issue materially exceeds this project's domain;
- commercialization requires full commercial challenge;
- governance design itself is being changed;
- a cross-project policy is proposed.

