import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = (
    ROOT
    / "docs"
    / "operations"
    / "command-center"
    / "living-operations"
    / "prototypes"
    / "home-reference-overlay"
)


class HomeReferenceOverlayTests(unittest.TestCase):
    def test_overlay_uses_exact_canonical_parent_path(self):
        html = (BASE / "index.html").read_text(encoding="utf-8")
        self.assertIn("../../references/01-home_owner_workspace.png", html)
        self.assertNotIn("79110079-3684-437e-9c29-825ac3f6cb4d", html)

    def test_all_eight_home_members_are_interactive(self):
        script = (BASE / "app.js").read_text(encoding="utf-8")
        for member_id in (
            "owner",
            "strategy",
            "research",
            "verification",
            "execution",
            "creative",
            "data",
            "learning",
        ):
            self.assertIn(f"{member_id}:", script)

        html = (BASE / "index.html").read_text(encoding="utf-8")
        self.assertEqual(html.count('data-kind="member"'), 8)
        self.assertEqual(html.count('data-kind="reasoning"'), 8)

    def test_overlay_state_never_claims_visual_or_runtime_authority(self):
        state_path = (
            ROOT
            / "state"
            / "command-center"
            / "living-operations-p1-home-interaction-overlay.json"
        )
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertFalse(state["visual_authority"])
        self.assertIn("visual_artifact_approved", state["forbidden_claims"])
        self.assertIn("runtime_execution_enabled", state["forbidden_claims"])
        self.assertEqual(state["next_visual_job"], "P1-HOME-ARTIFACT-002")
