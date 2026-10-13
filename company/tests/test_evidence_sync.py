import copy
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from company.runtime.evidence_sync import (
    EvidenceSyncError,
    _load_json,
    _parse_observed_at,
    apply_receipt_to_registry,
    discover_receipts,
    latest_by_capability,
    resolve_source_root,
    sync_repository,
    validate_imported_evidence,
    validate_receipt,
    validate_sync_config,
)

ROOT = Path(__file__).resolve().parents[2]
BASE_REGISTRY = json.loads((ROOT / "company/config/tool_authority.json").read_text(encoding="utf-8"))


class EvidenceSyncTests(unittest.TestCase):
    def make_source(self, root: Path):
        project = root / "project"
        receipt_dir = project / ".council/capability-receipts"
        receipt_dir.mkdir(parents=True)
        artifact = project / "proof.txt"
        artifact.write_text("verified desktop capability\n", encoding="utf-8")
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        subprocess.run(["git", "init"], cwd=project, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Evidence Test"], cwd=project, check=True)
        subprocess.run(["git", "config", "user.email", "evidence@example.test"], cwd=project, check=True)
        subprocess.run(["git", "add", "proof.txt"], cwd=project, check=True)
        subprocess.run(["git", "commit", "-m", "proof"], cwd=project, check=True, capture_output=True)
        source_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=project,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        receipt = {
            "schema_version": "1.0",
            "receipt_id": "test-desktop",
            "source_project": "TestProject",
            "source_commit": source_commit,
            "observed_at": "2026-10-12T12:00:00+03:00",
            "capability_id": "desktop_computer_use",
            "status": "RUNTIME_VERIFIED",
            "evidence_level": "HOST_INVOKED",
            "verified_scope": ["screenshot", "physical_click"],
            "unverified_scope": ["credential_entry"],
            "artifacts": [{"path": "proof.txt", "sha256": digest}],
        }
        (receipt_dir / "desktop.json").write_text(json.dumps(receipt), encoding="utf-8")
        source = {
            "id": "test-project",
            "project_id": "TestProject",
            "enabled": True,
            "root_env": "TEST_PROJECT_ROOT",
            "receipt_glob": ".council/capability-receipts/*.json",
            "allowed_capability_ids": ["desktop_computer_use"],
            "max_receipt_age_days": 30,
            "revoked_receipt_ids": [],
            "authority_bindings": {
                "desktop_computer_use": {
                    "operations": [
                        "desktop_computer_use.observe",
                        "desktop_computer_use.control",
                    ],
                    "allowed_evidence_levels": ["HOST_INVOKED"],
                    "allowed_verified_scope": ["screenshot", "physical_click"],
                    "operation_verified_scope": {
                        "desktop_computer_use.observe": ["screenshot"],
                        "desktop_computer_use.control": ["physical_click"],
                    },
                }
            },
        }
        return project, source, receipt

    def make_repo(self, root: Path, source):
        repo = root / "repo"
        (repo / "company/config").mkdir(parents=True)
        cfg = {
            "version": "1.0",
            "import_dir": "company/evidence/imported",
            "sources": [source],
        }
        (repo / "company/config/evidence_sync.json").write_text(json.dumps(cfg), encoding="utf-8")
        (repo / "company/config/tool_authority.json").write_text(json.dumps(BASE_REGISTRY), encoding="utf-8")
        return repo

    def test_sync_imports_receipt_and_preserves_authority(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project, source, receipt = self.make_source(root)
            source_commit = receipt["source_commit"]
            repo = self.make_repo(root, source)
            before = copy.deepcopy(BASE_REGISTRY)
            result = sync_repository(
                repo,
                env={"TEST_PROJECT_ROOT": str(project)},
                apply=True,
            )
            self.assertTrue(result["registry_changed"])
            imported = repo / "company/evidence/imported/test-project/desktop_computer_use.json"
            self.assertTrue(imported.exists())
            after = json.loads((repo / "company/config/tool_authority.json").read_text(encoding="utf-8"))
            for operation in ("desktop_computer_use.observe", "desktop_computer_use.control"):
                old = next(x for x in before["capabilities"] if x["operation"] == operation)
                new = next(x for x in after["capabilities"] if x["operation"] == operation)
                for field in (
                    "classification",
                    "authentication_class",
                    "effect",
                    "approval_policy",
                    "allowed_scope",
                    "prohibited_scope",
                    "enforcement",
                ):
                    self.assertEqual(old[field], new[field])
                self.assertEqual(new["source_or_pin"], source_commit)
                self.assertEqual(new["evidence_receipt"], imported.relative_to(repo).as_posix())
                expected_scope = ["screenshot"] if operation.endswith("observe") else ["physical_click"]
                self.assertEqual(new["verified_scope"], expected_scope)

    def test_receipt_cannot_claim_authority_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project, source, receipt = self.make_source(root)
            receipt["approval_policy"] = "READ_ALLOWED"
            with self.assertRaises(EvidenceSyncError):
                validate_receipt(receipt, source, project)

    def test_receipt_cannot_overclaim_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project, source, receipt = self.make_source(root)
            receipt["verified_scope"].append("external_publish")
            with self.assertRaises(EvidenceSyncError):
                validate_receipt(receipt, source, project)

    def test_artifact_hash_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project, source, receipt = self.make_source(root)
            receipt["artifacts"][0]["sha256"] = "0" * 64
            with self.assertRaises(EvidenceSyncError):
                validate_receipt(receipt, source, project)

    def test_future_revoked_and_foreign_commit_receipts_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project, source, receipt = self.make_source(root)

            future = copy.deepcopy(receipt)
            future["observed_at"] = "2099-01-01T00:00:00+00:00"
            with self.assertRaises(EvidenceSyncError):
                validate_receipt(future, source, project)

            revoked_source = copy.deepcopy(source)
            revoked_source["revoked_receipt_ids"] = [receipt["receipt_id"]]
            with self.assertRaises(EvidenceSyncError):
                validate_receipt(receipt, revoked_source, project)

            foreign = copy.deepcopy(receipt)
            foreign["source_commit"] = "b" * 40
            with self.assertRaises(EvidenceSyncError):
                validate_receipt(foreign, source, project)

    def test_unavailable_source_is_nonfatal_and_does_not_change_registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, source, _ = self.make_source(root)
            source.pop("root_env")
            source.pop("root_hint", None)
            repo = self.make_repo(root, source)
            result = sync_repository(repo, env={}, apply=True)
            self.assertEqual(result["unavailable_sources"], ["test-project"])
            self.assertFalse(result["registry_changed"])

    def test_json_and_sync_config_validation_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            missing = root / "missing.json"
            with self.assertRaises(EvidenceSyncError):
                _load_json(missing)

            non_object = root / "array.json"
            non_object.write_text("[]", encoding="utf-8")
            with self.assertRaises(EvidenceSyncError):
                _load_json(non_object)

            project, source, _ = self.make_source(root)
            self.assertTrue(project.exists())
            bad_configs = [
                {"version": "2.0", "sources": []},
                {"version": "1.0", "sources": {}},
                {"version": "1.0", "sources": ["bad"]},
                {"version": "1.0", "sources": [{k: v for k, v in source.items() if k != "id"}]},
                {"version": "1.0", "sources": [source, copy.deepcopy(source)]},
            ]
            overbound = copy.deepcopy(source)
            overbound["authority_bindings"]["other"] = copy.deepcopy(
                overbound["authority_bindings"]["desktop_computer_use"]
            )
            bad_configs.append({"version": "1.0", "sources": [overbound]})
            for cfg in bad_configs:
                with self.subTest(cfg=cfg):
                    with self.assertRaises(EvidenceSyncError):
                        validate_sync_config(cfg)

    def test_source_hint_and_timestamp_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project, source, _ = self.make_source(root)
            hinted = copy.deepcopy(source)
            hinted.pop("root_env")
            hinted["root_hint"] = str(project)
            self.assertEqual(resolve_source_root(hinted, env={}), project.resolve())

            with self.assertRaises(EvidenceSyncError):
                _parse_observed_at("not-a-date")
            with self.assertRaises(EvidenceSyncError):
                _parse_observed_at("2026-10-12T12:00:00")

    def test_receipt_field_and_artifact_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project, source, receipt = self.make_source(root)

            variants = []

            missing = copy.deepcopy(receipt)
            missing.pop("status")
            variants.append(missing)

            for field, value in (
                ("schema_version", "2.0"),
                ("source_project", "OtherProject"),
                ("capability_id", "other_capability"),
                ("status", "UNVERIFIED"),
                ("source_commit", "abc"),
                ("observed_at", "not-a-date"),
                ("observed_at", "2026-10-12T12:00:00"),
                ("verified_scope", []),
                ("unverified_scope", "not-a-list"),
                ("evidence_level", "BOUNDARY_ENFORCED"),
                ("artifacts", []),
            ):
                variant = copy.deepcopy(receipt)
                variant[field] = value
                variants.append(variant)

            malformed_artifact = copy.deepcopy(receipt)
            malformed_artifact["artifacts"] = [{"path": "proof.txt"}]
            variants.append(malformed_artifact)

            escape_target = root / "outside.txt"
            escape_target.write_text("outside", encoding="utf-8")
            escaping = copy.deepcopy(receipt)
            escaping["artifacts"] = [
                {
                    "path": "../outside.txt",
                    "sha256": hashlib.sha256(escape_target.read_bytes()).hexdigest(),
                }
            ]
            variants.append(escaping)

            missing_artifact = copy.deepcopy(receipt)
            missing_artifact["artifacts"] = [{"path": "missing.txt", "sha256": "0" * 64}]
            variants.append(missing_artifact)

            for variant in variants:
                with self.subTest(variant=variant):
                    with self.assertRaises(EvidenceSyncError):
                        validate_receipt(variant, source, project)

    def test_discovery_latest_selection_and_missing_operation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project, source, receipt = self.make_source(root)

            unavailable = copy.deepcopy(source)
            unavailable.pop("root_env")
            self.assertEqual(discover_receipts(unavailable, env={}), [])

            older = copy.deepcopy(receipt)
            older["observed_at"] = "2026-10-11T12:00:00+03:00"
            newer = copy.deepcopy(receipt)
            newer["observed_at"] = "2026-10-13T12:00:00+03:00"
            selected = latest_by_capability([(project / "older.json", older), (project / "newer.json", newer)])
            self.assertEqual(
                selected["desktop_computer_use"][1]["observed_at"],
                newer["observed_at"],
            )

            broken_source = copy.deepcopy(source)
            broken_source["authority_bindings"]["desktop_computer_use"]["operations"] = ["missing.operation"]
            with self.assertRaises(EvidenceSyncError):
                apply_receipt_to_registry(
                    BASE_REGISTRY,
                    receipt,
                    broken_source,
                    "company/evidence/imported/test.json",
                )

    def test_disabled_source_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project, source, _ = self.make_source(root)
            source["enabled"] = False
            repo = self.make_repo(root, source)
            result = sync_repository(
                repo,
                env={"TEST_PROJECT_ROOT": str(project)},
                apply=False,
            )
            self.assertEqual(result["imported"], [])
            self.assertFalse(result["registry_changed"])

    def test_imported_evidence_validation_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project, source, _ = self.make_source(root)
            repo = self.make_repo(root, source)
            sync_repository(
                repo,
                env={"TEST_PROJECT_ROOT": str(project)},
                apply=True,
            )
            cfg_path = repo / "company/config/evidence_sync.json"
            registry_path = repo / "company/config/tool_authority.json"
            imported_path = repo / "company/evidence/imported/test-project/desktop_computer_use.json"
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            original_receipt = json.loads(imported_path.read_text(encoding="utf-8"))

            self.assertTrue(validate_imported_evidence(repo, cfg, registry))

            duplicate_cfg = copy.deepcopy(cfg)
            duplicate_source = copy.deepcopy(duplicate_cfg["sources"][0])
            duplicate_source["id"] = "duplicate-source"
            duplicate_cfg["sources"].append(duplicate_source)
            with self.assertRaises(EvidenceSyncError):
                validate_imported_evidence(repo, duplicate_cfg, registry)

            unbound_registry = copy.deepcopy(registry)
            github = next(x for x in unbound_registry["capabilities"] if x["operation"] == "github.read")
            github["evidence_receipt"] = "company/evidence/imported/test-project/desktop_computer_use.json"
            with self.assertRaises(EvidenceSyncError):
                validate_imported_evidence(repo, cfg, unbound_registry)

            observe = next(x for x in registry["capabilities"] if x["operation"] == "desktop_computer_use.observe")
            mutations = [
                ("path_escape", lambda r, c: r.__setitem__("evidence_receipt", "../outside.json")),
                (
                    "missing_path",
                    lambda r, c: r.__setitem__(
                        "evidence_receipt",
                        "company/evidence/imported/test-project/missing.json",
                    ),
                ),
                ("missing_field", lambda r, c: c.pop("status")),
                ("authority_field", lambda r, c: c.__setitem__("effect", "WRITE")),
                ("source_project", lambda r, c: c.__setitem__("source_project", "OtherProject")),
                ("capability", lambda r, c: c.__setitem__("capability_id", "other_capability")),
                ("status", lambda r, c: c.__setitem__("status", "UNVERIFIED")),
                ("source_pin", lambda r, c: r.__setitem__("source_or_pin", "b" * 40)),
                ("evidence_level", lambda r, c: r.__setitem__("evidence_level", "SCRIPT_TESTED")),
                ("date", lambda r, c: r.__setitem__("last_verified_at", "2026-10-11")),
            ]

            for name, mutate in mutations:
                with self.subTest(name=name):
                    case_registry = copy.deepcopy(registry)
                    case_receipt = copy.deepcopy(original_receipt)
                    case_observe = next(
                        x for x in case_registry["capabilities"] if x["operation"] == "desktop_computer_use.observe"
                    )
                    mutate(case_observe, case_receipt)
                    imported_path.write_text(json.dumps(case_receipt), encoding="utf-8")
                    with self.assertRaises(EvidenceSyncError):
                        validate_imported_evidence(repo, cfg, case_registry)

            imported_path.write_text(json.dumps(original_receipt), encoding="utf-8")
            self.assertEqual(observe["source_or_pin"], original_receipt["source_commit"])


if __name__ == "__main__":
    unittest.main()
