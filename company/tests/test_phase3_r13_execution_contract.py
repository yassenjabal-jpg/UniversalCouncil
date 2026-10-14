from __future__ import annotations

import json
import unittest
from pathlib import Path

from company.runtime.execution_contract import (
    ExecutionContractError,
    build_execution_contract,
    build_execution_plan,
    validate_execution_contract_config,
)

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "company/config/execution_contract.json").read_text(encoding="utf-8"))


class Phase3R13DecisionExecutionSeparationTests(unittest.TestCase):
    def test_config_separates_council_and_execution_orchestrator_ownership(self):
        self.assertTrue(validate_execution_contract_config(CFG))
        self.assertEqual(
            set(CFG["council_owns"]),
            {"what", "why", "constraints", "authority", "blocking_conditions", "verification_target"},
        )
        self.assertEqual(
            set(CFG["execution_orchestrator_owns"]),
            {"how", "where", "tool", "route", "recovery", "verification_method"},
        )
        self.assertFalse(CFG["execution_orchestrator_is_voting_member"])

    def test_council_contract_contains_what_why_constraints_authority_only(self):
        contract = build_execution_contract(
            {
                "decision_id": "d1",
                "what": "Apply bounded configuration change",
                "why": "Reduce operator burden",
                "constraints": ["no main modification"],
                "authority": {
                    "principal": "technical_operator",
                    "operations": ["github.write"],
                    "targets": ["yassenjabal-jpg/UniversalCouncil"],
                    "scopes": ["phase3_branch"],
                },
                "blocking_conditions": [],
                "verification_target": "tests green and target config updated",
            },
            CFG,
        )
        self.assertTrue(contract["execution_ready"])
        for forbidden in ("how", "where", "tool", "route", "recovery", "verification_method"):
            self.assertNotIn(forbidden, contract)

    def test_council_cannot_preselect_tool_or_route(self):
        base = {
            "decision_id": "d2",
            "what": "Change config",
            "why": "Need bounded update",
            "constraints": [],
            "authority": {
                "principal": "technical_operator",
                "operations": ["github.write"],
                "targets": ["repo"],
                "scopes": ["branch"],
            },
            "blocking_conditions": [],
            "verification_target": "tests pass",
        }
        for field, value in (("tool", "github"), ("route", "api"), ("how", "edit json")):
            with self.subTest(field=field):
                with self.assertRaises(ExecutionContractError):
                    build_execution_contract({**base, field: value}, CFG)

    def test_unresolved_blocker_makes_contract_not_execution_ready(self):
        contract = build_execution_contract(
            {
                "decision_id": "blocked",
                "what": "Deploy",
                "why": "Production need",
                "constraints": [],
                "authority": {
                    "principal": "technical_operator",
                    "operations": ["deploy"],
                    "targets": ["prod"],
                    "scopes": ["service-a"],
                },
                "blocking_conditions": [
                    {
                        "blocker_id": "SEC-1",
                        "status": "OPEN",
                        "authority_scope": "security",
                    }
                ],
                "verification_target": "healthy deployment",
            },
            CFG,
        )
        self.assertFalse(contract["execution_ready"])
        with self.assertRaises(ExecutionContractError):
            build_execution_plan(
                contract,
                {
                    "how": "deploy script",
                    "where": "prod",
                    "tool": "approved_gateway",
                    "route": "native",
                    "operation": "deploy",
                    "target": "prod",
                    "scope": "service-a",
                    "recovery": "rollback",
                    "verification_method": "health check",
                },
                CFG,
            )

    def test_execution_orchestrator_cannot_expand_operation_target_or_scope(self):
        contract = build_execution_contract(
            {
                "decision_id": "bounded",
                "what": "Update one branch",
                "why": "Implement approved change",
                "constraints": ["no merge"],
                "authority": {
                    "principal": "technical_operator",
                    "operations": ["github.write"],
                    "targets": ["repo"],
                    "scopes": ["phase3_branch"],
                },
                "blocking_conditions": [],
                "verification_target": "tests pass",
            },
            CFG,
        )
        base_plan = {
            "how": "update file",
            "where": "repo",
            "tool": "github_connector",
            "route": "native_api",
            "operation": "github.write",
            "target": "repo",
            "scope": "phase3_branch",
            "recovery": "revert commit",
            "verification_method": "tests",
        }
        plan = build_execution_plan(contract, base_plan, CFG)
        self.assertFalse(plan["voting_member"])
        self.assertEqual(plan["decision_id"], "bounded")

        for field, value in (
            ("operation", "github.merge"),
            ("target", "other-repo"),
            ("scope", "main"),
        ):
            with self.subTest(field=field):
                with self.assertRaises(ExecutionContractError):
                    build_execution_plan(contract, {**base_plan, field: value}, CFG)

    def test_execution_orchestrator_cannot_change_why_or_constraints(self):
        contract = build_execution_contract(
            {
                "decision_id": "immutable",
                "what": "Run test",
                "why": "Verify behavior",
                "constraints": ["read-only"],
                "authority": {
                    "principal": "technical_operator",
                    "operations": ["test.run"],
                    "targets": ["YASSIN"],
                    "scopes": ["worktree"],
                },
                "blocking_conditions": [],
                "verification_target": "test pass",
            },
            CFG,
        )
        for forbidden in ("why", "constraints", "authority"):
            with self.subTest(forbidden=forbidden):
                proposal = {
                    "how": "python unittest",
                    "where": "YASSIN",
                    "tool": "remote_shell",
                    "route": "host",
                    "operation": "test.run",
                    "target": "YASSIN",
                    "scope": "worktree",
                    "recovery": "stop",
                    "verification_method": "exit code plus test report",
                    forbidden: "override",
                }
                with self.assertRaises(ExecutionContractError):
                    build_execution_plan(contract, proposal, CFG)


if __name__ == "__main__":
    unittest.main()
