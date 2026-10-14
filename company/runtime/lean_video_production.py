"""Lean production policy and content-bound gate receipts, not a video renderer.

External tools perform craft. Reviewers attach their observations to actual files;
this module rejects stale approvals, missing files and unsupported delivery claims.
"""

from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any


class ProductionWorkflowError(ValueError):
    pass


STAGES = ["research_script", "visual_direction", "asset_pack", "edit_motion", "final_qc"]
AUTHORITIES = dict(
    zip(
        STAGES,
        [
            "Editorial Director / Showrunner",
            "Visual Art Director / Frame Curator",
            "Media Producer / Production Coordinator",
            "Motion & Picture Editor",
            "Independent QC Reviewer",
        ],
    )
)
GATES = ["Preproduction Lock", "Rough Cut Review", "Final QC"]
METRICS = [
    "active_minutes",
    "wall_minutes",
    "service_queue_minutes",
    "render_minutes",
    "cost",
    "generation_jobs",
    "revision_rounds",
    "qc_defects",
]
GATE_AUTHORITIES = dict(
    zip(GATES, [AUTHORITIES["research_script"], AUTHORITIES["research_script"], AUTHORITIES["final_qc"]])
)
GATE_INPUTS = {
    GATES[0]: ["script", "direction", "asset_plan"],
    GATES[1]: ["script", "direction", "asset_plan", "assets", "rough_cut"],
    GATES[2]: ["script", "direction", "asset_plan", "assets", "rough_cut", "export"],
}
GATE_CHECKS = {
    GATES[0]: ["facts_checked", "rights_plan", "visual_direction", "reference_fidelity", "voice_plan", "budget"],
    GATES[1]: [
        "narration_complete",
        "story_pacing",
        "visual_coherence",
        "reference_fidelity",
        "rights_clear",
        "no_filler",
        "sync",
    ],
    GATES[2]: [
        "facts_checked",
        "rights_clear",
        "arabic_readability",
        "narration_complete",
        "voice_accepted",
        "sync",
        "audio_intelligibility",
        "visual_coherence",
        "reference_fidelity",
        "clean_export",
    ],
}

