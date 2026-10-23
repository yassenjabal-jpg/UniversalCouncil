# Motion Platform MP3 — Renderer Role Matrix

Date: 2026-10-23  
Status: EVIDENCE MATRIX — NOT AN ADOPTION DECISION

## Decision principle

MP3 does not search for one universal animation engine.

Each renderer is evaluated only for the motion families it can execute truthfully, accessibly, and maintainably behind the MotionKit adapter boundary.

## Current matrix

| Candidate | Highest evidence | Current role | WPF path | Current verdict |
| --- | --- | --- | --- | --- |
| SkiaSharp 4.153.1 | RUNTIME_EVIDENCE | dynamic drawing, paths, diagrams, data-driven 2D | owned core Skia -> BitmapSource bridge | VALIDATED_SPECIALIST_CANDIDATE |
| Windows Composition / WASDK 2.5.1 | COMPILE_EVIDENCE | Windows-native property/micro motion | WPF + unpackaged Windows App SDK; runtime host still unproven | COMPILE_FEASIBLE_RUNTIME_PENDING |
| Rive runtime @ f4da8fa42ed2c256d3d672e3828d18a328528f50 | SOURCE_EVIDENCE | stateful/interactable vector scenes | native C++ interop required | SOURCE_VALIDATED_NATIVE_INTEROP_RESEARCH |
| Lottie-Windows / LottieGen | SOURCE_EVIDENCE | pre-authored timelines and AE/codegen handoff | WinUI/generated Composition interop research | SOURCE_VALIDATED_WINUI_CODEGEN_SPECIALIST |

## SkiaSharp

Validated:
- actual offscreen rendering through the MotionKit adapter;
- deterministic output hashes;
- Full/Reduced profile distinction;
- lifecycle and unsupported-capability behavior;
- .NET 10 WPF compile with an owned core-Skia pixel bridge.

Blocked path:
- direct `SkiaSharp.Views.WPF 4.153.1` is not accepted for .NET 10 because the probe produced NU1701 through legacy-compatible OpenTK dependency restoration.

What is still missing:
- actual WPF window rendering;
- frame pacing and memory on reference Windows hardware;
- owner-visible fidelity;
- accessibility interaction.

## Windows Composition

Validated:
- `Microsoft.WindowsAppSDK 2.5.1` restores in the WPF probe;
- WPF and `Microsoft.UI.Composition` coexist at compile time;
- `Compositor`, `SpriteVisual`, and scalar keyframe animation APIs compile.

What is still missing:
- creating/owning a compositor in the actual WPF runtime;
- attaching a Composition visual tree to the WPF HWND/surface;
- cancellation/lifetime evidence under window close/recreate;
- frame pacing and GPU cost.

Therefore Composition is a strong Windows-native candidate, but compile evidence is not runtime evidence.

## Rive

Pinned source:
`f4da8fa42ed2c256d3d672e3828d18a328528f50`

Source evidence confirms:
- MIT license;
- native C++ runtime;
- animation/state-machine advancement;
- abstract renderer boundary;
- D3D11/D3D12 Windows backends;
- documented Windows native build path.

There is still no MotionKit .NET/WPF interop evidence. Rive remains native-interoperability research.

## Lottie-Windows / LottieGen

Pinned source:
`dce2d4ac945b7d8d400c19bca440907315901b5f`

Source evidence confirms:
- MIT license;
- latest reviewed release `v8.1.240821.1`;
- WinUI/UWP-oriented Windows rendering;
- LottieGen .NET global tool capable of generating C#/C++ and other output from Lottie/Bodymovin JSON.

This makes Lottie primarily an authored-animation/codegen candidate. It is not considered a direct WPF control.

## Next evidence order

1. Windows Composition WPF runtime host probe.
2. LottieGen tool execution/code generation probe.
3. Rive exact-commit Windows native build feasibility.
4. Reference-Windows performance methodology and measurements.

None of these probes authorize production adoption or Command Center integration.
