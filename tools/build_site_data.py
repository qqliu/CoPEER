#!/usr/bin/env python3
"""Build the explorer and benchmark data for the website from the released evidence.

Outputs (all under docs/data/):
  dossiers_index.js/.json   one row per released dossier (284): identity, group, populations, current review layer,
                            reference lines, certificate binding, claim quote
  views.js/.json            the 14 reporting views (13 configurations) with display names and the core scores
  benchmark_inputs.js/.json the current benchmark inputs (100 primary + 31 supplementary) for the exercise list
  records/<id>.js           per-record detail loaded on demand: numbered source lines, dossier fields, declarations,
                            certificate text, membership record, per-view recorded selections and outcomes
Displayed text has email patterns masked; the released files are not modified. The core scores are checked against
the paper's Table 16 values in docs/data/localization_full.json.
"""
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

root = Path(__file__).resolve().parents[1]
out = root / 'docs' / 'data'
rec_dir = out / 'records'
rec_dir.mkdir(parents=True, exist_ok=True)
EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')


import html as _html


def mask(t):
    """Display projection: numeric/named HTML entities decoded, email patterns masked. Files are not modified."""
    if not isinstance(t, str):
        return t
    return EMAIL.sub('[contact omitted in display]', _html.unescape(t))


def jload(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def pyjson(s):
    """Several release fields are Python-literal strings; decode them safely."""
    if not isinstance(s, str):
        return s
    try:
        return json.loads(s)
    except Exception:
        import ast
        try:
            return ast.literal_eval(s)
        except Exception:
            return s


def write_js(name, obj, where=out):
    js = json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
    (where / (name + '.json')).write_bytes((js + '\n').encode('utf-8'))
    (where / (name + '.js')).write_text('window.COPEER_DATA = window.COPEER_DATA || {};\nwindow.COPEER_DATA[%s] = %s;\n' % (json.dumps(name), js), encoding='utf-8')
    return hashlib.sha256((js + '\n').encode('utf-8')).hexdigest()


# ---------------------------------------------------------------- views
VIEW_NAMES = {
    'EXP1__claude-haiku-4-5-20251001': 'Haiku 4.5 (retained notice)',
    'EXP5__claude-haiku-4-5-20251001': 'Haiku 4.5 (continuation)',
    'EXP1__claude-sonnet-5': 'Sonnet 5',
    'EXP2__claude-opus-5-5': 'Opus 5.5',
    'EXP2__local_deepseek_r1_qwen_32b': 'DeepSeek R1 Qwen',
    'EXP2__local_gemma3_27b': 'Gemma 3 27B',
    'EXP2__local_glm45_air_fp8': 'GLM 4.5 Air',
    'EXP2__local_gpt_oss_120b': 'GPT-OSS 120B',
    'EXP2__local_gpt_oss_20b': 'GPT-OSS 20B',
    'EXP2__local_kimi_linear_48b_a3b_instruct': 'Kimi Linear',
    'EXP2__local_nemotron35_lightning_30b_a3b': 'Nemotron 3.5 Lightning',
    'EXP2__local_nemotron3_super_120b_a12b_fp8': 'Nemotron 3 Super',
    'EXP4__gemini-3.1-pro': 'Gemini 3.1 Pro',
    'EXP4__gpt-5.6-luna': 'GPT-5.6 Luna',
}
views_meta = jload(root / 'benchmark/views.json')['views']
scores = jload(root / 'benchmark/core/expected_scores.json')
prim = scores['populations']['retained_original_primary']
supp = scores['populations']['retained_scorable_evaluation']
assert set(views_meta) == set(VIEW_NAMES), 'view ids changed'
table16 = {r['name']: r for r in jload(out / 'localization_full.json')['rows']}
table1_names = set(r['name'] for r in jload(out / 'localization_main.json')['rows'] if r['kind'] == 'model')
views = []
for vid, meta in views_meta.items():
    sc = prim['views'][vid]
    name = VIEW_NAMES[vid]
    t = table16[name.replace('TF–IDF', 'TF-IDF')]
    assert abs(sc['hit1']['percent'] - t['hit1']['value']) < 1e-9 and abs(sc['hit3']['percent'] - t['hit3']['value']) < 1e-9, (vid, sc['hit1'], t['hit1'])
    views.append({'view_id': vid, 'name': name, 'lane': meta['lane'], 'reporting_scope': meta['reporting_scope'], 'main_table': name in table1_names, 'release_main_table_flag': bool(sc.get('main_table_configuration')),
                  'primary': {'hit1': sc['hit1'], 'hit3': sc['hit3'], 'rule_misses_by_cause': sc.get('rule_misses_by_cause')},
                  'supplementary': {'hit1': supp['views'][vid]['hit1'], 'hit3': supp['views'][vid]['hit3']}})
views.sort(key=lambda v: -v['primary']['hit1']['percent'])
views_obj = {'source': {'label': 'release:benchmark/core/expected_scores.json', 'caption': 'Core scores from the released replay (100 primary inputs from %d problem clusters; %d supplementary scorable inputs). Percentages equal the paper\'s Table 16 (checked at build time).' % (prim['n_problem_clusters'], supp['denominator'])},
             'primary_denominator': prim['denominator'], 'supplementary_denominator': supp['denominator'], 'n_problem_clusters': prim['n_problem_clusters'],
             'baselines': prim['baselines'], 'views': views}

# ---------------------------------------------------------------- membership and index
membership = jload(root / 'bugbank/core/membership.json')
mrec = {r['record_id']: r for r in membership['records']}
eligible = set(membership['eligible_record_ids'])
primary100 = set(membership['benchmark_clean_primary191_record_ids'])
scorable131 = set(membership['benchmark_clean_all255_record_ids'])
exact_gold = set(membership['exact_current_human_gold_record_ids'])
excluded = set(membership['benchmark_excluded_record_ids'])
assert len(eligible) == 147 and len(primary100) == 100 and len(scorable131) == 131
index = jload(root / 'bugbank/index.json')
assert len(index['records']) == 284
GROUP_NAMES = {'qedbench': 'QEDBench', 'stackexchange': 'Stack Exchange collection', 'mse': 'math.SE collection', 'proofwiki': 'ProofWiki', 'arxiv': 'arXiv', 'reddit_a': 'Reddit', 'reddit_b': 'Reddit', 'additions': 'Reference-proof additions'}

# ---------------------------------------------------------------- selections and outcomes (per item per view)
sel = defaultdict(dict)
with open(root / 'benchmark/selections.jsonl', encoding='utf-8') as f:
    for line in f:
        d = json.loads(line)
        cp = pyjson(d['candidate_parse']); rec = pyjson(d['record']); fa = pyjson(d['final_attempt_status'])
        sel[d['item_id']][d['view_id']] = {'candidates': (cp or {}).get('candidates') if isinstance(cp, dict) else None, 'attempt_class': (rec or {}).get('attempt_class') if isinstance(rec, dict) else None, 'valid_protocol': (rec or {}).get('valid_protocol') if isinstance(rec, dict) else None, 'final_attempt_class': (fa or {}).get('final_attempt_class') if isinstance(fa, dict) else None, 'answer_file': d.get('answer_file')}
outc = defaultdict(dict)
with open(root / 'benchmark/outcomes_derived.jsonl', encoding='utf-8') as f:
    for line in f:
        d = json.loads(line)
        outc[d['item_id']][d['view_id']] = {'hit1': int(d['hit1']) if str(d['hit1']).isdigit() else d['hit1'], 'hit3': int(d['hit3']) if str(d['hit3']).isdigit() else d['hit3'], 'valid': str(d['valid']) == 'True', 'attempt_class': d['attempt_class'], 'cause': d['cause']}

# ---------------------------------------------------------------- mechanism annotations (bugbank/annotations/records)
MECH_NAMES = {'structural_inference': 'Structural inference', 'algebra_order': 'Algebra or order', 'omitted_case': 'Omitted case', 'counting': 'Counting', 'quantifier_scope': 'Quantifier scope', 'definition_scope': 'Definition or domain', 'algorithm_invariant': 'Algorithm invariant', 'analytic_inference': 'Analytic inference'}
ann = {}
ann_path = root / 'bugbank/annotations/records/annotations_current.json'
if ann_path.exists():
    for a in jload(ann_path):
        key = a.get('record') or a.get('record_id')
        unc = 'mechanism' in (a.get('uncertain_fields') or [])
        ann[key] = {'mechanism': a.get('mechanism'), 'mechanism_name': MECH_NAMES.get(a.get('mechanism'), a.get('mechanism')), 'mechanism_uncertain': unc}

# ---------------------------------------------------------------- per record
rows = []
inputs = []
total_bytes = 0
for ir in index['records']:
    rid = ir['record_id']
    dossier = jload(root / ir['dossier']); src = jload(root / ir['source'])
    cert_path = root / ir['certificate']; cert_text = cert_path.read_text(encoding='utf-8'); cert_sha = hashlib.sha256(cert_path.read_bytes()).hexdigest()
    m = mrec.get(rid)
    lines = pyjson(src['lines'])
    gold_src = pyjson(src.get('gold')) if src.get('gold') is not None else None
    fields = dossier.get('fields') or {}
    decls = pyjson(dossier.get('selected_declarations')) or []
    roles = pyjson(dossier.get('benchmark_roles')) or {}
    rv = (m or {}).get('review_evidence') or []
    row = {
        'id': rid, 'group': ir['group'], 'group_name': GROUP_NAMES.get(ir['group'], ir['group']),
        'core': rid in eligible, 'primary': rid in primary100, 'scorable': rid in scorable131, 'benchmark_excluded': rid in excluded,
        'exact_gold': rid in exact_gold,
        'continuity': (m or {}).get('continuity'), 'current_gold': (m or {}).get('current_gold'),
        'review': [{'cohort': e.get('cohort'), 'locator': e.get('review_locator'), 'answers': e.get('answers')} for e in rv],
        'any_all_yes': any(e.get('answers') == ['YES', 'YES', 'YES'] for e in rv),
        'any_adverse': any(any(a != 'YES' for a in (e.get('answers') or [])) for e in rv),
        'original_primary191': bool(ir.get('primary')), 'original_scorable255': bool(ir.get('scorable')),
        'n_nonblank': src.get('n_nonblank_text') or roles.get('n_nonblank_text'),
        'claim_quote': mask(fields.get('claim_quote') or ''),
        'flaw': mask(fields.get('flaw') or ''),
        'declaration': (decls[0].get('name') if decls and isinstance(decls[0], dict) else None),
        'axioms': (decls[0].get('axioms') if decls and isinstance(decls[0], dict) else None),
        'certificate': ir['certificate'], 'certificate_sha256_12': cert_sha[:12],
        'evidence_tier_historical': ir.get('evidence_tier'),
        'mechanism': (ann.get(rid) or {}).get('mechanism'), 'mechanism_name': (ann.get(rid) or {}).get('mechanism_name'), 'mechanism_uncertain': (ann.get(rid) or {}).get('mechanism_uncertain'),
    }
    rows.append(row)
    detail = {
        'id': rid, 'index': row,
        'source_lines': [{'label': str(l[0]), 'text': mask(l[1])} for l in lines],
        'gold_source_file': gold_src,
        'fields': {k: mask(v) for k, v in fields.items() if k in ('problem', 'source_context', 'claim_quote', 'flaw', 'witness', 'explanation')},
        'declarations': decls,
        'certificate': {'path': ir['certificate'], 'sha256': cert_sha, 'text': mask(cert_text)},
        'membership': ({k: m.get(k) for k in ('eligible', 'eligibility_reasons', 'continuity', 'current_gold', 'review_evidence', 'current_source_scope_flags', 'original_primary191', 'original_scorable255')} if m else None),
        'bindings': (m or {}).get('current_scientific_bindings'),
        'historical_export_fields': {'evidence_tier': dossier.get('evidence_tier'), 'human_approval_of_current_artifact': dossier.get('human_approval_of_current_artifact'), 'source_correspondence': dossier.get('source_correspondence')},
        'selections': {vid: dict(sel.get(rid, {}).get(vid, {}), **{'outcome': outc.get(rid, {}).get(vid)}) for vid in VIEW_NAMES},
    }
    if m and cert_sha != m['current_scientific_bindings']['certificate_sha256']:
        detail['certificate']['note'] = 'file hash differs from the membership binding'
    js = json.dumps(detail, ensure_ascii=False, separators=(',', ':'))
    (rec_dir / (rid + '.js')).write_text('window.COPEER_RECORDS = window.COPEER_RECORDS || {};\nwindow.COPEER_RECORDS[%s] = %s;\n' % (json.dumps(rid), js), encoding='utf-8')
    total_bytes += len(js)
    if rid in scorable131:
        inputs.append({'id': rid, 'group_name': row['group_name'], 'primary': rid in primary100, 'n_nonblank': row['n_nonblank'], 'n_lines': len([l for l in lines if str(l[0]).isdigit()]), 'gold': row['current_gold'], 'exact_gold': row['exact_gold']})

counts = {'released': len(rows), 'core': sum(r['core'] for r in rows), 'primary': sum(r['primary'] for r in rows), 'scorable': sum(r['scorable'] for r in rows), 'with_any_all_yes_review': sum(r['any_all_yes'] for r in rows), 'by_group': {}}
for r in rows:
    counts['by_group'][r['group_name']] = counts['by_group'].get(r['group_name'], 0) + 1
assert counts['core'] == 147 and counts['primary'] == 100 and counts['scorable'] == 131
h1 = write_js('dossiers_index', {'source': {'label': 'release:bugbank/index.json + bugbank/core/membership.json', 'caption': 'One row per released dossier; the current human-review layer is joined by record id from membership.json. Historical automated-export fields are kept apart.'}, 'counts': counts, 'rows': rows})
h2 = write_js('views', views_obj)
h3 = write_js('benchmark_inputs', {'source': {'label': 'release:benchmark/core/expected_scores.json populations', 'caption': 'Current benchmark inputs: 100 primary and 31 supplementary scorable records with their current reference lines.'}, 'rows': sorted(inputs, key=lambda x: (not x['primary'], x['id']))})
print('dossiers_index %d rows (core %d, primary %d, scorable %d); views %d; inputs %d; records %d files, %.1f MB' % (len(rows), counts['core'], counts['primary'], counts['scorable'], len(views), len(inputs), len(rows), total_bytes / 1e6))
print('sha256 dossiers_index %s views %s benchmark_inputs %s' % (h1[:16], h2[:16], h3[:16]))
