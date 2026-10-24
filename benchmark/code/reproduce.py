#!/usr/bin/env python3
"""Replay the published counterexample-location benchmark using saved answers.

Python 3.9+ standard library only. No model calls, credentials or network access.
"""
import argparse
import ast
import collections
import hashlib
import json
from pathlib import Path
import sys

import frozen_common as parser
import frozen_score as score

HERE = Path(__file__).resolve().parent
ROLES = {'primary_ge10_lines': 'evaluation_primary',
         'secondary_scorable': 'evaluation_scorable',
         'pilot_scorable': 'pilot_scorable'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def check_code():
    provenance = read_json(HERE / 'provenance.json')
    for name, binding in provenance['modules'].items():
        raw = (HERE / name).read_bytes()
        need(sha(raw) == binding['distributed_sha256'], 'Frozen module changed: ' + name)
        names, constants = set(binding['functions']), set(binding['constants'])
        nodes = []
        for node in ast.parse(raw).body:
            if isinstance(node, ast.FunctionDef) and node.name in names:
                nodes.append(node)
            elif isinstance(node, ast.Assign) and {t.id for t in node.targets if isinstance(t, ast.Name)} & constants:
                nodes.append(node)
        digest = sha(canonical([ast.dump(n, include_attributes=False) for n in nodes]))
        need(digest == binding['scientific_ast_sha256'], 'Frozen scientific function mismatch: ' + name)
    return provenance


def restore_outcome_record(selection, candidates):
    """Reconstruct only fields read by the frozen outcome rule, from public metadata."""
    status = selection['final_attempt_status']
    def row(prefix):
        result = {}
        for key in ('attempt_class', 'valid_protocol', 'transport_failure', 'stop_reason', 'finish_reason'):
            value = status.get(prefix + key)
            if value is not None:
                result[key] = value
        reason = status.get(prefix + 'hard_stop_reason')
        if reason is not None:
            result['hard_stop'] = {'reason': reason}
        reason = status.get(prefix + 'usage_stop_reason')
        if reason is not None:
            result['usage'] = {'stop_reason': reason}
        return result
    record = row('top_')
    record['candidates'] = candidates
    if status['n_attempts']:
        # Only the final attempt affects this scoring rule. Earlier native usage is separate.
        record['attempts'] = [row('final_')]
    return record


def replay(root, populations, with_intervals):
    provenance = check_code()
    settings = read_json(HERE / 'settings.json')
    need(score.RESAMPLES == settings['resamples'] == 10000, 'Bootstrap setting changed')
    views = read_json(root / 'benchmark/views.json')['views']
    need(set(views) == set(settings['seed_lane_identifiers']), 'View roster changed')
    items_list = read_jsonl(root / 'benchmark/items.jsonl')
    items = {item['record_id']: item for item in items_list}
    need(len(items) == len(items_list) == 285, 'Item roster changed')
    for rid, item in items.items():
        if item['in_current_release']:
            source = read_json(root / 'bugbank/sources' / (rid + '.json'))
            for key in ('lines', 'gold', 'group', 'split', 'current_roles', 'reference_item_sha256'):
                need(source[key] == item[key], 'Resource/benchmark mismatch: ' + rid + ' ' + key)
            item['cluster_merged'] = source['cluster_merged']
            item['cluster'] = source['cluster']
    selections = read_jsonl(root / 'benchmark/selections.jsonl')
    need(len(selections) == len(views) * len(items), 'Selected answer roster changed')
    selected = {}
    outcomes = {}
    parse_counts = collections.Counter()
    answer_cache = {}
    for selection in selections:
        ck, rid = selection['view_id'], selection['item_id']
        key = (ck, rid)
        need(key not in selected, 'Duplicate selection: ' + str(key))
        selected[key] = selection
        item = items[rid]
        need(selection['current_roles'] == item['current_roles'], 'Population mask changed: ' + str(key))
        need(selection['reference_item_sha256'] == item['reference_item_sha256'], 'Reference binding changed')
        relative = Path(selection['answer_file'])
        need(not relative.is_absolute() and '..' not in relative.parts, 'Unsafe answer path')
        if str(relative) not in answer_cache:
            answer_cache[str(relative)] = (root / ('benchmark' / relative if relative.parts and relative.parts[0] == 'answers' else relative)).read_bytes()
        raw = answer_cache[str(relative)]
        need(sha(raw) == selection['selected_answer_sha256'], 'Saved answer hash mismatch: ' + str(key))
        need(len(raw) == selection['selected_answer_bytes'], 'Saved answer byte count mismatch')
        visible = raw.decode('utf-8')
        if settings['visible_answer_rule'][ck] == 'after_last_closing_think_tag' and '</think>' in visible:
            visible = visible.split('</think>')[-1]
        need(sha(visible.encode()) == selection['visible_answer_sha256'], 'Visible answer hash mismatch: ' + str(key))
        # Gold labels are deliberately not supplied to the parser.
        audit = parser.parse_candidates_audit(visible, {'record_id': rid, 'split': item['split'], 'lines': item['lines']})
        need(sha(canonical(audit)) == selection['candidate_parse_sha256'], 'Full parser audit hash mismatch: ' + str(key))
        need(audit['candidates'] == selection['record']['candidates'], 'Saved candidates mismatch: ' + str(key))
        projection = {k: audit.get(k) for k in ('parser_version', 'candidates', 'parse_reason')}
        projection['slots'] = [{k: slot.get(k) for k in ('rank', 'normalized', 'reason', 'scored', 'exclusion_reason')}
                               for slot in audit['slot_audit']]
        need(projection == selection['candidate_parse'], 'Saved parser projection mismatch')
        parse_counts[audit['parser_version']] += 1
        record = restore_outcome_record(selection, audit['candidates'])
        result = score.outcome(item, record)
        if item['current_roles']['evaluation_scorable'] or item['current_roles']['pilot_scorable']:
            outcomes[key] = {'view_id': ck, 'item_id': rid, **{k: result[k] for k in ('hit1', 'hit3', 'valid', 'cause', 'attempt_class')}}
    expected_outcomes = {(r['view_id'], r['item_id']): r for r in read_jsonl(root / 'benchmark/outcomes_derived.jsonl')}
    need(outcomes == expected_outcomes, 'Replayed outcomes differ from distributed outcome evidence')
    saved = read_json(root / 'benchmark/aggregates.json')
    result_populations = {}
    for pop in populations:
        population_items = [items[rid] for rid in sorted(items) if items[rid]['current_roles'][ROLES[pop]]]
        n = len(population_items)
        tag = 'all_items' if pop == 'secondary_scorable' else pop
        baseline = [score.baselines(item) for item in population_items]
        baseline_results = {}
        for name in baseline[0]:
            values = [r[name] for r in baseline]
            result = {'mean': round(sum(values) / n, 4)}
            if with_intervals:
                result['ci95'] = score.boot(population_items, values, tag + name)
            expected = settings['baseline_expected'][pop][name]
            need(all(expected[k] == v for k, v in result.items()), 'Baseline differs: ' + pop + ' ' + name)
            baseline_results[name] = result
        rows = {}
        for ck in sorted(views):
            responses = [outcomes[(ck, item['record_id'])] for item in population_items]
            row = {'denominator': n, 'n_clusters': len({x['cluster_merged'] for x in population_items}),
                   'rule_misses_by_cause': dict(collections.Counter(x['cause'] for x in responses if x['cause']))}
            valid = [x for x in responses if x['valid']]
            row['per_protocol_hit1'] = {'n_valid': len(valid), 'mean': round(sum(x['hit1'] for x in valid) / len(valid), 4) if valid else None}
            for metric in ('hit1', 'hit3'):
                values = [x[metric] for x in responses]
                row[metric] = {'numerator': int(sum(values)), 'mean': round(sum(values) / n, 4)}
                if with_intervals:
                    row[metric]['ci95'] = score.boot(population_items, values, tag + settings['seed_lane_identifiers'][ck] + metric)
            expected = saved['populations'][ck][pop]
            for field in ('denominator', 'rule_misses_by_cause', 'per_protocol_hit1'):
                need(row[field] == expected[field], 'Aggregate differs: ' + ck + ' ' + pop + ' ' + field)
            for metric in ('hit1', 'hit3'):
                need(all(expected[metric][k] == v for k, v in row[metric].items()), 'Metric differs: ' + ck + ' ' + pop + ' ' + metric)
            rows[ck] = row
        result_populations[pop] = {'n_items': n, 'baselines': baseline_results, 'views': rows}
        print('Verified ' + pop + ': ' + str(n) + ' items, ' + str(len(rows)) + ' views', flush=True)
    return {'schema': 'copeer-portable-scoring-replay/v1', 'all_checks_pass': True,
            'selected_answers_reparsed': len(selections), 'unique_answer_files_verified': len(answer_cache),
            'scored_outcomes_reproduced': len(outcomes), 'parser_versions': dict(parse_counts),
            'confidence_intervals_reproduced': with_intervals, 'resamples': score.RESAMPLES if with_intervals else None,
            'manuscript_views': settings['manuscript_views'], 'archival_views': settings['archival_views'],
            'populations': result_populations,
            'verified_scope': 'Exact saved answer bytes, visible-answer transformation, complete parser audits, outcome rules, population scores, baseline means and requested bootstrap intervals.',
            'accounting_scope': 'Native token-accounting aggregates are preserved in benchmark/aggregates.json; this replay verifies answer scoring and does not reconstruct omitted per-attempt provider telemetry.',
            'frozen_scientific_source_hashes': {name: x['scientific_ast_sha256'] for name, x in provenance['modules'].items()}}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=HERE.parents[1], help='Extracted co-peer repository root')
    ap.add_argument('--output', type=Path, default=Path('benchmark-replay.json'))
    ap.add_argument('--all-populations', action='store_true', help='Also reproduce the 255-item scored evaluation and 20-item pilot')
    ap.add_argument('--counts-only', action='store_true', help='Reparse all answers and verify counts; skip bootstrap intervals')
    args = ap.parse_args()
    result = replay(args.root.resolve(), list(ROLES) if args.all_populations else ['primary_ge10_lines'], not args.counts_only)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print('PASS: ' + str(args.output))


if __name__ == '__main__':
    main()
