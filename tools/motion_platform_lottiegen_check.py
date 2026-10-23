from __future__ import annotations

import hashlib
import sys
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


if len(sys.argv) != 3:
    raise SystemExit("usage: motion_platform_lottiegen_check.py OUTPUT_A OUTPUT_B")

first = Path(sys.argv[1])
second = Path(sys.argv[2])

first_files = sorted(first.glob("*.cs"))
second_files = sorted(second.glob("*.cs"))

if len(first_files) != 1 or len(second_files) != 1:
    raise SystemExit(
        f"expected exactly one generated C# file per run; "
        f"got {len(first_files)} and {len(second_files)}"
    )

first_text = first_files[0].read_text(encoding="utf-8-sig")
second_text = second_files[0].read_text(encoding="utf-8-sig")

for marker in ("MotionKit.Lab", "MotionKitProbe"):
    if marker not in first_text:
        raise SystemExit(f"generated Lottie C# missing marker: {marker}")

first_hash = digest(first_files[0])
second_hash = digest(second_files[0])
if first_hash != second_hash or first_text != second_text:
    raise SystemExit("LottieGen -TestMode output is not deterministic across two runs")

print(
    "MotionKit LottieGen codegen probe: PASS "
    f"(file={first_files[0].name}, sha256={first_hash})"
)
