import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from company.runtime.hybrid_execution import (
    CouncilVideoStudioGuiAdapter,
    DcHostAdapter,
    ExecutionPath,
    HybridExecutionError,
    HybridExecutor,
    PassthroughVerifier,
    ResultState,
    RiskTier,
    SharedExecutionState,
    authorize,
    choose_path,
    classify_risk,
    eligible_for_routine_graduation,
    enforce_tool_authority,
    load_config,
    load_state,
    plan_action,
    save_state,
    validate_config,
)

ROOT = Path(__file__).resolve().parents[2]
BASE_CFG = json.loads((ROOT / "company/config/hybrid_execution.json").read_text(encoding="utf-8"))
BASE_REGISTRY = json.loads((ROOT / "company/config/tool_authority.json").read_text(encoding="utf-8"))


class MockAdapter:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def dispatch(self, action):
        self.calls.append(action)
        return copy.deepcopy(self.result)


class MockVerifier:
    def __init__(self, verified):
        self.verified = verified
        self.calls = 0

    def verify(self, action, result):
        self.calls += 1
        return {"verified": self.verified, "mode": "mock"}


class SequenceAdapter:
    def __init__(self, results):
        self.results = list(results)
        self.calls = []

    def dispatch(self, action):
        self.calls.append(action)
        return copy.deepcopy(self.results[len(self.calls) - 1])


