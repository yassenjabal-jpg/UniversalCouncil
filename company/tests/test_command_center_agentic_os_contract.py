from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "state" / "command-center" / "project-governance"
STATE = ROOT / "state" / "command-center"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class CommandCenterAgenticOsContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = load(PROJECT / "agentic-os-policy.json")
        cls.invariants = load(PROJECT / "architecture-invariants.json")
        cls.capsule = load(PROJECT / "context-capsule-contract.json")
        cls.envelope = load(PROJECT / "change-envelope-contract.json")
        cls.visual_manifest = load(STATE / "living-operations-reference-manifest.json")

    def test_gateway_is_logical_boundary_not_monolith(self) -> None:
        gateway = self.policy["logical_gateway"]
        self.assertTrue(gateway["not_a_god_object"])
        self.assertTrue(gateway["one_logical_authority_boundary"])
        self.assertGreaterEqual(len(gateway["delegates_to"]), 8)

    def test_agentic_policy_cannot_expand_authority(self) -> None:
        authority = self.policy["authority"]
        self.assertFalse(authority["execution_authority"])
        self.assertFalse(authority["stage8_opened"])
        self.assertFalse(authority["parent_mutation_allowed"])
        self.assertTrue(authority["owner_final_authority"])

    def test_context_content_is_data_not_authority(self) -> None:
        security = self.policy["context_security"]
        self.assertTrue(security["all_retrieved_content_is_data_by_default"])
        self.assertTrue(security["retrieved_text_cannot_grant_permissions"])
        self.assertTrue(security["tool_output_cannot_modify_policy"])

    def test_result_model_contains_drift_states(self) -> None:
        states = set(self.policy["result_model"]["states"])
        self.assertIn("STALE_CONTEXT", states)
        self.assertIn("CONTEXT_CONFLICT", states)
        self.assertIn("UNKNOWN", states)
        self.assertTrue(self.policy["result_model"]["unknown_never_success"])

    def test_visual_policy_inherits_existing_eight_reference_lock(self) -> None:
        visual = self.policy["visual_inheritance"]
        self.assertEqual(visual["canonical_reference_count"], 8)
        self.assertEqual(len(self.visual_manifest["references"]), 8)
        self.assertTrue(visual["generic_visual_capsule_may_not_weaken_existing_gate"])
        self.assertTrue(visual["actual_reference_bytes_required"])

    def test_invariants_have_scoped_applicability(self) -> None:
        invariants = self.invariants["invariants"]
        self.assertEqual(len(invariants), 24)
        self.assertTrue(any(item["applies_from"] != "NOW" for item in invariants))
        for item in invariants:
            self.assertTrue(item["change_classes"])
            self.assertTrue(item["enforcement"])
            self.assertTrue(item["implementation_state"])

    def test_context_capsule_is_immutable_and_fails_closed(self) -> None:
        self.assertTrue(self.capsule["immutable_per_job"])
        self.assertEqual(self.capsule["conflict_result"], "CONTEXT_CONFLICT")
        self.assertEqual(self.capsule["stale_result"], "STALE_CONTEXT")

    def test_change_envelope_prevents_silent_scope_growth(self) -> None:
        self.assertEqual(
            self.envelope["unplanned_scope_expansion"],
            "RETURN_TICKET_OR_NEW_CHANGE_ENVELOPE",
        )
        self.assertTrue(self.envelope["material_mutation_from_freeform_prompt_only_forbidden"])
        self.assertTrue(self.envelope["delta_only_default"])


if __name__ == "__main__":
    unittest.main()
