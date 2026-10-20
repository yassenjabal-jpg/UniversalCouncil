from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CORE_TO_BENCHMARK = {
    "evidence": "Evidence & Verification",
    "redteam": "Red Team / Falsification",
    "execution": "Execution & Feasibility",
    "risk": "Risk & Assurance",
    "human": "Human & Adoption",
    "value": "Value & Economics",
}

SPECIALIST_TO_BENCHMARK = {
    "software": "Software & Systems",
    "media": "Media & Content",
    "business": "Business & Operations",
    "customer_skeptic": "Customer Skeptic",
}


def _load(root: Path, relative: str) -> dict[str, Any]:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def route_v03(root: Path, prompt: str, source: str) -> list[str]:
    """Reproduce the v0.3 deterministic routing contract without parallel agents."""
    routing = _load(root, "config/domain-routing.json")
    modes = _load(root, "config/modes.json")
    text = f"{prompt}\n{source}".casefold()

    selected_core: list[str] = []
    selected_specialists: list[str] = []

    # All historical bake-off cases are material governance decisions, so use
    # the existing COUNCIL default pattern rather than inventing a new mode.
    for role_id in modes["modes"]["COUNCIL"]["default_core"]:
        if role_id in CORE_TO_BENCHMARK and role_id not in selected_core:
            selected_core.append(role_id)

    for route in routing["routes"]:
        if any(str(signal).casefold() in text for signal in route["signals"]):
            for role_id in route.get("core_add", []):
                if role_id in CORE_TO_BENCHMARK and role_id not in selected_core:
                    selected_core.append(role_id)
            for role_id in route.get("specialists", []):
                if role_id in SPECIALIST_TO_BENCHMARK and role_id not in selected_specialists:
                    selected_specialists.append(role_id)

    # v0.3 COUNCIL requires a serious challenge and practical execution view.
    for role_id in ("evidence", "redteam", "execution"):
        if role_id not in selected_core:
            selected_core.append(role_id)

    participants = [CORE_TO_BENCHMARK[role_id] for role_id in selected_core]
    participants.extend(SPECIALIST_TO_BENCHMARK[role_id] for role_id in selected_specialists)
    return participants[:7]
