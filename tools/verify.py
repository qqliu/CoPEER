#!/usr/bin/env python3
"""Verify the byte lengths and SHA-256 hashes of this submission release."""

import argparse
import hashlib
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="also reject unlisted files")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest_path = root / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors = []
    listed = set()
    for entry in manifest["files"]:
        relative = Path(entry["path"])
        if relative.is_absolute() or ".." in relative.parts:
            errors.append(f"Unsafe manifest path: {relative}")
            continue
        name = relative.as_posix()
        if name in listed:
            errors.append(f"Duplicate manifest entry: {name}")
        listed.add(name)
        path = root / relative
        if any(
            (root / Path(*relative.parts[:length])).is_symlink()
            for length in range(1, len(relative.parts) + 1)
        ):
            errors.append(f"Symbolic link in file path: {name}")
            continue
        if not path.is_file():
            errors.append(f"Missing file: {name}")
            continue
        data = path.read_bytes()
        if len(data) != entry["bytes"]:
            errors.append(f"Length mismatch: {name}")
        if hashlib.sha256(data).hexdigest() != entry["sha256"]:
            errors.append(f"SHA-256 mismatch: {name}")
    if args.strict:
        actual = {
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file()
            and ".git" not in path.relative_to(root).parts
            and path != manifest_path
        }
        for name in sorted(actual - listed):
            errors.append(f"Unlisted file: {name}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Verified {len(listed)} files against MANIFEST.json.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
