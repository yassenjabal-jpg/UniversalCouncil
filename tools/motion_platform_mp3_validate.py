from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "motion-platform" / "mp3-compatibility-lab.json"
SPEC = ROOT / "docs" / "operations" / "motion-platform" / "07_COMPATIBILITY_LAB_EXECUTION.md"
SKIA_PROJECT = ROOT / "apps" / "UniversalCouncil.MotionKit.SkiaLab" / "UniversalCouncil.MotionKit.SkiaLab.csproj"
SKIA_ADAPTER = ROOT / "apps" / "UniversalCouncil.MotionKit.SkiaLab" / "SkiaOffscreenLabAdapter.cs"
SKIA_VALIDATION = ROOT / "apps" / "UniversalCouncil.MotionKit.SkiaLabValidation" / "Program.cs"
WPF_PROJECT = (
    ROOT
    / "apps"
    / "UniversalCouncil.MotionKit.SkiaWpfCompileProbe"
    / "UniversalCouncil.MotionKit.SkiaWpfCompileProbe.csproj"
)
WPF_PROBE = ROOT / "apps" / "UniversalCouncil.MotionKit.SkiaWpfCompileProbe" / "SkiaWpfProbe.cs"
COMPOSITION_PROJECT = (
    ROOT
    / "apps"
    / "UniversalCouncil.MotionKit.CompositionWpfCompileProbe"
    / "UniversalCouncil.MotionKit.CompositionWpfCompileProbe.csproj"
)
COMPOSITION_PROBE = ROOT / "apps" / "UniversalCouncil.MotionKit.CompositionWpfCompileProbe" / "CompositionWpfProbe.cs"

for path in (
    STATE,
    SPEC,
    SKIA_PROJECT,
    SKIA_ADAPTER,
    SKIA_VALIDATION,
    WPF_PROJECT,
    WPF_PROBE,
    COMPOSITION_PROJECT,
    COMPOSITION_PROBE,
):
    if not path.exists():
        raise SystemExit(f"missing MP3 artifact: {path.relative_to(ROOT)}")

state = json.loads(STATE.read_text(encoding="utf-8"))
if state["candidate_id"] != "motionkit-mp3-compatibility-lab-20261023":
    raise SystemExit("MP3 identity drifted")
if state["parent_mp2_sha"] != "8b9e3a20ca407fff6734c945db59708d2718c2b5":
    raise SystemExit("MP3 parent MP2 binding drifted")
if state["status"] != "LAB_ACTIVE_NOT_ACCEPTED":
    raise SystemExit("MP3 may not self-promote")

expected_evidence = [
    "SOURCE_EVIDENCE",
    "COMPILE_EVIDENCE",
    "RUNTIME_EVIDENCE",
    "WINDOW_EVIDENCE",
    "OWNER_VISUAL_EVIDENCE",
]
if state["evidence_classes"] != expected_evidence:
    raise SystemExit("MP3 evidence-class ordering drifted")

candidates = state["candidates"]
required = {"SKIASHARP", "WINDOWS_COMPOSITION", "RIVE", "LOTTIE_WINDOWS"}
if set(candidates) != required:
    raise SystemExit("MP3 candidate set drifted")

skia = candidates["SKIASHARP"]
if skia["version"] != "4.153.1" or skia["license"] != "MIT" or skia["status"] != "LAB_ONLY":
    raise SystemExit("SkiaSharp pin/license/status drifted")
if set(skia["authorized_probes"]) != {"LINUX_HEADLESS_RUNTIME", "WINDOWS_WPF_CORE_BRIDGE_COMPILE"}:
    raise SystemExit("SkiaSharp probe authority drifted")
findings = {item["id"]: item for item in skia.get("observed_findings", [])}
finding = findings.get("SKIA_VIEWS_WPF_NET10_NU1701")
if not finding or finding["status"] != "BLOCKED" or finding["evidence_class"] != "COMPILE_EVIDENCE":
    raise SystemExit("SkiaSharp Views.WPF net10 compatibility finding missing")

composition = candidates["WINDOWS_COMPOSITION"]
if composition["version"] != "2.5.1" or composition["status"] != "LAB_ONLY":
    raise SystemExit("Windows Composition research pin drifted")
if set(composition["authorized_probes"]) != {
    "WINDOWS_WPF_COMPOSITION_COMPILE",
    "WINDOWS_RUNTIME_LATER",
}:
    raise SystemExit("Windows Composition probe authority drifted")

if candidates["RIVE"]["status"] != "NATIVE_INTEROP_RESEARCH":
    raise SystemExit("Rive was promoted without native interop evidence")
if candidates["LOTTIE_WINDOWS"]["status"] != "WINUI_SPECIALIST_RESEARCH":
    raise SystemExit("Lottie-Windows was promoted beyond WinUI specialist research")

policy = state["performance_policy"]
if policy["shared_ci_wall_clock_is_gating"]:
    raise SystemExit("shared CI wall-clock must remain informational")
if not policy["correctness_is_gating"]:
    raise SystemExit("MP3 correctness gates unexpectedly disabled")
if not policy["reference_windows_hardware_required_before_performance_gate"]:
    raise SystemExit("performance gates require reference Windows hardware")

