import copy
import json
import unittest
from pathlib import Path

from company.runtime.tool_authority import (
    ToolAuthorityError,
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
                "linear.read",
                "linear.write",
                "remote_shell.read",
                "remote_shell.execute",
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


if __name__ == "__main__":
    unittest.main()
