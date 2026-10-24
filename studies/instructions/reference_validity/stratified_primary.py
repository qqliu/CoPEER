#!/usr/bin/env python3
"""Table 1 recomputed on nested reference-audit tiers. Offline only; reads existing grades and usage receipts.

Tiers (record sets), all derived from audit.json crosswalk and the v5 semantic binding:
  all100        the 100 frozen proofs100 inputs
  ledger71      crosswalk current_release_status != NOT_IN_425_LEDGER (joined to an audited ledger record by exact witness)
  kept43        RETAINED and witness_action KEPT (reference confirmed as written)
  supported42   v5 automated_source_audit_supported_subset
  whole22       v5 supported_whole_source_equivalence_subset (the paper's reference_sensitivity_table.tex set)
  exact15       v5 supported_with_exact_source_text_subset
  invalidated13 blocker SEMANTIC_EXCLUDED (10, excluded as wrong) + RETAINED with witness_action REPLACED_INVALID (3)
  unresolved15  blocker SEMANTIC_UNRESOLVED
The all100 block must reproduce paper_v3/generated/witness_primary_table.tex byte for byte and the whole22 block must
reproduce reference_sensitivity_table.tex; the script aborts with exit code 2 otherwise.
"""
import json
import sys
sys.dont_write_bytecode = True
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

ids = C.load_ids()
audit = C.read_json(C.AUDIT)
binding = C.read_json(C.BINDING)
cw = {r['record_id']: r for r in audit['crosswalk']}
assert sorted(cw) == ids, 'crosswalk record ids differ from proofs100'


def blockers(r):
    return set(r.get('blockers') or [])


tiers = {}
tiers['all100'] = ids
tiers['ledger71'] = [r for r in ids if cw[r]['current_release_status'] != 'NOT_IN_425_LEDGER']
tiers['kept43'] = [r for r in ids if cw[r]['current_release_status'] == 'RETAINED' and cw[r].get('witness_action') == 'KEPT']
tiers['supported42'] = sorted(binding['automated_source_audit_supported_subset'])
tiers['whole22'] = sorted(binding['supported_whole_source_equivalence_subset'])
tiers['exact15'] = sorted(binding['supported_with_exact_source_text_subset'])
excluded10 = [r for r in ids if 'SEMANTIC_EXCLUDED' in blockers(cw[r])]
replaced3 = [r for r in ids if cw[r]['current_release_status'] == 'RETAINED' and cw[r].get('witness_action') == 'REPLACED_INVALID']
tiers['invalidated13'] = sorted(excluded10 + replaced3)
tiers['unresolved15'] = [r for r in ids if 'SEMANTIC_UNRESOLVED' in blockers(cw[r])]
never_audited = [r for r in ids if cw[r]['current_release_status'] == 'NOT_IN_425_LEDGER']

expected_n = {'all100': 100, 'ledger71': 71, 'kept43': 43, 'supported42': 42, 'whole22': 22, 'exact15': 15, 'invalidated13': 13, 'unresolved15': 15}
for k, n in expected_n.items():
    assert len(tiers[k]) == n and len(set(tiers[k])) == n and set(tiers[k]) <= set(ids), (k, len(tiers[k]))
assert len(excluded10) == 10 and len(replaced3) == 3 and len(never_audited) == 29
S = {k: set(v) for k, v in tiers.items()}
assert S['exact15'] < S['whole22'] < S['supported42'] <= S['kept43'] < S['ledger71'] < S['all100'], 'tiers are not nested'
assert S['invalidated13'].isdisjoint(S['unresolved15']) and (S['invalidated13'] | S['unresolved15'] | S['kept43']) == S['ledger71']
assert not (S['invalidated13'] | S['unresolved15']) & S['supported42']
# the 22 must be the set the paper's sensitivity table was built on
sens = C.read_json(C.BASE / 'reports/reference_sensitivity_20260917/results.json')
assert sorted(sens['record_ids']) == tiers['whole22'], 'whole22 differs from reference_sensitivity_20260917 record_ids'

