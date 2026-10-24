"""Shared read-only loaders for section4_fixes. Every file read is sha256-pinned in PINS.

Token conventions are those of the verified prior scripts (oral_route_decision_20260917/scripts/flawhunt/recompute.py,
verify_flawhunt/v.py) and reproduce audit.json required_witness_comparison to every digit:
  sol   (codex engine): output = output_tokens_bound_model; uncached = input_tokens - cached_input_tokens; cache = cached_input_tokens
  gemini (agy engine):  output = output_tokens_bound_model; uncached = input_tokens; cache = cache_read_tokens
  opus_task1:           runs/cost_experiment/telemetry.jsonl fields output, input_uncached, input_cache_read (per-line sums, provisional)
  full = output + uncached + cache ; input_only = uncached + cache
Tool use ('extra execution') = usage.extra_exec_count > 0, i.e. shell commands / tool executions beyond the single
print-only read of the input file, as counted by the harness and used by flawhunt/noexec.py. Not recorded for opus_task1.
No model, API or Slurm call is made anywhere in this package.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True

MAIN = Path('<workspace>')
REV = Path('<workspace-home>/claude_review_originmain_20260917')
BASE = MAIN / 'qedbench_certificate_availability_triage'
RUN = BASE / 'runs/cost_experiment_repro_20260915'
TELEMETRY = BASE / 'runs/cost_experiment/telemetry.jsonl'
AUDIT = REV / 'astra/referee_revision_audit_20260917/audit.json'
BINDING = BASE / 'reports/reference_semantic_binding_20260917/reference_semantic_binding_v5_20260917T183227Z.json'
PAPER_GEN = REV / 'iclr_submission/paper_v3/generated'
OUT = BASE / 'reports/oral_route_decision_20260917/section4_fixes'
ARMS = ['refute', 'verify_earlystop_witness']
MODELS = [('sol', 'proofs100'), ('gemini', 'proofs100'), ('opus_task1', 'proofs100_task1')]
LABELS = {'sol': 'GPT-5.6 Sol', 'gemini': 'Gemini 3.1 Pro', 'opus_task1': 'Archived Opus$^*$'}
GRADES = ['CAUGHT_MATCHING', 'CAUGHT_DIFFERENT', 'FALSE_CATCH', 'MISSED']
CAUGHT = ('CAUGHT_MATCHING', 'CAUGHT_DIFFERENT')
SEED, B = 20260917, 20000
PINS = {}
OUTPUTS = {}


def read_bytes(path):
    path = Path(path)
    data = path.read_bytes()
    PINS[str(path)] = hashlib.sha256(data).hexdigest()
    return data


def read_json(path):
    return json.loads(read_bytes(path))


def read_text(path):
    return read_bytes(path).decode()


def cell_name(rid, arm):
    return rid.replace(' ', '_') + '__' + arm + '.json'


def load_ids():
    ids = sorted(read_json(RUN / 'manifest.json')['proofs100'])
    assert len(ids) == 100 and len(set(ids)) == 100
    return ids


def load_usage(model, ids):
    out = {}
    if model == 'opus_task1':
        for line in read_text(TELEMETRY).splitlines():
            r = json.loads(line)
            if r['arm'] in ARMS:
                out[r['record_id'], r['arm']] = {'output': r['output'], 'uncached': r['input_uncached'], 'cache': r['input_cache_read'],
                                                 'api_calls': r.get('api_calls'), 'extra_exec': None, 'attempt': None}
    else:
        for rid in ids:
            for arm in ARMS:
                u = read_json(RUN / 'usage/proofs100' / model / cell_name(rid, arm))
                us = u['usage']
                assert u['record_id'] == rid and u['arm'] == arm
                if us['engine'] == 'agy':
                    t = us['usage']
                    rec = {'output': us['output_tokens_bound_model'], 'uncached': int(t['input_tokens']),
                           'cache': int(t.get('cache_read_tokens', 0)), 'api_calls': len(us.get('usage_steps') or [])}
                elif us['engine'] == 'codex':
                    t = us['usage_total']
                    rec = {'output': us['output_tokens_bound_model'], 'uncached': int(t['input_tokens']) - int(t.get('cached_input_tokens', 0)),
                           'cache': int(t.get('cached_input_tokens', 0)), 'api_calls': len(us.get('turns') or [])}
                else:
                    raise SystemExit('unexpected engine ' + str(us['engine']))
                rec['extra_exec'] = int(us.get('extra_exec_count', 0) or 0)
                rec['attempt'] = u.get('attempt')
                out[rid, arm] = rec
    for rid in ids:
        for arm in ARMS:
            assert (rid, arm) in out, (model, rid, arm)
            assert all(isinstance(out[rid, arm][k], int) and out[rid, arm][k] >= 0 for k in ['output', 'uncached', 'cache']), (model, rid, arm)
    return out


def load_grades(model, dataset, ids):
    g = {}
    for rid in ids:
        for arm in ARMS:
            d = read_json(RUN / 'grades' / dataset / model / cell_name(rid, arm))
            assert d['record_id'] == rid and d['arm'] == arm
            g[rid, arm] = d['grade']
    return g


def boot_index(n):
    return np.random.default_rng(SEED).integers(0, n, size=(B, n))


def ratio_ci(a, b, ix):
    return np.quantile(a[ix].sum(1) / b[ix].sum(1), [.025, .975]).tolist()


def block(model, U, G, ids):
    """Paired statistics on the task list `ids` for one model. Same estimator and bootstrap as the paper."""
    n = len(ids)
    ix = boot_index(n)
    a = np.array([G[r, ARMS[0]] in CAUGHT for r in ids], int)
    b = np.array([G[r, ARMS[1]] in CAUGHT for r in ids], int)
    d = a - b
    res = {'model': model, 'n': n, 'search_catches': int(a.sum()), 'witness_review_catches': int(b.sum()),
           'both': int(((a == 1) & (b == 1)).sum()), 'search_only': int((d == 1).sum()), 'review_only': int((d == -1).sum()),
           'neither': int(((a == 0) & (b == 0)).sum()),
           'paired_difference': float(d.mean()), 'paired_difference_ci95': np.quantile(d[ix].mean(1), [.025, .975]).tolist()}
    vec = {}
    for key in ['output', 'uncached', 'cache']:
        vec[key] = [np.array([U[r, arm][key] for r in ids], float) for arm in ARMS]
    vec['input_only'] = [vec['uncached'][i] + vec['cache'][i] for i in range(2)]
    vec['full_tokens'] = [vec['output'][i] + vec['input_only'][i] for i in range(2)]
    for name in ['output', 'full_tokens', 'input_only']:
        v = vec[name]
        res[name + '_ratio'] = float(v[0].sum() / v[1].sum())
        res[name + '_ratio_ci95'] = ratio_ci(v[0], v[1], ix)
    res['token_components'] = {arm: {'output': int(vec['output'][i].sum()), 'input_uncached': int(vec['uncached'][i].sum()),
                                     'input_cache_read': int(vec['cache'][i].sum()), 'full_tokens': int(vec['full_tokens'][i].sum())}
                               for i, arm in enumerate(ARMS)}
    for arm in ARMS:
        other = [G[r, arm] for r in ids if G[r, arm] not in GRADES]
        assert not other, (model, arm, other)
    res['grade_counts'] = {arm: {g: int(sum(1 for r in ids if G[r, arm] == g)) for g in GRADES} for arm in ARMS}
    return res


def fmt_ratio(r, key):
    a, b = r[key + '_ratio_ci95']
    return r'\shortstack{' + f"{r[key + '_ratio']:.3f}" + r'\\{\scriptsize [' + f'{a:.3f}, {b:.3f}' + ']}}'


def fmt_diff(r, decimals):
    lo, hi = r['paired_difference_ci95']
    f = f'+.{decimals}f'
    return (r'\shortstack{' + format(100 * r['paired_difference'], f) + r'\\{\scriptsize ['
            + format(100 * lo, f) + ', ' + format(100 * hi, f) + ']}}')


def primary_row(r, decimals, tail):
    return (f"{LABELS[r['model']]} & {r['search_catches']}/{r['witness_review_catches']} & {fmt_diff(r, decimals)} & "
            f"{fmt_ratio(r, 'output')} & {fmt_ratio(r, 'full_tokens')}" + tail)


HEADER = [r'\begin{tabular}{lccrr}', r'\toprule',
          r'Model & Catches & $\Delta$ catches (pp) & Output ratio & Full-token ratio \\', r'\midrule']


def render_primary_style(rows):
    """Byte-exact format of paper_v3/scripts/publish_witness_primary.py."""
    lines = HEADER + [primary_row(r, 0, r' \\') for r in rows]
    return '\n'.join(lines + [r'\bottomrule', r'\end{tabular}']) + '\n'


def render_sensitivity_style(rows):
    """Byte-exact format of paper_v3/scripts/analyze_reference_sensitivity.py."""
    lines = HEADER + [primary_row(r, 1, r' \\[3pt]') for r in rows]
    return '\n'.join(lines + [r'\bottomrule', r'\end{tabular}']) + '\n'


def write(path, text):
    path = Path(path)
    path.write_text(text)
    OUTPUTS[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
