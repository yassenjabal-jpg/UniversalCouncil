# MP3 — YASSIN reference evidence and MP4 handoff

Date: 2026-10-23. Status: FEASIBILITY_EVIDENCE_COMPLETE_ACCEPTANCE_PENDING.

## Scope and source binding

Work started from PR #83 head f7e2db143898e4f1d1a43e8d43dc875632c2ed0a in a clean worktree on motion-platform/compatibility-lab-20261023.
PR #72/#80/#81/#82/#83 were verified Draft, open and unmerged. No merge was performed.
MP1/MP2 source, Command Center product source, unrelated S4d work and Stage8 authority are unchanged.

Evidence is in lab/motion-platform/evidence/yassin-20261023.
The manifest binds source bytes and captured artifacts by SHA-256, avoiding a circular self-commit claim.
The probe was run from these source bytes; CI builds the interactive executable but does not claim to reproduce the desktop capture.

Reference host: YASSIN, interactive session 5, Windows 11 Pro 10.0.26200,
Intel Core i5-12400F, NVIDIA GeForce RTX 4060 Ti, driver 32.0.16.1088,
.NET SDK 10.0.402. Measurements are informational and apply only to these fixtures.

## Results and limits

| Candidate | Observed result | Limit |
| --- | --- | --- |
| Windows App SDK 2.5.1 Composition | Original API probe exits 0. A real WPF HWND hosts ContentIsland through DesktopChildSiteBridge. Thirty Full captures contain 25 distinct sprite colors; ten Reduced captures have one stable color. Normal process exit 0. | Window feasibility, not S1..S5, GPU pacing or product acceptance. |
| SkiaSharp 4.153.1 | Actual WPF window, 600 SKBitmap-to-BitmapSource updates, 64x64 pixel fixture, normal exit 0. Dispatcher median 28.96 ms, p95 34.91 ms. Offscreen adapter correctness passes; 100 frames observed at 42.98 ms. | Static bridge fixture, not animated product routes. Dispatcher cadence is not GPU FPS. |
| LottieGen 8.2.250604 | Baseline exact-head Windows CI strict/TestMode two-pass deterministic codegen verified. | Tool execution, not WPF playback. |
| Rive f4da8fa42ed2c256d3d672e3828d18a328528f50 | Baseline exact-head Windows CI official build wrapper generated rive.sln. | Build generation, not native compilation, rendering or .NET interop. |

Referenced baseline CI: https://github.com/yassenjabal-jpg/UniversalCouncil/actions/runs/39929833512
Windows job: 120335079367. LottieGen and Rive steps were independently checked as successful.
New-head CI must still pass after this change; old CI is not presented as validation of new source.

The first interactive host displayed correctly but attempted to access root.Children after the ContentIsland had closed its visual resources. That lab-only cleanup access was removed. The final captured run completed without stderr and exited 0.
The historical headless shutdown timeout remains preserved as evidence; it is superseded only as a reason to defer interactive Windows testing.

## Reproduce

Run from the repository root on an unlocked interactive Windows desktop:

```powershell
dotnet run --project apps/UniversalCouncil.MotionKit.CompositionRuntimeProbe -c Release
dotnet run --project apps/UniversalCouncil.MotionKit.CompositionRuntimeProbe -c Release -- --interactive build/mp3-reference
dotnet run --project apps/UniversalCouncil.MotionKit.SkiaWpfCompileProbe -c Release -- build/mp3-reference
dotnet run --project apps/UniversalCouncil.MotionKit.SkiaLabValidation -c Release
```

The saved capture-reference.ps1 records the Composition fixture and checks bounded process exit.
It uses the observed 1920x1080 desktop crop x=648,y=328,w=624,h=400; reposition/recalculate this crop on a different display before recording. Keep the probe unobscured. Captures contain only its client surface.
Source and screenshot hashes are validated by the MP3 validator. Captured JSON alone is not evidence of successful process shutdown; retained stdout/stderr and the verified runner exit are required.

Hosting uses existing platform APIs documented in:
- https://learn.microsoft.com/windows/windows-app-sdk/api/winrt/microsoft.ui.content.desktopchildsitebridge
- https://learn.microsoft.com/windows/windows-app-sdk/api/winrt/microsoft.ui.content.contentisland

## Governance and acceptance boundary

Open-Source First / Integration over Invention remains governing.
No new shared engine, timeline, state machine, dispatcher abstraction or native wrapper was added.
MP1 and MP2 remain frozen for expansion. Both probes remain LAB_ONLY; no production adapter or automatic fallback is selected.

This closes the outstanding reference-Windows feasibility investigation.
It does NOT declare RENDERER_ROLE_MATRIX_ACCEPTED: the existing mandatory S1..S5 scenario bake-off, keyboard/accessibility checks, dense-screen CPU/allocation/GPU measurements and owner visual acceptance are still unpassed.
No threshold was lowered and no UNKNOWN was promoted to SUCCESS.

## MP4 preparation — concrete next slice

1. Inventory the existing Command Center icons, roles, routes and handoff visuals against their real state/event bindings. Preserve screen identity and Stage8 authority.
2. First bounded adapter proposal: Composition property motion for an existing state-backed icon, or Skia route drawing where geometry is data-driven. Choose one actual screen and one semantic event; retain the existing static fallback until runtime parity is proven.
3. Keep renderer objects and authored asset details inside the adapter. Reuse the existing MP2 request/lease/profile boundary; do not grow MP1/MP2 without an integration failure demonstrating a missing contract.
4. Exercise S1 (keyboard/pointer icon), S3 (RETURN during route), S4 (unavailable destination) and S5 (dense screen) for relevant roles; S2 only if stateful vector is claimed. Preserve stale completion rejection and exact final state.
5. Capture exact-source Full and Reduced in-screen video, interruption/re-entry, resize/DPI and disposal evidence before proposing production adoption. No scripted perpetual activity in product screens.
6. Lottie stays an authored-codegen specialist until a host is proven. Rive interop is deferred until a concrete stateful-vector asset justifies native complexity.

MP4 preparation is ready; this document grants no product integration, merge or runtime authority.

## Technical acceptance continuation

The earlier feasibility evidence above remains historical and valid for its original claims. It is now superseded only for the statement that S1..S5 technical bake-off was still wholly unexecuted.

The follow-on reference probe is recorded under lab/motion-platform/evidence/yassin-20261023-acceptance/ and is defined by 10_MP3_REFERENCE_ACCEPTANCE.md.

Technical disposition:
- S1: PASS Full + Reduced for hover-state handler, focus, keyboard press, selected/deselected and accessibility; hardware-pointer injection is explicitly not claimed because the active game reclaims the OS cursor.
- S2: NOT_APPLICABLE_CURRENT_ACCEPTED_ROLE_SET; no accepted role is assigned STATEFUL_VECTOR.
- S3: PASS Full + Reduced, including RETURN during transfer.
- S4: PASS Full + Reduced, including destination-unavailable fallback.
- S5: PASS Full + Reduced, with reference-host CPU/allocation/memory/input/presentation-loop observations.
- renderer disposal/re-entry: PASS.
- formal gate: still NOT PASSED because owner visual acceptance is not yet recorded.

The original headless Composition shutdown timeout remains historical evidence. Nothing in this continuation claims it was reproduced or repaired on headless CI.
