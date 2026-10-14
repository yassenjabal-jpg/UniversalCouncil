from __future__ import annotations

import json
import unittest
from pathlib import Path

from company.runtime.application_profiles import assess_application_request
from company.runtime.contribution_ledger import evaluate_role_contribution
from company.runtime.council_intelligent_routing import route_decision
from company.runtime.council_role_contracts import validate_role_contracts
from company.runtime.council_shadow import synthesize_shadow, validate_shadow_config
from company.runtime.execution_contract import build_execution_contract
from company.runtime.execution_fsm import run_execution_fsm
from company.runtime.task_aware_router import route_execution

ROOT = Path(__file__).resolve().parents[2]


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


ROLES = load("config/roles.json")
SHADOW = load("company/config/council_shadow.json")
ROLE_CONTRACTS = load("company/config/council_role_contracts.json")
COUNCIL_ROUTER = load("company/config/council_routing_candidate.json")
LEDGER = load("company/config/contribution_ledger.json")
EXECUTION_CONTRACT = load("company/config/execution_contract.json")
TASK_ROUTER = load("company/config/task_aware_router.json")
PROFILES = load("company/config/application_profiles.json")
FSM = load("company/config/execution_fsm.json")


class Phase3ArchitectureGateTests(unittest.TestCase):
    def test_v03_remains_governing_and_candidate_reduces_chair_synthesis_overlap(self):
        self.assertEqual(ROLES["version"], "0.3.0")
        self.assertTrue(validate_shadow_config(SHADOW, ROLES))
        self.assertTrue(validate_role_contracts(ROLE_CONTRACTS, ROLES))
        self.assertEqual(SHADOW["status"], "CANDIDATE_SHADOW_ONLY")
        self.assertNotIn("synthesis", ROLE_CONTRACTS["roles"]["chair"]["outputs"])
        self.assertEqual(
            ROLE_CONTRACTS["roles"]["synthesis"]["activation"]["model"],
            "protocol_stage",
        )

    def test_intelligent_activation_preserves_commercial_specialists_and_blockers(self):
        route = route_decision(
            {
                "decision_id": "commercial-gate",
                "domains": ["business"],
                "materiality": "MATERIAL",
                "uncertainty": "HIGH",
                "risk": "MEDIUM",
                "freshness": "HIGH",
                "required_capabilities": ["value", "human"],
                "commercial": True,
                "active_domain_blockers": ["security"],
            },
            COUNCIL_ROUTER,
            ROLES,
        )
        self.assertIn("customer_skeptic", route["specialists"])
        self.assertIn("moat_auditor", route["specialists"])
        self.assertIn("security", route["specialists"])
        self.assertIn("active_domain_blocker", route["activation_reasons"]["security"])

        synthesis = synthesize_shadow(
            {
                "decision_id": "commercial-gate",
                "candidate_recommendation": "OPTION_A",
                "alternatives": ["OPTION_A", "OPTION_B"],
                "dissent": [{"role": "redteam", "position": "OPTION_B"}],
                "domain_blockers": [
                    {
                        "specialist": "security",
                        "blocker_id": "SEC-1",
                        "status": "OPEN",
                        "authority_scope": "security",
                    }
                ],
            },
            SHADOW,
        )
        self.assertTrue(synthesis["minority_preserved"])
        self.assertEqual(synthesis["domain_blockers"][0]["blocker_id"], "SEC-1")

    def test_decision_execution_route_and_fsm_form_bounded_pipeline(self):
        contract = build_execution_contract(
            {
                "decision_id": "pipeline",
                "what": "Apply bounded document update",
                "why": "Approved implementation",
                "constraints": ["no main modification"],
                "authority": {
                    "principal": "technical_operator",
                    "operations": ["edit"],
                    "targets": ["app"],
                    "scopes": ["document"],
                },
                "blocking_conditions": [],
                "verification_target": "document updated and verified",
            },
            EXECUTION_CONTRACT,
        )
        route = route_execution(
            {
                "task_class": "structured_application",
                "operation": "edit",
                "target": "app",
                "scope": "document",
                "available_routes": ["native_api", "semantic_uia"],
                "authorized_routes": ["native_api", "semantic_uia"],
            },
            contract,
            TASK_ROUTER,
        )
        result = run_execution_fsm(
            observer=lambda: {"target": "old"},
            planner=lambda observation: route,
            actor=lambda plan: {"state": "SUCCEEDED", "target": "new"},
            verifier=lambda execution: {
                "verified": execution.get("target") == "new",
                "target_state": execution.get("target"),
            },
            diagnoser=lambda execution: {"cause": "unexpected"},
            recoverer=lambda diagnosis: {"state": "FAILED"},
            checkpointer=lambda verified: {"durable": True, "checkpoint_id": "cp-gate"},
            cfg=FSM,
        )
        self.assertEqual(result["status"], "VERIFIED_SUCCESS")
        self.assertEqual(result["history"][-2:], ["CHECKPOINT", "COMPLETE"])
        self.assertEqual(result["plan"]["authority"]["operation"], "edit")
        self.assertEqual(result["plan"]["authority"]["target"], "app")
        self.assertEqual(result["plan"]["authority"]["scope"], "document")

    def test_fallback_cannot_expand_authority(self):
        contract = build_execution_contract(
            {
                "decision_id": "no-escalation",
                "what": "Read bounded repo",
                "why": "Inspect state",
                "constraints": [],
                "authority": {
                    "principal": "technical_operator",
                    "operations": ["read"],
                    "targets": ["repo"],
                    "scopes": ["branch"],
                },
                "blocking_conditions": [],
                "verification_target": "state observed",
            },
            EXECUTION_CONTRACT,
        )
        route = route_execution(
            {
                "task_class": "external_service",
                "operation": "read",
                "target": "repo",
                "scope": "branch",
                "available_routes": ["authorized_connector_api", "gui_semantic_uia"],
                "authorized_routes": ["gui_semantic_uia"],
            },
            contract,
            TASK_ROUTER,
        )
        self.assertEqual(route["route"], "gui_semantic_uia")
        self.assertEqual(route["authority"]["operation"], "read")
        self.assertEqual(route["authority"]["target"], "repo")
        self.assertEqual(route["authority"]["scope"], "branch")
        self.assertIn("no_authority_expansion", route["fallback_restrictions"])

    def test_first_application_profile_adds_value_before_profile_growth(self):
        self.assertEqual(list(PROFILES["profiles"]), ["after_effects"])
        assessment = assess_application_request(
            "after_effects",
            {"detected": False, "version": None, "action": "create_comp"},
            PROFILES,
        )
        self.assertFalse(assessment["control_allowed"])
        self.assertTrue(assessment["profile_added_value"])
        self.assertEqual(assessment["next_step"], "detect_or_install")

    def test_contribution_ledger_remains_advisory_not_voting(self):
        observation = {
            "unique_evidence": 1,
            "unique_objection": 1,
            "option_added": 0,
            "test_changed": 1,
            "decision_changed": 0,
            "duplicate_reasoning": 0,
            "false_blocker": 0,
            "missed_blocker": 0,
            "latency_ms": 100,
            "cost_units": 1,
            "human_override": 0,
        }
        result = evaluate_role_contribution("redteam", [observation] * 3, LEDGER)
        self.assertEqual(result["recommendation"], "KEEP")
        self.assertFalse(result["use_as_voting_weight"])


if __name__ == "__main__":
    unittest.main()
