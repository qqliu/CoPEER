"""Verify the distributed saved evidence without invoking Lean or a model."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
manifest = json.loads((root / 'MANIFEST.json').read_text())
listed = set()
for item in manifest['files']:
    path = (root / item['path']).resolve()
    assert path.is_relative_to(root), item['path']
    data = path.read_bytes()
    assert len(data) == item['bytes'], item['path']
    assert hashlib.sha256(data).hexdigest() == item['distributed_sha256'], item['path']
    listed.add(path)
pairs = json.loads((root / 'PAIR_INDEX.json').read_text())['pairs']
assert len(pairs) == len({pair['record_id'] for pair in pairs}) == 16
for pair in pairs:
    for path_key, hash_key in [('old_certificate', 'historical_sha256'),
                               ('current_certificate', 'current_sha256')]:
        path = root / pair[path_key]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == pair[hash_key], pair['record_id']
replay = json.loads((root / 'earlier_versions/replay/MANIFEST.json').read_text())
assert len(replay['rows']) == 12
assert sum(row['declarations_inspected'] for row in replay['rows']) == 123
assert all(row['lean_4_30_0'] == row['lean_4_34_0'] == 'PASS' for row in replay['rows'])
print(json.dumps({'status': 'PASS', 'files_checked': len(listed), 'old_current_pairs': len(pairs),
                  'saved_replay_sources': 12, 'saved_compile_outcomes': 24,
                  'saved_theorem_lemma_inspections': 123,
                  'new_Lean_or_model_executions': 0}, indent=2))
