# Motion Platform MP3 — Renderer Role Matrix

Date: 2026-10-23  
Status: EVIDENCE MATRIX — NOT AN ADOPTION DECISION

## Decision principle

MP3 does not search for one universal animation engine.

Each renderer is evaluated only for the motion families it can execute truthfully, accessibly, and maintainably behind the MotionKit adapter boundary.

## Current matrix

| Candidate | Highest evidence | Current role | WPF path | Current verdict |
| --- | --- | --- | --- | --- |
| SkiaSharp 4.153.1 | WINDOW_EVIDENCE | dynamic drawing, paths, diagrams, data-driven 2D | owned core Skia -> BitmapSource bridge | VALIDATED_SPECIALIST_CANDIDATE |
| Windows Composition / WASDK 2.5.1 | WINDOW_EVIDENCE | Windows-native property/micro motion | WPF HWND + ContentIsland/DesktopChildSiteBridge on YASSIN | INTERACTIVE_WPF_WINDOW_PROVEN_LAB_ONLY |
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
- product-scale WPF rendering (the isolated pixel bridge window is now proven);
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

The historical verdict COMPILE_PROVEN_RUNTIME_DEFERRED_INTERACTIVE_WINDOWS is superseded for YASSIN by WINDOW_EVIDENCE. Headless failure history is retained. ContentIsland hosting, visible Full opacity changes, Reduced static settle, and normal shutdown are proven; production adoption remains false.

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

## Reference Windows evidence

See [YASSIN evidence and MP4 handoff](09_YASSIN_REFERENCE_EVIDENCE_AND_MP4_HANDOFF.md). The mandatory S1..S5 acceptance bake-off is not claimed by these feasibility probes.

## 2026-10-23 reference acceptance addendum

YASSIN reference testing now closes the technical bake-off for the currently assigned roles:

| Scenario | Assigned renderer path | Full | Reduced | Disposition |
| --- | --- | --- | --- | --- |
| S1 Interactive Icon | SkiaSharp core pixels + native WPF input/accessibility surface | PASS | PASS | shared WPF hover-state handler, keyboard Space/Enter parity, selected/deselected, accessible name and Invoke pattern verified; hardware pointer injection not claimed on the active-game host |
| S2 Stateful Sigil | none | N/A | N/A | NOT_APPLICABLE_CURRENT_ACCEPTED_ROLE_SET; Rive remains compile-evidence research only |
| S3 Route Transfer | SkiaSharp core pixels -> WPF BitmapSource | PASS | PASS | RETURN at mid-transfer settles at source with identity preserved |
| S4 Semantic Object Handoff | SkiaSharp core pixels -> WPF BitmapSource | PASS | PASS | unavailable destination settles deterministically to source fallback |
| S5 Dense Screen Stress | SkiaSharp core pixels -> WPF BitmapSource | PASS | PASS | 64 independent objects; reference CPU/allocation/memory/input observations recorded |

SkiaSharp's current technical verdict is REFERENCE_WINDOWS_TECHNICALLY_ACCEPTED_SPECIALIST_CANDIDATE.
This is still not production adoption. OWNER_VISUAL_EVIDENCE is absent, GPU-present telemetry was not measured, and no post-hoc performance threshold was invented.

Rive remains COMPILE_FEASIBLE_NATIVE_INTEROP_SPECIALIST / UNASSIGNED_RESEARCH_ONLY. No native wrapper was created to manufacture an S2 pass.
