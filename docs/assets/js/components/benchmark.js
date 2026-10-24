/* Benchmark section: Table 1 as a dot plot with intervals and as a sortable table, Hit@1 / Hit@3 toggle. */
(function () {
  'use strict';
  var C = window.COPEER, D = window.COPEER_DATA || {}, h = C.h;

  function build() {
    var lm = D.localization_main, chart = document.getElementById('bench-chart'), tbody = document.getElementById('bench-rows'); if (!lm || !chart) return;
    var models = lm.rows.filter(function (r) { return r.kind === 'model'; });
    var baselines = lm.rows.filter(function (r) { return r.kind === 'baseline'; });
    var seg = document.getElementById('bench-metric');
    function draw() {
      var metric = C.segValue(seg) || 'hit1';
      var rows = models.slice().sort(function (a, b) { return C.val(b[metric]) - C.val(a[metric]) || C.val(b.hit1) - C.val(a.hit1); }).map(function (r) { var ci = C.ci(r[metric]); return { label: r.name, value: C.val(r[metric]), lo: ci && ci[0], hi: ci && ci[1] }; });
      var tf = baselines.filter(function (b) { return /TF/.test(b.name); })[0];
      C.dotPlot(chart, rows, { unit: '%', ariaLabel: (metric === 'hit1' ? 'Hit@1' : 'Hit@3') + ' by model configuration with 95% intervals', refLine: metric === 'hit1' && tf ? C.val(tf.hit1) : null, refLabel: metric === 'hit1' && tf ? 'best simple text rule ' + C.fmt(C.val(tf.hit1), 1) + '%' : '' });
      document.getElementById('bench-caption').textContent = (metric === 'hit1' ? 'First choice is a reference line (Hit@1), ' : 'Reference line among the first three choices (Hit@3), ') + 'percent of the 100 primary inputs, with 95% clustered bootstrap intervals over the 92 problem clusters. Responses that do not meet the rules count as misses.' + (metric === 'hit1' ? ' The dashed line is the TF-IDF centroid baseline (18.0%); the random-line expectation is 6.7%. One-line baselines have no top-three result.' : '');
    }
    seg.addEventListener('change', draw); draw();
    /* table */
    lm.rows.forEach(function (r) {
      var tr = h('tr', { class: r.kind === 'baseline' ? 'no-sort' : '' });
      tr.appendChild(h('td', { text: r.name }));
      [r.hit1, r.hit3].forEach(function (v) { var ci = C.ci(v); tr.appendChild(h('td', { class: 'num', 'data-value': v === null ? '' : String(C.val(v)) }, [v === null ? '—' : C.fmt(C.val(v), 1), ci ? h('span', { class: 'ci', text: ' [' + C.fmt(ci[0], 1) + ', ' + C.fmt(ci[1], 1) + ']' }) : null])); });
      tr.appendChild(h('td', { class: 'num', 'data-value': r.recorded_total_tokens === null ? '' : String(C.val(r.recorded_total_tokens)), text: r.recorded_total_tokens === null ? '—' : C.fmt(C.val(r.recorded_total_tokens), 0) }));
      tr.appendChild(h('td', { class: 'num', 'data-value': r.met_rules_of_100 === null ? '' : String(r.met_rules_of_100), text: r.met_rules_of_100 === null ? '—' : String(r.met_rules_of_100) }));
      tbody.appendChild(tr);
    });
    C.makeSortable(document.getElementById('bench-table'));
  }
  document.addEventListener('copeer:ready', build);
})();
