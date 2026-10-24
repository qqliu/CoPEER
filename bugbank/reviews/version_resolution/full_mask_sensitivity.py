#!/usr/bin/env python3
"""Descriptive exclusion sensitivity on the earlier evaluated collection using the frozen adverse masks.

Sums the saved per-response outcomes (failures already count as misses) over explicit record subsets:
the earlier primary (191) and scorable (255) sets, minus the semantic-review mask (31 ids) and minus the
combined benchmark mask (semantic + separate gold-line, 34 ids). Model/view selection, reference labels and
scoring rules are those of the release; no model call, grader call, bootstrap or proof build is made.

Portable usage from the release root:
  python3 -B reviews/version_resolution/full_mask_sensitivity.py --release . --masks reviews/version_resolution/adverse_masks.json --output /tmp/full_mask_sensitivity.json
"""
import argparse, hashlib, json, sys
from pathlib import Path

def read(p): return json.loads(Path(p).read_text())
def readl(p): return [json.loads(s) for s in Path(p).read_text().splitlines() if s.strip()]
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--release', type=Path, required=True); ap.add_argument('--masks', type=Path, required=True); ap.add_argument('--output', type=Path, required=True); ap.add_argument('--table', type=Path)
    a = ap.parse_args(); R = a.release.resolve()
    masks = read(a.masks)
    masks_rel = a.masks.resolve().relative_to(R).as_posix() if a.masks.resolve().is_relative_to(R) else 'reviews/version_resolution/adverse_masks.json'
    HAIKU_LABELS = {'EXP1__claude-haiku-4-5-20251001': 'Haiku 4.5, retained-notices view (session-limit notices kept as recorded answers)', 'EXP5__claude-haiku-4-5-20251001': 'Haiku 4.5, outage-continuation view (the view used in the earlier main table)'}
    items = {r['record_id']: r for r in readl(R / 'benchmark/items.jsonl')}
    settings = read(R / 'benchmark/code/settings.json'); views = read(R / 'benchmark/views.json')['views']
    outcomes_rows = readl(R / 'benchmark/outcomes_derived.jsonl'); outcomes = {(r['view_id'], r['item_id']): r for r in outcomes_rows}
    assert len(outcomes) == len(outcomes_rows) == 3850 and len(views) == 14 and len(settings['manuscript_views']) == 13
    published = read(R / 'benchmark/aggregates.json')['populations']
    primary = {rid for rid, x in items.items() if x['current_roles']['evaluation_primary']}
    scorable = {rid for rid, x in items.items() if x['current_roles']['evaluation_scorable']}
    assert len(primary) == 191 and len(scorable) == 255
    sem = set(masks['semantic_review_mask']['record_ids']); comb = set(masks['combined_benchmark_mask']['record_ids']); gold = set(masks['separate_gold_line_mask']['record_ids'])
    assert len(sem) == 31 and len(comb) == 34 and len(gold) == 3 and sem <= comb and comb == sem | gold
    assert len(primary - sem) == masks['semantic_review_mask']['earlier_primary_remaining'] == 173
    assert len(primary - comb) == masks['combined_benchmark_mask']['earlier_primary_remaining'] == 170
    assert len(scorable - sem) == masks['semantic_review_mask']['earlier_scorable_remaining'] == 230
    assert len(scorable - comb) == masks['combined_benchmark_mask']['earlier_scorable_remaining'] == 227
    subsets = {
        'earlier_primary_191': ('original', sorted(primary)),
        'earlier_primary_minus_semantic_mask_173': ('semantic_review_mask (31 ids)', sorted(primary - sem)),
        'earlier_primary_minus_combined_mask_170': ('combined_benchmark_mask (34 ids = semantic 31 + separate gold-line 3)', sorted(primary - comb)),
        'earlier_scorable_255': ('original', sorted(scorable)),
        'earlier_scorable_minus_semantic_mask_230': ('semantic_review_mask (31 ids)', sorted(scorable - sem)),
        'earlier_scorable_minus_combined_mask_227': ('combined_benchmark_mask (34 ids)', sorted(scorable - comb)),
    }
    sys.path.insert(0, str(R / 'benchmark/code')); import frozen_score as score
    base_values = {rid: score.baselines(item) for rid, item in items.items() if rid in scorable}
    result = {}
    for name, (mask_name, ids) in subsets.items():
        n = len(ids); view_results = {}
        for view in views:
            rr = [outcomes[(view, rid)] for rid in ids]; metrics = {}
            for metric in ('hit1', 'hit3'):
                k = sum(r[metric] for r in rr); metrics[metric] = {'hits': k, 'denominator': n, 'percent': round(100 * k / n, 1)}
            view_results[view] = {'in_earlier_191_reporting_selection': view in settings['manuscript_views'], 'view_label': HAIKU_LABELS.get(view, view), 'reporting_scope': views[view]['reporting_scope'], **metrics}
            pub_name = {'earlier_primary_191': 'primary_ge10_lines', 'earlier_scorable_255': 'secondary_scorable'}.get(name)
            if pub_name:
                pub = published[view][pub_name]; assert n == pub['denominator']
                for metric in ('hit1', 'hit3'): assert metrics[metric]['hits'] == pub[metric]['numerator'], (name, view, metric)
        baselines = {}
        for baseline in base_values[ids[0]]:
            k = sum(base_values[rid][baseline] for rid in ids); baselines[baseline] = {'expected_hits' if baseline == 'random_line' else 'hits': k, 'denominator': n, 'percent': round(100 * k / n, 1)}
        result[name] = {'mask': mask_name, 'denominator': n, 'excluded_ids': sorted((primary if 'primary' in name else scorable) - set(ids)), 'views': view_results, 'baselines': baselines}
    inputs = ['benchmark/items.jsonl', 'benchmark/outcomes_derived.jsonl', 'benchmark/views.json', 'benchmark/code/settings.json', 'benchmark/code/frozen_score.py', 'benchmark/aggregates.json']
    report = {'schema': 'copeer.full_adverse_mask_exclusion_sensitivity.v1',
              'method': 'Saved per-response outcomes (hit1/hit3 with unusable answers and failures as misses) summed over explicit record subsets; masks are the frozen adverse_masks.json ids; model/view selection, reference labels and scoring rules unchanged; no confidence intervals, bootstrap, model or grader call.',
              'scope': 'Descriptive sensitivity on the earlier evaluated collection (191 primary / 255 scorable). The current human-verified core (100 / 131) has zero overlap with both masks and is unchanged. The 13-view selection flag refers to the EARLIER 191-input reporting selection (benchmark/code/settings.json manuscript_views), not to the current 12-row main table, which omits Haiku.',
              'masks': {'semantic_review_mask': {'ids': sorted(sem), 'n': len(sem)}, 'separate_gold_line_mask': {'ids': sorted(gold), 'n': len(gold)}, 'combined_benchmark_mask': {'ids': sorted(comb), 'n': len(comb)}, 'source': {'path': masks_rel, 'sha256': digest(a.masks)}},
              'haiku_view_labels': HAIKU_LABELS,
              'earlier_191_reporting_selection': settings['manuscript_views'], 'all_views': list(views), 'subsets': result,
              'inputs': [{'path': p, 'sha256': digest(R / p), 'bytes': (R / p).stat().st_size} for p in inputs], 'script_sha256': digest(Path(__file__))}
    a.output.write_text(json.dumps(report, indent=1, ensure_ascii=False) + '\n')
    if a.table:
        lines = ['Denominators: 191 = earlier primary inputs; 173 = minus the semantic-review mask (31 ids); 170 = minus the combined mask (34 ids). The selection column refers to the earlier 191-input reporting selection (13 views), not the current 12-row main table. Haiku views: EXP1 = retained-notices view; EXP5 = outage-continuation view.', '', '| View | in earlier 191-input reporting selection | 191 Hit@1 | 173 Hit@1 | 170 Hit@1 | 191 Hit@3 | 173 Hit@3 | 170 Hit@3 |', '|---|---|---|---|---|---|---|---|']
        for view in views:
            r = lambda s, m: result[s]['views'][view][m]; f = lambda s, m: f"{r(s, m)['hits']} ({r(s, m)['percent']}%)"
            lines.append(f"| {HAIKU_LABELS.get(view, view)} | {'yes' if view in settings['manuscript_views'] else 'no'} | {f('earlier_primary_191','hit1')} | {f('earlier_primary_minus_semantic_mask_173','hit1')} | {f('earlier_primary_minus_combined_mask_170','hit1')} | {f('earlier_primary_191','hit3')} | {f('earlier_primary_minus_semantic_mask_173','hit3')} | {f('earlier_primary_minus_combined_mask_170','hit3')} |")
        lines += ['', '| View | 255 Hit@1 | 230 Hit@1 | 227 Hit@1 | 255 Hit@3 | 230 Hit@3 | 227 Hit@3 |', '|---|---|---|---|---|---|---|']
        for view in views:
            r = lambda s, m: result[s]['views'][view][m]; f = lambda s, m: f"{r(s, m)['hits']} ({r(s, m)['percent']}%)"
            lines.append(f"| {HAIKU_LABELS.get(view, view)} | {f('earlier_scorable_255','hit1')} | {f('earlier_scorable_minus_semantic_mask_230','hit1')} | {f('earlier_scorable_minus_combined_mask_227','hit1')} | {f('earlier_scorable_255','hit3')} | {f('earlier_scorable_minus_semantic_mask_230','hit3')} | {f('earlier_scorable_minus_combined_mask_227','hit3')} |")
        a.table.write_text('\n'.join(lines) + '\n')
    print(json.dumps({'subsets': {k: v['denominator'] for k, v in result.items()}, 'published_checks': 'PASS', 'output': str(a.output)}))

if __name__ == '__main__': main()
