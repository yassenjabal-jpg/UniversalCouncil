from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]


def test_post_p1_interaction_motion_law() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "command_center_post_p1_interaction_motion_validate.py")],
        cwd=ROOT,
        check=True,
    )
