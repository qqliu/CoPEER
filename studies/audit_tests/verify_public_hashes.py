#!/usr/bin/env python3
"""Verify public package file hashes without running the scientific checks."""
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
manifest = json.loads((ROOT / 'PUBLIC_MANIFEST.json').read_text())
failures = []
for row in manifest['files']:
    p = ROOT / row['path']
    if not p.is_file():
        failures.append({'path': row['path'], 'problem': 'missing'})
    elif hashlib.sha256(p.read_bytes()).hexdigest() != row['sha256']:
        failures.append({'path': row['path'], 'problem': 'hash mismatch'})
print(json.dumps({'checked': len(manifest['files']), 'failures': failures}, indent=2))
raise SystemExit(1 if failures else 0)
