from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def test_motion_platform_contract() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "motion_platform_contract_validate.py")],
        cwd=ROOT,
        check=True,
    )
