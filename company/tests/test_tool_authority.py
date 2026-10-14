import copy
import json
from datetime import datetime, timezone
import unittest
from pathlib import Path

from company.runtime.tool_authority import (
    ToolAuthorityError,
    capability_currentness,
    capability_dimensions,
    get_capability,
    requires_explicit_approval,
    validate_registry,
)

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "company" / "config" / "tool_authority.json"


class ToolAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.cfg = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_registry_contains_minimum_engineering_operations(self):
        self.assertTrue(validate_registry(self.cfg))
        operations = {record["operation"] for record in self.cfg["capabilities"]}
        self.assertTrue(
            {
                "github.read",
                "github.write",
                "github.merge",
                "memory.github_sync",
                "linear.read",
                "linear.write",
                "remote_shell.read",
                "remote_shell.execute",
                "desktop_computer_use.observe",
                "desktop_computer_use.control",
                "agent_reach.public_read",
                "browser.authenticated",
                "external.publish",
            }.issubset(operations)
        )

    def test_duplicate_operation_is_rejected(self):
        cfg = copy.deepcopy(self.cfg)
        cfg["capabilities"].append(copy.deepcopy(cfg["capabilities"][0]))
        cfg["capabilities"][-1]["id"] = "duplicate-id"
        with self.assertRaises(ToolAuthorityError):
            validate_registry(cfg)

    def test_write_or_execute_cannot_be_read_allowed(self):
        cfg = copy.deepcopy(self.cfg)
        record = next(item for item in cfg["capabilities"] if item["operation"] == "github.write")
        record["approval_policy"] = "READ_ALLOWED"
        with self.assertRaises(ToolAuthorityError):
            validate_registry(cfg)

    def test_write_or_execute_requires_prohibited_scope(self):
        cfg = copy.deepcopy(self.cfg)
        record = next(item for item in cfg["capabilities"] if item["operation"] == "remote_shell.execute")
        record["prohibited_scope"] = []
        with self.assertRaises(ToolAuthorityError):
            validate_registry(cfg)

    def test_policy_only_enforcement_cannot_claim_boundary_enforced_evidence(self):
        cfg = copy.deepcopy(self.cfg)
        record = next(item for item in cfg["capabilities"] if item["operation"] == "remote_shell.execute")
        record["evidence_level"] = "BOUNDARY_ENFORCED"
        with self.assertRaises(ToolAuthorityError):
            validate_registry(cfg)

    def test_memory_github_sync_is_narrow_owner_gated_write(self):
        record = get_capability(self.cfg, "memory.github_sync")
        self.assertEqual(record["classification"], "OWNER_GATED")
        self.assertEqual(record["effect"], "WRITE")
        self.assertEqual(record["approval_policy"], "OWNER_EXPLICIT")
        self.assertIn("memory/events", record["allowed_scope"][0])
        self.assertIn("write outside memory/", record["prohibited_scope"])
        self.assertIn("force update main", record["prohibited_scope"])

    def test_desktop_computer_use_is_split_between_observe_and_control(self):
        observe = get_capability(self.cfg, "desktop_computer_use.observe")
        control = get_capability(self.cfg, "desktop_computer_use.control")
        self.assertEqual(observe["effect"], "READ")
        self.assertEqual(observe["approval_policy"], "OWNER_EXPLICIT")
        self.assertEqual(control["effect"], "EXECUTE")
        self.assertEqual(control["classification"], "OWNER_GATED")
        self.assertEqual(control["approval_policy"], "OWNER_EXPLICIT")
        self.assertIn("credential entry", control["prohibited_scope"])

    def test_authenticated_browser_is_blocked_in_v1(self):
        record = get_capability(self.cfg, "browser.authenticated")
        self.assertEqual(record["classification"], "BLOCKED")
        self.assertEqual(record["approval_policy"], "BLOCKED")

    def test_external_publish_is_blocked(self):
        record = get_capability(self.cfg, "external.publish")
        self.assertEqual(record["classification"], "BLOCKED")
        self.assertTrue(requires_explicit_approval(record))

    def test_agent_reach_public_read_is_public_only(self):
        record = get_capability(self.cfg, "agent_reach.public_read")
        self.assertEqual(record["authentication_class"], "PUBLIC_ONLY")
        self.assertEqual(record["effect"], "READ")
        self.assertEqual(
            record["source_or_pin"],
            "94f06c1969dfc1834001269d79d3ad0972d9dee6",
        )

    def test_github_write_requires_confirmation(self):
        record = get_capability(self.cfg, "github.write")
        self.assertEqual(record["approval_policy"], "ASK_BEFORE_WRITE")
        self.assertTrue(requires_explicit_approval(record))

    def test_wrong_registry_version_is_rejected(self):
        cfg = copy.deepcopy(self.cfg)
        cfg["version"] = "2.0"
        with self.assertRaises(ToolAuthorityError):
            validate_registry(cfg)

    def test_capabilities_must_be_a_list(self):
        cfg = copy.deepcopy(self.cfg)
        cfg["capabilities"] = {}
        with self.assertRaises(ToolAuthorityError):
            validate_registry(cfg)

    def test_non_object_capability_is_rejected(self):
        cfg = copy.deepcopy(self.cfg)
        cfg["capabilities"].append("invalid")
        with self.assertRaises(ToolAuthorityError):
            validate_registry(cfg)

    def test_missing_required_fields_are_rejected(self):
        cfg = copy.deepcopy(self.cfg)
        cfg["capabilities"].append({"id": "incomplete"})
        with self.assertRaises(ToolAuthorityError):
            validate_registry(cfg)

    def test_duplicate_capability_id_is_rejected(self):
        cfg = copy.deepcopy(self.cfg)
        duplicate = copy.deepcopy(cfg["capabilities"][0])
        duplicate["operation"] = "test.unique_operation"
        cfg["capabilities"].append(duplicate)
        with self.assertRaises(ToolAuthorityError):
            validate_registry(cfg)

    def test_unknown_evidence_level_is_rejected(self):
        cfg = copy.deepcopy(self.cfg)
        cfg["capabilities"][0]["evidence_level"] = "UNVERIFIED_MAGIC"
        with self.assertRaises(ToolAuthorityError):
            validate_registry(cfg)

    def test_unknown_authority_enums_are_rejected(self):
        for field in (
            "classification",
            "authentication_class",
            "effect",
            "approval_policy",
            "enforcement",
        ):
            with self.subTest(field=field):
                cfg = copy.deepcopy(self.cfg)
                cfg["capabilities"][0][field] = "UNVERIFIED_MAGIC"
                with self.assertRaises(ToolAuthorityError):
                    validate_registry(cfg)

    def test_missing_minimum_operation_is_rejected(self):
        cfg = copy.deepcopy(self.cfg)
        cfg["capabilities"] = [record for record in cfg["capabilities"] if record["operation"] != "github.merge"]
        with self.assertRaises(ToolAuthorityError):
            validate_registry(cfg)

    def test_authenticated_browser_drift_is_rejected(self):
        cfg = copy.deepcopy(self.cfg)
        record = next(item for item in cfg["capabilities"] if item["operation"] == "browser.authenticated")
        record["classification"] = "AVAILABLE"
        with self.assertRaises(ToolAuthorityError):
            validate_registry(cfg)

    def test_external_publish_drift_is_rejected(self):
        cfg = copy.deepcopy(self.cfg)
        record = next(item for item in cfg["capabilities"] if item["operation"] == "external.publish")
        record["classification"] = "AVAILABLE"
        record["approval_policy"] = "ASK_BEFORE_WRITE"
        with self.assertRaises(ToolAuthorityError):
            validate_registry(cfg)

    def test_agent_reach_authenticated_drift_is_rejected(self):
        cfg = copy.deepcopy(self.cfg)
        record = next(item for item in cfg["capabilities"] if item["operation"] == "agent_reach.public_read")
        record["authentication_class"] = "AUTHENTICATED"
        with self.assertRaises(ToolAuthorityError):
            validate_registry(cfg)

    def test_allowed_targets_and_currentness_fields_are_validated(self):
        cfg = copy.deepcopy(self.cfg)
        record = next(item for item in cfg["capabilities"] if item["operation"] == "github.write")
        record["allowed_targets"] = []
        with self.assertRaises(ToolAuthorityError):
            validate_registry(cfg)

        cfg = copy.deepcopy(self.cfg)
        record = next(item for item in cfg["capabilities"] if item["operation"] == "github.write")
        record["allowed_targets"] = ["", 3]
        with self.assertRaises(ToolAuthorityError):
            validate_registry(cfg)

        for constraint in ("allowed_principals", "allowed_action_scopes"):
            cfg = copy.deepcopy(self.cfg)
            record = next(item for item in cfg["capabilities"] if item["operation"] == "github.write")
            record[constraint] = []
            with self.assertRaises(ToolAuthorityError):
                validate_registry(cfg)

            cfg = copy.deepcopy(self.cfg)
            record = next(item for item in cfg["capabilities"] if item["operation"] == "github.write")
            record[constraint] = ["", 3]
            with self.assertRaises(ToolAuthorityError):
                validate_registry(cfg)

        cfg = copy.deepcopy(self.cfg)
        cfg["capabilities"][0]["max_evidence_age_days"] = 0
        with self.assertRaises(ToolAuthorityError):
            validate_registry(cfg)

        cfg = copy.deepcopy(self.cfg)
        cfg["capabilities"][0]["last_verified_at"] = "not-a-date"
        with self.assertRaises(ToolAuthorityError):
            validate_registry(cfg)

    def test_capability_currentness_reports_current_stale_future_and_invalid(self):
        record = copy.deepcopy(get_capability(self.cfg, "github.read"))
        now = datetime(2026, 10, 14, tzinfo=timezone.utc)

        current = capability_currentness(record, as_of=now)
        self.assertTrue(current["current"])
        self.assertEqual(current["reason"], "current")

        stale = copy.deepcopy(record)
        stale["last_verified_at"] = "2000-01-01"
        result = capability_currentness(stale, as_of=now)
        self.assertFalse(result["current"])
        self.assertEqual(result["reason"], "stale_capability_evidence")

        future = copy.deepcopy(record)
        future["last_verified_at"] = "2099-01-01"
        result = capability_currentness(future, as_of=now)
        self.assertFalse(result["current"])
        self.assertEqual(result["reason"], "future_verification_timestamp")

        invalid = copy.deepcopy(record)
        invalid["last_verified_at"] = "bad"
        result = capability_currentness(invalid, as_of=now)
        self.assertFalse(result["current"])
        self.assertEqual(result["reason"], "invalid_last_verified_at")

        with self.assertRaises(ToolAuthorityError):
            capability_currentness(record, as_of=datetime(2026, 10, 14))

    def test_evidence_state_registry_validation_failures(self):
        operation = "github.read"

        bad = copy.deepcopy(self.cfg)
        record = next(item for item in bad["capabilities"] if item["operation"] == operation)
        record["evidence_state"] = "UNKNOWN_STATE"
        record["historical_capability"] = {}
        with self.assertRaises(ToolAuthorityError):
            validate_registry(bad)

        bad = copy.deepcopy(self.cfg)
        record = next(item for item in bad["capabilities"] if item["operation"] == operation)
        record["evidence_state"] = "HISTORICAL"
        record.pop("historical_capability", None)
        with self.assertRaises(ToolAuthorityError):
            validate_registry(bad)

        bad = copy.deepcopy(self.cfg)
        record = next(item for item in bad["capabilities"] if item["operation"] == operation)
        record["evidence_state"] = "CURRENT_VERIFIED"
        record["historical_capability"] = {}
        record.pop("current_verified_capability", None)
        with self.assertRaises(ToolAuthorityError):
            validate_registry(bad)

        bad = copy.deepcopy(self.cfg)
        record = next(item for item in bad["capabilities"] if item["operation"] == operation)
        record["evidence_state"] = "HISTORICAL"
        record["historical_capability"] = {}
        record["current_verified_capability"] = {}
        with self.assertRaises(ToolAuthorityError):
            validate_registry(bad)

    def test_capability_dimensions_separate_availability_authority_and_evidence(self):
        available = copy.deepcopy(get_capability(self.cfg, "github.read"))
        dims = capability_dimensions(
            available,
            as_of=datetime(2026, 10, 14, tzinfo=timezone.utc),
        )
        self.assertEqual(dims["availability"], "AVAILABLE")
        self.assertEqual(dims["authority"], available["classification"])
        self.assertTrue(dims["historical_capability"])

        unavailable = copy.deepcopy(available)
        unavailable["classification"] = "UNAVAILABLE"
        dims = capability_dimensions(
            unavailable,
            as_of=datetime(2026, 10, 14, tzinfo=timezone.utc),
        )
        self.assertEqual(dims["availability"], "UNAVAILABLE")

    def test_currentness_honors_explicit_evidence_states_and_expiry(self):
        base = copy.deepcopy(get_capability(self.cfg, "github.read"))
        now = datetime(2026, 10, 14, tzinfo=timezone.utc)

        for state, reason in (
            ("HISTORICAL", "historical_capability_only"),
            ("STALE", "stale_capability_evidence"),
            ("REVOKED", "revoked_capability_evidence"),
        ):
            record = copy.deepcopy(base)
            record["evidence_state"] = state
            record["historical_capability"] = {}
            record["current_verified_capability"] = None
            result = capability_currentness(record, as_of=now)
            self.assertFalse(result["current"])
            self.assertEqual(result["reason"], reason)

        record = copy.deepcopy(base)
        record["evidence_state"] = "CURRENT_VERIFIED"
        record["historical_capability"] = {}
        record["current_verified_capability"] = None
        self.assertEqual(
            capability_currentness(record, as_of=now)["reason"],
            "missing_current_capability_metadata",
        )

        for expiry, reason in (
            ("bad", "invalid_capability_expiry"),
            ("2026-10-20T00:00:00", "invalid_capability_expiry"),
            ("2026-10-13T00:00:00+00:00", "expired_capability_evidence"),
        ):
            record = copy.deepcopy(base)
            record["evidence_state"] = "CURRENT_VERIFIED"
            record["historical_capability"] = {}
            record["current_verified_capability"] = {"expires_at": expiry}
            result = capability_currentness(record, as_of=now)
            self.assertFalse(result["current"])
            self.assertEqual(result["reason"], reason)

        current = copy.deepcopy(base)
        current["evidence_state"] = "CURRENT_VERIFIED"
        current["historical_capability"] = {}
        current["current_verified_capability"] = {"expires_at": "2026-10-20T00:00:00+00:00"}
        current["last_verified_at"] = "2026-10-13T23:00:00+03:00"
        result = capability_currentness(current, as_of=now)
        self.assertTrue(result["current"])

    def test_unknown_operation_lookup_is_rejected(self):
        with self.assertRaises(ToolAuthorityError):
            get_capability(self.cfg, "missing.operation")


if __name__ == "__main__":
    unittest.main()
