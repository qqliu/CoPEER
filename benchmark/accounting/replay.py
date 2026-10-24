#!/usr/bin/env python3
"""Recompute saved token accounting; standard library only, no inference calls."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
from usage_rules import aggregate_output_usage, aggregate_usage, cost_components

HERE = Path(__file__).resolve().parent
COMPONENTS = ('measured_tokens', 'unknown_attempts', 'observed_lower_bound_tokens', 'charged_tokens')
ROLES = {
    'current_admitted_all': 'admitted',
    'current_admitted_evaluation': 'evaluation_population',
    'current_admitted_pilot': 'pilot_population',
    'current_primary': 'evaluation_primary',
    'current_secondary': 'evaluation_scorable',
}

def need(ok, message):
    if not ok:
        raise ValueError(message)

def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]

def add(values):
    return {key: sum(row[key] for row in values) for key in COMPONENTS}

def replay(directory=HERE):
    expected = json.loads((directory / 'expected_accounting.json').read_text())
    attempts = rows(directory / 'campaign_attempts.jsonl')
    coverage = set()
    attempt_ids = set()
    components = {}
    for row in attempts:
        need(row['attempt_id'] not in attempt_ids, 'Duplicate physical attempt')
        attempt_ids.add(row['attempt_id'])
        ids = row['coverage_ids']
        need(ids and len(ids) == len(set(ids)) and not coverage.intersection(ids), 'Overlapping physical coverage')
        coverage.update(ids)
        measured = cost_components(aggregate_usage([{'attempts': [row['usage_input']]}]))
        need(measured == row['expected_components'], 'Attempt accounting differs')
        components[row['attempt_id']] = measured
        need((measured['unknown_attempts'] == 0) == row['native_usage_complete'], 'Usage completeness differs')
    by_attempt = {row['attempt_id']: row for row in attempts}
    records_list = rows(directory / 'selected_records.jsonl')
    records = {r['selected_record_sha256']: r for r in records_list}
    need(len(records) == len(records_list), 'Duplicate selected record')
    for row in records.values():
        need(len(row['attempts']) == len(row['campaign_attempt_ids']), 'Attempt link count differs')
        if not row['attempts']:
            need(row.get('usage_origin') == 'preflight_no_inference' and row.get('usage_known') is True
                 and row.get('total_attributable_tokens') == 0, 'Unexplained zero-attempt record')
        for usage_input, linked in zip(row['attempts'], row['campaign_attempt_ids']):
            need(len(linked) == 1 and linked[0] in attempt_ids, 'Selected attempt is not uniquely bound to campaign')
            need(usage_input == by_attempt[linked[0]]['usage_input'], 'Selected and campaign usage differ')
    joins = rows(directory / 'selection_usage_join.jsonl')
    keys = [(r['view_id'], r['item_id']) for r in joins]
    need(len(keys) == len(set(keys)), 'Duplicate selected view/item')
    # Bind public selections by original record hash; numeric projections leave answers untouched.
    public_selections = rows(directory.parent / 'selections.jsonl')
    need({(r['view_id'], r['item_id'], r['selected_record_sha256']) for r in joins}
         == {(r['view_id'], r['item_id'], r['selected_record_sha256']) for r in public_selections},
         'Selected usage joins differ from released benchmark selections')
    for joined in joins:
        physical = joined['view_id'].replace('EXP5__', 'EXP1__')
        for linked in records[joined['selected_record_sha256']]['campaign_attempt_ids']:
            unit = by_attempt[linked[0]]
            need(unit['item_id'] == joined['item_id'] and unit['configuration'] == physical,
                 'Selected attempt has a different item or physical configuration')
    selected = {}
    for view in sorted({row['view_id'] for row in joins}):
        selected[view] = {}
        for subset, role in ROLES.items():
            chosen = [records[r['selected_record_sha256']] for r in joins
                      if r['view_id'] == view and r['current_roles'][role]]
            selected[view][subset] = {'usage': aggregate_usage(chosen),
                                      'output_usage': aggregate_output_usage(chosen)}
    need(selected == expected['selected_reporting_views'], 'Selected-view totals differ')
    scopes = {}
    for scope_name, target in expected['campaign_scopes'].items():
        configs = {}
        for configuration in target['configurations']:
            group = [r for r in attempts if r['configuration'] == configuration]
            initial = [components[r['attempt_id']] for r in group if r['phase'] == 'initial']
            fresh = [r for r in group if r['phase'] != 'initial']
            configs[configuration] = {
                'historical_campaign_once': add(initial),
                'fresh_all_physical_attempts_once': add([components[r['attempt_id']] for r in fresh]),
                'grand_cumulative_campaign': add([components[r['attempt_id']] for r in group]),
                'fresh_physical_attempts': len(fresh),
                'fresh_unresolved_orphans': sum(r['orphan_dispatch'] for r in fresh),
                'fresh_by_split': {s: add([components[r['attempt_id']] for r in fresh if r['split'] == s])
                                   for s in ('pilot', 'evaluation')},
                'fresh_by_cost_bucket': {b: add([components[r['attempt_id']] for r in fresh if r['cost_bucket'] == b])
                                         for b in ('CURRENT_ADMITTED_RERUN', 'WITHDRAWN_DIAGNOSTIC_RERUN')},
            }
        scopes[scope_name] = {'configurations': configs,
                             'grand_cumulative_all_configurations': add([r['grand_cumulative_campaign'] for r in configs.values()])}
    need(scopes == expected['campaign_scopes'], 'Campaign accounting differs')
    main_views = [view for view in sorted(selected) if view != 'EXP1__claude-haiku-4-5-20251001']
    table2 = {view: selected[view]['current_primary']['usage'] for view in main_views}
    aggregates = json.loads((directory.parent / 'aggregates.json').read_text())
    for view, usage in table2.items():
        need(usage == aggregates['populations'][view]['primary_ge10_lines']['inference_usage'],
             'Main-table usage differs from released aggregates')
    summary = {
        'status': 'PASS',
        'physical_attempts': len(attempts),
        'unique_selected_records': len(records),
        'selected_preflight_zero_attempt_records': sum(not r['attempts'] for r in records.values()),
        'selected_rows': len(joins),
        'reporting_views': len(selected),
        'main_table_configurations': len(table2),
        'table2_recorded_tokens': {view: row['observed_usage_lower_bound'] for view, row in table2.items()},
        'table2_incomplete_usage_attempts': {view: row['unknown_usage_attempts'] for view, row in table2.items()},
        'campaign_totals': {name: value['grand_cumulative_all_configurations'] for name, value in scopes.items()},
        'initial_orphan_dispatches': sum(r['phase'] == 'initial' and r['orphan_dispatch'] for r in attempts),
        'model_calls': 0,
    }
    return summary

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Optional replay-summary JSON destination')
    args = parser.parse_args()
    result = replay()
    encoded = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(encoded)
    print(encoded, end='')

if __name__ == '__main__':
    main()
