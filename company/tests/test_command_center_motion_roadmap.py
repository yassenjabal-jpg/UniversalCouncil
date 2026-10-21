from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def test_motion_remediation_master_roadmap() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "command_center_motion_roadmap_validate.py")],
        cwd=ROOT,
        check=True,
    )
