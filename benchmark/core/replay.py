#!/usr/bin/env python3
"""Score a bound retained-core membership on unchanged saved critic outputs.

This is deterministic replay, not new inference or mathematical grading.
"""
import argparse, collections, hashlib, json, sys, subprocess
sys.dont_write_bytecode = True
from pathlib import Path

HERE = Path(__file__).resolve().parent

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def public_path(p):
    """Saved records name answer files as answers/<sha>.txt; this repository keeps them under benchmark/answers/."""
    return 'benchmark/' + p if str(p).startswith('answers/') else p
def read(p): return json.loads(p.read_text())
def lines(p): return [json.loads(s) for s in p.read_text().splitlines() if s.strip()]
def require(v,s):
    if not v: raise ValueError(s)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--release','--root',dest='root',type=Path,required=True,help='Complete saved release directory')
    ap.add_argument('--membership','--ledger',dest='ledger',type=Path,required=True,help='Bound core-membership JSON ledger')
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--line-review',type=Path,default=HERE/'reference_line_coverage.json',help='Separate bound reference-line coverage ledger')
    ap.add_argument('--with-intervals',action='store_true')
    args=ap.parse_args();root=args.root.resolve()
    require(args.ledger.name=='membership.json','Use the public membership.json beside its verify.py')
    ledger_digest=sha(args.ledger);ledger=read(args.ledger)
    core_list=ledger['eligible_record_ids'];core=set(core_list)
    require(len(core_list)==len(core),'Duplicate eligible ID')
    span_excluded=set(ledger['benchmark_excluded_record_ids'])
    line_review=read(args.line_review) if args.line_review else None
    # The public verifier reconstructs membership from saved anonymous human
    # judgments and verifies exact scientific fields, source labels, original
    # roles, certificate bytes and the original benchmark-input hash. Its
    # scientific projections permit an active resource index restricted to core.
    verification = subprocess.run(
        [sys.executable, '-B', str(args.ledger.parent/'verify.py'), '--release', str(root)],
        check=True, capture_output=True, text=True)
    membership_verification = json.loads(verification.stdout)
    require(membership_verification['status']=='PASS','Public membership verification failed')
    release_bindings={}
    for row in ledger['records']:
        if row['record_id'] in core:
            bound=row['current_scientific_bindings']
            relative=bound['certificate'];p=Path(relative)
            require(not p.is_absolute() and '..' not in p.parts,'Unsafe certificate path')
            require(sha(root/p)==bound['certificate_sha256'],'Core certificate hash mismatch')
            release_bindings[relative]=bound['certificate_sha256']
    require(len(release_bindings)==len(core),'Core certificate coverage differs')
    if args.line_review:
        require(sha(args.line_review)==ledger['reference_line_coverage_sha256'],'Line coverage ledger hash mismatch')
    sys.path.insert(0,str(root/'benchmark/code'))
    import reproduce, frozen_common as parser, frozen_score as score
    reproduce.check_code()
    items={x['record_id']:x for x in lines(root/'benchmark/items.jsonl')}
    resource_ids={x['record_id'] for x in read(root/'bugbank/index.json')['records']}
    require(len(items)==285,'Original benchmark roster changed')
    require(core<=resource_ids,'Eligible record outside current retained resource')
    for rid,item in items.items():
        if rid in core:
            src=read(root/f'bugbank/sources/{rid}.json')
            for k in ('lines','gold','group','split','current_roles','reference_item_sha256'):
                require(src[k]==item[k],f'Resource/benchmark mismatch {rid} {k}')
            item['cluster_merged']=src['cluster_merged'];item['cluster']=src['cluster']
    views=read(root/'benchmark/views.json')['views'];settings=read(root/'benchmark/code/settings.json')
    require(len(views)==14 and len(settings['manuscript_views'])==13,'Configuration roster changed')
    outcomes={(x['view_id'],x['item_id']):x for x in lines(root/'benchmark/outcomes_derived.jsonl')}
    require(len(outcomes)==3850,'Outcome roster changed')
    selections=lines(root/'benchmark/selections.jsonl')
    require(len(selections)==3990,'Selection roster changed')
    usage_records_list=lines(root/'benchmark/accounting/selected_records.jsonl')
    usage_records={r['selected_record_sha256']:r for r in usage_records_list}
    require(len(usage_records)==len(usage_records_list),'Duplicate selected usage record')
    usage_joins=lines(root/'benchmark/accounting/selection_usage_join.jsonl')
    require({(r['view_id'],r['item_id'],r['selected_record_sha256']) for r in usage_joins}==
            {(r['view_id'],r['item_id'],r['selected_record_sha256']) for r in selections},'Usage-selection join mismatch')
    require(len(usage_joins)==len(selections),'Duplicate usage-selection joins')
    selected_usage={(r['view_id'],r['item_id']):usage_records[r['selected_record_sha256']] for r in usage_joins}
    seen=set();answer_cache={};replayed={}
    for s in selections:
        v,rid=s['view_id'],s['item_id'];key=(v,rid);require(key not in seen,'Duplicate saved selection');seen.add(key)
        raw_path=s['answer_file']
        require(not Path(raw_path).is_absolute() and '..' not in Path(raw_path).parts,'Unsafe answer path')
        if raw_path not in answer_cache:answer_cache[raw_path]=(root/public_path(raw_path)).read_bytes()
        raw=answer_cache[raw_path]
        require(hashlib.sha256(raw).hexdigest()==s['selected_answer_sha256'],'Answer hash mismatch')
        require(len(raw)==s['selected_answer_bytes'],'Answer bytes mismatch')
        visible=raw.decode('utf-8')
        if settings['visible_answer_rule'][v]=='after_last_closing_think_tag' and '</think>' in visible:
            visible=visible.split('</think>')[-1]
        require(hashlib.sha256(visible.encode()).hexdigest()==s['visible_answer_sha256'],'Visible answer mismatch')
        audit=parser.parse_candidates_audit(visible,{'record_id':rid,'split':items[rid]['split'],'lines':items[rid]['lines']})
        require(reproduce.sha(reproduce.canonical(audit))==s['candidate_parse_sha256'],'Parser audit mismatch')
        require(audit['candidates']==s['record']['candidates'],'Candidates mismatch')
        record=reproduce.restore_outcome_record(s,audit['candidates'])
        out=score.outcome(items[rid],record)
        if key in outcomes:
            projection={'view_id':v,'item_id':rid,**{k:out[k] for k in ('hit1','hit3','valid','cause','attempt_class')}}
            require(projection==outcomes[key],'Outcome mismatch')
            replayed[key]=projection
    require(replayed==outcomes,'Replayed outcome coverage differs')
    print(f'PASS: {len(selections)} saved selections reparsed; {len(answer_cache)} exact answer files; {len(replayed)} outcomes unchanged.',flush=True)
    primary={rid for rid,it in items.items() if it['current_roles']['evaluation_primary']}
    all_scored={rid for rid,it in items.items() if it['current_roles']['evaluation_scorable']}
    pilot={rid for rid,it in items.items() if it['current_roles']['pilot_scorable']}
    require(len(primary)==191 and len(all_scored)==255 and len(pilot)==20,'Original population changed')
    saved=read(root/'benchmark/aggregates.json')['populations']
    for pop,ids in [('primary_ge10_lines',primary),('secondary_scorable',all_scored),('pilot_scorable',pilot)]:
        for v in views:
            require(saved[v][pop]['denominator']==len(ids),'Original denominator changed')
            for metric in ('hit1','hit3'):
                require(sum(outcomes[(v,rid)][metric] for rid in ids)==saved[v][pop][metric]['numerator'],'Original aggregate changed')
            require(score.aggregate_usage([selected_usage[(v,rid)] for rid in ids])==saved[v][pop]['inference_usage'],
                    'Original selected-row usage differs')
    masks={'retained_original_primary':sorted((core&primary)-span_excluded),
           'retained_scorable_evaluation':sorted((core&all_scored)-span_excluded)}
    require(masks['retained_original_primary']==ledger['benchmark_clean_primary191_record_ids'],'Primary membership mask mismatch')
    require(masks['retained_scorable_evaluation']==ledger['benchmark_clean_all255_record_ids'],'Scorable membership mask mismatch')
    base={rid:score.baselines(items[rid]) for rid in all_scored}
    populations={}
    for name,ids in masks.items():
        require(bool(ids),'Empty retained benchmark intersection')
        its=[items[rid] for rid in ids];n=len(ids)
        pop={'denominator':n,'record_ids':ids,'groups':dict(collections.Counter(it['group'] for it in its)),
             'n_problem_clusters':len({it['cluster_merged'] for it in its}),'views':{},'baselines':{}}
        if line_review:
            q5=set();spans=set();uncleared=set()
            for rid in ids:
                lr=line_review['records'][rid]
                require(lr['current_gold']==items[rid]['gold'],'Line coverage ledger uses different current gold')
                if any(x['answer']=='YES' and x['source_array_exact'] and x['labels_exact'] for x in lr['optional_random_audit_Q5']):q5.add(rid)
                if any(x['clean_answer_pattern'] and x['matches_current_label_set'] for x in lr['separate_line_reviews']):spans.add(rid)
                if any(not x['clean_answer_pattern'] and x['matches_current_label_set'] for x in lr['separate_line_reviews']):uncleared.add(rid)
            require(not uncleared,'Current-label concern retained in scoring mask')
            pop['reference_line_review_coverage']={
                'optional_Q5_YES_exact_source_and_labels':{'n':len(q5),'record_ids':sorted(q5)},
                'separate_three_question_clean_current_label_set':{'n':len(spans),'record_ids':sorted(spans)},
                'union_positive_line_check':{'n':len(q5|spans),'record_ids':sorted(q5|spans)},
                'no_matching_positive_line_check_in_these_exports':{'n':len(set(ids)-q5-spans),'record_ids':sorted(set(ids)-q5-spans)},
                'scope':'Optional Q5 and complete three-question span review are different endpoints; separate-span exports bind labels and review-sheet hashes, but not complete reviewed source bytes.'}
        for baseline in base[ids[0]]:
            values=[base[rid][baseline] for rid in ids];total=sum(values)
            rr={'denominator':n,'mean':round(total/n,4),'percent':100*total/n,
                'expected_hits' if baseline=='random_line' else 'hits':total}
            if args.with_intervals:rr['ci95']=score.boot(its,values,name+baseline)
            pop['baselines'][baseline]=rr
        for v in views:
            outs=[outcomes[(v,rid)] for rid in ids]
            rr={'denominator':n,'main_table_configuration':v in settings['manuscript_views'],
                'reporting_scope':views[v]['reporting_scope'],
                'rule_misses_by_cause':dict(collections.Counter(o['cause'] for o in outs if o['cause']))}
            valid=[o for o in outs if o['valid']]
            rr['valid_answers']=len(valid)
            selected_records=[selected_usage[(v,rid)] for rid in ids]
            rr['selected_core_inference_usage']=score.aggregate_usage(selected_records)
            rr['selected_core_output_usage']=score.aggregate_output_usage(selected_records)
            rr['conditional_hit1']={'hits':sum(o['hit1'] for o in valid),'denominator':len(valid),
                'mean':round(sum(o['hit1'] for o in valid)/len(valid),4) if valid else None}
            for metric in ('hit1','hit3'):
                values=[o[metric] for o in outs];k=int(sum(values))
                rr[metric]={'hits':k,'denominator':n,'mean':round(k/n,4),'percent':100*k/n}
                if args.with_intervals:
                    rr[metric]['ci95']=score.boot(its,values,name+settings['seed_lane_identifiers'][v]+metric)
            pop['views'][v]=rr
        for metric in ('hit1','hit3'):
            best=max(r[metric]['hits'] for r in pop['views'].values() if r['main_table_configuration'])
            pop[metric+'_highest_observed']=[v for v,r in pop['views'].items() if r['main_table_configuration'] and r[metric]['hits']==best]
        deterministic={b:r for b,r in pop['baselines'].items() if b!='random_line'}
        best=max(r['hits'] for r in deterministic.values())
        pop['highest_observed_rule_baselines']=[b for b,r in deterministic.items() if r['hits']==best]
        populations[name]=pop
        print(name,n,pop['hit1_highest_observed'],pop['hit3_highest_observed'],flush=True)
    result={
      'schema':'copeer-public-human-approved-core-replay/v1',
      'status':'PASS',
      'eligibility_ledger_sha256':ledger_digest,'eligibility_ledger_filename':args.ledger.name,
      'reference_line_coverage_sha256':sha(args.line_review) if args.line_review else None,
      'eligible_record_ids':sorted(core),
      'membership':{'original_resource':284,'retained_resource':len(core),'removed_resource':284-len(core),
        'original_primary':191,'retained_original_primary':len((core&primary)-span_excluded),
        'original_scorable_evaluation':255,'retained_scorable_evaluation':len((core&all_scored)-span_excluded),
        'semantic_core_primary_before_span_exclusions':len(core&primary),
        'semantic_core_all_scorable_before_span_exclusions':len(core&all_scored),
        'current_span_concern_ids':sorted(span_excluded),
        'eligible_resource_ids_excluded_from_scoring_by_span_concerns':sorted(core&span_excluded),
        'retained_secondary_only':len(((core&all_scored)-primary)-span_excluded),'retained_pilot':len(core&pilot),
        'retained_unscorable':len(core-all_scored-pilot),
        'retained_pilot_ids':sorted(core&pilot),'retained_unscorable_ids':sorted(core-all_scored-pilot)},
      'populations':populations,
      'interval_method':{'computed':args.with_intervals,'resamples':score.RESAMPLES if args.with_intervals else None,
        'function':'frozen_score.boot','group_stratification':'source group','cluster':'cluster_merged',
        'seed':'SHA256(population_name + saved_seed_lane_identifier + metric), frozen seed_for implementation',
        'scope':'Cluster-resampling variability within this selected retained dataset; not an interval for reviewer error or general mathematical criticism.'},
      'validation':{'saved_selections_reparsed':len(selections),'exact_answer_files':len(answer_cache),
        'unchanged_outcomes':len(replayed),'original_191_255_20_aggregates_verified':True,
        'membership_certificate_hashes_verified':len(release_bindings),
        'original_191_255_20_selected_usage_aggregates_verified':True,
        'retained_resource_source_arrays_and_labels_verified':True,
        'public_membership_verification':membership_verification,'no_new_inference':True,'no_new_grading':True},
      'input_bindings':{p:sha(root/p) for p in ['bugbank/index.json','benchmark/items.jsonl','benchmark/views.json',
          'benchmark/selections.jsonl','benchmark/outcomes_derived.jsonl','benchmark/aggregates.json',
          'benchmark/accounting/selected_records.jsonl','benchmark/accounting/selection_usage_join.jsonl',
          'benchmark/code/frozen_score.py','benchmark/code/frozen_common.py','benchmark/code/settings.json']},
      'script_sha256':sha(Path(__file__)),
      'interpretation':[
        'Membership is specified by the bound eligibility ledger, independently of model predictions.',
        'All 13 configurations displayed in the prior main table are retained; the active Haiku view remains a separate archival reporting view.',
        'The original primary intersection preserves the original minimum-source-length rule. The all-scorable intersection also includes shorter secondary inputs and is reported separately.',
        'The eligibility ledger explicitly identifies current-span concerns excluded from both reported evaluation masks; resource-level semantic approval and reference-span approval remain separate.',
        'The two Haiku views reuse physical calls; no additional model configuration or token total is implied.',
        'Usage totals include exactly the selected core rows in each displayed reporting view. Observed usage lower bounds, complete measured usage, and budget charges remain distinct fields; historical campaign-wide totals are not substituted.',
        'Saved score rules count operational failures as misses. Conditional rates use different model-specific subsets.',
        'These results neither establish external reviewer independence nor relabel AI-only judgments as human judgments.'
      ]}
    expected=read(HERE/'expected_scores.json')
    def without_intervals(value):
        if isinstance(value,dict):return {k:without_intervals(v) for k,v in value.items() if k!='ci95'}
        if isinstance(value,list):return [without_intervals(v) for v in value]
        return value
    actual_numeric={k:result[k] for k in ('membership','populations')}
    expected_numeric={k:expected[k] for k in ('membership','populations')}
    if not args.with_intervals:
        actual_numeric=without_intervals(actual_numeric)
        expected_numeric=without_intervals(expected_numeric)
    require(actual_numeric==expected_numeric,'Public numeric results differ from accepted results')
    result['accepted_scientific_result_sha256']=expected['accepted_scientific_result_sha256']
    result['matches_accepted_numeric_results']=True
    require(sha(args.ledger)==ledger_digest,'Membership ledger changed during scoring')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS: '+str(args.output),flush=True)

if __name__=='__main__':main()
