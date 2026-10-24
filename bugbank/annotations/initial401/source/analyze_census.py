#!/usr/bin/env python3
"""Validate evidence-backed coding of a frozen census and regenerate its results.

No model calls, label inference, or modification of the historical experiment.
Run from any working directory. All substantive labels are retained in the
per-record annotations; this program only checks and aggregates them.
"""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import statistics

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
SOURCE_FIELDS = ('problem', 'claim_quote', 'flaw', 'witness', 'explanation')
ENUMS = {
    'object_kind': {'graph', 'finite_combinatorial', 'numeric_algebraic',
                    'function_sequence', 'set_topology', 'probability',
                    'algorithm_trace', 'other'},
    'mechanism': {'definition_scope', 'quantifier_scope', 'omitted_case',
                  'algebra_order', 'counting', 'structural_inference',
                  'analytic_inference', 'algorithm_invariant', 'other'},
    'family_kind': {'unbounded_discrete', 'continuous_parameter', 'both', 'none'},
    'minimality_scope': {'not_documented', 'search_order_or_bounded', 'global_argument'},
    'refutation_role': {'intermediate_step', 'target_statement', 'unclear'},
}
FLAGS = {
    'family_documented': 'family_evidence',
    'repair_documented': 'repair_evidence',
    'nondegenerate_alternative_documented': 'nondegenerate_evidence',
    'exhaustive_domain_documented': 'exhaustive_evidence',
}
EXTRA = {'record', 'mechanism_evidence', 'minimality_evidence', 'role_evidence',
         'notes', 'uncertain_fields'}
REQUIRED = set(ENUMS) | set(FLAGS) | set(FLAGS.values()) | EXTRA
REVIEW_SELECTION_RULE = ('Within each shard, take the 3 smallest '
                         'SHA256(UTF-8(record_id + review-v1)); no separators.')


def read(path):
    return json.loads(Path(path).read_text())


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(test, message):
    if not test:
        raise ValueError(message)


def load_inputs(base=BASE, root=ROOT):
    population = read(base / 'inputs/population.json')
    require(digest(root / population['manifest_path']) == population['manifest_sha256'],
            'Frozen release manifest has changed')
    release = read(root / population['manifest_path'])
    kept = release['kept_stems']
    require(len(set(kept)) == len(kept), 'Duplicate KEPT release record')
    release_rows = release['records']
    require(len({r['record'] for r in release_rows}) == len(release_rows),
            'Duplicate release manifest record')
    require({r['record'] for r in release_rows if r['release_status'] == 'KEPT'} == set(kept),
            'Release KEPT list differs from release record statuses')
    require(release['counts']['kept'] == len(kept), 'Release KEPT count differs')
    expected = {r['record']: r for r in population['records']}
    require(len(expected) == len(population['records']), 'Duplicate population record')
    require(len(expected) == population['record_count'], 'Population record count differs')
    # The frozen input JSONs retain spaces in ten legacy Graph Theory IDs.
    canonical = [rid.replace('Graph Theory', 'Graph_Theory') for rid in expected]
    require(len(set(canonical)) == len(canonical), 'Duplicate canonical population record')
    require(set(canonical) == set(kept), 'Population differs from exact KEPT release')
    inputs = {}
    for path in sorted((base / 'inputs').glob('shard_*.json')):
        for row in read(path):
            rid = row['record_id']
            require(rid in expected and rid not in inputs, f'Unexpected/duplicate input: {rid}')
            original = root / expected[rid]['input_path']
            require(digest(original) == expected[rid]['input_sha256'], f'Changed input: {rid}')
            raw = read(original)
            require(all(row.get(k) == raw.get(k) for k in raw), f'Shard differs from input: {rid}')
            inputs[rid] = row
    require(set(inputs) == set(expected), 'Input census incomplete')
    return population, inputs


def validate_row(row, source):
    rid = source['record_id']
    require(set(row) == REQUIRED, f'{rid}: schema fields differ: {set(row) ^ REQUIRED}')
    require(row['record'] == rid, f'{rid}: record mismatch')
    for key, allowed in ENUMS.items():
        require(row[key] in allowed, f'{rid}: invalid {key}: {row[key]}')
    for key, evidence in FLAGS.items():
        require(type(row[key]) is bool, f'{rid}: {key} must be boolean')
        require(bool(row[evidence]) == row[key], f'{rid}: {key}/evidence inconsistent')
    require((row['family_kind'] != 'none') == row['family_documented'], f'{rid}: family kind inconsistent')
    require(bool(row['minimality_evidence']) == (row['minimality_scope'] != 'not_documented'),
            f'{rid}: minimality evidence inconsistent')
    require(bool(row['role_evidence']) == (row['refutation_role'] != 'unclear'),
            f'{rid}: role evidence inconsistent')
    require(bool(row['mechanism_evidence']), f'{rid}: missing mechanism evidence')
    bindings = {}
    for key in list(FLAGS.values()) + ['mechanism_evidence', 'minimality_evidence', 'role_evidence']:
        excerpt = row[key]
        require(isinstance(excerpt, str), f'{rid}: {key} is not text')
        if excerpt:
            require(bool(excerpt.strip()), f'{rid}: {key} contains only whitespace')
            matches = [f for f in SOURCE_FIELDS if excerpt in source[f]]
            require(bool(matches), f'{rid}: {key} is not a verbatim source substring')
            bindings[key] = [{'field': f, 'start': source[f].index(excerpt),
                              'end': source[f].index(excerpt) + len(excerpt)} for f in matches]
    require(isinstance(row['notes'], str), f'{rid}: notes must be text')
    require(isinstance(row['uncertain_fields'], list) and
            all(k in REQUIRED for k in row['uncertain_fields']), f'{rid}: invalid uncertainty field')
    return bindings


