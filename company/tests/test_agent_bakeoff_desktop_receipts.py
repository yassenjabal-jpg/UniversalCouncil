from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from tools.apply_agent_bakeoff_desktop_receipts import REQUIRED_CASES, REQUIRED_RUNTIMES, validate_receipts

ROOT = Path(__file__).resolve().parents[2]


def manifest():
    return {
        "execution_host": "YASSIN",
        "financial_cost_usd": 0.0,
        "manifest_id": "m",
    }


def receipt(runtime_id: str, case_id: str):
    return {
        "runtime_id": runtime_id,
        "case_id": case_id,
        "execution_host": "YASSIN",
        "manifest_id": "m",
        "cost_usd": 0.0,
        "execution_path": "GUI_SEMANTIC",
        "fallback_reason": None,
        "desktop": {
            "task_completed": True,
            "verification_passed": True,
            "selector_recovered": True,
            "correct_execution_path": True,
            "no_unintended_action": True,
        },
        "evidence": [
            {"kind": "before", "ref": "before-ref"},
            {"kind": "semantic_action", "ref": "action-ref"},
            {"kind": "after", "ref": "after-ref"},
        ],
    }


def all_receipts():
    return [
        receipt(runtime_id, case_id)
        for runtime_id in sorted(REQUIRED_RUNTIMES)
        for case_id in sorted(REQUIRED_CASES)
    ]


class DesktopReceiptTests(unittest.TestCase):
    def test_exact_six_receipts_pass_schema(self):
        receipts = all_receipts()
        self.assertEqual(len(receipts), 6)
        validate_receipts(receipts, manifest())

    def test_missing_evidence_kind_is_rejected(self):
        receipts = all_receipts()
        receipts[0]["evidence"] = [
            {"kind": "before", "ref": "before-ref"},
            {"kind": "after", "ref": "after-ref"},
        ]
        with self.assertRaises(ValueError):
            validate_receipts(receipts, manifest())

    def test_physical_fallback_requires_reason(self):
        receipts = all_receipts()
        receipts[0]["execution_path"] = "GUI_PHYSICAL_FALLBACK"
        receipts[0]["fallback_reason"] = ""
        with self.assertRaises(ValueError):
            validate_receipts(receipts, manifest())

    def test_foreign_host_or_nonzero_cost_is_rejected(self):
        receipts = all_receipts()
        foreign = copy.deepcopy(receipts)
        foreign[0]["execution_host"] = "OTHER"
        with self.assertRaises(ValueError):
            validate_receipts(foreign, manifest())

        paid = copy.deepcopy(receipts)
        paid[0]["cost_usd"] = 0.01
        with self.assertRaises(ValueError):
            validate_receipts(paid, manifest())

    def test_example_template_has_exact_required_keys(self):
        example = json.loads(
            (ROOT / "benchmarks/agent_runtime/desktop_receipts.example.json").read_text(encoding="utf-8")
        )
        keys = {(item["runtime_id"], item["case_id"]) for item in example}
        expected = {(runtime_id, case_id) for runtime_id in REQUIRED_RUNTIMES for case_id in REQUIRED_CASES}
        self.assertEqual(keys, expected)


if __name__ == "__main__":
    unittest.main()
