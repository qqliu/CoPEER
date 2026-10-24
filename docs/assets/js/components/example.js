/* Front-page example: three tabs (even/odd decomposition, Shellsort matched pair, square-root recurrence),
   the dossier anatomy, and the two source-correspondence implications wired to the active tab. */
(function () {
  'use strict';
  var C = window.COPEER, M = window.COPEER_MATH, D = window.COPEER_DATA || {};
  var h = C.h;

  function tex(s) { var span = h('span'); span.innerHTML = C.texToHtml(s); return span; }

  /* ---------- Tab 1: even/odd ---------- */
  function buildEvenOdd() {
    var ex = D.benchmark_example, rec = D.example_record;
    if (!ex) return;
    /* excerpt */
    var ol = document.getElementById('eo-excerpt');
    ex.excerpt_lines.forEach(function (l) {
      var li = h('li', { class: l.line === ex.reference_line ? 'is-flagged' : '' }, [h('span', { class: 'n', text: '[' + l.line + ']' }), tex(l.tex)]);
      if (l.line === ex.reference_line) li.appendChild(h('span', { class: 'badge badge-crimson', text: 'challenged step' }));
      ol.appendChild(li);
      if (l.line === 1 || l.line === 3) ol.appendChild(h('li', { class: 'is-ellipsis' }, [h('span', { class: 'n', text: '' }), '…']));
    });
    ol.appendChild(h('li', { class: 'is-ellipsis' }, [h('span', { class: 'n', text: '' }), '… (' + ex.numbered_lines_total + ' nonblank numbered lines in all)']));
    /* full text on request */
    if (rec && rec.source_lines) {
      var full = document.getElementById('eo-full-lines');
      rec.source_lines.forEach(function (l) { if (!l.text.trim()) return; full.appendChild(h('li', { class: String(l.label) === String(ex.reference_line) ? 'is-flagged' : '' }, [h('span', { class: 'n', text: /^\d+$/.test(l.label) ? '[' + l.label + ']' : l.label }), h('span', { text: l.text })])); });
    }
    /* check the step */
    var readout = document.getElementById('eo-readout');
    var btn = document.getElementById('eo-try'), reset = document.getElementById('eo-reset'), scope = document.getElementById('eo-scope');
    function initial() {
      readout.className = 'readout';
      readout.innerHTML = '';
      readout.appendChild(h('p', {}, ['The step asserts ', tex('$f(x)=f(-x)+(-f(x))$'), ' for every ', tex('$x$'), ' in the domain. Pick the simplest function allowed by the hypothesis: the constant function ', tex('$f\\equiv 1$'), '.']));
      scope.hidden = true; reset.hidden = true; btn.hidden = false;
    }
    btn.addEventListener('click', function () {
      var c = M.evenOdd.check('const1', 1);
      readout.className = 'readout fail';
      readout.innerHTML = '';
      readout.appendChild(h('p', {}, ['With ', tex('$f\\equiv 1$'), ' and ', tex('$x=1$'), ': left side ', tex('$f(1)=1$'), '; right side ', tex('$f(-1)+(-f(1))=1-1=0$'), '. ', h('strong', { class: 'fail', text: '1 ≠ 0' }), ', so the asserted identity is false. ', h('span', { class: 'badge badge-crimson', text: 'line 5 refuted' })]));
      readout.appendChild(h('p', { class: 'small', text: 'Computed in the page: lhs ' + c.lhs + ', rhs ' + c.rhs + '. The dossier\'s Lean certificate proves the same statement for the finite domain {−1, 1}; see "exact saved witness" below.' }));
      scope.hidden = false; reset.hidden = false; btn.hidden = true;
      C.renderMath(readout);
    });
    reset.addEventListener('click', initial);
    initial();
    /* illustration: other functions */
    var sel = document.getElementById('eo-fn'), range = document.getElementById('eo-x'), xval = document.getElementById('eo-xval'), ill = document.getElementById('eo-illustration');
    Object.keys(M.evenOdd.functions).forEach(function (k) { sel.appendChild(h('option', { value: k, text: M.evenOdd.functions[k].label })); });
    function update() {
      var k = sel.value, x = parseFloat(range.value);
      xval.textContent = x.toFixed(2);
      var r = M.evenOdd.check(k, x), d = M.evenOdd.decomposition(k, x);
      ill.className = 'readout ' + (r.fails ? 'fail' : 'ok');
      ill.innerHTML = '';
      ill.appendChild(h('p', {}, [M.evenOdd.functions[k].label + ' at x = ' + x.toFixed(2) + ': left side f(x) = ' + r.lhs.toPrecision(6) + '; right side f(−x) + (−f(x)) = ' + r.rhs.toPrecision(6) + '. ', r.fails ? h('strong', { class: 'fail', text: 'The identity fails at this x.' }) : h('strong', { class: 'ok', text: 'The identity happens to hold at this x, so this x is not a counterexample.' })]));
      ill.appendChild(h('p', { class: 'small', text: 'Valid decomposition at this x: even part (f(x)+f(−x))/2 = ' + d.even.toPrecision(6) + ', odd part (f(x)−f(−x))/2 = ' + d.odd.toPrecision(6) + ', sum ' + (d.even + d.odd).toPrecision(6) + '. Floating-point values; equality is judged to 1e-9 relative tolerance.' }));
    }
    sel.addEventListener('change', update); range.addEventListener('input', update); update();
    /* saved witness and record facts */
    var saved = document.getElementById('eo-saved');
    if (rec) {
      var m = rec.membership, rv = (m.review_evidence || [])[0];
      saved.appendChild(h('dl', { class: 'kv' }, [
        h('dt', { text: 'Record' }), h('dd', {}, [h('code', { text: rec.record_id })]),
        h('dt', { text: 'Exact saved witness' }), h('dd', {}, [tex('domain $D=\\{-1,1\\}$, $f\\equiv 1$, $x=1$')]),
        h('dt', { text: 'Lean-checked statement' }), h('dd', { text: ex.lean_statement_text }),
        h('dt', { text: 'Certificate' }), h('dd', {}, [C.repoLink(rec.certificate.path), ' · SHA-256 ', h('code', { text: rec.certificate.sha256.slice(0, 12) + '…' }), ' · axioms used: propext, Quot.sound; no sorry, no native reduction']),
        h('dt', { text: 'Human review (current layer)' }), h('dd', {}, [rv ? ('three questions ' + rv.answers.join(' / ') + ' (cohort ' + rv.cohort + ', locator ' + rv.review_locator + '); continuity ' + m.continuity.toLowerCase().replace(/_/g, ' ')) : 'see membership record', '; in the human-approved core' + (m.in_primary_100 ? ' and among the 100 primary benchmark inputs' : '')]),
        h('dt', { text: 'Reference line' }), h('dd', { text: 'line ' + m.current_gold.join(', ') }),
        h('dt', { text: 'Recorded critic selection' }), h('dd', { text: ex.recorded_selection.model + ' returned candidates [' + ex.recorded_selection.candidates.join(', ') + ']: Hit@1 = ' + ex.recorded_selection.hit1 + ', Hit@3 = ' + ex.recorded_selection.hit3 + ' (the critic does not see the reference evidence)' })
      ]));
      var pre = h('pre', { class: 'lean no-math', text: rec.certificate.text.trim() });
      var det = h('details', {}, [h('summary', { text: 'Show the Lean certificate (' + rec.certificate.text.length + ' bytes)' }), pre]);
      saved.appendChild(det);
    }
  }

  /* ---------- Tab 2: Shellsort ---------- */
  function arrayChips(arr, hi) { return h('span', { class: 'strip mono' }, arr.map(function (v, i) { return h('span', { class: hi && hi.indexOf(i) >= 0 ? 'alt' : '', text: String(v) }); })); }
  function buildShellsort() {
    var panel = document.getElementById('ss-cases'); if (!panel) return;
    var cases = [{ key: 'orig', title: 'Original witness (3, 4, 2, 5, 1)', arr: M.shellsort.original, verdict: 'rejected by source review' }, { key: 'repl', title: 'Replacement witness (3, 5, 2, 6, 1, 7, 4)', arr: M.shellsort.replacement, verdict: 'admitted' }];
    var stepState = {};
    cases.forEach(function (c) {
      var a = M.shellsort.analyse(c.arr, 2);
      var card = h('div', { class: 'card' });
      card.appendChild(h('h3', { text: c.title }));
      card.appendChild(h('p', {}, ['Input ', arrayChips(c.arr)]));
      var checks = h('ul', { class: 'small' }, [
        h('li', {}, [h('span', { class: 'badge ' + (a.endpointAssumptionHolds ? 'badge-teal' : 'badge-crimson'), text: a.endpointAssumptionHolds ? 'holds' : 'violated' }), ' Source assumption ', tex('$x_0 < x_n$'), ': ' + c.arr[0] + ' < ' + c.arr[c.arr.length - 1] + ' is ' + (a.endpointAssumptionHolds ? 'true' : 'false') + '.']),
        h('li', {}, [h('span', { class: 'badge badge-indigo', text: 'exchange' }), ' First gap-2 insertion exchanges ' + c.arr[0] + ' and ' + a.firstExchangedIntoZero + ', so ' + a.firstExchangedIntoZero + ' moves to the front.']),
        h('li', {}, [h('span', { class: 'badge badge-indigo', text: 'final' }), ' Final gap-2 sorted array ', arrayChips(a.final, [0]), ' begins with ' + a.finalFirst + ', not ' + a.firstExchangedIntoZero + '.']),
        h('li', {}, [h('span', { class: 'badge badge-crimson', text: 'claim fails' }), ' The challenged step ("that exchanged-in entry remains first") fails on this input.']),
        h('li', {}, [h('span', { class: 'badge badge-teal', text: 'Lean' }), ' A Lean-checked theorem establishes the failed conclusion for this array.']),
        h('li', {}, [h('span', { class: 'badge ' + (c.key === 'repl' ? 'badge-teal' : 'badge-crimson'), text: c.key === 'repl' ? 'admitted' : 'rejected' }), c.key === 'repl' ? ' The witness satisfies the source\'s endpoint assumption, so the objection applies to the source claim.' : ' The formal premise omitted the endpoint assumption; the objection does not apply to the source claim as stated.'])
      ]);
      card.appendChild(checks);
      /* stepper */
      var stepper = h('div', { class: 'panel' });
      var pos = h('p', { class: 'small' });
      var view = h('div');
      var idx = -1;
      function show() {
        view.innerHTML = '';
        if (idx < 0) { view.appendChild(arrayChips(c.arr)); pos.textContent = 'Start of the gap-2 insertion pass. Entries two positions apart are compared and exchanged when out of order.'; }
        else { var st = a.steps[idx]; view.appendChild(arrayChips(st.array, st.swapped)); pos.textContent = 'Exchange ' + (idx + 1) + ' of ' + a.steps.length + ': positions ' + st.swapped[0] + ' and ' + st.swapped[1] + ' swapped' + (st.swapped[0] === 0 ? ' (position 0 changes)' : '') + '.'; }
        prev.disabled = idx < 0; next.disabled = idx >= a.steps.length - 1;
      }
      var prev = h('button', { class: 'btn btn-small', type: 'button', text: 'Previous', onclick: function () { idx = Math.max(-1, idx - 1); show(); } });
      var next = h('button', { class: 'btn btn-small', type: 'button', text: 'Next exchange', onclick: function () { idx = Math.min(a.steps.length - 1, idx + 1); show(); } });
      stepper.appendChild(h('div', { class: 'controls' }, [prev, next]));
      stepper.appendChild(view); stepper.appendChild(pos);
      show();
      card.appendChild(stepper);
      panel.appendChild(card);
      stepState[c.key] = a;
    });
    C.renderMath(panel);
  }

  /* ---------- Tab 3: square root ---------- */
  function buildSqrt() {
    var tbody = document.getElementById('sq-rows'); if (!tbody) return;
    var sel = document.getElementById('sq-max'), summary = document.getElementById('sq-summary');
    function render() {
      var maxX = parseInt(sel.value, 10), rows = M.sqrt.table(maxX), fails = [];
      tbody.innerHTML = '';
      rows.forEach(function (r) {
        if (r.fails) fails.push(r.x);
        tbody.appendChild(h('tr', { class: r.fails ? 'is-highlight' : '' }, [h('td', { class: 'num', text: String(r.x) }), h('td', { class: 'num', text: String(r.printed) }), h('td', { class: 'num', text: String(r.truth) }), h('td', { class: 'num', text: String(r.repaired) }), h('td', {}, [r.fails ? h('span', { class: 'badge badge-crimson', text: 'fails (perfect square)' }) : h('span', { class: 'badge badge-muted', text: 'agrees' })])]));
      });
      summary.textContent = 'Inputs 0 to ' + maxX + ': the printed recurrence disagrees with ⌊√x⌋ exactly at x = ' + fails.join(', ') + ' (' + fails.length + ' positive perfect squares); the strict guard agrees everywhere. Computed in the page; the proposition proves it for every natural number.';
    }
    sel.addEventListener('change', render); render();
  }

  /* ---------- anatomy and implications ---------- */
  var anatomy = {
    source: { title: 'Source and claim', text: 'The saved source version, quoted passage, selected assertion, and the assumptions under which that assertion is claimed to hold.' },
    witness: { title: 'Counterexample and proof', text: 'The concrete witness, formal definitions, and exact named Lean theorem proving that the encoded assumptions hold and the encoded conclusion fails for the witness.' },
    checking: { title: 'Checking record', text: 'File identifiers, dependencies, build logs, and the axioms and assumptions used by the formal proof.' },
    review: { title: 'Review and consequence', text: 'Assessments of source correspondence and of what the objection shows about the surrounding argument (local or global), with the reviewer (human or model), reviewed version, verdict, and any unresolved concerns recorded for each assessment.' }
  };
  function buildAnatomy() {
    var box = document.getElementById('anatomy'), desc = document.getElementById('anatomy-desc'); if (!box) return;
    Object.keys(anatomy).forEach(function (k, i) {
      var b = h('button', { type: 'button', 'aria-expanded': 'false', 'aria-controls': 'anatomy-desc' }, [anatomy[k].title, h('span', { class: 'sub', text: ['what was claimed, under which assumptions', 'the witness and its Lean theorem', 'how the proof was checked', 'does it fit the source; what follows'][i] })]);
      b.addEventListener('click', function () { box.querySelectorAll('button').forEach(function (x) { x.setAttribute('aria-expanded', 'false'); }); b.setAttribute('aria-expanded', 'true'); desc.innerHTML = ''; desc.appendChild(h('strong', { text: anatomy[k].title + '. ' })); desc.appendChild(document.createTextNode(anatomy[k].text)); });
      box.appendChild(b);
    });
    box.querySelector('button').click();
  }
  function setImplications(mode) {
    var el = document.getElementById('implications'); if (!el) return;
    var rows;
    if (mode === 'shellsort') rows = [
      ['Formal certificate: encoded assumptions hold and the encoded conclusion fails at the witness', 'ok', 'ok'],
      ['Implication 1: the encoded assumptions imply the source assumptions at the witness', 'fail', 'ok'],
      ['Implication 2: the source conclusion at the witness would imply the encoded conclusion', 'ok', 'ok'],
      ['Counterexample to the source assertion', 'fail', 'ok']];
    else if (mode === 'sqrt') rows = [
      ['Formal certificate (failure at the natural-number input x = 1)', 'ok', null],
      ['Implication 1: the input also satisfies the source\'s integer specification', 'ok', null],
      ['Source review of the original dossier: a human reviewer questioned its reading of the source', 'questioned', null],
      ['Status: outside the human-approved core; the family-level proposition is stated and proved separately', 'note', null]];
    else rows = [
      ['Formal certificate: domain closed under negation, 1 in the domain, f(1) ≠ f(−1) + (−f(1))', 'ok', null],
      ['Implication 1: the encoded hypothesis is the source\'s only hypothesis (domain closed under negation)', 'ok', null],
      ['Implication 2: if the source identity held at x = 1 the encoded identity would hold', 'ok', null],
      ['Counterexample to the source assertion at line 5 (local: the theorem is true)', 'ok', null]];
    var heads = mode === 'shellsort' ? ['original', 'replacement'] : ['status'];
    var table = h('table', { class: 'data' }, [h('thead', {}, [h('tr', {}, [h('th', { text: 'What must hold' })].concat(heads.map(function (x) { return h('th', { text: x }); })))]), h('tbody', {}, rows.map(function (r) {
      return h('tr', {}, [h('td', { class: 'text', text: r[0] })].concat(r.slice(1).filter(function (x, i) { return i < heads.length; }).map(function (v) { return h('td', {}, [v === null ? '' : h('span', { class: 'badge ' + (v === 'ok' ? 'badge-teal' : v === 'fail' ? 'badge-crimson' : 'badge-amber'), text: v === 'ok' ? 'holds' : v === 'fail' ? 'fails' : v === 'questioned' ? 'questioned' : 'note' })]); })));
    }))]);
    el.innerHTML = ''; el.appendChild(table);
  }

  document.addEventListener('copeer:ready', function () {
    buildEvenOdd(); buildShellsort(); buildSqrt(); buildAnatomy();
    var tabs = document.getElementById('example-tabs');
    function modeOf(id) { return id === 'tab-shellsort' ? 'shellsort' : id === 'tab-sqrt' ? 'sqrt' : 'evenodd'; }
    var selected = tabs ? tabs.querySelector('[role="tab"][aria-selected="true"]') : null;
    setImplications(modeOf(selected ? selected.id : 'tab-evenodd'));
    if (tabs) tabs.addEventListener('tabchange', function (e) { setImplications(modeOf(e.detail.id)); });
    C.renderMath(document.getElementById('example'));
  });
})();
