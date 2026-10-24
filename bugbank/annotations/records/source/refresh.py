#!/usr/bin/env python3
"""Stage a ledger-bound documentation census, requiring explicit changed-row recoding.

Never edits the historical census, release, or manuscript. No human answers are
created. Ledger acceptance and annotation review are distinct recorded attestations.
"""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD = ROOT / 'qedbench_certificate_availability_triage/validation/human_review_20260915'
BASELINE = OLD / 'confirmed_release/ledger.json'
ANNOTATIONS = OLD / 'verified_census/annotations_current.json'
SUMMARY = OLD / 'verified_census/summary.json'
BASE30 = ROOT / 'astra/resource30_corrections_20260923/release_v2/ledger.json'
PINS = {
    BASELINE: 'd8e4028ab7d844520167b49d2d21846e7fea3945c9fee395e8198c5997d6afc4',
    ANNOTATIONS: 'bf321113344781ef4bf5fff563f1a91b04ffbce6791aa0600ee169ce55ac6424',
    SUMMARY: '4caf6a08721ebdb60ce8ffd813400d5e3e599e4c0a859c35ead6cd0a4fbb84b5',
    BASE30: 'a289be149ad458068cd27db33d2e61f7302ad7e7d22ba6fc5179bc4bec961a03',
}
FIELDS = ('problem', 'claim_quote', 'flaw', 'witness', 'explanation')
OBJECTS = {'graph': 'Graph', 'finite_combinatorial': 'Finite combinatorial',
           'numeric_algebraic': 'Numeric/algebraic', 'function_sequence': 'Function/sequence',
           'set_topology': 'Set/topology', 'probability': 'Probability',
           'algorithm_trace': 'Algorithm trace', 'other': 'Other'}
MECHANISMS = {'definition_scope': 'Definition/domain scope', 'quantifier_scope': 'Quantifier scope',
              'omitted_case': 'Omitted case', 'algebra_order': 'Algebra/order', 'counting': 'Counting',
              'structural_inference': 'Structural inference', 'analytic_inference': 'Analytic inference',
              'algorithm_invariant': 'Algorithm invariant', 'other': 'Other'}
PROPERTIES = {'family_documented': ('Family', 'Infinite family'),
              'repair_documented': ('Repair', 'Justified correction'),
              'nondegenerate_alternative_documented': ('Nondegenerate', 'Named restriction survives'),
              'exhaustive_domain_documented': ('Exhaustive', 'Bounded exhaustive search')}
EVIDENCE = ('mechanism_evidence', 'family_evidence', 'repair_evidence',
            'nondegenerate_evidence', 'exhaustive_evidence', 'minimality_evidence', 'role_evidence')


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digest(path):
    return sha(Path(path).read_bytes())


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode()


def value_sha(value):
    # Preserve the original census input-hash convention, including separators.
    return sha(json.dumps(value, sort_keys=True, ensure_ascii=False).encode())


def read(path):
    return json.loads(Path(path).read_text())


def unique(rows, key):
    need(isinstance(rows, list), 'Expected a row list')
    out = {}
    for row in rows:
        rid = row[key]
        need(isinstance(rid, str) and rid and rid not in out, 'Duplicate/invalid identifier: ' + str(rid))
        out[rid] = row
    return out


def fields(record):
    result = {k: record['current_fields'].get(k, '') for k in FIELDS}
    need(all(isinstance(v, str) for v in result.values()), 'Current fields must be strings')
    return result


def context(record):
    """Changes to source context, theorem/evidence or scope also require recoding."""
    return {
        'release_status': record['release_status'],
        'other_current_fields': {k: v for k, v in record['current_fields'].items() if k not in FIELDS},
        'corrected_scope_metadata': record.get('corrected_scope_metadata', {}),
        'source_correspondence_flags': record.get('source_correspondence_flags', []),
        'public_supporting_evidence': record.get('public_supporting_evidence', []),
        'source_correspondence': record.get('source_correspondence', {}),
        'source_packet': record.get('source_packet'),
        'lean_sha256': record.get('lean_sha256'),
        'local_dependencies': record.get('local_dependencies', []),
        'selected_theorems': [{'name': t.get('name'), 'type': t.get('audit', {}).get('type')}
                              for t in record.get('build_record', {}).get('selected_theorems', [])],
    }


