from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]


def test_stage7_real_host_evidence_is_fail_closed() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "command_center_stage7_real_evidence_validate.py")],
        cwd=ROOT,
        check=True,
    )
