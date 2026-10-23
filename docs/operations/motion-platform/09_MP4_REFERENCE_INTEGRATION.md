# Motion Platform MP4 — Command Center Reference Integration

Date: 2026-10-23
Status: REFERENCE_INTEGRATION_CANDIDATE
Parent MP3 exact head: `602639dbc10a25824aa0b1f131fd6fc184771ac0`
Parent gate: `RENDERER_ROLE_MATRIX_ACCEPTED = true`

## Goal

Prove that the Open-Source-First strategy reduces bespoke in-screen motion code in the actual Command Center.

MP4 does not expand MotionKit Core or Runtime.

Implementation boundary: **SkiaSharp inside Command Center only**.

## First integration slice

Target 1: ROLE_ACTIVATION route cue.

Existing implementation:
- constructs a WPF Line;
- animates X2/Y2 with DoubleAnimation;
- uses a hard-coded semantic origin per screen.

MP4 candidate:
- preserve the existing origin/destination and click semantics;
- replace line drawing/reveal with SkiaSharp 4.153.1;
- use Skia's path/dash/trim APIs;
- use WPF CompositionTarget.Rendering only as the host frame callback;
- preserve current accent and duration.

Target 2: ARTIFACT_HANDOFF cue.

Existing implementation:
- constructs a WPF Line;
- constructs a temporary Border artifact;
- animates TranslateTransform.X with DoubleAnimation.

MP4 candidate:
- render the route and moving artifact in a single Skia-backed overlay frame;
- preserve current source/destination, accent and duration;
- keep the cue local/fixture-truthful until real handoff events are connected.

## Why this slice

These are in-screen object/route motions, matching the owner clarification.

They are preferred over screen transitions because:
- they directly represent roles/handoffs;
- they are currently bespoke WPF animation code;
- Skia already proved path/dynamic 2D capability in MP3;
- the change is adapter-local and reversible.

## Architecture Boundary Audit

Boundary: WPF view code emits only visual cue parameters into an adapter-local renderer. No product/business/data truth is moved into the renderer.

Evidence:
- no AppDbContext or persistence access is added;
- no business rule is added to MainWindow;
- SkiaMotionCueAnimator is stateless and owns only transient visual resources;
- WPF retains input, navigation and semantic ownership;
- shared MotionKit Core/Runtime remain untouched.

Risk: MainWindow still initiates the cue directly, which is accepted for this bounded reference slice but is not a new business-layer dependency.

Smallest safe extraction: keep SkiaMotionCueAnimator adapter-local now; if later event-backed motion expands, move cue invocation behind the existing coordinator/event surface rather than adding renderer state to the view.

Affected verification: MP4 source validator, Motion Platform tests, exact-head Windows Command Center build, and later YASSIN Full/Reduced visual evidence.

Migration path: reference slice first; reusable cross-project API only after MP4 evidence demonstrates a recurring boundary.

## Explicit non-goals

This slice does NOT:
- replace ScreenTransitionMotion;
- introduce a custom animation engine;
- add a shared MotionKit abstraction;
- change product truth;
- fabricate live council activity;
- introduce a Rive .NET wrapper;
- use SkiaSharp.Views.WPF;
- adopt SkiaSharp as the universal renderer;
- authorize PR72 merge;
- open Stage 8.

## Integration rule

The Command Center references core `SkiaSharp 4.153.1` directly.

It does not reference `SkiaSharp.Views.WPF` because MP3 recorded its net10 NU1701 dependency path as blocked.

The adapter-local implementation uses:
- SKPathBuilder;
- SKPathEffect.CreateDash;
- SKPathEffect.CreateTrim;
- BitmapSource bridge;
- CompositionTarget.Rendering.

No MotionKit shared layer is modified.

## Reduced Motion

The existing MotionEnabled gate is preserved.

When Windows/user Reduced Motion disables the cue:
- route travel is not started;
- semantic click behavior and inspector/drawer behavior remain available.

## Acceptance before any merge

1. exact-head Command Center build succeeds on Windows;
2. Motion Platform + Stage0 + CodeQL remain green;
3. existing Motion Platform MP0-MP3 validators remain green;
4. no SkiaSharp.Views.WPF dependency enters the product;
5. source audit confirms the two manual WPF route/handoff animations are replaced rather than duplicated;
6. actual owner-visible/reference-Windows evidence is still required before visual acceptance.

This branch is an integration candidate only, not production adoption.