def validate_annotation(annotation, record):
    a = deepcopy(annotation)
    rid = record['record_id']
    f = fields(record)
    need(a.get('record') == rid and a.get('input_sha256') == value_sha(f), 'Stale annotation: ' + rid)
    for key, allowed in [('object_kind', OBJECTS), ('mechanism', MECHANISMS),
                          ('family_kind', {'none', 'unbounded_discrete', 'continuous_parameter', 'both'}),
                          ('minimality_scope', {'not_documented', 'search_order_or_bounded', 'global_argument'}),
                          ('refutation_role', {'intermediate_step', 'target_statement', 'unclear'})]:
        need(a.get(key) in allowed, 'Invalid category ' + rid + ':' + key)
    for key in PROPERTIES:
        need(type(a.get(key)) is bool, 'Property must be boolean: ' + rid + ':' + key)
    need(a['family_documented'] == (a['family_kind'] != 'none'), 'Inconsistent family labels: ' + rid)
    for key in ('notes', 'review_reason'):
        need(isinstance(a.get(key), str), 'Missing annotation text: ' + rid + ':' + key)
    need(isinstance(a.get('uncertain_fields'), list) and
         all(isinstance(x, str) and x for x in a['uncertain_fields']), 'Invalid uncertain_fields: ' + rid)
    required = (True, a['family_documented'], a['repair_documented'],
                a['nondegenerate_alternative_documented'], a['exhaustive_domain_documented'],
                a['minimality_scope'] != 'not_documented', a['refutation_role'] != 'unclear')
    spans = {}
    for key, positive in zip(EVIDENCE, required):
        text = a.get(key)
        need(isinstance(text, str), 'Missing evidence string: ' + rid + ':' + key)
        matches = [(k, v.index(text)) for k, v in f.items() if text and text in v]
        need(not (positive or text) or bool(matches), 'Missing/nonverbatim evidence: ' + rid + ':' + key)
        if matches:
            k, start = matches[0]
            spans[key] = {'field': k, 'start': start, 'end': start + len(text)}
    a['evidence_spans'] = spans
    return a


def admission_scope(baseline, current, ledger_sha, verified_consensus=None):
    """Project a roster only after the caller's canonical consensus replay.

    This helper is not an approval verifier. Production entrypoint build() obtains
    verified_consensus exclusively from consensus_binding(), never a JSON label.
    """
    before, after = unique(baseline, 'record_id'), unique(current, 'record_id')
    need(list(before) == list(after), 'Ledger roster changed')
    membership_changed = any(before[k]['release_status'] != after[k]['release_status'] for k in before)
    if membership_changed:
        need(verified_consensus is not None,
             'Release membership changed without exact canonical consensus replay')
    corrected = verified_consensus['corrected_record_ids'] if verified_consensus else []
    admission = source_validator().admission_roster(baseline, current, corrected)
    if verified_consensus is not None:
        need(verified_consensus.get('ledger_sha256') == ledger_sha, 'Admission consensus ledger mismatch')
        need(verified_consensus.get('admission') == admission, 'Admission differs from exact consensus-bound roster')
    return admission


