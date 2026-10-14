"""Synthetic bytes test policy contracts; these are never real-media QC proof."""

import copy
import json
import tempfile
import unittest
from pathlib import Path
from company.runtime.lean_video_production import (
    GATES,
    GATE_INPUTS,
    GATE_CHECKS,
    GATE_AUTHORITIES,
    CRAFT_OUTPUTS_BY_STAGE,
    ProductionWorkflowError,
    artifact_hash,
    validate_production_config,
    validate_alignment,
    validate_gate,
    select_edit_route,
)

ROOT = Path(__file__).resolve().parents[2]


class LeanProductionTests(unittest.TestCase):
    def setUp(self):
        self.cfg = json.loads((ROOT / "company/config/channel_operating_system.json").read_text(encoding="utf-8"))
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.pilot = self.make_run("system_pilot", "synthetic-pilot")
        self.episode = self.make_run("episode", "synthetic-episode")

    def test_delivery_route_is_ae_and_descript_is_rough_only(self):
        with self.assertRaises(ProductionWorkflowError):
            select_edit_route(self.cfg)
        route = select_edit_route(self.cfg, current_probe=self.valid_probe())
        self.assertEqual(route["tool"], "Adobe After Effects 2026")
        self.assertEqual(route["transport"], "native_project_automation")
        rough = select_edit_route(self.cfg, purpose="rough_prep")
        self.assertEqual(rough["tool"], "Descript")
        self.assertFalse(rough["eligible_for_final_delivery"])
        with self.assertRaises(ProductionWorkflowError):
            select_edit_route(self.cfg, primary_failed=True, current_probe=self.valid_probe())

    def make_run(self, kind, identity):
        run = dict(
            kind=kind,
            episode_id=identity,
            system_version="2.0",
            writer_id="writer",
            editor_id="editor",
            mix_author_id="mixer",
            tool="Adobe After Effects 2026",
            localized_variant_requested=False,
            artifacts={},
            craft_outputs={},
            gates={},
            metrics={name: 1 for name in self.cfg["production_system"]["metrics"]},
        )
        run["metrics"]["generation_jobs"] = 0
        run["generation_attempts_by_asset"] = {}
        run["thumbnail_generation_jobs"] = 0
        for name in GATE_INPUTS[GATES[2]]:
            path = Path(self.tmp.name) / (identity + name)
            path.write_bytes(("SYNTHETIC POLICY TEST ONLY " + identity + name).encode())
            run["artifacts"][name] = str(path)
        for stage, outputs in CRAFT_OUTPUTS_BY_STAGE.items():
            for output_id, function_id in outputs.items():
                path = Path(self.tmp.name) / (identity + "-craft-" + output_id)
                path.write_text("SYNTHETIC CRAFT OUTPUT " + output_id, encoding="utf-8")
                run["craft_outputs"][output_id] = {
                    "status": "COMPLETE",
                    "stage": stage,
                    "function_id": function_id,
                    "author_id": ("fact-checker" if function_id == "independent_fact_checker" else function_id + "-author"),
                    "artifact": str(path),
                    "sha256": artifact_hash(str(path)),
                }
        evidence = Path(self.tmp.name) / (identity + "-observations.log")
        evidence.write_text("SYNTHETIC reviewer and delivery observations; not real QC proof")
        evidence_hash = artifact_hash(str(evidence))
        for gate in GATES:
            receipt = dict(
                status="PASS",
                authority=GATE_AUTHORITIES[gate],
                reviewer_id="independent-qc",
                episode_id=identity,
                system_version="2.0",
                fact_checker_id="fact-checker",
                unresolved_defects=[],
                input_hashes={name: artifact_hash(run["artifacts"][name]) for name in GATE_INPUTS[gate]},
                checks={
                    name: dict(
                        passed=True,
                        evidence_ref=str(evidence),
                        evidence_sha256=evidence_hash,
                        authority="Visual Art Director / Frame Curator",
                        reviewer_id="synthetic-art-director",
                    )
                    for name in GATE_CHECKS[gate]
                },
            )
            run["gates"][gate] = receipt
        run["gates"][GATES[2]]["delivery"] = dict(
            export_sha256=artifact_hash(run["artifacts"]["export"]),
            width=1920,
            height=1080,
            fps=30,
            duration_seconds=35 if kind == "system_pilot" else 480,
            integrated_lufs=-14,
            true_peak_dbtp=-1,
            watermark_free=True,
            measurement_evidence_ref=str(evidence),
            measurement_evidence_sha256=evidence_hash,
        )
        return run

    def test_technical_compliance_does_not_replace_reference_fidelity(self):
        for gate in GATES:
            for field, value in [("passed", False), ("authority", "Technical Operator"), ("reviewer_id", "")]:
                run = copy.deepcopy(self.pilot)
                run["gates"][gate]["checks"]["reference_fidelity"][field] = value
                self.rejects(run)
            run = copy.deepcopy(self.pilot)
            run["gates"][gate]["checks"].pop("reference_fidelity")
            self.rejects(run)

    def test_owner_artistic_rejection_blocks_technically_valid_export(self):
        cfg = copy.deepcopy(self.cfg)
        cfg["production_system"]["art_direction"]["owner_rejected_exports"][
            artifact_hash(self.pilot["artifacts"]["export"])
        ] = "Owner rejection evidence"
        with self.assertRaisesRegex(ProductionWorkflowError, "Owner-rejected art direction"):
            validate_gate(cfg, self.pilot, GATES[2])

    def test_art_direction_contract_cannot_be_downgraded_for_speed(self):
        for field in [
            "governing_doc",
            "kit",
            "reference_grammar",
            "implementation_language",
            "reference_fidelity_required",
            "technical_success_is_artistic_acceptance",
            "simplification_may_change_identity",
        ]:
            cfg = copy.deepcopy(self.cfg)
            cfg["production_system"]["art_direction"][field] = "incorrect"
            with self.assertRaises(ProductionWorkflowError):
                validate_production_config(cfg)
        cfg = copy.deepcopy(self.cfg)
        cfg["production_system"]["art_direction"]["owner_rejected_exports"] = []
        with self.assertRaises(ProductionWorkflowError):
            validate_production_config(cfg)

    def test_governing_configs_cannot_restore_mirrored_legacy_workflows(self):
        self.cfg = json.loads((ROOT / "company/config/channel_operating_system.json").read_text(encoding="utf-8"))
        media = json.loads((ROOT / "company/config/media_venture.json").read_text(encoding="utf-8"))
        policy = json.loads((ROOT / "company/config/media_specialized_tool_policy.json").read_text(encoding="utf-8"))
        self.assertTrue(validate_alignment(self.cfg, media, policy))
        mutations = [
            lambda m, p: p.update(version="old"),
            lambda m, p: p.update(quality_gates=GATES + ["extra"]),
            lambda m, p: p.update(editing_routes={}),
            lambda m, p: p.update(governing_workflow="other.json"),
            lambda m, p: m.update(system_pilot={}),
            lambda m, p: p.update(gates={}),
            lambda m, p: p.update(current_motion_state={}),
            lambda m, p: p["execution_constraints"].update(automatic_publish="ALLOW"),
            lambda m, p: p["execution_constraints"].update(gui_retry_loops="ALLOW"),
        ]
        for mutate in mutations:
            m, p = copy.deepcopy(media), copy.deepcopy(policy)
            mutate(m, p)
            with self.assertRaises(ProductionWorkflowError):
                validate_alignment(self.cfg, m, p)

    def test_actual_run_counters_cannot_exceed_or_hide_budget(self):
        for name, ceiling in [("generation_jobs", 12), ("revision_rounds", 1)]:
            for value in [True, None, -1, 1.0, ceiling + 1]:
                run = copy.deepcopy(self.episode)
                run["metrics"][name] = value
                self.rejects(run, pilot=self.pilot)
            run = copy.deepcopy(self.episode)
            run["metrics"].pop(name)
            self.rejects(run, pilot=self.pilot)
        for attempts in [None, [], {"asset": True}, {"asset": -1}, {"asset": 3}, {"asset": 1.0}, {"asset": 1}]:
            run = copy.deepcopy(self.episode)
            run["generation_attempts_by_asset"] = attempts
            self.rejects(run, pilot=self.pilot)
        for value in [True, None, -1, 2, 1.0]:
            run = copy.deepcopy(self.episode)
            run["thumbnail_generation_jobs"] = value
            self.rejects(run, pilot=self.pilot)
        run = copy.deepcopy(self.episode)
        run.pop("thumbnail_generation_jobs")
        self.rejects(run, pilot=self.pilot)
        run = copy.deepcopy(self.episode)
        run["metrics"]["generation_jobs"] = 12
        run["generation_attempts_by_asset"] = {str(i): 2 for i in range(6)}
        run["thumbnail_generation_jobs"] = 1
        self.assertTrue(validate_gate(self.cfg, run, GATES[2], system_pilot=self.pilot))

    def valid_probe(self):
        path = Path(self.tmp.name) / "synthetic-native-probe.log"
        path.write_text("SYNTHETIC successful current-session probe observation")
        return dict(
            tool="Adobe After Effects 2026",
            status="PASS",
            current_session=True,
            artifact=str(path),
            sha256=artifact_hash(str(path)),
        )

    def test_evidence_requires_existing_unchanged_files(self):
        for gate in GATES:
            for field, value in [("evidence_ref", "missing-file"), ("evidence_sha256", "stale")]:
                run = copy.deepcopy(self.pilot)
                run["gates"][gate]["checks"][GATE_CHECKS[gate][0]][field] = value
                self.rejects(run)
        run = copy.deepcopy(self.pilot)
        run["gates"][GATES[2]]["delivery"]["measurement_evidence_sha256"] = "stale"
        self.rejects(run)
        run = copy.deepcopy(self.pilot)
        run["gates"][GATES[2]]["delivery"]["measurement_evidence_ref"] = "missing-measurement-log"
        self.rejects(run)
        evidence = Path(self.pilot["gates"][GATES[0]]["checks"][GATE_CHECKS[GATES[0]][0]]["evidence_ref"])
        evidence.write_text("changed observations")
        self.rejects(self.pilot)
        evidence.write_bytes(b"")
        self.rejects(self.pilot)

    def test_current_primary_probe_rejects_stale_failed_or_historical_claims(self):
        for field, value in [
            ("tool", "other"),
            ("status", "FAIL"),
            ("current_session", False),
            ("artifact", "missing-probe"),
            ("sha256", "stale"),
        ]:
            probe = self.valid_probe()
            probe[field] = value
            with self.assertRaises(ProductionWorkflowError):
                select_edit_route(self.cfg, current_probe=probe)
        probe = self.valid_probe()
        Path(probe["artifact"]).write_bytes(b"")
        with self.assertRaises(ProductionWorkflowError):
            select_edit_route(self.cfg, current_probe=probe)

    def test_metrics_and_exact_config_types_cannot_bypass_limits(self):
        for metrics in [None, [], ["cost"]]:
            cfg = copy.deepcopy(self.cfg)
            cfg["production_system"]["metrics"] = metrics
            with self.assertRaises(ProductionWorkflowError):
                validate_production_config(cfg)
        for section, key, value in [
            ("pilot", "count", True),
            ("pilot", "once_per_system", 1),
            ("editing_routes", "max_backup_activations", True),
            ("review_budget", "rough_cut_revision_rounds_max", True),
        ]:
            cfg = copy.deepcopy(self.cfg)
            cfg["production_system"][section][key] = value
            with self.assertRaises(ProductionWorkflowError):
                validate_production_config(cfg)

    def rejects(self, run, gate=GATES[2], pilot=None):
        with self.assertRaises(ProductionWorkflowError):
            validate_gate(self.cfg, run, gate, system_pilot=pilot)

    def test_valid_pilot_and_episode_use_same_three_gates(self):
        self.assertTrue(validate_production_config(self.cfg))
        for gate in GATES:
            self.assertTrue(validate_gate(self.cfg, self.pilot, gate))
            self.assertTrue(validate_gate(self.cfg, self.episode, gate, system_pilot=self.pilot))
        self.assertEqual(
            select_edit_route(self.cfg, current_probe=self.valid_probe())["tool"],
            "Adobe After Effects 2026",
        )
        self.assertEqual(select_edit_route(self.cfg, purpose="rough_prep")["tool"], "Descript")
        with self.assertRaises(ProductionWorkflowError):
            select_edit_route(self.cfg, primary_failed=True, current_probe=self.valid_probe())

    def test_config_contract_negative_paths(self):
        paths = [("workflow",), ("quality_gates",)]
        paths += [
            ("production_system", k)
            for k in [
                "version",
                "stage_authorities",
                "gate_authorities",
                "craft_contributor_contract",
                "target_duration_seconds_min",
                "per_frame_review",
                "per_prototype_review",
                "committee_approval",
                "publication_authorized",
            ]
        ]
        for section, keys in [
            ("legacy", ["resume_allowed", "status", "historical_evidence"]),
            (
                "pilot",
                [
                    "count",
                    "once_per_system",
                    "duration_seconds_min",
                    "duration_seconds_max",
                    "gate_names",
                    "blocks_full_episode_until_pass",
                    "old_pilot_evidence_accepted",
                ],
            ),
            (
                "editing_routes",
                [
                    "max_routes",
                    "gui_retry_loops",
                    "max_backup_activations",
                    "backup_requires_current_probe",
                    "max_primary_diagnosis_minutes",
                ],
            ),
            (
                "review_budget",
                [
                    "script_drafts_max",
                    "rough_cut_revision_rounds_max",
                    "asset_pack_reviews_max",
                    "generation_attempts_per_missing_asset_max",
                    "generation_jobs_per_episode_max",
                    "tool_comparison_tournaments",
                ],
            ),
        ]:
            paths += [("production_system", section, k) for k in keys]
        for route in ["primary", "backup"]:
            paths += [("production_system", "editing_routes", route, k) for k in ["tool", "transport", "evidence"]]
        for path in paths:
            cfg = copy.deepcopy(self.cfg)
            target = cfg
            for key in path[:-1]:
                target = target[key]
            target.pop(path[-1])
            with self.subTest(path=path), self.assertRaises(ProductionWorkflowError):
                validate_production_config(cfg)
        for legacy in ["pilot_ladder", "retry_pipeline", "active_pilot_stage"]:
            cfg = copy.deepcopy(self.cfg)
            cfg["production_system"][legacy] = []
            with self.assertRaises(ProductionWorkflowError):
                validate_production_config(cfg)
        cfg = copy.deepcopy(self.cfg)
        cfg["production_system"]["editing_routes"]["tertiary"] = {}
        with self.assertRaises(ProductionWorkflowError):
            validate_production_config(cfg)

    def test_stale_content_invalidates_only_dependent_gates(self):
        for name, first_gate in [("script", 0), ("assets", 1), ("export", 2)]:
            run = self.make_run("system_pilot", "changed-" + name)
            Path(run["artifacts"][name]).write_bytes(b"changed synthetic content")
            for index, gate in enumerate(GATES):
                if index >= first_gate:
                    self.rejects(run, gate)
                else:
                    self.assertTrue(validate_gate(self.cfg, run, gate))

    def test_missing_empty_and_unreported_artifacts_fail(self):
        for name in GATE_INPUTS[GATES[2]]:
            run = self.make_run("system_pilot", "missing-" + name)
            Path(run["artifacts"][name]).unlink()
            self.rejects(run)
            Path(run["artifacts"][name]).touch()
            self.rejects(run)
            run["artifacts"].pop(name)
            self.rejects(run)

    def test_receipts_checks_and_identity_fail_closed(self):
        for field, value in [
            ("system_version", "old"),
            ("episode_id", ""),
            ("kind", "old"),
            ("writer_id", ""),
            ("editor_id", ""),
            ("mix_author_id", ""),
        ]:
            run = copy.deepcopy(self.pilot)
            run[field] = value
            self.rejects(run)
        self.rejects(self.pilot, "fourth gate")
        for gate in GATES:
            for field, value in [
                ("status", "UNVERIFIED"),
                ("authority", "committee"),
                ("reviewer_id", ""),
                ("episode_id", "other"),
                ("system_version", "old"),
                ("unresolved_defects", ["open defect"]),
            ]:
                run = copy.deepcopy(self.pilot)
                run["gates"][gate][field] = value
                self.rejects(run)
            run = copy.deepcopy(self.pilot)
            run["gates"][gate].pop("unresolved_defects")
            self.rejects(run)
            for check in GATE_CHECKS[gate]:
                for observation in [
                    {},
                    {"passed": False, "evidence_ref": "synthetic"},
                    {"passed": True, "evidence_ref": ""},
                ]:
                    run = copy.deepcopy(self.pilot)
                    run["gates"][gate]["checks"][check] = observation
                    self.rejects(run)
        for checker in ["writer", ""]:
            run = copy.deepcopy(self.pilot)
            run["gates"][GATES[0]]["fact_checker_id"] = checker
            self.rejects(run)
        for reviewer in ["editor", "mixer"]:
            run = copy.deepcopy(self.pilot)
            run["gates"][GATES[2]]["reviewer_id"] = reviewer
            self.rejects(run)

    def test_required_specialist_craft_outputs_fail_closed(self):
        stage_gate = {
            "research_script": GATES[0],
            "visual_direction": GATES[0],
            "asset_pack": GATES[0],
            "edit_motion": GATES[1],
            "final_qc": GATES[2],
        }
        for stage, outputs in CRAFT_OUTPUTS_BY_STAGE.items():
            for output_id in outputs:
                run = copy.deepcopy(self.pilot)
                run["craft_outputs"].pop(output_id)
                with self.subTest(output_id=output_id):
                    self.rejects(run, stage_gate[stage])

    def test_craft_outputs_require_real_content_identity_and_hash(self):
        output_id = "spotting_sheet"
        for field, value in [
            ("status", "PENDING"),
            ("stage", "visual_direction"),
            ("function_id", "motion_picture_editor"),
            ("author_id", ""),
            ("artifact", "missing-craft-file"),
            ("sha256", "stale"),
        ]:
            run = copy.deepcopy(self.pilot)
            run["craft_outputs"][output_id][field] = value
            with self.subTest(field=field):
                self.rejects(run, GATES[1])
        run = copy.deepcopy(self.pilot)
        Path(run["craft_outputs"][output_id]["artifact"]).write_bytes(b"")
        self.rejects(run, GATES[1])

    def test_fact_checker_craft_must_be_independent(self):
        run = copy.deepcopy(self.pilot)
        run["craft_outputs"]["claim_ledger"]["author_id"] = run["writer_id"]
        self.rejects(run, GATES[0])
        run = copy.deepcopy(self.pilot)
        run["craft_outputs"]["final_fact_spotcheck"]["author_id"] = run["writer_id"]
        self.rejects(run, GATES[2])

    def test_localized_variant_requires_localization_conform_only_at_final_qc(self):
        run = copy.deepcopy(self.pilot)
        run["localized_variant_requested"] = True
        self.assertTrue(validate_gate(self.cfg, run, GATES[0]))
        self.assertTrue(validate_gate(self.cfg, run, GATES[1]))
        self.rejects(run, GATES[2])
        path = Path(self.tmp.name) / "localized-conform"
        path.write_text("SYNTHETIC LOCALIZATION CONFORM", encoding="utf-8")
        run["craft_outputs"]["localization_conform_package"] = {
            "status": "COMPLETE",
            "stage": "final_qc",
            "function_id": "localization_producer",
            "author_id": "localization-author",
            "artifact": str(path),
            "sha256": artifact_hash(str(path)),
        }
        self.assertTrue(validate_gate(self.cfg, run, GATES[2]))

    def test_delivery_and_metrics_require_measured_finite_values(self):
        invalid = {
            "width": [1919],
            "height": [1079],
            "fps": [23],
            "duration_seconds": [29, 46],
            "integrated_lufs": [-16, -12],
            "true_peak_dbtp": [0],
            "watermark_free": [False],
            "measurement_evidence_ref": [""],
            "export_sha256": ["stale"],
        }
        for field in ["width", "height", "fps", "duration_seconds", "integrated_lufs", "true_peak_dbtp"]:
            invalid[field] += [None, True, "30", float("nan"), float("inf")]
        for field, values in invalid.items():
            for value in values:
                run = copy.deepcopy(self.pilot)
                run["gates"][GATES[2]]["delivery"][field] = value
                with self.subTest(field=field, value=value):
                    self.rejects(run)
        for name in self.cfg["production_system"]["metrics"]:
            for value in [None, True, -1, float("nan"), float("inf"), "1"]:
                run = copy.deepcopy(self.pilot)
                run["metrics"][name] = value
                self.rejects(run)
        run = copy.deepcopy(self.pilot)
        run["tool"] = "unknown"
        self.rejects(run)
        run = copy.deepcopy(self.episode)
        run["gates"][GATES[2]]["delivery"]["duration_seconds"] = 479
        self.rejects(run, pilot=self.pilot)

    def test_full_episode_requires_actual_valid_one_time_pilot(self):
        for pilot in [None, {}, self.episode]:
            self.rejects(self.episode, pilot=pilot)
        pilot = copy.deepcopy(self.pilot)
        pilot["gates"][GATES[2]]["status"] = "UNVERIFIED"
        self.rejects(self.episode, pilot=pilot)
        for count, probe in [(0, None), (1, "probe"), (2, "probe")]:
            with self.assertRaises(ProductionWorkflowError):
                select_edit_route(self.cfg, primary_failed=True, current_probe=probe, backup_activations=count)


if __name__ == "__main__":
    unittest.main()
