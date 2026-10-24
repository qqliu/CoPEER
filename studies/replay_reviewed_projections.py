#!/usr/bin/env python3
"""Check newly packaged scientific inputs and grading chronology, without running saved commands."""
from pathlib import Path
from collections import Counter
import hashlib,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent

def read(p):return json.loads(p.read_text())
def main():
    bindings=read(HERE/'reviewed_projection_bindings.json')
    for item in bindings['files']:
        p=ROOT/item['distributed']
        assert hashlib.sha256(p.read_bytes()).hexdigest()==item['distributed_sha256'],item['distributed']
    data=read(HERE/'instructions/reproduction/grader_cohort.json')
    early=data['historical_complete_rows'];later=data['later_complete_rows']
    cutoff=data['selection']['completed_at_or_before_utc']
    assert len(early)==1700 and len(later)==220
    assert all(r['t']<=cutoff for r in early) and all(r['t']>cutoff for r in later)
    assert sum(r['command_count']>0 for r in early)==6
    assert sum(r['command_count'] for r in early)==10
    assert sum(r['command_count']>0 for r in early+later)==7
    assert Counter(r['status'] for r in data['historical_noncomplete_rows'])=={'FAILED':6,'RATE_LIMITED':2}
    assert len({(r['set'],r['model'],r['cell']) for r in early+later})==1920
    for row in early+later:
        u=read(HERE/'instructions'/row['usage_receipt'])
        assert u['cell']==row['cell'] and u['attempt']==row['attempt']
        assert u['original_sha256']==row['original_usage_sha256']
        assert u['usage']['command_count']==row['command_count']==len(u['usage']['commands'])
    ledgers=[r for p in (HERE/'instructions/reproduction/grader_ledgers').glob('*.json') for r in read(p)['rows']]
    saved=early+later+data['historical_noncomplete_rows']+data['later_noncomplete_rows']
    key=lambda r:(r['original_ledger_source'],r['original_ledger_line'])
    assert sorted(ledgers,key=key)==sorted(saved,key=key)
    # The added original component analysis has all four instructions for all three models.
    full=read(HERE/'instructions/reference_validity/PROOFS100_FULL_COMPONENTS_CHECK.json')
    assert len(full['rows'])==12
    for row in full['rows']:
        records=[r for r in full['records'] if r['model']==row['model'] and r['arm']==row['arm']]
        assert len(records)==row['known_usage']
        for component in ['input_uncached_plus_creation','input_cache_read','output','full_tokens']:
            assert sum(r[component] for r in records)==row[component]
        assert row['full_tokens']==sum(row[k] for k in ['input_uncached_plus_creation','input_cache_read','output'])
    print(json.dumps({'status':'PASS','new_source_bindings':len(bindings['files']),'historical_completed_cells':1700,'historical_command_bearing_cells':6,'historical_command_invocations':10,'historical_noncomplete_attempts':8,'later_completed_cells':220,'final_completed_cells':1920,'final_command_bearing_cells':7,'all_instruction_component_rows':12,'saved_commands_executed':0,'scope':'The pause cohort is retrospectively reconstructed from recorded chronology, not an original prespecified freeze.'},indent=2))
if __name__=='__main__':main()
