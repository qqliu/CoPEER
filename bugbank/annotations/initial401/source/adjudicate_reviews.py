#!/usr/bin/env python3
"""Apply the documented conservative review policy without changing primary coding."""
import json
from copy import deepcopy
from pathlib import Path

BASE=Path(__file__).resolve().parent
PAIRS={'family_documented':'family_evidence','repair_documented':'repair_evidence',
       'nondegenerate_alternative_documented':'nondegenerate_evidence'}


def read(p):
    return json.loads(p.read_text())


def adjudicate(primary, reviews, blind_sample_record=None):
    """Return corrections and coverage without writes or primary mutation."""
    rows=deepcopy(primary)
    expected={(rid,k) for rid,row in rows.items() for k in PAIRS if row[k]} | {
        (rid,'minimality_scope') for rid,row in rows.items() if row['minimality_scope']=='global_argument'}
    actual=[(r['record'],r['field']) for p,r in reviews]
    if len(set(actual))!=len(actual) or set(actual)!=expected:
        raise ValueError('Positive review coverage must equal every initial positive property exactly once')
    corrections=[]
    decisions=[]
    for path,r in reviews:
        rid,key=r['record'],r['field']
        if set(r)!={'record','field','original_value','decision','proposed_changes','reason'}:
            raise ValueError('Review schema fields differ: '+rid)
        if not isinstance(r['reason'],str) or not r['reason'].strip():
            raise ValueError('Review needs a substantive reason: '+rid)
        if type(r['original_value']) is not type(primary[rid][key]) or r['original_value']!=primary[rid][key]:
            raise ValueError('Review does not bind the primary value: '+rid)
        if not isinstance(r['proposed_changes'],dict):
            raise ValueError('Review changes must be a mapping: '+rid)
        changes=dict(r['proposed_changes'])
        allowed={key,'uncertain_fields'} | ({PAIRS[key]} if key in PAIRS else {'minimality_evidence'})
        if key=='family_documented':allowed.add('family_kind')
        if set(changes)-allowed:
            raise ValueError('Field review changes an unrelated substantive label: '+rid)
        if r['decision']=='keep' and changes.get(key,primary[rid][key])!=primary[rid][key]:
            raise ValueError('Keep review changes the reviewed label: '+rid)
        # Field-level review must never erase unrelated uncertainty flags.
        uncertainty=set(rows[rid]['uncertain_fields'])
        uncertainty.update(changes.pop('uncertain_fields',[]))
        if r['decision']=='uncertain':
            if key not in PAIRS:
                raise ValueError('Unresolved nonboolean review needs an explicit adjudication')
            changes.update({key:False,PAIRS[key]:''})
            if key=='family_documented':changes['family_kind']='none'
            uncertainty.add(key)
            reason='Conservative documentation policy: unresolved positive excluded. '+r['reason']
        elif r['decision'] in {'keep','change'}:
            uncertainty.discard(key)
            reason='Independent full-packet review accepted. '+r['reason']
        else:
            raise ValueError('Unknown review decision')
        if sorted(uncertainty)!=rows[rid]['uncertain_fields']:
            changes['uncertain_fields']=sorted(uncertainty)
        changes={k:v for k,v in changes.items() if rows[rid][k]!=v}
        if changes:
            corrections.append({'record':rid,'changes':changes,'reason':reason,'review_source':path,
                                'adjudicator':'primary assistant, conservative documentation rule'})
            rows[rid].update(changes)
    # Resolve cross-field suggestions only after every direct field review.
    # This prevents a later review of another property from reintroducing
    # uncertainty already resolved by this field's accepted evidence.
    direct={}
    for path,r in reviews:
        direct.setdefault(r['record'],[]).append((path,r))
    for rid,record_reviews in direct.items():
        uncertainty=set(rows[rid]['uncertain_fields'])
        for path,r in record_reviews:
            if r['decision']=='uncertain':uncertainty.add(r['field'])
            else:uncertainty.discard(r['field'])
        if sorted(uncertainty)!=rows[rid]['uncertain_fields']:
            changes={'uncertain_fields':sorted(uncertainty)}
            corrections.append({'record':rid,'changes':changes,
                'reason':'Final direct field reviews resolve their own uncertainty; retain all other uncertainty.',
                'review_source':','.join(sorted({path for path,r in record_reviews})),
                'adjudicator':'primary assistant, conservative documentation rule'})
            rows[rid].update(changes)
    # The blind sample identified a boundary-label disagreement outside the
    # positive review's concerns. Strict convexity alone does not document a
    # contrasted restriction or alternative construction under this codebook.
    if blind_sample_record is not None:
        rid=blind_sample_record
        changes={'nondegenerate_alternative_documented':False,'nondegenerate_evidence':'',
                 'uncertain_fields':sorted(set(rows[rid]['uncertain_fields'])|{'mechanism','nondegenerate_alternative_documented'})}
        if any(rows[rid][key]!=value for key,value in changes.items()):
            corrections.append({'record':rid,'changes':changes,
                'reason':'Blind-sample adjudication: a strictly convex primary polygon is explicit, but the packet does not contrast it with a named boundary exception or an alternative; exclude under conservative documentation coding.',
                'review_source':'independent_sample.json','adjudicator':'primary assistant'})
            rows[rid].update(changes)
    for path,r in reviews:
        decisions.append({'record':r['record'],'field':r['field'],'review_source':path,
                          'review_decision':r['decision'],'final_value':rows[r['record']][r['field']]})
    coverage={
        'expected_positive_properties':len(expected),'reviewed_properties':len(actual),
        'reviewed_records':len({rid for rid,key in actual}),
        'policy':'All original positive family/repair/named-restriction/global-minimality fields reviewed; uncertain positives excluded from final documentation counts. Primary labels and independent agreement remain unchanged.',
        'decisions':decisions}
    return corrections,coverage,rows


def main():
    from analyze_census import load_annotations, load_inputs, validate_row
    _,inputs=load_inputs()
    primary=load_annotations(inputs)
    paths=[BASE/'review/positive_review_01_02_07.json']+[
        BASE/f'review/positive_review_{i:02}.json' for i in [3,4,5,6,8]]
    reviews=[(p.name,r) for p in paths for r in read(p)]
    corrections,coverage,rows=adjudicate(primary,reviews,'reddit_learnmath_157rs31')
    for rid,row in rows.items():validate_row(row,inputs[rid])
    (BASE/'review/corrections.json').write_text(json.dumps(corrections,ensure_ascii=False,indent=2)+'\n')
    (BASE/'review/positive_review_coverage.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'positive_properties_reviewed':coverage['reviewed_properties'],'records_reviewed':coverage['reviewed_records'],
                      'correction_entries':len(corrections),'corrected_records':len({r['record'] for r in corrections})}))


if __name__=='__main__':main()