def rebind(baseline, annotations, current, recodings, ledger_sha, verified_consensus=None):
    before, after = unique(baseline, 'record_id'), unique(current, 'record_id')
    need(set(before) == set(after), 'Ledger roster changed')
    admission = admission_scope(baseline, current, ledger_sha, verified_consensus)
    retained = {k: r for k, r in after.items() if r['release_status'] == 'RETAINED'}
    historical_retained = {k for k, r in before.items() if r['release_status'] == 'RETAINED'}
    old = unique(annotations, 'record')
    need(set(old) == historical_retained, 'Baseline annotation roster differs from historical retained ledger')
    recode = unique(recodings, 'record_id')
    need(set(recode) <= set(retained), 'Recoding is outside retained roster')
    withdrawn = []
    for rid in admission['newly_excluded_record_ids']:
        withdrawn.append({'record_id': rid, 'ledger_sha256': ledger_sha,
            'historical_release_status': before[rid]['release_status'],
            'current_release_status': after[rid]['release_status'],
            'historical_annotation_for_provenance_only': validate_annotation(old[rid], before[rid]),
            'historical_fields': fields(before[rid]),
            'historical_context_sha256': value_sha(context(before[rid])),
            'current_context_sha256': value_sha(context(after[rid])),
            'current_source_correspondence': after[rid].get('source_correspondence'),
            'public_supporting_evidence': after[rid].get('public_supporting_evidence', []),
            'included_in_current_documentation_counts': False,
            'benchmark_execution_role': 'REQUIRED_DIAGNOSTIC_ONLY_NOT_CURRENT_SCORED_MEMBER',
            'benchmark_rerun_reported_by_census': False})
    selected, queue, inputs, bindings = [], [], [], []
    for rid, r in sorted(retained.items()):
        prior = validate_annotation(old[rid], before[rid])
        f, oldf = fields(r), fields(before[rid])
        c, oldc = context(r), context(before[rid])
        changed_fields = [k for k in FIELDS if f[k] != oldf[k]]
        changed_context = [k for k in c if c[k] != oldc[k]]
        changed = bool(changed_fields or changed_context)
        bindings.append({'record_id': rid, 'input_sha256': value_sha(f),
                         'context_sha256': value_sha(c), 'requires_recoding': changed,
                         'annotation_status': 'PENDING_RECODING' if changed and rid not in recode
                         else 'EXPLICITLY_RECODED' if rid in recode else 'UNCHANGED_REBOUND'})
        inputs.append({'record': rid, 'input_sha256': value_sha(f), 'source_fields': f,
                       'context_sha256': value_sha(c), 'interpretation_context': c})
        if rid in recode:
            x = recode[rid]
            for key, expected in [('ledger_sha256', ledger_sha), ('prior_input_sha256', value_sha(oldf)),
                                  ('input_sha256', value_sha(f)), ('context_sha256', value_sha(c))]:
                need(x.get(key) == expected, 'Stale recoding binding ' + rid + ':' + key)
            for key in ('reviewer', 'reviewed_at_utc', 'rationale'):
                need(isinstance(x.get(key), str) and bool(x[key].strip()), 'Missing recoding attestation: ' + key)
            need(x.get('full_record_recoded') is True, 'Explicit whole-row recoding required: ' + rid)
            selected.append(validate_annotation(x['annotation'], r))
        elif changed:
            queue.append({'record_id': rid, 'ledger_sha256': ledger_sha,
                          'prior_input_sha256': value_sha(oldf), 'input_sha256': value_sha(f),
                          'context_sha256': value_sha(c), 'changed_fields': changed_fields,
                          'changed_context_keys': changed_context,
                          'prior_fields': oldf, 'current_fields': f,
                          'prior_context': oldc, 'current_context': c,
                          'historical_annotation_for_reference_only': prior,
                          'old_evidence_survives_verbatim': {k: any(prior[k] and prior[k] in v for v in f.values())
                                                           for k in EVIDENCE},
                          'required_action': 'Read current fields and context; explicitly recode the whole row, '
                          'including false properties and role. Supply current verbatim positive evidence.'})
        else:
            selected.append(validate_annotation(prior, r))
    return {'annotations': selected, 'queue': queue, 'inputs': inputs, 'bindings': bindings,
            'admission': admission, 'withdrawn_history': withdrawn}


def repo_path(root, path):
    p = (root / path).resolve()
    need(p.is_relative_to(root.resolve()), 'Input path escapes repository: ' + str(path))
    return p


