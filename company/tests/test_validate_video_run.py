"""CLI tests use synthetic bytes; a successful test is not media quality proof."""

import contextlib
import copy
import io
import json
import unittest
from pathlib import Path

from company.tests import test_lean_video_production as fixtures
from tools.validate_video_run import load_record, main


class VideoReceiptCliTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.LeanProductionTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.directory = Path(self.fixture.tmp.name)

    def save(self, run, name):
        record = copy.deepcopy(run)
        for key, value in record["artifacts"].items():
            record["artifacts"][key] = Path(value).name
        for receipt in record["gates"].values():
            for check in receipt["checks"].values():
                check["evidence_ref"] = Path(check["evidence_ref"]).name
            if "delivery" in receipt:
                delivery = receipt["delivery"]
                delivery["measurement_evidence_ref"] = Path(delivery["measurement_evidence_ref"]).name
        path = self.directory / name
        path.write_text(json.dumps(record), encoding="utf-8")
        return path

    def invoke(self, record, pilot=None):
        args = ["--record", str(record), "--gate", "Final QC"]
        if pilot:
            args += ["--system-pilot", str(pilot)]
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(args)
        return code, json.loads(output.getvalue())

    def test_pilot_and_episode_cli_resolve_all_evidence_paths(self):
        pilot = self.save(self.fixture.pilot, "pilot.json")
        episode = self.save(self.fixture.episode, "episode.json")
        self.assertEqual(load_record(pilot)["artifacts"], self.fixture.pilot["artifacts"])
        for record, proof in [(pilot, None), (episode, pilot)]:
            code, receipt = self.invoke(record, proof)
            self.assertEqual(code, 0)
            self.assertEqual(receipt["status"], "PASS")
            self.assertFalse(receipt["publication_authorized"])
            self.assertFalse(receipt["main_merge_authorized"])

    def test_missing_malformed_unreviewed_and_stale_records_block(self):
        record = self.directory / "record.json"
        code, receipt = self.invoke(record)
        self.assertEqual((code, receipt["status"]), (1, "BLOCKED"))
        for content in ["{", "null", "[]"]:
            record.write_text(content, encoding="utf-8")
            self.assertEqual(self.invoke(record)[0], 1)
        template = Path(__file__).resolve().parents[2] / "docs/templates/media/LEAN_VIDEO_RUN.json"
        self.assertEqual(self.invoke(template)[0], 1)
        run = copy.deepcopy(self.fixture.pilot)
        run["gates"]["Final QC"]["delivery"]["export_sha256"] = "stale"
        self.assertEqual(self.invoke(self.save(run, "stale.json"))[0], 1)


if __name__ == "__main__":
    unittest.main()
