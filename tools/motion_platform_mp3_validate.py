from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "motion-platform" / "mp3-compatibility-lab.json"
MATRIX = ROOT / "state" / "motion-platform" / "renderer-role-matrix.json"
SPEC = ROOT / "docs" / "operations" / "motion-platform" / "07_COMPATIBILITY_LAB_EXECUTION.md"
MATRIX_DOC = ROOT / "docs" / "operations" / "motion-platform" / "08_RENDERER_ROLE_MATRIX.md"
LOTTIE_FIXTURE = ROOT / "lab" / "motion-platform" / "lottie" / "MotionKitProbe.json"
LOTTIE_CHECKER = ROOT / "tools" / "motion_platform_lottiegen_check.py"
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
ACCEPTANCE_PROJECT = (
    ROOT
    / "apps"
    / "UniversalCouncil.MotionKit.SkiaWpfAcceptanceProbe"
    / "UniversalCouncil.MotionKit.SkiaWpfAcceptanceProbe.csproj"
)
ACCEPTANCE_PROGRAM = ROOT / "apps" / "UniversalCouncil.MotionKit.SkiaWpfAcceptanceProbe" / "Program.cs"
ACCEPTANCE_WINDOW = ROOT / "apps" / "UniversalCouncil.MotionKit.SkiaWpfAcceptanceProbe" / "AcceptanceWindow.cs"
ACCEPTANCE_RENDERER = ROOT / "apps" / "UniversalCouncil.MotionKit.SkiaWpfAcceptanceProbe" / "SkiaAcceptanceRenderer.cs"
ACCEPTANCE_CAPTURE = ROOT / "lab" / "motion-platform" / "capture-acceptance-reference.ps1"
ACCEPTANCE_DOC = ROOT / "docs" / "operations" / "motion-platform" / "10_MP3_REFERENCE_ACCEPTANCE.md"
COMPOSITION_PROJECT = (
    ROOT
    / "apps"
    / "UniversalCouncil.MotionKit.CompositionWpfCompileProbe"
    / "UniversalCouncil.MotionKit.CompositionWpfCompileProbe.csproj"
)
COMPOSITION_PROBE = ROOT / "apps" / "UniversalCouncil.MotionKit.CompositionWpfCompileProbe" / "CompositionWpfProbe.cs"
COMPOSITION_RUNTIME_PROJECT = (
    ROOT
    / "apps"
    / "UniversalCouncil.MotionKit.CompositionRuntimeProbe"
    / "UniversalCouncil.MotionKit.CompositionRuntimeProbe.csproj"
)
COMPOSITION_RUNTIME_PROGRAM = ROOT / "apps" / "UniversalCouncil.MotionKit.CompositionRuntimeProbe" / "Program.cs"

for path in (
    STATE,
    MATRIX,
    SPEC,
    MATRIX_DOC,
    LOTTIE_FIXTURE,
    LOTTIE_CHECKER,
    SKIA_PROJECT,
    SKIA_ADAPTER,
    SKIA_VALIDATION,
    WPF_PROJECT,
    WPF_PROBE,
    ACCEPTANCE_PROJECT,
    ACCEPTANCE_PROGRAM,
    ACCEPTANCE_WINDOW,
    ACCEPTANCE_RENDERER,
    ACCEPTANCE_CAPTURE,
    ACCEPTANCE_DOC,
    COMPOSITION_PROJECT,
    COMPOSITION_PROBE,
    COMPOSITION_RUNTIME_PROJECT,
    COMPOSITION_RUNTIME_PROGRAM,
):
    if not path.exists():
        raise SystemExit(f"missing MP3 artifact: {path.relative_to(ROOT)}")

state = json.loads(STATE.read_text(encoding="utf-8"))
matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
if state["candidate_id"] != "motionkit-mp3-compatibility-lab-20261023":
    raise SystemExit("MP3 identity drifted")
if state["parent_mp2_sha"] != "8b9e3a20ca407fff6734c945db59708d2718c2b5":
    raise SystemExit("MP3 parent MP2 binding drifted")
if state["status"] != "LAB_ACTIVE_NOT_ACCEPTED":
    raise SystemExit("MP3 may not self-promote")


