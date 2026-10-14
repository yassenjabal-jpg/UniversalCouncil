from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from company.runtime.application_profiles import (
    ApplicationProfileError,
    assess_application_request,
    validate_application_profiles,
)
from company.runtime.contribution_ledger import (
    ContributionLedgerError,
    evaluate_role_contribution,
    validate_contribution_config,
)
from company.runtime.council_intelligent_routing import (
    IntelligentRoutingError,
    route_decision,
    validate_routing_candidate,
)
from company.runtime.council_role_contracts import (
    RoleContractError,
    validate_role_contracts,
)
from company.runtime.council_shadow import (
    CouncilShadowError,
    build_shadow_plan,
    synthesize_shadow,
    validate_shadow_config,
)
from company.runtime.execution_contract import (
    ExecutionContractError,
    build_execution_contract,
    build_execution_plan,
    validate_execution_contract_config,
)
from company.runtime.execution_fsm import (
    ExecutionFSMError,
    run_execution_fsm,
    validate_fsm_config,
)
from company.runtime.task_aware_router import (
    TaskAwareRoutingError,
    route_execution,
    validate_task_router_config,
)

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


def valid_contract() -> dict:
    return build_execution_contract(
        {
            "decision_id": "c",
            "what": "Read",
            "why": "Verify",
            "constraints": [],
            "authority": {
                "principal": "technical_operator",
                "operations": ["read"],
                "targets": ["repo"],
                "scopes": ["branch"],
            },
            "blocking_conditions": [],
            "verification_target": "observed",
        },
        EXECUTION_CONTRACT,
    )


