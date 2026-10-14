import copy
import json
import unittest
from pathlib import Path

from company.runtime.media_execution_recovery import (
    MediaExecutionRecoveryError,
    next_recovery_action,
    resolve_handoff_state,
    validate_execution_recovery_policy,
    validate_handoff_checkpoint,
)


ROOT = Path(__file__).resolve().parents[2]
CONFIG = json.loads((ROOT / "company/config/media_venture.json").read_text(encoding="utf-8"))
POLICY = CONFIG["execution_recovery"]


class MediaExecutionRecoveryTests(unittest.TestCase):
    def checkpoint(self):
        return {
            "episode_id": "pilot-01",
            "stage_id": "motion",
            "action_id": "ae-001",
            "application": "After Effects",
            "application_version": "2025",
            "project_path": "C:/studio/pilot-01/pilot-01.aep",
            "artifact_or_project_version": "v003",
            "expected_postcondition": "composition saved with target layer present",
            "last_verified_state": "project open and v003 saved",
            "next_safe_action": "render motion preview",
            "state": "CHECKPOINT_SAVED",
        }

    def test_policy_is_valid_and_fail_closed(self):
        self.assertTrue(validate_execution_recovery_policy(POLICY))
        broken = copy.deepcopy(POLICY)
        broken["unknown_is_never_success"] = False
        with self.assertRaises(MediaExecutionRecoveryError):
            validate_execution_recovery_policy(broken)

    def test_checkpoint_requires_recoverable_identity(self):
        self.assertTrue(validate_handoff_checkpoint(self.checkpoint(), POLICY))
        broken = self.checkpoint()
        broken.pop("project_path")
        with self.assertRaises(MediaExecutionRecoveryError):
            validate_handoff_checkpoint(broken, POLICY)

    def test_success_without_independent_postcondition_is_unknown(self):
        self.assertEqual(
            resolve_handoff_state("SUCCEEDED", postcondition_verified=False),
            "UNKNOWN",
        )
        self.assertEqual(
            resolve_handoff_state("SUCCEEDED", postcondition_verified=True),
            "POSTCONDITION_VERIFIED",
        )

    def test_timeout_and_stall_are_unknown_not_failure_or_success(self):
        for state in {"TIMEOUT", "STALLED", "UNKNOWN"}:
            self.assertEqual(resolve_handoff_state(state, postcondition_verified=False), "UNKNOWN")

    def test_unknown_reconciles_before_any_replay(self):
        self.assertEqual(
            next_recovery_action("UNKNOWN", retry_count=0, policy=POLICY),
            "RECONCILE_JOURNAL_AND_PROJECT_CHECKPOINT",
        )

    def test_failed_action_gets_only_one_same_route_retry(self):
        self.assertEqual(
            next_recovery_action("FAILED", retry_count=0, policy=POLICY),
            "RESUME_CHECKPOINT_AND_RETRY_SAME_ROUTE",
        )
        self.assertEqual(
            next_recovery_action("FAILED", retry_count=1, policy=POLICY),
            "HOLD_AND_ESCALATE",
        )

    def test_authorized_fallback_is_used_only_after_retry_budget(self):
        self.assertEqual(
            next_recovery_action(
                "FAILED",
                retry_count=1,
                policy=POLICY,
                authorized_fallback_available=True,
            ),
            "USE_AUTHORIZED_FALLBACK",
        )

    def test_negative_retry_count_fails_closed(self):
        with self.assertRaises(MediaExecutionRecoveryError):
            next_recovery_action("FAILED", retry_count=-1, policy=POLICY)


if __name__ == "__main__":
    unittest.main()
