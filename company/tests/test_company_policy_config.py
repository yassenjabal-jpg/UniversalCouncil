import json, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

class CompanyPolicyConfig(unittest.TestCase):
    def test_hr_role_and_owner_authority(self):
        roles=json.loads((ROOT/"company/config/roles.json").read_text(encoding="utf-8"))
        self.assertEqual(roles["version"],"1.1")
        self.assertIn("HR & Capability Director",roles["functions"])
        hr=roles["hr_capability_director"]
        self.assertFalse(hr["may_fire_unilaterally"])
        self.assertEqual(hr["final_authority"],"Owner")
        self.assertTrue(hr["self_evaluation_forbidden"])
        self.assertEqual(hr["complaints_about_hr_route_directly_to"],"Owner")
        self.assertTrue(hr["protected_dissent"])
        self.assertIn("unique_contribution",hr["performance_criteria"])
        self.assertIn("tool_skill_utilization",hr["performance_criteria"])
        self.assertEqual(hr["unresolved_capability_escalation"],"Owner")

    def test_zero_revenue_mode_and_distribution_gate_are_default(self):
        defaults=json.loads((ROOT/"company/config/defaults.json").read_text(encoding="utf-8"))
        self.assertEqual(defaults["version"],"1.1")
        self.assertTrue(defaults["zero_revenue_founder_mode"])
        self.assertTrue(defaults["founder_mode_until_first_collected_payment"])
        self.assertTrue(defaults["distribution_local_market_fit_gate"])
        self.assertTrue(defaults["forced_conviction_required"])
        self.assertTrue(defaults["hr_capability_director_required"])

    def test_commercial_policy_forbids_safe_neutral_position(self):
        policy=json.loads((ROOT/"company/config/commercial_policy.json").read_text(encoding="utf-8"))
        founder=policy["zero_revenue_founder_mode"]
        self.assertEqual(
            set(founder["allowed_position_verdicts"]),
            {"SUPPORT","OPPOSE","KILL","PIVOT","TEST_NOW"},
        )
        self.assertTrue(founder["cost_of_delay_required"])
        distribution=policy["distribution_local_market_fit"]
        self.assertTrue(distribution["tool_availability_must_not_select_channel"])
        self.assertIn("CHANNEL_FAILURE",distribution["no_reply_diagnosis_states"])
        self.assertIn("INSUFFICIENT_EVIDENCE",distribution["no_reply_diagnosis_states"])

if __name__=="__main__":
    unittest.main()
