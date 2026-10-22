#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "profile-manifest.json"
AUDIT = ROOT / "YASSIN_ENGINEERING_AUDIT_POLICY.json"
ENFORCE = ROOT / "YASSIN_ENGINEERING_ENFORCE_POLICY.json"

DANGEROUS = {
    "Type", "Move", "Shortcut", "MultiSelect", "MultiEdit",
    "Clipboard", "Process", "Notification", "Registry", "ScheduledTask",
    "PowerShell", "FileSystem", "Scrape", "Package", "Credentials",
}

EXPECTED = {
    "App", "Assert", "CaptureEvidence", "Click", "DisplayInventory",
    "GetText", "GuardrailStatus", "Invoke", "Kill", "Recording",
    "Screenshot", "Scroll", "Snapshot", "Wait", "WaitFor",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def comparable_policy(policy: dict) -> dict:
    copy = dict(policy)
    copy.pop("mode", None)
    return copy


def main() -> int:
    manifest = load(MANIFEST)
    audit = load(AUDIT)
    enforce = load(ENFORCE)

    surface = manifest["surface"]
    expected = set(surface["expected_tools"])
    excluded = set(surface["excluded_tools"])

    errors: list[str] = []

    if manifest["profile_id"] != "YASSIN-ENGINEERING":
        errors.append("Unexpected profile_id")

    if manifest["upstream"]["release"] != "v1.4.0":
        errors.append("Upstream release drifted from v1.4.0")

    if set(surface["toolsets"]) != {"screen", "interaction", "apps", "testing"}:
        errors.append("Toolset surface changed")

    if expected != EXPECTED:
        errors.append(f"Expected tool set drifted: {sorted(expected ^ EXPECTED)}")

    if not DANGEROUS.issubset(excluded):
        errors.append(f"Dangerous tools no longer excluded: {sorted(DANGEROUS - excluded)}")

    overlap = expected & excluded
    if overlap:
        errors.append(f"Tools are both expected and excluded: {sorted(overlap)}")

    if audit.get("mode") != "audit":
        errors.append("Audit policy is not mode=audit")
    if enforce.get("mode") != "enforce":
        errors.append("Enforce policy is not mode=enforce")

    if comparable_policy(audit) != comparable_policy(enforce):
        errors.append("AUDIT and ENFORCE policy content drifted beyond mode")

    for name, policy in (("audit", audit), ("enforce", enforce)):
        rules = policy.get("rules", [])
        if not rules:
            errors.append(f"{name} policy has no rules")
        if not any(
            rule.get("match", {}).get("toolset") == "*"
            and "run-context" in rule.get("require", [])
            for rule in rules
        ):
            errors.append(f"{name} policy lost interactive-session baseline")

    if errors:
        print("YASSIN-ENGINEERING PROFILE: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("YASSIN-ENGINEERING PROFILE: PASS")
    print(f"expected_tools={len(expected)} excluded_tools={len(excluded)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
