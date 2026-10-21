from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "state" / "command-center"
PROJECT = STATE / "project-governance"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class CommandCenterRepairB2ConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = load(STATE / "living-operations-p1-b2-cross-screen-consistency.json")
        cls.pre = load(PROJECT / "approvals" / "2026-10-21-repair-b2-cross-screen-consistency-pre.json")
        cls.b2_1_check = load(PROJECT / "approvals" / "2026-10-21-repair-b2-1-shared-visual-check.json")
        cls.p1 = load(STATE / "living-operations-p1-visual-phase.json")
        cls.screen_review = load(STATE / "living-operations-p1-screen-review.json")
        cls.main = (
            ROOT
            / "apps"
            / "UniversalCouncil.CommandCenter"
            / "MainWindow.xaml.cs"
        ).read_text(encoding="utf-8")
        cls.xaml = (
            ROOT
            / "apps"
            / "UniversalCouncil.CommandCenter"
            / "MainWindow.xaml"
        ).read_text(encoding="utf-8")

    def test_b2_is_scoped_and_does_not_preapprove_b3(self) -> None:
        self.assertTrue(self.pre["implementation_authorized"])
        self.assertFalse(self.pre["merge_authorized"])
        self.assertFalse(self.pre["final_p1_approval_granted"])
        self.assertFalse(self.pre["b3_r10_opened"])
        self.assertFalse(self.pre["stage8_opened"])

    def test_b2_1_passed_before_b2_2(self) -> None:
        self.assertEqual(
            self.b2_1_check["decision"],
            "APPROVE_B2_1_CONTINUE",
        )
        self.assertEqual(
            self.plan["slices"]["B2.1_SHARED_VISUAL_TOKENS_AND_CHROME"]["state"],
            "APPROVED_TO_CONTINUE",
        )

    def test_shared_chrome_uses_cross_screen_tokens(self) -> None:
        for marker in (
            "CrossScreenVisualTokens.NavGlyphSize",
            "CrossScreenVisualTokens.NavLabelSize",
            "CrossScreenVisualTokens.DockGlyphSize",
            "CrossScreenVisualTokens.DockLabelSize",
        ):
            self.assertIn(marker, self.main)

    def test_shared_runtime_like_states_are_truth_aware(self) -> None:
        self.assertIn("_viewModel.ExecutionFabric.LiveDispatchEnabled", self.main)
        self.assertIn('"Autopilot — حالة التنفيذ"', self.main)
        self.assertNotIn('"Autopilot — يعمل الآن"', self.main)
        self.assertGreaterEqual(
            self.main.count('ChromeText("UNKNOWN", 9, "#6B7280"'),
            2,
        )

    def test_keyboard_and_accessibility_consistency(self) -> None:
        self.assertIn("AutomationProperties.SetHelpText", self.main)
        self.assertIn("e.Key == Key.K", self.main)
        self.assertIn("UNKNOWN / SEARCH PROVIDER NOT CONNECTED", self.main)
        self.assertIn(
            "SecondaryNativeLayer.Opacity = "
            "_nativeReferenceBlendEnabled && !isHome ? 0.46 : 1;",
            self.main,
        )
        self.assertIn('KeyboardNavigation.TabNavigation="Cycle"', self.xaml)
        self.assertIn('KeyboardNavigation.ControlTabNavigation="Cycle"', self.xaml)

    def test_b2_does_not_complete_p1(self) -> None:
        self.assertEqual(self.p1["status"], "IN_PROGRESS")
        self.assertFalse(self.p1["stage8_opened"])
        self.assertFalse(self.p1["runtime_authority"])
        self.assertFalse(self.screen_review["phase_complete"])


if __name__ == "__main__":
    unittest.main()
