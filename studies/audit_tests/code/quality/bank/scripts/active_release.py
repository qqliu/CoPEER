"""Persistent source-review authority for active builds and imports.

Historical releases do not acquire this policy retroactively. Reviewed current
entries are immutable to automatic QQ imports; a new review must update their
hash-bound release rows explicitly.
"""
import hashlib
import json
from pathlib import Path
import yaml

NAME = 'active_review.json'
SCHEMA = 'bugbank-active-review/v1'
CORRECTED_SCHEMA = 'bugbank-active-review/v2'

def safe_path(root, value):
    if not isinstance(value, str) or not value or Path(value).is_absolute() or '..' in Path(value).parts:
        raise ValueError('Unsafe release path: ' + str(value))
    path = (Path(root) / value).resolve()
    if not path.is_relative_to(Path(root).resolve()):
        raise ValueError('Release path escapes bank')
    return path

def ledger_path(root):
    data = json.loads((Path(root) / NAME).read_text())
    return safe_path(root, data.get('ledger', 'releases/' + data.get('release', 'human_review_20260917') + '/ledger.json'))

def release_manifest_path(root):
    data = json.loads((Path(root) / NAME).read_text())
    return safe_path(root, data.get('manifest', 'releases/' + data.get('release', 'human_review_20260917') + '/MANIFEST.json'))

def database_path(root):
    root = Path(root)
    manifest = root / NAME
    if not manifest.exists():
        return root / 'bugbank.sqlite'
    load(root)
    value = json.loads(manifest.read_text()).get('database')
    if not isinstance(value, str) or not value:
        raise ValueError('Active review must select its versioned database')
    path = Path(value)
    if path.is_absolute() or '..' in path.parts:
        raise ValueError('Unsafe active database path')
    return root / path

def normalize(value):
    return str(value).replace('Graph Theory_', 'Graph_Theory_')

def load(root):
    path = Path(root) / NAME
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    if data.get('schema') not in {SCHEMA, CORRECTED_SCHEMA} or not isinstance(data.get('records'), dict):
        raise ValueError('Invalid active review authority: ' + str(path))
    if data['schema'] == CORRECTED_SCHEMA:
        for key in ('ledger', 'manifest', 'database', 'previous_authority'):
            safe_path(root, data.get(key))
        if not data.get('source_ledger_sha256'):
            raise ValueError('Corrected authority lacks ledger digest')
    rows = data['records']
    ids = set()
    for rid, row in rows.items():
        if rid != normalize(rid) or row.get('decision') not in {'retain', 'withdraw'}:
            raise ValueError('Invalid review decision: ' + rid)
        if not row.get('entry_id') or row['entry_id'] in ids:
            raise ValueError('Duplicate or absent reviewed entry ID: ' + rid)
        ids.add(row['entry_id'])
        for key in ['entry_path', 'archive_path']:
            p = Path(row[key])
            if p.is_absolute() or '..' in p.parts:
                raise ValueError('Unsafe release path: ' + str(p))
        if data['schema'] == CORRECTED_SCHEMA and not row.get('record_sha256'):
            raise ValueError('Corrected authority lacks exact ledger record binding: ' + rid)
        if not row.get('original_entry_sha256') or not (row.get('audit_sha256') or row.get('decision_sha256')):
            raise ValueError('Unbound review row: ' + rid)
    return rows

def protected(rows, record_id=None, entry_id=None):
    return rows.get(normalize(record_id)) or next(
        (r for r in rows.values() if r['entry_id'] == entry_id or
         (r.get('source_record_id') is not None and r['source_record_id'] == normalize(record_id))), None)

def withdrawn_ids(rows):
    return {r['entry_id'] for r in rows.values() if r['decision'] == 'withdraw'}

def active_paths(root):
    root = Path(root)
    rows = load(root)
    seen = set()
    paths = []
    for p in sorted(root.glob('entries/*/*.md')):
        if p.name.startswith('_'):
            continue
        meta = yaml.safe_load(p.read_text().split('---', 2)[1])
        row = protected(rows, (meta.get('source') or {}).get('item'), meta['id'])
        if row and row['decision'] == 'withdraw':
            continue
        if row:
            if str(p.relative_to(root)) != row['entry_path'] or hashlib.sha256(p.read_bytes()).hexdigest() != row['entry_sha256']:
                raise ValueError('Reviewed entry changed without a new audit: ' + str(p))
            seen.add(row['entry_id'])
        paths.append(p)
    missing = {r['entry_id'] for r in rows.values() if r['decision'] == 'retain'} - seen
    if missing:
        raise ValueError('Retained reviewed entries missing: ' + repr(sorted(missing)))
    return paths

def prune_relations(entries, rows):
    removed = withdrawn_ids(rows)
    for entry in entries:
        entry['related'] = [rid for rid in entry.get('related') or [] if rid not in removed]
    return entries
