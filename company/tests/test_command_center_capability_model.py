from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "state" / "command-center"
PROJECT = STATE / "project-governance"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class CommandCenterCapabilityModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = load(STATE / "capability-registry.json")
        cls.policy = load(STATE / "model-broker-policy.json")
        cls.state = load(STATE / "capability-model-state.json")
        cls.pre = load(PROJECT / "approvals" / "2026-10-21-capability-model-broker-pre.json")

    def test_capabilities_are_operation_scoped(self) -> None:
        capabilities = self.registry["capabilities"]
        self.assertTrue(capabilities)
        keys = {(item["operation"], item["provider_id"], item["environment_host"]) for item in capabilities}
        self.assertEqual(len(keys), len(capabilities))
        self.assertTrue(all(item["ttl_seconds"] > 0 for item in capabilities))

    def test_model_provider_calls_remain_disconnected(self) -> None:
        self.assertFalse(self.policy["provider_calls_connected"])
        self.assertFalse(self.state["laws"]["provider_invocation_authorized"])
        self.assertFalse(self.state["laws"]["execution_authority_granted"])

    def test_owner_precedence_and_fallback_policy_are_locked(self) -> None:
        self.assertEqual(
            self.policy["selection_precedence"],
            [
                "TASK_OVERRIDE",
                "ROLE_OVERRIDE",
                "PROJECT_DEFAULT",
                "GLOBAL_DEFAULT",
            ],
        )
        self.assertFalse(self.policy["silent_fallback_allowed"])
        self.assertEqual(
            self.policy["allowed_fallback_modes"],
            ["Disabled", "ExplicitAllowlist"],
        )

    def test_no_production_model_claims_connected_provider(self) -> None:
        self.assertTrue(all(not model["provider_connected"] for model in self.policy["models"]))

    def test_model_invoke_is_blocked_in_production(self) -> None:
        capability = next(item for item in self.registry["capabilities"] if item["id"] == "model-invoke-external")
        self.assertEqual(capability["health"], "BLOCKED")
        self.assertEqual(capability["authentication_state"], "NOT_CONNECTED")
        self.assertFalse(capability["fallback_eligible"])

    def test_pending_slice_does_not_claim_healthy_model_selection(self) -> None:
        capability = next(item for item in self.registry["capabilities"] if item["id"] == "model-select-local")
        if self.state["status"] == "IMPLEMENTED_VALIDATION_PENDING":
            self.assertEqual(capability["health"], "IN_TEST")
        else:
            self.assertEqual(self.state["status"], "APPROVED_BY_AL_MURTAKAZ")
            self.assertEqual(capability["health"], "HEALTHY")

    def test_slice_is_bound_to_preapproved_baseline(self) -> None:
        self.assertEqual(
            self.state["canonical_base"],
            self.pre["canonical_base"]["sha"],
        )


if __name__ == "__main__":
    unittest.main()
