import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
roles = json.loads((ROOT / "config" / "roles.json").read_text(encoding="utf-8"))
modes = json.loads((ROOT / "config" / "modes.json").read_text(encoding="utf-8"))
routes = json.loads((ROOT / "config" / "domain-routing.json").read_text(encoding="utf-8"))
pulse = json.loads((ROOT / "config" / "pulse.json").read_text(encoding="utf-8"))

core = {r["id"] for r in roles["core_roles"]}
specialists = {r["id"] for r in roles["specialist_roles"]}
all_roles = core | specialists

assert len(core) == len(roles["core_roles"]), "duplicate core role IDs"
assert len(specialists) == len(roles["specialist_roles"]), "duplicate specialist role IDs"
assert not (core & specialists), "core/specialist ID collision"

expected_version = "0.3.0"
for name, cfg in {"roles": roles, "modes": modes, "routes": routes, "pulse": pulse}.items():
    assert cfg.get("version") == expected_version, f"{name}: expected version {expected_version}, got {cfg.get('version')}"

for mode_name, mode in modes["modes"].items():
    missing = set(mode["default_core"]) - core
    assert not missing, f"{mode_name}: unknown core roles {missing}"
    assert mode.get("selective_debate") is True, f"{mode_name}: selective_debate must be enabled"

assert modes["modes"]["ARENA"].get("independent_positions") == "required_blind_first_round", "ARENA must require blind first positions"
assert modes["modes"]["ARENA"].get("evidence_matrix") == "required", "ARENA must require evidence matrix"
assert modes["modes"]["ARENA"].get("premortem") == "required", "ARENA must require premortem"
assert modes["modes"]["ARENA"].get("consensus_required") is False, "ARENA must not require consensus"

for i, route in enumerate(routes["routes"]):
    missing = (set(route["specialists"]) | set(route["core_add"])) - all_roles
    assert not missing, f"route {i}: unknown roles {missing}"

required_commercial = {"business", "customer_skeptic", "moat_auditor"}
commercial_routes = [r for r in routes["routes"] if "business" in r["signals"] or "startup" in r["signals"]]
assert commercial_routes, "missing commercial route"
assert required_commercial.issubset(set(commercial_routes[0]["specialists"])), "commercial route missing mandatory specialists"

assert pulse.get("enabled") is True, "Council Pulse must be enabled"
required_pulse_checks = {
    "decision_expiry_trigger",
    "execution_enthusiasm_bias",
    "sunk_cost_bias",
    "free_ai_substitution",
    "foundation_model_uplift",
    "commitment_evidence_quality"
}
assert required_pulse_checks.issubset(set(pulse["checks"])), "Council Pulse missing v0.3 checks"

print(
    f"OK v{expected_version}: {len(core)} core roles, "
    f"{len(specialists)} specialists, {len(routes['routes'])} routing rules, "
    f"{len(modes['modes'])} modes, pulse enabled"
)
