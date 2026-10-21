from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "state" / "command-center"
PROJECT = STATE / "project-governance"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class CommandCenterGatewayRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = load(STATE / "gateway-routing-policy.json")
        cls.state = load(STATE / "gateway-routing-state.json")
        cls.pre = load(PROJECT / "approvals" / "2026-10-21-gateway-routing-pre.json")

    def test_gateway_is_shadow_planning_only(self) -> None:
        self.assertEqual(self.policy["status"], "SHADOW_PLANNING_ONLY")
        self.assertFalse(self.policy["live_dispatch_allowed"])
        self.assertFalse(self.policy["free_text_intent_inference_allowed"])
        self.assertFalse(self.policy["llm_route_proposal_connected"])

    def test_routing_has_eight_explicit_stages(self) -> None:
        self.assertEqual(
            self.policy["stage_order"],
            [
                "intent",
                "project_context",
                "authority_risk",
                "skill",
                "reasoning_path",
                "model",
                "execution",
                "verification",
            ],
        )

    def test_future_services_are_not_fabricated(self) -> None:
        self.assertEqual(
            set(self.policy["future_dependencies"].values()),
            {"NOT_IMPLEMENTED"},
        )

    def test_owner_approval_is_not_execution_authority(self) -> None:
        laws = self.state["laws"]
        self.assertTrue(laws["approval_is_not_execution_authority"])
        self.assertFalse(laws["execution_authorized"])
        self.assertFalse(laws["live_dispatch_allowed"])

    def test_gateway_does_not_dispatch_execution(self) -> None:
        self.assertTrue(self.state["laws"]["gateway_does_not_call_execution_fabric"])
        execution = self.policy["execution_policy"]
        self.assertFalse(execution["write_dispatch_allowed"])
        self.assertFalse(execution["execute_dispatch_allowed"])

    def test_gateway_is_bound_to_preapproved_baseline(self) -> None:
        self.assertEqual(self.state["canonical_base"], self.pre["canonical_base"]["sha"])

    def test_model_and_skill_dependencies_remain_explicit(self) -> None:
        components = self.state["components"]
        self.assertEqual(components["model_broker"], "NOT_IMPLEMENTED")
        self.assertEqual(components["skill_registry"], "NOT_IMPLEMENTED")
        self.assertEqual(components["capability_registry"], "NOT_IMPLEMENTED")
        self.assertEqual(components["job_engine"], "NOT_IMPLEMENTED")


if __name__ == "__main__":
    unittest.main()
