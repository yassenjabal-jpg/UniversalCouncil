from __future__ import annotations

import json
import unittest
from pathlib import Path

from company.runtime.execution_contract import build_execution_contract
from company.runtime.task_aware_router import (
    TaskAwareRoutingError,
    route_execution,
    validate_task_router_config,
)

ROOT = Path(__file__).resolve().parents[2]
ROUTER_CFG = json.loads((ROOT / "company/config/task_aware_router.json").read_text(encoding="utf-8"))
CONTRACT_CFG = json.loads((ROOT / "company/config/execution_contract.json").read_text(encoding="utf-8"))


def contract(operation="edit", target="app", scope="document"):
    return build_execution_contract(
        {
            "decision_id":"route-contract",
            "what":"Perform bounded operation",
            "why":"Approved implementation",
            "constraints":[],
            "authority":{
                "principal":"technical_operator",
                "operations":[operation],
                "targets":[target],
                "scopes":[scope],
            },
            "blocking_conditions":[],
            "verification_target":"target state verified",
        },
        CONTRACT_CFG,
    )


class Phase3R14TaskAwareRouterTests(unittest.TestCase):
    def test_config_encodes_task_specific_route_orders(self):
        self.assertTrue(validate_task_router_config(ROUTER_CFG))
        self.assertEqual(
            ROUTER_CFG["task_classes"]["visual_interaction"]["order"],
            ["semantic_uia","visual_grounding","bounded_physical_input"],
        )
        self.assertEqual(
            ROUTER_CFG["task_classes"]["structured_application"]["order"][0],
            "native_api",
        )
        self.assertEqual(
            ROUTER_CFG["task_classes"]["external_service"]["order"][0],
            "authorized_connector_api",
        )

    def test_visual_interaction_prefers_semantic_uia(self):
        result = route_execution(
            {
                "task_class":"visual_interaction",
                "operation":"edit","target":"app","scope":"document",
                "available_routes":["semantic_uia","visual_grounding","bounded_physical_input"],
                "authorized_routes":["semantic_uia","visual_grounding"],
                "allow_physical_input":False,
            },
            contract(),
            ROUTER_CFG,
        )
        self.assertEqual(result["route"], "semantic_uia")
        self.assertTrue(result["route_reason"])
        self.assertTrue(result["route_version"])

    def test_structured_application_prefers_native_api_over_gui(self):
        result = route_execution(
            {
                "task_class":"structured_application",
                "operation":"edit","target":"app","scope":"document",
                "available_routes":["native_api","semantic_uia","visual_grounding"],
                "authorized_routes":["native_api","semantic_uia","visual_grounding"],
            },
            contract(),
            ROUTER_CFG,
        )
        self.assertEqual(result["route"], "native_api")

    def test_host_work_prefers_dc_when_authorized(self):
        result = route_execution(
            {
                "task_class":"host_work",
                "operation":"inspect","target":"YASSIN","scope":"worktree",
                "available_routes":["dc_control_plane","native_host_tooling"],
                "authorized_routes":["dc_control_plane","native_host_tooling"],
            },
            contract("inspect","YASSIN","worktree"),
            ROUTER_CFG,
        )
        self.assertEqual(result["route"], "dc_control_plane")

    def test_external_service_prefers_authorized_connector_api(self):
        result = route_execution(
            {
                "task_class":"external_service",
                "operation":"read","target":"github","scope":"repo",
                "available_routes":["authorized_connector_api","gui_semantic_uia"],
                "authorized_routes":["authorized_connector_api"],
            },
            contract("read","github","repo"),
            ROUTER_CFG,
        )
        self.assertEqual(result["route"], "authorized_connector_api")

    def test_fallback_skips_unavailable_or_unauthorized_routes_without_escalation(self):
        result = route_execution(
            {
                "task_class":"structured_application",
                "operation":"edit","target":"app","scope":"document",
                "available_routes":["native_api","semantic_uia","visual_grounding"],
                "authorized_routes":["semantic_uia","visual_grounding"],
            },
            contract(),
            ROUTER_CFG,
        )
        self.assertEqual(result["route"], "semantic_uia")
        self.assertIn("preferred_route_not_authorized", result["fallback_reasons"])
        self.assertEqual(result["authority"]["operation"], "edit")
        self.assertEqual(result["authority"]["target"], "app")
        self.assertEqual(result["authority"]["scope"], "document")

    def test_physical_input_requires_explicit_bounded_permission(self):
        request={
            "task_class":"visual_interaction",
            "operation":"edit","target":"app","scope":"document",
            "available_routes":["bounded_physical_input"],
            "authorized_routes":["bounded_physical_input"],
            "allow_physical_input":False,
        }
        with self.assertRaises(TaskAwareRoutingError):
            route_execution(request, contract(), ROUTER_CFG)

        result=route_execution({**request,"allow_physical_input":True},contract(),ROUTER_CFG)
        self.assertEqual(result["route"],"bounded_physical_input")

    def test_recovery_route_requires_inspect_diagnose_and_approved_alternate(self):
        base={
            "task_class":"recovery",
            "operation":"edit","target":"app","scope":"document",
            "available_routes":["semantic_uia","visual_grounding"],
            "authorized_routes":["semantic_uia","visual_grounding"],
            "recovery":{
                "inspected":True,
                "diagnosed":True,
                "approved_alternate_routes":["visual_grounding"],
            },
        }
        result=route_execution(base,contract(),ROUTER_CFG)
        self.assertEqual(result["route"],"visual_grounding")
        self.assertEqual(result["recovery_sequence"],["Inspect","Diagnose","Approved alternate path"])

        for key in ("inspected","diagnosed"):
            broken=json.loads(json.dumps(base))
            broken["recovery"][key]=False
            with self.subTest(key=key):
                with self.assertRaises(TaskAwareRoutingError):
                    route_execution(broken,contract(),ROUTER_CFG)

    def test_router_cannot_expand_contract_authority(self):
        base={
            "task_class":"structured_application",
            "operation":"edit","target":"app","scope":"document",
            "available_routes":["native_api"],
            "authorized_routes":["native_api"],
        }
        for field,value in (("operation","delete"),("target","other"),("scope","global")):
            with self.subTest(field=field):
                with self.assertRaises(TaskAwareRoutingError):
                    route_execution({**base,field:value},contract(),ROUTER_CFG)

    def test_output_declares_fallback_restrictions(self):
        result=route_execution(
            {
                "task_class":"structured_application",
                "operation":"edit","target":"app","scope":"document",
                "available_routes":["native_api"],
                "authorized_routes":["native_api"],
            },
            contract(),
            ROUTER_CFG,
        )
        self.assertIn("no_authority_expansion",result["fallback_restrictions"])
        self.assertIn("alternate_route_must_be_authorized",result["fallback_restrictions"])


if __name__=="__main__":
    unittest.main()