if matrix["matrix_id"] != "motionkit-mp3-renderer-role-matrix-20261023":
    raise SystemExit("MP3 renderer role matrix identity drifted")
if matrix["status"] != "EVIDENCE_MATRIX_NOT_ADOPTION_DECISION":
    raise SystemExit("renderer role matrix may not become an adoption decision")
rules = matrix["rules"]
if rules["single_renderer_winner_required"]:
    raise SystemExit("MP3 must not force a single renderer winner")
if rules["production_adoption_authorized"]:
    raise SystemExit("renderer role matrix inflated production authority")
if not rules["evidence_class_must_match_claim"]:
    raise SystemExit("renderer role matrix weakened evidence-class discipline")
if rules["product_truth_may_enter_renderer"]:
    raise SystemExit("renderer role matrix weakened the truth firewall")

matrix_renderers = matrix["renderers"]
if set(matrix_renderers) != {"SKIASHARP", "WINDOWS_COMPOSITION", "RIVE", "LOTTIE_WINDOWS"}:
    raise SystemExit("renderer role matrix candidate set drifted")
if matrix_renderers["SKIASHARP"]["highest_evidence_class"] != "WINDOW_EVIDENCE":
    raise SystemExit("SkiaSharp role matrix evidence class drifted")
if matrix_renderers["WINDOWS_COMPOSITION"]["highest_evidence_class"] != "WINDOW_EVIDENCE":
    raise SystemExit("Composition role matrix over- or under-claimed evidence")
if matrix_renderers["RIVE"]["highest_evidence_class"] != "COMPILE_EVIDENCE":
    raise SystemExit("RIVE role matrix evidence class drifted")
if matrix_renderers["LOTTIE_WINDOWS"]["highest_evidence_class"] != "RUNTIME_EVIDENCE":
    raise SystemExit("Lottie tooling runtime evidence class drifted")
for candidate_id, entry in matrix_renderers.items():
    if entry["production_adoption"]:
        raise SystemExit(f"{candidate_id} was promoted to production inside MP3")

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
if set(skia["authorized_probes"]) != {
    "LINUX_HEADLESS_RUNTIME",
    "WINDOWS_WPF_CORE_BRIDGE_COMPILE",
    "WINDOWS_WPF_CORE_BRIDGE_RUNTIME",
    "WINDOWS_WPF_REFERENCE_ACCEPTANCE",
}:
    raise SystemExit("SkiaSharp probe authority drifted")
findings = {item["id"]: item for item in skia.get("observed_findings", [])}
finding = findings.get("SKIA_VIEWS_WPF_NET10_NU1701")
if not finding or finding["status"] != "BLOCKED" or finding["evidence_class"] != "COMPILE_EVIDENCE":
    raise SystemExit("SkiaSharp Views.WPF net10 compatibility finding missing")

composition = candidates["WINDOWS_COMPOSITION"]
if composition["version"] != "2.5.1" or composition["status"] != "INTERACTIVE_WPF_WINDOW_PROVEN_LAB_ONLY":
    raise SystemExit("Windows Composition research pin/status drifted")
if set(composition["authorized_probes"]) != {
    "WINDOWS_WPF_COMPOSITION_COMPILE",
    "WINDOWS_COMPOSITION_RUNTIME_API_REFERENCE_WINDOWS",
    "WINDOWS_WPF_VISUAL_HOST_RUNTIME",
}:
    raise SystemExit("Windows Composition probe authority drifted")

rive = candidates["RIVE"]
if rive["status"] != "COMPILE_FEASIBLE_NATIVE_INTEROP_RESEARCH":
    raise SystemExit("Rive compile-feasible research status drifted")
if set(rive["authorized_probes"]) != {
    "WINDOWS_NATIVE_PREMAKE_GENERATION",
    "INTEROP_BOUNDARY_LATER",
}:
    raise SystemExit("Rive probe authority drifted")
rive_probe = rive.get("probe_definition") or {}
if rive_probe.get("source_commit") != "f4da8fa42ed2c256d3d672e3828d18a328528f50":
    raise SystemExit("Rive native probe source pin drifted")
