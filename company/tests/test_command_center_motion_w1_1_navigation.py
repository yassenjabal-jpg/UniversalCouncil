from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def test_motion_w1_1_navigation_choreography() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "command_center_motion_w1_1_navigation_validate.py")],
        cwd=ROOT,
        check=True,
    )
