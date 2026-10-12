import unittest

from company.runtime.hybrid_projection import (
    project_execution_result,
    project_provider_result,
    project_text_payload,
)


class HybridProjectionTests(unittest.TestCase):
    def test_text_payload_handles_empty_text_and_json(self):
        self.assertEqual(project_text_payload(""), {"kind": "empty"})
        value = project_text_payload('{"text":"abc","elementId":"x"}')
        self.assertEqual(value["kind"], "json")
        self.assertEqual(value["value"]["text"], "abc")

    def test_text_payload_compacts_long_plain_text(self):
        value = project_text_payload("x" * 100, max_text=20)
        self.assertEqual(value["kind"], "text")
        self.assertEqual(value["chars"], 100)
        self.assertIn("omitted", value["preview"])

    def test_json_list_reports_count_and_limits_sample(self):
        value = project_text_payload(
            '[{"processName":"a"},{"processName":"b"},{"processName":"c"}]',
            max_items=2,
        )
        self.assertEqual(value["kind"], "json_list")
        self.assertEqual(value["items"], 3)
        self.assertEqual(value["sample"][-1], {"omitted_items": 1})

        short = project_text_payload('[{"processName":"a"}]', max_items=2)
        self.assertEqual(short["sample"], [{"processName": "a"}])

    def test_generic_dict_projection_limits_keys(self):
        value = project_text_payload('{"a":1,"b":2,"c":3}', max_items=2)
        self.assertEqual(value["value"]["_omitted_keys"], 1)

    def test_provider_projection_compacts_bridge_stdout(self):
        result = {
            "state": "SUCCEEDED",
            "plane": "GUI",
            "bridge_result": {
                "action": {
                    "action": "list_windows",
                    "returncode": 0,
                    "capture_path": None,
                    "stdout": '[{"processName":"a"},{"processName":"b"}]',
                    "stderr": "",
                }
            },
        }
        projected = project_provider_result(result, max_items=1)
        self.assertEqual(projected["state"], "SUCCEEDED")
        self.assertEqual(projected["bridge"]["action"], "list_windows")
        self.assertEqual(projected["bridge"]["stdout"]["kind"], "window_list")
        self.assertEqual(projected["bridge"]["stdout"]["items"], 2)
        self.assertEqual(projected["bridge"]["stdout"]["process_counts"], {"a": 1})
        self.assertIsNone(projected["bridge"]["stdout"]["foreground"])
        self.assertNotIn("bridge_result", projected)

    def test_provider_projection_includes_errors_and_host_handoff(self):
        result = {
            "state": "HOST_DISPATCH_REQUIRED",
            "plane": "DC",
            "stderr": "e" * 50,
            "host_request": {
                "operation": "remote_shell.read",
                "payload": {"kind": "read_file", "path": "x"},
            },
        }
        projected = project_provider_result(result, max_text=12)
        self.assertEqual(projected["host_request"]["operation"], "remote_shell.read")
        self.assertIn("omitted", projected["stderr"])

        bridge_error = project_provider_result(
            {
                "bridge_result": {
                    "action": {
                        "action": "inspect",
                        "returncode": 0,
                        "stdout": None,
                        "stderr": "bridge warning",
                    }
                }
            }
        )
        self.assertEqual(bridge_error["bridge"]["stderr"], "bridge warning")

        no_action = project_provider_result({"bridge_result": {"action": "not-a-dict"}})
        self.assertEqual(no_action["bridge_result"]["action"], "not-a-dict")

    def test_provider_projection_list_windows_fallbacks_and_foreground(self):
        malformed = project_provider_result(
            {
                "bridge_result": {
                    "action": {
                        "action": "list_windows",
                        "returncode": 0,
                        "stdout": "not-json",
                    }
                }
            }
        )
        self.assertEqual(malformed["bridge"]["stdout"]["kind"], "text")

        non_list = project_provider_result(
            {
                "bridge_result": {
                    "action": {
                        "action": "list_windows",
                        "returncode": 0,
                        "stdout": '{"processName":"x"}',
                    }
                }
            }
        )
        self.assertEqual(non_list["bridge"]["stdout"]["kind"], "json")

        foreground = project_provider_result(
            {
                "bridge_result": {
                    "action": {
                        "action": "list_windows",
                        "returncode": 0,
                        "stdout": (
                            '[{"processName":"a","className":"A","isForeground":false},'
                            '{"processName":"b","className":"B","isForeground":true},'
                            '"noise"]'
                        ),
                    }
                }
            }
        )
        self.assertEqual(
            foreground["bridge"]["stdout"]["foreground"],
            {"processName": "b", "className": "B"},
        )

    def test_provider_projection_falls_back_for_unknown_shape(self):
        projected = project_provider_result({"alpha": "beta"})
        self.assertEqual(projected["alpha"], "beta")

    def test_execution_projection_keeps_reason_and_verification_not_raw_payload(self):
        execution = {
            "state": "UNKNOWN",
            "reason": "r" * 40,
            "result": {
                "state": "SUCCEEDED",
                "plane": "GUI",
                "bridge_result": {
                    "action": {
                        "action": "get_value",
                        "returncode": 0,
                        "stdout": '{"text":"secret-but-bounded"}',
                    }
                },
            },
            "verification": {
                "verified": False,
                "mode": "independent_gui_post_state",
                "checks": {"text": {"match": False, "expected": "x", "actual": "y"}},
            },
        }
        projected = project_execution_result(execution, max_text=10, max_items=3)
        self.assertEqual(projected["state"], "UNKNOWN")
        self.assertIn("omitted", projected["reason"])
        self.assertIn("verification", projected)
        self.assertNotIn("planned", projected)

        minimal = project_execution_result({"state": "SUCCEEDED"})
        self.assertEqual(minimal, {"state": "SUCCEEDED"})


if __name__ == "__main__":
    unittest.main()
