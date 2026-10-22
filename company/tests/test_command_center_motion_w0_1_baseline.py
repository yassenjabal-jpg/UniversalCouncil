from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def test_motion_w0_1_baseline_lock() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "command_center_motion_w0_1_baseline_validate.py")],
        cwd=ROOT,
        check=True,
    )
