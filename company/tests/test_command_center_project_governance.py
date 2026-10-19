from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROJECT_STATE = ROOT / "state" / "command-center" / "project-governance"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class CommandCenterProjectGovernanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.lock = load_json(PROJECT_STATE / "inheritance-lock.json")
        self.council = load_json(PROJECT_STATE / "project-council.json")
        self.studio = load_json(PROJECT_STATE / "product-studio.json")
        self.parent_roles = load_json(ROOT / "config" / "roles.json")
        self.parent_contracts = load_json(ROOT / "company" / "config" / "council_role_contracts.json")
        self.parent_media = load_json(ROOT / "company" / "config" / "media_venture.json")
        self.identity = load_json(PROJECT_STATE / "al-murtakaz.json")
        self.review = load_json(PROJECT_STATE / "al-murtakaz-review.json")

    def test_parent_versions_are_explicit_and_read_only(self) -> None:
        parents = self.lock["parent_sources"]
        self.assertEqual(parents["roles"]["version"], self.parent_roles["version"])
        self.assertEqual(parents["role_contracts"]["version"], self.parent_contracts["version"])
        self.assertEqual(parents["media_studio"]["version"], self.parent_media["version"])
        self.assertFalse(self.lock["rules"]["allow_parent_mutation"])
        self.assertFalse(self.lock["rules"]["allow_parent_replacement"])

    def test_project_profiles_cannot_expand_authority(self) -> None:
        for profile in (self.council, self.studio):
            authority = profile["authority"]
            self.assertFalse(authority["may_modify_parent"])
            self.assertFalse(authority["may_mutate_authority"])
            self.assertFalse(authority["may_open_stage8"])
            self.assertTrue(authority["owner_final_authority"])

        self.assertFalse(self.council["authority"]["may_execute_tools_by_role_definition"])
        self.assertFalse(self.studio["authority"]["execution_authority"])
        self.assertFalse(self.studio["authority"]["live_publish_authority"])

    def test_project_council_uses_local_ids_and_inherits_known_parent_capabilities(self) -> None:
        known_parent = {item["id"] for item in self.parent_roles["core_roles"] + self.parent_roles["specialist_roles"]}
        local_ids = {role["id"] for role in self.council["core_roles"]}
        self.assertTrue(all(role_id.startswith("cc_") for role_id in local_ids))

        for role in self.council["core_roles"]:
            for parent_id in role["inherits_from"]:
                self.assertIn(parent_id, known_parent)

    def test_product_studio_is_not_media_studio_replacement(self) -> None:
        self.assertEqual(
            self.studio["parent"]["inheritance_mode"],
            "PRINCIPLES_ONLY_READ_ONLY",
        )
        local_ids = {function["id"] for function in self.studio["functions"]}
        self.assertTrue(all(function_id.startswith("cc_") for function_id in local_ids))
        self.assertNotIn("media_producer", local_ids)
        self.assertNotIn("editorial_director", local_ids)

    def test_truth_and_prototype_safeguards_remain_fail_closed(self) -> None:
        self.assertTrue(self.lock["rules"]["unknown_is_never_success"])
        self.assertTrue(self.council["truth_rules"]["unknown_is_never_success"])

        prototype = self.studio["prototype_rules"]
        self.assertTrue(prototype["fixtures_must_be_labeled"])
        self.assertTrue(prototype["fixtures_must_not_enter_runtime_truth"])
        self.assertTrue(prototype["fixtures_must_not_enter_evidence_truth"])

    def test_project_studio_has_clearance_and_handoff_rules(self) -> None:
        clearances = set(self.studio["mandatory_clearance"])
        self.assertIn("cc_accessibility_clearance", clearances)
        self.assertIn("cc_visual_qa", clearances)

        handoff = self.studio["handoff"]
        self.assertTrue(handoff["acceptance_required"])
        self.assertTrue(handoff["return_ticket_required_on_rejection"])
        self.assertTrue(handoff["downstream_direct_repair_forbidden"])

    def test_al_murtakaz_identity_is_canonical_and_project_local(self) -> None:
        self.assertEqual(self.identity["id"], "al-murtakaz")
        self.assertEqual(self.identity["name_ar"], "المرتكز")
        self.assertEqual(self.identity["units"]["governance"]["name_ar"], "هيئة المرتكز")
        self.assertEqual(self.identity["units"]["workshop"]["name_ar"], "مشغل المرتكز")
        self.assertFalse(self.identity["authority"]["execution_authority"])
        self.assertFalse(self.identity["authority"]["may_open_stage8"])
        self.assertFalse(self.identity["authority"]["may_modify_parent_systems"])

    def test_full_review_keeps_p1_conditional_and_stage8_closed(self) -> None:
        self.assertEqual(
            self.review["verdict"],
            "STRONG_FOUNDATION_CONDITIONAL_GO_FOR_NON_AUTHORITATIVE_P1",
        )
        self.assertFalse(self.review["stage8_opened"])
        self.assertFalse(self.review["execution_authority_changed"])
        self.assertEqual(
            self.review["pre_prototype_gate"]["decision"],
            "CONDITIONAL_GO",
        )
        self.assertIn(
            "MP-02_MURTAKAZ_ORCHESTRATION_PROJECTION",
            self.review["pre_prototype_gate"]["required"],
        )

    def test_project_write_roots_do_not_include_parent_paths(self) -> None:
        roots = self.lock["project_write_roots"]
        self.assertEqual(
            roots,
            [
                "docs/operations/command-center/project-governance/",
                "state/command-center/project-governance/",
            ],
        )

        parent_paths = set(self.lock["parent_files_read_only"])
        for root in roots:
            self.assertTrue(all(not parent.startswith(root) for parent in parent_paths))


if __name__ == "__main__":
    unittest.main()
