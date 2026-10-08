import json, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

class CompanyPolicyConfig(unittest.TestCase):
    def test_hr_role_and_owner_authority(self):
        roles=json.loads((ROOT/"company/config/roles.json").read_text(encoding="utf-8"))
        self.assertEqual(roles["version"],"1.2")
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
        self.assertIn("media_workforce_capability",hr["owns"])
        self.assertIn("media_toolchain_capability",hr["owns"])
        media_scoped={x["id"] for x in roles["venture_scoped_functions"]}
        self.assertEqual(media_scoped,{"editorial_director","ai_visual_post_producer","audience_growth_packaging"})

    def test_zero_revenue_mode_and_distribution_gate_are_default(self):
        defaults=json.loads((ROOT/"company/config/defaults.json").read_text(encoding="utf-8"))
        self.assertEqual(defaults["version"],"1.3")
        self.assertTrue(defaults["zero_revenue_founder_mode"])
        self.assertTrue(defaults["founder_mode_until_first_collected_payment"])
        self.assertTrue(defaults["distribution_local_market_fit_gate"])
        self.assertTrue(defaults["forced_conviction_required"])
        self.assertTrue(defaults["hr_capability_director_required"])
        self.assertTrue(defaults["market_reality_definition_gate"])
        self.assertTrue(defaults["market_reality_required_before_project_candidate"])
        self.assertTrue(defaults["market_scope_must_precede_solution"])
        self.assertTrue(defaults["media_venture_capability_layer"])
        self.assertTrue(defaults["media_three_video_pilot_required"])
        self.assertTrue(defaults["media_full_scale_before_pilot_forbidden"])

    def test_commercial_policy_forbids_safe_neutral_position(self):
        policy=json.loads((ROOT/"company/config/commercial_policy.json").read_text(encoding="utf-8"))
        self.assertEqual(policy["version"],"1.2")
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
        reality=policy["market_reality_definition"]
        self.assertTrue(reality["mandatory_before_project_candidate"])
        self.assertTrue(reality["age_requires_life_stage"])
        self.assertTrue(reality["project_price_must_fit_segment_capacity"])
        self.assertTrue(reality["project_first_reasoning_forbidden"])

if __name__=="__main__":
    unittest.main()
