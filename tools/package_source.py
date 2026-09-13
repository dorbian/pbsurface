"""Create a deterministic, manifest-bearing ZipRunner source archive."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
PACKAGE_ROOT = f"playbook-surface-{VERSION}"
OUTPUT = ROOT / "dist" / f"playbook-surface-{VERSION}-source.zip"
EXCLUDED_PARTS = {".git", ".venv", "__pycache__", "build", "dist", "local", "logs", "private", "firmware", "toolchains", "device-backups"}
EXCLUDED_SUFFIXES = {".pyc", ".bar", ".signed"}


def source_files() -> list[Path]:
    result: list[Path] = []
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if not path.is_file() or set(relative.parts) & EXCLUDED_PARTS:
            continue
        if path.suffix.lower() in EXCLUDED_SUFFIXES or path.name.startswith(".env"):
            continue
        result.append(path)
    return sorted(result, key=lambda item: item.relative_to(ROOT).as_posix())


def manifest_for(files: list[Path]) -> dict[str, object]:
    rows = []
    for path in files:
        data = path.read_bytes()
        rows.append({
            "path": path.relative_to(ROOT).as_posix(),
            "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        })
    return {"schema": "playbook-surface.source-package/v1", "project": "playbook-surface", "version": VERSION, "files": rows}


def write_member(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, data)


def main() -> int:
    files = source_files()
    manifest = manifest_for(files)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w") as archive:
        for path in files:
            relative = path.relative_to(ROOT).as_posix()
            write_member(archive, f"{PACKAGE_ROOT}/{relative}", path.read_bytes())
        encoded = json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n"
        write_member(archive, f"{PACKAGE_ROOT}/PACKAGE-MANIFEST.json", encoded)
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

