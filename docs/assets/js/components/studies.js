/* Studies section: instruction arms (Tables 6, 7, 8), repair (Tables 10, 11), proof development (Table 12), open-problem retrieval (Table 13). */
(function () {
  'use strict';
  var C = window.COPEER, D = window.COPEER_DATA || {}, h = C.h, v = C.val, ci = C.ci;

  function scope(text) { return h('div', { class: 'note scope' }, [h('p', { text: text })]); }
  function cell(x, digits) { var c = ci(x); return h('td', { class: 'num', 'data-value': x === null ? '' : String(v(x)) }, [x === null ? '—' : C.fmt(v(x), digits), c ? h('span', { class: 'ci', text: ' [' + C.fmt(c[0], digits) + ', ' + C.fmt(c[1], digits) + ']' }) : null]); }

  /* ---------- instruction arms ---------- */
  function instruction(root) {
    var ia = D.instruction_arms, it = D.instruction_tokens, is = D.instruction_summary; if (!ia) return;
    var rows = ia.rows.filter(function (r) { return !r.section; });
    var panels = []; rows.forEach(function (r) { if (panels.indexOf(r.panel_model) < 0) panels.push(r.panel_model); });
    var sel = h('select', {}, panels.map(function (p) { return h('option', { value: p, text: p.replace(/^proofs, /, '100 proofs · ').replace(/^claims, /, '60 statements · ') }); }));
    sel.value = 'proofs, GPT-5.6 Sol';
    var metricSeg = h('span', { class: 'segmented', role: 'group', 'aria-label': 'Metric' }, [
      h('button', { type: 'button', 'data-value': 'confirmed', 'aria-pressed': 'true', text: 'Confirmed objections' }),
      h('button', { type: 'button', 'data-value': 'tokens', 'aria-pressed': 'false', text: 'Output tokens' }),
      h('button', { type: 'button', 'data-value': 'ratio', 'aria-pressed': 'false', text: 'Output ratio' })]);
    var chart = h('div'), caption = h('p', { class: 'caption' }), tableWrap = h('div', { class: 'table-wrap' });
    root.appendChild(h('div', { class: 'controls' }, [h('label', {}, ['Panel and model ', sel]), metricSeg]));
    root.appendChild(chart); root.appendChild(caption); root.appendChild(tableWrap);
    var armNames = { 'counterexample': 'Counterexample-first search', 'full verify': 'Full sequential verification', 'full proof': 'Full proof attempt', 'early stop': 'Early stop (ordinary)', 'early + witness': 'Early stop, counterexample required' };
    var armShort = { 'counterexample': 'Search first', 'full verify': 'Full verification', 'full proof': 'Full proof', 'early stop': 'Early stop', 'early + witness': 'Early stop + witness' };
    function draw() {
      var p = sel.value, metric = C.segValue(metricSeg), prows = rows.filter(function (r) { return r.panel_model === p; });
      if (metric === 'confirmed') {
        C.barGroups(chart, prows.map(function (r) { return { label: armShort[r.arm] || r.arm, values: [r.strict, r.lenient] }; }), [{ name: 'strict (accepted counterexample or refutation)', color: 'var(--indigo)' }, { name: 'lenient (also a correct unsupported verdict)', color: 'var(--teal)' }], { max: prows[0].n, digits: 0, ariaLabel: 'Confirmed objections by arm' });
        caption.textContent = 'Confirmed objections out of ' + prows[0].n + ' graded inputs for ' + p + ', by instruction arm. Strict counts an accepted counterexample or refutation; lenient also counts a correct unsupported verdict. False counts invalid objections and unverifiable counts objects the grader could not check (see the table).';
      } else if (metric === 'tokens') {
        C.barGroups(chart, prows.map(function (r) { return { label: armShort[r.arm] || r.arm, values: [r.mean_output_tokens] }; }), [{ name: 'mean accepted-response output tokens', color: 'var(--indigo)' }], { digits: 0, ariaLabel: 'Mean output tokens by arm' });
        caption.textContent = 'Mean accepted-response output tokens by instruction arm for ' + p + '. Absolute costs are not compared across harnesses.';
      } else {
        C.barGroups(chart, prows.map(function (r) { return { label: armShort[r.arm] || r.arm, values: [v(r.output_ratio)] }; }), [{ name: 'search output ÷ comparison output (paired records)', color: 'var(--crimson)' }], { max: 1.5, digits: 3, ariaLabel: 'Output-token ratio by arm' });
        caption.textContent = 'Ratio of counterexample-first output to each arm\'s output on paired records, with 95% record-bootstrap intervals in the table; a ratio below one favours counterexample-first search. The reference arm has ratio 1.';
      }
      tableWrap.innerHTML = '';
      tableWrap.appendChild(h('table', { class: 'data' }, [h('thead', {}, [h('tr', {}, ['Arm', 'n', 'Strict', 'Lenient', 'False', 'Unverifiable', 'Mean output tokens', 'Output ratio [95% CI]', 'Observed ratio'].map(function (t, i) { return h('th', { class: i ? 'num' : '', text: t }); }))]), h('tbody', {}, prows.map(function (r) { return h('tr', {}, [h('td', { text: armNames[r.arm] || r.arm }), h('td', { class: 'num', text: String(r.n) }), h('td', { class: 'num', text: String(r.strict) }), h('td', { class: 'num', text: String(r.lenient) }), h('td', { class: 'num', text: String(r.false) }), h('td', { class: 'num', text: String(r.unverifiable) }), h('td', { class: 'num', text: C.fmt(r.mean_output_tokens, 0) }), r.output_ratio && r.output_ratio.reference ? h('td', { class: 'num', text: '1 (reference)' }) : cell(r.output_ratio, 3), h('td', { class: 'num', text: r.observed_ratio === null ? '—' : C.fmt(r.observed_ratio, 3) })]); }))]));
    }
    sel.addEventListener('change', draw); metricSeg.addEventListener('change', draw); draw();
    root.appendChild(scope('Across 100 proofs flagged by the pipeline as flawed, counterexample-first search uses 15–31% fewer output tokens than sequential review that must also give a counterexample, with no clear difference in the rate of objections that a reference-assisted model grader confirmed (intervals include zero). Original Opus proof grades and transcript accounting are retained; all other rows use the common September grades by gpt-6-astra and native usage. Opus 5 proof-panel token accounting is provisional.'));
    /* token components */
    if (it) {
      var det = h('details', {}, [h('summary', { text: 'Recorded token components for the four proof-panel arms (Table 8)' })]);
      var tchart = h('div'); det.appendChild(tchart);
      var models = []; it.rows.forEach(function (r) { if (models.indexOf(r.model) < 0) models.push(r.model); });
      var msel = h('select', {}, models.map(function (m) { return h('option', { value: m, text: m }); }));
      det.insertBefore(h('div', { class: 'controls' }, [h('label', {}, ['Model ', msel])]), tchart);
      function drawT() { var m = msel.value, trows = it.rows.filter(function (r) { return r.model === m; }); C.barGroups(tchart, trows.map(function (r) { return { label: r.instruction + (r.n < 100 ? ' (n = ' + r.n + ')' : ''), values: [r.uncached_input, r.cache_reads, r.output] }; }), [{ name: 'uncached input', color: 'var(--indigo)' }, { name: 'cache reads', color: 'var(--c6)' }, { name: 'output (reasoning counted once)', color: 'var(--teal)' }], { digits: 0, ariaLabel: 'Token components by instruction' }); }
      msel.addEventListener('change', drawT); drawT();
      det.appendChild(h('div', { class: 'table-wrap' }, [h('table', { class: 'data' }, [h('thead', {}, [h('tr', {}, ['Model', 'Instruction', 'n (usage coverage)', 'Uncached input', 'Cache reads', 'Output', 'Recorded total tokens'].map(function (t, i) { return h('th', { class: i > 1 ? 'num' : '', text: t }); }))]), h('tbody', {}, it.rows.map(function (r) { return h('tr', {}, [h('td', { text: r.model }), h('td', { text: r.instruction }), h('td', { class: 'num', text: String(r.n) }), h('td', { class: 'num', text: C.fmt(r.uncached_input, 0) }), h('td', { class: 'num', text: C.fmt(r.cache_reads, 0) }), h('td', { class: 'num', text: C.fmt(r.output, 0) }), h('td', { class: 'num', text: C.fmt(r.recorded_total, 0) })]); }))])]));
      det.appendChild(h('p', { class: 'small', text: it.source.caption.replace(/\[ref:[^\]]+\]/g, '') }));
      root.appendChild(det);
    }
    var cs = D.claims60_sensitivity, c6 = D.claims60_summary;
    if (cs) {
      var det3 = h('details', {}, [h('summary', { text: 'The 60-statement panel: instruction and subset sensitivity (Tables 14 and 15)' })]);
      var models60 = []; cs.rows.forEach(function (r) { if (models60.indexOf(r.model) < 0) models60.push(r.model); });
      var subsets = []; cs.rows.forEach(function (r) { if (subsets.indexOf(r.subset) < 0) subsets.push(r.subset); });
      var ssel = h('select', {}, subsets.map(function (x) { return h('option', { value: x, text: x }); }));
      var c60chart = h('div'), c60table = h('div', { class: 'table-wrap' });
      det3.appendChild(h('div', { class: 'controls' }, [h('label', {}, ['Subset ', ssel])]));
      det3.appendChild(c60chart); det3.appendChild(c60table);
      var armNames60 = { F: 'Full proof attempt', O: 'Ordinary early stop', W: 'Early stop, witness required' };
      function draw60() {
        var sub = ssel.value, rows60 = cs.rows.filter(function (r) { return r.subset === sub; });
        C.barGroups(c60chart, rows60.map(function (r) { return { label: r.model + ' · ' + (armNames60[r.arm] || r.arm), values: [v(r.output_ratio), v(r.recorded_total_ratio)] }; }), [{ name: 'output tokens, search ÷ comparator', color: 'var(--crimson)' }, { name: 'recorded total tokens, search ÷ comparator', color: 'var(--indigo)' }], { max: 1.5, digits: 3, ariaLabel: 'Token ratios on the 60-statement panel' });
        c60table.innerHTML = '';
        c60table.appendChild(h('table', { class: 'data' }, [h('thead', {}, [h('tr', {}, ['Model', 'Comparator arm', 'n', 'Confirmed: search / comparator', 'Output ratio', 'Recorded total ratio'].map(function (t, i) { return h('th', { class: i > 1 ? 'num' : '', text: t }); }))]), h('tbody', {}, rows60.map(function (r) { return h('tr', {}, [h('td', { text: r.model }), h('td', { text: armNames60[r.arm] || r.arm }), h('td', { class: 'num', text: String(v(r.n)) }), h('td', { class: 'num', text: r.catches_s_c.pair.join(' / ') }), h('td', { class: 'num', text: C.fmt(r.output_ratio, 3) }), h('td', { class: 'num', text: C.fmt(r.recorded_total_ratio, 3) })]); }))]));
      }
      ssel.addEventListener('change', draw60); draw60();
      det3.appendChild(h('p', { class: 'small', text: cs.source.caption.replace(/\[ref:[^\]]+\]/g, '') + (c6 ? ' Table 14 intervals: ' + c6.rows.map(function (r) { return r.model + ' output ' + C.fmt(r.output_ratio_s_w, 3) + ' [' + ci(r.output_ratio_s_w).join(', ') + '], recorded total ' + C.fmt(r.recorded_total_ratio_s_w, 3) + ' [' + ci(r.recorded_total_ratio_s_w).join(', ') + ']'; }).join('; ') + '.' : '') }));
      root.appendChild(det3);
    }
    if (is) {
      var det2 = h('details', {}, [h('summary', { text: 'Search versus sequential review with a counterexample required (Table 6)' })]);
      det2.appendChild(h('div', { class: 'table-wrap' }, [h('table', { class: 'data' }, [h('thead', {}, [h('tr', {}, is.header.map(function (t, i) { return h('th', { class: i ? 'num' : '', text: t }); }))]), h('tbody', {}, is.rows.map(function (r) { if (r.section) return h('tr', { class: 'is-highlight' }, [h('td', { colspan: '5', text: r.section })]); return h('tr', {}, [h('td', { text: r.model }), h('td', { class: 'num', text: String(v(r.search_confirmed)) }), h('td', { class: 'num', text: String(v(r.sequential_confirmed)) }), cell(r.output_ratio, 3), cell(r.recorded_total_ratio, 3)]); }))])]));
      det2.appendChild(h('p', { class: 'small', text: is.source.caption.replace(/\[ref:[^\]]+\]/g, '') }));
      root.appendChild(det2);
    }
  }

  /* ---------- repair ---------- */
  function repair(root) {
    var ro = D.repair_outcomes, rr = D.repair_resources; if (!ro) return;
    var solvers = []; ro.rows.forEach(function (r) { if (solvers.indexOf(r.solver) < 0) solvers.push(r.solver); });
    var chart = h('div'); root.appendChild(chart);
    C.barGroups(chart, solvers.map(function (s) { var a = ro.rows.filter(function (r) { return r.solver === s && r.condition === 'A'; })[0], b = ro.rows.filter(function (r) { return r.solver === s && r.condition === 'B'; })[0]; return { label: s, values: [a.pass, b.pass] }; }), [{ name: 'A: context, defect, repair template and required statements', color: 'var(--c6)' }, { name: 'B: the same plus the checked counterexample', color: 'var(--teal)' }], { max: 16, digits: 0, ariaLabel: 'First-attempt checker-accepted submissions out of 16' });
    root.appendChild(h('p', { class: 'caption', text: 'First-attempt checker-accepted submissions on the 16 source-derived repair tasks. Each solver received up to three attempts per task and condition; missing submissions count as failures.' }));
    root.appendChild(h('div', { class: 'table-wrap' }, [h('table', { class: 'data' }, [h('thead', {}, [h('tr', {}, ['Solver', 'Condition', 'PASS', 'FAIL', 'Absent', 'Recorded total tokens', 'Output tokens', 'Attempts with recorded usage'].map(function (t, i) { return h('th', { class: i > 1 ? 'num' : '', text: t }); }))]), h('tbody', {}, ro.rows.map(function (r) { var res = rr ? rr.rows.filter(function (x) { return x.condition === r.condition && r.solver.indexOf(x.configuration.replace('Claude ', '')) >= 0; })[0] : null; return h('tr', {}, [h('td', { text: r.solver }), h('td', { text: r.condition }), h('td', { class: 'num', text: String(r.pass) }), h('td', { class: 'num', text: String(r.fail) }), h('td', { class: 'num', text: String(r.absent) }), h('td', { class: 'num', text: res ? ((res.recorded_total_tokens.lower_bound ? '≥ ' : '') + C.fmt(v(res.recorded_total_tokens), 0)) : '—' }), h('td', { class: 'num', text: res ? ((res.output_tokens.lower_bound ? '≥ ' : '') + C.fmt(v(res.output_tokens), 0)) : '—' }), h('td', { class: 'num', text: res ? res.attempts_with_recorded_usage.pair.join('/') : '—' })]); }))])]));
    root.appendChild(scope('This tests completing a specified correction, not discovering an unknown repair: both conditions supply the source context, definitions, identified defect, repair template and required proof statements; condition B adds the checked counterexample. The fixed checker accepts a submission when its edits are allowed and its proofs establish the requested correction for all permitted inputs, show that the hypotheses admit an example, and establish any task-specific endpoint properties. Token totals marked ≥ have attempts without recorded usage.'));
  }

  /* ---------- proof development ---------- */
  function development(root) {
    var pd = D.proof_development, op = D.open_problem_retrieval; if (!pd) return;
    var chart = h('div'); root.appendChild(chart);
    C.barGroups(chart, pd.rows.map(function (r) { var p = r.graded_correct_bugbank_plain.pair; return { label: r.model + ' · ' + r.protocol + ' rule', values: [p[0], p[1]] }; }), [{ name: 'BugBank retrieval (up to three records per queried claim)', color: 'var(--indigo)' }, { name: 'Plain (iterative self-feedback)', color: 'var(--c6)' }], { max: 50, digits: 0, ariaLabel: 'Proofs judged correct out of 50 by condition' });
    root.appendChild(h('p', { class: 'caption', text: 'Proof development outcomes on 50 tasks per model: final drafts judged correct by model graders using the recorded rubric. The shared-rule protocol uses the same revision cap and stopping rule in both conditions; the original-protocol rows retain the earlier stopping rules as a separate comparison.' }));
    root.appendChild(h('div', { class: 'table-wrap' }, [h('table', { class: 'data' }, [h('thead', {}, [h('tr', {}, ['Model', 'Protocol', 'Graded correct (/50) B / P', 'Output tokens B / P', 'Recorded total tokens B / P', 'Total-token ratio B ÷ P [95% CI]'].map(function (t, i) { return h('th', { class: i > 1 ? 'num' : '', text: t }); }))]), h('tbody', {}, pd.rows.map(function (r) { return h('tr', {}, [h('td', { text: r.model }), h('td', { text: r.protocol }), h('td', { class: 'num', text: r.graded_correct_bugbank_plain.pair.join(' / ') }), h('td', { class: 'num', text: r.output_tokens_bugbank_plain.pair.map(function (x) { return C.fmt(x, 0); }).join(' / ') }), h('td', { class: 'num', text: r.recorded_total_bugbank_plain.pair.map(function (x) { return C.fmt(x, 0); }).join(' / ') }), cell(r.total_token_ratio, 3)]); }))])]));
    root.appendChild(scope('Under the shared rule the models differ: Opus used fewer recorded tokens with retrieval (ratio 0.696 [0.555, 0.887]) and had 44 proofs judged correct against 43; Sol and Gemini used more tokens with retrieval, with 45 against 47 and 43 against 42. Under the original stopping rules all three ratios exceeded one. Retrieving stored objections did not consistently increase the number of proofs judged correct, so the broader value of retrieval during proof development remains open. These tasks and the 661-entry retrieval database belong to this study alone.'));
    if (op) {
      var det = h('details', {}, [h('summary', { text: 'Retrieval in open-problem search: paired components (Table 13)' })]);
      det.appendChild(h('div', { class: 'table-wrap' }, [h('table', { class: 'data' }, [h('thead', {}, [h('tr', {}, ['Component', 'Paired units', 'Audited-full (B / P)', 'Both', 'B-only / P-only', 'Neither'].map(function (t, i) { return h('th', { class: i ? 'num' : '', text: t }); }))]), h('tbody', {}, op.rows.map(function (r) { return h('tr', {}, [h('td', { text: r.component }), h('td', { class: 'num', text: String(r.paired_units) }), h('td', { class: 'num', text: r.audited_full_b_p.pair.join(' / ') }), h('td', { class: 'num', text: String(r.both) }), h('td', { class: 'num', text: r.b_only_p_only.pair.join(' / ') }), h('td', { class: 'num', text: String(r.neither) })]); }))])]));
      det.appendChild(h('p', { class: 'small', text: 'A model audit accepted a full resolution of the stated target in 12 retrieval runs and 11 self-critique runs over 36 distinct final targets: eleven targets in both conditions, one only with retrieval, 24 in neither. ' + op.source.caption.replace(/\[ref:[^\]]+\]/g, '') }));
      root.appendChild(det);
    }
  }

  document.addEventListener('copeer:ready', function () {
    var root = document.getElementById('studies-panels'); if (!root) return;
    root.innerHTML = '';
    var tabs = h('div', { class: 'tabs', role: 'tablist', 'aria-label': 'Studies', 'data-tabs': '' }, [
      h('button', { role: 'tab', id: 'tab-instr', 'aria-controls': 'panel-instr', 'aria-selected': 'true', type: 'button', text: 'Instructions: search first or review step by step' }),
      h('button', { role: 'tab', id: 'tab-repair', 'aria-controls': 'panel-repair', 'aria-selected': 'false', type: 'button', text: 'Repair tasks with the correction given' }),
      h('button', { role: 'tab', id: 'tab-dev', 'aria-controls': 'panel-dev', 'aria-selected': 'false', type: 'button', text: 'Retrieval during proof revision' })]);
    var p1 = h('div', { role: 'tabpanel', id: 'panel-instr', 'aria-labelledby': 'tab-instr' }), p2 = h('div', { role: 'tabpanel', id: 'panel-repair', 'aria-labelledby': 'tab-repair', hidden: '' }), p3 = h('div', { role: 'tabpanel', id: 'panel-dev', 'aria-labelledby': 'tab-dev', hidden: '' });
    root.appendChild(tabs); root.appendChild(p1); root.appendChild(p2); root.appendChild(p3);
    instruction(p1); repair(p2); development(p3);
    C.initTabs(root); C.initSegmented(root);
    tabs.addEventListener('tabchange', function () { C._charts.forEach(function (c) { if (root.contains(c.container)) c.redraw(); }); });
  });
})();