def load_annotations(inputs, base=BASE):
    rows = {}
    files = sorted((base / 'annotations').glob('shard_*.json'))
    require(len(files) == 8, f'Expected 8 annotation shards, found {len(files)}')
    for path in files:
        assigned = {r['record_id'] for r in read(base / 'inputs' / path.name)}
        values = read(path)
        require({r['record'] for r in values} == assigned and len(values) == len(assigned),
                f'{path.name}: incomplete or duplicate coverage')
        for row in values:
            rid = row['record']
            require(rid not in rows, f'Duplicate annotation: {rid}')
            validate_row(row, inputs[rid])
            rows[rid] = row
    require(set(rows) == set(inputs), 'Annotation census incomplete')
    return rows


def load_review(inputs, population, base=BASE):
    """Bind recoding to the frozen, deterministically selected review sample."""
    manifest_path = base / 'review/sample_manifest.json'
    review_path = base / 'review/independent_sample.json'
    require(manifest_path.exists() and review_path.exists(), 'Frozen review sample missing')
    manifest = read(manifest_path)
    require(manifest['selection_rule'] == REVIEW_SELECTION_RULE, 'Review selection rule differs')
    require(manifest['codebook_sha256'] == digest(base / 'CODEBOOK.md'),
            'Review codebook hash differs')
    require(manifest['independent_sample_sha256'] == digest(review_path),
            'Frozen independent review file has changed')
    require(manifest['finalized_before_primary_annotations_viewed'] is True,
            'Review independence declaration missing')
    population_rows = {r['record']: r for r in population['records']}
    selected = {}
    selection_hash = lambda rid: hashlib.sha256((rid + 'review-v1').encode('utf-8')).hexdigest()
    for path in sorted((base / 'inputs').glob('shard_*.json')):
        shard = read(path)
        chosen = sorted(shard, key=lambda r: selection_hash(r['record_id']))[:3]
        for source in chosen:
            rid = source['record_id']
            require(rid not in selected and rid in inputs, 'Invalid review input assignment')
            selected[rid] = {'shard': path.name, 'record': rid,
                             'selection_sha256': selection_hash(rid),
                             'input_sha256': population_rows[rid]['input_sha256']}
    retained = manifest['records']
    require(len({r['record'] for r in retained}) == len(retained), 'Duplicate sample manifest row')
    require({r['record']: r for r in retained} == selected,
            'Review sample differs from frozen deterministic selection')
    review = read(review_path)
    require(len({r['record'] for r in review}) == len(review), 'Duplicate review row')
    require({r['record'] for r in review} == set(selected), 'Independent review sample incomplete')
    for row in review:
        validate_row(row, inputs[row['record']])
    return review


def agreement(primary, review):
    require(bool(review), 'Cannot compute agreement on an empty sample')
    require(len({r['record'] for r in review}) == len(review), 'Duplicate agreement record')
    require(all(r['record'] in primary for r in review), 'Unknown agreement record')
    output = {}
    for key in list(FLAGS) + list(ENUMS):
        pairs = [(primary[r['record']][key], r[key]) for r in review]
        n = len(pairs)
        observed = sum(a == b for a, b in pairs) / n
        a, b = Counter(x for x, y in pairs), Counter(y for x, y in pairs)
        expected = sum(a[k] * b[k] for k in set(a) | set(b)) / n**2
        output[key] = {'n': n, 'agreements': sum(x == y for x, y in pairs),
                       'agreement': observed,
                       'cohen_kappa': (observed - expected) / (1 - expected) if expected < 1 else None,
                       'disagreements': [r['record'] for r in review
                                         if primary[r['record']][key] != r[key]]}
    return output


