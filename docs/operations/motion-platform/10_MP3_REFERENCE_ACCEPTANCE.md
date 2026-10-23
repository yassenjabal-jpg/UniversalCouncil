# Motion Platform MP3 — Reference Acceptance

Date: 2026-10-23
Host: YASSIN
Status: REFERENCE_ACCEPTED_OWNER_APPROVED

## Scope

This document records the MP3 reference-Windows acceptance run for the renderer roles that are actually assigned by the role matrix. It does not create a universal renderer, does not authorize production adoption, and does not change Stage8 or runtime authority.

The executable reference probe is apps/UniversalCouncil.MotionKit.SkiaWpfAcceptanceProbe.

Renderer boundary:
- SkiaSharp 4.153.1 owns drawing only.
- WPF owns keyboard focus, button semantics and UI Automation.
- product truth does not enter the renderer.
- Full and Reduced Motion reach the same semantic final states.
- SkiaSharp.Views.WPF remains blocked by its previously recorded NU1701 path.

## Scenario disposition

| Scenario | Result | Evidence |
| --- | --- | --- |
| S1 Interactive Icon | PASS Full + Reduced | keyboard focus, Space/Enter activation, selected/deselected, accessible name and Invoke pattern |
| S2 Stateful Sigil | NOT_APPLICABLE_CURRENT_ACCEPTED_ROLE_SET | no accepted renderer role currently claims STATEFUL_VECTOR; Rive remains compile-evidence research only |
| S3 Route Transfer | PASS Full + Reduced | RETURN is issued mid-transfer; the same artifact identity settles at SOURCE |
| S4 Semantic Object Handoff | PASS Full + Reduced | destination becomes unavailable; artifact deterministically falls back to SOURCE |
| S5 Dense Screen Stress | PASS Full + Reduced | Full: 64 independent visual objects / 240 frames; Reduced: static equivalent |

No UNKNOWN state is promoted to forward progress. If a future MP4 use case assigns STATEFUL_VECTOR responsibility, S2 becomes mandatory before that renderer role can be accepted.

## Reference performance observations

The Full S5 run recorded:
- 64 independent objects over 240 frames.
- WPF presentation-loop interval median: 3.2258 ms.
- p95: 7.0367 ms.
- p99: 32.8537 ms.
- 2 frame intervals above 33.333 ms.
- normalized process CPU observation: 12.4904%.
- managed allocated-byte delta: 3,201,208 bytes.
- working-set delta: 4,157,440 bytes.
- DispatcherPriority.Input latency median: 0.0336 ms; p95: 2.0019 ms.
- actual keyboard activation during the dense run: 3 interactions; median 10.2973 ms; p95 15.4295 ms.
- Reduced S5 also performed 1 actual keyboard interaction before static settle.

These are reference-host observations, not GPU presentation telemetry. No performance threshold was created after observing the data, so the numbers are non-gating. Correctness and deterministic final state remain gating.

## Accessibility and lifecycle

S1 exposes a native WPF Button surface with an accessible name and Invoke pattern. Space and Enter both activate the same semantic toggle path in Full and Reduced Motion.

The WPF MouseEnter/MouseLeave hover-state handler is exercised through the same state function used by the real pointer path. Hardware-pointer injection is explicitly NOT claimed in this run because Nioh 3 on the reference host continuously reclaimed the OS cursor/foreground. This limitation is recorded in the structured evidence rather than hidden.

During S5 Full, three actual keyboard activations are injected while 64 independent objects are updating; Reduced S5 performs one actual keyboard activation before static settle.

The Full renderer is disposed, garbage collection/finalization is forced, and a new renderer instance is created before the Reduced suite. A lifecycle race discovered during this work (pointer event arriving in the dispose/re-entry gap) was fixed by making the interactive redraw path no-op while the renderer slot is null. Re-entry count is recorded as one and the process exits normally with code 0.

## Evidence

Evidence directory: lab/motion-platform/evidence/yassin-20261023-acceptance/.

It contains the structured JSON run record, stdout/stderr/exit-code evidence and Full/Reduced PNG captures for S1, S3, S4 and S5. manifest.json binds the probe source and evidence bytes by SHA-256.

## Gate

Technical bake-off for currently assigned roles: PASS.

Formal MP3 gate RENDERER_ROLE_MATRIX_ACCEPTED: PASSED.

Owner visual acceptance was explicitly granted on 2026-10-23 after review of the MP3 visual package. The approval is recorded in `11_MP3_OWNER_VISUAL_REVIEW.md`. This does not promote any renderer to production adoption.

## MP4 transition

The concrete next integration already exists as a bounded stacked candidate on motion-platform/mp4-reference-integration-20261023 / PR #84: the Command Center's real ROLE_ACTIVATION route cue and ARTIFACT_HANDOFF cue are routed through an adapter-local Skia renderer while keeping existing semantic bindings and static fallback.

MP4 must still produce exact-head owner-visible Full/Reduced evidence before COMMAND_CENTER_MOTION_REFERENCE_ACCEPTED can pass.
