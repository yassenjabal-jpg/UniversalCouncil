import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
roles = json.loads((ROOT / "config" / "roles.json").read_text(encoding="utf-8"))
modes = json.loads((ROOT / "config" / "modes.json").read_text(encoding="utf-8"))
routes = json.loads((ROOT / "config" / "domain-routing.json").read_text(encoding="utf-8"))

core = {r["id"] for r in roles["core_roles"]}
specialists = {r["id"] for r in roles["specialist_roles"]}
all_roles = core | specialists

assert len(core) == len(roles["core_roles"]), "duplicate core role IDs"
assert len(specialists) == len(roles["specialist_roles"]), "duplicate specialist role IDs"
assert not (core & specialists), "core/specialist ID collision"

for mode_name, mode in modes["modes"].items():
    missing = set(mode["default_core"]) - core
    assert not missing, f"{mode_name}: unknown core roles {missing}"

for i, route in enumerate(routes["routes"]):
    missing = (set(route["specialists"]) | set(route["core_add"])) - all_roles
    assert not missing, f"route {i}: unknown roles {missing}"

print(f"OK: {len(core)} core roles, {len(specialists)} specialists, {len(routes['routes'])} routing rules, {len(modes['modes'])} modes")
