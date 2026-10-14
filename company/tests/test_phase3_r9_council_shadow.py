from __future__ import annotations

import json
import unittest
from pathlib import Path

from company.runtime.council_shadow import (
    CouncilShadowError,
    build_shadow_plan,
    synthesize_shadow,
    validate_shadow_config,
)

ROOT = Path(__file__).resolve().parents[2]
SHADOW_CFG = json.loads((ROOT / "company/config/council_shadow.json").read_text(encoding="utf-8"))
ROLES = json.loads((ROOT / "config/roles.json").read_text(encoding="utf-8"))
ROUTING = json.loads((ROOT / "config/domain-routing.json").read_text(encoding="utf-8"))


class Phase3R9CouncilShadowTests(unittest.TestCase):
    def test_shadow_is_candidate_only_and_v03_remains_governing(self):
        self.assertTrue(validate_shadow_config(SHADOW_CFG, ROLES))
        self.assertEqual(SHADOW_CFG["status"], "CANDIDATE_SHADOW_ONLY")
        self.assertEqual(SHADOW_CFG["governing_council_version"], "0.3.0")
        self.assertFalse(SHADOW_CFG["may_replace_governing_council"])
        self.assertFalse(SHADOW_CFG["may_execute_tools"])
        self.assertFalse(SHADOW_CFG["may_mutate_authority"])
        self.assertEqual(ROLES["version"], "0.3.0")

    def test_decision_orchestrator_coordinates_chair_but_synthesis_stays_protocol_stage(self):
        plan = build_shadow_plan(
            {
                "decision_id": "d1",
                "mode": "COUNCIL",
                "domain_signals": ["software", "architecture"],
                "materiality": "MATERIAL",
                "commercial": False,
            },
            SHADOW_CFG,
            ROLES,
            ROUTING,
        )
        self.assertEqual(plan["coordinator"], "decision_orchestrator")
        self.assertIn("chair", plan["capabilities"])
        self.assertNotIn("synthesis", plan["capabilities"])
        self.assertIn("synthesis", plan["protocol_stages"])
        self.assertTrue(plan["shadow_only"])
        self.assertFalse(plan["execution_authority"])

    def test_material_commercial_shadow_preserves_customer_skeptic_and_moat_auditor(self):
        plan = build_shadow_plan(
            {
                "decision_id": "commercial-1",
                "mode": "COUNCIL",
                "domain_signals": ["business", "revenue", "customer"],
                "materiality": "MATERIAL",
                "commercial": True,
            },
            SHADOW_CFG,
            ROLES,
            ROUTING,
        )
        self.assertIn("customer_skeptic", plan["specialists"])
        self.assertIn("moat_auditor", plan["specialists"])
        self.assertIn("redteam", plan["capabilities"])
        self.assertIn("evidence", plan["capabilities"])

    def test_synthesis_cannot_drop_dissent_or_domain_blockers(self):
        packet = {
            "decision_id": "dissent-1",
            "candidate_recommendation": "OPTION_A",
            "dissent": [
                {
                    "role": "redteam",
                    "position": "OPTION_B",
                    "reason": "failure mode remains unresolved",
                }
            ],
            "domain_blockers": [
                {
                    "specialist": "security",
                    "blocker_id": "SEC-1",
                    "reason": "credential boundary not proven",
                    "authority_scope": "security",
                }
            ],
            "alternatives": ["OPTION_A", "OPTION_B"],
        }
        result = synthesize_shadow(packet, SHADOW_CFG)
        self.assertEqual(result["dissent"], packet["dissent"])
        self.assertEqual(result["domain_blockers"], packet["domain_blockers"])
        self.assertTrue(result["minority_preserved"])
        self.assertFalse(result["governing_decision"])

    def test_shadow_rejects_attempt_to_claim_execution_or_authority(self):
        for forbidden in (
            {"execute": True},
            {"authority_change": {"operation": "github.write"}},
            {"governing_decision": True},
        ):
            with self.subTest(forbidden=forbidden):
                with self.assertRaises(CouncilShadowError):
                    synthesize_shadow(
                        {
                            "decision_id": "unsafe",
                            "candidate_recommendation": "A",
                            "dissent": [],
                            "domain_blockers": [],
                            "alternatives": ["A"],
                            **forbidden,
                        },
                        SHADOW_CFG,
                    )

    def test_shadow_runtime_is_honest_about_non_independent_roles(self):
        plan = build_shadow_plan(
            {
                "decision_id": "honesty-1",
                "mode": "LIGHT",
                "domain_signals": [],
                "materiality": "LOW",
                "commercial": False,
            },
            SHADOW_CFG,
            ROLES,
            ROUTING,
        )
        self.assertEqual(
            plan["runtime_model"],
            "structured_capabilities_not_claimed_as_independent_agents",
        )


if __name__ == "__main__":
    unittest.main()
