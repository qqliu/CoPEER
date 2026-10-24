#!/usr/bin/env python3
"""Freeze existing evidence and render the two 50-task studies; never run models.

Use --capture once for a new dated snapshot, then rerun without it to reproduce
the tables and figure from that snapshot. Native reasoning counts are subsets
of output; cached input is separated before summing; auxiliary models count.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import random

PAPER = Path(__file__).resolve().parents[1]
REPO = PAPER.parents[1]
RUNS = REPO / 'qedbench_certificate_availability_triage/runs'
PROOF = RUNS / 'proof_construction_repro_20260916'
LEAN = RUNS / 'lean_cert_repro_20260916'
SNAPSHOT = PAPER / 'generated/studies50_snapshot_20260917.json.gz'
COMPLETION = PAPER / 'generated/proof50_grade_completion_20260917.json'
MODELS = {'sol': 'GPT-5.6 Sol', 'gemini': 'Gemini 3.1 Pro', 'opus': 'Claude Opus 5'}
PROTOCOLS = [('shared', 'Shared rule', 'bugbank_parity', 'plain_parity'),
             ('original', 'Original', 'bugbank_orig', 'plain_orig')]
PROOF_ARMS = {a for _, _, a, b in PROTOCOLS for a in (a, b)}
LEAN_ARMS = ['plain', 'bugbank', 'mathlib']
COMPONENTS = ['input_uncached', 'cache_creation', 'cache_read', 'output']


def digest(data):
    return hashlib.sha256(data).hexdigest()


def native_usage(raw):
    """Return disjoint components; no receipt or failed zero receipt is unknown."""
    engine = raw.get('engine')
    auxiliary = 0
    if engine == 'claude':
        models = raw.get('modelUsage') or {}
        if not models:
            return None
        parts = {'input_uncached': 0, 'cache_creation': 0, 'cache_read': 0, 'output': 0}
        reasoning = 0
        for model, u in models.items():
            v = dict(zip(COMPONENTS, [u.get('inputTokens', 0), u.get('cacheCreationInputTokens', 0),
                                     u.get('cacheReadInputTokens', 0), u.get('outputTokens', 0)]))
            if model != 'claude-opus-5':
                auxiliary += sum(v.values())
            for k in COMPONENTS:
                parts[k] += v[k]
            reasoning += u.get('thinkingTokens', 0)
    elif engine == 'codex':
        u = raw.get('usage_total') or {}
        if not all(k in u and u[k] is not None for k in ['input_tokens', 'output_tokens']):
            return None
        cached = u.get('cached_input_tokens') or 0
        parts = dict(zip(COMPONENTS, [u['input_tokens'] - cached, 0, cached, u['output_tokens']]))
        reasoning = u.get('reasoning_output_tokens')
    elif engine == 'agy':
        u = raw.get('usage') or {}
        if not all(k in u and u[k] is not None for k in ['input_tokens', 'output_tokens']):
            return None
        parts = dict(zip(COMPONENTS, [u['input_tokens'], 0, u.get('cache_read_tokens') or 0, u['output_tokens']]))
        reasoning = u.get('thinking_tokens')
    else:
        return None
    assert all(isinstance(v, int) and v >= 0 for v in parts.values()), parts
    total = sum(parts.values())
    if not total and raw.get('status', raw.get('exit_code')) != 0:
        return None
    return {**parts, 'total': total, 'reasoning_within_output': reasoning,
            'auxiliary_within_total': auxiliary}


def capture():
    sources = {}

    def read(p):
        data = p.read_bytes()
        try:
            name = str(p.relative_to(REPO))
        except ValueError:
            name = str(p)
        sources[name] = digest(data)
        return data

    def usage_receipt(p):
        if not p.exists():
            return {'path': str(p), 'missing': True, 'tokens': None}
        data = read(p)
        u = json.loads(data)
        # Keep native accounting and identity fields, never credentials/log prose.
        keys = ['engine', 'requested_model', 'requested_effort', 'init_model', 'status',
                'exit_code', 'result_status', 'modelUsage', 'bound_model_usage',
                'usage_total', 'usage', 'output_tokens_bound_model']
        raw = {k: u[k] for k in keys if k in u}
        return {'path': str(p), 'sha256': digest(data), 'raw': raw, 'tokens': native_usage(raw)}

    now = datetime.now(timezone.utc).isoformat()
    data = {'schema': 'fifty-task-paper-snapshot/1', 'captured_at_utc': now,
            'scope': {'proof_tasks': 50, 'proof_cells': 600, 'lean_tasks': 50, 'lean_cells': 450},
            'proof': {}, 'lean': {}, 'sources': sources}
    proof_plan = json.loads(read(PROOF / 'plan.json'))
    data['proof_roster'] = proof_plan['record_order']
    assert len(data['proof_roster']) == len(set(data['proof_roster'])) == 50
    roster = json.loads(read(LEAN / 'E2/ROSTER.json'))
    assert roster['status'] == 'FROZEN' and len(roster['tasks']) == 50
    data['lean_roster'] = roster
    for task in roster['tasks']:
        p = REPO / task['file']
        if not p.exists():
            p = LEAN / 'E2/src/E2Frozen' / Path(task['file']).name
        assert digest(read(p)) == task['sha256'], task['record_id']
    lean_ids = {x['record_id'] for x in roster['tasks']}
    for model in MODELS:
        rows = [json.loads(line) for line in read(PROOF / f'telemetry/{model}.jsonl').decode().splitlines()]
        rows = [r for r in rows if r['arm'] in PROOF_ARMS]
        selected = {}
        attempts = []
        for r in rows:
            assert r['record_id'] in data['proof_roster']
            receipt = usage_receipt(Path(r['attempt_dir']) / 'usage.json')
            attempts.append({'row': r, 'receipt': receipt})
            if r['status'] == 0:
                selected[(r['record_id'], r['arm'])] = {'row': r, 'receipt': receipt}
        endpoints = []
        for (rid, arm), r in sorted(selected.items()):
            draft_path = PROOF / f'drafts/{model}/{arm}/{rid}.json'
            draft = json.loads(read(draft_path))
            h = digest(draft['final_proof'].encode())
            grade_path = PROOF / f'grades/astra/{model}/{arm}/{rid}.json'
            grade = json.loads(read(grade_path)) if grade_path.exists() else None
            if grade:
                assert grade['draft_sha256'] == h, f'stale grade: {grade_path}'
                assert grade['grader_model'] == 'gpt-6-astra'
            endpoints.append({**r, 'draft_text_sha256': h, 'grade': grade})
        grader_receipts = []
        grade_root = Path('<workspace-home>/pc_repro_ops/grade/astra') / model
        for arm in sorted(PROOF_ARMS):
            for p in sorted((grade_root / arm).glob('*/usage*.json')):
                grader_receipts.append(usage_receipt(p))
        data['proof'][model] = {'endpoints': endpoints, 'attempts': attempts, 'grader_receipts': grader_receipts}
        cells = []
        for p in sorted((LEAN / 'cells' / model).glob('*.json')):
            cell = json.loads(read(p))
            if cell['arm'] not in LEAN_ARMS:
                continue
            assert cell['record_id'] in lean_ids
            if cell['accepted']:
                accepted = [r for r in cell['rounds'] if (r.get('audit') or {}).get('accepted')]
                assert len(accepted) == 1
                r = accepted[0]
                audit = r['audit']
                assert r['lean_rc'] == 0 and audit['audit_rc'] == 0
                assert all(audit[k] for k in ['type_match', 'candidate_is_theorem', 'axioms_standard', 'imports_ok', 'replay_ok'])
                assert not audit['unsafe_or_partial'] and not audit['declares_axiom_or_opaque']
                source = Path(cell['cell_dir']) / f"attempt_{r['attempt']}" / 'candidate.lean'
                assert digest(read(source)) == r['candidate_sha256'], source
                cell['accepted_candidate_evidence'] = {'path': str(source), 'sha256': r['candidate_sha256']}
            cells.append(cell)
        telemetry = [json.loads(line) for line in read(LEAN / f'telemetry/{model}.jsonl').decode().splitlines()]
        telemetry = [r for r in telemetry if r['arm'] in LEAN_ARMS]
        receipts = []
        for arm in LEAN_ARMS:
            for directory in sorted((Path('<workspace-home>/e2_ops') / model / arm).glob('*/attempt_*')):
                if not directory.is_dir():
                    continue
                p = directory / 'usage.json'
                if p.parents[1].name.split('__infra_')[0] not in lean_ids:
                    continue
                receipts.append({'arm': arm, 'record_id': p.parents[1].name.split('__infra_')[0],
                                 'archived': '__infra_' in p.parents[1].name, **usage_receipt(p)})
        data['lean'][model] = {'cells': cells, 'telemetry': telemetry, 'usage_receipts': receipts}
    SNAPSHOT.write_bytes(gzip.compress((json.dumps(data, sort_keys=True) + '\n').encode(), mtime=0))
    return data


def load_completed_data():
    """Apply only the four newly sealed grades; preserve the historical snapshot."""
    data = json.loads(gzip.decompress(SNAPSHOT.read_bytes()))
    if COMPLETION.exists():
        supplement = json.loads(COMPLETION.read_bytes())
        assert supplement['base_snapshot_sha256'] == digest(SNAPSHOT.read_bytes())
        assert len(supplement['entries']) == 4
        for item in supplement['entries']:
            grade = item['grade']
            endpoint = next(e for e in data['proof']['opus']['endpoints']
                            if e['row']['arm'] == grade['arm_key'] and e['row']['record_id'] == grade['record_id'])
            assert endpoint['grade'] is None and endpoint['draft_text_sha256'] == grade['draft_sha256']
            assert grade['grader_model'] == 'gpt-6-astra' and grade['reasoning_effort'] == 'max'
            endpoint['grade'] = grade
            report = item['report']
            raw = {'engine': 'codex', 'status': 0, 'usage_total': report['usage']}
            data['proof']['opus']['grader_receipts'].append({'path': item['report_path'],
                'sha256': item['report_sha256'], 'raw': raw, 'tokens': native_usage(raw)})
        data['proof_grades_completed_at_utc'] = supplement['completed_at_utc']
        data['proof_grade_completion_sha256'] = digest(COMPLETION.read_bytes())
    return data


def additional_attempt_costs(pd):
    """A rerun can reuse a path: failed telemetry rows still count as attempts."""
    chosen = {r['row']['attempt_dir'] for r in pd['endpoints']}
    failed = [x for x in pd['attempts'] if x['row']['status'] != 0]
    receipts = []
    primary_lower_bound = 0
    for x in failed:
        receipt = x['receipt']
        if x['row']['attempt_dir'] in chosen:
            receipt = {'tokens': None, 'reason': 'Native path overwritten by successful rerun'}
        receipts.append(receipt)
        if receipt['tokens'] is None:
            u = x['row']['usage']
            # Native helper details may be absent, but nonzero historical primary
            # telemetry is still a measured lower bound, never a reconstructed zero.
            primary_lower_bound += sum(u.get(k) or 0 for k in ['input_uncached', 'input_cache_read', 'output_tokens'])
    result = sum_usage(receipts)
    result['native_known_total'] = result['total']
    result['historical_primary_only_lower_bound'] = primary_lower_bound
    result['total'] += primary_lower_bound
    result['total_is_lower_bound'] = bool(result['unknown'])
    result['component_totals_cover_native_receipts_only'] = True
    return result


def sum_usage(receipts):
    known = [r['tokens'] for r in receipts if r['tokens'] is not None]
    return {**{k: sum(r[k] for r in known) for k in COMPONENTS + ['total', 'auxiliary_within_total']},
            'receipts': len(receipts), 'unknown': len(receipts) - len(known)}


def bootstrap(a, b):
    assert len(a) == len(b)
    if not a or not sum(b):
        return None
    rng = random.Random(20260916)
    n = len(a)
    draws = []
    for _ in range(2000):
        idx = [rng.randrange(n) for _ in range(n)]
        denominator = sum(b[i] for i in idx)
        if denominator:
            draws.append(sum(a[i] for i in idx) / denominator)
    draws.sort()
    return [sum(a)/sum(b), draws[int(.025*len(draws))], draws[int(.975*len(draws))-1]]


def summarize(data):
    result = {'captured_at_utc': data['captured_at_utc'], 'snapshot_sha256': digest(SNAPSHOT.read_bytes()),
              'proof': [], 'lean': [], 'lean_pairs': [], 'costs': []}
    for key in ['proof_grades_completed_at_utc', 'proof_grade_completion_sha256']:
        if key in data:
            result[key] = data[key]
    for model in MODELS:
        pd = data['proof'][model]
        endpoints = {(x['row']['record_id'], x['row']['arm']): x for x in pd['endpoints']}
        for key, label, a, b in PROTOCOLS:
            ids = sorted(rid for rid in data['proof_roster'] if (rid, a) in endpoints and (rid, b) in endpoints)
            graded = [rid for rid in ids if endpoints[(rid, a)]['grade'] and endpoints[(rid, b)]['grade']]
            row = {'model': model, 'protocol': key, 'n_pairs': len(ids), 'n_graded_pairs': len(graded)}
            for tag, arm in [('bugbank', a), ('plain', b)]:
                selected = [endpoints[(rid, arm)] for rid in ids]
                row[tag] = {'correct': sum(endpoints[(rid, arm)]['grade']['correctness'] == 'CORRECT' for rid in graded),
                            'tokens': sum_usage([x['receipt'] for x in selected]),
                            'primary_output': sum(x['row']['usage']['output_tokens'] for x in selected)}
            row['output_ratio'] = bootstrap([endpoints[(rid, a)]['row']['usage']['output_tokens'] for rid in ids],
                                            [endpoints[(rid, b)]['row']['usage']['output_tokens'] for rid in ids])
            assert all(endpoints[(rid, arm)]['receipt']['tokens'] is not None for rid in ids for arm in [a, b])
            row['full_ratio'] = bootstrap([endpoints[(rid, a)]['receipt']['tokens']['total'] for rid in ids],
                                          [endpoints[(rid, b)]['receipt']['tokens']['total'] for rid in ids])
            result['proof'].append(row)
        result['costs'].append({'study': 'proof', 'model': model, 'category': 'additional attempts', **additional_attempt_costs(pd)})
        result['costs'].append({'study': 'proof', 'model': model, 'category': 'grading', **sum_usage(pd['grader_receipts'])})
        ld = data['lean'][model]
        by_id = {(x['record_id'], x['arm']): x for x in ld['cells']}
        for arm in LEAN_ARMS:
            cells = [x for x in ld['cells'] if x['arm'] == arm]
            accepted = sum(x['accepted'] for x in cells)
            infra = sum(x['infra_failed'] for x in cells)
            exhausted = sum(not x['accepted'] and not x['infra_failed'] for x in cells)
            assert accepted + infra + exhausted == len(cells)
            receipts = [x for x in ld['usage_receipts'] if x['arm'] == arm]
            result['lean'].append({'model': model, 'arm': arm, 'accepted': accepted,
                                   'exhausted': exhausted, 'infra': infra, 'pending': 50-len(cells),
                                   'terminal': accepted+exhausted, 'tokens': sum_usage(receipts)})
        ids = sorted(x['record_id'] for x in data['lean_roster']['tasks'])
        paired = [r for r in ids if all((r, a) in by_id and not by_id[(r,a)]['infra_failed'] for a in ['bugbank','plain'])]
        both = [r for r in paired if all(by_id[(r,a)]['accepted'] for a in ['bugbank','plain'])]
        result['lean_pairs'].append({'model': model, 'terminal_pairs': len(paired), 'both_certified': len(both),
                                     'bugbank_certified': sum(by_id[(r,'bugbank')]['accepted'] for r in paired),
                                     'plain_certified': sum(by_id[(r,'plain')]['accepted'] for r in paired),
                                     'output_ratio': bootstrap([by_id[(r,'bugbank')]['output_tokens_to_accept'] for r in both],
                                                               [by_id[(r,'plain')]['output_tokens_to_accept'] for r in both])})
    return result


def interval(value):
    return '--' if value is None else f'{value[0]:.3f} [{value[1]:.3f}, {value[2]:.3f}]'


def render_tables(result):
    rows = [r'\begin{table}[htbp]', r'\centering\scriptsize',
            r'\caption{Proof development on 50 problems per model. Each row compares BugBank (B) with plain review (P). Costs use all 50 completed pairs; correctness uses only pairs with both independent Astra grades. Full tokens include auxiliary models. Ratios are B/P with 95\% task-bootstrap intervals.}',
            r'\label{tab:proof50-results}', r'\begin{tabular}{llrrll}', r'\toprule',
            r'Model & Rule & Graded pairs & Correct B/P & Output ratio [95\% CI] & Full ratio [95\% CI] \\', r'\midrule']
    for x in result['proof']:
        rows.append(f"{MODELS[x['model']]} & {x['protocol'].capitalize()} & {x['n_graded_pairs']}/50 & {x['bugbank']['correct']}/{x['plain']['correct']} & {interval(x['output_ratio'])} & {interval(x['full_ratio'])} " + r'\\')
    rows += [r'\bottomrule', r'\end{tabular}', r'\end{table}', '', r'\begin{table}[htbp]', r'\centering\scriptsize',
             r'\caption{Exact solver-token sums on the 50 completed proof-development pairs, including auxiliary-model usage. Input excludes separately listed cache creation and cache reads. Reasoning is already included in output. Failed/additional attempts and grading are listed separately below.}',
             r'\label{tab:proof50-tokens}', r'\begin{tabular}{lllrrrrr}', r'\toprule',
             r'Model & Rule & Arm & Input & Cache creation & Cache read & Output & Total \\', r'\midrule']
    for x in result['proof']:
        for arm in ['plain', 'bugbank']:
            u = x[arm]['tokens']
            rows.append(' & '.join([MODELS[x['model']], x['protocol'].capitalize(), arm.capitalize()] + [f'{u[k]:,}' for k in COMPONENTS+['total']]) + r' \\')
    rows += [r'\bottomrule', r'\end{tabular}', r'\end{table}', '', r'\begin{table}[htbp]', r'\centering\small',
             r'\caption{Operational Lean-certificate counts at the fixed snapshot, not protocol-eligibility counts. Each row has 50 planned tasks. Acceptance passes type/axiom/kernel checks but includes one post-cap acceptance; 15 Gemini stopped episodes have infrastructure-contaminated budgets. See the audit caveats in Appendix~\ref{app:fifty-task-studies}.}',
             r'\label{tab:lean50-progress}', r'\begin{tabular}{llrrrr}', r'\toprule',
             r'Model & Arm & Accepted & Exhausted & Infra. & No summary \\', r'\midrule']
    for x in result['lean']:
        rows.append(' & '.join([MODELS[x['model']], x['arm'].capitalize()] + [str(x[k]) for k in ['accepted','exhausted','infra','pending']]) + r' \\')
    rows += [r'\bottomrule',r'\end{tabular}',r'\end{table}', '', r'\begin{table}[htbp]',r'\centering\small',
             r'\caption{Descriptive Lean runner-terminal pair counts. A terminal file is not necessarily a clean mathematical outcome: failed attempts affected stopping budgets, and one acceptance is post-cap. Inferential token ratios are withheld pending a per-cell protocol audit. These counts are not final comparative estimates.}',
             r'\label{tab:lean50-pairs}',r'\begin{tabular}{lrrrl}',r'\toprule',
             r'Model & Terminal pairs & Accepted B/P & Both accepted & Output ratio [95\% CI] \\',r'\midrule']
    for x in result['lean_pairs']:
        rows.append(f"{MODELS[x['model']]} & {x['terminal_pairs']} & {x['bugbank_certified']}/{x['plain_certified']} & {x['both_certified']} & Withheld " + r'\\')
    rows += [r'\bottomrule',r'\end{tabular}',r'\end{table}', '', r'\begin{table}[htbp]',r'\centering\scriptsize',
             r'\caption{Observed Lean solver-token spend, including archived retries, failed attempts with receipts, and attempts without terminal cell summaries. Totals include auxiliary models. Unknown-usage attempts are counted separately: displayed sums are lower bounds where usage is missing. This is campaign spend, not the paired tokens-to-acceptance endpoint.}',
             r'\label{tab:lean50-tokens}',r'\begin{tabular}{llrrrrrr}',r'\toprule',
             r'Model & Arm & Input & Cache creation & Cache read & Output & Known total & Unknown \\',r'\midrule']
    for x in result['lean']:
        u=x['tokens']
        rows.append(' & '.join([MODELS[x['model']],x['arm'].capitalize()]+[f'{u[k]:,}' for k in COMPONENTS+['total','unknown']])+r' \\')
    rows += [r'\bottomrule',r'\end{tabular}',r'\end{table}', '',r'\begin{table}[htbp]',r'\centering\small',
             r'\caption{Additional proof-development costs, excluded from the successful-attempt comparison. Failed attempts are identified by telemetry status even if their paths were reused. Known token lower bounds combine retained native receipts (including auxiliary models) and surviving primary-model telemetry for overwritten receipts. Unknown full usage is not imputed as zero. The four completion grades add 8,356 tokens.}',
             r'\label{tab:proof50-additional-costs}',r'\begin{tabular}{llrrr}',r'\toprule',
             r'Model & Category & Attempts/receipts & Known tokens & Unknown full usage \\',r'\midrule']
    for x in result['costs']:
        rows.append(f"{MODELS[x['model']]} & {x['category'].capitalize()} & {x['receipts']} & {x['total']:,} & {x['unknown']} " + r'\\')
    rows += [r'\bottomrule',r'\end{tabular}',r'\end{table}']
    (PAPER/'generated/studies50_tables_20260917.tex').write_text('\n'.join(rows)+'\n')


def render_plot(result):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 9, 'pdf.fonttype': 42, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(2, 2, figsize=(12, 7.2))
    colors={'plain':'#9DAEC1','bugbank':'#176B80'}
    for col,(protocol,title,_,_) in enumerate(PROTOCOLS):
        selected=[x for x in result['proof'] if x['protocol']==protocol]
        for i,x in enumerate(selected):
            for arm,shift in [('plain',-.18),('bugbank',.18)]:
                count=x[arm]['correct']; n=x['n_graded_pairs']; u=x[arm]['tokens']
                axes[0,col].barh(i+shift,100*count/n,height=.3,color=colors[arm],label=arm.capitalize() if i==0 else None)
                axes[0,col].text(100*count/n-2,i+shift,f'{count}/{n}',ha='right',va='center')
                total=u['total']; mean=total/x['n_pairs']/1000
                axes[1,col].barh(i+shift,mean,height=.3,color=colors[arm])
                axes[1,col].text(mean+4,i+shift,f'{mean:.1f}k; sum {total/1e6:.2f}M',va='center',fontsize=8)
        for row in range(2):
            axes[row,col].set_yticks(range(3),[MODELS[x['model']] for x in selected]);axes[row,col].invert_yaxis()
            axes[row,col].grid(axis='x',alpha=.15);axes[row,col].set_axisbelow(True)
        axes[0,col].set(title=title,xlim=(0,105),xlabel='Correct among independently graded pairs (%)')
        maximum=max(x[a]['tokens']['total']/50/1000 for x in selected for a in colors)
        axes[1,col].set(xlim=(0,maximum*1.72),xlabel='Full solver tokens per completed draft (thousands)')
    handles, names = axes[0,1].get_legend_handles_labels()
    names = ['BugBank' if x == 'Bugbank' else x for x in names]
    fig.legend(handles, names, loc='upper center', bbox_to_anchor=(.5,.94), ncol=2, frameon=False)
    fig.suptitle('50-problem proof development: grades and full token usage',fontsize=15)
    fig.text(.02,.015,'50 completed and graded pairs per model and rule. Full tokens include auxiliary models, cache creation/read and reasoning.\nSuccessful-attempt costs shown; additional attempts and grading costs are separate. Solver snapshot: '+result['captured_at_utc'][:16]+' UTC; grades complete 05:04 UTC.',fontsize=8)
    fig.tight_layout(rect=[0,.07,1,.90])
    for ext in ['pdf','png']:
        fig.savefig(PAPER/f'figures/proof_development_frontier_20260917.{ext}',dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(14, 7.3), gridspec_kw={'width_ratios':[1.5,1]})
    labels=[MODELS[x['model']]+' / '+({'bugbank':'BugBank'}.get(x['arm'],x['arm'].capitalize())) for x in result['lean']]
    for i,x in enumerate(result['lean']):
        left=0
        for key,name,color in [('accepted','Kernel accepted','#176B80'),('exhausted','Runner stopped, no proof','#9DAEC1'),
                               ('infra','Infrastructure failure','#E2A348'),('pending','No terminal summary','#EDF0F4')]:
            v=x[key]
            axes[0].barh(i,v,left=left,color=color,label=name if i==0 else None,height=.7)
            if v>=4:
                axes[0].text(left+v/2,i,str(v),ha='center',va='center',fontsize=9,
                             color='white' if key=='accepted' else '#172033')
            left+=v
        assert left==50
        u=x['tokens']; value=u['total']/1e6
        axes[1].barh(i,value,color='#788BA3',height=.7)
        axes[1].text(value+.3,i,f"{value:.2f}M"+(' + unknown' if u['unknown'] else ''),va='center',fontsize=9)
    axes[0].set(yticks=range(9),yticklabels=labels,xlim=(0,50),xlabel='Tasks per model and arm (50 planned)',title='Execution and kernel-acceptance status')
    axes[1].set(yticks=range(9),yticklabels=[],xlim=(0,max(x['tokens']['total']/1e6 for x in result['lean'])*1.5),
                xlabel='Known full solver tokens (millions)',title='Observed spend, including failed attempts')
    for ax in axes:
        ax.invert_yaxis();ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
    handles,names=axes[0].get_legend_handles_labels()
    fig.legend(handles,names,loc='lower center',bbox_to_anchor=(.5,.06),ncol=4,frameon=False)
    fig.suptitle('50-task Lean certificates: unfinished experiment',fontsize=16)
    fig.text(.02,.015,'Operational counts only: 15 Gemini stopped cells have infrastructure-contaminated budgets; one kernel acceptance is post-cap.\nFull tokens include auxiliary models and archived retries; missing usage remains unknown. Snapshot: '+result['captured_at_utc'][:16]+' UTC.',fontsize=8)
    fig.tight_layout(rect=[0,.12,1,.95])
    for ext in ['pdf','png']:
        fig.savefig(PAPER/f'figures/lean50_progress_20260917.{ext}',dpi=180)
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture',action='store_true')
    args=parser.parse_args()
    data=capture() if args.capture else load_completed_data()
    result=summarize(data)
    (PAPER/'generated/studies50_results_20260917.json').write_text(json.dumps(result,indent=2)+'\n')
    render_tables(result)
    render_plot(result)
    print(json.dumps({'captured_at_utc':result['captured_at_utc'],
                      'proof_pairs':[(x['model'],x['protocol'],x['n_pairs'],x['n_graded_pairs']) for x in result['proof']],
                      'lean':[{k:x[k] for k in ['model','arm','accepted','exhausted','infra','pending']} for x in result['lean']]},indent=2))


if __name__=='__main__':
    main()