def source_validator():
    path = HERE.parent / 'build_extension_release.py'
    spec = importlib.util.spec_from_file_location('census_extension_source_validator', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def quality(record, root, assignment=None, source_reader=None):
    """Stored source verdicts and stored kernel receipts are different quantities."""
    flags = record.get('source_correspondence_flags', [])
    corrected = record.get('corrected_release', {})
    audit = record.get('audit', {})
    source_verdict = audit.get('source_fidelity')
    source_label = source_verdict.get('status') if isinstance(source_verdict, dict) else source_verdict
    active = None
    if 'public_supporting_evidence' in record or 'source_correspondence' in record:
        need(assignment is not None, 'Public source evidence requires the actual review-plan assignment')
        validator = source_validator()
        validator.validate_record_source_evidence(record, assignment, reader=source_reader)
        active = validator.active_source_state(record)
    if record.get('source_correspondence') is not None:
        source = 'ACTIVE_SOURCE_' + active['status']
    elif flags:
        source = 'UNRESOLVED_SOURCE_FLAGS'
    elif corrected.get('author_side_consensus') == 'ALL_THREE_APPROVED_EXACT_FINAL_CHANGE':
        source = 'EXACT_CORRECTION_ALL_THREE_CONSENSUS_RECORDED'
    elif corrected.get('author_side_second_review') == 'APPROVED_EXACT_CHANGE':
        source = 'EXACT_CORRECTION_AUTHOR_REVIEW_RECORDED'
    elif corrected:
        source = 'CORRECTED_ARTIFACT_NO_CURRENT_SOURCE_VERDICT'
    elif source_label:
        source = 'RECORDED_SOURCE_' + str(source_label)
    else:
        source = 'NO_CURRENT_SOURCE_VERDICT'
    b = record.get('build_record', {})
    lean = record.get('lean_path')
    p = repo_path(root, lean) if lean else None
    file_sha = digest(p) if p and p.is_file() else None
    sha_expected = record.get('lean_sha256')
    errors = []
    if not sha_expected or file_sha != sha_expected:
        errors.append('CURRENT_SOURCE_HASH_MISMATCH_OR_MISSING')
    if b.get('status') != 'PASS' or b.get('selected_theorems_present') is not True:
        errors.append('NO_SUCCESSFUL_SELECTED_THEOREM_RECEIPT')
    if b.get('source_sha256') != sha_expected or b.get('sha256') != sha_expected:
        errors.append('RECEIPT_SOURCE_HASH_MISMATCH')
    if b.get('selected_theorem_trust_tier') != 'KERNEL_ONLY':
        errors.append('NO_KERNEL_ONLY_SELECTED_RECEIPT')
    selected = b.get('selected_theorems', [])
    if not selected or any(not t.get('audit', {}).get('type') or
                           t.get('audit', {}).get('disallowed_axioms') or
                           t.get('audit', {}).get('uses_native_reduction') is not False or
                           t.get('audit', {}).get('unsafe') is not False for t in selected):
        errors.append('SELECTED_DECLARATION_AUDIT_INCOMPLETE_OR_UNSAFE')
    return {'record_id': record['record_id'], 'source_quality_status': source,
            'source_correspondence_flags': flags, 'recorded_source_verdict': audit.get('source_fidelity'),
            'active_source_correspondence': active,
            'public_supporting_evidence': record.get('public_supporting_evidence', []),
            'recorded_witness_verdict': audit.get('witness_validity'),
            'recorded_lean_fidelity_verdict': audit.get('lean_fidelity'),
            'exact_correction_review_status': corrected.get('author_side_consensus') or corrected.get('author_side_second_review'),
            'recorded_correction_consensus_status': corrected.get('author_side_consensus'),
            'human_approval_of_current_artifact': record.get('human_approval_of_current_artifact'),
            'kernel_receipt_status': 'BOUND_STORED_KERNEL_RECEIPT' if not errors else 'INCOMPLETE_OR_STALE',
            'kernel_receipt_issues': errors, 'lean_path': lean, 'actual_lean_sha256': file_sha,
            'expected_lean_sha256': sha_expected}


def accept_provenance(path, ledger_path, current, root=ROOT, base_path=BASE30, base_sha=None):
    """Validate an exact builder acceptance attestation; do not infer who executed it."""
    p = read(path)
    expected_base = base_sha or PINS[BASE30]
    need(p.get('schema') == 'remaining255-approved-extension/v1', 'Approved extension provenance required')
    need(p.get('ledger_sha256') == digest(ledger_path), 'Accepted provenance ledger mismatch')
    need(p.get('base_ledger_sha256') == expected_base and digest(base_path) == expected_base,
         'Accepted provenance base mismatch')
    need(p.get('named_approvals_bind_exact_changes') is True and p.get('human_approval_created') is False,
         'Exact named-change approvals must be recorded without creating human approval')
    need(p.get('total_rows') == len(current), 'Accepted row count mismatch')
    before, after = unique(read(base_path), 'record_id'), unique(current, 'record_id')
    need(set(before) == set(after), 'Accepted extension roster mismatch')
    changed = sorted(k for k in before if before[k] != after[k])
    need(p.get('changed_record_ids') == changed, 'Accepted changed-record list mismatch')
    need(isinstance(p.get('inputs'), dict) and bool(p['inputs']), 'Missing accepted input bindings')
    for name, binding in p['inputs'].items():
        f = repo_path(root, name)
        need(f.is_file() and digest(f) == binding.get('sha256') and f.stat().st_size == binding.get('bytes'),
             'Accepted input binding mismatch: ' + name)
    return p


def separate_computation(root=ROOT):
    receipt = root / 'astra/resource285_quality_check_20260923/targeted_checks/R149_census/RERUN_RECEIPT.json'
    if not receipt.is_file():
        return {'status': 'R149_RERUN_RECEIPT_NOT_PRESENT', 'included_in_documentation_counts_automatically': False}
    r = read(receipt)
    need(r.get('schema') == 'R149-independent-census-rerun/v1' and r.get('status') == 'PASS'
         and r.get('exit_code') == 0, 'R149 receipt does not record successful rerun')
    output = repo_path(root, r['output_path'])
    script = root / 'qedbench_certificate_availability_triage/validation/human_review_20260915/verified_census/checks/proofwiki_132447_count_check.py'
    need(digest(output) == r['output_sha256'] and digest(script) == r['script_sha256'], 'R149 evidence hash mismatch')
    need(r['results']['totals'] == {'matroids': 91, 'violations': 87}, 'Unexpected R149 computation result')
    return {'status': 'BOUND_SEPARATE_COMPUTATION', 'record_id': 'proofwiki_132447',
            'receipt_path': str(receipt.relative_to(root)), 'receipt_sha256': digest(receipt),
            'script_sha256': r['script_sha256'], 'output_path': r['output_path'],
            'output_sha256': r['output_sha256'], 'results': r['results'], 'scope': r['scope'],
            'selected_lean_certifies_this_computation': False,
            'included_in_documentation_counts_automatically': False,
            'documentation_count_rule': 'Positive exhaustive-domain coding requires supporting current prose '
            'and explicit recoding when that prose or evidence changed. The separate 87/91 result remains evidence '
            'on labeled nonempty ground sets of sizes 1 through 4, not an isomorphism-class count.'}


def census_counts(annotations, retained):
    need(all(r['release_status'] == 'RETAINED' for r in retained), 'Withdrawn/excluded record passed to current totals')
    need(set(unique(annotations, 'record')) == set(unique(retained, 'record_id')),
         'Current census annotation/count roster differs')
    n = len(annotations)
    counts = {'N': n, 'SourceUnits': len({r['historical_inventory']['problem_sha256'] for r in retained}),
              'CertificateHashes': len({r['lean_sha256'] for r in retained}),
              'CertificateFiles': len({r['lean_path'] for r in retained}),
              'FamilyRepairBoth': sum(a['family_documented'] and a['repair_documented'] for a in annotations),
              'FamilyRepairEither': sum(a['family_documented'] or a['repair_documented'] for a in annotations),
              'Intermediate': sum(a['refutation_role'] == 'intermediate_step' for a in annotations),
              'Target': sum(a['refutation_role'] == 'target_statement' for a in annotations),
              'RoleUnknown': sum(a['refutation_role'] == 'unclear' for a in annotations),
              'MinimalGlobal': sum(a['minimality_scope'] == 'global_argument' for a in annotations),
              'MinimalBounded': sum(a['minimality_scope'] == 'search_order_or_bounded' for a in annotations),
              'AnyUncertainty': sum(bool(a['uncertain_fields']) for a in annotations)}
    for key, (macro, _) in PROPERTIES.items():
        counts[macro] = sum(a[key] for a in annotations)
        counts[macro + 'Pct'] = f'{100 * counts[macro] / n:.1f}' if n else '0.0'
    categories = {k: dict(sorted(Counter(a[k] for a in annotations).items()))
                  for k in ('object_kind', 'mechanism', 'refutation_role', 'minimality_scope')}
    return counts, categories


def venue(record_id):
    for prefix, label in [('arxiv_', 'arXiv'), ('proofwiki_', 'ProofWiki'),
                          ('Algorithms_', 'QEDBench'), ('Graph_Theory_', 'QEDBench'),
                          ('reddit_', 'Reddit'), ('SE_', 'Stack Exchange'),
                          ('mse_', 'Math StackExchange'), ('g3ref-', 'Reference-proof additions')]:
        if record_id.startswith(prefix):
            return label
    raise ValueError('Unknown source venue: ' + record_id)


def table(headers, rows):
    return '\\begin{tabular}{lr}\n\\toprule\n' + headers + ' \\\\\n\\midrule\n' + ''.join(
        f'{label} & {value} \\\\\n' for label, value in rows) + '\\bottomrule\n\\end{tabular}\n'


def render_assets(summary):
    c, categories = summary['counts'], summary['categories']
    files = {'generated/verified_counterexample_summary.json': encoded(summary),
             'generated/verified_counterexample_counts.tex': (
                 '% Staged current documentation census. Source quality and kernel coverage are separate.\n'
                 + ''.join('\\newcommand{\\vcex' + k + '}{' + str(v) + '}\n' for k, v in c.items())).encode(),
             'generated/verified_counterexample_properties.tex': table('Documented property & Records (\\%)',
                 [(label, f"{c[macro]} ({c[macro+'Pct']})") for macro, label in PROPERTIES.values()]).encode(),
             'generated/verified_counterexample_categories.tex': table('Recorded mechanism & Records',
                 [(label, categories['mechanism'].get(k, 0)) for k, label in MECHANISMS.items()]).encode(),
             'generated/verified_counterexample_objects.tex': table('Witness object & Records',
                 [(label, categories['object_kind'].get(k, 0)) for k, label in OBJECTS.items()]).encode()}
    quality_rows = [(k.replace('_', '\\_'), v) for k, v in summary['source_quality_counts'].items()]
    files['generated/current_source_quality.tex'] = table('Recorded source-quality status & Records', quality_rows).encode()
    files['generated/verified_counterexample_dispositions.tex'] = (
        '% Replaces historical disposition display with current recorded source status.\n'
        + table('Recorded source-quality status & Records', quality_rows)).encode()
    files['generated/current_kernel_coverage.tex'] = table('Stored kernel receipt coverage & Records',
        [(k.replace('_', '\\_'), v) for k, v in summary['kernel_receipt_counts'].items()]).encode()
    files['generated/verified_counterexample_sources.tex'] = table('Source & Retained records',
        list(summary['by_source'].items())).encode()
    return files


def render_figure(summary, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), gridspec_kw={'width_ratios': [1.25, 1]})
    for ax, labels, vals, title in [
        (axes[0], list(MECHANISMS.values()), [summary['categories']['mechanism'].get(k, 0) for k in MECHANISMS], 'Recorded mechanisms'),
        (axes[1], [v[1] for v in PROPERTIES.values()], [summary['counts'][v[0]] for v in PROPERTIES.values()], 'Documented properties (overlap)')]:
        ax.barh(range(len(labels)), vals, color='#315f8c')
        ax.set_yticks(range(len(labels)), labels); ax.invert_yaxis()
        for i, value in enumerate(vals):
            ax.text(value + .8, i, str(value), va='center', fontsize=9)
        ax.set_xlim(0, max([1] + vals) * 1.17)
        ax.set_title(title); ax.set_xlabel('Retained records')
        ax.spines[['top', 'right']].set_visible(False)
    fig.suptitle(f"Documentation census of {summary['counts']['N']} current retained records")
    fig.tight_layout(rect=(0, .05, 1, .96))
    fig.text(.5, .018, 'Documentation coding; source-quality status and kernel receipt coverage reported separately.', ha='center', fontsize=8)
    (output / 'figures').mkdir()
    for ext in ('pdf', 'png'):
        fig.savefig(output / ('figures/verified_counterexample_categories.' + ext), dpi=180)
    plt.close(fig)


