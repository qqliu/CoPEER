#!/usr/bin/env python3
"""Deterministic replay of saved joint-criticism judgments and finite-panel bounds."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

VALID = {'VERIFIED_VALID_KERNEL', 'VERIFIED_VALID_EXACT', 'ANALYTIC_VALID'}
GEMINI = 'EXP4__gemini-3.1-pro'
NEMOTRON = 'EXP2__local_nemotron3_super_120b_a12b_fp8'
OSS120 = 'EXP2__local_gpt_oss_120b'
OSS20 = 'EXP2__local_gpt_oss_20b'


def load(path):
    return json.loads(path.read_text())


def jsonl(path):
    return [json.loads(row) for row in path.read_text().splitlines()]


def positive(reading):
    return reading['J1'] == 'YES' and reading['J3'] in VALID


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('EXISTING_EVIDENCE_RESULTS.json'))
    args = parser.parse_args()
    root = args.release
    bpath = root / 'studies/response_review'
    source_paths = [bpath / name for name in ['B_RESULTS_v1.json', 'B_JOINT_VIEW_v1.json', 'B_ADJUDICATION_SUMMARY_v2.json', 'B_ADJUDICATION_SCOPE_REVIEW.md', 'B_PROTOCOL_v1.md']]
    source_paths += [root / 'benchmark/items.jsonl', root / 'benchmark/selections.jsonl']
    records = load(source_paths[0])['records']
    joint_saved = load(source_paths[1])
    adjudications = {row['packet_id']: row['adjudication'] for row in load(source_paths[2])['packets']}
    items = {row['record_id']: row for row in jsonl(root / 'benchmark/items.jsonl')}
    selected = {(row['view_id'], row['item_id']): row for row in jsonl(root / 'benchmark/selections.jsonl')}
    primary = sorted(key for key, row in items.items() if row['current_roles']['evaluation_primary'])
    sampled = sorted({row['record_id'] for row in records})
    assert len(primary) == 191 and len(sampled) == 24 and len(records) == 48
    assert set(sampled) <= set(primary)

    def prediction(model, item):
        row = selected[model, item]
        if row['final_attempt_status']['final_attempt_class'] != 'VALID_ANSWER':
            return None
        slot = next((s for s in row['candidate_parse']['slots'] if s['rank'] == 1), None)
        if not slot or not slot['scored']:
            return None
        return slot['normalized']

    for row in records:
        current = selected[row['configuration'], row['record_id']]
        slot = next((s for s in current['candidate_parse']['slots'] if s['rank'] == 1), None)
        assert (slot['normalized'] if slot else None) == row['first_choice_label'], row['packet_id']
        assert current['final_attempt_status']['final_attempt_class'] == row['attempt_class'], row['packet_id']
        assert int(prediction(row['configuration'], row['record_id']) in items[row['record_id']]['gold']) == row['hit1_frozen_rule']

    modes = ['first_reader', 'both_original_readers', 'saved_adjudication', 'saved_adjudication_with_P31_source_scope']
    modes_results = {}
    label_sets = {}
    packet_rows = []
    for mode in modes:
        counts = defaultdict(Counter)
        pass_by_item = defaultdict(dict)
        accepted_labels = defaultdict(list)
        for row in records:
            reading = row['reader1']
            if mode.startswith('saved_adjudication'):
                reading = adjudications.get(row['packet_id'], reading)
            passes = positive(reading)
            if mode == 'both_original_readers':
                passes = passes and positive(row['reader2'])
            if mode == 'saved_adjudication_with_P31_source_scope' and row['packet_id'] == 'P31':
                passes = False
            protocol_ok = row['attempt_class'] == 'VALID_ANSWER'
            passes = protocol_ok and passes
            config = row['configuration']
            counts[config]['total'] += 1
            counts[config]['reference_hits'] += row['hit1_frozen_rule']
            counts[config]['reference_misses'] += 1 - row['hit1_frozen_rule']
            counts[config]['joint_pass'] += int(passes)
            counts[config]['joint_other'] += int(not passes)
            if passes:
                assert reading['J2'] == 'SPECIFIED', row['packet_id']
                if mode == 'both_original_readers':
                    assert row['reader2']['J2'] == 'SPECIFIED', row['packet_id']
                counts[config]['joint_pass_among_hits' if row['hit1_frozen_rule'] else 'joint_pass_among_misses'] += 1
                accepted_labels[row['record_id'], row['first_choice_label']].append(row['packet_id'])
            if not protocol_ok:
                reason = 'protocol_invalid'
            elif mode == 'saved_adjudication_with_P31_source_scope' and row['packet_id'] == 'P31':
                reason = 'invalid_under_recorded_source_scope'
            elif passes:
                reason = 'joint_pass'
            elif reading['J1'] == 'NO':
                reason = 'line_mismatch_or_nonapplicability'
            elif reading['J3'] == 'INVALID':
                reason = 'invalid_supplied_evidence'
            elif mode == 'both_original_readers' and not positive(row['reader2']):
                reason = 'second_reader_not_joint_positive'
            else:
                reason = 'unclear_or_unresolved'
            counts[config]['reason_' + reason] += 1
            pass_by_item[row['record_id']][config] = passes
            packet_rows.append({'mode': mode, 'packet_id': row['packet_id'], 'record_id': row['record_id'], 'configuration': config, 'first_choice_label': row['first_choice_label'], 'reference_hit': row['hit1_frozen_rule'], 'protocol_valid': protocol_ok, 'joint_pass': passes, 'reason': reason})
        paired = Counter(('both_pass' if r[GEMINI] and r[NEMOTRON] else 'Gemini_only' if r[GEMINI] else 'Nemotron_only' if r[NEMOTRON] else 'neither_pass') for r in pass_by_item.values())
        modes_results[mode] = {'counts': dict(counts), 'paired_24_inputs': dict(paired)}
        label_sets[mode] = dict(accepted_labels)

    # Reproduce the already saved stricter miss totals as a consistency check.
    for model in [GEMINI, NEMOTRON]:
        assert modes_results['both_original_readers']['counts'][model]['joint_pass_among_misses'] == joint_saved['stricter_descriptive_view'][model]['misses_J3_valid_AND_J1_YES_both_readers_AND_valid_attempt']

    def bounds(ids, model_a, model_b, accepted, assume_gold):
        rows = []
        low_total = high_total = 0
        coincident_unknown = 0
        unknown_disagreement_labels = set()
        marginal = {model_a: [0, 0], model_b: [0, 0]}
        for item in ids:
            pa, pb = prediction(model_a, item), prediction(model_b, item)

            def status(p):
                if p is None:
                    return (0, 0, 'null')
                if (item, p) in accepted:
                    return (1, 1, 'joint_review_positive')
                if assume_gold and p in items[item]['gold']:
                    return (1, 1, 'assumed_sound_reference')
                return (0, 1, 'unknown')

            za, zb = status(pa), status(pb)
            for model, value in [(model_a, za), (model_b, zb)]:
                marginal[model][0] += value[0]
                marginal[model][1] += value[1]
            if pa == pb:
                lo = hi = 0
                coincident_unknown += int(za[2] == 'unknown')
            else:
                lo, hi = za[0] - zb[1], za[1] - zb[0]
                for p, z in [(pa, za), (pb, zb)]:
                    if z[2] == 'unknown':
                        unknown_disagreement_labels.add((item, p))
            low_total += lo
            high_total += hi
            rows.append({'record_id': item, 'a_prediction': pa, 'b_prediction': pb, 'same_normalized_prediction': pa == pb, 'a_status': za[2], 'b_status': zb[2], 'lower_numerator': lo, 'upper_numerator': hi})
        # Construct and verify explicit endpoint-attaining binary assignments.
        for end in ['lower', 'upper']:
            assignments = {}
            for row in rows:
                for which in ['a', 'b']:
                    p = row[f'{which}_prediction']
                    status_ = row[f'{which}_status']
                    if p is None:
                        continue
                    key = (row['record_id'], p)
                    if status_ != 'unknown':
                        value = 1
                    elif row['same_normalized_prediction']:
                        value = 0
                    else:
                        value = int((end == 'upper' and which == 'a') or (end == 'lower' and which == 'b'))
                    if key in assignments:
                        assert assignments[key] == value
                    assignments[key] = value
            attained = sum((assignments.get((r['record_id'], r['a_prediction']), 0) if r['a_prediction'] is not None else 0) - (assignments.get((r['record_id'], r['b_prediction']), 0) if r['b_prediction'] is not None else 0) for r in rows)
            assert attained == (low_total if end == 'lower' else high_total)
        assert high_total - low_total == len(unknown_disagreement_labels)
        return {'n': len(ids), 'model_a': model_a, 'model_b': model_b, 'difference_direction': 'a_minus_b', 'assume_all_reference_labels_source_admissible': assume_gold, 'bound_numerators': [low_total, high_total], 'bound_percent_points': [100 * low_total / len(ids), 100 * high_total / len(ids)], 'same_prediction_items': sum(r['same_normalized_prediction'] for r in rows), 'same_unknown_prediction_items_cancelled': coincident_unknown, 'disagreement_items': sum(not r['same_normalized_prediction'] for r in rows), 'unknown_disagreement_line_labels': len(unknown_disagreement_labels), 'marginal_count_bounds': marginal, 'independent_marginal_difference_numerators': [marginal[model_a][0] - marginal[model_b][1], marginal[model_a][1] - marginal[model_b][0]], 'endpoint_attainment_verified': True, 'per_item': rows}

    paired_bounds = {}
    for population, ids in [('B24', sampled), ('primary191', primary)]:
        for pair_name, a, b in [('Gemini_minus_Nemotron', GEMINI, NEMOTRON), ('GPTOSS120_minus_20', OSS120, OSS20)]:
            for labels_name, labels, assume_gold in [('no_semantic_labels', {}, False), ('B_first_reader_positives', label_sets['first_reader'], False), ('B_both_readers_positives', label_sets['both_original_readers'], False), ('B_adjudication_source_scope_positives', label_sets['saved_adjudication_with_P31_source_scope'], False), ('sound_reference_assumption_only', {}, True), ('sound_reference_plus_B_scope_positives', label_sets['saved_adjudication_with_P31_source_scope'], True)]:
                paired_bounds[f'{population}/{pair_name}/{labels_name}'] = bounds(ids, a, b, labels, assume_gold)

    result = {'schema': 'copeer-existing-evidence-secondary-analysis/v1', 'status': 'recorded_secondary_analysis', 'new_model_calls': 0, 'new_human_reviews': 0, 'new_semantic_judgments': 0, 'source_sha256': {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}, 'checks': {'B_rows_joined_to_same_primary_predictions_and_attempt_classes': 48, 'B_primary_items': 24, 'saved_strict_miss_counts_reproduced': True}, 'joint_endpoint_definition': 'Protocol-valid attempt AND J1=YES AND J3 in {kernel-valid,exact-valid,analytic-valid}. All modes secondary; original primary J3 table unchanged.', 'endpoint_modes': modes_results, 'per_packet_joint_endpoint': packet_rows, 'accepted_line_labels_by_mode': {mode: [{'record_id': k[0], 'line': k[1], 'supporting_packets': v} for k, v in sorted(labels.items())] for mode, labels in label_sets.items()}, 'bound_interpretation': 'Finite-panel identification bounds, conditional on correctness of the explicitly chosen positive line judgments and (when named) sound gold. Invalid criticism never supplies a nonfalse-line label. Unknown lines share indicators across models on the same item. No sampling confidence, population extrapolation, or generated-explanation bound is claimed.', 'paired_line_label_bounds': paired_bounds}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'output': str(args.output), 'checks': result['checks'], 'endpoint_modes': modes_results, 'illustrations': {k: {a: v[a] for a in ['bound_numerators', 'bound_percent_points', 'same_prediction_items', 'disagreement_items', 'unknown_disagreement_line_labels', 'same_unknown_prediction_items_cancelled', 'independent_marginal_difference_numerators']} for k, v in paired_bounds.items() if k.endswith('B_adjudication_source_scope_positives') or k.endswith('sound_reference_assumption_only')}}, indent=2))


if __name__ == '__main__':
    main()
