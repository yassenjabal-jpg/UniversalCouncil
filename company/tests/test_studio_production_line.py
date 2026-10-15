import unittest

from company.runtime.studio_production_line import (
    StudioProductionLineError,
    validate_department_handoff,
    validate_owner_title_lock,
    validate_phase_transition,
    validate_return_ticket,
    validate_stage_record,
    validate_title_candidate_packet,
    validate_title_revision_request,
)


STORY_ARCHETYPES = [
    "mystery_investigation",
    "hidden_system",
    "engineering_impossibility",
]


def topic_card(idx: int, topic: str):
    return {
        "id": f"P{idx}",
        "topic": topic,
        "story_premise": f"A concrete story premise for {topic}",
        "story_archetype": STORY_ARCHETYPES[idx - 1],
        "hero_anchor": f"hero-{idx}",
        "tension_or_mystery": "an unresolved contradiction",
        "viewer_stakes": "the answer changes how the viewer understands the subject",
        "why_now": "current market signal",
        "market_signal": "rising audience interest",
        "competition_level": "MEDIUM",
        "key_visual": "one unmistakable visual anchor",
        "thumbnail_hypothesis": {
            "hero_subject": f"hero-{idx}",
            "visual_tension": "one visible contradiction",
            "composition": "single dominant subject with negative space",
            "text_0_4_words": "",
            "works_without_explanatory_text": True,
        },
        "visual_potential": "HIGH",
        "evidence_feasibility": "PASS",
        "eight_minute_story_feasibility": "PASS",
        "risk_notes": "bounded",
        "title_variants": [
            {
                "id": f"P{idx}A",
                "title": f"{topic}: direct title",
                "click_reason": "direct curiosity gap",
                "viewer_promise": "specific answer",
                "thumbnail_complement": "title asks what the image does not explain",
                "stranger_click_test": "PASS",
                "youtube_title_style_status": "PASS",
            },
            {
                "id": f"P{idx}B",
                "title": f"{topic}: documentary title",
                "click_reason": "alternative curiosity framing",
                "viewer_promise": "same story promise from a different angle",
                "thumbnail_complement": "title adds the consequence behind the image",
                "stranger_click_test": "PASS",
                "youtube_title_style_status": "PASS",
            },
        ],
    }


