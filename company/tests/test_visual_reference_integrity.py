import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.command_center_visual_reference_validate import validate

ROOT = Path(__file__).resolve().parents[2]


class VisualReferenceIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        manifest_path = ROOT / "state" / "command-center" / "living-operations-reference-manifest.json"
        self.manifest = json.loads(manifest_path.read_text())

        for ref in self.manifest["references"]:
            path = self.root / ref["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((ROOT / ref["path"]).read_bytes())

        for key in ("object_inventory_path", "production_protocol_path"):
            source_path = self.manifest[key]
            target = self.root / source_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / source_path).read_bytes())

        (self.root / "output.png").write_bytes(b"fixture output")
        (self.root / "comparison.md").write_text("fixture comparison")

        parent = self.manifest["references"][0]
        self.binding = {
            "job_id": "test",
            "parent_role": parent["role"],
            "parent_path": parent["path"],
            "parent_sha256": parent["sha256"],
            "tool_name": "fixture-reference-editor",
            "production_mode": "REFERENCE_EDIT",
            "tool_received_reference_bytes": True,
            "single_screen": True,
            "phase": "PRE_RENDER",
            "render_not_started": True,
            "tool_reference_locator": "fixture://canonical-home",
            "screen_inventory_id": parent["role"],
            "member_inventory_verified": True,
        }
        self.binding_path = self.root / "reference-binding.json"
        self.binding_path.write_text(json.dumps(self.binding))

        self.preflight_job = {
            "job_id": "test",
            "state": "PREFLIGHT_REGISTERED",
            "parent_role": parent["role"],
            "parent_sha256": parent["sha256"],
            "production_mode": "REFERENCE_EDIT",
            "tool_name": "fixture-reference-editor",
            "single_screen_only": True,
            "preflight_registered": True,
            "screen_inventory_id": parent["role"],
            "member_inventory_verified": True,
            "allowed_delta": "fixture",
            "reference_binding_evidence": "reference-binding.json",
        }
        self.manifest["visual_jobs"] = [self.preflight_job]

    def rendered_job(self, state="RENDERED_REVIEW_REQUIRED"):
        job = copy.deepcopy(self.preflight_job)
        job.update(
            state=state,
            output_path="output.png",
            output_sha256=hashlib.sha256(b"fixture output").hexdigest(),
            comparison_evidence="comparison.md",
            render_started_after_preflight=True,
        )
        return job

    def test_valid_preflight_provenance(self):
        validate(self.root, self.manifest)

    def test_valid_rendered_provenance(self):
        self.manifest["visual_jobs"] = [self.rendered_job()]
        validate(self.root, self.manifest)

    def test_missing_or_modified_reference(self):
        path = self.root / self.manifest["references"][0]["path"]
        path.write_bytes(b"changed")
        with self.assertRaises(ValueError):
            validate(self.root, self.manifest)
        path.unlink()
        with self.assertRaises(ValueError):
            validate(self.root, self.manifest)

    def test_preflight_blocks_unsafe_visual_paths(self):
        mutations = [
            ("parent_sha256", "bad"),
            ("production_mode", "TEXT_TO_IMAGE"),
            ("tool_name", ""),
            ("single_screen_only", False),
            ("preflight_registered", False),
            ("screen_inventory_id", "wrong-screen"),
            ("member_inventory_verified", False),
            ("reference_binding_evidence", "missing.json"),
            ("source_generation_id", "generated-parent"),
        ]
        for field, value in mutations:
            with self.subTest(field=field):
                manifest = copy.deepcopy(self.manifest)
                manifest["visual_jobs"][0][field] = value
                with self.assertRaises(ValueError):
                    validate(self.root, manifest)

    def test_reference_binding_receipt_is_fail_closed(self):
        mutations = [
            ("parent_sha256", "bad"),
            ("tool_received_reference_bytes", False),
            ("single_screen", False),
            ("phase", "POST_RENDER"),
            ("render_not_started", False),
            ("tool_reference_locator", ""),
            ("screen_inventory_id", "wrong-screen"),
            ("member_inventory_verified", False),
        ]
        for field, value in mutations:
            with self.subTest(field=field):
                binding = copy.deepcopy(self.binding)
                binding[field] = value
                self.binding_path.write_text(json.dumps(binding))
                with self.assertRaises(ValueError):
                    validate(self.root, self.manifest)
        self.binding_path.write_text(json.dumps(self.binding))

    def test_preflight_state_cannot_claim_rendered_output(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["visual_jobs"][0]["output_path"] = "output.png"
        with self.assertRaises(ValueError):
            validate(self.root, manifest)

    def test_rendered_job_requires_output_and_preflight_ancestry(self):
        job = self.rendered_job()
        self.manifest["visual_jobs"] = [job]
        validate(self.root, self.manifest)

        mutations = [
            ("output_path", "missing.png"),
            ("output_sha256", "bad"),
            ("comparison_evidence", "missing.md"),
            ("render_started_after_preflight", False),
        ]
        for field, value in mutations:
            with self.subTest(field=field):
                manifest = copy.deepcopy(self.manifest)
                manifest["visual_jobs"][0][field] = value
                with self.assertRaises(ValueError):
                    validate(self.root, manifest)

    def test_approval_bound_to_delta(self):
        job = self.rendered_job("APPROVED_BY_AL_MURTAKAZ")
        receipt = {
            "decision": "APPROVED_BY_AL_MURTAKAZ",
            "job_id": "test",
            "output_sha256": job["output_sha256"],
            "parent_sha256": job["parent_sha256"],
            "allowed_delta": "fixture",
            "reviewer": "fixture reviewer",
            "review_mode": "test",
        }
        (self.root / "review.json").write_text(json.dumps(receipt))
        job.update(governance_review="review.json", workshop_review="review.json")
        self.manifest["visual_jobs"] = [job]
        validate(self.root, self.manifest)

        self.manifest["visual_jobs"][0]["allowed_delta"] = "different scope"
        with self.assertRaises(ValueError):
            validate(self.root, self.manifest)

    def test_manifest_locks_out_repeated_drift_mechanisms(self):
        rules = self.manifest["rules"]
        self.assertTrue(rules["freeform_text_to_image_for_canonical_ui_forbidden"])
        self.assertTrue(rules["multi_screen_composite_forbidden"])
        self.assertTrue(rules["generated_image_parent_forbidden"])
        self.assertTrue(rules["preflight_visual_job_registration_required"])
        self.assertTrue(rules["actual_reference_binding_receipt_required"])
        self.assertTrue(rules["eligible_tool_must_consume_reference_bytes"])
        self.assertTrue(rules["fail_closed_when_reference_capable_tool_unavailable"])

    def test_governing_visual_direction_has_no_rejected_theme_vocabulary(self):
        manifest_path = ROOT / "state" / "command-center" / "living-operations-reference-manifest.json"
        manifest = json.loads(manifest_path.read_text())
        self.assertTrue(manifest["rules"]["unapproved_decorative_theme_forbidden"])
        self.assertTrue(manifest["rules"]["reference_observed_visual_language_only"])
        self.assertNotIn("architecture_decorative_theme_forbidden", manifest["rules"])

        visual_root = ROOT / "docs" / "operations" / "command-center" / "living-operations"
        visual_files = (
            visual_root / "01_VISUAL_BIBLE.md",
            visual_root / "15_P1_VISUAL_DIRECTION_LOCK.md",
            visual_root / "18_REFERENCE_ONLY_VISUAL_LOCK.md",
            visual_root / "19_REFERENCE_FIDELITY_AUDIT_AND_CONTRACT.md",
        )
        forbidden = ("architecture", "architectural", "عمارة", "معمار")
        for visual_file in visual_files:
            content = visual_file.read_text(encoding="utf-8").casefold()
            for term in forbidden:
                self.assertNotIn(term.casefold(), content, str(visual_file))