def consensus_binding(path, ledger_path, root=ROOT):
    """Reuse the canonical builder's full replay of its emitted consensus receipt."""
    if path is None:
        return None
    def descriptor(file):
        p = repo_path(root, file)
        return {'path': str(p.relative_to(root.resolve())), 'sha256': digest(p)}
    return source_validator().verify_consensus_receipt(
        descriptor(path), ledger_descriptor=descriptor(ledger_path))


def ready_for_assets(accepted, preview, pending_recodings, missing_kernel, consensus=None):
    return bool(accepted and consensus and not preview and not pending_recodings and not missing_kernel)


def build(ledger_path, output, recoding_path=None, provenance_path=None, preview=False, figures=True, consensus_path=None):
    output = Path(output).resolve()
    need(output.is_relative_to((HERE / 'staging').resolve()), 'Output must be a new census_refresh/staging subdirectory')
    need(output != (HERE / 'staging').resolve() and not output.exists(), 'Use a new staging version; never overwrite')
    need(preview or provenance_path is not None, 'Final candidate requires explicit accepted extension provenance')
    for path, expected in PINS.items():
        need(digest(path) == expected, 'Historical/base pin mismatch: ' + str(path))
    ledger_path = Path(ledger_path).resolve()
    current = read(ledger_path)
    need(len(current) == 425, 'Expected the unchanged 425-record ledger identity inventory')
    accepted = accept_provenance(provenance_path, ledger_path, current) if provenance_path else None
    consensus = consensus_binding(consensus_path, ledger_path)
    recodings = read(recoding_path) if recoding_path else []
    result = rebind(read(BASELINE), read(ANNOTATIONS), current, recodings, digest(ledger_path), consensus)
    if accepted is not None and consensus is not None:
        need(accepted.get('admission') == result['admission'], 'Accepted provenance admission differs from consensus')
    retained = [r for r in current if r['release_status'] == 'RETAINED']
    review_plan_path = HERE.parent / 'REVIEW_PLAN.json'
    assignments = unique(read(review_plan_path)['rows'], 'record_id')
    qualities = [quality(r, ROOT, assignments.get(r['record_id'])) for r in retained]
    withdrawn_ids = set(result['admission']['newly_excluded_record_ids'])
    diagnostic_qualities = [quality(r, ROOT, assignments.get(r['record_id'])) for r in current
                            if r['record_id'] in withdrawn_ids]
    source_counts = dict(sorted(Counter(r['source_quality_status'] for r in qualities).items()))
    kernel_counts = dict(sorted(Counter(r['kernel_receipt_status'] for r in qualities).items()))
    missing_kernel = [r['record_id'] for r in qualities if r['kernel_receipt_issues']]
    ready = ready_for_assets(accepted, preview, result['queue'], missing_kernel, consensus)
    status = {'schema': 'current-documentation-census/staging-v1',
              'status': 'READY_FOR_GEMINI_REVIEW' if ready else 'PENDING_NOT_CURRENT_COUNTS',
              'preview': preview, 'accepted_extension_provenance_bound': accepted is not None,
              'three_reviewer_consensus_bound': consensus is not None,
              'ledger_path': str(ledger_path.relative_to(ROOT)), 'ledger_sha256': digest(ledger_path),
              'recoding_count': len(recodings), 'pending_recoding_count': len(result['queue']),
              'annotation_coverage_count': len(result['annotations']), 'retained_roster_count': len(retained),
              'current_retained_ids_sha256': result['admission']['current_retained_ids_sha256'],
              'withdrawn_historical_annotation_count': len(result['withdrawn_history']),
              'diagnostic_only_corrected_record_ids': result['admission']['diagnostic_only_corrected_record_ids'],
              'diagnostic_benchmark_reruns_reported_by_census': False,
              'kernel_binding_pending_record_ids': missing_kernel,
              'current_property_counts_emitted': ready, 'publication_performed': False,
              'human_approval_created': False,
              'notes': ['Named coding attestations do not establish independent human validation.',
                        'Stored kernel receipt binding is not fresh compilation or source correspondence.',
                        'Population dispositions in the original census are historical provenance only.'],
              'inputs': {str(p.relative_to(ROOT)): digest(p) for p in [*PINS, ledger_path, Path(__file__).resolve(),
                        review_plan_path, HERE.parent / 'build_extension_release.py']}}
    for p in (recoding_path, provenance_path, consensus_path):
        if p:
            status['inputs'][str(Path(p).resolve().relative_to(ROOT))] = digest(p)
    files = {'STATUS.json': encoded(status), 'RECODING_QUEUE.json': encoded(result['queue']),
             'ADMISSION.json': encoded(result['admission']),
             'WITHDRAWN_ANNOTATION_HISTORY.json': encoded(result['withdrawn_history']),
             'INPUTS_CURRENT.json': encoded(result['inputs']), 'ANNOTATION_BINDINGS.json': encoded(result['bindings']),
             'ANNOTATIONS_REBOUND_PARTIAL.json': encoded(result['annotations']),
             'SOURCE_AND_KERNEL_STATUS.json': encoded({'source_quality_counts': source_counts,
                  'kernel_receipt_counts': kernel_counts, 'rows': qualities,
                  'scope': 'Current retained roster only; withdrawn records are outside these counts. '
                  'Exact recorded statuses. No all-source-PASS inference from kernel success.'}),
             'DIAGNOSTIC_ONLY_STATUS.json': encoded({'rows': diagnostic_qualities,
                  'included_in_current_documentation_counts': False,
                  'benchmark_reruns_reported_by_census': False,
                  'scope': 'Withdrawn corrected records still require diagnostic benchmark reruns. '
                  'Stored receipt binding is not that rerun and does not restore admission.'}),
             'SEPARATE_COMPUTATIONS.json': encoded(separate_computation()),
             'HISTORICAL_PROVENANCE.json': encoded({'baseline_summary_path': str(SUMMARY.relative_to(ROOT)),
                  'baseline_summary_sha256': digest(SUMMARY),
                  'scope': 'Original population dispositions are historical only. They are not new current census counts.'})}
    summary = None
    if ready:
        counts, categories = census_counts(result['annotations'], retained)
        summary = {'schema': 'current-documentation-census/v2', 'counts': counts, 'categories': categories,
                   'ledger_sha256': digest(ledger_path), 'annotation_sha256': sha(encoded(result['annotations'])),
                   'current_retained_record_ids': result['admission']['current_retained_record_ids'],
                   'current_retained_ids_sha256': result['admission']['current_retained_ids_sha256'],
                   'source_quality_counts': source_counts, 'kernel_receipt_counts': kernel_counts,
                   'by_source': dict(sorted(Counter(venue(r['record_id']) for r in retained).items())),
                   'annotation_scope': 'Current five-field documentation of the exact consensus-bound retained subset; '
                   'unchanged annotations rebound, changed annotations explicitly recoded. '
                   'Withdrawn records and their historical annotations are outside current totals. '
                   'This does not establish semantic validity or independent human agreement.'}
        files.update(render_assets(summary))
        files['annotations_current.json'] = encoded(result['annotations'])
    output.mkdir(parents=True)
    for relative, data in files.items():
        path = output / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    if ready and figures:
        render_figure(summary, output)
    manifest = {'schema': 'current-documentation-census/output-manifest-v1',
                'outputs': {str(p.relative_to(output)): digest(p) for p in sorted(output.rglob('*')) if p.is_file()}}
    (output / 'OUTPUT_MANIFEST.json').write_bytes(encoded(manifest))
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ledger', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--recodings', type=Path, help='List of explicit full-row recoding attestations')
    parser.add_argument('--accepted-provenance', type=Path)
    parser.add_argument('--consensus', type=Path, help='Canonical extension CONSENSUS.json; verified by full builder replay')
    parser.add_argument('--preview', action='store_true', help='Always withhold current totals and paper assets')
    parser.add_argument('--no-figures', action='store_true')
    args = parser.parse_args()
    print(json.dumps(build(args.ledger, args.output, args.recodings, args.accepted_provenance,
                           args.preview, not args.no_figures, args.consensus), indent=2))


if __name__ == '__main__':
    main()
