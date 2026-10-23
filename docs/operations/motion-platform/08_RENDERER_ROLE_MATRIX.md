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
| Windows Composition / WASDK 2.5.1 | COMPILE_EVIDENCE | Windows-native property/micro motion | WPF + unpackaged Windows App SDK; headless runtime deferred to interactive Windows | COMPILE_PROVEN_RUNTIME_DEFERRED_INTERACTIVE_WINDOWS |
| Rive runtime @ f4da8fa42ed2c256d3d672e3828d18a328528f50 | COMPILE_EVIDENCE | stateful/interactable vector scenes | official Windows build generation proven; native C++ interop still required | COMPILE_FEASIBLE_NATIVE_INTEROP_SPECIALIST |
| Lottie-Windows / LottieGen | RUNTIME_EVIDENCE (tooling) | pre-authored timelines and AE/codegen handoff | deterministic LottieGen C# codegen proven; renderer host still pending | TOOLING_RUNTIME_VALIDATED_WINUI_CODEGEN_SPECIALIST |

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

Observed:
- compile/API coexistence is proven;
- two bounded headless runtime attempts exceeded the shutdown budget even after explicit queue ownership/event-loop work;
- no MotionKit-specific workaround will be invented for headless CI.

What is still missing:
- interactive/reference-Windows runtime hosting;
- attachment of the Composition visual tree to the WPF HWND/surface;
- cancellation/lifetime evidence under real window close/recreate;
- frame pacing and GPU cost.

Therefore Composition remains a Windows-native candidate, but its runtime path is deferred rather than allowed to block MP3.

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

Lab evidence now proves the pinned source can run its official Windows build-generation path and produce a Visual Studio solution after enabling standard Windows Git long-path support.

The pinned low-level runtime has no official C# runtime/binding project. Therefore no general MotionKit .NET wrapper will be invented now. Rive remains a specialist candidate: native interop is considered only if a concrete stateful-vector reference use case justifies its cost.

## Lottie-Windows / LottieGen

Pinned source:
`dce2d4ac945b7d8d400c19bca440907315901b5f`

Source evidence confirms:
- MIT license;
- latest reviewed release `v8.1.240821.1`;
- WinUI/UWP-oriented Windows rendering;
- LottieGen .NET global tool capable of generating C#/C++ and other output from Lottie/Bodymovin JSON.

The pinned LottieGen tool now executes successfully in our Windows lab with strict parsing and TestMode; two independent generations produce byte-identical C# and identical SHA-256 output.

This validates the authored-animation/codegen workflow as tooling runtime evidence. It still does not prove WinUI/WPF renderer runtime integration, and Lottie is not considered a direct WPF control.

## Next evidence order

1. Rive exact-commit Windows native build-system feasibility.
2. Windows Composition interactive/reference-Windows runtime host evidence.
3. Reference-Windows performance methodology and measurements.
4. Command Center reference-integration preparation.

None of these probes authorize production adoption or Command Center integration.
