from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "state" / "motion-platform" / "mp2-renderer-boundary-candidate.json"
SPEC = ROOT / "docs" / "operations" / "motion-platform" / "06_RENDERER_BOUNDARY_SPEC.md"
RUNTIME_PROJECT = ROOT / "apps" / "UniversalCouncil.MotionKit.Runtime" / "UniversalCouncil.MotionKit.Runtime.csproj"
CONTRACTS = ROOT / "apps" / "UniversalCouncil.MotionKit.Runtime" / "RendererContracts.cs"
GUARD = ROOT / "apps" / "UniversalCouncil.MotionKit.Runtime" / "MotionRendererContractGuard.cs"
RESOLVER = ROOT / "apps" / "UniversalCouncil.MotionKit.Runtime" / "MotionProfileResolver.cs"
TESTING_PROJECT = ROOT / "apps" / "UniversalCouncil.MotionKit.Testing" / "UniversalCouncil.MotionKit.Testing.csproj"
FAKE = ROOT / "apps" / "UniversalCouncil.MotionKit.Testing" / "DeterministicFakeRenderer.cs"
VALIDATION_PROJECT = (
    ROOT
    / "apps"
    / "UniversalCouncil.MotionKit.RendererValidation"
    / "UniversalCouncil.MotionKit.RendererValidation.csproj"
)
VALIDATION_PROGRAM = ROOT / "apps" / "UniversalCouncil.MotionKit.RendererValidation" / "Program.cs"

for path in (
    CANDIDATE,
    SPEC,
    RUNTIME_PROJECT,
    CONTRACTS,
    GUARD,
    RESOLVER,
    TESTING_PROJECT,
    FAKE,
    VALIDATION_PROJECT,
    VALIDATION_PROGRAM,
):
    if not path.exists():
        raise SystemExit(f"missing MP2 artifact: {path.relative_to(ROOT)}")

candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
if candidate["candidate_id"] != "motionkit-mp2-renderer-boundary-20261023":
    raise SystemExit("MP2 candidate identity drifted")
if candidate["parent_mp1_sha"] != "cfd965afca6c12383333c81c15a76ac6376bc05c":
    raise SystemExit("MP2 parent MP1 binding drifted")
if candidate["status"] != "IMPLEMENTATION_CANDIDATE_NOT_ACCEPTED":
    raise SystemExit("MP2 candidate may not self-promote")

required_scope = {
    "RENDERER_NEUTRAL_CAPABILITIES",
    "TRUTH_FIREWALL",
    "PRODUCT_MOTION_PROFILE_RESOLUTION",
    "FULL_REDUCED_VARIANTS",
    "ADAPTER_CONTRACT",
    "DETERMINISTIC_FAKE_RENDERER",
    "RENDERER_DIAGNOSTICS",
    "PROFILE_IDENTITY_EVIDENCE",
    "ADAPTER_VERSION_EVIDENCE",
    "STATIC_FALLBACK_CAPABILITY_GUARD",
}
if set(candidate["scope"]) != required_scope:
    raise SystemExit("MP2 scope drifted")

for key, value in candidate["authority"].items():
    if value:
        raise SystemExit(f"MP2 authority unexpectedly enabled: {key}")

for forbidden in (
    "REAL_RENDERER_ADOPTION",
    "WPF_INTEGRATION",
    "RIVE_INTEGRATION",
    "LOTTIE_INTEGRATION",
    "SKIASHARP_INTEGRATION",
    "ANDROID_INTEGRATION",
    "COMMAND_CENTER_PRODUCTION_INTEGRATION",
    "PR72_MERGE",
    "STAGE8",
):
    if forbidden not in candidate["out_of_scope"]:
        raise SystemExit(f"MP2 boundary weakened: {forbidden}")

projects = (RUNTIME_PROJECT, TESTING_PROJECT, VALIDATION_PROJECT)
for project in projects:
    content = project.read_text(encoding="utf-8")
    if "<PackageReference" in content:
        raise SystemExit(f"MP2 project acquired external package: {project.relative_to(ROOT)}")

