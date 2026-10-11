import unittest

from tools.coverage_gate import evaluate_coverage, file_metrics


def coverage_file(line_percent, branch_percent=None):
    statements = 100
    covered = round(statements * line_percent / 100)
    branches = 0 if branch_percent is None else 100
    covered_branches = 0 if branch_percent is None else round(branches * branch_percent / 100)
    return {
        "summary": {
            "covered_lines": covered,
            "num_statements": statements,
            "percent_covered": line_percent,
            "num_branches": branches,
            "covered_branches": covered_branches,
        }
    }


class CoverageGateTests(unittest.TestCase):
    def test_legacy_file_equal_to_baseline_passes_below_95(self):
        current = {"files": {"company/runtime/policy.py": coverage_file(70.0, 60.0)}}
        baseline = {
            "version": "1.0",
            "files": {"company/runtime/policy.py": {"line": 70.0, "branch": 60.0}},
        }
        self.assertEqual(
            evaluate_coverage(current, baseline, ["company/runtime/policy.py"]),
            [],
        )

    def test_legacy_line_regression_fails(self):
        current = {"files": {"company/runtime/policy.py": coverage_file(69.9, 60.0)}}
        baseline = {
            "version": "1.0",
            "files": {"company/runtime/policy.py": {"line": 70.0, "branch": 60.0}},
        }
        failures = evaluate_coverage(current, baseline, ["company/runtime/policy.py"])
        self.assertTrue(any("line coverage regressed" in failure for failure in failures))

    def test_new_runtime_file_below_95_fails(self):
        current = {"files": {"company/runtime/new_module.py": coverage_file(94.9)}}
        baseline = {"version": "1.0", "files": {}}
        failures = evaluate_coverage(current, baseline, ["company/runtime/new_module.py"])
        self.assertTrue(any("new file line coverage" in failure for failure in failures))

    def test_new_runtime_file_at_95_passes_without_branches(self):
        current = {"files": {"company/runtime/new_module.py": coverage_file(95.0)}}
        baseline = {"version": "1.0", "files": {}}
        self.assertEqual(
            evaluate_coverage(current, baseline, ["company/runtime/new_module.py"]),
            [],
        )

    def test_file_metrics_reports_branch_percentage_separately(self):
        metrics = file_metrics(coverage_file(80.0, 50.0))
        self.assertEqual(metrics["line"], 80.0)
        self.assertEqual(metrics["branch"], 50.0)

    def test_missing_current_coverage_fails_closed(self):
        baseline = {
            "version": "1.0",
            "files": {"company/runtime/policy.py": {"line": 70.0, "branch": None}},
        }
        failures = evaluate_coverage({"files": {}}, baseline, ["company/runtime/policy.py"])
        self.assertTrue(any("missing current coverage" in failure for failure in failures))

    def test_malformed_baseline_fails_closed(self):
        failures = evaluate_coverage(
            {"files": {"company/runtime/policy.py": coverage_file(90.0)}},
            {"version": "1.0"},
            ["company/runtime/policy.py"],
        )
        self.assertTrue(any("invalid baseline" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
