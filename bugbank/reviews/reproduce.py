#!/usr/bin/env python3
"""Reproduce reported review counts and exact random-audit intervals.

Python 3 standard library only. No model or network call; no regrading.
The exact interval routine preserves the integer-tail calculation used in
the study analyzer. This script consumes only anonymous categorical exports.
"""
import argparse
from collections import Counter
from fractions import Fraction
import json
import hashlib
from pathlib import Path
import random
import sys

sys.dont_write_bytecode = True
from random100.exact_interval import hypergeom_interval

HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads((HERE / path).read_text())


def exact(value):
    value = Fraction(value)
    return {'numerator': value.numerator, 'denominator': value.denominator,
            'decimal': float(value)}


def counts(rows):
    return {'n': len(rows),
            'all_yes': sum(r['answers'] == ['YES'] * 3 for r in rows),
            'any_no': sum('NO' in r['answers'] for r in rows),
            'question_counts': {f'Q{i+1}':dict(sorted(Counter(r['answers'][i] for r in rows).items()))
                                for i in range(3)}}


def source_given_math_and_lean(rows):
    selected = [r for r in rows if r['answers'][1:] == ['YES', 'YES']]
    return {'n':len(selected), 'source_answers':dict(sorted(Counter(r['answers'][0] for r in selected).items()))}


def reproduce():
    output = {}
    for cohort in ('original100','selected33','scoped_supplements','earlier_selected30','selected30','random100'):
        rows = read(cohort + '/answers.json')['rows']
        output[cohort] = counts(rows)
        if cohort == 'original100':
            output[cohort]['source_given_math_and_lean'] = source_given_math_and_lean(rows)
            unambiguous = [r for r in rows if not r['comment_attribution_ambiguous']]
            output[cohort]['unambiguous_comment_rows'] = counts(unambiguous)
            output[cohort]['unambiguous_source_given_math_and_lean'] = source_given_math_and_lean(unambiguous)
        if cohort == 'selected30':
            output[cohort]['strata'] = {s:counts([r for r in rows if r['stratum'] == s])
                                        for s in sorted({r['stratum'] for r in rows})}

    design = read('random100/design.json')
    rows = read('random100/answers.json')['rows']
    rng = random.Random(int(design['seed_integer_hex'],16))
    totalN = sum(s['N'] for s in design['strata'].values())
    lower_failure = upper_failure = 0
    point = Fraction(0)
    output['random100']['strata'] = {}
    drawn = []
    for name in design['draw_order']:
        stratum = design['strata'][name]
        N,n = stratum['N'],stratum['n']
        if len(set(stratum['ids'])) != N:
            raise ValueError('Invalid sampling frame')
        drawn.extend(rng.sample(sorted(stratum['ids']),N)[:n])
        selected = [r for r in rows if r['stratum'] == name]
        if len(selected) != n:
            raise ValueError('Wrong stratum size')
        summary = counts(selected)
        failures = n - summary['all_yes']
        bounds = list(hypergeom_interval(N,n,failures,Fraction(39,40)))
        lower_failure += bounds[0]
        upper_failure += bounds[1]
        point += Fraction(N,totalN) * Fraction(summary['all_yes'],n)
        summary['N'] = N
        summary['population_non_all_yes_97_5_component'] = bounds
        summary['population_non_all_yes_95_companion'] = list(hypergeom_interval(N,n,failures,Fraction(19,20)))
        output['random100']['strata'][name] = summary
    if drawn != [r['record_id'] for r in rows]:
        raise ValueError('Saved sample differs from deterministic draw')
    output['random100']['draw_reproduced'] = True
    output['random100']['optional_reference_line_check'] = dict(sorted(Counter(r['optional_reference_line_check'] for r in rows).items()))
    output['random100']['design_weighted_all_yes'] = exact(point)
    output['random100']['joint_95_all_yes_fraction'] = {
        'lower':exact(Fraction(totalN-upper_failure,totalN)),
        'upper':exact(Fraction(totalN-lower_failure,totalN))}

    line_records = {}
    for cohort in ('initial40','fresh40'):
        line_records[cohort] = read('reference_lines/' + cohort + '.json')['rows']
        clean = sum(r['answers'] == ['YES','NO','NO'] for r in line_records[cohort])
        output[cohort] = {'n':len(line_records[cohort]), 'clean_line_sets':clean,
                          'acceptance_threshold':38,'meets_threshold':clean>=38}
    if set(r['record_id'] for r in line_records['initial40']) & set(r['record_id'] for r in line_records['fresh40']):
        raise ValueError('Line-review rounds are not disjoint')
    output['line_review_rounds_disjoint'] = True

    rows = read('sonnet_misses/answers.json')['rows']
    design = read('sonnet_misses/design.json')
    if random.Random(design['seed']).sample(sorted(design['eligible_frame_ids']),30) != design['sample_order']:
        raise ValueError('Sonnet sample differs from deterministic draw')
    if design['sample_order'] != [r['record_id'] for r in rows]:
        raise ValueError('Sonnet sampled order differs from judgments')
    output['sonnet_misses'] = {
        'n':len(rows), 'final_class_counts':dict(sorted(Counter(r['final_class'] for r in rows).items())),
        'class_A_primary_llm_soundness':dict(sorted(Counter(r['primary_llm_counterexample_soundness'] for r in rows if r['final_class']=='A').items())),
        'review_method':'LLM_ONLY','draw_reproduced':True}
    output['scientific_packet_counts'] = {}
    for cohort in ('random100','selected30','sonnet_misses'):
        packets = read(cohort + '/packet_index.json')['packets']
        for packet in packets:
            path = HERE / cohort / packet['packet_file']
            if hashlib.sha256(path.read_bytes()).hexdigest() != packet['distributed_packet_sha256']:
                raise ValueError('Scientific packet hash mismatch: ' + packet['packet_id'])
        output['scientific_packet_counts'][cohort] = len(packets)
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true',help='Compare with the included expected results')
    parser.add_argument('--output',type=Path,help='Write JSON to this optional path')
    args = parser.parse_args()
    result = reproduce()
    if args.check:
        if result != read('expected_results.json'):
            raise SystemExit('FAIL: results differ from expected_results.json')
        print('PASS: counts, two random draws, exact intervals, disjoint line-review rounds, and 160 packet hashes reproduced.')
    elif args.output:
        args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        print(json.dumps(result,indent=2,sort_keys=True))
