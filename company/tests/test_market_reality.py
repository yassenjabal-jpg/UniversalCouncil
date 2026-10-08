import json, unittest
from pathlib import Path

from company.runtime.market_reality import (
    MarketRealityError,
    validate_market_reality,
    market_pull_score,
    classify_market_pull,
    validate_project_candidate,
)

ROOT=Path(__file__).resolve().parents[2]

def valid_market():
    return {
        "discovery_mode":"SEGMENT_FIRST",
        "geography":{
            "country":"Iraq",
            "region":"Babil",
            "city":"Al Hillah",
            "urban_rural":"urban",
            "precision_basis":"city affects local commerce, delivery and buying channels",
        },
        "demography":{
            "age_min":25,
            "age_max":44,
            "life_stage":"working adults / owner-operators",
        },
        "social_occupational":{
            "segment":"small retail and restaurant owner-operators",
            "user":"owner or staff",
            "buyer":"owner",
            "payer":"owner",
            "decision_maker":"owner",
        },
        "purchasing_capacity":{
            "currency":"IQD",
            "capacity_evidence":["local service prices","merchant interviews"],
            "discretionary_budget_evidence":["existing monthly business software/service spend"],
            "existing_spend_evidence":["delivery, ads, accounting or operational services"],
            "willingness_to_pay_evidence":["purchases of adjacent services"],
            "price_floor_minor":10000000,
            "price_ceiling_minor":75000000,
            "payment_methods":["cash","local electronic payment"],
        },
        "buying_behavior":{
            "discovery_channels":["Facebook","Instagram","referrals"],
            "first_touch_channels":["phone","WhatsApp"],
            "conversation_channels":["WhatsApp","phone"],
            "formal_document_channels":["email"],
            "trust_constraints":["local reputation","proof before payment"],
            "payment_behavior":["cash","local electronic payment"],
            "delivery_constraints":["local service availability"],
            "reachability_status":"HUMAN_REQUIRED",
        },
        "evidence_scope":{
            "local_sources":["Iraqi merchant interviews","local business pages","Iraqi market pricing"],
            "geography_matches_target":True,
            "segment_matches_target":True,
            "foreign_evidence_role":"SECONDARY_CONTEXT",
        },
    }

def strong_ratings():
    return {
        "pain_frequency":8,
        "existing_spend":8,
        "urgency":7,
        "workaround_burden":8,
        "buyer_clarity":9,
        "reachability":8,
        "free_ai_resistance":7,
        "repeatability":8,
        "margin_potential":8,
        "evidence_diversity":8,
        "purchasing_capacity":8,
        "local_price_fit":9,
    }

class MarketRealityTests(unittest.TestCase):
    def test_valid_market_reality_passes(self):
        self.assertTrue(validate_market_reality(valid_market()))

    def test_age_without_life_stage_fails(self):
        m=valid_market()
        m["demography"]["life_stage"]=""
        with self.assertRaises(MarketRealityError):
            validate_market_reality(m)

    def test_foreign_pain_cannot_replace_local_evidence(self):
        m=valid_market()
        m["evidence_scope"]["local_sources"]=[]
        m["evidence_scope"]["foreign_evidence_role"]="SECONDARY_CONTEXT"
        with self.assertRaises(MarketRealityError):
            validate_market_reality(m)

    def test_mismatched_geography_or_segment_fails_gate(self):
        m=valid_market()
        m["evidence_scope"]["geography_matches_target"]=False
        with self.assertRaises(MarketRealityError):
            validate_market_reality(m)
        m=valid_market()
        m["evidence_scope"]["segment_matches_target"]=False
        with self.assertRaises(MarketRealityError):
            validate_market_reality(m)

    def test_market_pull_score_is_weighted_and_classified(self):
        score=market_pull_score(strong_ratings())
        self.assertGreaterEqual(score,75)
        self.assertIn(classify_market_pull(score),{"VALIDATION_CANDIDATE","PRIORITY_CANDIDATE"})

    def test_project_price_must_fit_segment_capacity(self):
        m=valid_market()
        ratings=strong_ratings()
        with self.assertRaises(MarketRealityError):
            validate_project_candidate(m,ratings,{
                "name":"Too expensive",
                "problem":"verified local problem",
                "price_minor":100000000,
                "currency":"IQD",
            })

    def test_project_candidate_can_pass_only_after_market_reality(self):
        result=validate_project_candidate(valid_market(),strong_ratings(),{
            "name":"Local operations service",
            "problem":"repeated verified merchant workflow burden",
            "price_minor":50000000,
            "currency":"IQD",
        })
        self.assertGreaterEqual(result["score"],60)
        self.assertNotEqual(result["state"],"REJECT")

    def test_market_policy_weights_sum_to_100(self):
        cfg=json.loads((ROOT/"company/config/market_reality.json").read_text(encoding="utf-8"))
        self.assertTrue(cfg["mandatory_before_project_candidate"])
        self.assertEqual(sum(cfg["market_pull_weights"].values()),100)
        self.assertTrue(cfg["price_must_fit_segment_capacity"])
        self.assertTrue(cfg["project_first_reasoning_forbidden"])

if __name__=="__main__":
    unittest.main()
