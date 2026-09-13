"""Verify a PlayBook Surface source ZIP without extracting it."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import PurePosixPath


def verify(path: str) -> tuple[str, int]:
    with zipfile.ZipFile(path, "r") as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("archive contains duplicate members")
        if not names:
            raise ValueError("archive is empty")
        roots = {PurePosixPath(name).parts[0] for name in names}
        if len(roots) != 1:
            raise ValueError("archive must contain exactly one package root")
        root = next(iter(roots))
        if not root.startswith("playbook-surface-"):
            raise ValueError("unexpected package root")
        for name in names:
            parts = PurePosixPath(name).parts
            if name.startswith("/") or ".." in parts or "\\" in name:
                raise ValueError(f"unsafe archive path: {name}")
        manifest_name = f"{root}/PACKAGE-MANIFEST.json"
        if manifest_name not in names:
            raise ValueError("package manifest is missing")
        manifest = json.loads(archive.read(manifest_name))
        if manifest.get("schema") != "playbook-surface.source-package/v1":
            raise ValueError("unsupported package manifest")
        rows = manifest.get("files")
        if not isinstance(rows, list):
            raise ValueError("manifest files must be a list")
        expected_names = {manifest_name}
        for row in rows:
            relative = row["path"]
            member = f"{root}/{relative}"
            expected_names.add(member)
            data = archive.read(member)
            if len(data) != row["size"]:
                raise ValueError(f"size mismatch: {relative}")
            if hashlib.sha256(data).hexdigest() != row["sha256"]:
                raise ValueError(f"hash mismatch: {relative}")
        if expected_names != set(names):
            raise ValueError("archive and manifest member sets differ")
        return root, len(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive")
    args = parser.parse_args()
    root, count = verify(args.archive)
    print(f"verified {root}: {count} source files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

