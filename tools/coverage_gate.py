from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.change_scope import git_changed_files, normalize_paths

TOLERANCE = 0.01


def file_metrics(coverage_file: dict[str, Any]) -> dict[str, float | None]:
    summary = coverage_file.get("summary")
    if not isinstance(summary, dict):
        raise ValueError("coverage file is missing summary")
    line = summary.get("percent_covered")
    if not isinstance(line, (int, float)):
        raise ValueError("coverage file is missing percent_covered")
    branches = summary.get("num_branches", 0)
    covered_branches = summary.get("covered_branches", 0)
    if not isinstance(branches, int) or not isinstance(covered_branches, int):
        raise ValueError("coverage branch counters are invalid")
    branch = None if branches == 0 else covered_branches / branches * 100.0
    return {"line": float(line), "branch": branch}


def _baseline_files(baseline: dict[str, Any]) -> dict[str, Any]:
    if baseline.get("version") != "1.0" or not isinstance(baseline.get("files"), dict):
        raise ValueError("baseline must contain version 1.0 and files mapping")
    return baseline["files"]


def evaluate_coverage(
    current: dict[str, Any],
    baseline: dict[str, Any],
    changed_files: list[str],
    new_file_min: float = 95.0,
) -> list[str]:
    failures: list[str] = []
    try:
        baseline_files = _baseline_files(baseline)
    except (TypeError, ValueError) as exc:
        return [f"invalid baseline: {exc}"]

    current_files = current.get("files")
    if not isinstance(current_files, dict):
        return ["invalid current coverage: missing files mapping"]

    production_files = [
        path
        for path in normalize_paths(changed_files)
        if path.startswith("company/runtime/") and path.endswith(".py")
    ]
    for path in production_files:
        entry = current_files.get(path)
        if not isinstance(entry, dict):
            failures.append(f"{path}: missing current coverage")
            continue
        try:
            metrics = file_metrics(entry)
        except ValueError as exc:
            failures.append(f"{path}: invalid current coverage: {exc}")
            continue

        prior = baseline_files.get(path)
        if prior is None:
            if metrics["line"] + TOLERANCE < new_file_min:
                failures.append(f"{path}: new file line coverage {metrics['line']:.2f}% is below {new_file_min:.2f}%")
            continue
        if not isinstance(prior, dict) or not isinstance(prior.get("line"), (int, float)):
            failures.append(f"{path}: invalid baseline entry")
            continue

        baseline_line = float(prior["line"])
        if metrics["line"] + TOLERANCE < baseline_line:
            failures.append(f"{path}: line coverage regressed from {baseline_line:.2f}% to {metrics['line']:.2f}%")

        baseline_branch = prior.get("branch")
        if baseline_branch is not None:
            if not isinstance(baseline_branch, (int, float)):
                failures.append(f"{path}: invalid baseline branch coverage")
            elif metrics["branch"] is None:
                failures.append(f"{path}: branch coverage disappeared from current report")
            elif metrics["branch"] + TOLERANCE < float(baseline_branch):
                failures.append(
                    f"{path}: branch coverage regressed from {float(baseline_branch):.2f}% to {metrics['branch']:.2f}%"
                )

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Enforce changed-runtime coverage non-regression.")
    parser.add_argument("--coverage", required=True)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", default="HEAD")
    args = parser.parse_args(argv)

    current = json.loads(Path(args.coverage).read_text(encoding="utf-8"))
    baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    changed = git_changed_files(args.base, args.head)
    failures = evaluate_coverage(current, baseline, changed)
    for failure in failures:
        print(f"FAIL: {failure}")
    if failures:
        return 1
    print("Coverage ratchet PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