TIER_TITLES = {
    'all100': 'All 100 benchmark references (published Table 1)',
    'ledger71': 'Joined to an audited ledger record by exact witness',
    'kept43': 'Retained with the reference witness kept as written',
    'supported42': 'Automated source audit supported',
    'whole22': 'Whole frozen proof matches the source (published sensitivity table)',
    'exact15': 'Exact source text match',
    'invalidated13': 'Reference invalidated by the audit (10 excluded as wrong + 3 witness replaced)',
    'unresolved15': 'Reference unresolved by the audit',
}
TIER_SHORT = {'all100': 'All', 'ledger71': 'Ledger-joined', 'kept43': 'Kept as written', 'supported42': 'Audit-supported',
              'whole22': 'Whole-source match', 'exact15': 'Exact source text', 'invalidated13': 'Invalidated', 'unresolved15': 'Unresolved'}

results = {}
for model, dataset in C.MODELS:
    U = C.load_usage(model, ids)
    G = C.load_grades(model, dataset, ids)
    for tier, tids in tiers.items():
        results.setdefault(tier, []).append(C.block(model, U, G, tids))

# ---- reproduction checks (abort on any mismatch) -----------------------------------------------------------------
failures = []
pub_primary = C.read_text(C.PAPER_GEN / 'witness_primary_table.tex')
pub_sens = C.read_text(C.PAPER_GEN / 'reference_sensitivity_table.tex')
pub_json = C.read_json(C.PAPER_GEN / 'witness_primary_results.json')
mine_primary = C.render_primary_style(results['all100'])
mine_sens = C.render_sensitivity_style(results['whole22'])
if mine_primary != pub_primary:
    failures.append('witness_primary_table.tex\n--- published\n' + pub_primary + '--- recomputed\n' + mine_primary)
if mine_sens != pub_sens:
    failures.append('reference_sensitivity_table.tex\n--- published\n' + pub_sens + '--- recomputed\n' + mine_sens)
for r, p in zip(results['all100'], pub_json['rows']):
    assert r['model'] == p['model']
    for mine, theirs in [('search_catches', 'search_catches'), ('witness_review_catches', 'witness_earlystop_catches'),
                         ('both', 'both'), ('search_only', 'search_only'), ('review_only', 'witness_earlystop_only'), ('neither', 'neither')]:
        if r[mine] != p[theirs]:
            failures.append(f"{r['model']} {mine}: {r[mine]} vs published {p[theirs]}")
    for arm in C.ARMS:
        for k in ['output', 'input_uncached', 'input_cache_read', 'full_tokens']:
            if r['token_components'][arm][k] != p['accepted_attempt_token_components'][arm][k]:
                failures.append(f"{r['model']} {arm} {k}: {r['token_components'][arm][k]} vs published {p['accepted_attempt_token_components'][arm][k]}")
        for g, n in p['grade_counts'][arm].items():
            if r['grade_counts'][arm].get(g, 0) != n:
                failures.append(f"{r['model']} {arm} grade {g}: {r['grade_counts'][arm].get(g, 0)} vs published {n}")
    for mine, theirs in [('output_ratio', 'output_ratio'), ('full_tokens_ratio', 'full_token_ratio')]:
        if abs(r[mine] - p[theirs]) > 1e-9:
            failures.append(f"{r['model']} {mine}: {r[mine]} vs published {p[theirs]}")
    if abs(r['paired_difference'] - p['paired_catch_difference']) > 1e-9:
        failures.append(f"{r['model']} paired difference {r['paired_difference']} vs {p['paired_catch_difference']}")
    for mine, theirs in [('paired_difference_ci95', 'paired_percentile_bootstrap_ci95')]:
        if any(abs(x - y) > 1e-9 for x, y in zip(r[mine], p[theirs])):
            failures.append(f"{r['model']} {mine}: {r[mine]} vs published {p[theirs]}")
    for mine, theirs in [('output_ratio_ci95', 'output'), ('full_tokens_ratio_ci95', 'full_tokens')]:
        if any(abs(x - y) > 1e-9 for x, y in zip(r[mine], p['paired_cost_percentile_bootstrap_ci95'][theirs])):
            failures.append(f"{r['model']} {mine}: {r[mine]} vs published {p['paired_cost_percentile_bootstrap_ci95'][theirs]}")
