from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class MotionPlatformMp1Tests(unittest.TestCase):
    def test_mp1_semantic_kernel_contract(self) -> None:
        subprocess.run(
            [sys.executable, str(ROOT / "tools" / "motion_platform_mp1_validate.py")],
            cwd=ROOT,
            check=True,
        )


if __name__ == "__main__":
    unittest.main()