class StudioProductionLineTests(unittest.TestCase):
    def packet(self):
        return {
            "market_scan_status": "PASS",
            "social_trend_scan_status": "PASS",
            "story_feasibility_status": "PASS",
            "youtube_native_discovery_status": "PASS",
            "discovery_evidence_mode": "FULL",
            "packaging_hypothesis_status": "PASS",
            "red_team_click_challenge_status": "PASS",
            "topics": [
                topic_card(1, "Topic One"),
                topic_card(2, "Topic Two"),
                topic_card(3, "Topic Three"),
            ],
        }

    def test_exactly_three_topics_with_two_titles_each_are_required(self):
        packet = self.packet()
        self.assertTrue(validate_title_candidate_packet(packet))
        packet["topics"] = packet["topics"][:2]
        with self.assertRaises(StudioProductionLineError):
            validate_title_candidate_packet(packet)

        packet = self.packet()
        packet["topics"][0]["title_variants"] = packet["topics"][0]["title_variants"][:1]
        with self.assertRaises(StudioProductionLineError):
            validate_title_candidate_packet(packet)

    def test_title_candidates_require_discovery_feasibility_packaging_and_red_team(self):
        for key in {
            "market_scan_status",
            "social_trend_scan_status",
            "story_feasibility_status",
            "youtube_native_discovery_status",
            "packaging_hypothesis_status",
            "red_team_click_challenge_status",
        }:
            packet = self.packet()
            packet[key] = "FAIL"
            with self.assertRaises(StudioProductionLineError):
                validate_title_candidate_packet(packet)

        packet = self.packet()
        packet["discovery_evidence_mode"] = "DEGRADED_HOLD"
        with self.assertRaises(StudioProductionLineError):
            validate_title_candidate_packet(packet)

        packet = self.packet()
        packet["discovery_evidence_mode"] = "AUTHORIZED_NATIVE_FALLBACK"
        self.assertTrue(validate_title_candidate_packet(packet))

    def test_owner_is_only_title_lock_authority(self):
        packet = self.packet()
        selection = {
            "authority": "Owner",
            "status": "OWNER_TITLE_LOCK",
            "selected_topic_id": "P2",
            "selected_title_id": "P2B",
            "locked_topic": "Topic Two",
            "locked_title": "Topic Two: documentary title",
        }
        self.assertTrue(validate_owner_title_lock(packet, selection))

        selection["authority"] = "Showrunner"
        with self.assertRaises(StudioProductionLineError):
            validate_owner_title_lock(packet, selection)

    def test_locked_title_must_belong_to_selected_topic(self):
        packet = self.packet()
        with self.assertRaises(StudioProductionLineError):
            validate_owner_title_lock(
                packet,
                {
                    "authority": "Owner",
                    "status": "OWNER_TITLE_LOCK",
                    "selected_topic_id": "P1",
                    "selected_title_id": "P2A",
                    "locked_topic": "Topic One",
                    "locked_title": "Other",
                },
            )

    def test_title_revision_requires_owner_reapproval(self):
        req = {
            "current_title": "Title One",
            "proposed_title": "Title One, Refined",
            "reason": "accuracy",
            "evidence": "new source",
            "impact_on_script_or_packaging": "minor",
            "owner_reapproval_status": "APPROVED",
        }
        self.assertTrue(validate_title_revision_request(req))
        req["owner_reapproval_status"] = "PENDING"
        with self.assertRaises(StudioProductionLineError):
            validate_title_revision_request(req)

    def test_phase_gates_fail_closed(self):
        self.assertTrue(
            validate_phase_transition(
                "writing",
                "pre_production",
                {"owner_title_lock": True, "script_lock": True},
            )
        )
        with self.assertRaises(StudioProductionLineError):
            validate_phase_transition("writing", "pre_production", {"owner_title_lock": True})
        self.assertTrue(
            validate_phase_transition(
                "pre_production",
                "production",
                {"production_ready_lock": True},
            )
        )
        with self.assertRaises(StudioProductionLineError):
            validate_phase_transition("writing", "production", {"production_ready_lock": True})

    def test_stage_enforces_one_program_and_verified_exit(self):
        stage = {
            "stage_id": "motion_build",
            "program": "Adobe After Effects 2025",
            "status": "VERIFIED_COMPLETE",
            "output_ref": "motion-v1",
            "checkpoint_ref": "cp-1",
        }
        self.assertTrue(validate_stage_record(stage))
        stage["secondary_craft_programs"] = ["Adobe Premiere Pro 2025"]
        with self.assertRaises(StudioProductionLineError):
            validate_stage_record(stage)

    def test_handoff_requires_qc_pass_to_accept(self):
        handoff = {
            "project_id": "EP-001",
            "handoff_id": "H-001",
            "from_department": "P03_motion_compositing",
            "to_department": "P04_picture_edit",
            "completed_stage_ids": ["motion_build", "compositing", "motion_qc"],
            "artifact_manifest": ["motion-v1"],
            "locked_artifacts": ["motion-v1"],
            "change_log": [],
            "known_limitations": [],
            "qc_result": "PASS",
            "acceptance_criteria": ["all sequences present"],
            "checkpoint_ref": "cp-3",
            "handoff_status": "ACCEPTED",
        }
        self.assertTrue(validate_department_handoff(handoff))
        handoff["qc_result"] = "FAIL"
        with self.assertRaises(StudioProductionLineError):
            validate_department_handoff(handoff)

    def test_return_ticket_keeps_repair_with_source_department(self):
        ticket = {
            "return_ticket_id": "R-1",
            "source_department": "P02_visual_assets",
            "detecting_department": "P03_motion_compositing",
            "artifact_ref": "asset-17",
            "defect": "insufficient resolution",
            "reason_for_rejection": "fails motion crop",
            "requested_correction": "rebuild asset at required dimensions",
            "do_not_change": "composition identity",
            "resume_handoff": "VISUAL_ASSET_PACKET",
        }
        self.assertTrue(validate_return_ticket(ticket))

    def test_title_packet_failure_paths_are_covered(self):
        base = self.packet()

        cases = []

        missing_variant_field = self.packet()
        missing_variant_field["topics"][0]["title_variants"][0].pop("viewer_promise")
        cases.append(missing_variant_field)

        empty_id = self.packet()
        empty_id["topics"][0]["id"] = ""
        cases.append(empty_id)

        empty_title = self.packet()
        empty_title["topics"][0]["title_variants"][0]["title"] = " "
        cases.append(empty_title)

        duplicate_topic_id = self.packet()
        duplicate_topic_id["topics"][1]["id"] = duplicate_topic_id["topics"][0]["id"]
        cases.append(duplicate_topic_id)

        duplicate_topic = self.packet()
        duplicate_topic["topics"][1]["topic"] = duplicate_topic["topics"][0]["topic"]
        cases.append(duplicate_topic)

        missing_topic_field = self.packet()
        missing_topic_field["topics"][0].pop("story_premise")
        cases.append(missing_topic_field)

        empty_story_field = self.packet()
        empty_story_field["topics"][0]["hero_anchor"] = " "
        cases.append(empty_story_field)

        unsupported_archetype = self.packet()
        unsupported_archetype["topics"][0]["story_archetype"] = "generic_explainer"
        cases.append(unsupported_archetype)

        duplicate_archetype = self.packet()
        duplicate_archetype["topics"][1]["story_archetype"] = duplicate_archetype["topics"][0]["story_archetype"]
        cases.append(duplicate_archetype)

        non_object_thumbnail = self.packet()
        non_object_thumbnail["topics"][0]["thumbnail_hypothesis"] = "pretty image"
        cases.append(non_object_thumbnail)

        missing_thumbnail_field = self.packet()
        missing_thumbnail_field["topics"][0]["thumbnail_hypothesis"].pop("visual_tension")
        cases.append(missing_thumbnail_field)

        empty_thumbnail_field = self.packet()
        empty_thumbnail_field["topics"][0]["thumbnail_hypothesis"]["composition"] = ""
        cases.append(empty_thumbnail_field)

        too_much_thumbnail_text = self.packet()
        too_much_thumbnail_text["topics"][0]["thumbnail_hypothesis"]["text_0_4_words"] = "one two three four five"
        cases.append(too_much_thumbnail_text)

        explanatory_thumbnail = self.packet()
        explanatory_thumbnail["topics"][0]["thumbnail_hypothesis"]["works_without_explanatory_text"] = False
        cases.append(explanatory_thumbnail)

        wrong_variant_count = self.packet()
        wrong_variant_count["topics"][0]["title_variants"] = wrong_variant_count["topics"][0]["title_variants"][:1]
        cases.append(wrong_variant_count)

        duplicate_title = self.packet()
        duplicate_title["topics"][1]["title_variants"][0]["title"] = duplicate_title["topics"][0]["title_variants"][0][
            "title"
        ]
        cases.append(duplicate_title)

        duplicate_title_id = self.packet()
        duplicate_title_id["topics"][1]["title_variants"][0]["id"] = duplicate_title_id["topics"][0]["title_variants"][
            0
        ]["id"]
        cases.append(duplicate_title_id)

        empty_click_reason = self.packet()
        empty_click_reason["topics"][0]["title_variants"][0]["click_reason"] = ""
        cases.append(empty_click_reason)

        empty_viewer_promise = self.packet()
        empty_viewer_promise["topics"][0]["title_variants"][0]["viewer_promise"] = ""
        cases.append(empty_viewer_promise)

        empty_thumbnail_complement = self.packet()
        empty_thumbnail_complement["topics"][0]["title_variants"][0]["thumbnail_complement"] = ""
        cases.append(empty_thumbnail_complement)

        stranger_click_fail = self.packet()
        stranger_click_fail["topics"][0]["title_variants"][0]["stranger_click_test"] = "FAIL"
        cases.append(stranger_click_fail)

        article_title = self.packet()
        article_title["topics"][0]["title_variants"][0]["youtube_title_style_status"] = "FAIL"
        cases.append(article_title)

        evidence_fail = self.packet()
        evidence_fail["topics"][0]["evidence_feasibility"] = "FAIL"
        cases.append(evidence_fail)

        duration_fail = self.packet()
        duration_fail["topics"][0]["eight_minute_story_feasibility"] = "FAIL"
        cases.append(duration_fail)

        visual_fail = self.packet()
        visual_fail["topics"][0]["visual_potential"] = "MEDIUM"
        cases.append(visual_fail)

        for packet in cases:
            with self.assertRaises(StudioProductionLineError):
                validate_title_candidate_packet(packet)

        self.assertTrue(validate_title_candidate_packet(base))

    def test_owner_title_lock_failure_paths_are_covered(self):
        packet = self.packet()
        cases = [
            {
                "authority": "Owner",
                "status": "PENDING",
                "selected_topic_id": "P1",
                "selected_title_id": "P1A",
                "locked_topic": "Topic One",
                "locked_title": "Topic One: direct title",
            },
            {
                "authority": "Owner",
                "status": "OWNER_TITLE_LOCK",
                "selected_topic_id": "P1",
                "selected_title_id": "P1A",
                "locked_topic": "Topic One",
                "locked_title": "",
            },
            {
                "authority": "Owner",
                "status": "OWNER_TITLE_LOCK",
                "selected_title_id": "T1",
                "locked_title": "Wrong Title",
            },
        ]
        cases.extend(
            [
                {
                    "authority": "Owner",
                    "status": "OWNER_TITLE_LOCK",
                    "selected_topic_id": "P9",
                    "selected_title_id": "P9A",
                    "locked_topic": "Other",
                    "locked_title": "Other",
                },
                {
                    "authority": "Owner",
                    "status": "OWNER_TITLE_LOCK",
                    "selected_topic_id": "P1",
                    "selected_title_id": "P2A",
                    "locked_topic": "Topic One",
                    "locked_title": "Topic Two: direct title",
                },
                {
                    "authority": "Owner",
                    "status": "OWNER_TITLE_LOCK",
                    "selected_topic_id": "P1",
                    "selected_title_id": "P1A",
                    "locked_topic": "Wrong Topic",
                    "locked_title": "Topic One: direct title",
                },
            ]
        )

        for selection in cases:
            with self.assertRaises(StudioProductionLineError):
                validate_owner_title_lock(packet, selection)

    def test_title_revision_missing_fields_fails(self):
        with self.assertRaises(StudioProductionLineError):
            validate_title_revision_request(
                {
                    "current_title": "A",
                    "proposed_title": "B",
                    "reason": "accuracy",
                    "evidence": "source",
                    "owner_reapproval_status": "APPROVED",
                }
            )

    def test_phase_transition_unknown_reverse_and_missing_gates_fail(self):
        with self.assertRaises(StudioProductionLineError):
            validate_phase_transition("unknown", "production", {})
        with self.assertRaises(StudioProductionLineError):
            validate_phase_transition("pre_production", "writing", {})
        with self.assertRaises(StudioProductionLineError):
            validate_phase_transition(
                "writing",
                "pre_production",
                {"owner_title_lock": False, "script_lock": True},
            )
        with self.assertRaises(StudioProductionLineError):
            validate_phase_transition(
                "pre_production",
                "production",
                {"production_ready_lock": False},
            )

    def test_stage_record_failure_paths_are_covered(self):
        with self.assertRaises(StudioProductionLineError):
            validate_stage_record({"stage_id": "x"})
        with self.assertRaises(StudioProductionLineError):
            validate_stage_record(
                {
                    "stage_id": "x",
                    "program": " ",
                    "status": "VERIFIED_COMPLETE",
                    "output_ref": "o",
                    "checkpoint_ref": "c",
                }
            )
        with self.assertRaises(StudioProductionLineError):
            validate_stage_record(
                {
                    "stage_id": "x",
                    "program": "ChatGPT",
                    "status": "IN_PROGRESS",
                    "output_ref": "o",
                    "checkpoint_ref": "c",
                }
            )

    def test_handoff_failure_paths_are_covered(self):
        with self.assertRaises(StudioProductionLineError):
            validate_department_handoff({"project_id": "EP-1"})

        handoff = {
            "project_id": "EP-001",
            "handoff_id": "H-001",
            "from_department": "P01_voice_narration",
            "to_department": "P02_visual_assets",
            "completed_stage_ids": ["narration_recording"],
            "artifact_manifest": ["voice.wav"],
            "locked_artifacts": ["voice.wav"],
            "change_log": [],
            "known_limitations": [],
            "qc_result": "PASS",
            "acceptance_criteria": ["voice ready"],
            "checkpoint_ref": "cp-1",
            "handoff_status": "INVALID",
        }
        with self.assertRaises(StudioProductionLineError):
            validate_department_handoff(handoff)

    def test_return_ticket_failure_paths_are_covered(self):
        with self.assertRaises(StudioProductionLineError):
            validate_return_ticket({"return_ticket_id": "R1"})

        ticket = {
            "return_ticket_id": "R-1",
            "source_department": "P02_visual_assets",
            "detecting_department": "P02_visual_assets",
            "artifact_ref": "asset-17",
            "defect": "bad",
            "reason_for_rejection": "bad",
            "requested_correction": "fix",
            "do_not_change": "style",
            "resume_handoff": "VISUAL_ASSET_PACKET",
        }
        with self.assertRaises(StudioProductionLineError):
            validate_return_ticket(ticket)


if __name__ == "__main__":
    unittest.main()
