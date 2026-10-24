#!/usr/bin/env python3
"""Rebuild MANIFEST.json (schema copeer-submission-manifest-v1) over every file in the repository
except the .git directory and the manifest itself, so that `tools/verify_release.py --strict` passes.
Usage: python3 -B tools/update_manifest.py [--diff OLD_MANIFEST.json]
"""
import hashlib
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
manifest_path = root / 'MANIFEST.json'
old = None
if '--diff' in sys.argv:
    old = json.loads(Path(sys.argv[sys.argv.index('--diff') + 1]).read_text(encoding='utf-8'))
files = []
for p in sorted(root.rglob('*')):
    if not p.is_file() or p == manifest_path:
        continue
    rel = p.relative_to(root)
    if '.git' in rel.parts[:1] or any(part == '.git' for part in rel.parts):
        continue
    data = p.read_bytes()
    files.append({'path': rel.as_posix(), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
manifest = {
    'schema': 'copeer-submission-manifest-v1',
    'description': 'SHA-256 and byte length of every distributed file except this manifest itself.',
    'file_count': len(files),
    'total_bytes': sum(f['bytes'] for f in files),
    'verification': 'python3 -B tools/verify_release.py --strict',
    'files': files,
}
manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
print('MANIFEST.json: %d files, %d bytes' % (len(files), manifest['total_bytes']))
if old:
    o = {f['path']: f for f in old['files']}
    n = {f['path']: f for f in files}
    added = sorted(set(n) - set(o)); removed = sorted(set(o) - set(n))
    changed = sorted(k for k in set(n) & set(o) if n[k]['sha256'] != o[k]['sha256'])
    print('compared with the previous manifest: %d added, %d removed, %d changed' % (len(added), len(removed), len(changed)))
    for label, items in (('added', added), ('removed', removed), ('changed', changed)):
        tops = {}
        for k in items:
            t = k.split('/')[0] if '/' in k else k
            tops[t] = tops.get(t, 0) + 1
        print('  %s by top-level entry: %s' % (label, ', '.join('%s (%d)' % kv for kv in sorted(tops.items()))))
    for k in changed:
        print('  changed:', k)
    for k in removed:
        print('  removed:', k)
