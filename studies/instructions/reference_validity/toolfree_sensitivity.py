#!/usr/bin/env python3
"""Tool-use sensitivity of the Table 1 token ratios. Offline only; reads existing usage receipts and grades.

Definition (identical to oral_route_decision_20260917/scripts/flawhunt/noexec.py and verify_flawhunt/v.py):
  a cell "used tools" iff its accepted-attempt usage record has extra_exec_count > 0, i.e. the harness counted at least one
  shell command / tool execution beyond the single print-only read of the input file.  A task is "tool-free" iff BOTH of
  its cells (search and witness review) have extra_exec_count == 0.  The archived Opus (Task 1) telemetry does not record
  this field, so no tool-free split is possible for that model; its all-100 row is repeated for reference.
Ratios and intervals use the same paired percentile bootstrap as the paper (20000 resamples, seed 20260917) over the
retained tasks.  The prior verified values (analysis_and_verification.json) are asserted: Sol tool-free full 0.977
[0.971, 0.983] on 96, Gemini 0.955 [0.937, 0.976] on 94, input-only 0.996 / 0.998.
"""
import json
import sys
sys.dont_write_bytecode = True
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

ids = C.load_ids()
rows = []
for model, dataset in C.MODELS:
    U = C.load_usage(model, ids)
    G = C.load_grades(model, dataset, ids)
    r = {'model': model, 'tool_use_recorded': model != 'opus_task1'}
    r['all100'] = C.block(model, U, G, ids)
    if model == 'opus_task1':
        r['cells_with_tool_use'] = {arm: None for arm in C.ARMS}
        r['toolfree'] = None
        r['note'] = 'runs/cost_experiment/telemetry.jsonl has no extra_exec_count; tool use cannot be determined offline'
        rows.append(r)
        continue
    r['cells_with_tool_use'] = {arm: int(sum(1 for t in ids if U[t, arm]['extra_exec'] > 0)) for arm in C.ARMS}
    r['extra_exec_total'] = {arm: int(sum(U[t, arm]['extra_exec'] for t in ids)) for arm in C.ARMS}
    r['api_calls_distribution'] = {arm: sorted(Counter(U[t, arm]['api_calls'] for t in ids).items()) for arm in C.ARMS}
    r['attempt_gt1_cells'] = {arm: int(sum(1 for t in ids if (U[t, arm]['attempt'] or 1) > 1)) for arm in C.ARMS}
    tool_tasks = [t for t in ids if any(U[t, arm]['extra_exec'] > 0 for arm in C.ARMS)]
    keep = [t for t in ids if t not in tool_tasks]
    r['tasks_with_tool_use_either_arm'] = len(tool_tasks)
    r['tool_use_tasks'] = [{'record_id': t, **{arm: {'extra_exec': U[t, arm]['extra_exec'], 'api_calls': U[t, arm]['api_calls'],
                                                      'input_only': U[t, arm]['uncached'] + U[t, arm]['cache'], 'output': U[t, arm]['output'],
                                                      'grade': G[t, arm]} for arm in C.ARMS}} for t in tool_tasks]
    r['toolfree'] = C.block(model, U, G, keep)
    r['toolfree']['record_ids_excluded'] = tool_tasks
    rows.append(r)

# assert agreement with the prior verified analysis (3 decimals as printed there)
prior = {'sol': {'n': 96, 'full': (0.977, 0.971, 0.983), 'output': (0.676, 0.604, 0.761), 'catches': (92, 90), 'input_only': 0.996},
         'gemini': {'n': 94, 'full': (0.955, 0.937, 0.976), 'output': (0.843, 0.774, 0.916), 'catches': (81, 84), 'input_only': 0.998}}
problems = []
for r in rows:
    if r['model'] not in prior:
        continue
    p, t = prior[r['model']], r['toolfree']
    checks = [('n', t['n'], p['n']), ('catches', (t['search_catches'], t['witness_review_catches']), p['catches']),
              ('full', tuple(round(x, 3) for x in [t['full_tokens_ratio']] + t['full_tokens_ratio_ci95']), p['full']),
              ('output', tuple(round(x, 3) for x in [t['output_ratio']] + t['output_ratio_ci95']), p['output']),
              ('input_only', round(t['input_only_ratio'], 3), p['input_only'])]
    for name, mine, theirs in checks:
        if mine != theirs:
            problems.append(f"{r['model']} {name}: recomputed {mine} vs prior verified {theirs}")
if problems:
    print('PRIOR-ANALYSIS CHECK FAILED; nothing written.\n' + '\n'.join(problems))
    sys.exit(2)
print('Check against prior verified flawhunt/noexec values PASSED (sol n=96, gemini n=94).')

