import copy
import json
import unittest
from pathlib import Path

from company.runtime.hybrid_execution import (
    HybridExecutionError,
    HybridExecutor,
    PassthroughVerifier,
    ResultState,
    RiskTier,
    SharedExecutionState,
    enforce_tool_authority,
    plan_action,
)
from company.runtime.hybrid_verification import GuiPostStateVerifier

ROOT = Path(__file__).resolve().parents[2]
BASE_CFG = json.loads((ROOT / "company/config/hybrid_execution.json").read_text(encoding="utf-8"))
BASE_REGISTRY = json.loads((ROOT / "company/config/tool_authority.json").read_text(encoding="utf-8"))


class MockAdapter:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def dispatch(self, action):
        self.calls.append(copy.deepcopy(action))
        return copy.deepcopy(self.result)


def bridge_result(stdout: str):
    return {
        "state": ResultState.SUCCEEDED.value,
        "bridge_result": {"action": {"stdout": stdout}},
    }


class Phase2AuthorityVerificationReproductionTests(unittest.TestCase):
    def test_f01_gui_set_value_derives_state_change_risk_from_trusted_operation(self):
        planned = plan_action(
            {"id": "f01", "gui_request": {"action": "set_value"}},
            BASE_CFG,
        )
        self.assertEqual(planned.risk, RiskTier.T2)
        self.assertTrue(planned.requires_verification)

    def test_f01_caller_cannot_downgrade_gui_control_effect(self):
        with self.assertRaises(HybridExecutionError):
            plan_action(
                {
                    "id": "f01-downgrade",
                    "effect": "READ",
                    "gui_request": {"action": "set_value"},
                },
                BASE_CFG,
            )

    def test_f02_empty_gui_postcondition_is_not_verified(self):
        verifier = GuiPostStateVerifier(MockAdapter(bridge_result("{}")))
        result = verifier.verify(
            {
                "verify": {
                    "request": {"action": "get_value", "selector": "doc"},
                    "expect": {},
                }
            },
            {},
        )
        self.assertFalse(result["verified"])

    def test_f03_provider_success_is_not_independent_verification(self):
        verifier = PassthroughVerifier()
        result = verifier.verify(
            {"id": "f03"},
            {"state": ResultState.SUCCEEDED.value},
        )
        self.assertFalse(result["verified"])

    def test_f04_missing_authority_registry_fails_closed_before_dispatch(self):
        adapter = MockAdapter({"state": ResultState.SUCCEEDED.value})
        executor = HybridExecutor(BASE_CFG, gui_adapter=adapter)
        state = SharedExecutionState("f04")
        result = executor.execute(
            {
                "id": "f04",
                "effect": "WRITE",
                "local_state_change": True,
                "gui_request": {"action": "set_value"},
            },
            state,
            requester="technical_operator",
            task_approved=True,
        )
        self.assertEqual(result["state"], ResultState.BLOCKED.value)
        self.assertEqual(adapter.calls, [])

    def test_f04_structured_target_constraint_is_enforced(self):
        registry = copy.deepcopy(BASE_REGISTRY)
        record = next(item for item in registry["capabilities"] if item["operation"] == "github.write")
        record["allowed_targets"] = ["yassenjabal-jpg/UniversalCouncil"]
        planned = plan_action(
            {
                "id": "f04-target",
                "native_available": True,
                "authority_operation": "github.write",
                "effect": "WRITE",
                "target_repo": "someone-else/private",
            },
            BASE_CFG,
        )
        with self.assertRaises(HybridExecutionError):
            enforce_tool_authority(planned, registry)


if __name__ == "__main__":
    unittest.main()
