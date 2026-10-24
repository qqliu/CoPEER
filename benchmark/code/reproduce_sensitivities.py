#!/usr/bin/env python3
"""Reproduce label, source-mapping, and paired-score sensitivity analyses."""
import argparse
import collections
import json
from pathlib import Path

import reproduce as core
import frozen_score as score

HERE = Path(__file__).resolve().parent
DATA = HERE / 'sensitivity_data'
VERSIONS = ('v2_original_human40', 'v3_corrected', 'v4_current_final')
TRANSITIONS = ((VERSIONS[0], VERSIONS[1]), (VERSIONS[1], VERSIONS[2]), (VERSIONS[0], VERSIONS[2]))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=HERE.parents[1])
    ap.add_argument('--output', type=Path, default=Path('benchmark-sensitivity-replay.json'))
    ap.add_argument('--comparisons', action='store_true', help='Also reproduce all main-set model pairs and baseline comparisons; takes longer')
    ap.add_argument('--counts-only', action='store_true', help='Skip bootstrap calculations')
    args = ap.parse_args()
    root = args.root.resolve()
    # Revalidate the raw answers before deriving any sensitivity from their candidate lists.
    core.replay(root, ['primary_ge10_lines'], False)
    pins = core.read_json(DATA / 'PROVENANCE.json')['files']
    for name, pin in pins.items():
        raw = (DATA / name).read_bytes()
        core.need(core.sha(raw) == pin['distributed_sha256'], 'Sensitivity input drift: ' + name)
    labels = core.read_json(DATA / 'gold_versions.json')['labels']
    gold_expected = core.read_json(DATA / 'gold_expected.json')
    exclusion = core.read_json(DATA / 'exclusion_expected.json')
    comparisons = core.read_json(DATA / 'comparison_expected.json')['populations']['primary_ge10_lines']
    settings = core.read_json(HERE / 'settings.json')
    items = {r['record_id']: r for r in core.read_jsonl(root / 'benchmark/items.jsonl') if r['current_roles']['evaluation_primary']}
    for rid, item in items.items():
        item['cluster_merged'] = core.read_json(root / 'bugbank/sources' / (rid + '.json'))['cluster_merged']
        core.need(set(item['gold']) == set(labels['v4_current_final'][rid]), 'Current reference mismatch: ' + rid)
    ids = sorted(items)
    selections = {(r['view_id'], r['item_id']): r for r in core.read_jsonl(root / 'benchmark/selections.jsonl')}
    gold_results = {}
    final_outcomes = {}
    for ck in settings['seed_lane_identifiers']:
        rows = []
        final_outcomes[ck] = {}
        for rid in ids:
            selection = selections[(ck, rid)]
            record = core.restore_outcome_record(selection, selection['record']['candidates'])
            outputs = {v: score.outcome({**items[rid], 'gold': labels[v][rid]}, record) for v in VERSIONS}
            final_outcomes[ck][rid] = outputs[VERSIONS[-1]]
            rows.append({'record_id': rid, 'valid': outputs[VERSIONS[-1]]['valid'],
                         **{m: {v: outputs[v][m] for v in VERSIONS} for m in ('hit1', 'hit3')}})
        totals = {m: {v: int(sum(r[m][v] for r in rows)) for v in VERSIONS} for m in ('hit1', 'hit3')}
        valid = sum(r['valid'] for r in rows)
        result = {'n_items': len(ids), 'totals': totals,
                  'rates': {m: {v: round(totals[m][v] / len(ids), 4) for v in VERSIONS} for m in totals},
                  'protocol_valid_n': valid,
                  'valid_only_hit1': {v: round(totals['hit1'][v] / valid, 4) if valid else None for v in VERSIONS},
                  'transitions': {}}
        for a, b in TRANSITIONS:
            result['transitions'][a + '->' + b] = {}
            for metric in ('hit1', 'hit3'):
                gain = [r['record_id'] for r in rows if r[metric][a] == 0 and r[metric][b] == 1]
                loss = [r['record_id'] for r in rows if r[metric][a] == 1 and r[metric][b] == 0]
                result['transitions'][a + '->' + b][metric] = {'miss_to_hit': len(gain), 'hit_to_miss': len(loss),
                    'net': len(gain) - len(loss), 'miss_to_hit_ids': gain, 'hit_to_miss_ids': loss}
        for field, value in result.items():
            core.need(value == gold_expected['views'][ck][field], 'Gold sensitivity differs: ' + ck + ' ' + field)
        gold_results[ck] = result
    changes = {a + '->' + b: {'record_ids': [rid for rid in ids if set(labels[a][rid]) != set(labels[b][rid])]}
               for a, b in TRANSITIONS}
    for value in changes.values():
        value['n'] = len(value['record_ids'])
    core.need(changes == gold_expected['primary_gold_changes_on_fixed_191'], 'Changed-label roster mismatch')
    print('Verified three reference versions and paired gain/loss counts for all 14 views', flush=True)

    excluded = set(exclusion['excluded_record_ids'])
    kept = [rid for rid in ids if rid not in excluded]
    small_items = [items[rid] for rid in kept]
    core.need(len(kept) == 190 and len({r['cluster_merged'] for r in small_items}) == 172, 'Exclusion roster changed')
    small = {}
    for ck in settings['seed_lane_identifiers']:
        outcomes = final_outcomes[ck]
        valid = sum(outcomes[rid]['valid'] for rid in kept)
        result = {'denominator': len(kept), 'valid_n': valid,
                  'valid_only_hit1': round(sum(outcomes[rid]['hit1'] for rid in kept) / valid, 4) if valid else None}
        tag = 'primary_ge10_lines_excl_conditional_reference_v1' + settings['seed_lane_identifiers'][ck]
        for metric in ('hit1', 'hit3'):
            values = [outcomes[rid][metric] for rid in kept]
            result[metric + '_numerator'] = int(sum(values))
            result[metric + '_mean'] = round(sum(values) / len(kept), 4)
            if not args.counts_only:
                result[metric + '_ci95'] = score.boot(small_items, values, tag + metric)
        for field, value in result.items():
            core.need(value == exclusion['views'][ck]['sensitivity_190'][field], '190-item result differs: ' + ck + ' ' + field)
        for rid in excluded:
            wanted = exclusion['excluded_record_outcomes_by_view_inspected_after_mask_freeze'][ck][rid]
            core.need(all(outcomes[rid][k] == v for k, v in wanted.items()), 'Excluded-item outcome differs')
        small[ck] = result
    print('Verified the 190-item source-mapping sensitivity', flush=True)

    comparison_results = {}
    if args.comparisons:
        item_list = [items[rid] for rid in ids]
        base = [score.baselines(item) for item in item_list]
        critics = {}
        for ck in sorted(final_outcomes):
            outs = [final_outcomes[ck][rid] for rid in ids]
            tag = 'primary_ge10_lines' + settings['seed_lane_identifiers'][ck]
            if args.counts_only:
                result = {'chance_corrected_hit1': {'mean': round(sum(o['hit1'] - b['random_line'] for o, b in zip(outs, base)) / len(ids), 4)},
                          'minus_baseline': {name: {'mean': round(sum(o['hit1'] - b[name] for o, b in zip(outs, base)) / len(ids), 4)} for name in base[0]}}
                for field in result:
                    if field == 'minus_baseline':
                        for name in result[field]:
                            core.need(result[field][name]['mean'] == comparisons['critics'][ck][field][name]['mean'], 'Baseline comparison mean differs')
                    else:
                        core.need(result[field]['mean'] == comparisons['critics'][ck][field]['mean'], 'Chance correction differs')
            else:
                summary = score.summarise(item_list, outs, base, tag)
                result = {k: summary[k] for k in comparisons['critics'][ck]}
                core.need(result == comparisons['critics'][ck], 'Baseline/group comparison differs: ' + ck)
            critics[ck] = result
            print('Verified baseline comparisons: ' + ck, flush=True)
        comparison_results['critics'] = critics
        for metric in ('hit1', 'hit3'):
            field = 'paired_' + metric + '_differences'
            comparison_results[field] = {}
            for pair, expected in comparisons[field].items():
                left, right = pair.split(' minus ')
                values = [final_outcomes[left][rid][metric] - final_outcomes[right][rid][metric] for rid in ids]
                result = {'mean': round(sum(values) / len(ids), 4)}
                if not args.counts_only:
                    tag = 'primary_ge10_lines' + settings['seed_lane_identifiers'][left] + settings['seed_lane_identifiers'][right] + ('' if metric == 'hit1' else metric)
                    result['ci95'] = score.boot(item_list, values, tag)
                core.need(all(expected[k] == v for k, v in result.items()), 'Paired comparison differs: ' + pair)
                comparison_results[field][pair] = result
            print('Verified ' + str(len(comparison_results[field])) + ' paired ' + metric + ' comparisons', flush=True)
    result = {'schema': 'copeer-sensitivity-replay/v1', 'all_checks_pass': True,
              'confidence_intervals_reproduced': not args.counts_only, 'gold_versions': gold_results,
              'primary_label_changes': changes, 'source_mapping_exclusion_190': small,
              'primary_comparisons': comparison_results}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print('PASS: ' + str(args.output))


if __name__ == '__main__':
    main()