if rive_probe.get("expected_artifact") != "tests/out/release/rive.sln":
    raise SystemExit("Rive native probe expected artifact drifted")
if rive_probe.get("production_adoption"):
    raise SystemExit("Rive feasibility probe inflated production authority")
rive_evidence = {item["id"]: item for item in rive.get("observed_evidence", [])}
rive_pass = rive_evidence.get("RIVE_WINDOWS_NATIVE_PREMAKE_GENERATION_PASS")
if not rive_pass or rive_pass["status"] != "PASS" or rive_pass["evidence_class"] != "COMPILE_EVIDENCE":
    raise SystemExit("Rive Windows build-generation evidence missing")
if "RIVE_NO_OFFICIAL_CSHARP_BINDING_IN_PINNED_RUNTIME" not in rive_evidence:
    raise SystemExit("Rive C# binding absence observation missing")
lottie = candidates["LOTTIE_WINDOWS"]
if lottie["status"] != "WINUI_SPECIALIST_RESEARCH":
    raise SystemExit("Lottie-Windows was promoted beyond WinUI specialist research")
if lottie["license"] != "MIT":
    raise SystemExit("Lottie-Windows MIT license evidence drifted")
if lottie["lottiegen_tool_version"] != "8.2.250604":
    raise SystemExit("LottieGen tool version pin drifted")
if set(lottie["authorized_probes"]) != {"LOTTIEGEN_WINDOWS_CODEGEN_RUNTIME", "WINUI_COMPILE_LATER"}:
    raise SystemExit("Lottie-Windows probe authority drifted")
lottie_findings = {item["id"]: item for item in lottie.get("observed_findings", [])}
strict_finding = lottie_findings.get("LOTTIEGEN_STRICTMODE_HELP_PARSER_MISMATCH")
glob_finding = lottie_findings.get("LOTTIEGEN_GLOB_WINDOWS_SEPARATOR_ON_LINUX")
if (
    not strict_finding
    or strict_finding["status"] != "OBSERVED"
    or strict_finding["evidence_class"] != "RUNTIME_EVIDENCE"
):
    raise SystemExit("LottieGen strict-switch runtime finding missing")
if (
    not glob_finding
    or glob_finding["status"] != "PLATFORM_TOOLING_LIMITATION"
    or glob_finding["evidence_class"] != "RUNTIME_EVIDENCE"
):
    raise SystemExit("LottieGen Linux glob limitation finding missing")

composition_findings = {item["id"]: item for item in composition.get("observed_findings", [])}
queue_finding = composition_findings.get("WINDOWS_COMPOSITION_HEADLESS_RUNTIME_SHUTDOWN_TIMEOUT")
if (
    not queue_finding
    or queue_finding["status"] != "DEFERRED_INTERACTIVE_WINDOWS"
    or queue_finding["evidence_class"] != "RUNTIME_EVIDENCE"
):
    raise SystemExit("Composition headless runtime deferral evidence missing")

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

composition_runtime_project = COMPOSITION_RUNTIME_PROJECT.read_text(encoding="utf-8")
if "<UseWPF>true</UseWPF>" not in composition_runtime_project:
    raise SystemExit("Composition runtime probe stopped using WPF process model")
if "<WindowsPackageType>None</WindowsPackageType>" not in composition_runtime_project:
    raise SystemExit("Composition runtime probe lost unpackaged Windows App SDK contract")
if 'PackageReference Include="Microsoft.WindowsAppSDK" Version="2.5.1"' not in composition_runtime_project:
    raise SystemExit("Windows App SDK pin drifted in Composition runtime probe")

# External renderer packages must remain isolated to explicit lab/probe projects.
for path in (ROOT / "apps").glob("UniversalCouncil.MotionKit.*/*.csproj"):
    text = path.read_text(encoding="utf-8")
    has_skia = "SkiaSharp" in text
    if has_skia and path.parent.name not in {
        "UniversalCouncil.MotionKit.SkiaLab",
        "UniversalCouncil.MotionKit.SkiaWpfCompileProbe",
        "UniversalCouncil.MotionKit.SkiaWpfAcceptanceProbe",
    }:
        raise SystemExit(f"SkiaSharp leaked outside MP3 lab boundary: {path.relative_to(ROOT)}")
    has_winappsdk = "Microsoft.WindowsAppSDK" in text
    if has_winappsdk and path.parent.name not in {
        "UniversalCouncil.MotionKit.CompositionWpfCompileProbe",
        "UniversalCouncil.MotionKit.CompositionRuntimeProbe",
    }:
        raise SystemExit(f"Windows App SDK leaked outside MP3 Composition probes: {path.relative_to(ROOT)}")

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

