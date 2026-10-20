from __future__ import annotations

import copy
import json
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from company.runtime.hybrid_execution import HybridExecutionError, enforce_tool_authority, plan_action
from company.runtime.evidence_sync import (
    EvidenceState,
    EvidenceSyncError,
    build_imported_receipt,
    receipt_evidence_state,
    validate_receipt,
)


ROOT = Path(__file__).resolve().parents[2]
FIXED_NOW = datetime(2026, 10, 13, 19, tzinfo=timezone.utc)
BASE_CFG = json.loads((ROOT / "company/config/hybrid_execution.json").read_text(encoding="utf-8"))
BASE_REGISTRY = json.loads((ROOT / "company/config/tool_authority.json").read_text(encoding="utf-8"))


class Phase2R7EvidenceModelTests(unittest.TestCase):
    def make_source(self, root: Path):
        project = root / "source"
        project.mkdir()
        (project / "proof.txt").write_text("proof\n", encoding="utf-8")
        subprocess.run(["git", "init"], cwd=project, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Evidence Test"], cwd=project, check=True)
        subprocess.run(["git", "config", "user.email", "evidence@example.test"], cwd=project, check=True)
        subprocess.run(["git", "add", "proof.txt"], cwd=project, check=True)
        subprocess.run(["git", "commit", "-m", "proof"], cwd=project, check=True, capture_output=True)
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=project,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        proof = subprocess.run(
            ["git", "show", f"{commit}:proof.txt"],
            cwd=project,
            check=True,
            capture_output=True,
        ).stdout
        import hashlib

        source = {
            "id": "source",
            "project_id": "SourceProject",
            "repository_identity": "local:SourceProject",
            "component": "desktop_bridge",
            "expected_host": "YASSIN",
            "enabled": True,
            "receipt_glob": "*.json",
            "allowed_capability_ids": ["desktop_computer_use"],
            "allow_legacy_historical": True,
            "max_receipt_age_days": 7,
            "revoked_receipt_ids": [],
            "authority_bindings": {
                "desktop_computer_use": {
                    "operations": ["desktop_computer_use.observe"],
                    "allowed_evidence_levels": ["HOST_INVOKED"],
                    "allowed_verified_scope": ["status"],
                    "operation_verified_scope": {
                        "desktop_computer_use.observe": ["status"],
                    },
                }
            },
        }
        legacy = {
            "schema_version": "1.0",
            "receipt_id": "legacy",
            "source_project": "SourceProject",
            "source_commit": commit,
            "observed_at": "2026-10-13T18:00:00+00:00",
            "capability_id": "desktop_computer_use",
            "status": "RUNTIME_VERIFIED",
            "evidence_level": "HOST_INVOKED",
            "verified_scope": ["status"],
            "unverified_scope": [],
            "artifacts": [{"path": "proof.txt", "sha256": hashlib.sha256(proof).hexdigest()}],
        }
        current = {
            **legacy,
            "schema_version": "1.1",
            "receipt_id": "current",
            "source_repository": "local:SourceProject",
            "component": "desktop_bridge",
            "component_version": commit,
            "host": "YASSIN",
            "session_id": "phase2-r7-test",
            "expires_at": "2026-10-20T00:00:00+00:00",
            "verifier": "UniversalCouncil.evidence_sync",
            "verifier_version": "1.1",
        }
        return project, source, legacy, current

    def test_legacy_receipt_is_historical_not_current(self):
        with tempfile.TemporaryDirectory() as tmp:
            project, source, legacy, _ = self.make_source(Path(tmp))
            self.assertTrue(validate_receipt(legacy, source, project, as_of=FIXED_NOW))
            state = receipt_evidence_state(
                legacy,
                source,
                as_of=datetime(2026, 10, 13, 19, tzinfo=timezone.utc),
            )
            self.assertEqual(state, EvidenceState.HISTORICAL)

    def test_v11_receipt_can_be_current_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            project, source, _, current = self.make_source(Path(tmp))
            self.assertTrue(validate_receipt(current, source, project, as_of=FIXED_NOW))
            state = receipt_evidence_state(
                current,
                source,
                as_of=datetime(2026, 10, 13, 19, tzinfo=timezone.utc),
            )
            self.assertEqual(state, EvidenceState.CURRENT_VERIFIED)
            imported = build_imported_receipt(
                current,
                source,
                ingested_at="2026-10-13T19:05:00+00:00",
            )
            self.assertEqual(imported["evidence_state"], EvidenceState.CURRENT_VERIFIED.value)
            metadata = imported["evidence_metadata"]
            self.assertEqual(metadata["source_repository"], "local:SourceProject")
            self.assertEqual(metadata["host"], "YASSIN")
            self.assertEqual(metadata["session_id"], "phase2-r7-test")
            self.assertEqual(metadata["ingested_at"], "2026-10-13T19:05:00+00:00")
            self.assertEqual(metadata["verifier_version"], "1.1")

    def test_v11_binding_mismatch_and_expiry_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            project, source, _, current = self.make_source(Path(tmp))
            for field, value in (
                ("source_repository", "foreign:repo"),
                ("component", "other"),
                ("host", "OTHER"),
                ("session_id", ""),
                ("verifier", ""),
                ("verifier_version", ""),
            ):
                variant = copy.deepcopy(current)
                variant[field] = value
                with self.subTest(field=field):
                    with self.assertRaises(EvidenceSyncError):
                        validate_receipt(variant, source, project, as_of=FIXED_NOW)

            expired = copy.deepcopy(current)
            expired["expires_at"] = "2026-10-13T17:00:00+00:00"
            self.assertEqual(
                receipt_evidence_state(
                    expired,
                    source,
                    as_of=datetime(2026, 10, 13, 19, tzinfo=timezone.utc),
                ),
                EvidenceState.STALE,
            )

    def test_revoked_receipt_state_is_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            project, source, _, current = self.make_source(Path(tmp))
            revoked_source = copy.deepcopy(source)
            revoked_source["revoked_receipt_ids"] = [current["receipt_id"]]
            self.assertEqual(
                receipt_evidence_state(
                    current,
                    revoked_source,
                    as_of=datetime(2026, 10, 13, 19, tzinfo=timezone.utc),
                ),
                EvidenceState.REVOKED,
            )
            with self.assertRaises(EvidenceSyncError):
                validate_receipt(current, revoked_source, project, as_of=FIXED_NOW)

    def test_gui_execution_cannot_exceed_verified_evidence_scope(self):
        registry = copy.deepcopy(BASE_REGISTRY)
        observe = next(item for item in registry["capabilities"] if item["operation"] == "desktop_computer_use.observe")
        control = next(item for item in registry["capabilities"] if item["operation"] == "desktop_computer_use.control")
        for record, verified_scope in (
            (observe, ["status", "list_windows", "inspect_ui"]),
            (control, ["focus"]),
        ):
            metadata = {"expires_at": "2026-10-20T00:00:00+00:00", "test_fixture": True}
            record["evidence_state"] = "CURRENT_VERIFIED"
            record["historical_capability"] = dict(metadata)
            record["current_verified_capability"] = dict(metadata)
            record["verified_scope"] = verified_scope
            record["last_verified_at"] = "2026-10-13"

        status = plan_action(
            {"id": "status", "gui_request": {"action": "status"}},
            BASE_CFG,
        )
        self.assertEqual(
            enforce_tool_authority(status, registry, principal="technical_operator", as_of=FIXED_NOW)["operation"],
            "desktop_computer_use.observe",
        )

        focus = plan_action(
            {"id": "focus", "gui_request": {"action": "focus"}},
            BASE_CFG,
        )
        self.assertEqual(
            enforce_tool_authority(focus, registry, principal="technical_operator", as_of=FIXED_NOW)["operation"],
            "desktop_computer_use.control",
        )

        set_value = plan_action(
            {"id": "set", "gui_request": {"action": "set_value"}},
            BASE_CFG,
        )
        with self.assertRaises(HybridExecutionError):
            enforce_tool_authority(set_value, registry, principal="technical_operator", as_of=FIXED_NOW)

        screenshot = plan_action(
            {"id": "shot", "gui_request": {"action": "screenshot"}},
            BASE_CFG,
        )
        with self.assertRaises(HybridExecutionError):
            enforce_tool_authority(screenshot, registry, principal="technical_operator", as_of=FIXED_NOW)


if __name__ == "__main__":
    unittest.main()
