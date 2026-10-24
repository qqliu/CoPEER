/* Integrity checks for the generated data files (docs/data/*.js).
 * Runs in the browser (docs/tests.html) and in node (tests/run_checks.mjs) unchanged.
 * Each check returns {name, pass, detail}. The checks compare the extracted tables with one
 * another and with the paper's stated totals; they never recompute the paper's statistics.
 */
(function (root) {
  'use strict';

  function val(x) { return (x && typeof x === 'object' && 'value' in x) ? x.value : x; }
  function ci(x) { return (x && typeof x === 'object' && x.ci95) ? x.ci95 : null; }
  function pair(x) { return (x && typeof x === 'object' && x.pair) ? x.pair : null; }
  function triple(x) { return (x && typeof x === 'object' && x.triple) ? x.triple : null; }

  function runDataChecks(D) {
    var out = [];
    function check(name, cond, detail) { out.push({ name: name, pass: !!cond, detail: detail || '' }); }
    function need(key) { if (!D[key]) { check('file present: ' + key, false, 'missing'); return null; } return D[key]; }

    // every file points at the same manuscript source
    var commits = {}, shas = {};
    var paperFiles = Object.keys(D).filter(function (k) { var s = D[k].source || {}; return /^(tab|fig|text):/.test(s.label || ''); });
    paperFiles.forEach(function (k) { var s = D[k].source || {}; commits[s.commit] = 1; shas[s.main_tex_sha256] = 1; });
    check('all paper-derived files cite one manuscript commit', Object.keys(commits).length === 1 && paperFiles.length >= 26, Object.keys(commits).join(',') + ' (' + paperFiles.length + ' files)');
    check('all paper-derived files cite one main.tex hash', Object.keys(shas).length === 1, Object.keys(shas).map(function (s) { return String(s).slice(0, 8); }).join(','));
    if (D.dossiers_index && D.core_composition) {
      var di = D.dossiers_index.rows, want = {};
      D.core_composition.by_source_collection.forEach(function (r) { if (!/^Total/.test(r.source_collection)) want[r.source_collection] = r; });
      var okCore = Object.keys(want).every(function (g) { return di.filter(function (r) { return r.core && r.group_name === g; }).length === want[g].dossiers && di.filter(function (r) { return r.primary && r.group_name === g; }).length === want[g].inputs; });
      check('Explorer index: core and primary counts by source collection equal Table 5', okCore && di.filter(function (r) { return r.core; }).length === 147 && di.filter(function (r) { return r.primary; }).length === 100, di.length + ' released rows');
      var wantM = {}; D.core_composition.by_error_mechanism.forEach(function (r) { if (!/^Total/.test(r.error_mechanism)) wantM[r.error_mechanism] = r; });
      var okMech = Object.keys(wantM).every(function (g) { return di.filter(function (r) { return r.core && r.mechanism_name === g; }).length === wantM[g].dossiers && di.filter(function (r) { return r.primary && r.mechanism_name === g; }).length === wantM[g].inputs; });
      check('Explorer index: core and primary counts by error mechanism equal Table 5', okMech && di.filter(function (r) { return r.core && r.mechanism_uncertain; }).length === 6 && di.filter(function (r) { return r.primary && r.mechanism_uncertain; }).length === 3);
      check('Explorer index: every core record has an all-YES review; every current benchmark input has reference lines', di.filter(function (r) { return r.core; }).every(function (r) { return r.any_all_yes; }) && di.filter(function (r) { return r.scorable; }).every(function (r) { return r.current_gold && r.current_gold.length; }));
      check('Explorer index: primary and supplementary inputs are core records (100 and 131)', di.filter(function (r) { return r.primary; }).every(function (r) { return r.core; }) && di.filter(function (r) { return r.scorable; }).length === 131);
    }
    if (D.views && D.localization_full) {
      var full = D.localization_full.rows.filter(function (r) { return r.kind === 'model'; });
      check('Views: 14 reporting views whose core scores equal Table 16', D.views.views.length === 14 && D.views.views.every(function (vw) { var t = full.filter(function (r) { return r.name === vw.name; })[0]; return t && t.hit1.value === vw.primary.hit1.percent && t.hit3.value === vw.primary.hit3.percent; }));
      check('Views: the TF-IDF baseline is 18.0 and the random-line expectation is 6.7', Math.round(D.views.baselines.tfidf_centroid_line.percent * 10) / 10 === 18.0 && Math.round(D.views.baselines.random_line.percent * 10) / 10 === 6.7);
    }
    if (D.example_record) check('example record: built from the release with the certificate hash bound in membership.json', D.example_record.membership && D.example_record.membership.bindings.certificate_sha256 === D.example_record.certificate.sha256 && D.example_record.gold[0] === 5);

    var lm = need('localization_main'), lf = need('localization_full');
    if (lm && lf) {
      var models = lm.rows.filter(function (r) { return r.kind === 'model'; });
      check('Table 1: 12 model rows and 2 baselines', models.length === 12 && lm.rows.length === 14, lm.rows.length + ' rows');
      check('Table 1: Hit@3 >= Hit@1 for every model', models.every(function (r) { return val(r.hit3) >= val(r.hit1); }));
      check('Table 1: every interval contains its value', models.every(function (r) { var a = ci(r.hit1), b = ci(r.hit3); return a && b && a[0] <= val(r.hit1) && val(r.hit1) <= a[1] && b[0] <= val(r.hit3) && val(r.hit3) <= b[1]; }));
      check('Table 1: met-rules counts are at most 100', models.every(function (r) { return r.met_rules_of_100 <= 100; }));
      check('Table 1: best Hit@1 is Gemini 3.1 Pro at 73.0', models.reduce(function (b, r) { return val(r.hit1) > val(b.hit1) ? r : b; }).name === 'Gemini 3.1 Pro' && models.some(function (r) { return r.name === 'Gemini 3.1 Pro' && val(r.hit1) === 73.0; }));
      check('Table 1: TF-IDF baseline 18.0 without Hit@3', lm.rows.some(function (r) { return r.kind === 'baseline' && val(r.hit1) === 18.0 && r.hit3 === null; }));
      var full = lf.rows.filter(function (r) { return r.kind === 'model'; });
      check('Table 16: 14 model rows (13 configurations, Haiku in two views)', full.length === 14, full.length + ' rows');
      check('Table 16 contains both Haiku views (31.0 and 56.0)', full.some(function (r) { return /Haiku/.test(r.name) && val(r.hit1) === 31.0; }) && full.some(function (r) { return /Haiku/.test(r.name) && val(r.hit1) === 56.0; }));
      var agree = models.every(function (r) { var f = full.filter(function (x) { return x.name === r.name; })[0]; return f && val(f.hit1) === val(r.hit1) && val(f.hit3) === val(r.hit3) && val(f.recorded_total_tokens) === val(r.recorded_total_tokens); });
      check('Tables 1 and 16 agree on every shared row', agree);
      check('Table 16: output tokens never exceed recorded total', full.every(function (r) { return val(r.recorded_output_tokens) <= val(r.recorded_total_tokens); }));
    }

    var ia = need('instruction_arms'), it = need('instruction_tokens'), is = need('instruction_summary');
    if (ia) {
      var rows = ia.rows.filter(function (r) { return !r.section; });
      check('Table 7: 24 rows (6 panels x 4 arms)', rows.length === 24, rows.length + ' rows');
      check('Table 7: strict <= lenient <= n in every row', rows.every(function (r) { return r.strict <= r.lenient && r.lenient <= r.n; }));
      check('Table 7: n is 100 for proofs and 60 for claims', rows.every(function (r) { return (/^proofs/.test(r.panel_model) && r.n === 100) || (/^claims/.test(r.panel_model) && r.n === 60); }));
      check('Table 7: each panel starts with the counterexample arm as reference', rows.filter(function (r) { return r.arm === 'counterexample'; }).every(function (r) { return r.output_ratio && r.output_ratio.reference === true; }) && rows.filter(function (r) { return r.arm === 'counterexample'; }).length === 6);
    }
    if (it) {
      check('Table 8: 12 rows (3 models x 4 instructions)', it.rows.length === 12, it.rows.length + ' rows');
      check('Table 8: uncached + cache reads + output = recorded total in every row', it.rows.every(function (r) { return r.uncached_input + r.cache_reads + r.output === r.recorded_total; }));
      check('Table 8: usage coverage n = 100 except Opus 5 early stop (99)', it.rows.every(function (r) { return r.n === 100 || (r.model === 'Opus 5' && r.instruction === 'Early stop' && r.n === 99); }));
    }
    if (is && ia) {
      var byPanel = {};
      ia.rows.filter(function (r) { return !r.section; }).forEach(function (r) { byPanel[r.panel_model + '|' + r.arm] = r; });
      function cmp(panel, model) {
        var s = is.rows.filter(function (r) { return r.model === model; });
        var a = byPanel[panel + '|counterexample'], b = byPanel[panel + '|early + witness'];
        return s.length && a && b && (val(s[0].search_confirmed) === a.strict || val(s[1] && s[1].search_confirmed) === a.strict);
      }
      check('Table 6 search counts match Table 7 strict counterexample counts (Sol, Gemini)', cmp('proofs, GPT-5.6 Sol', 'Sol') && cmp('proofs, Gemini 3.1 Pro', 'Gemini') && cmp('claims, GPT-5.6 Sol', 'Sol') && cmp('claims, Gemini 3.1 Pro', 'Gemini'));
    }

    var c6 = need('claims60_summary'), cs = need('claims60_sensitivity');
    if (c6 && cs) {
      check('Table 14: 3 models with S/O/W counts', c6.rows.length === 3 && c6.rows.every(function (r) { return triple(r.supported_s_o_w); }));
      var ok = c6.rows.every(function (r) {
        var t = triple(r.supported_s_o_w);
        function catches(arm) { var x = cs.rows.filter(function (q) { return q.model === r.model && q.arm === arm && q.subset === 'All'; })[0]; return x ? pair(x.catches_s_c) : null; }
        var o = catches('O'), w = catches('W');
        return o && w && o[0] === t[0] && w[0] === t[0] && o[1] === t[1] && w[1] === t[2];
      });
      check('Tables 14 and 15 agree on the All-subset counts for every model', ok);
      check('Table 15: every subset n is at most 60', cs.rows.every(function (r) { return val(r.n) <= 60; }));
      check('Table 15: 30 rows (Sol 12, Gemini 12, Opus 6 without tool-free rows)', cs.rows.length === 30 && cs.rows.filter(function (r) { return r.model === 'Opus'; }).length === 6, cs.rows.length + ' rows');
    }

    var ro = need('repair_outcomes'), rr = need('repair_resources');
    if (ro) {
      check('Table 10: 6 rows, PASS + FAIL + Absent = 16', ro.rows.length === 6 && ro.rows.every(function (r) { return r.pass + r.fail + r.absent === 16; }));
      check('Table 10: condition B never has fewer passes than A for the same solver', ['Claude Opus 5.5', 'Claude Sonnet 5', 'GPT-OSS 120B'].every(function (s) { var a = ro.rows.filter(function (r) { return r.solver === s && r.condition === 'A'; })[0], b = ro.rows.filter(function (r) { return r.solver === s && r.condition === 'B'; })[0]; return a && b && b.pass >= a.pass; }));
    }
    if (rr) {
      check('Table 11: usage coverage denominators are 16', rr.rows.every(function (r) { return pair(r.attempts_with_recorded_usage)[1] === 16; }));
      check('Table 11: output tokens <= recorded total tokens', rr.rows.every(function (r) { return val(r.output_tokens) <= val(r.recorded_total_tokens); }));
    }

    var pd = need('proof_development'), op = need('open_problem_retrieval');
    if (pd) {
      check('Table 12: 6 rows, graded correct at most 50 in both conditions', pd.rows.length === 6 && pd.rows.every(function (r) { var p = pair(r.graded_correct_bugbank_plain); return p[0] <= 50 && p[1] <= 50; }));
      check('Table 12: Opus shared-rule ratio 0.696 [0.555, 0.887]', pd.rows.some(function (r) { return r.model === 'Opus 5' && r.protocol === 'shared' && val(r.total_token_ratio) === 0.696 && ci(r.total_token_ratio)[0] === 0.555; }));
      check('Table 12: ratio direction matches the token pair in every row', pd.rows.every(function (r) { var p = pair(r.recorded_total_bugbank_plain); return (p[0] / p[1] < 1) === (val(r.total_token_ratio) < 1); }));
    }
    if (op) {
      check('Table 13: both + B-only + P-only + neither = paired units in every row', op.rows.every(function (r) { var bp = pair(r.b_only_p_only); return r.both + bp[0] + bp[1] + r.neither === r.paired_units; }));
      check('Table 13: 36 distinct final targets, 12/11 audited-full', op.rows[0].paired_units === 36 && pair(op.rows[0].audited_full_b_p)[0] === 12 && pair(op.rows[0].audited_full_b_p)[1] === 11);
    }

    var cc = need('core_composition');
    if (cc) {
      function sums(panel) { var s = [0, 0]; panel.forEach(function (r) { if (!/^Total/.test(r[Object.keys(r)[0]])) { s[0] += r.dossiers; s[1] += r.inputs; } }); return s; }
      var a = sums(cc.by_source_collection), b = sums(cc.by_error_mechanism);
      check('Table 5: source collections sum to 147 dossiers and 100 inputs', a[0] === 147 && a[1] === 100, a.join('/'));
      check('Table 5: error mechanisms sum to 147 dossiers and 100 inputs', b[0] === 147 && b[1] === 100, b.join('/'));
    }

    var rv = need('review_rounds'), an = need('audit_nonapprovals'), pm = need('population_map');
    if (rv) check('Table 3: 7 review rounds', rv.rows.length === 7, rv.rows.length + ' rows');
    if (an) {
      check('Table 4: 9 nonapprovals with 12-hex certificate versions', an.rows.length === 9 && an.rows.every(function (r) { return /^[0-9a-f]{12}$/.test(r.certificate_version); }));
      check('Table 4: every negative check names Q1, Q2 or Q3', an.rows.every(function (r) { return /^Q[123](, Q[123])*$/.test(r.negative_checks); }));
    }
    if (pm) check('Table 2: 6 populations', pm.rows.length === 6, pm.rows.length + ' rows');

    var ep = need('explanation_packages'), cf = need('certified_families'), pc = need('projective_cube_families'), rs = need('related_resources'), eb = need('experiment_b');
    if (ep) check('Table 21: thirteen explanation packages', ep.rows.length === 13, ep.rows.length + ' rows');
    if (cf) check('Table 22: seven certified families', cf.rows.length === 7, cf.rows.length + ' rows');
    if (pc) check('Table 23: d = 5, 7, 8 with densities 13/16, 7/8, 8/9', pc.rows.length === 3 && pc.rows.map(function (r) { return r.d; }).join(',') === '5,7,8' && /13\/16/.test(pc.rows[0].density) && /7\/8/.test(pc.rows[1].density) && /8\/9/.test(pc.rows[2].density));
    if (rs) {
      check('Table 24: nine resources, Co-PEER first', rs.rows.length === 9 && /Co-PEER/.test(rs.rows[0].resource_and_scale));
      var keys = Object.keys(rs.bibliography || {});
      check('Table 24: every cited key resolved in the bibliography', keys.length > 0 && keys.every(function (k) { return rs.bibliography[k] && rs.bibliography[k].title; }), keys.length + ' keys');
    }
    if (eb) check('Table 19: valid objections = valid among matches + valid among misses', eb.rows.every(function (r) { return pair(r.total_valid_objections)[0] === r.valid_among_matches + r.valid_among_misses && pair(r.total_valid_objections)[1] === 24; }));

    var ex = need('benchmark_example'), wf = need('workflow_counts'), es = need('execution_settings'), lmod = need('local_models'), mc = need('math_constants'), smt = need('source_matched');
    if (ex) {
      check('Figure 1: reference line 5 is the recorded first choice (Hit@1 = 1)', ex.reference_line === 5 && ex.recorded_selection.candidates[0] === 5 && ex.recorded_selection.hit1 === 1);
      check('Figure 1: the excerpt contains lines 1, 3 and 5 of a 10-line input', ex.numbered_lines_total === 10 && ex.excerpt_lines.map(function (l) { return l.line; }).join(',') === '1,3,5');
      check('Figure 1: the false identity appears on line 5', /f\(x\) = f\(-x\) \+ \(-f\(x\)\)/.test(ex.excerpt_lines[2].tex));
    }
    if (wf) {
      check('Executable checks: 351 + 12 + 221 + 20 = 604', wf.witnesses + wf.exhaustive_without_witness + wf.inconclusive + wf.outside_permitted_setting === wf.executable_tasks && wf.executable_tasks === 604);
      check('Executable checks: 348 confirmed + 3 rejected = 351 witnesses', wf.checker_confirmed + wf.checker_rejected === wf.witnesses);
    }
    if (es) check('Table 18: 13 model configurations', es.rows.length === 13, es.rows.length + ' rows');
    if (lmod) check('Table 17: 8 local models with Hugging Face repositories', lmod.rows.length === 8 && lmod.rows.every(function (r) { return /\//.test(r.repository); }));
    if (mc) check('Mathematics statements located in the source', ['sqrt', 'cycle_blowup', 'schur', 'projective_cubes', 'rooks', 'even_odd', 'shellsort'].every(function (k) { return mc.items[k] && mc.items[k].lines.every(function (n) { return n > 0; }); }));
    if (smt) check('Table 9: 3 models on 22 source-matched cases', smt.rows.length === 3 && smt.rows.every(function (r) { var p = pair(r.catches); return p[0] <= 22 && p[1] <= 22; }));

    return out;
  }

  root.COPEER_CHECKS = root.COPEER_CHECKS || {};
  root.COPEER_CHECKS.runDataChecks = runDataChecks;
})(typeof window !== 'undefined' ? window : globalThis);
