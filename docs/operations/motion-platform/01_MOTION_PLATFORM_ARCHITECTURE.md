# Motion Platform / MotionKit — Architecture

Date: 2026-10-23
Status: FOUNDATION_DRAFT
Architecture version: 0.1

## 1. Core principle

The renderer is replaceable. The semantic meaning is not.

A product must be able to express:

- ROLE_ACTIVATED
- ROUTE_TRANSFER
- WAITING_OWNER
- BLOCKED
- VERIFIED_COMPLETE
- EXPAND
- COLLAPSE
- SELECT
- INSPECT
- HANDOFF
- RETURN
- RECOVERY_FOCUS
- FORK

without knowing whether the result is implemented by WPF/Composition, Rive, Lottie, Skia, Compose or a future renderer.

## 2. Layer model

### Layer A — Semantic Motion Contract

Defines:
- semantic event;
- source state;
- destination state;
- eligible object;
- purpose: NAVIGATION / STATE / FEEDBACK / ROUTING / HANDOFF / RECOVERY;
- allowed start condition;
- allowed completion condition;
- cancel condition;
- Reduced Motion equivalent;
- truth requirements.

This layer has no UI framework dependency.

### Layer B — Motion Orchestrator

Responsibilities:
- validate event/state compatibility;
- resolve semantic contract;
- enforce re-entry and duplicate-trigger policy;
- schedule start/stop;
- cancel superseded motion;
- settle to deterministic final state;
- prevent stale completion callbacks from mutating current visual state;
- emit observability events.

The orchestrator does not decide product truth.

### Layer C — Choreography + Tokens

Defines reusable parameters:
- duration classes;
- easing/spring families;
- travel constraints;
- emphasis level;
- stagger rules;
- quiet-at-rest policy;
- motion density;
- interruption behavior.

Tokens are referenced by semantic name, not hard-coded in product screens.

### Layer D — Product Motion Profile

Each product may define its own personality while preserving semantics.

Examples:
- Command Center: restrained semantic routes, sigils, evidence objects.
- RevenueSystem: faster financial feedback, minimal travel, stronger confirmation.
- Future media tool: richer vector/character behavior.

The profile may change visual expression but must not change truth meaning.

### Layer E — Renderer Adapter

Candidate adapters:
- Native Windows / Composition;
- Rive;
- Lottie;
- SkiaSharp;
- Android Compose;
- future renderers.

Adapter contract:
- capabilities;
- begin;
- update semantic inputs;
- cancel;
- settle;
- Reduced Motion mode;
- diagnostics;
- disposal.

No adapter may silently fabricate unsupported behavior. Unsupported capability returns explicit NOT_SUPPORTED and the orchestrator chooses an authorized fallback.

### Layer F — Evidence + QA

Captures:
- semantic event ID;
- state source;
- adapter used;
- start/stop timestamps;
- interruption reason;
- settled state;
- frame/performance telemetry where available;
- Reduced Motion equivalence;
- exact build/commit identity for acceptance evidence.

## 3. Motion instance identity

Every non-trivial motion receives an instance ID.

A completion callback must prove it still owns the target before applying a final visual state.

This prevents:
- stale animation completion;
- rapid-click race conditions;
- old route animations overwriting a newer state;
- double-trigger completion.

## 4. Interruption model

Every contract declares one:

- REPLACE: newer semantic event supersedes current.
- QUEUE: ordered visual sequence is required.
- COALESCE: repeated same event collapses to one.
- IGNORE_DUPLICATE: duplicate while active is discarded.
- PARALLEL_SAFE: independent targets may run simultaneously.

Default is REPLACE for direct interaction and state visualization.

## 5. Truth boundary

Truth source must always be outside MotionKit.

Example:

Bad:
spinner starts -> product infers WORKING.

Good:
product state becomes WORKING -> MotionKit may display restrained current.

If state becomes UNKNOWN, forward-progress motion stops.

## 6. Reduced Motion

Reduced Motion is a semantic adapter mode, not a global "duration = 0" hack.

It removes:
- long travel;
- springs;
- pulses;
- route drawing;
- flourish.

It preserves:
- source focus;
- destination focus;
- state label/icon;
- direct fade or instant settle;
- before/after clarity.

## 7. Renderer selection policy

Initial hypothesis, subject to lab evidence:

- Native Windows / Composition: micro-interactions, focus, selection, simple routes.
- Rive: stateful interactive vector scenes, sigils, characters, complex reusable objects.
- Lottie: pre-authored finite sequences exported from motion-design tools.
- SkiaSharp: custom dynamic diagrams/routes/data-driven 2D scenes.
- Compose: Android-native micro/state motion and platform-specific interaction.

This is not an adoption decision.

## 8. Dependency rule

Third-party packages stay behind adapters.

Product screens depend on semantic contracts, not concrete renderer packages.

This makes it possible to:
- replace an engine;
- disable a renderer on weak hardware;
- test semantics without graphics;
- preserve product code when library versions change.

## 9. Failure model

Renderer failure must be explicit.

Allowed:
- settle to truthful static state;
- choose an authorized fallback adapter;
- record diagnostics.

Forbidden:
- fake success;
- endless loading animation;
- silently switch to a visually different semantic outcome;
- drop required accessibility state.

## 10. Performance law

Motion is not approved because it "looks smooth on one machine".

The platform must budget:
- setup latency;
- frame time;
- allocations;
- retained memory;
- CPU/GPU use where measurable;
- repeated-play leakage;
- asset load cost.

No permanent high-frequency animation is allowed without an explicit semantic need and performance evidence.
