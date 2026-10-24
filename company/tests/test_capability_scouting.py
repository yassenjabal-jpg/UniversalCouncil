import json
import unittest
from pathlib import Path

from company.runtime.capability_scout import (
    approval_gate_for,
    build_gap,
    hr_may_execute,
    scouting_due,
    validate_candidate,
    validate_g0_evidence,
)

ROOT = Path(__file__).resolve().parents[2]


class CapabilityScoutingPolicy(unittest.TestCase):
    def test_policy_is_enabled_and_hr_owned(self):
        cfg = json.loads((ROOT / "company/config/capability_scouting.json").read_text(encoding="utf-8"))
        self.assertEqual(cfg["version"], "2.0")
        self.assertTrue(cfg["enabled"])
        self.assertEqual(cfg["owner"], "HR & Capability Director")
        self.assertTrue(cfg["governing_gate"]["mandatory"])
        self.assertTrue(cfg["governing_gate"]["cannot_be_skipped"])
        self.assertEqual(cfg["governing_gate"]["sequence"][-1], "BUILD_LAST")
        self.assertIn("G0_RESEARCH_REUSE", cfg["approval_gates"])
        self.assertFalse(cfg["permanent_new_role"])
        self.assertTrue(cfg["cadence"]["event_driven"])
        self.assertEqual(cfg["cadence"]["periodic_active_days"], 7)
        self.assertIn("EXTERNAL_CAPABILITY_ADVANCE", cfg["gap_triggers"])
        self.assertIn("version_or_commit_pin", cfg["candidate_required_fields"])

    def test_repeated_manual_work_requires_repetition(self):
        with self.assertRaises(ValueError):
            build_gap("G1", "REPEATED_MANUAL_WORK", "manual task", repeat_count=1)
        gap = build_gap("G1", "REPEATED_MANUAL_WORK", "manual task", repeat_count=2, impact_metric="minutes")
        self.assertEqual(gap["status"], "GAP_OPEN")
        self.assertEqual(gap["owner"], "HR & Capability Director")

    def test_periodic_scouting_due(self):
        self.assertTrue(scouting_due(None, "2026-10-11T00:00:00+00:00"))
        self.assertFalse(scouting_due("2026-10-06T00:00:00+00:00", "2026-10-11T00:00:00+00:00", active=True))
        self.assertTrue(scouting_due("2026-10-01T00:00:00+00:00", "2026-10-11T00:00:00+00:00", active=True))
        self.assertFalse(scouting_due("2026-10-01T00:00:00+00:00", "2026-10-11T00:00:00+00:00", active=False))

    def test_hr_is_read_only_by_default(self):
        self.assertTrue(hr_may_execute("DISCOVER"))
        self.assertTrue(hr_may_execute("REVIEW_SECURITY_ADVISORIES"))
        self.assertFalse(hr_may_execute("INSTALL_TOOL"))
        self.assertFalse(hr_may_execute("AUTHENTICATE_ACCOUNT"))
        self.assertFalse(hr_may_execute("WRITE_EXTERNAL"))
        self.assertEqual(approval_gate_for("INSTALL_TOOL"), "OWNER_APPROVAL_REQUIRED")

    def test_candidate_requires_dossier_and_security_boundaries(self):
        candidate = {
            "gap_id": "G1",
            "candidate_name": "Example",
            "source_url_or_identifier": "maintainer/repo",
            "capability_added": "social research",
            "existing_capability_overlap": "partial",
            "maintenance_signal": "active",
            "license_or_terms": "MIT",
            "install_or_connection_method": "pinned package",
            "permissions_required": ["browser_debugger", "cookies"],
            "data_access": "authenticated browser session",
            "external_write_capable": True,
            "cost_model": "free",
            "security_risks": ["session exposure"],
            "rollback_plan": "remove isolated profile and package",
            "sandbox_test": "isolated research profile",
            "success_metric": "research coverage",
            "kill_trigger": "security regression",
            "version_or_commit_pin": "abc123",
        }
        result = validate_candidate(candidate)
        self.assertFalse(result["ready_for_council_review"])
        self.assertIn("external write capability requires an explicit write boundary", result["blockers"])
        self.assertIn("sensitive browser/session permissions require an isolation plan", result["blockers"])

        candidate["write_boundary"] = "read-only during pilot"
        candidate["isolation_plan"] = "separate browser profile and research accounts"
        result = validate_candidate(candidate)
        self.assertTrue(result["ready_for_council_review"])
        self.assertEqual(result["next_gate"], "SECURITY_REVIEW")

    def test_g0_research_reuse_gate_blocks_incomplete_evidence(self):
        result = validate_g0_evidence({
            "problem_statement": "Need a reusable motion component",
            "decision": "ADAPT",
        })
        self.assertFalse(result["g0_passed"])
        self.assertIn("official_or_maintainer_sources", result["missing_fields"])
        self.assertEqual(result["next_gate"], "G0_RESEARCH_REUSE")

    def test_g0_research_reuse_gate_allows_evidence_backed_adaptation(self):
        evidence = {
            "problem_statement": "Need a reusable motion component",
            "official_or_maintainer_sources": ["official docs"],
            "github_or_open_source_candidates": ["maintainer/repo"],
            "specialist_community_evidence": ["production issue and discussion review"],
            "known_failure_modes": ["unmount resource leak"],
            "existing_capability_overlap": "partial",
            "decision": "ADAPT",
            "expected_custom_loc": 120,
            "estimated_loc_avoided": 1800,
            "rollback_or_exit_plan": "remove adapter and restore previous renderer",
        }
        result = validate_g0_evidence(evidence)
        self.assertTrue(result["g0_passed"])
        self.assertEqual(result["next_gate"], "ARCHITECTURE_AND_DUPLICATION_REVIEW")

    def test_custom_build_requires_rejected_alternatives_and_justification(self):
        evidence = {
            "problem_statement": "Need a capability not covered by candidates",
            "official_or_maintainer_sources": ["official docs"],
            "github_or_open_source_candidates": ["candidate/a", "candidate/b"],
            "specialist_community_evidence": ["maintainer discussion"],
            "known_failure_modes": ["candidate cannot satisfy authority boundary"],
            "existing_capability_overlap": "none",
            "decision": "CUSTOM_BUILD_JUSTIFIED",
            "expected_custom_loc": 300,
            "estimated_loc_avoided": 0,
            "rollback_or_exit_plan": "feature flag and removable adapter",
        }
        blocked = validate_g0_evidence(evidence)
        self.assertFalse(blocked["g0_passed"])
        self.assertIn("custom build requires explicit justification", blocked["blockers"])
        self.assertIn("custom build requires documented rejected alternatives", blocked["blockers"])

        evidence["custom_build_justification"] = "No candidate preserves the required authority boundary."
        evidence["rejected_alternatives"] = ["candidate/a: authority leak", "candidate/b: unsupported platform"]
        allowed = validate_g0_evidence(evidence)
        self.assertTrue(allowed["g0_passed"])


if __name__ == "__main__":
    unittest.main()
