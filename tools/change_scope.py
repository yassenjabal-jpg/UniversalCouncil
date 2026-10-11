from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def normalize_paths(paths: list[str]) -> list[str]:
    normalized: set[str] = set()
    for raw in paths:
        value = raw.strip().replace("\\", "/")
        while value.startswith("./"):
            value = value[2:]
        if value:
            normalized.add(value)
    return sorted(normalized)


def filter_python_files(paths: list[str]) -> list[str]:
    return [path for path in normalize_paths(paths) if path.endswith(".py") and Path(path).is_file()]


def filter_production_files(paths: list[str]) -> list[str]:
    return [path for path in filter_python_files(paths) if path.startswith("company/runtime/")]


def git_changed_files(base: str, head: str = "HEAD") -> list[str]:
    result = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            "--diff-filter=ACMR",
            f"{base}...{head}",
            "--",
        ],
        shell=False,
        check=True,
        text=True,
        capture_output=True,
    )
    return normalize_paths(result.stdout.splitlines())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="List deterministic repository change scope.")
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--python", action="store_true")
    parser.add_argument("--production", action="store_true")
    args = parser.parse_args(argv)

    paths = git_changed_files(args.base, args.head)
    if args.production:
        paths = filter_production_files(paths)
    elif args.python:
        paths = filter_python_files(paths)

    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
