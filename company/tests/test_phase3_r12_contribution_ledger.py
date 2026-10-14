from __future__ import annotations

import json
import unittest
from pathlib import Path

from company.runtime.contribution_ledger import (
    ContributionLedgerError,
    evaluate_role_contribution,
    validate_contribution_config,
)

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "company/config/contribution_ledger.json").read_text(encoding="utf-8"))


class Phase3R12ContributionLedgerTests(unittest.TestCase):
    def test_config_is_candidate_only_and_has_no_voting_weights(self):
        self.assertTrue(validate_contribution_config(CFG))
        self.assertEqual(CFG["status"], "CANDIDATE_SHADOW_ONLY")
        self.assertFalse(CFG["use_as_voting_weights"])
        self.assertNotIn("weights", CFG)

    def test_metrics_cover_canonical_contribution_fields(self):
        self.assertEqual(
            set(CFG["metrics"]),
            {
                "unique_evidence",
                "unique_objection",
                "option_added",
                "test_changed",
                "decision_changed",
                "duplicate_reasoning",
                "false_blocker",
                "missed_blocker",
                "latency_ms",
                "cost_units",
                "human_override",
            },
        )

    def test_strong_unique_contribution_returns_keep(self):
        observations = [
            {
                "unique_evidence": 2,
                "unique_objection": 1,
                "option_added": 1,
                "test_changed": 1,
                "decision_changed": 1,
                "duplicate_reasoning": 0,
                "false_blocker": 0,
                "missed_blocker": 0,
                "latency_ms": 100,
                "cost_units": 1,
                "human_override": 0,
            }
            for _ in range(3)
        ]
        result = evaluate_role_contribution("redteam", observations, CFG)
        self.assertEqual(result["recommendation"], "KEEP")
        self.assertGreater(result["totals"]["unique_objection"], 0)

    def test_repeated_duplication_can_narrow_or_move_on_demand(self):
        observations = [
            {
                "unique_evidence": 0,
                "unique_objection": 0,
                "option_added": 0,
                "test_changed": 0,
                "decision_changed": 0,
                "duplicate_reasoning": 3,
                "false_blocker": 0,
                "missed_blocker": 0,
                "latency_ms": 900,
                "cost_units": 5,
                "human_override": 0,
            }
            for _ in range(4)
        ]
        result = evaluate_role_contribution("value", observations, CFG)
        self.assertIn(result["recommendation"], {"NARROW", "ON_DEMAND", "MERGE"})
        self.assertIn("duplicate_reasoning", result["reasons"])

    def test_false_or_missed_blockers_trigger_improvement_trial_before_remove(self):
        observations = [
            {
                "unique_evidence": 0,
                "unique_objection": 1,
                "option_added": 0,
                "test_changed": 0,
                "decision_changed": 0,
                "duplicate_reasoning": 0,
                "false_blocker": 1,
                "missed_blocker": 1,
                "latency_ms": 100,
                "cost_units": 1,
                "human_override": 0,
            }
            for _ in range(3)
        ]
        result = evaluate_role_contribution("risk", observations, CFG)
        self.assertEqual(result["recommendation"], "IMPROVEMENT_TRIAL")

    def test_remove_requires_more_evidence_than_minimum_window(self):
        observations = [
            {
                "unique_evidence": 0,
                "unique_objection": 0,
                "option_added": 0,
                "test_changed": 0,
                "decision_changed": 0,
                "duplicate_reasoning": 2,
                "false_blocker": 1,
                "missed_blocker": 1,
                "latency_ms": 1500,
                "cost_units": 8,
                "human_override": 1,
            }
            for _ in range(6)
        ]
        result = evaluate_role_contribution("some_role", observations, CFG)
        self.assertEqual(result["recommendation"], "REMOVE")
        self.assertTrue(result["requires_owner_review"])

    def test_too_few_observations_yield_improvement_trial_not_remove(self):
        result = evaluate_role_contribution(
            "role",
            [
                {
                    "unique_evidence": 0,
                    "unique_objection": 0,
                    "option_added": 0,
                    "test_changed": 0,
                    "decision_changed": 0,
                    "duplicate_reasoning": 1,
                    "false_blocker": 0,
                    "missed_blocker": 0,
                    "latency_ms": 100,
                    "cost_units": 1,
                    "human_override": 0,
                }
            ],
            CFG,
        )
        self.assertEqual(result["recommendation"], "IMPROVEMENT_TRIAL")
        self.assertIn("insufficient_observations", result["reasons"])

    def test_unknown_metric_or_negative_values_fail_closed(self):
        bad = [{metric: 0 for metric in CFG["metrics"]}]
        bad[0]["unexpected"] = 1
        with self.assertRaises(ContributionLedgerError):
            evaluate_role_contribution("role", bad, CFG)

        bad = [{metric: 0 for metric in CFG["metrics"]}]
        bad[0]["unique_evidence"] = -1
        with self.assertRaises(ContributionLedgerError):
            evaluate_role_contribution("role", bad, CFG)


if __name__ == "__main__":
    unittest.main()