class Phase3FailClosedCoverageTests(unittest.TestCase):
    def test_application_profile_validation_failures(self):
        broken = copy.deepcopy(PROFILES)
        broken["status"] = "GOVERNING"
        with self.assertRaises(ApplicationProfileError):
            validate_application_profiles(broken)

        broken = copy.deepcopy(PROFILES)
        broken["profile_growth_policy"] = "AUTO_GROW"
        with self.assertRaises(ApplicationProfileError):
            validate_application_profiles(broken)

        for profiles in (None, {}):
            broken = copy.deepcopy(PROFILES)
            broken["profiles"] = profiles
            with self.subTest(profiles=profiles):
                with self.assertRaises(ApplicationProfileError):
                    validate_application_profiles(broken)

        mutations = [
            lambda p: p.pop("recovery"),
            lambda p: p["application"].update(id="wrong"),
            lambda p: p["version"].update(policy="ASSUME"),
            lambda p: p["apis_scripts"].update(supported_actions=[]),
            lambda p: p["apis_scripts"].update(supported_actions=["x", "x"]),
            lambda p: p.update(task_classes=[]),
            lambda p: p["verification"].update(receipt_status_success="OK"),
            lambda p: p["verification"].update(timeout_seconds=0),
            lambda p: p.update(checkpoint_format={}),
        ]
        for mutate in mutations:
            broken = copy.deepcopy(PROFILES)
            mutate(broken["profiles"]["after_effects"])
            with self.subTest(mutate=mutate):
                with self.assertRaises(ApplicationProfileError):
                    validate_application_profiles(broken)

        broken = copy.deepcopy(PROFILES)
        broken["profiles"]["after_effects"] = "bad"
        with self.assertRaises(ApplicationProfileError):
            validate_application_profiles(broken)

        with self.assertRaises(ApplicationProfileError):
            assess_application_request("missing", {}, PROFILES)
        with self.assertRaises(ApplicationProfileError):
            assess_application_request("after_effects", "bad", PROFILES)
        with self.assertRaises(ApplicationProfileError):
            assess_application_request(
                "after_effects",
                {"detected": False, "version": None, "action": ""},
                PROFILES,
            )
        with self.assertRaises(ApplicationProfileError):
            assess_application_request(
                "after_effects",
                {"detected": "maybe", "version": None, "action": "create_comp"},
                PROFILES,
            )

    def test_contribution_ledger_validation_and_remaining_outcomes(self):
        mutations = [
            lambda c: c.update(status="BAD"),
            lambda c: c.update(use_as_voting_weights=True),
            lambda c: c.update(metrics=[]),
            lambda c: c.update(metrics=c["metrics"] + [c["metrics"][0]]),
            lambda c: c.update(recommendations=["KEEP"]),
            lambda c: c.update(minimum_observations=2),
            lambda c: c.update(remove_minimum_observations=1),
            lambda c: c.update(removal_requires_owner_review=False),
        ]
        for mutate in mutations:
            broken = copy.deepcopy(LEDGER)
            mutate(broken)
            with self.subTest(mutate=mutate):
                with self.assertRaises(ContributionLedgerError):
                    validate_contribution_config(broken)

        with self.assertRaises(ContributionLedgerError):
            evaluate_role_contribution("", [{m: 0 for m in LEDGER["metrics"]}], LEDGER)
        with self.assertRaises(ContributionLedgerError):
            evaluate_role_contribution("role", [], LEDGER)
        with self.assertRaises(ContributionLedgerError):
            evaluate_role_contribution("role", ["bad"], LEDGER)

        bad = {m: 0 for m in LEDGER["metrics"]}
        bad["unique_evidence"] = "one"
        with self.assertRaises(ContributionLedgerError):
            evaluate_role_contribution("role", [bad], LEDGER)
        bad = {m: 0 for m in LEDGER["metrics"]}
        bad["unique_evidence"] = True
        with self.assertRaises(ContributionLedgerError):
            evaluate_role_contribution("role", [bad], LEDGER)

        low = {m: 0 for m in LEDGER["metrics"]}
        result = evaluate_role_contribution("role", [low, low, low], LEDGER)
        self.assertEqual(result["recommendation"], "ON_DEMAND")

        good = {m: 0 for m in LEDGER["metrics"]}
        good["unique_evidence"] = 1
        good["human_override"] = 1
        result = evaluate_role_contribution("role", [good, good, good], LEDGER)
        self.assertIn("human_override_observed", result["reasons"])

    def test_intelligent_router_validation_failures(self):
        mutations = [
            lambda c: c.update(status="BAD"),
            lambda c: c.update(governing_council_version="x"),
            lambda c: c.update(free_text_keyword_routing=True),
            lambda c: c.update(callable_core_capabilities=["synthesis"]),
            lambda c: c.update(callable_core_capabilities=["chair", "unknown"]),
            lambda c: c.update(domain_specialists={}),
            lambda c: c.update(domain_specialists={"x": "unknown"}),
            lambda c: c.update(commercial_mandatory_specialists=["customer_skeptic"]),
            lambda c: c.update(dimensions=["domain"]),
        ]
        for mutate in mutations:
            broken = copy.deepcopy(COUNCIL_ROUTER)
            mutate(broken)
            with self.subTest(mutate=mutate):
                with self.assertRaises(IntelligentRoutingError):
                    validate_routing_candidate(broken, ROLES)

        base = {
            "decision_id": "r",
            "domains": [],
            "materiality": "LOW",
            "uncertainty": "LOW",
            "risk": "LOW",
            "freshness": "LOW",
            "required_capabilities": [],
            "commercial": False,
            "active_domain_blockers": [],
        }
        for field, value in (
            ("decision_id", ""),
            ("materiality", "BAD"),
            ("uncertainty", "BAD"),
            ("risk", "BAD"),
            ("freshness", "BAD"),
            ("domains", "bad"),
            ("required_capabilities", "bad"),
            ("active_domain_blockers", "bad"),
        ):
            with self.subTest(field=field):
                with self.assertRaises(IntelligentRoutingError):
                    route_decision({**base, field: value}, COUNCIL_ROUTER, ROLES)

        with self.assertRaises(IntelligentRoutingError):
            route_decision(
                {**base, "active_domain_blockers": ["unknown"]},
                COUNCIL_ROUTER,
                ROLES,
            )
        with self.assertRaises(IntelligentRoutingError):
            route_decision(
                {**base, "required_capabilities": ["chair"]},
                COUNCIL_ROUTER,
                ROLES,
            )

        freshness = route_decision(
            {**base, "freshness": "HIGH"},
            COUNCIL_ROUTER,
            ROLES,
        )
        self.assertIn("freshness_requirement", freshness["activation_reasons"]["evidence"])

    def test_role_contract_validation_failures(self):
        mutations = [
            lambda c: c.update(status="BAD"),
            lambda c: c.update(governing_council_version="x"),
        ]
        for mutate in mutations:
            broken = copy.deepcopy(ROLE_CONTRACTS)
            mutate(broken)
            with self.assertRaises(RoleContractError):
                validate_role_contracts(broken, ROLES)

        broken = copy.deepcopy(ROLE_CONTRACTS)
        broken["roles"]["chair"] = "bad"
        with self.assertRaises(RoleContractError):
            validate_role_contracts(broken, ROLES)

        broken = copy.deepcopy(ROLE_CONTRACTS)
        broken["roles"]["chair"].pop("mission")
        with self.assertRaises(RoleContractError):
            validate_role_contracts(broken, ROLES)

        broken = copy.deepcopy(ROLE_CONTRACTS)
        broken["roles"]["chair"]["mission"] = None
        with self.assertRaises(RoleContractError):
            validate_role_contracts(broken, ROLES)

        broken = copy.deepcopy(ROLE_CONTRACTS)
        broken["roles"]["chair"]["authority"] = "bad"
        with self.assertRaises(RoleContractError):
            validate_role_contracts(broken, ROLES)

        for flag in ("may_execute_tools", "may_mutate_authority", "may_self_approve"):
            broken = copy.deepcopy(ROLE_CONTRACTS)
            broken["roles"]["chair"]["authority"][flag] = True
            with self.subTest(flag=flag):
                with self.assertRaises(RoleContractError):
                    validate_role_contracts(broken, ROLES)

        broken = copy.deepcopy(ROLE_CONTRACTS)
        broken["roles"]["software"]["blocker_scope"] = "bad"
        with self.assertRaises(RoleContractError):
            validate_role_contracts(broken, ROLES)

        broken = copy.deepcopy(ROLE_CONTRACTS)
        broken["roles"]["software"]["blocker_scope"]["type"] = "invalid"
        with self.assertRaises(RoleContractError):
            validate_role_contracts(broken, ROLES)

        broken = copy.deepcopy(ROLE_CONTRACTS)
        broken["roles"]["software"]["blocker_scope"]["requires_evidence"] = False
        with self.assertRaises(RoleContractError):
            validate_role_contracts(broken, ROLES)

        broken = copy.deepcopy(ROLE_CONTRACTS)
        broken["roles"]["chair"]["merge_remove_trigger"] = "bad"
        with self.assertRaises(RoleContractError):
            validate_role_contracts(broken, ROLES)

        broken = copy.deepcopy(ROLE_CONTRACTS)
        broken["roles"]["chair"]["merge_remove_trigger"]["automatic"] = True
        with self.assertRaises(RoleContractError):
            validate_role_contracts(broken, ROLES)

        broken = copy.deepcopy(ROLE_CONTRACTS)
        broken["roles"]["chair"]["merge_remove_trigger"]["minimum_observation_count"] = 1
        with self.assertRaises(RoleContractError):
            validate_role_contracts(broken, ROLES)

        broken = copy.deepcopy(ROLE_CONTRACTS)
        broken["roles"]["chair"]["merge_remove_trigger"]["signals"] = []
        with self.assertRaises(RoleContractError):
            validate_role_contracts(broken, ROLES)

        broken = copy.deepcopy(ROLE_CONTRACTS)
        broken["roles"]["chair"]["outputs"].append("synthesis")
        with self.assertRaises(RoleContractError):
            validate_role_contracts(broken, ROLES)

        broken = copy.deepcopy(ROLE_CONTRACTS)
        broken["roles"]["chair"]["authority"]["decision_function"] = "synthesize"
        with self.assertRaises(RoleContractError):
            validate_role_contracts(broken, ROLES)

        broken = copy.deepcopy(ROLE_CONTRACTS)
        broken["roles"]["synthesis"]["activation"]["model"] = "agent"
        with self.assertRaises(RoleContractError):
            validate_role_contracts(broken, ROLES)

        for flag in ("may_override_dissent", "may_override_domain_blockers"):
            broken = copy.deepcopy(ROLE_CONTRACTS)
            broken["roles"]["synthesis"]["authority"][flag] = True
            with self.subTest(flag=flag):
                with self.assertRaises(RoleContractError):
                    validate_role_contracts(broken, ROLES)

        broken = copy.deepcopy(ROLE_CONTRACTS)
        broken["roles"]["customer_skeptic"]["activation"]["required_when"] = []
        with self.assertRaises(RoleContractError):
            validate_role_contracts(broken, ROLES)

    def test_council_shadow_validation_failures(self):
        with self.assertRaises(CouncilShadowError):
            validate_shadow_config("bad", ROLES)

        mutations = [
            lambda c: c.update(status="BAD"),
            lambda c: c.update(governing_council_version="x"),
            lambda c: c.update(may_replace_governing_council=True),
            lambda c: c.update(may_execute_tools=True),
            lambda c: c.update(may_mutate_authority=True),
            lambda c: c.update(callable_core_capabilities=[]),
            lambda c: c.update(callable_core_capabilities=["chair", "unknown"]),
            lambda c: c.update(callable_core_capabilities=["chair", "synthesis"]),
            lambda c: c.update(protocol_stages=[]),
            lambda c: c.update(commercial_mandatory_specialists=["customer_skeptic"]),
        ]
        for mutate in mutations:
            broken = copy.deepcopy(SHADOW)
            mutate(broken)
            with self.subTest(mutate=mutate):
                with self.assertRaises(CouncilShadowError):
                    validate_shadow_config(broken, ROLES)

        mutations = [
            lambda c: c["decision_orchestrator"].update(coordinates=["chair", "synthesis"]),
            lambda c: c["decision_orchestrator"].update(protocol_stages=[]),
            lambda c: c["decision_orchestrator"].update(cannot_override_domain_blockers=False),
            lambda c: c["decision_orchestrator"].update(cannot_erase_dissent=False),
        ]
        for mutate in mutations:
            broken = copy.deepcopy(SHADOW)
            mutate(broken)
            with self.assertRaises(CouncilShadowError):
                validate_shadow_config(broken, ROLES)

        with self.assertRaises(CouncilShadowError):
            build_shadow_plan(
                {"decision_id": ""},
                SHADOW,
                ROLES,
                load("config/domain-routing.json"),
            )

        broken = copy.deepcopy(SHADOW)
        broken["status"] = "BAD"
        with self.assertRaises(CouncilShadowError):
            synthesize_shadow({"decision_id": "d"}, broken)

        with self.assertRaises(CouncilShadowError):
            synthesize_shadow({}, SHADOW)

        for field in ("dissent", "domain_blockers", "alternatives"):
            packet = {
                "decision_id": "d",
                "candidate_recommendation": "A",
                "dissent": [],
                "domain_blockers": [],
                "alternatives": [],
            }
            packet[field] = "bad"
            with self.subTest(field=field):
                with self.assertRaises(CouncilShadowError):
                    synthesize_shadow(packet, SHADOW)

    def test_execution_contract_validation_failures(self):
        mutations = [
            lambda c: c.update(status="BAD"),
            lambda c: c.update(council_owns=[]),
            lambda c: c.update(execution_orchestrator_owns=[]),
            lambda c: c.update(execution_orchestrator_owns=c["execution_orchestrator_owns"] + ["what"]),
            lambda c: c.update(execution_orchestrator_is_voting_member=True),
        ]
        for mutate in mutations:
            broken = copy.deepcopy(EXECUTION_CONTRACT)
            mutate(broken)
            with self.assertRaises(ExecutionContractError):
                validate_execution_contract_config(broken)

        with self.assertRaises(ExecutionContractError):
            build_execution_contract("bad", EXECUTION_CONTRACT)

        base = {
            "decision_id": "d",
            "what": "Do",
            "why": "Reason",
            "constraints": [],
            "authority": {
                "principal": "technical_operator",
                "operations": ["read"],
                "targets": ["repo"],
                "scopes": ["branch"],
            },
            "blocking_conditions": [],
            "verification_target": "verified",
        }
        for field, value in (
            ("decision_id", ""),
            ("what", ""),
            ("why", ""),
            ("constraints", "bad"),
            ("blocking_conditions", "bad"),
            ("verification_target", ""),
        ):
            with self.subTest(field=field):
                with self.assertRaises(ExecutionContractError):
                    build_execution_contract({**base, field: value}, EXECUTION_CONTRACT)

        missing = copy.deepcopy(base)
        missing.pop("why")
        with self.assertRaises(ExecutionContractError):
            build_execution_contract(missing, EXECUTION_CONTRACT)

        authority_cases = [
            "bad",
            {"principal": "", "operations": ["read"], "targets": ["repo"], "scopes": ["branch"]},
            {"principal": "p", "operations": [], "targets": ["repo"], "scopes": ["branch"]},
            {"principal": "p", "operations": [""], "targets": ["repo"], "scopes": ["branch"]},
        ]
        for authority in authority_cases:
            with self.subTest(authority=authority):
                with self.assertRaises(ExecutionContractError):
                    build_execution_contract({**base, "authority": authority}, EXECUTION_CONTRACT)

        blockers = copy.deepcopy(base)
        blockers["blocking_conditions"] = ["bad"]
        with self.assertRaises(ExecutionContractError):
            build_execution_contract(blockers, EXECUTION_CONTRACT)

        contract = valid_contract()
        with self.assertRaises(ExecutionContractError):
            build_execution_plan(contract, "bad", EXECUTION_CONTRACT)

        incomplete = {
            "how": "x",
            "where": "x",
            "tool": "x",
            "route": "x",
            "recovery": "x",
            "verification_method": "x",
            "operation": "read",
            "target": "repo",
        }
        with self.assertRaises(ExecutionContractError):
            build_execution_plan(contract, incomplete, EXECUTION_CONTRACT)

        empty = {
            "how": "",
            "where": "x",
            "tool": "x",
            "route": "x",
            "recovery": "x",
            "verification_method": "x",
            "operation": "read",
            "target": "repo",
            "scope": "branch",
        }
        with self.assertRaises(ExecutionContractError):
            build_execution_plan(contract, empty, EXECUTION_CONTRACT)

    def test_execution_fsm_validation_failures(self):
        mutations = [
            lambda c: c.update(status="BAD"),
            lambda c: c.update(verification_required=False),
            lambda c: c.update(checkpoint_required=False),
            lambda c: c.update(success_path=[]),
            lambda c: c.update(failure_path=[]),
            lambda c: c.update(max_recovery_attempts=-1),
            lambda c: c.update(transitions=None),
        ]
        for mutate in mutations:
            broken = copy.deepcopy(FSM)
            mutate(broken)
            with self.assertRaises(ExecutionFSMError):
                validate_fsm_config(broken)

        valid_plan = {
            "route": "native_api",
            "route_reason": "reason",
            "route_version": "v",
            "authority": {"operation": "read", "target": "repo", "scope": "branch"},
        }

        with self.assertRaises(ExecutionFSMError):
            run_execution_fsm(
                observer=lambda: "bad",
                planner=lambda obs: valid_plan,
                actor=lambda plan: {"state": "SUCCEEDED"},
                verifier=lambda result: {"verified": True},
                diagnoser=lambda result: {},
                recoverer=lambda diagnosis: {"state": "SUCCEEDED"},
                checkpointer=lambda verified: {"durable": True},
                cfg=FSM,
            )

        with self.assertRaises(ExecutionFSMError):
            run_execution_fsm(
                observer=lambda: {},
                planner=lambda obs: "bad",
                actor=lambda plan: {"state": "SUCCEEDED"},
                verifier=lambda result: {"verified": True},
                diagnoser=lambda result: {},
                recoverer=lambda diagnosis: {"state": "SUCCEEDED"},
                checkpointer=lambda verified: {"durable": True},
                cfg=FSM,
            )

        with self.assertRaises(ExecutionFSMError):
            run_execution_fsm(
                observer=lambda: {},
                planner=lambda obs: {
                    **valid_plan,
                    "authority": {"operation": "", "target": "repo", "scope": "branch"},
                },
                actor=lambda plan: {"state": "SUCCEEDED"},
                verifier=lambda result: {"verified": True},
                diagnoser=lambda result: {},
                recoverer=lambda diagnosis: {"state": "SUCCEEDED"},
                checkpointer=lambda verified: {"durable": True},
                cfg=FSM,
            )

        with self.assertRaises(ExecutionFSMError):
            run_execution_fsm(
                observer=lambda: {},
                planner=lambda obs: valid_plan,
                actor=lambda plan: "bad",
                verifier=lambda result: {"verified": True},
                diagnoser=lambda result: {},
                recoverer=lambda diagnosis: {"state": "SUCCEEDED"},
                checkpointer=lambda verified: {"durable": True},
                cfg=FSM,
            )

        with self.assertRaises(ExecutionFSMError):
            run_execution_fsm(
                observer=lambda: {},
                planner=lambda obs: valid_plan,
                actor=lambda plan: {"state": "SUCCEEDED"},
                verifier=lambda result: "bad",
                diagnoser=lambda result: {},
                recoverer=lambda diagnosis: {"state": "SUCCEEDED"},
                checkpointer=lambda verified: {"durable": True},
                cfg=FSM,
            )

        with self.assertRaises(ExecutionFSMError):
            run_execution_fsm(
                observer=lambda: {},
                planner=lambda obs: valid_plan,
                actor=lambda plan: {"state": "FAILED"},
                verifier=lambda result: {"verified": False},
                diagnoser=lambda result: "bad",
                recoverer=lambda diagnosis: {"state": "SUCCEEDED"},
                checkpointer=lambda verified: {"durable": True},
                cfg=FSM,
            )

        with self.assertRaises(ExecutionFSMError):
            run_execution_fsm(
                observer=lambda: {},
                planner=lambda obs: valid_plan,
                actor=lambda plan: {"state": "FAILED"},
                verifier=lambda result: {"verified": False},
                diagnoser=lambda result: {},
                recoverer=lambda diagnosis: "bad",
                checkpointer=lambda verified: {"durable": True},
                cfg=FSM,
            )

        with self.assertRaises(ExecutionFSMError):
            run_execution_fsm(
                observer=lambda: {},
                planner=lambda obs: valid_plan,
                actor=lambda plan: {"state": "FAILED"},
                verifier=lambda result: "bad",
                diagnoser=lambda result: {},
                recoverer=lambda diagnosis: {"state": "SUCCEEDED"},
                checkpointer=lambda verified: {"durable": True},
                cfg=FSM,
            )

    def test_task_router_validation_failures(self):
        mutations = [
            lambda c: c.update(status="BAD"),
            lambda c: c.update(task_classes={}),
            lambda c: c["task_classes"]["host_work"].update(order=[]),
            lambda c: c["task_classes"]["host_work"].update(order=["dc_control_plane", "dc_control_plane"]),
            lambda c: c.update(route_version=""),
            lambda c: c.update(fallback_restrictions=[]),
        ]
        for mutate in mutations:
            broken = copy.deepcopy(TASK_ROUTER)
            mutate(broken)
            with self.assertRaises(TaskAwareRoutingError):
                validate_task_router_config(broken)

        contract = valid_contract()
        base = {
            "task_class": "external_service",
            "operation": "read",
            "target": "repo",
            "scope": "branch",
            "available_routes": ["authorized_connector_api", "gui_semantic_uia"],
            "authorized_routes": ["authorized_connector_api"],
        }
        with self.assertRaises(TaskAwareRoutingError):
            route_execution("bad", contract, TASK_ROUTER)
        with self.assertRaises(TaskAwareRoutingError):
            route_execution({**base, "task_class": "bad"}, contract, TASK_ROUTER)
        with self.assertRaises(TaskAwareRoutingError):
            route_execution({**base, "available_routes": "bad"}, contract, TASK_ROUTER)

        bad_contract = copy.deepcopy(contract)
        bad_contract["execution_ready"] = False
        with self.assertRaises(TaskAwareRoutingError):
            route_execution(base, bad_contract, TASK_ROUTER)

        bad_contract = copy.deepcopy(contract)
        bad_contract["authority"] = None
        with self.assertRaises(TaskAwareRoutingError):
            route_execution(base, bad_contract, TASK_ROUTER)

        recovery = {
            "task_class": "recovery",
            "operation": "read",
            "target": "repo",
            "scope": "branch",
            "available_routes": ["gui_semantic_uia"],
            "authorized_routes": ["gui_semantic_uia"],
        }
        with self.assertRaises(TaskAwareRoutingError):
            route_execution(recovery, contract, TASK_ROUTER)
        with self.assertRaises(TaskAwareRoutingError):
            route_execution(
                {
                    **recovery,
                    "recovery": {
                        "inspected": True,
                        "diagnosed": True,
                        "approved_alternate_routes": [],
                    },
                },
                contract,
                TASK_ROUTER,
            )
        with self.assertRaises(TaskAwareRoutingError):
            route_execution(
                {
                    **recovery,
                    "recovery": {
                        "inspected": True,
                        "diagnosed": True,
                        "approved_alternate_routes": ["visual_grounding"],
                    },
                },
                contract,
                TASK_ROUTER,
            )

        unavailable = route_execution(
            {
                **base,
                "available_routes": ["gui_semantic_uia"],
                "authorized_routes": ["gui_semantic_uia"],
            },
            contract,
            TASK_ROUTER,
        )
        self.assertIn("preferred_route_unavailable", unavailable["fallback_reasons"])


if __name__ == "__main__":
    unittest.main()
