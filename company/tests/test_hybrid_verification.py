import unittest

from company.runtime.hybrid_execution import HybridExecutionError, ResultState
from company.runtime.hybrid_verification import GuiPostStateVerifier, _extract_bridge_stdout


class MockAdapter:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def dispatch(self, action):
        self.calls.append(action)
        return self.result


def bridge_result(stdout):
    return {
        "state": ResultState.SUCCEEDED.value,
        "bridge_result": {
            "action": {
                "stdout": stdout,
            }
        },
    }


class HybridVerificationTests(unittest.TestCase):
    def test_extract_bridge_stdout_fail_closed(self):
        with self.assertRaises(HybridExecutionError):
            _extract_bridge_stdout({})
        with self.assertRaises(HybridExecutionError):
            _extract_bridge_stdout({"bridge_result": {}})
        with self.assertRaises(HybridExecutionError):
            _extract_bridge_stdout({"bridge_result": {"action": {}}})
        self.assertEqual(_extract_bridge_stdout(bridge_result('{"text":"x"}')), '{"text":"x"}')

    def test_missing_and_invalid_verify_specs(self):
        verifier = GuiPostStateVerifier(MockAdapter(bridge_result("{}")))
        self.assertEqual(verifier.verify({}, {})["mode"], "missing_verify_spec")
        invalid = verifier.verify({"verify": {"request": {}, "expect": "x"}}, {})
        self.assertEqual(invalid["mode"], "invalid_verify_spec")

    def test_probe_failure_is_not_verified(self):
        adapter = MockAdapter({"state": ResultState.FAILED.value})
        verifier = GuiPostStateVerifier(adapter)
        result = verifier.verify(
            {
                "verify": {
                    "request": {"action": "get_value"},
                    "expect": {"text": "x"},
                }
            },
            {},
        )
        self.assertFalse(result["verified"])
        self.assertEqual(result["mode"], "gui_post_state_probe_failed")

    def test_unreadable_probe_is_not_verified(self):
        verifier = GuiPostStateVerifier(MockAdapter(bridge_result("not-json")))
        result = verifier.verify(
            {
                "verify": {
                    "request": {"action": "get_value"},
                    "expect": {"text": "x"},
                }
            },
            {},
        )
        self.assertFalse(result["verified"])
        self.assertEqual(result["mode"], "gui_post_state_unreadable")

        bad_bridge = GuiPostStateVerifier(MockAdapter({"state": ResultState.SUCCEEDED.value, "bridge_result": {}}))
        result = bad_bridge.verify(
            {
                "verify": {
                    "request": {"action": "get_value"},
                    "expect": {"text": "x"},
                }
            },
            {},
        )
        self.assertFalse(result["verified"])

    def test_match_and_mismatch_are_reported(self):
        adapter = MockAdapter(bridge_result('{"text":"HYBRID_CHANGED\\r","elementId":"doc"}'))
        verifier = GuiPostStateVerifier(adapter)
        match = verifier.verify(
            {
                "verify": {
                    "request": {"action": "get_value", "selector": "doc"},
                    "expect": {"text": "HYBRID_CHANGED\r", "elementId": "doc"},
                }
            },
            {},
        )
        self.assertTrue(match["verified"])
        self.assertEqual(match["mode"], "independent_gui_post_state")
        self.assertEqual(len(adapter.calls), 1)

        mismatch = verifier.verify(
            {
                "verify": {
                    "request": {"action": "get_value", "selector": "doc"},
                    "expect": {"text": "OTHER"},
                }
            },
            {},
        )
        self.assertFalse(mismatch["verified"])
        self.assertFalse(mismatch["checks"]["text"]["match"])

    def test_non_dict_payload_cannot_match(self):
        verifier = GuiPostStateVerifier(MockAdapter(bridge_result('["x"]')))
        result = verifier.verify(
            {
                "verify": {
                    "request": {"action": "get_value"},
                    "expect": {"text": "x"},
                }
            },
            {},
        )
        self.assertFalse(result["verified"])
        self.assertIsNone(result["checks"]["text"]["actual"])


if __name__ == "__main__":
    unittest.main()