contracts = CONTRACTS.read_text(encoding="utf-8")
guard = GUARD.read_text(encoding="utf-8")
resolver = RESOLVER.read_text(encoding="utf-8")
fake = FAKE.read_text(encoding="utf-8")
program = VALIDATION_PROGRAM.read_text(encoding="utf-8")
spec = SPEC.read_text(encoding="utf-8")

for forbidden_truth in (
    "MotionTruthSnapshot",
    "TruthRequirementId",
    "TruthSourceVersion",
    "TruthObservedAt",
):
    if forbidden_truth in contracts:
        raise SystemExit(f"renderer contract leaked product truth: {forbidden_truth}")

for renderer_brand in (
    "Rive",
    "Lottie",
    "SkiaSharp",
    "Windows.UI.Composition",
    "Microsoft.UI.Composition",
    "Android",
):
    if renderer_brand in contracts or renderer_brand in guard or renderer_brand in resolver:
        raise SystemExit(f"real renderer brand leaked into MP2 runtime: {renderer_brand}")

required_contract_markers = (
    "MotionRenderCapability",
    "MotionRenderStatus",
    "MotionSettleMode",
    "MotionRenderIdentity",
    "MotionVisualVariant",
    "MotionVisualRule",
    "MotionProductProfile",
    "MotionRenderCommand",
    "ProfileId",
    "AdapterVersion",
    "IMotionRendererAdapter",
)
for marker in required_contract_markers:
    if marker not in contracts:
        raise SystemExit(f"MP2 renderer contract marker missing: {marker}")

required_guard_markers = (
    "KnownCapabilities",
    "MaxDuration",
    "ValidateCommand",
    "ValidateAdapter",
    "Adapter version is invalid.",
    "Supports",
    "KnownCapabilitySet",
)
for marker in required_guard_markers:
    if marker not in guard:
        raise SystemExit(f"MP2 renderer guard missing: {marker}")

for marker in ("ToFrozenDictionary", "MotionAccessibilityMode.Reduced", "RuleNotFound"):
    if marker not in resolver:
        raise SystemExit(f"MP2 profile resolver guard missing: {marker}")

for forbidden_fake in ("Task.Delay", "Random(", "Random.Shared", "System.Timers", "DispatcherTimer"):
    if forbidden_fake in fake:
        raise SystemExit(f"deterministic fake renderer acquired nondeterminism: {forbidden_fake}")

for marker in (
    "DeterministicFakeRenderer",
    "DuplicateInstance",
    "NotSupported",
    "SnapshotDiagnostics",
    "Static fallback requires StaticSettle capability.",
    "AdapterVersion",
    "lock (_gate)",
):
    if marker not in fake:
        raise SystemExit(f"MP2 fake renderer marker missing: {marker}")

required_validation_markers = (
    "CheckFullAndReducedProfileResolution",
    "CheckProfileSnapshotImmutability",
    "CheckMissingRuleFailsClosed",
    "CheckInvalidProfileFailsClosed",
    "CheckRenderCommandTruthFirewall",
    "CheckSupportedBeginDuplicateSettleAsync",
    "CheckUnsupportedCapabilityAsync",
    "CheckCancelAndNotActiveAsync",
    "CheckUnknownCapabilityRejectedAsync",
    "CheckStaticFallbackRequiresCapabilityAsync",
    "CheckAdapterVersionValidation",
    "CheckConcurrentFakeRendererAsync",
    "CheckDisposalCleanupAsync",
)
for marker in required_validation_markers:
    if marker not in program:
        raise SystemExit(f"MP2 behavioral validation missing: {marker}")

for marker in (
    "Truth firewall",
    "Reduced Motion is therefore a first-class variant",
    "Deterministic fake renderer",
    "product Motion Profile ID",
    "explicit adapter version",
    "no silent fallback",
):
    if marker not in spec:
        raise SystemExit(f"MP2 specification drifted: {marker}")

print("Motion Platform MP2 validation: PASS (renderer boundary + truth firewall + fake renderer)")
