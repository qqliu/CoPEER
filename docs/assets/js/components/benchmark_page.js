/* Benchmark page: complete results for the 14 reporting views, baselines, settings, and the localization exercise. */
(function () {
  'use strict';
  var C = window.COPEER, D = window.COPEER_DATA || {}, h = C.h;
  var loaded = {};
  function loadRecord(id) {
    return new Promise(function (resolve, reject) {
      if (window.COPEER_RECORDS && window.COPEER_RECORDS[id]) return resolve(window.COPEER_RECORDS[id]);
      if (loaded[id]) return loaded[id].then(resolve, reject);
      loaded[id] = new Promise(function (res, rej) { var s = document.createElement('script'); s.src = 'data/records/' + encodeURIComponent(id) + '.js'; s.onload = function () { res(window.COPEER_RECORDS[id]); }; s.onerror = function () { rej(new Error('record not found: ' + id)); }; document.head.appendChild(s); });
      loaded[id].then(resolve, reject);
    });
  }

  /* ---------- complete results ---------- */
  function results() {
    var V = D.views; if (!V) return;
    var chart = document.getElementById('b-chart'), seg = document.getElementById('b-metric'), popSeg = document.getElementById('b-pop'), cap = document.getElementById('b-caption'), tbody = document.getElementById('b-rows');
    function draw() {
      var metric = C.segValue(seg) || 'hit1', pop = C.segValue(popSeg) || 'primary';
      var rows = V.views.slice().sort(function (a, b) { return b[pop][metric].percent - a[pop][metric].percent; }).map(function (vw) { var s = vw[pop][metric]; return { label: vw.name + (vw.main_table ? '' : ' †'), value: s.percent, lo: s.ci95[0] * 100, hi: s.ci95[1] * 100 }; });
      var tf = V.baselines.tfidf_centroid_line;
      C.dotPlot(chart, rows, { unit: '%', ariaLabel: (metric === 'hit1' ? 'Hit@1' : 'Hit@3') + ' for all reporting views', refLine: metric === 'hit1' && pop === 'primary' ? tf.percent : null, refLabel: 'TF-IDF centroid ' + C.fmt(tf.percent, 1) + '%' });
      cap.textContent = (metric === 'hit1' ? 'Hit@1' : 'Hit@3') + ' on the ' + (pop === 'primary' ? V.primary_denominator + ' primary inputs (' + V.n_problem_clusters + ' problem clusters)' : V.supplementary_denominator + ' scorable inputs including the 31 shorter supplementary texts') + ', with 95% clustered bootstrap intervals from the released replay. † marks the two reporting views of the Haiku 4.5 configuration, which the paper\'s main table (12 configurations) omits; the views are two reporting scopes of one lane, share calls, and their costs must not be added.';
    }
    seg.addEventListener('change', draw); popSeg.addEventListener('change', draw); draw();
    V.views.forEach(function (vw) {
      var p = vw.primary, s = vw.supplementary;
      var tr = h('tr', {});
      tr.appendChild(h('td', { text: vw.name + (vw.main_table ? '' : ' †') }));
      tr.appendChild(h('td', { class: 'num', 'data-value': String(p.hit1.percent) }, [C.fmt(p.hit1.percent, 1), h('span', { class: 'ci', text: ' [' + C.fmt(p.hit1.ci95[0] * 100, 1) + ', ' + C.fmt(p.hit1.ci95[1] * 100, 1) + ']' })]));
      tr.appendChild(h('td', { class: 'num', 'data-value': String(p.hit3.percent) }, [C.fmt(p.hit3.percent, 1), h('span', { class: 'ci', text: ' [' + C.fmt(p.hit3.ci95[0] * 100, 1) + ', ' + C.fmt(p.hit3.ci95[1] * 100, 1) + ']' })]));
      tr.appendChild(h('td', { class: 'num', 'data-value': String(s.hit1.percent), text: C.fmt(s.hit1.percent, 1) }));
      tr.appendChild(h('td', { class: 'num', 'data-value': String(s.hit3.percent), text: C.fmt(s.hit3.percent, 1) }));
      var t16 = (D.localization_full ? D.localization_full.rows : []).filter(function (r) { return r.name.replace('TF–IDF', 'TF-IDF') === vw.name; })[0];
      tr.appendChild(h('td', { class: 'num', 'data-value': t16 ? String(C.val(t16.recorded_total_tokens)) : '', text: t16 ? ((t16.recorded_total_tokens && t16.recorded_total_tokens.lower_bound ? '≥ ' : '') + C.fmt(C.val(t16.recorded_total_tokens), 0)) : '—' }));
      tr.appendChild(h('td', { class: 'num', 'data-value': t16 ? String(C.val(t16.recorded_output_tokens)) : '', text: t16 ? C.fmt(C.val(t16.recorded_output_tokens), 0) : '—' }));
      var misses = p.rule_misses_by_cause || {};
      tr.appendChild(h('td', { class: 'small', text: Object.keys(misses).length ? Object.keys(misses).map(function (k) { return k.replace(/_/g, ' ') + ' ' + misses[k]; }).join(', ') : '—' }));
      tbody.appendChild(tr);
    });
    C.makeSortable(document.getElementById('b-table'));
    var bl = document.getElementById('b-baselines');
    var baseNames = { tfidf_centroid_line: 'TF-IDF centroid line', most_word_tokens: 'Most word tokens', most_math_symbols: 'Most mathematical symbols', longest_line_chars: 'Longest line (characters)', random_line: 'Uniform random line (analytical expectation)' };
    Object.keys(V.baselines).sort(function (a, b) { return V.baselines[b].percent - V.baselines[a].percent; }).forEach(function (k) { var b = V.baselines[k]; bl.appendChild(h('tr', {}, [h('td', { text: baseNames[k] || k.replace(/_/g, ' ') }), h('td', { class: 'num', text: C.fmt(b.percent, 1) }), h('td', { class: 'num', text: '[' + C.fmt(b.ci95[0] * 100, 1) + ', ' + C.fmt(b.ci95[1] * 100, 1) + ']' })])); });
  }

  /* ---------- settings ---------- */
  function settings() {
    var es = D.execution_settings, lm = D.local_models;
    if (es) { var t = document.getElementById('b-settings'); es.rows.forEach(function (r) { var tr = h('tr', {}); tr.appendChild(h('td', { text: r.model })); tr.appendChild(h('td', { class: 'num', text: r.context_tokens && typeof r.context_tokens === 'object' ? 'not recorded' : C.fmt(r.context_tokens, 0) })); var td = h('td'); td.innerHTML = C.texToHtml(r.generation_setting); tr.appendChild(td); tr.appendChild(h('td', { text: r.interface })); t.appendChild(tr); }); }
    if (lm) { var t2 = document.getElementById('b-models'); lm.rows.forEach(function (r) { var repo = r.repository.split(' ')[0]; var extra = r.repository.slice(repo.length).trim(); t2.appendChild(h('tr', {}, [h('td', { text: r.label }), h('td', {}, [h('a', { href: 'https://huggingface.co/' + repo, rel: 'noopener' }, [h('code', { text: repo })]), extra ? ' ' + extra : ''])])); }); }
  }

  /* ---------- exercise ---------- */
  function exercise() {
    var inputs = D.benchmark_inputs, V = D.views; if (!inputs) return;
    var sel = document.getElementById('e-input'), rnd = document.getElementById('e-random'), lines = document.getElementById('e-lines'), picks = document.getElementById('e-picks'), score = document.getElementById('e-score'), reveal = document.getElementById('e-reveal'), scoreBtn = document.getElementById('e-score-btn'), clearBtn = document.getElementById('e-clear'), status = document.getElementById('e-status'), tutorial = document.getElementById('e-tutorial');
    inputs.rows.forEach(function (r) { sel.appendChild(h('option', { value: r.id, text: (r.primary ? '' : '(supplementary) ') + r.id + ' · ' + r.group_name + ' · ' + r.n_lines + ' lines' })); });
    var current = null, chosen = [];
    function setStatus(t) { status.textContent = t; }
    function renderLines(rec) {
      lines.innerHTML = ''; chosen = []; picks.textContent = 'No lines chosen yet.'; score.innerHTML = ''; reveal.innerHTML = ''; reveal.hidden = true;
      rec.source_lines.forEach(function (l) {
        if (!l.text.trim()) return;
        var numbered = /^\d+$/.test(l.label);
        var li = h('li', { class: numbered ? '' : 'is-context', tabindex: numbered ? '0' : null, role: numbered ? 'button' : null, 'aria-pressed': numbered ? 'false' : null, 'data-line': l.label }, [h('span', { class: 'n', text: numbered ? '[' + l.label + ']' : l.label }), h('span', { text: l.text })]);
        if (numbered) { var toggle = function () { var n = parseInt(l.label, 10), k = chosen.indexOf(n); if (k >= 0) chosen.splice(k, 1); else { if (chosen.length >= 3) { setStatus('You may choose at most three lines; remove one first.'); return; } chosen.push(n); } li.setAttribute('aria-pressed', k >= 0 ? 'false' : 'true'); picks.textContent = chosen.length ? 'Your ranked choices: ' + chosen.map(function (x, i) { return (i + 1) + '. line ' + x; }).join(', ') : 'No lines chosen yet.'; setStatus(''); }; li.addEventListener('click', toggle); li.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); } }); }
        lines.appendChild(li);
      });
      lines.classList.add('selectable');
    }
    var wanted = null;
    function load(id) {
      current = null; wanted = id; setStatus('Loading ' + id + '…');
      loadRecord(id).then(function (rec) { if (wanted !== id) return; current = rec; renderLines(rec); setStatus(''); tutorial.hidden = id !== 'reddit_learnmath_dm6itc'; history.replaceState(null, '', '#input=' + encodeURIComponent(id)); }, function (e) { if (wanted === id) setStatus(e.message); });
    }
    sel.addEventListener('change', function () { load(sel.value); });
    rnd.addEventListener('click', function () { var prim = inputs.rows.filter(function (r) { return r.primary && r.id !== 'reddit_learnmath_dm6itc'; }); var pick = prim[Math.floor(Math.random() * prim.length)]; sel.value = pick.id; load(pick.id); });
    sel.insertBefore(h('option', { value: '', text: '— choose an input —' }), sel.firstChild);
    clearBtn.addEventListener('click', function () { if (current) renderLines(current); });
    scoreBtn.addEventListener('click', function () {
      if (!current) return;
      var gold = (current.index.current_gold || []).map(Number);
      if (!chosen.length) { setStatus('Choose up to three lines first.'); return; }
      var hit1 = gold.indexOf(chosen[0]) >= 0 ? 1 : 0, hit3 = chosen.some(function (x) { return gold.indexOf(x) >= 0; }) ? 1 : 0;
      score.innerHTML = ''; score.className = 'readout ' + (hit3 ? 'ok' : 'fail');
      score.appendChild(h('p', {}, [h('strong', { class: hit1 ? 'ok' : 'fail', text: 'Hit@1 = ' + hit1 }), '  ', h('strong', { class: hit3 ? 'ok' : 'fail', text: 'Hit@3 = ' + hit3 }), '. Reference line' + (gold.length > 1 ? 's' : '') + ': ' + gold.join(', ') + '. Your choices: ' + chosen.join(', ') + '.']));
      /* reveal (idempotent) */
      Array.prototype.forEach.call(lines.querySelectorAll('li[data-line]'), function (li) { var n = parseInt(li.getAttribute('data-line'), 10); if (gold.indexOf(n) >= 0 && !li.classList.contains('is-flagged')) { li.classList.add('is-flagged'); li.appendChild(h('span', { class: 'badge badge-crimson', text: 'reference line' })); } });
      reveal.hidden = false; reveal.innerHTML = '';
      var f = current.fields || {};
      reveal.appendChild(h('h4', { text: 'The held-out evidence' }));
      if (f.claim_quote) reveal.appendChild(h('p', {}, [h('strong', { text: 'Quoted challenged claim. ' }), f.claim_quote]));
      if (f.witness) reveal.appendChild(h('details', { open: '' }, [h('summary', { text: 'Counterexample (witness)' }), h('pre', { class: 'wrap no-math', text: f.witness })]));
      if (f.explanation) reveal.appendChild(h('details', {}, [h('summary', { text: 'Explanation' }), h('pre', { class: 'wrap no-math', text: f.explanation })]));
      if (V) {
        var t = h('table', { class: 'data' }, [h('thead', {}, [h('tr', {}, ['Configuration', 'Recorded candidates', 'Hit@1', 'Hit@3', 'Attempt'].map(function (x, i) { return h('th', { class: i >= 1 && i < 4 ? 'num' : '', text: x }); }))]), h('tbody', {}, V.views.map(function (vw) { var sv = current.selections[vw.view_id] || {}, o = sv.outcome || {}; return h('tr', {}, [h('td', { text: vw.name }), h('td', { class: 'num', text: sv.candidates ? '[' + sv.candidates.join(', ') + ']' : '—' }), h('td', { class: 'num', text: o.hit1 === undefined || o.hit1 === null ? '—' : String(o.hit1) }), h('td', { class: 'num', text: o.hit3 === undefined || o.hit3 === null ? '—' : String(o.hit3) }), h('td', { class: 'small', text: (o.attempt_class || '—') + (o.cause && o.cause !== 'None' ? ' (' + o.cause + ')' : '') })]); }))]);
        reveal.appendChild(h('details', { open: '' }, [h('summary', { text: 'How the evaluated configurations did on this input' }), h('div', { class: 'table-wrap' }, [t])]));
      }
      reveal.appendChild(h('p', { class: 'small' }, [h('a', { href: 'bugbank.html#record=' + encodeURIComponent(current.id), text: 'Open this dossier in the explorer' }), ' (certificate, reviews, full record).']));
      C.renderMath(reveal);
    });
    function starter() { var prim = inputs.rows.filter(function (r) { return r.primary && r.id !== 'reddit_learnmath_dm6itc' && r.n_lines <= 30; }); if (!prim.length) prim = inputs.rows.filter(function (r) { return r.primary; }); return prim[Math.floor(Math.random() * prim.length)].id; }
    var m = /input=([^&]+)/.exec(location.hash);
    var start = m ? decodeURIComponent(m[1]) : null;
    if (start && !inputs.rows.some(function (r) { return r.id === start; })) { setStatus('The requested record "' + start + '" is not among the 131 current benchmark inputs (it may be a released dossier outside the benchmark roster). Choose an input above or draw a random one.'); sel.value = ''; return; }
    if (!start) start = starter();
    sel.value = start; load(start);
  }

  document.addEventListener('copeer:ready', function () { results(); settings(); exercise(); C.renderMath(document.body); });
})();
