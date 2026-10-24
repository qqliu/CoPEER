#!/usr/bin/env python3
"""Check saved census counts with original arithmetic helpers. No models, regrading or Lean.
This is a projection check, not a rerun of the historical audit pipeline.
"""
from pathlib import Path
from collections import Counter
import hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent

def load(p):return json.loads((HERE/p).read_text())
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,HERE/path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    manifest=load('CENSUS_INCLUSION_MANIFEST.json')
    for r in manifest['files']:
        assert hashlib.sha256((HERE/r['public_path']).read_bytes()).hexdigest()==r['public_sha256'],r['public_path']
    c=module('current_census_helpers','records/source/refresh.py')
    annotations=load('records/annotations_current.json')
    metadata=load('records/record_identity_projection.json')
    saved=load('records/generated/verified_counterexample_summary.json')
    counts,categories=c.census_counts(annotations,metadata)
    assert counts==saved['counts']
    assert categories==saved['categories']
    assert dict(sorted(Counter(c.venue(r['record_id'])for r in metadata).items()))==saved['by_source']
    inputrows={r['record']:r for r in load('records/INPUTS_CURRENT.json')}
    for a in annotations:
        fields=inputrows[a['record']]['source_fields']
        for key,span in a.get('evidence_spans',{}).items():
            assert fields[span['field']][span['start']:span['end']]==a[key],(a['record'],key)
    h=module('historical_census_helpers','initial401/source/analyze_census.py')
    inputs={r['record_id']:r for p in sorted((HERE/'initial401/inputs').glob('shard_*.json'))for r in json.loads(p.read_text())}
    primary={r['record']:r for p in sorted((HERE/'initial401/annotations').glob('shard_*.json'))for r in json.loads(p.read_text())}
    final=load('initial401/results/annotated_records.json')
    savedh=load('initial401/results/census.json')
    assert h.summarize(final,inputs)==savedh['counts']
    assert h.summarize(primary.values(),inputs)==savedh['primary_counts']
    review=load('initial401/review/independent_sample.json')
    assert h.agreement(primary,review)==savedh['review']['agreement_before_corrections']
    for r in final:
        a={k:r[k]for k in h.REQUIRED}
        assert h.validate_row(a,inputs[r['record']])==r['evidence_bindings']
    print(json.dumps({'current_records':len(annotations),'historical_records':len(final),'historical_recoding_sample':len(review),'saved_counts_match':True,'source_excerpt_offsets_match':True,'models_called':0,'lean_executed':0},indent=2))
if __name__=='__main__':main()
