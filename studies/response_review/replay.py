#!/usr/bin/env python3
"""Check distributed evidence and replay the saved Experiment B analysis offline."""
import collections
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent


def load(name):
    return json.loads((HERE / name).read_text())


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evidence_class(value):
    if value in ('VERIFIED_VALID_KERNEL', 'VERIFIED_VALID_EXACT', 'ANALYTIC_VALID'):
        return 'VALID'
    if value == 'INVALID':
        return 'INVALID'
    return 'UNRESOLVED_OR_INSUFFICIENT'


def review_values(reader, packet):
    data = load(f'readings/{reader}/{packet}.json')
    j3 = data.get('J3_evidence_check') or {}
    values = {'reader': reader, 'confidence': data.get('confidence'),
              'minutes': data.get('minutes'), 'tooling_failure': j3.get('tooling_failure'),
              'lean_attempts': j3.get('lean_attempts')}
    for label, key in [('J1','J1_line_asserts_challenged_proposition'),
                       ('J2','J2_evidence_specified'), ('J3','J3_evidence_check'),
                       ('J4','J4_consequence_overreach')]:
        values[label] = (data.get(key) or {}).get('value')
    return values


def main():
    manifest = load('MANIFEST.json')
    for f in manifest['files']:
        need(digest(HERE / f['path']) == f['sha256'], 'Distributed file drift: '+f['path'])
    packets = load('PACKETS_MANIFEST.json')['packets']
    need(len(packets) == 48, 'Expected 48 packets')
    for pid, packet in packets.items():
        need(digest(HERE/'packets'/f'{pid}.md') == packet['sha256'], 'Packet drift: '+pid)
    locks = load('READING_LOCKS.json')['readings']
    need(len(locks) == 104, 'Expected 96 original reviews plus 8 adjudications')
    for row in locks:
        need(row['matched_last_original_log_entry'], 'Original lock mismatch')
        need(digest(HERE/row['path']) == row['distributed_sha256'], 'Reading drift: '+row['path'])

    freeze = load('B_SAMPLE_FREEZE.json')
    commit = load('B_COMMITMENT.json')
    seed = commit['seed']['sha256_prefix16']
    need(hashlib.sha256(commit['seed']['string'].encode()).hexdigest()[:16] == seed, 'Sampling commitment drift')
    population = load('PRIMARY_POPULATION_IDS.json')
    need(len(population) == 191 and population == sorted(set(population)), 'Primary population mismatch')
    need(random.Random(int(seed, 16)).sample(population,24) == freeze['drawn_record_ids_in_order'], 'Sample draw mismatch')

    roles = collections.defaultdict(dict)
    for reader, assignment in load('READER_ASSIGNMENT_PLAN.json')['readers'].items():
        for role, field in [('reader1','first_reader_packets'), ('reader2','second_reader_packets')]:
            for pid in assignment[field]:
                need(role not in roles[pid], 'Duplicate review role')
                roles[pid][role] = reader
    need(set(roles) == set(packets), 'Review coverage mismatch')
    refs = {r['record_id']:r for r in load('REFERENCE_ITEMS_SAMPLE.json')['items']}
    runtimes = {}
    for cfg, binding in load('FROZEN_FUNCTIONS.json').items():
        path = HERE/binding['path']
        need(digest(path) == binding['sha256'], 'Frozen functions drift')
        spec = importlib.util.spec_from_file_location('frozen_'+str(len(runtimes)),path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        runtimes[cfg] = module

    results = load('B_RESULTS_v1.json')
    published = {r['packet_id']:r for r in results['records']}
    rows = []; parser_metadata_differences = []
    for pair in freeze['pairs_public']:
        pid = pair['packet_id']; expected = published[pid]
        for key in ['record','answer']:
            need(digest(HERE/pair[key]['path']) == pair[key]['sha256'], 'Attempt drift: '+pid)
        rec = load(pair['record']['path'])
        answer = (HERE/pair['answer']['path']).read_text()
        item = refs[pair['record_id']]
        runtime = runtimes[pair['configuration']]
        parsed = runtime.parse_candidates_audit(answer,item)
        for key in ['raw_candidates','candidates','slot_audit','parse_reason']:
            need(parsed.get(key) == rec['candidate_parse'].get(key), 'Frozen parser selection mismatch: '+pid+' '+key)
        metadata_diff = {k:{'recorded':rec['candidate_parse'].get(k),'replayed':parsed.get(k)}
                         for k in set(parsed)|set(rec['candidate_parse'])
                         if parsed.get(k) != rec['candidate_parse'].get(k)}
        if metadata_diff:
            parser_metadata_differences.append({'packet_id':pid,'differences':metadata_diff})
        need(parsed['candidates'] == rec['candidates'], 'Frozen candidates mismatch: '+pid)
        outcome = runtime.outcome(item,rec)
        for key in ['hit1','hit3']:
            need(int(outcome[key]) == expected[key+'_frozen_rule'], 'Frozen score mismatch: '+pid)
        row = copy.deepcopy(expected)
        for role in ['reader1','reader2']:
            values = review_values(roles[pid][role],pid)
            need(values == expected[role], 'Review/assigned-role mismatch: '+pid+' '+role)
            row[role] = values
        row['primary_evidence_class'] = evidence_class(row['reader1']['J3'])
        row['readers_agree_J3_class'] = evidence_class(row['reader1']['J3']) == evidence_class(row['reader2']['J3'])
        row['readers_agree_J3_exact'] = row['reader1']['J3'] == row['reader2']['J3']
        need(row == expected, 'Recorded row mismatch: '+pid)
        rows.append(row)
    need(len(rows) == 48, 'Expected 48 scored responses')

    tables = {}; agreement = {}; diagnostics = {j:{} for j in ['J1','J2','J3','J4']}
    valid_misses = {}; unsupported_hits = {}
    for cfg in commit['configurations']:
        sub = [r for r in rows if r['configuration'] == cfg]
        need(len(sub) == 24, 'Expected 24 outputs per configuration')
        tables[cfg] = {key:dict(collections.Counter(r['primary_evidence_class'] for r in sub
                           if bool(r['hit1_frozen_rule']) == (key=='hit1'))) for key in ['hit1','miss']}
        agreement[cfg] = {'J3_class_agree':sum(r['readers_agree_J3_class'] for r in sub),
                          'J3_exact_agree':sum(r['readers_agree_J3_exact'] for r in sub), 'n':len(sub)}
        for j in diagnostics:
            diagnostics[j][cfg] = dict(collections.Counter(r['reader1'][j] for r in sub))
        valid_misses[cfg] = sum(not r['hit1_frozen_rule'] and r['primary_evidence_class']=='VALID' for r in sub)
        unsupported_hits[cfg] = sum(r['hit1_frozen_rule'] and r['primary_evidence_class']!='VALID' for r in sub)
    need(tables == results['primary_table_hit1_by_evidence_class_first_reader'], 'Primary table mismatch')
    need(agreement == results['secondary_reader_agreement'], 'Agreement table mismatch')
    for j in diagnostics:
        field = 'J3_exact_values_first_reader' if j=='J3' else j+'_first_reader'
        need(diagnostics[j] == results[field], field+' mismatch')
    need(valid_misses == results['valid_objections_among_misses_first_reader'], 'Valid miss count mismatch')
    need(unsupported_hits == results['hits_without_valid_evidence_first_reader'], 'Unsupported hit count mismatch')
    need(sum(bool(r[k]['tooling_failure']) for r in rows for k in ['reader1','reader2']) == results['tooling_failures'], 'Tooling tally mismatch')
    need(sum(r[k]['minutes'] or 0 for r in rows for k in ['reader1','reader2'] if isinstance(r[k]['minutes'],(int,float))) == results['reader_minutes_total'], 'Reader minutes mismatch')
    sensitivity = copy.deepcopy(tables)
    cfg = published['P31']['configuration']
    need(published['P31']['hit1_frozen_rule']==1 and published['P31']['primary_evidence_class']=='VALID','P31 baseline mismatch')
    sensitivity[cfg]['hit1']['VALID'] -= 1
    sensitivity[cfg]['hit1']['INVALID'] += 1
    need(sensitivity[cfg]['hit1']=={'VALID':15,'INVALID':3},'Source-assumptions view mismatch')
    print(json.dumps({'status':'PASS','distributed_files_checked':len(manifest['files']),
          'packets':48,'readings_and_adjudications_locked':104,'sample_draw_reproduced':True,
          'frozen_parser_and_score_replayed':48,'first_review_tables':tables,
          'parser_metadata_differences':parser_metadata_differences,
          'reader_agreement':agreement,
          'separate_source_assumptions_nemotron_hit_view':sensitivity[cfg]['hit1']},indent=2))


if __name__ == '__main__':
    main()
