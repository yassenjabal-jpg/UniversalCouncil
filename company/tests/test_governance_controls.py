import unittest
from company.runtime.governance_controls import (
    GovernanceControlError,
    validate_founder_position,
    validate_pass_with_conditions,
    validate_distribution_gate,
    diagnose_no_reply,
    validate_hr_recommendation,
    validate_hr_self_review,
    complaint_route,
)

class GovernanceControls(unittest.TestCase):
    def test_founder_mode_forces_clear_position(self):
        good={
            "verdict":"KILL","confidence_0_100":82,
            "next_10_hours_yes_no":"NO","own_money_yes_no":"NO",
            "single_strongest_reason":"weak willingness-to-pay evidence",
            "one_evidence_that_changes_view":"two paid pilots",
            "cost_of_delay":"another week displaces a stronger test",
        }
        self.assertTrue(validate_founder_position(good))
        bad=dict(good); bad["verdict"]="PASS-WITH-CONDITIONS"
        with self.assertRaises(GovernanceControlError):
            validate_founder_position(bad)

    def test_pass_with_conditions_cannot_be_vague(self):
        with self.assertRaises(GovernanceControlError):
            validate_pass_with_conditions({"metric":"reply rate"})
        self.assertTrue(validate_pass_with_conditions({
            "metric":"qualified replies",
            "deadline":"2026-10-15",
            "threshold":2,
            "default_failure_action":"PIVOT",
        }))

    def test_distribution_gate_requires_local_evidence_and_channels(self):
        record={
            "buyer":"Iraqi contractor",
            "decision_maker":"business development lead",
            "where_buyer_spends_attention":["phone","WhatsApp","LinkedIn"],
            "first_touch_channel":"phone",
            "conversation_channel":"WhatsApp",
            "formal_document_channel":"email",
            "normal_response_window":"2 business days",
            "fallback_channel":"LinkedIn",
            "local_market_evidence":["company contact pages","buyer interviews"],
            "channel_capability_status":"HUMAN_REQUIRED",
        }
        self.assertTrue(validate_distribution_gate(record))
        record["local_market_evidence"]=[]
        with self.assertRaises(GovernanceControlError):
            validate_distribution_gate(record)

    def test_no_reply_is_not_not_interested(self):
        self.assertEqual(
            diagnose_no_reply(
                delivery_confirmed=True,
                channel_supported=False,
                contact_supported=True,
                timing_supported=True,
                offer_supported=True,
            ),
            "CHANNEL_FAILURE",
        )
        self.assertEqual(
            diagnose_no_reply(
                delivery_confirmed=True,
                channel_supported=True,
                contact_supported=True,
                timing_supported=True,
                offer_supported=True,
            ),
            "INSUFFICIENT_EVIDENCE",
        )

    def test_hr_cannot_fire_or_self_review(self):
        self.assertTrue(validate_hr_recommendation({
            "role":"Commercial Operator",
            "recommendation":"REPLACE",
            "evidence":["three reviews without decision-changing contribution"],
            "unique_value_assessment":"duplicated by Venture Operator",
            "replacement_or_merge_plan":"replace with Local Distribution Specialist",
            "review_trigger":"after next two market experiments",
        }))
        with self.assertRaises(GovernanceControlError):
            validate_hr_self_review("HR & Capability Director")
        self.assertEqual(complaint_route("HR & Capability Director"),"Owner")
        self.assertEqual(complaint_route("Commercial Operator"),"HR & Capability Director")

if __name__=="__main__":
    unittest.main()
