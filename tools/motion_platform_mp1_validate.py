from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "state" / "motion-platform" / "mp1-semantic-kernel-candidate.json"
CORE_PROJECT = ROOT / "apps" / "UniversalCouncil.MotionKit.Core" / "UniversalCouncil.MotionKit.Core.csproj"
CORE_CONTRACTS = ROOT / "apps" / "UniversalCouncil.MotionKit.Core" / "MotionContracts.cs"
CORE_COORDINATOR = ROOT / "apps" / "UniversalCouncil.MotionKit.Core" / "MotionCoordinator.cs"
VALIDATION_PROJECT = (
    ROOT / "apps" / "UniversalCouncil.MotionKit.Validation" / "UniversalCouncil.MotionKit.Validation.csproj"
)
VALIDATION_PROGRAM = ROOT / "apps" / "UniversalCouncil.MotionKit.Validation" / "Program.cs"
SPEC = ROOT / "docs" / "operations" / "motion-platform" / "05_SEMANTIC_KERNEL_SPEC.md"

for path in (
    CANDIDATE,
    CORE_PROJECT,
    CORE_CONTRACTS,
    CORE_COORDINATOR,
    VALIDATION_PROJECT,
    VALIDATION_PROGRAM,
    SPEC,
):
    if not path.exists():
        raise SystemExit(f"missing MP1 artifact: {path.relative_to(ROOT)}")

candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
if candidate["candidate_id"] != "motionkit-mp1-semantic-kernel-20261023":
    raise SystemExit("MP1 candidate identity drifted")
if candidate["status"] != "IMPLEMENTATION_CANDIDATE_NOT_ACCEPTED":
    raise SystemExit("MP1 candidate may not self-promote to accepted")
if candidate["parent_foundation_sha"] != "faf610d24b26cd0f566272c96d8e047f8a3eebcd":
    raise SystemExit("MP1 parent foundation binding drifted")

required_scope = {
    "RENDERER_FREE_CONTRACTS",
    "TRUTH_GATING",
    "INTERRUPTION",
    "INSTANCE_OWNERSHIP",
    "STALE_COMPLETION_REJECTION",
    "QUEUE_FRESHNESS",
    "REDUCED_MOTION_MODE_PRESERVATION",
    "TRUTH_REVOCATION",
    "IMMUTABLE_CONTRACT_SNAPSHOT",
}
if set(candidate["scope"]) != required_scope:
    raise SystemExit("MP1 scope drifted")

for key, value in candidate["authority"].items():
    if value:
        raise SystemExit(f"MP1 authority unexpectedly enabled: {key}")

for forbidden in ("WPF", "RIVE", "LOTTIE", "SKIASHARP", "ANDROID"):
    if forbidden not in candidate["out_of_scope"]:
        raise SystemExit(f"MP1 renderer boundary weakened: {forbidden}")

core_project = CORE_PROJECT.read_text(encoding="utf-8")
validation_project = VALIDATION_PROJECT.read_text(encoding="utf-8")
if "<PackageReference" in core_project:
    raise SystemExit("MotionKit.Core must remain dependency-free in MP1")
if "<PackageReference" in validation_project:
    raise SystemExit("MP1 validation must not acquire renderer packages")

contracts = CORE_CONTRACTS.read_text(encoding="utf-8")
coordinator = CORE_COORDINATOR.read_text(encoding="utf-8")
program = VALIDATION_PROGRAM.read_text(encoding="utf-8")
spec = SPEC.read_text(encoding="utf-8")

required_contract_markers = (
    "MotionPurpose",
    "MotionInterruptionMode",
    "MotionAccessibilityMode",
    "MotionTruthSnapshot",
    "MotionContract",
    "PendingMotion",
    "MotionLease",
    "MotionTransition",
)
for marker in required_contract_markers:
    if marker not in contracts:
        raise SystemExit(f"MP1 contract marker missing: {marker}")

required_coordinator_markers = (
    "MaxQueueDepthPerTarget = 32",
    "RejectedTruth",
    "StaleCompletionIgnored",
    "QueuedAwaitingFreshTruth",
    "Enum.IsDefined",
    "NextUniqueInstanceId",
    "ReconcileTruth",
    "ToFrozenSet",
)
for marker in required_coordinator_markers:
    if marker not in coordinator:
        raise SystemExit(f"MP1 coordinator guard missing: {marker}")

for renderer_name in ("Rive", "Lottie", "SkiaSharp", "Windows.UI", "Microsoft.UI.Xaml"):
    if renderer_name in contracts or renderer_name in coordinator:
        raise SystemExit(f"renderer leaked into semantic kernel: {renderer_name}")

required_validation_markers = (
    "CheckFalseTruthRejected",
    "CheckWrongTruthIdentityRejected",
    "CheckReplaceAndStaleCompletion",
    "CheckQueueRequiresFreshTruth",
    "CheckReducedMotionPreserved",
    "CheckFutureTruthRejected",
    "CheckMissingReducedEquivalentRejected",
    "CheckUnknownEnumInputsRejected",
    "CheckTruthRevocationStopsMotion",
    "CheckStaleTruthRevocationCannotCancelNewerMotion",
    "CheckTruthRevocationReleasesNextQueuedIntent",
    "CheckContractSnapshotIsImmutable",
    "CheckQueueBound",
    "CheckCancelTarget",
)
for marker in required_validation_markers:
    if marker not in program:
        raise SystemExit(f"MP1 behavioral validation missing: {marker}")

required_spec_markers = (
    "The kernel owns coordination, not graphics.",
    "Stale completion law",
    "Queue freshness law",
    "Truth revocation law",
    "Contract snapshot law",
    "MP1 does not:",
)
for marker in required_spec_markers:
    if marker not in spec:
        raise SystemExit(f"MP1 specification drifted: {marker}")

print("Motion Platform MP1 validation: PASS (renderer-free semantic kernel guards enforced)")
