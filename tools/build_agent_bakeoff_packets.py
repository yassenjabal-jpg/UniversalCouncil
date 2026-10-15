from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

SENSITIVE_HEADING_TERMS = (
    "decision",
    "final",
    "verdict",
    "recommendation",
    "result",
    "outcome",
    "accepted",
    "acceptance",
    "status",
    "selected",
    "selection",
    "conclusion",
)

MASK = "[REDACTED_FROM_MODEL_PACKET]"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_label(label: str) -> set[str]:
    raw = str(label).strip()
    variants = {
        raw,
        raw.replace("_", " "),
        raw.replace("-", " "),
        raw.replace("_", "-"),
    }
    return {variant for variant in variants if variant}


def strip_sensitive_sections(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    dropping_level: int | None = None

    for line in lines:
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if heading:
            level = len(heading.group(1))
            title = heading.group(2).strip().casefold()
            if dropping_level is not None and level <= dropping_level:
                dropping_level = None
            if any(term in title for term in SENSITIVE_HEADING_TERMS):
                out.append(f"{'#' * level} {MASK}")
                dropping_level = level
                continue
        if dropping_level is not None:
            continue
        out.append(line)
    return "\n".join(out)


def redact_known_labels(text: str, case: dict[str, Any]) -> str:
    redacted = text
    labels: set[str] = set()
    labels.update(normalize_label(case["expected_decision"]))
    for field in ("expected_blockers", "required_dissent_tags"):
        for item in case[field]:
            labels.update(normalize_label(item))

    for label in sorted(labels, key=len, reverse=True):
        if len(label) < 4:
            continue
        redacted = re.sub(re.escape(label), MASK, redacted, flags=re.IGNORECASE)
    return redacted


def compact_text(text: str, max_chars: int) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if len(text) <= max_chars:
        return text
    half = max_chars // 2
    return f"{text[:half]}\n\n[...PACKET TRUNCATED...]\n\n{text[-half:]}"


def build_packet(case: dict[str, Any], *, max_chars: int) -> dict[str, Any]:
    source_path = ROOT / case["source_artifact"]
    source = source_path.read_text(encoding="utf-8", errors="replace")
    masked = redact_known_labels(strip_sensitive_sections(source), case)
    masked = compact_text(masked, max_chars)

    expected_variants = normalize_label(case["expected_decision"])
    lowered = masked.casefold()
    leaks = [variant for variant in expected_variants if len(variant) >= 4 and variant.casefold() in lowered]
    if leaks:
        raise ValueError(f"{case['case_id']}: expected decision leaked into model packet: {sorted(leaks)}")

    return {
        "case_id": case["case_id"],
        "prompt": case["prompt"],
        "source_artifact": case["source_artifact"],
        "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "packet_sha256": sha256_text(masked),
        "model_context": masked,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build answer-masked immutable packets for the YASSIN bake-off.")
    parser.add_argument("--cases", default="benchmarks/agent_runtime/cases.json")
    parser.add_argument("--out", default="benchmarks/agent_runtime/case_packets.json")
    parser.add_argument("--max-chars", type=int, default=8000)
    args = parser.parse_args()

    cases = json.loads((ROOT / args.cases).read_text(encoding="utf-8"))
    packets = [build_packet(case, max_chars=args.max_chars) for case in cases]
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(packets, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "OK", "packets": len(packets), "out": str(out.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