acceptance_project = ACCEPTANCE_PROJECT.read_text(encoding="utf-8")
if 'PackageReference Include="SkiaSharp" Version="4.153.1"' not in acceptance_project:
    raise SystemExit("Skia reference acceptance package pin drifted")
if "SkiaSharp.Views.WPF" in acceptance_project:
    raise SystemExit("blocked SkiaSharp.Views.WPF path entered reference acceptance probe")

acceptance_window = ACCEPTANCE_WINDOW.read_text(encoding="utf-8")
for marker in (
    "RunS1Async",
    "RunS3Async",
    "RunS4Async",
    "RunS5Async",
    "MotionKit interactive icon",
    "PatternInterface.Invoke",
    "VirtualKeySpace",
    "VirtualKeyReturn",
    "SetPointerHoverState",
    "PreviewMouseLeftButtonDown",
    "actualKeyboardInteractions",
    "CompositionTarget.Rendering",
    "GC.GetTotalAllocatedBytes",
    "DispatcherPriority.Input",
    "RendererReentryCount",
):
    if marker not in acceptance_window:
        raise SystemExit(f"Skia reference acceptance marker missing: {marker}")

acceptance_program = ACCEPTANCE_PROGRAM.read_text(encoding="utf-8")
for marker in (
    "S2_STATEFUL_SIGIL",
    "NOT_APPLICABLE_CURRENT_ACCEPTED_ROLE_SET",
    "Rive remains research-only and unassigned",
    "owner_visual_acceptance = false",
    "production_adoption = false",
    "stage8_opened = false",
):
    if marker not in acceptance_program:
        raise SystemExit(f"Skia reference acceptance policy marker missing: {marker}")

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

lottie_fixture = json.loads(LOTTIE_FIXTURE.read_text(encoding="utf-8"))
for key in ("v", "fr", "ip", "op", "w", "h", "layers"):
    if key not in lottie_fixture:
        raise SystemExit(f"owned Lottie fixture missing required key: {key}")
if lottie_fixture["nm"] != "MotionKitProbe":
    raise SystemExit("owned Lottie fixture identity drifted")

lottie_checker = LOTTIE_CHECKER.read_text(encoding="utf-8")
for marker in (
    "hashlib.sha256",
    "expected exactly one generated C# file per run",
    "MotionKit.Lab",
    "MotionKitProbe",
    "not deterministic across two runs",
):
    if marker not in lottie_checker:
        raise SystemExit(f"LottieGen determinism checker marker missing: {marker}")

composition_runtime = COMPOSITION_RUNTIME_PROGRAM.read_text(encoding="utf-8")
for marker in (
    "[STAThread]",
    "new Compositor()",
    "CreateSpriteVisual",
    "CreateScalarKeyFrameAnimation",
    'StartAnimation("Opacity"',
    'StopAnimation("Opacity"',
    "CreatePropertySet",
    "DispatcherQueueController.CreateOnCurrentThread",
    "HasThreadAccess",
    "EnqueueEventLoopExit",
    "RunEventLoop",
    "ShutdownQueue()",
):
    if marker not in composition_runtime:
        raise SystemExit(f"Composition runtime API marker missing: {marker}")

spec = SPEC.read_text(encoding="utf-8")
matrix_doc = MATRIX_DOC.read_text(encoding="utf-8")
for marker in (
    "A lower evidence class must never be described as a higher one.",
    "Skia headless probe",
    "Windows WPF core-bridge compile probe",
    "Windows Composition WPF compile probe",
    "Windows Composition runtime API probe",
    "shared CI runners are not stable performance reference hardware",
    "Rive is NOT treated as a .NET/WPF drop-in dependency.",
    "Lottie-Windows is NOT treated as a direct WPF control.",
    "LottieGen deterministic codegen probe",
    "Observed tooling discrepancy:",
    "Observed platform limitation:",
    "first bounded runtime probe",
):
    if marker not in spec:
        raise SystemExit(f"MP3 specification drifted: {marker}")