for r, p in zip(results['whole22'], sens['rows']):
    assert r['model'] == p['model']
    for k in ['search_catches', 'witness_review_catches', 'both', 'search_only', 'review_only', 'neither']:
        if r[k] != p[k]:
            failures.append(f"22 {r['model']} {k}: {r[k]} vs {p[k]}")
    for k in ['output_ratio', 'full_tokens_ratio', 'paired_difference']:
        if abs(r[k] - p[k]) > 1e-9:
            failures.append(f"22 {r['model']} {k}: {r[k]} vs {p[k]}")
    for k in ['output_ratio_ci95', 'full_tokens_ratio_ci95', 'paired_difference_ci95']:
        if any(abs(x - y) > 1e-9 for x, y in zip(r[k], p[k])):
            failures.append(f"22 {r['model']} {k}: {r[k]} vs {p[k]}")
if failures:
    print('REPRODUCTION FAILED; nothing written.\n' + '\n'.join(failures))
    sys.exit(2)
print('Reproduction check PASSED: all100 block == witness_primary_table.tex (byte-exact), whole22 block == reference_sensitivity_table.tex '
      '(byte-exact), all counts/components/ratios/intervals == witness_primary_results.json and reference_sensitivity_20260917/results.json.')

# ---- render -------------------------------------------------------------------------------------------------------
C.OUT.mkdir(parents=True, exist_ok=True)
lines = list(C.HEADER)
for i, tier in enumerate(tiers):
    if i:
        lines.append(r'\midrule')
    lines.append(r'\multicolumn{5}{l}{\textit{' + TIER_TITLES[tier] + '}, $n=' + str(len(tiers[tier])) + r'$} \\')
    lines += [C.primary_row(r, 1, r' \\[3pt]') for r in results[tier]]
lines += [r'\bottomrule', r'\end{tabular}']
C.write(C.OUT / 'stratified_primary_table.tex', '\n'.join(lines) + '\n')

glines = [r'\begin{tabular}{llrrrrrrrr}', r'\toprule',
          r'Tier ($n$) & Model & \multicolumn{4}{c}{Search} & \multicolumn{4}{c}{Witness review} \\',
          r'\cmidrule(lr){3-6}\cmidrule(lr){7-10}',
          r' & & Match. & Diff. & False & Missed & Match. & Diff. & False & Missed \\', r'\midrule']
for i, tier in enumerate(tiers):
    if i:
        glines.append(r'\midrule')
    for j, r in enumerate(results[tier]):
        first = f'{TIER_SHORT[tier]} ({len(tiers[tier])})' if j == 0 else ''
        cells = [str(r['grade_counts'][arm][g]) for arm in C.ARMS for g in C.GRADES]
        glines.append(f"{first} & {C.LABELS[r['model']]} & " + ' & '.join(cells) + r' \\')
glines += [r'\bottomrule', r'\end{tabular}']
C.write(C.OUT / 'stratified_grades_table.tex', '\n'.join(glines) + '\n')

# byte-exact reproductions, kept so the check can be re-run with diff
C.write(C.OUT / 'reproduced_witness_primary_table.tex', mine_primary)
C.write(C.OUT / 'reproduced_reference_sensitivity_table.tex', mine_sens)

