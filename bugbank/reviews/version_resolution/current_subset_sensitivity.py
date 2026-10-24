#!/usr/bin/env python3
"""Descriptive saved-output sensitivities on subsets of the current human-verified core (100 primary inputs), scored
against the current accepted-line sets exactly as the core replay does, plus a classification of the 34
owner-confirmed continuity bindings by what the saved review cohorts recorded.

Subsets (from reviews/verified_core/membership.json and benchmark/verified_core/reference_line_coverage.json):
  current_100                 the 100 retained original-primary inputs
  exact_line_reviewed_55      current_100 records whose final random-audit packet answered Q5 = YES (designated lines locate the challenged claim)
  separate_line_clean_27      current_100 records with a clean (YES/NO/NO) separate reference-line review (initial40 or fresh40)
  all_line_approved_69        union of the two (13 records are in both)
Per-record outcome: validity/cause from benchmark/outcomes_derived.jsonl (failures and unusable answers are misses);
hit1 = first parsed candidate in the current accepted-line set; hit3 = any of the first three. The 100-record totals are
asserted equal to benchmark/verified_core/expected_scores.json for every view. No model, grader or bootstrap call.
Portable usage from the release root:
  python3 -B reviews/version_resolution/current_subset_sensitivity.py --release . --output /tmp/current_subset_sensitivity.json --table /tmp/current_subset_sensitivity.md --continuity /tmp/continuity_bindings.json
"""
import argparse, hashlib, json
from pathlib import Path
def read(p): return json.loads(Path(p).read_text())
def readl(p): return [json.loads(s) for s in Path(p).read_text().splitlines() if s.strip()]
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap = argparse.ArgumentParser(description=__doc__); ap.add_argument('--release', type=Path, required=True); ap.add_argument('--output', type=Path, required=True); ap.add_argument('--table', type=Path); ap.add_argument('--continuity', type=Path)
    a = ap.parse_args(); R = a.release.resolve()
    m = read(R / 'reviews/verified_core/membership.json'); cov = read(R / 'benchmark/verified_core/reference_line_coverage.json')['records']
    exp = read(R / 'benchmark/verified_core/expected_scores.json')['populations']['retained_original_primary']['views']
    settings = read(R / 'benchmark/code/settings.json'); views_meta = read(R / 'benchmark/views.json')['views']
    cur = list(m['benchmark_clean_primary191_record_ids']); assert len(cur) == 100; curset = set(cur)
    gold = {r['record_id']: set(r['current_gold']) for r in m['records']}
    q5 = {r for r, x in cov.items() if any(v.get('answer') == 'YES' for v in x['optional_random_audit_Q5'])}
    sep = {r for r, x in cov.items() if any(v.get('clean_answer_pattern') for v in x['separate_line_reviews'])}
    subsets = {'current_100': sorted(curset), 'exact_line_reviewed_55': sorted(curset & q5), 'separate_line_clean_27': sorted(curset & sep), 'all_line_approved_69': sorted(curset & (q5 | sep))}
    assert [len(v) for v in subsets.values()] == [100, 55, 27, 69] and len(curset & q5 & sep) == 13
    od = {(r['view_id'], r['item_id']): r for r in readl(R / 'benchmark/outcomes_derived.jsonl')}
    sel = {(r['view_id'], r['item_id']): r for r in readl(R / 'benchmark/selections.jsonl')}
    views = sorted({v for v, _ in od}); assert len(views) == 14
    HAIKU = {'EXP1__claude-haiku-4-5-20251001': 'Haiku 4.5, retained-notices view', 'EXP5__claude-haiku-4-5-20251001': 'Haiku 4.5, outage-continuation view'}
    def score(v, rid):
        o = od.get((v, rid)); c = (sel[(v, rid)]['candidate_parse'].get('candidates') or []) if (v, rid) in sel else []
        valid = bool(o and o.get('valid')); return float(valid and c and c[0] in gold[rid]), float(valid and any(x in gold[rid] for x in c[:3]))
    result = {}
    for name, ids in subsets.items():
        n = len(ids); vr = {}
        for v in views:
            h1 = h3 = 0.0
            for rid in ids: a1, a3 = score(v, rid); h1 += a1; h3 += a3
            vr[v] = {'in_earlier_191_reporting_selection': v in settings['manuscript_views'], 'view_label': HAIKU.get(v, v), 'reporting_scope': views_meta[v]['reporting_scope'], 'hit1': {'hits': int(h1), 'denominator': n, 'percent': round(100 * h1 / n, 1)}, 'hit3': {'hits': int(h3), 'denominator': n, 'percent': round(100 * h3 / n, 1)}}
            if name == 'current_100': assert (int(h1), int(h3)) == (exp[v]['hit1']['hits'], exp[v]['hit3']['hits']), (v, h1, h3)
        result[name] = {'denominator': n, 'record_ids': ids, 'views': vr}
    # 34 continuity bindings: classify by what the saved cohorts recorded (no inference about unrecorded versions)
    cont = []
    cohort_hash_fields = {'original100': [], 'earlier_selected30': ['original_lean_sha256', 'original_input_sha256', 'original_packet_sha256'], 'selected33': ['original_packet_sha256', 'reported_actual_packet_sha256'], 'selected30': ['original_packet_sha256'], 'random100': ['original_lean_sha256', 'original_input_sha256', 'original_packet_sha256']}
    tables = {}
    pmap = m.get('packet_record_mapping', {})
    for cname in ('original100', 'earlier_selected30', 'selected33'):
        d = read(R / f'reviews/{cname}/answers.json'); rows = d['rows'] if isinstance(d, dict) and 'rows' in d else d
        p2r = pmap.get(cname, {}); p2r = p2r.get('packets', p2r) if isinstance(p2r, dict) else {}
        tables[cname] = {(r.get('record_id') or (p2r.get(r.get('packet_id')) if isinstance(p2r.get(r.get('packet_id')), str) else (p2r.get(r.get('packet_id')) or {}).get('record_id')) or r.get('packet_id')): r for r in rows}
    for r in m['records']:
        if not (r['eligible'] and r['continuity'] == 'OWNER_CONFIRMED_CURRENT_APPLICABILITY'): continue
        cohorts = [ev['cohort'] for ev in r['review_evidence'] if ev.get('continuity') == 'OWNER_CONFIRMED_CURRENT_APPLICABILITY']
        recorded = {}
        for cname in cohorts:
            row = tables.get(cname, {}).get(r['record_id']) or next((x for x in tables.get(cname, {}).values() if x.get('record_id') == r['record_id']), None)
            recorded[cname] = {k: row.get(k) for k in cohort_hash_fields.get(cname, []) if row and row.get(k)} if row else {}
        any_hash = any(recorded[c] for c in recorded)
        lean_cmp = None
        for c in recorded:
            if recorded[c].get('original_lean_sha256'): lean_cmp = (recorded[c]['original_lean_sha256'] == r['current_scientific_bindings']['certificate_sha256'])
        cont.append({'record_id': r['record_id'], 'in_current_100': r['record_id'] in curset, 'continuity_cohorts': cohorts, 'reviewed_artifact_hashes_recorded': any_hash, 'recorded_hash_fields': {c: sorted(v) for c, v in recorded.items()}, 'reviewed_lean_sha256_equals_current_certificate': lean_cmp, 'current_certificate_sha256': r['current_scientific_bindings']['certificate_sha256'], 'current_source_lines_sha256': r['current_scientific_bindings']['source_lines_sha256'], 'classification': 'reviewed_revision_not_recorded' if not any_hash else 'reviewed_artifact_hash_recorded'})
    counts = {'total': len(cont), 'reviewed_revision_not_recorded': sum(c['classification'] == 'reviewed_revision_not_recorded' for c in cont), 'reviewed_artifact_hash_recorded': sum(c['classification'] == 'reviewed_artifact_hash_recorded' for c in cont), 'lean_hash_equal_to_current': sum(c['reviewed_lean_sha256_equals_current_certificate'] is True for c in cont), 'lean_hash_differs_from_current': sum(c['reviewed_lean_sha256_equals_current_certificate'] is False for c in cont), 'in_current_100': sum(c['in_current_100'] for c in cont)}
    inputs = ['reviews/verified_core/membership.json', 'benchmark/verified_core/reference_line_coverage.json', 'benchmark/verified_core/expected_scores.json', 'benchmark/outcomes_derived.jsonl', 'benchmark/selections.jsonl', 'benchmark/code/settings.json', 'benchmark/views.json', 'reviews/original100/answers.json', 'reviews/earlier_selected30/answers.json', 'reviews/selected33/answers.json']
    binds = [{'path': p, 'sha256': digest(R / p)} for p in inputs]
    a.output.write_text(json.dumps({'schema': 'copeer.current_core_subset_sensitivity.v1', 'method': __doc__.strip(), 'subset_sizes': {k: len(v) for k, v in subsets.items()}, 'overlap_exact_and_separate': 13, 'current_100_totals_equal_expected_scores': True, 'subsets': result, 'inputs': binds, 'script_sha256': digest(Path(__file__))}, indent=1, ensure_ascii=False) + '\n')
    if a.continuity: a.continuity.write_text(json.dumps({'schema': 'copeer.owner_confirmed_continuity_bindings.v1', 'scope': 'The 34 eligible records whose all-YES reviews apply to the current set by the authors\' explicit confirmation. Classification records only what the saved cohorts stored; it does not infer whether unrecorded reviewed versions were changed or unchanged.', 'counts': counts, 'records': cont, 'inputs': binds, 'script_sha256': digest(Path(__file__))}, indent=1, ensure_ascii=False) + '\n')
    if a.table:
        L = ['Current-core subsets (current accepted-line sets; failures as misses). 55 = final random-audit Q5 YES; 27 = clean separate line review; 69 = union (13 in both).', '', '| View | in earlier 191 selection | 100 Hit@1 | 55 Hit@1 | 69 Hit@1 | 100 Hit@3 | 55 Hit@3 | 69 Hit@3 |', '|---|---|---|---|---|---|---|---|']
        for v in views:
            f = lambda s, k: f"{result[s]['views'][v][k]['hits']} ({result[s]['views'][v][k]['percent']}%)"
            L.append(f"| {HAIKU.get(v, v)} | {'yes' if v in settings['manuscript_views'] else 'no'} | {f('current_100','hit1')} | {f('exact_line_reviewed_55','hit1')} | {f('all_line_approved_69','hit1')} | {f('current_100','hit3')} | {f('exact_line_reviewed_55','hit3')} | {f('all_line_approved_69','hit3')} |")
        a.table.write_text('\n'.join(L) + '\n')
    print(json.dumps({'subset_sizes': {k: len(v) for k, v in subsets.items()}, 'continuity_counts': counts}))
if __name__ == '__main__': main()