for marker in (
    "VALIDATED_SPECIALIST_CANDIDATE",
    "COMPILE_PROVEN_RUNTIME_DEFERRED_INTERACTIVE_WINDOWS",
    "COMPILE_FEASIBLE_NATIVE_INTEROP_SPECIALIST",
    "TOOLING_RUNTIME_VALIDATED_WINUI_CODEGEN_SPECIALIST",
    "None of these probes authorize production adoption",
):
    if marker not in matrix_doc:
        raise SystemExit(f"renderer role matrix documentation drifted: {marker}")


# Reference evidence is bound to the probe source and captured artifacts, not an old CI head.
evidence_dir = ROOT / "lab/motion-platform/evidence/yassin-20261023"
manifest = json.loads((evidence_dir / "manifest.json").read_text(encoding="utf-8"))
for relative, expected in manifest["sha256"].items():
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT.resolve()):
        raise SystemExit("reference manifest path escaped repository")
    data = path.read_bytes()
    if path.suffix != ".png":
        data = data.replace(b"\r\n", b"\n")
    if hashlib.sha256(data).hexdigest() != expected:
        raise SystemExit(f"reference evidence/source hash mismatch: {relative}")
if manifest["composition_exit_code"] != 0 or manifest["skia_exit_code"] != 0:
    raise SystemExit("reference window process did not exit cleanly")
for name in ("composition", "skia"):
    if (evidence_dir / f"{name}.stderr.txt").read_text(encoding="utf-8").strip():
        raise SystemExit(f"{name} reference stderr is not empty")
pixels = json.loads((evidence_dir / "pixel-check.json").read_text(encoding="utf-8"))
if pixels["full_unique_sprite_colors"] < 10 or pixels["reduced_unique_sprite_colors"] != 1:
    raise SystemExit("reference Full/Reduced visible pixel evidence failed")
acceptance_dir = ROOT / "lab/motion-platform/evidence/yassin-20261023-acceptance"
acceptance_manifest = json.loads((acceptance_dir / "manifest.json").read_text(encoding="utf-8"))
for relative, expected in acceptance_manifest["sha256"].items():
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT.resolve()):
        raise SystemExit("acceptance manifest path escaped repository")
    data = path.read_bytes()
    if path.suffix != ".png":
        data = data.replace(b"\r\n", b"\n")
    if hashlib.sha256(data).hexdigest() != expected:
        raise SystemExit(f"acceptance evidence/source hash mismatch: {relative}")
if acceptance_manifest["acceptance_exit_code"] != 0:
    raise SystemExit("reference acceptance process did not exit cleanly")
if (acceptance_dir / "skia-acceptance.stderr.txt").read_text(encoding="utf-8").strip():
    raise SystemExit("reference acceptance stderr is not empty")

acceptance = json.loads((acceptance_dir / "skia-acceptance.json").read_text(encoding="utf-8"))
if acceptance["owner_visual_acceptance"] or acceptance["production_adoption"] or acceptance["stage8_opened"]:
    raise SystemExit("reference acceptance inflated owner/production/Stage8 authority")
if acceptance["renderer_reentry_count"] < 1:
    raise SystemExit("reference acceptance did not prove renderer disposal/re-entry")

results = {(item["Scenario"], item["Mode"]): item for item in acceptance["results"]}
for scenario in (
    "S1_INTERACTIVE_ICON",
    "S3_ROUTE_TRANSFER",
    "S4_SEMANTIC_OBJECT_HANDOFF",
    "S5_DENSE_SCREEN_STRESS",
):
    for mode in ("FULL", "REDUCED"):
        item = results.get((scenario, mode))
        if not item or item["Status"] != "PASS":
            raise SystemExit(f"reference acceptance scenario missing/failing: {scenario} {mode}")

