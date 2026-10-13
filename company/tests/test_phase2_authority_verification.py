import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from company.runtime.execution_controls import ExecutionJournal, HostControllerLease
from company.runtime.hybrid_execution import (
    CouncilVideoStudioGuiAdapter,
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
from company.runtime.tool_authority import capability_currentness

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

    def test_f04_principal_and_action_scope_are_enforced(self):
        planned = plan_action(
            {
                "id": "f04-structured",
                "native_available": True,
                "authority_operation": "github.write",
                "effect": "WRITE",
                "target_repo": "yassenjabal-jpg/UniversalCouncil",
                "authority_scope": "universal_council_repository",
            },
            BASE_CFG,
        )
        with self.assertRaises(HybridExecutionError):
            enforce_tool_authority(planned, BASE_REGISTRY, principal="media_specialist")

        wrong_scope = copy.deepcopy(planned.payload)
        wrong_scope["authority_scope"] = "unrelated_repository"
        wrong_planned = plan_action(wrong_scope, BASE_CFG)
        with self.assertRaises(HybridExecutionError):
            enforce_tool_authority(wrong_planned, BASE_REGISTRY, principal="technical_operator")

        record = enforce_tool_authority(
            planned,
            BASE_REGISTRY,
            principal="technical_operator",
        )
        self.assertEqual(record["operation"], "github.write")

    def test_f05_host_shared_controller_lease_blocks_second_executor(self):
        with tempfile.TemporaryDirectory() as tmp:
            lease_path = Path(tmp) / "controller.lock"
            verified = {
                "state": ResultState.SUCCEEDED.value,
                "verification": {"verified": True, "independent": True, "mode": "test"},
            }
            first = HybridExecutor(
                BASE_CFG,
                gui_adapter=MockAdapter(verified),
                authority_registry=BASE_REGISTRY,
                controller_lease=HostControllerLease(lease_path),
            )
            second_adapter = MockAdapter(verified)
            second = HybridExecutor(
                BASE_CFG,
                gui_adapter=second_adapter,
                authority_registry=BASE_REGISTRY,
                controller_lease=HostControllerLease(lease_path),
            )
            state1 = SharedExecutionState("lease-1")
            result1 = first.execute(
                {"id": "lease-a", "gui_request": {"action": "set_value"}},
                state1,
                requester="technical_operator",
                task_approved=True,
                retain_controller=True,
            )
            self.assertEqual(result1["state"], ResultState.SUCCEEDED.value)

            state2 = SharedExecutionState("lease-2")
            result2 = second.execute(
                {"id": "lease-b", "gui_request": {"action": "set_value"}},
                state2,
                requester="technical_operator",
                task_approved=True,
            )
            self.assertEqual(result2["state"], ResultState.BLOCKED.value)
            self.assertEqual(second_adapter.calls, [])

            state1.release_controller("operator-a")
            first.controller_lease.release("desktop:YASSIN", "technical_operator:lease-1")

    def test_f06_gui_timeout_becomes_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / "bridge/yassin_control/verified_action.py"
            script.parent.mkdir(parents=True)
            script.write_text("print('{}')", encoding="utf-8")
            cfg = copy.deepcopy(BASE_CFG)
            cfg["gui_interaction_plane"]["root_hint"] = str(root)
            adapter = CouncilVideoStudioGuiAdapter(cfg, env={})
            with patch(
                "company.runtime.hybrid_execution.subprocess.run",
                side_effect=subprocess.TimeoutExpired(cmd="gui", timeout=30),
            ):
                result = adapter.dispatch({"gui_request": {"action": "screenshot"}})
            self.assertEqual(result["state"], ResultState.UNKNOWN.value)
            self.assertEqual(result["reason"], "gui_action_timeout")

    def test_f06_pending_journal_intent_requires_reconciliation(self):
        with tempfile.TemporaryDirectory() as tmp:
            journal = ExecutionJournal(Path(tmp) / "journal.jsonl")
            journal.record_intent(
                task_id="journal-task",
                action_id="pending",
                requester="technical_operator",
                path="native_api_or_connector",
                risk=RiskTier.T0.value,
                authority_operation="github.read",
            )
            adapter = MockAdapter({"state": ResultState.SUCCEEDED.value})
            executor = HybridExecutor(
                BASE_CFG,
                native_adapter=adapter,
                authority_registry=BASE_REGISTRY,
                journal=journal,
            )
            result = executor.execute(
                {
                    "id": "pending",
                    "native_available": True,
                    "authority_operation": "github.read",
                },
                SharedExecutionState("journal-task"),
                requester="technical_operator",
                task_approved=True,
            )
            self.assertEqual(result["state"], ResultState.UNKNOWN.value)
            self.assertEqual(adapter.calls, [])

    def test_gui_reversible_actions_are_t1_and_state_change_cannot_be_downgraded(self):
        planned = plan_action(
            {"id": "focus", "gui_request": {"action": "focus"}},
            BASE_CFG,
        )
        self.assertEqual(planned.risk, RiskTier.T1)
        self.assertEqual(planned.payload["effect"], "EXECUTE")
        self.assertFalse(planned.payload["local_state_change"])

        with self.assertRaises(HybridExecutionError):
            plan_action(
                {
                    "id": "downgrade-state",
                    "local_state_change": False,
                    "gui_request": {"action": "set_value"},
                },
                BASE_CFG,
            )

        with self.assertRaises(HybridExecutionError):
            plan_action({"id": "dc-missing-effect", "dc_capable": True}, BASE_CFG)

    def test_authority_missing_target_and_stale_evidence_fail_closed(self):
        no_target = plan_action(
            {
                "id": "no-target",
                "native_available": True,
                "authority_operation": "github.write",
                "effect": "WRITE",
            },
            BASE_CFG,
        )
        with self.assertRaises(HybridExecutionError):
            enforce_tool_authority(no_target, BASE_REGISTRY)

        stale_registry = copy.deepcopy(BASE_REGISTRY)
        read = next(item for item in stale_registry["capabilities"] if item["operation"] == "github.read")
        read["last_verified_at"] = "2000-01-01"
        read_action = plan_action(
            {
                "id": "stale-read",
                "native_available": True,
                "authority_operation": "github.read",
            },
            BASE_CFG,
        )
        with self.assertRaises(HybridExecutionError):
            enforce_tool_authority(read_action, stale_registry)

    def test_executor_requires_requester_and_preserves_unknown_provider_state(self):
        adapter = MockAdapter({"state": ResultState.UNKNOWN.value, "reason": "provider-uncertain"})
        executor = HybridExecutor(
            BASE_CFG,
            native_adapter=adapter,
            authority_registry=BASE_REGISTRY,
        )
        no_requester = executor.execute(
            {
                "id": "no-requester",
                "native_available": True,
                "authority_operation": "github.read",
            },
            SharedExecutionState("requester"),
            requester="",
            task_approved=True,
        )
        self.assertEqual(no_requester["state"], ResultState.BLOCKED.value)
        self.assertEqual(adapter.calls, [])

        unknown = executor.execute(
            {
                "id": "provider-unknown",
                "native_available": True,
                "authority_operation": "github.read",
            },
            SharedExecutionState("unknown"),
            requester="technical_operator",
            task_approved=True,
        )
        self.assertEqual(unknown["state"], ResultState.UNKNOWN.value)

    def test_journal_records_completed_dispatch_and_clears_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            journal = ExecutionJournal(Path(tmp) / "journal.jsonl")
            adapter = MockAdapter({"state": ResultState.SUCCEEDED.value})
            executor = HybridExecutor(
                BASE_CFG,
                native_adapter=adapter,
                authority_registry=BASE_REGISTRY,
                journal=journal,
            )
            result = executor.execute(
                {
                    "id": "journal-success",
                    "native_available": True,
                    "authority_operation": "github.read",
                },
                SharedExecutionState("journal-success-task"),
                requester="technical_operator",
                task_approved=True,
            )
            self.assertEqual(result["state"], ResultState.SUCCEEDED.value)
            self.assertEqual(journal.pending_action_ids(), set())

    def test_batch_host_lease_conflict_fails_before_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "controller.lock"
            blocker = HostControllerLease(path)
            blocker.acquire("desktop:YASSIN", "other")
            adapter = MockAdapter(
                {
                    "state": ResultState.SUCCEEDED.value,
                    "verification": {"verified": True, "independent": True},
                }
            )
            executor = HybridExecutor(
                BASE_CFG,
                gui_adapter=adapter,
                authority_registry=BASE_REGISTRY,
                controller_lease=HostControllerLease(path),
            )
            result = executor.execute_batch(
                [{"id": "batch-conflict", "gui_request": {"action": "click"}}],
                SharedExecutionState("batch-conflict"),
                requester="technical_operator",
                task_approved=True,
            )
            self.assertEqual(result["state"], ResultState.BLOCKED.value)
            self.assertEqual(result["results"], [])
            self.assertEqual(adapter.calls, [])
            blocker.release("desktop:YASSIN", "other")

    def test_f15_stale_capability_evidence_is_not_current(self):
        record = copy.deepcopy(
            next(item for item in BASE_REGISTRY["capabilities"] if item["operation"] == "github.read")
        )
        record["last_verified_at"] = "2000-01-01"
        currentness = capability_currentness(record)
        self.assertFalse(currentness["current"])
        self.assertEqual(currentness["reason"], "stale_capability_evidence")


if __name__ == "__main__":
    unittest.main()
