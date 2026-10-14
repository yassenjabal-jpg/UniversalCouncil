from __future__ import annotations

import json
import unittest
from pathlib import Path

from company.runtime.execution_fsm import (
    ExecutionFSMError,
    FSMState,
    run_execution_fsm,
    validate_fsm_config,
    validate_transition,
)

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "company/config/execution_fsm.json").read_text(encoding="utf-8"))


class Phase3R16ExecutionFSMTests(unittest.TestCase):
    def test_config_uses_canonical_paths(self):
        self.assertTrue(validate_fsm_config(CFG))
        self.assertEqual(
            CFG["success_path"],
            ["OBSERVE", "PLAN", "ACT", "VERIFY", "CHECKPOINT", "COMPLETE"],
        )
        self.assertEqual(
            CFG["failure_path"],
            ["DIAGNOSE", "RECOVER", "VERIFY"],
        )
        self.assertTrue(CFG["verification_required"])
        self.assertTrue(CFG["checkpoint_required"])

    def test_happy_path_requires_verify_and_checkpoint(self):
        result = run_execution_fsm(
            observer=lambda: {"window": "ready"},
            planner=lambda obs: {
                "route": "native_api",
                "route_reason": "structured application operation",
                "route_version": "task-aware-0.1",
                "authority": {"operation": "edit", "target": "app", "scope": "doc"},
            },
            actor=lambda plan: {"state": "SUCCEEDED", "provider_result": "ok"},
            verifier=lambda result: {
                "verified": True,
                "target_state": {"saved": True},
            },
            diagnoser=lambda result: {"cause": "unused"},
            recoverer=lambda diagnosis: {"state": "SUCCEEDED"},
            checkpointer=lambda verified: {
                "durable": True,
                "checkpoint_id": "cp-1",
            },
            cfg=CFG,
        )
        self.assertEqual(result["status"], "VERIFIED_SUCCESS")
        self.assertEqual(result["final_state"], "COMPLETE")
        self.assertEqual(
            result["history"],
            ["OBSERVE", "PLAN", "ACT", "VERIFY", "CHECKPOINT", "COMPLETE"],
        )
        self.assertTrue(result["verified"])
        self.assertTrue(result["checkpointed"])

    def test_provider_success_without_verification_is_not_success(self):
        result = run_execution_fsm(
            observer=lambda: {"ready": True},
            planner=lambda obs: {
                "route": "semantic_uia",
                "route_reason": "interactive semantic route",
                "route_version": "task-aware-0.1",
                "authority": {"operation": "edit", "target": "app", "scope": "doc"},
            },
            actor=lambda plan: {"state": "SUCCEEDED"},
            verifier=lambda result: {"verified": False},
            diagnoser=lambda result: {"cause": "postcondition_missing"},
            recoverer=lambda diagnosis: {"state": "FAILED", "safe": False},
            checkpointer=lambda verified: {"durable": True},
            cfg=CFG,
        )
        self.assertNotEqual(result["status"], "VERIFIED_SUCCESS")
        self.assertIn("DIAGNOSE", result["history"])
        self.assertIn(result["final_state"], {"ESCALATE", "DIAGNOSE"})

    def test_unknown_result_enters_diagnose_and_never_counts_as_success(self):
        result = run_execution_fsm(
            observer=lambda: {"ready": True},
            planner=lambda obs: {
                "route": "semantic_uia",
                "route_reason": "interactive semantic route",
                "route_version": "task-aware-0.1",
                "authority": {"operation": "edit", "target": "app", "scope": "doc"},
            },
            actor=lambda plan: {"state": "UNKNOWN", "reason": "timeout"},
            verifier=lambda result: {"verified": False},
            diagnoser=lambda result: {"cause": "unknown_outcome"},
            recoverer=lambda diagnosis: {"state": "UNKNOWN"},
            checkpointer=lambda verified: {"durable": True},
            cfg=CFG,
        )
        self.assertEqual(result["status"], "ESCALATED")
        self.assertFalse(result["verified"])
        self.assertNotIn("COMPLETE", result["history"])
        self.assertIn("DIAGNOSE", result["history"])

    def test_recovery_can_succeed_only_after_reverification_and_checkpoint(self):
        verifications = iter(
            [
                {"verified": False},
                {"verified": True, "target_state": {"saved": True}},
            ]
        )
        result = run_execution_fsm(
            observer=lambda: {"ready": True},
            planner=lambda obs: {
                "route": "semantic_uia",
                "route_reason": "interactive route",
                "route_version": "task-aware-0.1",
                "authority": {"operation": "edit", "target": "app", "scope": "doc"},
            },
            actor=lambda plan: {"state": "FAILED", "reason": "modal"},
            verifier=lambda result: next(verifications),
            diagnoser=lambda result: {"cause": "modal_dialog"},
            recoverer=lambda diagnosis: {"state": "SUCCEEDED", "recovered": True},
            checkpointer=lambda verified: {
                "durable": True,
                "checkpoint_id": "cp-recovered",
            },
            cfg=CFG,
        )
        self.assertEqual(result["status"], "VERIFIED_SUCCESS")
        self.assertIn("RECOVER", result["history"])
        self.assertGreaterEqual(result["history"].count("VERIFY"), 1)
        self.assertEqual(result["history"][-2:], ["CHECKPOINT", "COMPLETE"])

    def test_nondurable_checkpoint_prevents_complete(self):
        result = run_execution_fsm(
            observer=lambda: {"ready": True},
            planner=lambda obs: {
                "route": "native_api",
                "route_reason": "structured route",
                "route_version": "task-aware-0.1",
                "authority": {"operation": "edit", "target": "app", "scope": "doc"},
            },
            actor=lambda plan: {"state": "SUCCEEDED"},
            verifier=lambda result: {"verified": True},
            diagnoser=lambda result: {"cause": "unused"},
            recoverer=lambda diagnosis: {"state": "SUCCEEDED"},
            checkpointer=lambda verified: {"durable": False},
            cfg=CFG,
        )
        self.assertEqual(result["status"], "CHECKPOINT_FAILED")
        self.assertEqual(result["final_state"], "CHECKPOINT")
        self.assertNotIn("COMPLETE", result["history"])

    def test_plan_requires_route_explainability_and_authority(self):
        for plan in (
            {"route": "native_api", "route_version": "v", "authority": {}},
            {"route": "native_api", "route_reason": "r", "authority": {}},
            {"route": "native_api", "route_reason": "r", "route_version": "v"},
        ):
            with self.subTest(plan=plan):
                with self.assertRaises(ExecutionFSMError):
                    run_execution_fsm(
                        observer=lambda: {},
                        planner=lambda obs, plan=plan: plan,
                        actor=lambda plan: {"state": "SUCCEEDED"},
                        verifier=lambda result: {"verified": True},
                        diagnoser=lambda result: {},
                        recoverer=lambda diagnosis: {"state": "SUCCEEDED"},
                        checkpointer=lambda verified: {"durable": True},
                        cfg=CFG,
                    )

    def test_illegal_state_transition_is_rejected(self):
        with self.assertRaises(ExecutionFSMError):
            validate_transition(FSMState.OBSERVE, FSMState.ACT, CFG)
        with self.assertRaises(ExecutionFSMError):
            validate_transition(FSMState.ACT, FSMState.COMPLETE, CFG)


if __name__ == "__main__":
    unittest.main()
