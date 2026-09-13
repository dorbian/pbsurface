from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from verify_package import verify


class PackageTests(unittest.TestCase):
    def test_rejects_traversal_member(self) -> None:
        test_root = ROOT / "build" / "test-temp"
        test_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=test_root) as directory:
            archive_path = Path(directory) / "unsafe.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("playbook-surface-0.1.0/../bad.txt", "bad")
            with self.assertRaises(ValueError):
                verify(str(archive_path))

    def test_source_policy_excludes_private_inputs(self) -> None:
        spec = importlib.util.spec_from_file_location("package_source", ROOT / "tools" / "package_source.py")
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        relatives = {path.relative_to(ROOT).as_posix() for path in module.source_files()}
        self.assertFalse(any(path.startswith("local/") for path in relatives))
        self.assertFalse(any(path.startswith("firmware/") for path in relatives))
        self.assertNotIn("dist/anything.zip", relatives)


if __name__ == "__main__":
    unittest.main()

