from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "command-center"
INDEX = STATE / "stage7-real-host-evidence-index.json"
POLICY = STATE / "owner-device-tailnet-policy.json"
PROJECTION = STATE / "owner-device-tailnet.json"
STAGE_MAP = STATE / "project-governance" / "stage-phase-map.json"
PHASE0 = STATE / "phase0-execution-gates.json"

REQUIRED_REAL_GATES = (
    "yassin_host_probe",
    "owner_device_enrollment",
    "tailscale_private_serve",
    "real_owner_phone_round_trip",
    "session_revocation_round_trip",
)

POLICY_GATE_MAP = {
    "yassin_host_probe": "yassin_host_probe_passed",
    "owner_device_enrollment": "owner_device_enrollment_passed",
    "tailscale_private_serve": "tailscale_private_serve_passed",
    "real_owner_phone_round_trip": "real_owner_phone_round_trip_passed",
    "session_revocation_round_trip": "session_revocation_round_trip_passed",
}

FORBIDDEN_EVIDENCE_KEYS = {
    "peer_list",
    "peers",
    "account_email",
    "account_identity",
    "auth_key",
    "tailscale_auth_key",
    "bearer_token",
    "session_token",
    "raw_status",
    "raw_tailscale_status",
}


def load(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing Stage 7 real-evidence artifact: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def walk_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key.casefold()
            yield from walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_keys(child)


index = load(INDEX)
policy = load(POLICY)
projection = load(PROJECTION)
stage_map = load(STAGE_MAP)
phase0 = load(PHASE0)

if index.get("schema_version") != "1.0" or index.get("stage") != "STAGE_7":
    raise SystemExit("Stage 7 real-evidence index schema/stage drifted")
if index.get("target_host") != "YASSIN":
    raise SystemExit("Stage 7 real evidence must remain bound to YASSIN")

snapshot = index["observed_access_snapshot"]
if snapshot["device_state"] != "OFFLINE" or snapshot["remote_tool_calls_left_pct"] != 0:
    raise SystemExit("Current Stage 7 external-access snapshot drifted from observed YASSIN blocker")

protected = index["protected_truth"]
if (
    protected["stage8_opened"]
    or protected["live_execution_authorized"]
    or protected["execution_state"] != "BLOCKED_PHASE0"
    or protected["tailscale_funnel_allowed"]
    or protected["public_bind_allowed"]
):
    raise SystemExit("Stage 7 evidence index inflated execution/network authority")

delivery = stage_map["delivery"]
if delivery["authoritative_current_stage"] != "STAGE_7":
    raise SystemExit("Stage 7 evidence intake may run only while Stage 7 is authoritative")
stage8 = next(item for item in delivery["stages"] if item["id"] == "STAGE_8")
if stage8["status"] != "NOT_OPENED":
    raise SystemExit("Stage 8 must remain unopened during Stage 7 evidence intake")

if phase0["live_execution_authorized"]:
    raise SystemExit("Phase 0 still forbids live execution during Stage 7")

if policy["host_evidence"]["remote_command_channel_state"] != "DEVICE_OFFLINE_AND_TOOL_QUOTA_BLOCKED":
    raise SystemExit("Stage 7 policy no longer reflects the current YASSIN access blocker")
if (
    projection["host_evidence"]["remote_command_channel_state"]
    != policy["host_evidence"]["remote_command_channel_state"]
):
    raise SystemExit("Stage 7 projection/policy host-access truth diverged")

gates = index["gates"]
if gates["stage7_ci_foundation"]["status"] != "VERIFIED":
    raise SystemExit("Stage 7 CI foundation must remain verified")
if policy["gates"]["stage7_ci_foundation_passed"] is not True:
    raise SystemExit("Stage 7 policy lost verified CI foundation")

real_verified = []
for gate_name in REQUIRED_REAL_GATES:
    gate = gates[gate_name]
    policy_value = policy["gates"][POLICY_GATE_MAP[gate_name]]
    projection_value = projection["gates"][POLICY_GATE_MAP[gate_name]]
    is_verified = gate["status"] == "VERIFIED"

    if policy_value is not is_verified or projection_value is not is_verified:
        raise SystemExit(f"Stage 7 gate truth mismatch: {gate_name}")

    if is_verified:
        real_verified.append(gate_name)
        evidence = gate.get("evidence")
        if not isinstance(evidence, dict):
            raise SystemExit(f"Verified Stage 7 gate lacks evidence: {gate_name}")
        if evidence.get("sanitized") is not True:
            raise SystemExit(f"Verified Stage 7 evidence is not sanitized: {gate_name}")
        digest = evidence.get("sha256")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise SystemExit(f"Verified Stage 7 evidence lacks SHA-256: {gate_name}")
        if not evidence.get("reference"):
            raise SystemExit(f"Verified Stage 7 evidence lacks reference: {gate_name}")
    elif gate.get("evidence") is not None:
        raise SystemExit(f"Pending Stage 7 gate may not carry promoted evidence: {gate_name}")

if snapshot["device_state"] == "OFFLINE" and real_verified:
    raise SystemExit("Real-host/device gates may not be newly verified while current YASSIN snapshot is offline")

closure = index["closure"]
all_verified = len(real_verified) == len(REQUIRED_REAL_GATES)
if closure["eligible"] is not all_verified:
    raise SystemExit("Stage 7 closure eligibility does not match verified real-evidence gates")
if not all_verified and not closure.get("blocker"):
    raise SystemExit("Pending Stage 7 closure must expose a blocker")

if policy["gates"]["live_execution_authorized"] or projection["gates"]["live_execution_authorized"]:
    raise SystemExit("Stage 7 evidence may not authorize live execution")

for key in walk_keys(index):
    if key in FORBIDDEN_EVIDENCE_KEYS:
        raise SystemExit(f"Sensitive/raw evidence key forbidden in Stage 7 index: {key}")

print(
    "Stage 7 real-host evidence validation: PASS "
    f"({len(real_verified)}/{len(REQUIRED_REAL_GATES)} real gates verified; "
    "fail-closed pending external YASSIN access)"
)
