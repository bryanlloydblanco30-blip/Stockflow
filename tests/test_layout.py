"""
tests/test_layout.py
Verification test for Task 0.1: Package and folder layout.
Runs under both unittest (built-in) and pytest.
"""

from pathlib import Path
import importlib
import unittest


class TestProjectLayout(unittest.TestCase):
    def test_packages_are_importable(self):
        packages = [
            "ds",
            "models",
            "services",
            "db",
            "ui",
            "ui.components",
            "ui.screens",
            "data",
            "benchmarks",
            "tests",
        ]
        for pkg in packages:
            mod = importlib.import_module(pkg)
            self.assertIsNotNone(mod, f"Failed to import package: {pkg}")

    def test_required_directories_exist(self):
        root = Path(__file__).resolve().parent.parent
        expected_dirs = [
            root / "docs" / "adt",
            root / "design" / "wireframes",
            root / "benchmarks" / "results",
            root / "scripts",
        ]
        for d in expected_dirs:
            self.assertTrue(d.is_dir(), f"Expected directory does not exist: {d}")


if __name__ == "__main__":
    unittest.main()