CRAFT_OUTPUTS_BY_STAGE = {
    "research_script": {
        "claim_ledger": "independent_fact_checker",
        "narration_performance_map": "script_voice_director",
        "hook_retention_notes": "audience_growth_strategist",
    },
    "visual_direction": {
        "motion_feasibility_map": "motion_picture_editor",
        "sonic_visual_intent": "music_sound_supervisor",
        "packaging_hook_continuity": "thumbnail_packaging_designer",
    },
    "asset_pack": {
        "visual_asset_clearance": "visual_art_director",
        "music_sfx_asset_plan": "music_sound_supervisor",
        "dialogue_mix_input_spec": "dialogue_mix_engineer",
        "thumbnail_packaging_spec": "thumbnail_packaging_designer",
    },
    "edit_motion": {
        "narration_continuity_notes": "script_voice_director",
        "spotting_sheet": "music_sound_supervisor",
        "rough_mix_receipt": "dialogue_mix_engineer",
        "visual_conform_notes": "visual_art_director",
    },
    "final_qc": {
        "final_mix_receipt": "dialogue_mix_engineer",
        "final_fact_spotcheck": "independent_fact_checker",
    },
}
GATE_CRAFT_STAGES = {
    GATES[0]: ["research_script", "visual_direction", "asset_pack"],
    GATES[1]: ["research_script", "visual_direction", "asset_pack", "edit_motion"],
    GATES[2]: STAGES,
}
CONDITIONAL_CRAFT_OUTPUTS = {
    "localization_conform_package": {
        "function_id": "localization_producer",
        "stage": "final_qc",
        "trigger": "localized_variant_requested",
    }
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProductionWorkflowError(message)


def validate_production_config(cfg: dict[str, Any]) -> bool:
    system = cfg.get("production_system", {})
    require(cfg.get("workflow") == STAGES, "exactly five ordered production stages required")
    require(cfg.get("quality_gates") == GATES, "exactly three ordered gates required; no extra gates")
    require(system.get("version") == "2.0", "lean production system must be 2.0")
    require(system.get("stage_authorities") == AUTHORITIES, "one final authority per stage required")
    require(system.get("gate_authorities") == GATE_AUTHORITIES, "gate authority drift")
    require(
        system.get("studio_identity")
        == {
            "name_ar": "الاستوديو",
            "name_en": "The Studio",
            "legacy_operating_name": "Council",
            "scope": "MEDIA_PRODUCTION_ONLY",
            "historical_evidence_keeps_legacy_name": True,
            "repository_name_unchanged": True,
        },
        "active media identity must remain The Studio",
    )
    require(
        system.get("studio_operating_model")
        == {
            "config": "company/config/studio_operating_model.json",
            "doc": "docs/operations/media/STUDIO_OPERATING_MODEL.md",
            "version": "1.0",
            "departments": [
                "studio_management",
                "editorial_research",
                "visual_design",
                "post_production",
                "qc_delivery",
            ],
            "episode_pod": True,
            "technical_stage_ids_unchanged": True,
            "technical_gate_ids_unchanged": True,
        },
        "Studio operating-model pointer or department contract drifted",
    )
    require(
        system.get("gate_placement")
        == {
            "Preproduction Lock": "after_asset_pack",
            "Rough Cut Review": "during_edit_motion",
            "Final QC": "after_export",
        },
        "Studio gate placement drifted",
    )
    craft = system.get("craft_contributor_contract", {})
    require(craft.get("mode") == "MANDATORY_PARALLEL_WITHIN_STAGES", "mandatory craft contributor mode required")
    require(craft.get("creates_additional_gates") is False, "craft contributors cannot create extra gates")
    require(
        craft.get("missing_required_output_action") == "BLOCK_STAGE_LOCK",
        "missing craft output must block stage lock",
    )
    require(
        craft.get("stage_authority_retains_final_decision") is True,
        "stage authority must retain final decision",
    )
    require(
        craft.get("contributor_outputs_are_production_artifacts_not_votes") is True,
        "specialist contributions must be production artifacts, not committee votes",
    )
    craft_stages = craft.get("stages", {})
    require(set(craft_stages) == set(STAGES), "craft contributor stages drifted")
    for stage, expected_outputs in CRAFT_OUTPUTS_BY_STAGE.items():
        declared = craft_stages.get(stage, [])
        actual = {item.get("output_id"): item.get("function_id") for item in declared if item.get("required") is True}
        require(
            actual == expected_outputs,
            f"mandatory craft outputs drifted: {stage}",
        )
    localization = craft.get("conditional", {}).get("localization_producer", {})
    require(
        localization
        == {
            "trigger": "localized_variant_requested",
            "stage": "final_qc",
            "output_id": "localization_conform_package",
            "required_when_triggered": True,
        },
        "conditional localization craft contract drifted",
    )
    require(system.get("target_duration_seconds_min") == 480, "8+ minute target required")
    art = system.get("art_direction", {})
    for key, expected in {
        "governing_doc": "docs/operations/media/DESIGN.md",
        "kit": "docs/operations/media/VISUAL_PRODUCTION_KIT_v1.1.md",
        "reference_grammar": "docs/operations/media/reference/REFERENCE_TEMPORAL_GRAMMAR_1000061003_v1.0.md",
        "implementation_language": "Kinetic Editorial Surrealism / Mixed Media",
        "reference_fidelity_required": True,
        "technical_success_is_artistic_acceptance": False,
        "simplification_may_change_identity": False,
    }.items():
        require(
            type(art.get(key)) is type(expected) and art.get(key) == expected, f"art direction contract drift: {key}"
        )
    require(isinstance(art.get("owner_rejected_exports"), dict), "Owner artistic dispositions must be retained")
    for key in ["per_frame_review", "per_prototype_review", "committee_approval", "publication_authorized"]:
        require(system.get(key) is False, f"{key} must remain disabled")
    require(system.get("legacy", {}).get("resume_allowed") is False, "cancelled workflow cannot resume")
    require(system.get("legacy", {}).get("status") == "SUPERSEDED_CANCELLED", "legacy status missing")
    require(bool(system.get("legacy", {}).get("historical_evidence")), "historical evidence must be retained")
    require(
        not {"pilot_ladder", "retry_pipeline", "active_pilot_stage"}.intersection(system),
        "legacy pipeline reintroduced",
    )
    pilot = system.get("pilot", {})
    for key, value in {
        "count": 1,
        "once_per_system": True,
        "duration_seconds_min": 30,
        "duration_seconds_max": 45,
        "gate_names": GATES,
        "blocks_full_episode_until_pass": True,
        "old_pilot_evidence_accepted": False,
    }.items():
        require(
            type(pilot.get(key)) is type(value) and pilot.get(key) == value,
            f"single system pilot contract drift: {key}",
        )
    require(system.get("metrics") == METRICS, "measured system pilot metrics required")
    routes = system.get("editing_routes", {})
    require(
        set(routes).intersection({"primary", "backup", "tertiary"}) == {"primary", "backup"},
        "only the current delivery route and rough utility are allowed",
    )
    primary = routes.get("primary", {})
    require(
        primary.get("tool") == "Adobe After Effects 2026"
        and primary.get("transport") == "native_project_automation"
        and primary.get("role") == "EDIT_MOTION_AND_DELIVERY"
        and primary.get("requires_current_probe") is True,
        "current delivery route drift",
    )
    require(bool(primary.get("evidence")), "primary route evidence missing")
    backup = routes.get("backup", {})
    require(
        backup.get("tool") == "Descript"
        and backup.get("transport") == "native_api_or_connector"
        and backup.get("role") == "ROUGH_TRANSCRIPT_UTILITY_ONLY"
        and backup.get("eligible_for_final_delivery") is False,
        "rough utility route drift",
    )
    require(bool(backup.get("evidence")), "rough utility evidence missing")
    for key, value in {
        "max_routes": 2,
        "gui_retry_loops": False,
        "max_backup_activations": 1,
        "backup_requires_current_probe": False,
        "max_primary_diagnosis_minutes": 10,
        "backup_trigger": "ROUGH_PREP_ONLY",
        "fallback_failure_action": "CAPABILITY_GAP_STOP_NO_DELIVERY_FALLBACK",
    }.items():
        require(type(routes.get(key)) is type(value) and routes.get(key) == value, f"route limit drift: {key}")
    budget = system.get("review_budget", {})
    for key, value in {
        "script_drafts_max": 2,
        "rough_cut_revision_rounds_max": 1,
        "asset_pack_reviews_max": 1,
        "generation_attempts_per_missing_asset_max": 2,
        "generation_jobs_per_episode_max": 12,
        "tool_comparison_tournaments": False,
    }.items():
        require(
            type(budget.get(key)) is type(value) and budget.get(key) == value, f"review/generation budget drift: {key}"
        )
    return True


def validate_alignment(channel: dict[str, Any], media: dict[str, Any], policy: dict[str, Any]) -> bool:
    """Prevent other governing configs from restoring an obsolete gate/tool mirror."""
    validate_production_config(channel)
    require(policy.get("version") == "2.0", "specialized tool policy must be 2.0")
    require(policy.get("quality_gates") == GATES, "specialized policy cannot add gates")
    require(
        policy.get("editing_routes") == channel["production_system"]["editing_routes"], "editing route mirrors drifted"
    )
    require(
        policy.get("governing_workflow") == "company/config/channel_operating_system.json",
        "single governing workflow required",
    )
    require(media.get("system_pilot") == channel["production_system"]["pilot"], "system pilot mirrors drifted")
    require("gates" not in policy and "current_motion_state" not in policy, "superseded tool pipeline reintroduced")
    require(
        policy.get("execution_constraints", {}).get("automatic_publish") == "BLOCK", "automatic publication forbidden"
    )
    require(policy.get("execution_constraints", {}).get("gui_retry_loops") == "FORBIDDEN", "long GUI loops forbidden")
    return True


def artifact_hash(path: str) -> str:
    artifact = Path(path)
    require(artifact.is_file() and artifact.stat().st_size > 0, f"missing or empty artifact: {artifact}")
    with artifact.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def validate_craft_outputs(run: dict[str, Any], gate: str) -> bool:
    outputs = run.get("craft_outputs", {})
    require(isinstance(outputs, dict), "craft outputs must be reported")
    for stage in GATE_CRAFT_STAGES[gate]:
        for output_id, function_id in CRAFT_OUTPUTS_BY_STAGE[stage].items():
            receipt = outputs.get(output_id, {})
            require(receipt.get("status") == "COMPLETE", f"missing mandatory craft output: {output_id}")
            require(receipt.get("stage") == stage, f"craft output stage drift: {output_id}")
            require(receipt.get("function_id") == function_id, f"craft contributor mismatch: {output_id}")
            require(bool(receipt.get("author_id")), f"craft output author missing: {output_id}")
            artifact = receipt.get("artifact")
            require(isinstance(artifact, str) and bool(artifact), f"craft output artifact missing: {output_id}")
            require(receipt.get("sha256") == artifact_hash(artifact), f"craft output stale: {output_id}")
            if function_id == "independent_fact_checker":
                require(receipt["author_id"] != run.get("writer_id"), "fact checker craft output must be independent")
    if run.get("localized_variant_requested") is True and "final_qc" in GATE_CRAFT_STAGES[gate]:
        spec = CONDITIONAL_CRAFT_OUTPUTS["localization_conform_package"]
        receipt = outputs.get("localization_conform_package", {})
        require(receipt.get("status") == "COMPLETE", "localized variant requires localization conform package")
        require(receipt.get("stage") == spec["stage"], "localization craft stage drift")
        require(receipt.get("function_id") == spec["function_id"], "localization contributor mismatch")
        require(bool(receipt.get("author_id")), "localization craft author missing")
        artifact = receipt.get("artifact")
        require(isinstance(artifact, str) and bool(artifact), "localization craft artifact missing")
        require(receipt.get("sha256") == artifact_hash(artifact), "localization craft output stale")
    return True


def validate_gate(
    cfg: dict[str, Any], run: dict[str, Any], gate: str, *, system_pilot: dict[str, Any] | None = None
) -> bool:
    """Validate current gate and prerequisites against files, not historical PASS labels.

    For a full episode, supply the one-time accepted pilot record. The pilot itself
    uses these same three gates; it does not recursively require another pilot.
    """
    validate_production_config(cfg)
    require(gate in GATES, "unknown gate")
    require(run.get("system_version") == "2.0" and bool(run.get("episode_id")), "current run identity required")
    require(run.get("kind") in {"system_pilot", "episode"}, "invalid production kind")
    require(run.get("localized_variant_requested") in {False, True}, "localized variant flag required")
    if run["kind"] == "episode":
        require(
            isinstance(system_pilot, dict) and system_pilot.get("kind") == "system_pilot",
            "one accepted system pilot required",
        )
        validate_gate(cfg, system_pilot, GATES[2])
    for current in GATES[: GATES.index(gate) + 1]:
        receipt = run.get("gates", {}).get(current, {})
        require(receipt.get("status") == "PASS", f"{current} is not approved")
        require(
            receipt.get("authority") == GATE_AUTHORITIES[current] and bool(receipt.get("reviewer_id")),
            f"{current} needs final authority and named reviewer",
        )
        require(
            receipt.get("episode_id") == run["episode_id"] and receipt.get("system_version") == "2.0",
            "receipt identity is stale",
        )
        for name in GATE_INPUTS[current]:
            path = run.get("artifacts", {}).get(name)
            require(isinstance(path, str) and bool(path), f"{current} artifact missing: {name}")
            require(
                receipt.get("input_hashes", {}).get(name) == artifact_hash(path), f"{current} stale approval: {name}"
            )
        validate_craft_outputs(run, current)
        require(
            not receipt.get("unresolved_defects", ["missing defect disposition"]),
            f"{current} has unresolved or unreported defects",
        )
        for check in GATE_CHECKS[current]:
            observation = receipt.get("checks", {}).get(check, {})
            require(
                observation.get("passed") is True and bool(observation.get("evidence_ref")),
                f"{current} lacks evidenced check: {check}",
            )
            require(
                observation.get("evidence_sha256") == artifact_hash(observation["evidence_ref"]),
                f"{current} check evidence stale: {check}",
            )
            if check == "reference_fidelity":
                require(
                    observation.get("authority") == AUTHORITIES["visual_direction"]
                    and bool(observation.get("reviewer_id")),
                    "reference fidelity requires evidenced Art Director disposition, not technical/coherence approval",
                )
        if current == GATES[0]:
            require(
                bool(run.get("writer_id"))
                and bool(receipt.get("fact_checker_id"))
                and receipt["fact_checker_id"] != run["writer_id"],
                "facts require independent reviewer",
            )
        if current == GATES[2]:
            require(
                artifact_hash(run["artifacts"]["export"])
                not in cfg["production_system"]["art_direction"]["owner_rejected_exports"],
                "Owner-rejected art direction cannot pass Final QC on technical measurements",
            )
            require(
                bool(run.get("editor_id"))
                and bool(run.get("mix_author_id"))
                and receipt["reviewer_id"] not in {run["editor_id"], run["mix_author_id"]},
                "Final QC must be independent of edit and mix authors",
            )
            delivery = receipt.get("delivery", {})
            require(
                delivery.get("export_sha256") == artifact_hash(run["artifacts"]["export"]),
                "QC delivery is not bound to exact export",
            )
            for field in ["width", "height", "fps", "duration_seconds", "integrated_lufs", "true_peak_dbtp"]:
                value = delivery.get(field)
                require(
                    type(value) in {int, float} and math.isfinite(value), f"invalid measured delivery field: {field}"
                )
            require(
                delivery["width"] >= 1920 and delivery["height"] >= 1080 and delivery["fps"] >= 24,
                "insufficient delivery resolution or fps",
            )
            require(delivery.get("watermark_free") is True, "watermark-free export required")
            require(
                -15 <= delivery["integrated_lufs"] <= -13 and delivery["true_peak_dbtp"] <= -1,
                "audio outside internal loudness/peak targets",
            )
            duration = delivery["duration_seconds"]
            require(
                (30 <= duration <= 45) if run["kind"] == "system_pilot" else duration >= 480,
                "invalid pilot or episode duration",
            )
            require(bool(delivery.get("measurement_evidence_ref")), "actual delivery measurement receipt required")
            require(
                delivery.get("measurement_evidence_sha256") == artifact_hash(delivery["measurement_evidence_ref"]),
                "delivery measurement evidence stale",
            )
            if run["kind"] == "system_pilot":
                metrics = run.get("metrics", {})
                for name in cfg["production_system"]["metrics"]:
                    require(
                        type(metrics.get(name)) in {int, float} and math.isfinite(metrics[name]) and metrics[name] >= 0,
                        f"missing measured pilot metric: {name}",
                    )
                require(
                    run.get("tool") == cfg["production_system"]["editing_routes"]["primary"]["tool"],
                    "pilot final delivery must use the current qualified delivery route",
                )
            budget = cfg["production_system"]["review_budget"]
            counters = run.get("metrics", {})
            for name, ceiling in [
                ("generation_jobs", budget["generation_jobs_per_episode_max"]),
                ("revision_rounds", budget["rough_cut_revision_rounds_max"]),
            ]:
                require(
                    type(counters.get(name)) is int and 0 <= counters[name] <= ceiling,
                    f"runtime budget exceeded or unreported: {name}",
                )
            attempts = run.get("generation_attempts_by_asset", {})
            require(
                isinstance(attempts, dict)
                and all(
                    type(count) is int and 0 <= count <= budget["generation_attempts_per_missing_asset_max"]
                    for count in attempts.values()
                ),
                "per-asset generation budget exceeded",
            )
            require(
                sum(attempts.values()) == counters["generation_jobs"],
                "generation attempts must reconcile with actual job count",
            )
            require(
                type(run.get("thumbnail_generation_jobs")) is int and 0 <= run["thumbnail_generation_jobs"] <= 1,
                "single thumbnail generation boundary exceeded",
            )
    return True


def select_edit_route(
    cfg: dict[str, Any],
    *,
    purpose: str = "delivery",
    primary_failed: bool = False,
    current_probe: dict[str, Any] | None = None,
    backup_activations: int = 0,
) -> dict[str, Any]:
    validate_production_config(cfg)
    routes = cfg["production_system"]["editing_routes"]

    if purpose == "rough_prep":
        require(
            backup_activations <= routes["max_backup_activations"],
            "rough utility activation budget exceeded",
        )
        return dict(routes["backup"])

    require(purpose in {"delivery", "edit_motion"}, "unknown edit-route purpose")
    require(
        primary_failed is False,
        "primary delivery failure is a capability gap; do not retry known-failed delivery tools",
    )
    require(isinstance(current_probe, dict), "current successful primary probe required")
    require(
        current_probe.get("tool") == routes["primary"]["tool"]
        and current_probe.get("status") == "PASS"
        and current_probe.get("current_session") is True
        and bool(current_probe.get("artifact")),
        "current successful primary probe required",
    )
    require(current_probe.get("sha256") == artifact_hash(current_probe["artifact"]), "primary probe evidence stale")
    return dict(routes["primary"])
