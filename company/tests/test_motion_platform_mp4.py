from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class MotionPlatformMp4Tests(unittest.TestCase):
    def test_mp4_reference_integration_contract(self) -> None:
        subprocess.run(
            [sys.executable, str(ROOT / "tools" / "motion_platform_mp4_validate.py")],
            cwd=ROOT,
            check=True,
        )


if __name__ == "__main__":
    unittest.main()
