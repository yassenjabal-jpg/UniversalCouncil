from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def test_owner_visible_motion_gate() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "command_center_motion_visibility_validate.py")],
        cwd=ROOT,
        check=True,
    )
