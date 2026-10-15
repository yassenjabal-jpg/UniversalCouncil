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


def title_card(idx: int, title: str):
    return {
        "id": f"T{idx}",
        "title": title,
        "why_now": "current market signal",
        "market_signal": "rising audience interest",
        "story_angle": "specific documentary angle",
        "click_reason": "clear curiosity gap",
        "viewer_promise": "specific answer",
        "competition_level": "MEDIUM",
        "visual_potential": "HIGH",
        "evidence_feasibility": "PASS",
        "eight_minute_story_feasibility": "PASS",
        "risk_notes": "bounded",
    }


class StudioProductionLineTests(unittest.TestCase):
    def packet(self):
        return {
            "market_scan_status": "PASS",
            "social_trend_scan_status": "PASS",
            "story_feasibility_status": "PASS",
            "candidates": [
                title_card(1, "Title One"),
                title_card(2, "Title Two"),
                title_card(3, "Title Three"),
            ],
        }

    def test_exactly_three_titles_are_required(self):
        packet = self.packet()
        self.assertTrue(validate_title_candidate_packet(packet))
        packet["candidates"] = packet["candidates"][:2]
        with self.assertRaises(StudioProductionLineError):
            validate_title_candidate_packet(packet)

    def test_title_candidates_require_market_social_and_story_feasibility(self):
        for key in {"market_scan_status", "social_trend_scan_status", "story_feasibility_status"}:
            packet = self.packet()
            packet[key] = "FAIL"
            with self.assertRaises(StudioProductionLineError):
                validate_title_candidate_packet(packet)

    def test_owner_is_only_title_lock_authority(self):
        packet = self.packet()
        selection = {
            "authority": "Owner",
            "status": "OWNER_TITLE_LOCK",
            "selected_title_id": "T2",
            "locked_title": "Title Two",
        }
        self.assertTrue(validate_owner_title_lock(packet, selection))

        selection["authority"] = "Showrunner"
        with self.assertRaises(StudioProductionLineError):
            validate_owner_title_lock(packet, selection)

    def test_locked_title_must_be_one_of_three(self):
        packet = self.packet()
        with self.assertRaises(StudioProductionLineError):
            validate_owner_title_lock(
                packet,
                {
                    "authority": "Owner",
                    "status": "OWNER_TITLE_LOCK",
                    "selected_title_id": "T9",
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


if __name__ == "__main__":
    unittest.main()
