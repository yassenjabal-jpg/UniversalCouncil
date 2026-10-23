# Motion Platform MP4 — Command Center Reference Integration

Date: 2026-10-23
Status: REFERENCE_RUNTIME_EVIDENCE_COMPLETE_OWNER_VISUAL_REVIEW_PENDING
Parent MP3 exact head: `602639dbc10a25824aa0b1f131fd6fc184771ac0`
Parent gate: `RENDERER_ROLE_MATRIX_ACCEPTED = true`

## Restack record

- accepted MP3 parent: `602639dbc10a25824aa0b1f131fd6fc184771ac0`;
- previous MP4 head preserved at `motion-platform/mp4-reference-integration-pre-rebase-20261023` / `0813a617f3ad1db0c67387c196fc965d44f8ce41`;
- restack is history-reversible and did not merge PR #83 or #84.

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

## Reference runtime evidence

Focused MP4 evidence was captured on YASSIN from source SHA `c13fa2ad069075e21f35b3970b388b5922826ee8`.

Evidence directory: `lab/motion-platform/evidence/yassin-20261023-mp4`.

Full and Reduced recordings execute the exact same seven semantic steps at the same frame numbers:
- ROLE_ACTIVATION opens the same role context;
- ARTIFACT_HANDOFF opens the same handoff context;
- Full preserves route/handoff travel;
- Reduced preserves semantic state changes while removing the longer travel sequence.

Focused capture results:
- Full: 360 frames / 12 s, 32 visibly changed frames, longest changed run 9, motion runs 9;
- Reduced: 360 frames / 12 s, 11 visibly changed frames, longest changed run 3, motion runs 7.

Owner-review artifacts:
- `mp4-reference-full-motion.mp4`;
- `mp4-reference-reduced-motion.mp4`;
- `mp4-owner-review-contact-sheet.png`;
- selected ROLE_ACTIVATION / ARTIFACT_HANDOFF PNG frames;
- Full/Reduced evidence manifests and SHA-256 summary.

An exploratory persistent WGC run was rejected because it delivered only one fresh source frame and zero visible changes. The WGC path was hardened fail-closed so stale one-frame capture can no longer report PASS.

Owner visual acceptance remains pending. This evidence does not authorize production renderer adoption, Stage 8, or PR merge.

## Acceptance before any merge

1. exact-head Command Center build succeeds on Windows;
2. Motion Platform + Stage0 + CodeQL remain green;
3. existing Motion Platform MP0-MP3 validators remain green;
4. no SkiaSharp.Views.WPF dependency enters the product;
5. source audit confirms the two manual WPF route/handoff animations are replaced rather than duplicated;
6. owner reviews the committed Full/Reduced reference-Windows package and explicitly approves visual acceptance.

This branch is an integration candidate only, not production adoption.
