import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
roles = json.loads((ROOT / "config" / "roles.json").read_text(encoding="utf-8"))
modes = json.loads((ROOT / "config" / "modes.json").read_text(encoding="utf-8"))
routes = json.loads((ROOT / "config" / "domain-routing.json").read_text(encoding="utf-8"))
pulse = json.loads((ROOT / "config" / "pulse.json").read_text(encoding="utf-8"))
company_roles = json.loads((ROOT / "company" / "config" / "roles.json").read_text(encoding="utf-8"))
scouting = json.loads((ROOT / "company" / "config" / "capability_scouting.json").read_text(encoding="utf-8"))
gateway = json.loads((ROOT / "company" / "config" / "intelligence_gateway.json").read_text(encoding="utf-8"))

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
    "commitment_evidence_quality",
    "capability_gap",
    "tooling_or_external_capability_change",
    "hr_capability_scouting_due",
}
assert required_pulse_checks.issubset(set(pulse["checks"])), "Council Pulse missing required checks"

hr = company_roles["hr_capability_director"]
assert company_roles.get("version") == "1.3", "company HR role config must be v1.3"
assert hr.get("may_run_read_only_capability_discovery") is True, "HR read-only scouting must be enabled"
for key in (
    "may_install_tools_unilaterally",
    "may_connect_credentials_unilaterally",
    "may_authenticate_accounts_unilaterally",
    "may_purchase_tools_unilaterally",
    "may_change_permissions_unilaterally",
    "may_enable_browser_extensions_unilaterally",
    "may_execute_external_writes_unilaterally",
):
    assert hr.get(key) is False, f"{key} must fail closed"

assert scouting.get("enabled") is True, "capability scouting must be enabled"
assert scouting.get("owner") == "HR & Capability Director", "capability scouting owner mismatch"
assert scouting.get("permanent_new_role") is False, "scouting must not add a permanent role"
assert scouting["cadence"]["periodic_active_days"] == 7, "active scouting cadence mismatch"
assert scouting["cadence"]["periodic_inactive_days"] == 30, "inactive scouting cadence mismatch"
assert scouting["supply_chain_requirements"]["version_or_commit_pin_required"] is True, "pilot pinning required"
assert scouting["supply_chain_requirements"]["moving_branch_install_for_pilot_forbidden"] is True, "moving pilot installs must be forbidden"
for action in ("INSTALL_TOOL","CONNECT_CREDENTIALS","AUTHENTICATE_ACCOUNT","PURCHASE","CHANGE_PERMISSIONS","ENABLE_BROWSER_EXTENSION","WRITE_EXTERNAL","PUBLISH","SEND_MESSAGE"):
    assert action in scouting["hr_forbidden_unilateral_actions"], f"missing HR action boundary: {action}"


def validate_intelligence_gateway(cfg):
    assert cfg.get("version") == "1.0", "intelligence gateway config must be v1.0"
    assert cfg.get("default_mode") == "READ_ONLY", "gateway must default to read-only"
    assert cfg.get("default_auth_requirement") == "PUBLIC_ONLY", "gateway must default to public-only"
    ar = cfg["agent_reach"]
    assert ar.get("strict_pin") is True, "Agent Reach strict pinning must be enabled"
    assert ar.get("approved_commit") == "94f06c1969dfc1834001269d79d3ad0972d9dee6", "unexpected Agent Reach pin"
    expected_ops = {
        "web_read_public",
        "youtube_metadata_public",
        "youtube_transcript_public",
        "rss_read_public",
        "bilibili_basic_public",
        "doctor_read_only",
    }
    assert set(ar.get("allowed_operations", ())) == expected_ops, "Agent Reach allowlist drift"
    forbidden = {"install", "configure", "opencli", "publish", "message"}
    assert forbidden.isdisjoint(set(ar.get("allowed_operations", ()))), "forbidden Agent Reach operation enabled"
    required_blocked = {
        "instagram_authenticated",
        "facebook_authenticated",
        "reddit_authenticated",
        "x_authenticated",
        "linkedin_authenticated",
        "xiaohongshu_authenticated",
    }
    assert required_blocked.issubset(set(cfg.get("blocked_intents", ()))), "authenticated social route missing block"
    assert cfg["routes"]["github"]["providers"] == ["native_github"], "GitHub must remain native-only"
    assert cfg["routes"]["private_drive"]["providers"] == ["native_drive"], "private Drive must remain native-only"


validate_intelligence_gateway(gateway)

print(
    f"OK v{expected_version}: {len(core)} core roles, "
    f"{len(specialists)} specialists, {len(routes['routes'])} routing rules, "
    f"{len(modes['modes'])} modes, pulse enabled, HR capability scouting + intelligence gateway enforced"
)
