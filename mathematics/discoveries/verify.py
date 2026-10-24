#!/usr/bin/env python3
"""Inspect the twelve exported deposits; optionally rerun exact saved checkers."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

BASE = Path(__file__).resolve().parent

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='check hashes and evidence bindings (default)')
    parser.add_argument('--replay', action='store_true', help='also execute all twelve exact checkers in temporary copies')
    args = parser.parse_args()
    manifest = json.loads((BASE / 'MANIFEST.json').read_text())
    for item in manifest['files']:
        path = BASE / item['path']
        assert path.is_file() and not path.is_symlink(), item['path']
        raw = path.read_bytes()
        assert sha(raw) == item['sha256'] and len(raw) == item['bytes'], item['path']
    index = json.loads((BASE / 'index.json').read_text())
    rows = index['rows']
    assert len(rows) == len({r['record_id'] for r in rows}) == len({r['entry_id'] for r in rows}) == 12
    assert index['source_database_entries'] == 673 and index['prior_retrieval_entries_not_exported_here'] == 661
    for row in rows:
        card = json.loads((BASE / row['card_json']).read_text())
        assert card['id'] == row['entry_id'] and card['status'] == 'draft'
        assert (BASE / row['card']).is_file()
        assert row['original_card_matches_release_manifest'] is True
        assert sha((BASE / row['original_card']).read_bytes()) == row['original_card_sha256']
        checker = BASE / row['checker']
        ast.parse(checker.read_text())
        assert row['recorded_checker_result'] == {'path': row['checker'], 'exit_code': 0}
        for path in row['provenance_files']:
            assert (BASE / path).is_file(), path
    sun = next(r for r in rows if r['record_id'] == 'rx_numbers_sun_qlogconvex_bundle')
    checker = BASE / sun['checker']
    assignments = {node.targets[0].id: ast.literal_eval(node.value)
                   for node in ast.parse(checker.read_text()).body
                   if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
                   and node.targets[0].id in {'PARENT_SHA256', 'CLAIM_HASHES'}}
    parent = checker.with_name('baseline.json').read_bytes()
    assert sha(parent) == assignments['PARENT_SHA256']
    claims = json.loads(parent)['results']
    assert [sha(r['claim'].encode()) for r in claims] == assignments['CLAIM_HASHES']
    results = {'status': 'PASS', 'deposits': 12, 'files_checked': len(manifest['files']),
               'mode': 'saved-evidence integrity', 'new_model_calls': 0}
    if args.replay:
        runs = []
        with tempfile.TemporaryDirectory(prefix='copeer-discoveries-') as temporary:
            work = Path(temporary) / 'discovery'
            shutil.copytree(BASE, work)
            for row in rows:
                checker = work / row['checker']
                run = subprocess.run([sys.executable, '-B', str(checker)], cwd=checker.parent,
                                     capture_output=True, text=True, timeout=600)
                runs.append({'record_id': row['record_id'], 'exit_code': run.returncode,
                             'stdout': run.stdout, 'stderr': run.stderr})
                if run.returncode:
                    print(json.dumps({'status': 'FAIL', 'runs': runs}, indent=2))
                    return 1
        results.update(mode='fresh deterministic checker replay', runs=runs)
    print(json.dumps(results, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
