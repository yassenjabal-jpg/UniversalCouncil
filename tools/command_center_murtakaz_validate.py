from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "command-center"
PROJECT = STATE / "project-governance"
PROJECTION = PROJECT / "murtakaz-orchestration.json"
STAGE_MAP = PROJECT / "stage-phase-map.json"
TAILNET_POLICY = STATE / "owner-device-tailnet-policy.json"
TAILNET_PROJECTION = STATE / "owner-device-tailnet.json"
BUILDER = ROOT / "tools" / "build_command_center_murtakaz_projection.py"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location("murtakaz_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise SystemExit("Cannot load Murtakaz projection builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def blob_sha(relative: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{relative}"],
        cwd=ROOT,
        text=True,
    ).strip()


for required in (
    PROJECTION,
    STAGE_MAP,
    TAILNET_POLICY,
    TAILNET_PROJECTION,
    BUILDER,
):
    if not required.exists():
        raise SystemExit(f"missing Murtakaz alignment artifact: {required.relative_to(ROOT)}")

projection = load(PROJECTION)
builder = load_builder()
expected = builder.build()
if projection != expected:
    raise SystemExit("Murtakaz orchestration projection drifted; regenerate it")

if projection["source_type"] != "project_local_repository_projection":
    raise SystemExit("Murtakaz projection source type drifted")
for source in projection["source_files"]:
    if blob_sha(source["path"]) != source["blob_sha"]:
        raise SystemExit(f"Murtakaz source digest drift: {source['path']}")

authority = projection["authority"]
if (
    authority["execution_authority"]
    or authority["stage8_opened"]
    or authority["parent_mutation_allowed"]
    or not authority["owner_final_authority"]
):
    raise SystemExit("Murtakaz authority boundary drifted")

runtime = projection["runtime"]
if (
    runtime["task_state"] != "NO_LIVE_TASK"
    or runtime["active_governance_roles"]
    or runtime["active_workshop_function"] is not None
    or runtime["active_model"] is not None
    or runtime["provider_call_in_flight"]
):
    raise SystemExit("Murtakaz projection fabricated live activity")

model = projection["model_control"]
if not model["role_model_separation"] or not model["owner_controlled_selection"] or model["silent_fallback_allowed"]:
    raise SystemExit("Murtakaz model-control policy drifted")

stage_map = load(STAGE_MAP)
if stage_map["status"] != "CANONICAL":
    raise SystemExit("Stage/Phase map is not canonical")
if stage_map["delivery"]["authoritative_current_stage"] != "STAGE_7":
    raise SystemExit("Unexpected current delivery stage")
if not stage_map["rules"]["phase_number_is_not_stage_number"]:
    raise SystemExit("Stage/Phase ambiguity protection missing")
if stage_map["rules"]["stage8_opened"]:
    raise SystemExit("Stage 8 may not be opened by taxonomy mapping")
stage8 = next(item for item in stage_map["delivery"]["stages"] if item["id"] == "STAGE_8")
if stage8["status"] != "NOT_OPENED":
    raise SystemExit("Stage 8 taxonomy state drifted")

policy = load(TAILNET_POLICY)
tailnet = load(TAILNET_PROJECTION)
if policy["gates"]["stage7_ci_foundation_passed"] is not True:
    raise SystemExit("Stage 7 CI foundation policy must record verified baseline PASS")
if tailnet["gates"]["stage7_ci_foundation_passed"] is not True:
    raise SystemExit("Stage 7 CI foundation projection must record verified baseline PASS")

for pending_gate in (
    "yassin_host_probe_passed",
    "owner_device_enrollment_passed",
    "tailscale_private_serve_passed",
    "real_owner_phone_round_trip_passed",
    "session_revocation_round_trip_passed",
):
    if policy["gates"][pending_gate] or tailnet["gates"][pending_gate]:
        raise SystemExit(f"Real-host/device gate must remain pending: {pending_gate}")

if policy["gates"]["live_execution_authorized"] or tailnet["gates"]["live_execution_authorized"]:
    raise SystemExit("Murtakaz alignment may not authorize live execution")

print("Al-Murtakaz pre-prototype alignment validation: PASS")