inval_cm = {m: sum(results['invalidated13'][i]['grade_counts'][a]['CAUGHT_MATCHING'] for a in C.ARMS) for i, (m, _) in enumerate(C.MODELS)}
payload = {
    'schema': 'section4-fixes/stratified-primary/v1',
    'bootstrap': {'paired_resamples': C.B, 'seed': C.SEED, 'method': 'paired percentile bootstrap over tasks; same index draw '
                  'np.random.default_rng(seed).integers(0,n,(B,n)) as the paper; pointwise, post hoc'},
    'catch_rule': 'caught = grade in {CAUGHT_MATCHING, CAUGHT_DIFFERENT}',
    'token_convention': C.__doc__,
    'tier_definitions': {
        'all100': 'runs/cost_experiment_repro_20260915/manifest.json proofs100',
        'ledger71': 'audit.json crosswalk current_release_status != NOT_IN_425_LEDGER',
        'kept43': 'crosswalk current_release_status == RETAINED and witness_action == KEPT',
        'supported42': 'v5 binding automated_source_audit_supported_subset',
        'whole22': 'v5 binding supported_whole_source_equivalence_subset (== reference_sensitivity_20260917 record_ids)',
        'exact15': 'v5 binding supported_with_exact_source_text_subset',
        'invalidated13': 'crosswalk blockers contain SEMANTIC_EXCLUDED (10) or RETAINED with witness_action REPLACED_INVALID (3)',
        'unresolved15': 'crosswalk blockers contain SEMANTIC_UNRESOLVED',
        'never_audited29': 'crosswalk current_release_status == NOT_IN_425_LEDGER (not tabulated; nothing is known about these references)'},
    'tier_record_ids': {**tiers, 'excluded10': sorted(excluded10), 'replaced3': sorted(replaced3), 'never_audited29': never_audited},
    'nesting_checks': 'exact15 < whole22 < supported42 <= kept43 < ledger71 < all100; invalidated13, unresolved15, kept43 partition ledger71',
    'reproduction_check': {'witness_primary_table_tex_byte_exact': True, 'reference_sensitivity_table_tex_byte_exact': True,
                           'witness_primary_results_json_all_fields': True, 'reference_sensitivity_results_json_all_fields': True},
    'caught_matching_on_invalidated13_by_model': inval_cm,
    'caught_matching_on_invalidated13_total_cells': [sum(inval_cm.values()), 13 * 3 * 2],
    'rows': results,
    'inputs_sha256': dict(sorted(C.PINS.items())),
    'limitations': [
        'Tiers are selected subsets defined by an automated audit and semantic binding; none is a random sample, and no tier is new human approval.',
        'Only the tiers inside supported42 have references the audit found consistent with the source text; kept43 is release status, not source fidelity.',
        'Grades are the frozen September model-grader grades; nothing was regraded. A CAUGHT_MATCHING grade on an invalidated reference is agreement with a reference the audit rejected.',
        'Full tokens = output + uncached input + cache-read input on accepted solver attempts only; Opus counts are per-transcript-line sums and provisional.',
        'Intervals are pointwise paired percentile bootstraps (20000 resamples, seed 20260917), not equivalence tests; small tiers have wide intervals.',
    ],
}
C.write(C.OUT / 'stratified_primary.json', json.dumps(payload, indent=1) + '\n')
json.dump({'inputs_sha256': C.PINS, 'outputs_sha256': C.OUTPUTS}, open(C.OUT / '.pins_stratified_primary.json', 'w'), indent=1)
for tier in tiers:
    for r in results[tier]:
        print(f"{tier:14s} {r['model']:10s} n={r['n']:3d} catches {r['search_catches']}/{r['witness_review_catches']} "
              f"dpp {100*r['paired_difference']:+.1f} [{100*r['paired_difference_ci95'][0]:+.1f},{100*r['paired_difference_ci95'][1]:+.1f}] "
              f"out {r['output_ratio']:.3f} [{r['output_ratio_ci95'][0]:.3f},{r['output_ratio_ci95'][1]:.3f}] "
              f"full {r['full_tokens_ratio']:.3f} [{r['full_tokens_ratio_ci95'][0]:.3f},{r['full_tokens_ratio_ci95'][1]:.3f}] "
              f"inp {r['input_only_ratio']:.3f} CM {r['grade_counts'][C.ARMS[0]]['CAUGHT_MATCHING']}/{r['grade_counts'][C.ARMS[1]]['CAUGHT_MATCHING']}")
print('CAUGHT_MATCHING on invalidated13:', inval_cm, sum(inval_cm.values()), 'of', 78)