for key, value in state["authority"].items():
    if value:
        raise SystemExit(f"MP3 authority unexpectedly enabled: {key}")

skia_project = SKIA_PROJECT.read_text(encoding="utf-8")
if 'PackageReference Include="SkiaSharp" Version="4.153.1"' not in skia_project:
    raise SystemExit("SkiaSharp lab package pin drifted")
if 'PackageReference Include="SkiaSharp.NativeAssets.Linux" Version="4.153.1"' not in skia_project:
    raise SystemExit("SkiaSharp Linux native asset pin drifted")

wpf_project = WPF_PROJECT.read_text(encoding="utf-8")
if "<UseWPF>true</UseWPF>" not in wpf_project:
    raise SystemExit("Skia WPF compile probe stopped being WPF")
if 'PackageReference Include="SkiaSharp" Version="4.153.1"' not in wpf_project:
    raise SystemExit("SkiaSharp core WPF bridge pin drifted")
if "SkiaSharp.Views.WPF" in wpf_project:
    raise SystemExit("blocked SkiaSharp.Views.WPF path re-entered .NET 10 probe")

composition_project = COMPOSITION_PROJECT.read_text(encoding="utf-8")
if "<UseWPF>true</UseWPF>" not in composition_project:
    raise SystemExit("Composition compile probe stopped being WPF")
if "<WindowsPackageType>None</WindowsPackageType>" not in composition_project:
    raise SystemExit("Composition WPF probe lost unpackaged Windows App SDK initialization contract")
if 'PackageReference Include="Microsoft.WindowsAppSDK" Version="2.5.1"' not in composition_project:
    raise SystemExit("Windows App SDK pin drifted in Composition probe")

# External renderer packages must remain isolated to explicit lab/probe projects.
for path in (ROOT / "apps").glob("UniversalCouncil.MotionKit.*/*.csproj"):
    text = path.read_text(encoding="utf-8")
    has_skia = "SkiaSharp" in text
    if has_skia and path.parent.name not in {
        "UniversalCouncil.MotionKit.SkiaLab",
        "UniversalCouncil.MotionKit.SkiaWpfCompileProbe",
    }:
        raise SystemExit(f"SkiaSharp leaked outside MP3 lab boundary: {path.relative_to(ROOT)}")
    has_winappsdk = "Microsoft.WindowsAppSDK" in text
    if has_winappsdk and path.parent.name != "UniversalCouncil.MotionKit.CompositionWpfCompileProbe":
        raise SystemExit(f"Windows App SDK leaked outside MP3 Composition probe: {path.relative_to(ROOT)}")

adapter = SKIA_ADAPTER.read_text(encoding="utf-8")
for marker in (
    "SkiaOffscreenLabAdapter",
    "SkiaSharp-4.153.1",
    "RenderDeterministicFrame",
    "SHA256.HashData",
    "MotionRenderCapability.PathGeometry",
    "MotionRenderCapability.DynamicDrawing",
):
    if marker not in adapter:
        raise SystemExit(f"Skia lab adapter marker missing: {marker}")

for forbidden_claim in (
    "| MotionRenderCapability.StatefulVector",
    "| MotionRenderCapability.PreauthoredTimeline",
    "| MotionRenderCapability.HitTesting",
):
    if forbidden_claim in adapter.split("public MotionRenderCapability Capabilities =>", 1)[1].split(";", 1)[0]:
        raise SystemExit(f"Skia lab over-claimed capability: {forbidden_claim}")

validation = SKIA_VALIDATION.read_text(encoding="utf-8")
for marker in (
    "CheckDeterministicFrameAsync",
    "CheckReducedVariantAsync",
    "CheckUnsupportedStatefulVectorAsync",
    "CheckLifecycleAsync",
    "ObserveBatchCostAsync",
    "non-gating",
):
    if marker not in validation:
        raise SystemExit(f"Skia lab validation marker missing: {marker}")

probe = WPF_PROBE.read_text(encoding="utf-8")
for marker in ("BitmapSource.Create", "bitmap.GetPixels()", "PixelFormats.Bgra32"):
    if marker not in probe:
        raise SystemExit(f"Skia WPF core bridge marker missing: {marker}")

composition_probe = COMPOSITION_PROBE.read_text(encoding="utf-8")
for marker in (
    "Microsoft.UI.Composition",
    "Compositor",
    "CreateScalarKeyFrameAnimation",
    "CreateSpriteVisual",
    "WindowInteropHelper",
):
    if marker not in composition_probe:
        raise SystemExit(f"Composition WPF compile marker missing: {marker}")

spec = SPEC.read_text(encoding="utf-8")
for marker in (
    "A lower evidence class must never be described as a higher one.",
    "Skia headless probe",
    "Windows WPF core-bridge compile probe",
    "Windows Composition WPF compile probe",
    "shared CI runners are not stable performance reference hardware",
    "Rive is NOT treated as a .NET/WPF drop-in dependency.",
    "Lottie-Windows is NOT treated as a direct WPF control.",
):
    if marker not in spec:
        raise SystemExit(f"MP3 specification drifted: {marker}")

print("Motion Platform MP3 validation: PASS (compatibility lab boundaries + Skia probes)")