for mode in ("FULL", "REDUCED"):
    s1 = results[("S1_INTERACTIVE_ICON", mode)]["Metrics"]
    if not s1.get("hover_state_path") or not s1.get("focus_path"):
        raise SystemExit(f"S1 hover/focus path missing in {mode}")
    if s1.get("hardware_pointer_injection"):
        raise SystemExit("S1 must not claim hardware pointer injection on the active-game reference host")
    if not s1.get("keyboard_space") or not s1.get("keyboard_enter"):
        raise SystemExit(f"S1 keyboard parity missing in {mode}")
    if not s1.get("selected_then_deselected"):
        raise SystemExit(f"S1 semantic toggle path missing in {mode}")
    if not s1.get("accessible_name") or not s1.get("invoke_pattern"):
        raise SystemExit(f"S1 accessibility evidence missing in {mode}")

s2 = results.get(("S2_STATEFUL_SIGIL", "ROLE_MATRIX"))
if not s2 or s2["Status"] != "NOT_APPLICABLE_CURRENT_ACCEPTED_ROLE_SET":
    raise SystemExit("S2 role disposition drifted")
if s2["Metrics"]["accepted_stateful_vector_renderer"]:
    raise SystemExit("S2 fabricated an accepted stateful-vector renderer")
if s2["Metrics"]["unknown_forward_progress_allowed"]:
    raise SystemExit("S2 permits fake UNKNOWN forward progress")

s5 = results[("S5_DENSE_SCREEN_STRESS", "FULL")]["Metrics"]
for metric in (
    "frame_interval_median_ms",
    "frame_interval_p95_ms",
    "frame_interval_p99_ms",
    "cpu_percent_process_normalized",
    "allocated_bytes_delta",
    "working_set_bytes_delta",
    "input_dispatch_latency_median_ms",
    "input_dispatch_latency_p95_ms",
):
    if metric not in s5:
        raise SystemExit(f"S5 reference metric missing: {metric}")
if s5["performance_gating"]:
    raise SystemExit("reference performance observation may not become a post-hoc threshold gate")
if s5.get("actual_keyboard_interactions", 0) < 3:
    raise SystemExit("S5 Full did not include actual keyboard interaction under load")
reduced_s5 = results[("S5_DENSE_SCREEN_STRESS", "REDUCED")]["Metrics"]
if reduced_s5.get("actual_keyboard_interactions", 0) < 1:
    raise SystemExit("S5 Reduced did not include actual keyboard interaction before static settle")
if "if (_renderer is null)" not in acceptance_window:
    raise SystemExit("reference acceptance lifecycle gap guard missing")

qualification = state["reference_windows_qualification"]
if qualification["status"] != "TECHNICAL_BAKEOFF_COMPLETE_OWNER_VISUAL_ACCEPTANCE_PENDING":
    raise SystemExit("reference Windows qualification status drifted")
if not qualification.get("technical_bakeoff_passed"):
    raise SystemExit("technical bake-off completion was not recorded")
if qualification.get("remaining") != ["Owner visual acceptance"]:
    raise SystemExit("MP3 remaining gate set drifted")
if qualification["acceptance_gate_passed"]:
    raise SystemExit("MP3 may not claim formal acceptance before owner visual acceptance")

matrix_gate = matrix.get("mp3_gate") or {}
if not matrix_gate.get("technical_bakeoff_passed"):
    raise SystemExit("renderer role matrix did not record technical bake-off")
if matrix_gate.get("owner_visual_acceptance") or matrix_gate.get("gate_passed"):
    raise SystemExit("renderer role matrix self-promoted owner/formal acceptance")
if matrix_renderers["SKIASHARP"]["current_verdict"] != "REFERENCE_WINDOWS_TECHNICALLY_ACCEPTED_SPECIALIST_CANDIDATE":
    raise SystemExit("Skia reference technical verdict drifted")
if matrix_renderers["RIVE"].get("role_assignment") != "UNASSIGNED_RESEARCH_ONLY":
    raise SystemExit("Rive role must remain unassigned research only")

print("Motion Platform MP3 validation: PASS (technical bake-off complete; owner visual acceptance pending)")
