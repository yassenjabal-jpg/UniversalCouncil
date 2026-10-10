import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class IntelligenceContracts(unittest.TestCase):
    def _text(self, path):
        return (ROOT / path).read_text(encoding="utf-8").lower()

    def test_evidence_contract_requires_native_first_and_provenance(self):
        text = self._text("contracts/EVIDENCE_AND_RESEARCH.md")
        self.assertIn("native-first routing", text)
        self.assertIn("evidence provenance", text)
        self.assertIn("agent reach public-read", text)

    def test_skill_blocks_authenticated_social_in_v1(self):
        text = self._text("skills/universal-council/SKILL.md")
        self.assertIn("authenticated social channels remain blocked in v1", text)
        self.assertIn("capability gap", text)
        self.assertIn("native-first routing", text)

    def test_gateway_is_not_a_council_member_or_decision_authority(self):
        text = self._text("company/README.md")
        self.assertIn("not a council member", text)
        self.assertIn("no decision authority", text)

    def test_acceptance_document_covers_read_only_and_owner_gates(self):
        text = self._text("company/docs/INTELLIGENCE_GATEWAY_ACCEPTANCE.md")
        self.assertIn("read_only / public_only", text)
        self.assertIn("no opencli", text)
        self.assertIn("evidence provenance", text)
        self.assertIn("capability-gap", text)


if __name__ == "__main__":
    unittest.main()
