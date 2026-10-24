#!/usr/bin/env python3
"""Reconstruct the human-approved core from anonymous saved reviews."""
import argparse
import hashlib
import json
from pathlib import Path

def read(path):
    return json.loads(path.read_text())

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode()).hexdigest()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    bundle = Path(__file__).resolve().parent
    data = read(bundle/'membership.json')
    policy = read(bundle/'policy.json')
    receipt = read(bundle/'author_continuity_receipt.json')
    assert sha(bundle/'policy.json') == data['policy_sha256']
    assert sha(bundle/'author_continuity_receipt.json') == data['continuity_receipt_sha256']
    assert receipt['applicability_confirmed'] is True
    rows = {r['record_id']: r for r in data['records']}
    assert len(rows) == data['original_release_records'] == 284
    # Original line labels and benchmark roles are immutable inputs, even when
    # the retained resource index is pruned for publication.
    original_benchmark = data['original_benchmark']
    assert sha(args.release/original_benchmark['path']) == original_benchmark['sha256']
    benchmark = {r['record_id']: r for r in
                 map(json.loads, (args.release/original_benchmark['path']).read_text().splitlines())}
    assert len(benchmark) == original_benchmark['records']
    mapping_info = data['source_unit_mapping']
    assert sha(args.release/mapping_info['path']) == mapping_info['sha256']
    source_units = {r['record_id']: r['historical_inventory']['problem_sha256']
                    for r in read(args.release/mapping_info['path'])}
    assert len(source_units) == mapping_info['records'] == 284
    assert len(set(source_units.values())) == mapping_info['source_units'] == 265
    for rid, row in rows.items():
        item = benchmark[rid]
        assert {k:v for k,v in item.items() if k != 'lines'} == row['original_benchmark_metadata'], rid
        assert item['gold'] == row['current_gold'], rid
        assert item['current_roles']['evaluation_primary'] == row['original_primary191'], rid
        assert item['current_roles']['evaluation_scorable'] == row['original_scorable255'], rid
        assert source_units[rid] == row['source_unit_sha256'], rid
    votes = {rid: [] for rid in rows}
    for cohort, rel in data['review_tables'].items():
        path = args.release/rel
        assert sha(path) == data['review_table_sha256'][rel], rel
        for review in read(path)['rows']:
            rid = review.get('record_id')
            if not rid:
                rid = data['packet_record_mapping'].get(cohort, {}).get(review['packet_id'])
            if rid in rows:
                votes[rid].append((cohort, review['answers']))
    good = set()
    for rid, row in rows.items():
        positive = any(ans == ['YES']*3 for _, ans in votes[rid])
        adverse = any(ans != ['YES']*3 for _, ans in votes[rid])
        scope_blocked = any(f['status'] in policy['excluded_source_scope_statuses']
                            for f in row['current_source_scope_flags'])
        if positive and not adverse and not scope_blocked:
            good.add(rid)
        assert row['eligible'] == (rid in good), rid
    assert good == set(data['eligible_record_ids'])
    current_index = {r['record_id']: r for r in read(args.release/'bugbank/index.json')['records']}
    assert good <= set(current_index)
    for rid in sorted(good):
        x = current_index[rid]
        source = read(args.release/x['source'])
        dossier = read(args.release/x['dossier'])
        expected = rows[rid]['current_scientific_bindings']
        item = benchmark[rid]
        assert source['gold'] == rows[rid]['current_gold'] == item['gold'], rid
        assert source['lines'] == item['lines'], rid
        for key in ['current_roles', 'group', 'split', 'unscorable',
                    'exclude_from_primary', 'n_nonblank_text', 'reference_item_sha256']:
            assert source[key] == item[key], (rid, key)
        assert x['primary'] == item['current_roles']['evaluation_primary'], rid
        assert x['scorable'] == item['current_roles']['evaluation_scorable'], rid
        assert x['group'] == item['group'] and x['split'] == item['split'], rid
        assert sha(args.release/x['certificate']) == expected['certificate_sha256'], rid
        assert digest(source['lines']) == expected['source_lines_sha256'], rid
        fields = {k:dossier['fields'].get(k) for k in expected['scientific_field_names']}
        assert digest(fields) == expected['scientific_fields_sha256'], rid
        assert digest(dossier['selected_declarations']) == expected['selected_declarations_sha256'], rid
        assert not any(f.get('status') in policy['excluded_source_scope_statuses']
                       for f in dossier.get('source_correspondence_flags') or []), rid
    # Conservative conflicts depend on unchanged gold-label sets; complete original
    # source-byte identity for these older line sheets is not asserted.
    span_bad = set()
    for cohort in ['initial40','fresh40']:
        rel = 'bugbank/reviews/reference_lines/'+cohort+'.json'
        assert sha(args.release/rel) == data['line_review_table_sha256'][rel]
        for review in read(args.release/rel)['rows']:
            rid = review['record_id']
            if rid in rows and review['answers'] != ['YES','NO','NO']:
                if set(review['marked_lines']) == set(rows[rid]['current_gold']):
                    span_bad.add(rid)
    assert span_bad == set(data['benchmark_excluded_record_ids'])
    primary = {rid for rid in good if rows[rid]['original_primary191']} - span_bad
    scorable = {rid for rid in good if rows[rid]['original_scorable255']} - span_bad
    exact = {rid for rid in good if rows[rid]['continuity'] == 'EXACT_CURRENT_SCIENTIFIC_CONTENT'}
    result = dict(status='PASS', eligible_records=len(good),
                  source_units=len({rows[rid]['source_unit_sha256'] for rid in good}),
                  distinct_certificate_files=len({current_index[rid]['certificate'] for rid in good}),
                  exact_current_scientific_content=len(exact),
                  owner_confirmed_continuity_only=len(good-exact),
                  benchmark_original_primary=len(primary), benchmark_all_scorable=len(scorable),
                  excluded_current_label_sets=sorted(span_bad),
                  current_source_and_certificate_content_checked=len(good),
                  policy_and_saved_judgments_reconstructed=True,
                  original_gold_roles_and_source_unit_mapping_checked=True,
                  new_human_or_model_judgments=False)
    assert result['eligible_records'] == 147
    assert result['source_units'] == 137
    assert result['exact_current_scientific_content'] == 113
    assert result['owner_confirmed_continuity_only'] == 34
    assert result['benchmark_original_primary'] == 100
    assert result['benchmark_all_scorable'] == 131
    output = json.dumps(result, indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output)
    print(output, end='')

if __name__ == '__main__':
    main()
