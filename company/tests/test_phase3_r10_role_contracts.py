from __future__ import annotations

import json
import unittest
from pathlib import Path

from company.runtime.council_role_contracts import (
    RoleContractError,
    validate_role_contracts,
)

ROOT = Path(__file__).resolve().parents[2]
ROLES = json.loads((ROOT / "config/roles.json").read_text(encoding="utf-8"))
CONTRACTS = json.loads((ROOT / "company/config/council_role_contracts.json").read_text(encoding="utf-8"))

REQUIRED_FIELDS = {
    "mission",
    "inputs",
    "outputs",
    "activation",
    "blocker_scope",
    "authority",
    "tools",
    "escalation",
    "conflicts",
    "contribution_criteria",
    "merge_remove_trigger",
}


class Phase3R10RoleContractTests(unittest.TestCase):
    def test_every_governing_role_has_exactly_one_candidate_contract(self):
        self.assertTrue(validate_role_contracts(CONTRACTS, ROLES))
        expected = {item["id"] for item in ROLES["core_roles"] + ROLES["specialist_roles"]}
        actual = set(CONTRACTS["roles"])
        self.assertEqual(actual, expected)

    def test_all_contracts_define_required_fields(self):
        for role_id, contract in CONTRACTS["roles"].items():
            with self.subTest(role=role_id):
                self.assertTrue(REQUIRED_FIELDS.issubset(contract))
                for field in REQUIRED_FIELDS:
                    self.assertIsNotNone(contract[field])

    def test_chair_and_synthesis_are_explicitly_separated(self):
        chair = CONTRACTS["roles"]["chair"]
        synthesis = CONTRACTS["roles"]["synthesis"]
        self.assertNotIn("synthesis", chair["outputs"])
        self.assertEqual(chair["authority"]["decision_function"], "coordinate_and_record")
        self.assertEqual(synthesis["activation"]["model"], "protocol_stage")
        self.assertFalse(synthesis["authority"]["may_override_dissent"])
        self.assertFalse(synthesis["authority"]["may_override_domain_blockers"])

    def test_contracts_do_not_gain_execution_or_permission_authority(self):
        for role_id, contract in CONTRACTS["roles"].items():
            with self.subTest(role=role_id):
                authority = contract["authority"]
                self.assertFalse(authority["may_execute_tools"])
                self.assertFalse(authority["may_mutate_authority"])
                self.assertFalse(authority["may_self_approve"])

    def test_specialist_blockers_are_domain_bounded(self):
        for role in ROLES["specialist_roles"]:
            contract = CONTRACTS["roles"][role["id"]]
            with self.subTest(role=role["id"]):
                self.assertEqual(contract["blocker_scope"]["type"], "domain_bounded")
                self.assertTrue(contract["blocker_scope"]["requires_evidence"])

    def test_commercial_challenge_roles_have_material_commercial_activation(self):
        for role_id in ("customer_skeptic", "moat_auditor"):
            contract = CONTRACTS["roles"][role_id]
            with self.subTest(role=role_id):
                self.assertIn("material_commercial_decision", contract["activation"]["required_when"])
                self.assertEqual(contract["blocker_scope"]["type"], "domain_bounded")

    def test_merge_remove_is_evidence_based_and_never_automatic(self):
        for role_id, contract in CONTRACTS["roles"].items():
            trigger = contract["merge_remove_trigger"]
            with self.subTest(role=role_id):
                self.assertFalse(trigger["automatic"])
                self.assertGreaterEqual(trigger["minimum_observation_count"], 3)
                self.assertIn("duplicate_reasoning", trigger["signals"])
                self.assertIn("low_unique_contribution", trigger["signals"])

    def test_invalid_contract_cannot_claim_global_blocker_or_missing_role(self):
        broken = json.loads(json.dumps(CONTRACTS))
        broken["roles"]["software"]["blocker_scope"]["type"] = "global"
        with self.assertRaises(RoleContractError):
            validate_role_contracts(broken, ROLES)

        broken = json.loads(json.dumps(CONTRACTS))
        del broken["roles"]["risk"]
        with self.assertRaises(RoleContractError):
            validate_role_contracts(broken, ROLES)


if __name__ == "__main__":
    unittest.main()
