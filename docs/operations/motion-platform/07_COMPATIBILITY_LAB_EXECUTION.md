# Motion Platform MP3 — Compatibility Lab Execution

Date: 2026-10-23
Status: IMPLEMENTATION_CANDIDATE
Parent: MP2 exact head `8b9e3a20ca407fff6734c945db59708d2718c2b5`

## Purpose

MP3 tests real renderer candidates behind the MP2 adapter boundary.

This phase evaluates renderer roles. It does not select a universal winner and does not authorize production adoption.

## Current public-source evidence reviewed

### SkiaSharp
Repository: mono/SkiaSharp
Current latest GitHub release reviewed: v4.153.1 (2026-09-30)
License: MIT
Repository states direct support for:
- .NET 6+;
- Windows Classic Desktop / WPF;
- Android;
- WinUI 3;
- cross-platform 2D rendering.

MP3 role hypothesis:
- DYNAMIC_DRAWING;
- PATH_GEOMETRY;
- route/diagram rendering;
- data-driven 2D scenes.

Empirical probes authorized now:
- Linux headless offscreen rendering;
- Windows WPF core-bridge compile probe.

Observed compile evidence:
- direct `SkiaSharp.Views.WPF 4.153.1` on `net10.0-windows` emitted NU1701 because its OpenTK/OpenTK.GLWpfControl dependency path restored through .NET Framework compatibility;
- this warning is treated as a real compatibility risk and is NOT suppressed;
- the lab therefore tests a direct bridge from core `SkiaSharp` pixels into WPF `BitmapSource` instead of treating the Views.WPF package as production-ready.

Status: LAB_ONLY.

### Windows Composition / Windows App SDK
Repository: microsoft/WindowsAppSDK + WindowsAppSDK-Samples
Current stable release reviewed: 2.5.1 (2026-09-16)
License: MIT repository.
Official samples include Windows Composition / Input / SceneGraph.

MP3 role hypothesis:
- Windows-native micro motion;
- focus/selection;
- low-overhead visual property animation;
- composition-backed route/object motion.

Empirical probe:
- Windows compile probe first;
- actual WPF interop/runtime probe later on Windows evidence environment.

Status: LAB_ONLY.

### Rive
Repository: rive-app/rive-runtime
License: MIT
Current repository README states:
- C++17 runtime;
- advances animations and state machines;
- abstract Renderer interface;
- GPU backends include D3D11, D3D12, Metal, Vulkan and OpenGL/WebGL;
- Windows build requires a C++ toolchain;
- official higher-level runtimes wrap the C++ library.

Important:
Rive is NOT treated as a .NET/WPF drop-in dependency.

MP3 role hypothesis:
- STATEFUL_VECTOR;
- interactive sigils/characters;
- complex vector state machines.

Empirical probe sequence:
1. native Windows toolchain/build feasibility;
2. interop boundary prototype;
3. only then WPF host integration.

Status: NATIVE_INTEROP_RESEARCH.

### Lottie-Windows
Repository: CommunityToolkit/Lottie-Windows
Current latest GitHub release reviewed: v8.1.240821.1 (2024-08-27)
Repository current activity observed in 2026.
README explicitly targets WinUI 3 / UWP integration and uses Windows Composition.

MP3 role hypothesis:
- PREAUTHORED_TIMELINE;
- After Effects -> code/product handoff.

Important:
Lottie-Windows is NOT treated as a direct WPF control.

Empirical probe sequence:
1. codegen/package compatibility;
2. Windows/WinUI isolated host;
3. only if justified, WPF island/interop study.

Status: WINUI_SPECIALIST_RESEARCH.

## Scenario contract

The lab retains the five mandatory scenarios:

S1 INTERACTIVE_ICON
S2 STATEFUL_SIGIL
S3 ROUTE_TRANSFER
S4 SEMANTIC_OBJECT_HANDOFF
S5 DENSE_SCREEN_STRESS

Candidates are not required to implement scenarios outside their declared role.

A candidate is scored only where its declared capabilities match the scenario.

## Evidence classes

SOURCE_EVIDENCE:
- repository metadata;
- README/docs;
- release/license information.

COMPILE_EVIDENCE:
- exact package/version restores and builds in our lab.

RUNTIME_EVIDENCE:
- adapter executes;
- produces deterministic renderer output;
- obeys lifecycle/capability contract.

WINDOW_EVIDENCE:
- actual Windows window/interactivity/performance evidence.

OWNER_VISUAL_EVIDENCE:
- owner-visible Full/Reduced Motion output.

A lower evidence class must never be described as a higher one.

## Performance policy

MP3 CI records timing/allocation observations but does not gate on wall-clock thresholds.

Reason:
shared CI runners are not stable performance reference hardware.

Performance gates are introduced only after:
- a reference Windows hardware class is selected;
- measurement procedure is repeatable;
- warmup/sample policy is fixed.

Correctness gates apply immediately.

## Skia headless probe

The first real adapter is an isolated Skia offscreen lab adapter.

It:
- references SkiaSharp only in a LAB project;
- implements the MP2 adapter contract;
- renders an offscreen deterministic frame;
- exposes a SHA-256 frame hash for lab assertions;
- does not modify Command Center;
- does not become a production package.

Expected capability claim:
STATIC_SETTLE | OPACITY | TRANSLATION | SCALE | ROTATION | PATH_GEOMETRY | DYNAMIC_DRAWING | COLOR_BINDING

Explicitly NOT claimed:
STATEFUL_VECTOR | PREAUTHORED_TIMELINE | HIT_TESTING

## Windows WPF core-bridge compile probe

A separate Windows-only project references core SkiaSharp 4.153.1 and compiles a direct `SKBitmap -> BitmapSource` bridge under `net10.0-windows`.

This probe exists because the direct SkiaSharp.Views.WPF package path produced unsuppressed NU1701 compatibility warnings under .NET 10.

Passing the core-bridge probe proves managed API/package compile compatibility only.
It does NOT prove:
- runtime frame pacing;
- WPF visual-host correctness;
- actual animation quality;
- accessibility;
- production readiness.

## Stop conditions

MP3 stops a candidate immediately if:
- package/license metadata cannot be pinned;
- adapter boundary must be bypassed;
- product truth must enter renderer;
- Reduced Motion cannot be represented;
- candidate requires product-wide framework migration;
- actual evidence contradicts claimed role.

## Authority

MP3 does not authorize:
- production renderer adoption;
- WPF product integration;
- PR72 merge;
- Stage 8;
- runtime authority expansion.
