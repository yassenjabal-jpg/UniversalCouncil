from __future__ import annotations

import json
import unittest
from pathlib import Path

from company.runtime.council_intelligent_routing import (
    IntelligentRoutingError,
    route_decision,
    validate_routing_candidate,
)

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "company/config/council_routing_candidate.json").read_text(encoding="utf-8"))
ROLES = json.loads((ROOT / "config/roles.json").read_text(encoding="utf-8"))


class Phase3R11IntelligentRoutingTests(unittest.TestCase):
    def test_candidate_config_is_valid_and_non_governing(self):
        self.assertTrue(validate_routing_candidate(CFG, ROLES))
        self.assertEqual(CFG["status"], "CANDIDATE_SHADOW_ONLY")
        self.assertEqual(CFG["governing_council_version"], "0.3.0")

    def test_low_stakes_route_uses_smallest_useful_set(self):
        result = route_decision(
            {
                "decision_id": "low-1",
                "domains": ["software"],
                "materiality": "LOW",
                "uncertainty": "LOW",
                "risk": "LOW",
                "freshness": "LOW",
                "required_capabilities": ["execution"],
                "commercial": False,
                "active_domain_blockers": [],
            },
            CFG,
            ROLES,
        )
        self.assertEqual(result["core_capabilities"], ["chair", "execution"])
        self.assertEqual(result["specialists"], ["software"])
        self.assertLessEqual(result["voice_count"], 3)

    def test_high_uncertainty_and_freshness_activate_evidence_and_redteam(self):
        result = route_decision(
            {
                "decision_id": "uncertain-1",
                "domains": ["science"],
                "materiality": "MATERIAL",
                "uncertainty": "HIGH",
                "risk": "MEDIUM",
                "freshness": "HIGH",
                "required_capabilities": [],
                "commercial": False,
                "active_domain_blockers": [],
            },
            CFG,
            ROLES,
        )
        self.assertIn("evidence", result["core_capabilities"])
        self.assertIn("redteam", result["core_capabilities"])
        self.assertIn("risk", result["core_capabilities"])
        self.assertIn("science", result["specialists"])

    def test_material_commercial_route_preserves_required_commercial_specialists(self):
        result = route_decision(
            {
                "decision_id": "commercial-1",
                "domains": ["business"],
                "materiality": "MATERIAL",
                "uncertainty": "MEDIUM",
                "risk": "MEDIUM",
                "freshness": "MEDIUM",
                "required_capabilities": ["value", "human"],
                "commercial": True,
                "active_domain_blockers": [],
            },
            CFG,
            ROLES,
        )
        self.assertIn("customer_skeptic", result["specialists"])
        self.assertIn("moat_auditor", result["specialists"])
        self.assertIn("value", result["core_capabilities"])
        self.assertIn("human", result["core_capabilities"])

    def test_active_domain_blocker_forces_relevant_specialist(self):
        result = route_decision(
            {
                "decision_id": "blocker-1",
                "domains": [],
                "materiality": "LOW",
                "uncertainty": "LOW",
                "risk": "LOW",
                "freshness": "LOW",
                "required_capabilities": [],
                "commercial": False,
                "active_domain_blockers": ["security"],
            },
            CFG,
            ROLES,
        )
        self.assertIn("security", result["specialists"])
        reason = result["activation_reasons"]["security"]
        self.assertIn("active_domain_blocker", reason)

    def test_route_is_dimension_driven_not_free_text_keyword_driven(self):
        base = {
            "decision_id": "dim-1",
            "domains": ["finance"],
            "materiality": "LOW",
            "uncertainty": "LOW",
            "risk": "LOW",
            "freshness": "LOW",
            "required_capabilities": [],
            "commercial": False,
            "active_domain_blockers": [],
        }
        with_noise = {**base, "free_text": "health security youtube travel legal software"}
        a = route_decision(base, CFG, ROLES)
        b = route_decision(with_noise, CFG, ROLES)
        self.assertEqual(a["core_capabilities"], b["core_capabilities"])
        self.assertEqual(a["specialists"], b["specialists"])

    def test_unknown_required_capability_or_domain_fails_closed(self):
        bad = {
            "decision_id": "bad-1",
            "domains": ["unknown-domain"],
            "materiality": "LOW",
            "uncertainty": "LOW",
            "risk": "LOW",
            "freshness": "LOW",
            "required_capabilities": [],
            "commercial": False,
            "active_domain_blockers": [],
        }
        with self.assertRaises(IntelligentRoutingError):
            route_decision(bad, CFG, ROLES)

        bad = {
            **bad,
            "domains": [],
            "required_capabilities": ["unknown-capability"],
        }
        with self.assertRaises(IntelligentRoutingError):
            route_decision(bad, CFG, ROLES)

    def test_route_explains_every_activation_and_dimensions(self):
        result = route_decision(
            {
                "decision_id": "explain-1",
                "domains": ["design"],
                "materiality": "HIGH",
                "uncertainty": "MEDIUM",
                "risk": "HIGH",
                "freshness": "LOW",
                "required_capabilities": ["human"],
                "commercial": False,
                "active_domain_blockers": [],
            },
            CFG,
            ROLES,
        )
        for role_id in result["core_capabilities"] + result["specialists"]:
            self.assertIn(role_id, result["activation_reasons"])
            self.assertTrue(result["activation_reasons"][role_id])
        self.assertEqual(
            set(result["dimensions"]),
            {"domain","materiality","uncertainty","risk","freshness","blocker_authority","required_capability"},
        )


if __name__ == "__main__":
    unittest.main()
