# Motion Platform — Open-Source First Implementation Policy

Date: 2026-10-23
Status: GOVERNING_FOR_MP3_AND_LATER
Owner direction: APPROVED

## Decision

Motion Platform is an integration platform, not a new animation engine.

Default rule:

> Open Source / existing platform capability first. Custom MotionKit code only fills a verified gap that cannot be solved safely by an adopted dependency or platform API.

## Frozen internal layers

MP1 Semantic Kernel and MP2 Renderer Boundary are now FROZEN_FOR_EXPANSION.

They may receive:
- bug fixes;
- security fixes;
- correctness fixes;
- adapter-boundary corrections required by a real integration;
- evidence/diagnostic fields required to verify a real integration.

They may NOT receive:
- new rendering algorithms;
- custom vector engines;
- custom timeline engines;
- custom animation authoring systems;
- custom GPU/rendering stacks;
- speculative abstractions without a failing real integration proving the need.

## Integration-over-invention rule

Before adding reusable MotionKit code, the change must answer:

1. Which real renderer/integration exposed the gap?
2. Why can the existing dependency/platform API not solve it?
3. Why can an adapter-local solution not solve it?
4. What is the smallest shared code required?
5. How is renderer replaceability preserved?

If those questions are not answered, the shared-platform change is rejected.

## Preferred responsibility split

MotionKit owns:
- semantic truth boundary;
- lifecycle/cancellation coordination;
- Reduced Motion semantics;
- product Motion Profiles;
- renderer adapter contract;
- evidence/diagnostics;
- renderer selection policy after empirical proof.

Open-source/platform renderers own:
- vector rendering;
- path rasterization;
- animation timelines;
- stateful vector playback;
- GPU composition;
- asset decoding;
- renderer-specific performance work.

## Current renderer strategy

- SkiaSharp: dynamic/path/data-driven 2D.
- Windows Composition: Windows-native micro/property motion where runtime evidence supports it.
- Lottie/LottieGen: pre-authored finite motion / After Effects handoff.
- Rive: stateful/interactable vector motion if native Windows interop proves viable.

No candidate is production-adopted by this policy.

## Stop rule

If MotionKit starts duplicating a capability already present in a maintained dependency, stop and move the implementation behind that dependency's adapter unless a documented safety, licensing, portability, or product-truth reason prevents it.

## MP4 consequence

MP4 must prefer visible integration of proven external renderers over further platform abstraction.

The success criterion shifts from "more framework" to:
- less bespoke animation code;
- more reusable authored assets;
- measurable renderer evidence;
- visible in-screen motion in the reference application;
- preserved truth/accessibility semantics.
