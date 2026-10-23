from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class MotionPlatformMp2Tests(unittest.TestCase):
    def test_mp2_renderer_boundary_contract(self) -> None:
        subprocess.run(
            [sys.executable, str(ROOT / "tools" / "motion_platform_mp2_validate.py")],
            cwd=ROOT,
            check=True,
        )


if __name__ == "__main__":
    unittest.main()