C.OUT.mkdir(parents=True, exist_ok=True)


def sr(r, key):
    return C.fmt_ratio(r, key)


lines = [r'\begin{tabular}{lcccrrr}', r'\toprule',
         r'Model & Cells with tool use (S/R) & Tasks & Catches & Output ratio & Full-token ratio & Input-only ratio \\', r'\midrule']
for r in rows:
    a = r['all100']
    m = C.LABELS[r['model']]
    if r['tool_use_recorded']:
        cu = f"{r['cells_with_tool_use'][C.ARMS[0]]}/{r['cells_with_tool_use'][C.ARMS[1]]}"
        lines.append(f"{m}, all cells & {cu} & 100 & {a['search_catches']}/{a['witness_review_catches']} & {sr(a, 'output')} & {sr(a, 'full_tokens')} & {sr(a, 'input_only')}" + r' \\[3pt]')
        t = r['toolfree']
        lines.append(f"{m}, tool-free tasks & 0/0 & {t['n']} & {t['search_catches']}/{t['witness_review_catches']} & {sr(t, 'output')} & {sr(t, 'full_tokens')} & {sr(t, 'input_only')}" + r' \\[3pt]')
    else:
        lines.append(f"{m}, all cells & n/r & 100 & {a['search_catches']}/{a['witness_review_catches']} & {sr(a, 'output')} & {sr(a, 'full_tokens')} & {sr(a, 'input_only')}" + r' \\[3pt]')
lines += [r'\bottomrule', r'\end{tabular}']
C.write(C.OUT / 'toolfree_sensitivity_table.tex', '\n'.join(lines) + '\n')

caption = ('Tool use is defined exactly as in the prior flawhunt scripts: a cell used tools iff its accepted-attempt usage record has '
           r'\texttt{extra\_exec\_count} $>0$, that is, the harness counted at least one shell command or tool execution beyond the single '
           'print-only read of the input file; a task is tool-free iff both its search (S) and witness-review (R) cells have '
           r'\texttt{extra\_exec\_count} $=0$. The prompt forbade such executions but the prohibition was not enforceable. '
           'Intervals are paired percentile bootstraps over the retained tasks (20000 resamples, seed 20260917). '
           'The archived Opus telemetry does not record tool use (n/r), so no tool-free split exists for that model. '
           'Input-only ratio = (uncached input + cache-read input) in the search arm over the same in the review arm.')
C.write(C.OUT / 'toolfree_sensitivity_caption.tex', caption + '\n')

payload = {
    'schema': 'section4-fixes/toolfree-sensitivity/v1',
    'bootstrap': {'paired_resamples': C.B, 'seed': C.SEED},
    'tool_use_definition': __doc__,
    'caption': caption,
    'prior_verified_values_asserted': prior,
    'rows': rows,
    'inputs_sha256': dict(sorted(C.PINS.items())),
    'limitations': [
        'extra_exec_count is the harness count of executions beyond the print-only input read; it does not distinguish mathematical tool use from other commands, and it is absent for the archived Opus run.',
        'The tool-free subset is defined post hoc by an outcome of the run, so its ratios are conditional, descriptive statistics, not a pre-registered contrast.',
        'Tool-free removes tasks, not cells; a task with tool use in one arm is dropped from both arms to keep the pairing.',
        'Full tokens = output + uncached input + cache-read input on accepted attempts only; the input-only ratio is dominated by the fixed harness prefix and the identical input file.',
    ],
}
C.write(C.OUT / 'toolfree_sensitivity.json', json.dumps(payload, indent=1) + '\n')
json.dump({'inputs_sha256': C.PINS, 'outputs_sha256': C.OUTPUTS}, open(C.OUT / '.pins_toolfree_sensitivity.json', 'w'), indent=1)
for r in rows:
    a = r['all100']
    print(r['model'], 'cells with tool use S/R', r['cells_with_tool_use'], 'all100 out %.3f full %.3f inp %.3f' % (a['output_ratio'], a['full_tokens_ratio'], a['input_only_ratio']))
    if r['toolfree']:
        t = r['toolfree']
        print('   tool-free n=%d catches %d/%d out %.3f [%.3f,%.3f] full %.3f [%.3f,%.3f] inp %.3f [%.3f,%.3f]' % (
            t['n'], t['search_catches'], t['witness_review_catches'], t['output_ratio'], *t['output_ratio_ci95'],
            t['full_tokens_ratio'], *t['full_tokens_ratio_ci95'], t['input_only_ratio'], *t['input_only_ratio_ci95']))
        print('   excluded:', [(x['record_id'], x[C.ARMS[0]]['extra_exec'], x[C.ARMS[1]]['extra_exec']) for x in r['tool_use_tasks']])