class HybridExecutionTests(unittest.TestCase):
    def test_config_load_and_invariants(self):
        self.assertTrue(validate_config(BASE_CFG))
        self.assertEqual(load_config(ROOT / "company/config/hybrid_execution.json")["version"], "0.2")

        bad = []
        for mutator in (
            lambda c: c.__setitem__("version", "9"),
            lambda c: c.__setitem__("primary_plane", "DC"),
            lambda c: c.__setitem__("secondary_plane", "GUI"),
            lambda c: c.__setitem__("execution_order", list(reversed(c["execution_order"]))),
            lambda c: c["routing_profiles"]["interactive_app"].__setitem__(
                "dc_fallback_requires_explicit_opt_in", False
            ),
            lambda c: c["routing_profiles"]["interactive_app"].__setitem__(
                "dc_must_not_bypass_gui_when_gui_available", False
            ),
            lambda c: c["gui_interaction_plane"].__setitem__("semantic_first", False),
            lambda c: c["gui_interaction_plane"].__setitem__("raw_coordinates_enabled", True),
            lambda c: c["shared_state"].__setitem__("single_physical_controller", False),
            lambda c: c["verification"].__setitem__("unknown_is_never_success", False),
            lambda c: c["result_projection"].__setitem__("enabled", False),
            lambda c: c["result_projection"].__setitem__("raw_output_default", True),
            lambda c: c["result_projection"].__setitem__("max_items", 0),
            lambda c: c["result_projection"].__setitem__("max_text_chars", 10),
            lambda c: c["automation_graduation"].__setitem__("verified_repeats_required", 1),
        ):
            cfg = copy.deepcopy(BASE_CFG)
            mutator(cfg)
            bad.append(cfg)
        for cfg in bad:
            with self.subTest(cfg=cfg):
                with self.assertRaises(HybridExecutionError):
                    validate_config(cfg)

        with tempfile.TemporaryDirectory() as tmp:
            malformed = Path(tmp) / "bad.json"
            malformed.write_text("{", encoding="utf-8")
            with self.assertRaises(HybridExecutionError):
                load_config(malformed)

    def test_risk_classification(self):
        self.assertEqual(classify_risk({"effect": "READ"}), RiskTier.T0)
        self.assertEqual(classify_risk({"effect": "EXECUTE"}), RiskTier.T1)
        self.assertEqual(classify_risk({"effect": "WRITE", "local_state_change": True}), RiskTier.T2)
        self.assertEqual(classify_risk({"effect": "WRITE", "external_consequence": True}), RiskTier.T3)
        self.assertEqual(classify_risk({"effect": "READ", "policy_blocked": True}), RiskTier.T4)

    def test_route_preference_and_fail_closed(self):
        self.assertEqual(
            choose_path(
                {
                    "gui_request": {"action": "inspect"},
                    "dc_capable": True,
                    "native_available": True,
                    "routine_available": True,
                }
            ),
            ExecutionPath.GUI_UIA,
        )
        self.assertEqual(
            choose_path(
                {
                    "visual_only": True,
                    "gui_request": {"action": "screenshot"},
                    "dc_capable": True,
                }
            ),
            ExecutionPath.GUI_VISUAL,
        )
        self.assertEqual(choose_path({"native_available": True, "dc_capable": True}), ExecutionPath.DC)
        self.assertEqual(
            choose_path(
                {
                    "task_class": "external_service",
                    "native_available": True,
                    "dc_capable": True,
                }
            ),
            ExecutionPath.NATIVE,
        )
        self.assertEqual(choose_path({"dc_capable": True, "routine_available": True}), ExecutionPath.DC)
        self.assertEqual(choose_path({"routine_available": True}), ExecutionPath.ROUTINE)
        self.assertEqual(choose_path({"gui_request": {"action": "inspect"}}), ExecutionPath.GUI_UIA)
        self.assertEqual(
            choose_path(
                {
                    "interactive_app": True,
                    "dc_capable": True,
                    "allow_dc_fallback": True,
                }
            ),
            ExecutionPath.DC,
        )
        with self.assertRaises(HybridExecutionError):
            choose_path({"interactive_app": True, "dc_capable": True})
        with self.assertRaises(HybridExecutionError):
            choose_path({"visual_only": True})
        with self.assertRaises(HybridExecutionError):
            choose_path({})

    def test_plan_authorities_and_verification(self):
        read_dc = plan_action({"id": "a", "dc_capable": True, "effect": "READ"}, BASE_CFG)
        self.assertEqual(read_dc.authority_operation, "remote_shell.read")
        self.assertFalse(read_dc.requires_verification)

        write_dc = plan_action(
            {"id": "b", "dc_capable": True, "effect": "WRITE", "local_state_change": True},
            BASE_CFG,
        )
        self.assertEqual(write_dc.authority_operation, "remote_shell.execute")
        self.assertTrue(write_dc.requires_verification)

        observe = plan_action({"id": "c", "gui_request": {"action": "screenshot"}}, BASE_CFG)
        self.assertEqual(observe.authority_operation, "desktop_computer_use.observe")

        control = plan_action(
            {"id": "d", "effect": "WRITE", "local_state_change": True, "gui_request": {"action": "set_value"}},
            BASE_CFG,
        )
        self.assertEqual(control.authority_operation, "desktop_computer_use.control")
        self.assertTrue(control.requires_verification)

        gui_beats_dc = plan_action(
            {
                "id": "gui-first",
                "effect": "WRITE",
                "local_state_change": True,
                "interactive_app": True,
                "dc_capable": True,
                "gui_request": {"action": "click"},
            },
            BASE_CFG,
        )
        self.assertEqual(gui_beats_dc.path, ExecutionPath.GUI_UIA)
        self.assertEqual(gui_beats_dc.authority_operation, "desktop_computer_use.control")

        external = plan_action(
            {
                "id": "e",
                "native_available": True,
                "authority_operation": "external.publish",
                "effect": "WRITE",
                "external_consequence": True,
            },
            BASE_CFG,
        )
        self.assertTrue(external.requires_owner_confirmation)

        with self.assertRaises(HybridExecutionError):
            plan_action({"dc_capable": True}, BASE_CFG)
        with self.assertRaises(HybridExecutionError):
            plan_action({"id": "x", "policy_blocked": True, "dc_capable": True}, BASE_CFG)

    def test_plan_rejects_unknown_gui_and_missing_native_authority(self):
        with self.assertRaises(HybridExecutionError):
            plan_action({"id": "x", "gui_request": {"action": "unknown"}}, BASE_CFG)
        with self.assertRaises(HybridExecutionError):
            plan_action({"id": "n", "native_available": True}, BASE_CFG)
        with self.assertRaises(HybridExecutionError):
            plan_action({"id": "r", "routine_available": True}, BASE_CFG)

    def test_authorization_boundaries(self):
        t0 = plan_action({"id": "a", "dc_capable": True, "effect": "READ"}, BASE_CFG)
        t1 = plan_action({"id": "b", "dc_capable": True, "effect": "EXECUTE"}, BASE_CFG)
        t3 = plan_action(
            {
                "id": "c",
                "dc_capable": True,
                "effect": "WRITE",
                "external_consequence": True,
            },
            BASE_CFG,
        )
        self.assertTrue(authorize(t0, task_approved=False))
        self.assertFalse(authorize(t1, task_approved=False))
        self.assertTrue(authorize(t1, task_approved=True))
        self.assertFalse(authorize(t3, task_approved=True, owner_confirmed=False))
        self.assertTrue(authorize(t3, task_approved=True, owner_confirmed=True))

    def test_tool_authority_is_enforced_before_dispatch(self):
        allowed = plan_action(
            {"id": "allowed", "native_available": True, "authority_operation": "github.read"},
            BASE_CFG,
        )
        self.assertEqual(enforce_tool_authority(allowed, BASE_REGISTRY)["operation"], "github.read")

        blocked = plan_action(
            {
                "id": "blocked",
                "native_available": True,
                "authority_operation": "external.publish",
                "effect": "WRITE",
                "external_consequence": True,
            },
            BASE_CFG,
        )
        with self.assertRaises(HybridExecutionError):
            enforce_tool_authority(blocked, BASE_REGISTRY)

        approval_blocked_registry = copy.deepcopy(BASE_REGISTRY)
        approval_blocked = next(
            item for item in approval_blocked_registry["capabilities"] if item["operation"] == "github.read"
        )
        approval_blocked["approval_policy"] = "BLOCKED"
        with self.assertRaises(HybridExecutionError):
            enforce_tool_authority(allowed, approval_blocked_registry)

        unknown = plan_action(
            {"id": "unknown", "native_available": True, "authority_operation": "missing.operation"},
            BASE_CFG,
        )
        with self.assertRaises(HybridExecutionError):
            enforce_tool_authority(unknown, BASE_REGISTRY)

        adapter = MockAdapter({"state": ResultState.SUCCEEDED.value})
        executor = HybridExecutor(
            BASE_CFG,
            native_adapter=adapter,
            authority_registry=BASE_REGISTRY,
        )
        state = SharedExecutionState("blocked-task")
        result = executor.execute(
            blocked.payload,
            state,
            requester="commercial",
            task_approved=True,
            owner_confirmed=True,
        )
        self.assertEqual(result["state"], ResultState.BLOCKED.value)
        self.assertEqual(adapter.calls, [])

        governed = HybridExecutor(BASE_CFG, authority_registry=BASE_REGISTRY)
        state = SharedExecutionState("approval-task")
        no_approval = governed.execute(
            {"id": "read", "dc_capable": True, "effect": "READ"},
            state,
            requester="tech",
            task_approved=False,
        )
        self.assertEqual(no_approval["state"], ResultState.BLOCKED.value)
        self.assertIn("approval required", no_approval["reason"])
        approved = governed.execute(
            {"id": "read2", "dc_capable": True, "effect": "READ"},
            state,
            requester="tech",
            task_approved=True,
        )
        self.assertEqual(approved["state"], ResultState.HOST_DISPATCH_REQUIRED.value)

    def test_shared_state_persists_and_restores(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state/task.json"
            state = SharedExecutionState("task")
            state.acquire_controller("tech")
            state.last_path = "dc_control_plane"
            state.last_result = "SUCCEEDED"
            save_state(state, path)
            restored = load_state(path)
            self.assertEqual(restored.as_dict(), state.as_dict())

            with self.assertRaises(HybridExecutionError):
                SharedExecutionState.from_dict({})
            broken = Path(tmp) / "broken.json"
            broken.write_text("{", encoding="utf-8")
            with self.assertRaises(HybridExecutionError):
                load_state(broken)

    def test_shared_state_lease_delta_and_event_window(self):
        state = SharedExecutionState("task")
        with self.assertRaises(HybridExecutionError):
            state.acquire_controller("")
        state.acquire_controller("one")
        state.acquire_controller("one")
        with self.assertRaises(HybridExecutionError):
            state.acquire_controller("two")
        with self.assertRaises(HybridExecutionError):
            state.release_controller("two")
        state.release_controller("one")
        self.assertIsNone(state.controller_lease)
        with self.assertRaises(HybridExecutionError):
            state.delta(-1)
        for index in range(15):
            state._append({"type": "test", "index": index})
        self.assertEqual(len(state.events), 12)
        self.assertEqual(state.delta(state.revision - 2)["events"][-1]["index"], 14)

    def test_dc_host_adapter_formats_host_request(self):
        adapter = DcHostAdapter()
        read = adapter.dispatch({"effect": "READ", "dc_request": {"cmd": "inspect"}})
        self.assertEqual(read["state"], ResultState.HOST_DISPATCH_REQUIRED.value)
        self.assertEqual(read["host_request"]["operation"], "remote_shell.read")
        write = adapter.dispatch({"effect": "WRITE", "dc_request": {"cmd": "change"}})
        self.assertEqual(write["host_request"]["operation"], "remote_shell.execute")

    def test_gui_adapter_initialization_and_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / "bridge/yassin_control/verified_action.py"
            script.parent.mkdir(parents=True)
            script.write_text("print('{}')", encoding="utf-8")
            cfg = copy.deepcopy(BASE_CFG)
            cfg["gui_interaction_plane"]["root_hint"] = str(root)

            adapter = CouncilVideoStudioGuiAdapter(cfg, env={})
            self.assertEqual(adapter.root, root.resolve())

            success = type("Proc", (), {"returncode": 0, "stdout": '{"action": {"ok": true}}', "stderr": ""})()
            with patch("company.runtime.hybrid_execution.subprocess.run", return_value=success):
                result = adapter.dispatch({"gui_request": {"action": "screenshot", "app": "demo"}})
            self.assertEqual(result["state"], ResultState.SUCCEEDED.value)
            self.assertTrue(result["bridge_result"]["action"]["ok"])
            self.assertEqual(list(root.glob("council_hybrid_*.json")), [])

            failure = type("Proc", (), {"returncode": 2, "stdout": "", "stderr": "failed"})()
            with patch("company.runtime.hybrid_execution.subprocess.run", return_value=failure):
                result = adapter.dispatch({"gui_request": {"action": "screenshot", "app": "demo"}})
            self.assertEqual(result["state"], ResultState.FAILED.value)

            non_json = type("Proc", (), {"returncode": 0, "stdout": "not-json", "stderr": ""})()
            with patch("company.runtime.hybrid_execution.subprocess.run", return_value=non_json):
                with self.assertRaises(HybridExecutionError):
                    adapter.dispatch({"gui_request": {"action": "screenshot", "app": "demo"}})

            with self.assertRaises(HybridExecutionError):
                adapter.dispatch({})

    def test_gui_adapter_missing_root_or_script(self):
        cfg = copy.deepcopy(BASE_CFG)
        cfg["gui_interaction_plane"]["root_hint"] = "Z:\\definitely-missing"
        with self.assertRaises(HybridExecutionError):
            CouncilVideoStudioGuiAdapter(cfg, env={})

        with tempfile.TemporaryDirectory() as tmp:
            cfg = copy.deepcopy(BASE_CFG)
            cfg["gui_interaction_plane"]["root_hint"] = tmp
            with self.assertRaises(HybridExecutionError):
                CouncilVideoStudioGuiAdapter(cfg, env={})

    def test_gui_adapter_prefers_environment_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / "bridge/yassin_control/verified_action.py"
            script.parent.mkdir(parents=True)
            script.write_text("print('{}')", encoding="utf-8")
            adapter = CouncilVideoStudioGuiAdapter(
                BASE_CFG,
                env={"COUNCIL_VIDEO_STUDIO_ROOT": str(root)},
            )
            self.assertEqual(adapter.root, root.resolve())

    def test_passthrough_verifier_paths(self):
        verifier = PassthroughVerifier()
        explicit = verifier.verify(
            {},
            {"verification": {"verified": True, "independent": True, "mode": "explicit"}},
        )
        self.assertEqual(explicit["mode"], "explicit")
        provider = verifier.verify({}, {"state": ResultState.SUCCEEDED.value})
        self.assertFalse(provider["verified"])
        missing = verifier.verify(
            {"verify": {"action": "wait_for"}},
            {"state": ResultState.SUCCEEDED.value},
        )
        self.assertFalse(missing["verified"])

    def test_executor_dc_host_dispatch_and_blocked(self):
        executor = HybridExecutor(BASE_CFG, authority_registry=BASE_REGISTRY)
        state = SharedExecutionState("t1")
        result = executor.execute(
            {"id": "read", "dc_capable": True, "effect": "READ"},
            state,
            requester="tech",
            task_approved=True,
        )
        self.assertEqual(result["state"], ResultState.HOST_DISPATCH_REQUIRED.value)
        self.assertEqual(state.last_result, ResultState.HOST_DISPATCH_REQUIRED.value)

        blocked = executor.execute(
            {"id": "write", "dc_capable": True, "effect": "EXECUTE"},
            state,
            requester="tech",
            task_approved=False,
        )
        self.assertEqual(blocked["state"], ResultState.BLOCKED.value)
        self.assertEqual(state.last_result, ResultState.BLOCKED.value)

    def test_executor_gui_controller_is_released_on_success_and_failure(self):
        success_adapter = MockAdapter(
            {
                "state": ResultState.SUCCEEDED.value,
                "verification": {"verified": True, "independent": True, "mode": "test"},
            }
        )
        executor = HybridExecutor(BASE_CFG, gui_adapter=success_adapter, authority_registry=BASE_REGISTRY)
        state = SharedExecutionState("t2")
        result = executor.execute(
            {"id": "gui", "gui_request": {"action": "click"}},
            state,
            requester="media",
            task_approved=True,
        )
        self.assertEqual(result["state"], ResultState.SUCCEEDED.value)
        self.assertIsNone(state.controller_lease)

        failed_adapter = MockAdapter({"state": ResultState.FAILED.value})
        executor = HybridExecutor(BASE_CFG, gui_adapter=failed_adapter, authority_registry=BASE_REGISTRY)
        state = SharedExecutionState("t3")
        result = executor.execute(
            {"id": "gui2", "gui_request": {"action": "click"}},
            state,
            requester="media",
            task_approved=True,
        )
        self.assertEqual(result["state"], ResultState.FAILED.value)
        self.assertIsNone(state.controller_lease)

    def test_executor_unknown_when_required_verification_fails(self):
        adapter = MockAdapter({"state": ResultState.SUCCEEDED.value})
        verifier = MockVerifier(False)
        executor = HybridExecutor(BASE_CFG, gui_adapter=adapter, verifier=verifier, authority_registry=BASE_REGISTRY)
        state = SharedExecutionState("t4")
        result = executor.execute(
            {
                "id": "edit",
                "effect": "WRITE",
                "local_state_change": True,
                "gui_request": {"action": "set_value"},
            },
            state,
            requester="media",
            task_approved=True,
        )
        self.assertEqual(result["state"], ResultState.UNKNOWN.value)
        self.assertEqual(verifier.calls, 1)
        self.assertIsNone(state.controller_lease)

    def test_executor_verified_state_change_succeeds(self):
        adapter = MockAdapter({"state": ResultState.SUCCEEDED.value})
        verifier = MockVerifier(True)
        executor = HybridExecutor(BASE_CFG, gui_adapter=adapter, verifier=verifier, authority_registry=BASE_REGISTRY)
        state = SharedExecutionState("t5")
        result = executor.execute(
            {
                "id": "edit",
                "effect": "WRITE",
                "local_state_change": True,
                "gui_request": {"action": "set_value"},
            },
            state,
            requester="media",
            task_approved=True,
        )
        self.assertEqual(result["state"], ResultState.SUCCEEDED.value)
        self.assertTrue(result["verification"]["verified"])
        self.assertEqual(state.last_result, ResultState.SUCCEEDED.value)

    def test_executor_native_and_routine_adapters(self):
        native = MockAdapter({"state": ResultState.SUCCEEDED.value})
        routine = MockAdapter({"state": ResultState.SUCCEEDED.value})
        executor = HybridExecutor(
            BASE_CFG, native_adapter=native, routine_adapter=routine, authority_registry=BASE_REGISTRY
        )
        state = SharedExecutionState("t6")
        n = executor.execute(
            {"id": "n", "native_available": True, "authority_operation": "github.read"},
            state,
            requester="tech",
            task_approved=True,
        )
        self.assertEqual(n["state"], ResultState.SUCCEEDED.value)
        r = executor.execute(
            {
                "id": "r",
                "routine_available": True,
                "authority_operation": "remote_shell.execute",
                "authority_target": "YASSIN",
            },
            state,
            requester="tech",
            task_approved=True,
        )
        self.assertEqual(r["state"], ResultState.SUCCEEDED.value)

    def test_executor_missing_adapters_fail_closed(self):
        executor = HybridExecutor(BASE_CFG, authority_registry=BASE_REGISTRY)
        state = SharedExecutionState("t7")
        with self.assertRaises(HybridExecutionError):
            executor._adapter_for("unexpected")  # type: ignore[arg-type]
        with self.assertRaises(HybridExecutionError):
            executor.execute(
                {"id": "n", "native_available": True, "authority_operation": "github.read"},
                state,
                requester="tech",
                task_approved=True,
            )
        with self.assertRaises(HybridExecutionError):
            executor.execute(
                {
                    "id": "r",
                    "routine_available": True,
                    "authority_operation": "remote_shell.execute",
                    "authority_target": "YASSIN",
                },
                state,
                requester="tech",
                task_approved=True,
            )
        with self.assertRaises(HybridExecutionError):
            executor.execute(
                {"id": "g", "gui_request": {"action": "screenshot"}},
                state,
                requester="tech",
                task_approved=True,
            )

    def test_controller_lease_conflict_blocks_second_gui_controller(self):
        adapter = MockAdapter({"state": ResultState.SUCCEEDED.value})
        executor = HybridExecutor(BASE_CFG, gui_adapter=adapter, authority_registry=BASE_REGISTRY)
        state = SharedExecutionState("t8")
        state.acquire_controller("other")
        result = executor.execute(
            {"id": "g", "gui_request": {"action": "click"}},
            state,
            requester="media",
            task_approved=True,
        )
        self.assertEqual(result["state"], ResultState.BLOCKED.value)

    def test_batch_requires_bounds_and_keeps_single_controller_lease(self):
        adapter = MockAdapter(
            {
                "state": ResultState.SUCCEEDED.value,
                "verification": {"verified": True, "independent": True, "mode": "test"},
            }
        )
        executor = HybridExecutor(BASE_CFG, gui_adapter=adapter, authority_registry=BASE_REGISTRY)
        state = SharedExecutionState("batch")
        actions = [
            {"id": "a", "gui_request": {"action": "click"}},
            {"id": "b", "gui_request": {"action": "click"}},
        ]
        result = executor.execute_batch(
            actions,
            state,
            requester="media",
            task_approved=True,
        )
        self.assertEqual(result["state"], ResultState.SUCCEEDED.value)
        self.assertEqual(result["completed"], 2)
        self.assertIsNone(result["stopped_at"])
        self.assertIsNone(state.controller_lease)
        controller_events = [
            event["type"] for event in state.events if event["type"] in {"controller_acquired", "controller_released"}
        ]
        self.assertEqual(controller_events, ["controller_acquired", "controller_released"])

        with self.assertRaises(HybridExecutionError):
            executor.execute_batch([], state, requester="media", task_approved=True)
        too_many = actions * 4
        with self.assertRaises(HybridExecutionError):
            executor.execute_batch(too_many, state, requester="media", task_approved=True)

    def test_batch_without_gui_control_does_not_acquire_controller(self):
        native = MockAdapter({"state": ResultState.SUCCEEDED.value})
        executor = HybridExecutor(BASE_CFG, native_adapter=native, authority_registry=BASE_REGISTRY)
        state = SharedExecutionState("batch-native")
        result = executor.execute_batch(
            [
                {"id": "n1", "native_available": True, "authority_operation": "github.read"},
                {"id": "n2", "native_available": True, "authority_operation": "github.read"},
            ],
            state,
            requester="tech",
            task_approved=True,
        )
        self.assertEqual(result["state"], ResultState.SUCCEEDED.value)
        self.assertFalse(any(event["type"] == "controller_acquired" for event in state.events))

    def test_batch_stops_on_first_non_success(self):
        adapter = SequenceAdapter(
            [
                {
                    "state": ResultState.SUCCEEDED.value,
                    "verification": {"verified": True, "independent": True, "mode": "test"},
                },
                {"state": ResultState.FAILED.value},
                {
                    "state": ResultState.SUCCEEDED.value,
                    "verification": {"verified": True, "independent": True, "mode": "test"},
                },
            ]
        )
        executor = HybridExecutor(BASE_CFG, gui_adapter=adapter, authority_registry=BASE_REGISTRY)
        state = SharedExecutionState("batch-stop")
        actions = [
            {"id": "a", "gui_request": {"action": "click"}},
            {"id": "b", "gui_request": {"action": "click"}},
            {"id": "c", "gui_request": {"action": "click"}},
        ]
        result = executor.execute_batch(
            actions,
            state,
            requester="media",
            task_approved=True,
        )
        self.assertEqual(result["state"], ResultState.FAILED.value)
        self.assertEqual(result["completed"], 1)
        self.assertEqual(result["stopped_at"], 1)
        self.assertEqual(len(adapter.calls), 2)
        self.assertIsNone(state.controller_lease)

    def test_retain_controller_leaves_lease_for_batch_owner(self):
        adapter = MockAdapter(
            {
                "state": ResultState.SUCCEEDED.value,
                "verification": {"verified": True, "independent": True, "mode": "test"},
            }
        )
        executor = HybridExecutor(BASE_CFG, gui_adapter=adapter, authority_registry=BASE_REGISTRY)
        state = SharedExecutionState("retain")
        result = executor.execute(
            {"id": "a", "gui_request": {"action": "click"}},
            state,
            requester="media",
            task_approved=True,
            retain_controller=True,
        )
        self.assertEqual(result["state"], ResultState.SUCCEEDED.value)
        self.assertEqual(state.controller_lease, "media")
        state.release_controller("media")
        executor.controller_lease.release("desktop:YASSIN", "media")

    def test_routine_graduation_requires_verified_clean_repeats(self):
        clean = [
            {"state": ResultState.SUCCEEDED.value, "verified": True},
            {"state": ResultState.SUCCEEDED.value, "verified": True},
            {"state": ResultState.SUCCEEDED.value, "verified": True},
        ]
        self.assertTrue(eligible_for_routine_graduation(clean, BASE_CFG))

        too_few = clean[:2]
        self.assertFalse(eligible_for_routine_graduation(too_few, BASE_CFG))

        unknown = clean + [{"state": ResultState.UNKNOWN.value, "verified": False}]
        self.assertFalse(eligible_for_routine_graduation(unknown, BASE_CFG))

        accidental = clean + [{"state": ResultState.SUCCEEDED.value, "verified": True, "accidental_action": True}]
        self.assertFalse(eligible_for_routine_graduation(accidental, BASE_CFG))


if __name__ == "__main__":
    unittest.main()
