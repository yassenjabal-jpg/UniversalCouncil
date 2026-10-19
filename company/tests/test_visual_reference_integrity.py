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
        self.manifest = json.loads(
            (ROOT / "state/command-center/living-operations-reference-manifest.json").read_text()
        )
        for ref in self.manifest["references"]:
            path = self.root / ref["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((ROOT / ref["path"]).read_bytes())
        (self.root / "output.png").write_bytes(b"fixture output")
        (self.root / "comparison.md").write_text("fixture comparison")
        parent = self.manifest["references"][0]
        self.job = dict(
            job_id="test",
            parent_role=parent["role"],
            parent_sha256=parent["sha256"],
            reference_attached=True,
            allowed_delta="fixture",
            output_path="output.png",
            output_sha256=hashlib.sha256(b"fixture output").hexdigest(),
            comparison_evidence="comparison.md",
            review_status="MURTAKAZ_REVIEW_REQUIRED",
        )
        self.manifest["visual_jobs"] = [self.job]

    def test_valid_provenance(self):
        validate(self.root, self.manifest)

    def test_missing_or_modified_reference(self):
        path = self.root / self.manifest["references"][0]["path"]
        path.write_bytes(b"changed")
        with self.assertRaises(ValueError):
            validate(self.root, self.manifest)
        path.unlink()
        with self.assertRaises(ValueError):
            validate(self.root, self.manifest)

    def test_incomplete_or_forged_job(self):
        mutations = [
            ("parent_sha256", "bad"),
            ("reference_attached", False),
            ("allowed_delta", ""),
            ("comparison_evidence", "missing.md"),
            ("output_sha256", "bad"),
            ("review_status", "APPROVED_BY_AL_MURTAKAZ"),
            ("source_generation_id", self.manifest["rejected_recent_generations"][0]),
        ]
        for field, value in mutations:
            with self.subTest(field=field):
                manifest = copy.deepcopy(self.manifest)
                manifest["visual_jobs"][0][field] = value
                with self.assertRaises(ValueError):
                    validate(self.root, manifest)

    def test_approval_bound_to_delta(self):
        receipt = dict(
            decision="APPROVED_BY_AL_MURTAKAZ",
            job_id="test",
            output_sha256=self.job["output_sha256"],
            parent_sha256=self.job["parent_sha256"],
            allowed_delta="fixture",
            reviewer="fixture reviewer",
            review_mode="test",
        )
        (self.root / "review.json").write_text(json.dumps(receipt))
        self.job.update(
            review_status="APPROVED_BY_AL_MURTAKAZ", governance_review="review.json", workshop_review="review.json"
        )
        validate(self.root, self.manifest)
        self.job["allowed_delta"] = "different scope"
        with self.assertRaises(ValueError):
            validate(self.root, self.manifest)

    def test_governing_visual_direction_has_no_rejected_theme_vocabulary(self):
        manifest = json.loads(
            (ROOT / "state/command-center/living-operations-reference-manifest.json").read_text()
        )
        self.assertTrue(manifest["rules"]["unapproved_decorative_theme_forbidden"])
        self.assertTrue(manifest["rules"]["reference_observed_visual_language_only"])
        self.assertNotIn("architecture_decorative_theme_forbidden", manifest["rules"])

        visual_files = (
            "docs/operations/command-center/living-operations/01_VISUAL_BIBLE.md",
            "docs/operations/command-center/living-operations/15_P1_VISUAL_DIRECTION_LOCK.md",
            "docs/operations/command-center/living-operations/18_REFERENCE_ONLY_VISUAL_LOCK.md",
            "docs/operations/command-center/living-operations/19_REFERENCE_FIDELITY_AUDIT_AND_CONTRACT.md",
        )
        forbidden = ("architecture", "architectural", "عمارة", "معمار")
        for relative in visual_files:
            content = (ROOT / relative).read_text(encoding="utf-8").casefold()
            for term in forbidden:
                self.assertNotIn(term.casefold(), content, relative)
