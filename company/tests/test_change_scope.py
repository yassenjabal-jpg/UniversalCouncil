import subprocess
import unittest
from unittest.mock import patch

from tools.change_scope import (
    filter_production_files,
    filter_python_files,
    git_changed_files,
    normalize_paths,
)


class ChangeScopeTests(unittest.TestCase):
    def test_normalize_paths_converts_windows_slashes_and_deduplicates(self):
        self.assertEqual(
            normalize_paths(
                [
                    r"company\runtime\policy.py",
                    "./tools/validate_config.py",
                    "tools/validate_config.py",
                    "",
                ]
            ),
            ["company/runtime/policy.py", "tools/validate_config.py"],
        )

    def test_filter_python_files_keeps_only_existing_python_files(self):
        result = filter_python_files(
            [
                "company/runtime/policy.py",
                "README.md",
                "company/runtime/not_real.py",
            ]
        )
        self.assertEqual(result, ["company/runtime/policy.py"])

    def test_filter_production_files_is_runtime_python_only(self):
        result = filter_production_files(
            [
                "company/runtime/policy.py",
                "company/tests/test_stage0.py",
                "tools/validate_config.py",
            ]
        )
        self.assertEqual(result, ["company/runtime/policy.py"])

    @patch("tools.change_scope.subprocess.run")
    def test_git_changed_files_is_deterministic_and_shell_free(self, run):
        run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="tools/validate_config.py\ncompany\\runtime\\policy.py\ntools/validate_config.py\n",
            stderr="",
        )
        result = git_changed_files("origin/main", "HEAD")
        self.assertEqual(
            result,
            ["company/runtime/policy.py", "tools/validate_config.py"],
        )
        run.assert_called_once_with(
            [
                "git",
                "diff",
                "--name-only",
                "--diff-filter=ACMR",
                "origin/main...HEAD",
                "--",
            ],
            shell=False,
            check=True,
            text=True,
            capture_output=True,
        )

    @patch("tools.change_scope.subprocess.run")
    def test_git_changed_files_fails_closed_for_invalid_base(self, run):
        run.side_effect = subprocess.CalledProcessError(
            128,
            ["git", "diff"],
            stderr="fatal: bad revision",
        )
        with self.assertRaises(subprocess.CalledProcessError):
            git_changed_files("missing/ref")


if __name__ == "__main__":
    unittest.main()