def summarize(rows, inputs):
    rows = list(rows)
    n = len(rows)
    out = {'n': n,
           'flags': {k: {'yes': sum(r[k] for r in rows), 'denominator': n,
                          'fraction': sum(r[k] for r in rows) / n} for k in FLAGS},
           'categorical': {k: dict(sorted(Counter(r[k] for r in rows).items())) for k in ENUMS},
           'family_and_repair': sum(r['family_documented'] and r['repair_documented'] for r in rows),
           'family_or_repair': sum(r['family_documented'] or r['repair_documented'] for r in rows),
           'any_uncertainty': sum(bool(r['uncertain_fields']) for r in rows),
           'uncertain_fields': dict(Counter(k for r in rows for k in r['uncertain_fields']))}
    out['by_corpus'] = {}
    for corpus in sorted({inputs[r['record']]['corpus'] for r in rows}):
        subset = [r for r in rows if inputs[r['record']]['corpus'] == corpus]
        out['by_corpus'][corpus] = {'n': len(subset),
                                  **{k: sum(r[k] for r in subset) for k in FLAGS}}
    out['document_lengths'] = {}
    for field in ['claim_quote', 'witness', 'explanation']:
        lengths = sorted(len(inputs[r['record']][field]) for r in rows)
        out['document_lengths'][field] = {'unit': 'Unicode characters',
                                          'median': statistics.median(lengths),
                                          'minimum': min(lengths), 'maximum': max(lengths)}
    out['documentation_length_by_flag'] = {
        'measure': 'len(witness) + len(explanation)',
        'unit': 'Unicode characters',
        'interpretation': 'Descriptive conditioning on the stored documentation label; no significance test or causal inference.',
        'flags': {},
    }
    for key in ('family_documented', 'repair_documented', 'nondegenerate_alternative_documented'):
        groups = {}
        for value, label in ((True, 'documented'), (False, 'not_documented')):
            lengths = [len(inputs[r['record']]['witness']) + len(inputs[r['record']]['explanation'])
                       for r in rows if r[key] is value]
            groups[label] = {'n': len(lengths), 'median': statistics.median(lengths) if lengths else None}
        out['documentation_length_by_flag']['flags'][key] = groups
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    population, inputs = load_inputs()
    primary = load_annotations(inputs)
    rows = {k: dict(v) for k, v in primary.items()}
    corrections_path = BASE / 'review/corrections.json'
    corrections = read(corrections_path) if corrections_path.exists() else []
    changed = set()
    for correction in corrections:
        rid = correction['record']
        require(rid in rows, f'Unknown correction: {rid}')
        require(bool(correction['reason']), f'Unexplained correction: {rid}')
        require('record' not in correction['changes'], 'Cannot rename a corrected record')
        rows[rid].update(correction['changes'])
        validate_row(rows[rid], inputs[rid])
        changed.add(rid)
    bindings = {rid: validate_row(row, inputs[rid]) for rid, row in rows.items()}
    review = load_review(inputs, population)
    result = {
        'population': population['population'],
        'interpretation': 'Descriptive documentation census of a selected release; no claim of independent mathematical validation, error prevalence, or treatment effect.',
        'annotation_method': 'Assistant semantic reading, source-bound excerpts, independent same-model sample review; corrections retained separately.',
        'counts': summarize(rows.values(), inputs),
        'primary_counts': summarize(primary.values(), inputs),
        'review': {'sample_n': len(review), 'agreement_before_corrections': agreement(primary, review) if review else {},
                   'corrected_records': len(changed), 'correction_entries': len(corrections)},
        'provenance': {str(p.relative_to(ROOT)): digest(p)
                       for p in sorted([BASE / 'CODEBOOK.md', BASE / 'inputs/population.json',
                                        Path(__file__), BASE / 'adjudicate_reviews.py',
                                        BASE / 'review/ADJUDICATION_POLICY.md'] + list((BASE / 'inputs').glob('shard_*.json')) +
                                       list((BASE / 'annotations').glob('shard_*.json')) +
                                       list((BASE / 'review').glob('*.json')))},
    }
    if not args.validate_only:
        (BASE / 'results/census.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
        (BASE / 'results/annotated_records.json').write_text(json.dumps(
            [{'corpus': inputs[rid]['corpus'], **rows[rid], 'evidence_bindings': bindings[rid]}
             for rid in sorted(rows)], indent=2, ensure_ascii=False) + '\n')
        with (BASE / 'results/annotated_records.csv').open('w', newline='') as stream:
            fields = ['record', 'corpus'] + list(ENUMS) + list(FLAGS) + ['uncertain_fields']
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for rid in sorted(rows):
                writer.writerow({k: (inputs[rid]['corpus'] if k == 'corpus' else
                                     '|'.join(rows[rid][k]) if k == 'uncertain_fields' else rows[rid][k])
                                 for k in fields})
    print(json.dumps({'validated_records': len(rows), 'review_records': len(review),
                      'corrected_records': len(changed), 'counts': result['counts']}, indent=2))


if __name__ == '__main__':
    main()
