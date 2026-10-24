/* Evidence section: the search-outcome bar and the BugBank tiers, composition tables and review rounds. */
(function () {
  'use strict';
  var C = window.COPEER, D = window.COPEER_DATA || {}, h = C.h;

  function outcomesBar() {
    var w = D.workflow_counts, box = document.getElementById('outcomes'); if (!w || !box) return;
    var segs = [{ k: 'witnesses', label: 'witness found', v: w.witnesses, color: 'var(--c3)', ink: 'var(--c3-ink)' }, { k: 'exhaustive', label: 'exhaustive search, no witness in the finite set', v: w.exhaustive_without_witness, color: 'var(--c1)', ink: 'var(--c1-ink)' }, { k: 'inconclusive', label: 'inconclusive', v: w.inconclusive, color: 'var(--c6)', ink: 'var(--c6-ink)' }, { k: 'outside', label: 'outside the permitted setting', v: w.outside_permitted_setting, color: 'var(--c4)', ink: 'var(--c4-ink)' }];
    var width = 720, height = 54, x = 0;
    var svg = C.svg('svg', { class: 'chart', viewBox: '0 0 ' + width + ' ' + height, role: 'img', 'aria-label': 'Outcomes of ' + w.executable_tasks + ' executable search tasks' });
    segs.forEach(function (s) { var ww = s.v / w.executable_tasks * width; var g = C.svg('g', {}); g.appendChild(C.svg('title', { text: s.label + ': ' + s.v })); var r = C.svg('rect', { x: x, y: 8, width: ww, height: 28, rx: 2 }); r.style.fill = s.color; g.appendChild(r); if (ww > 34) { var tv = C.svg('text', { class: 'bar-val', x: x + ww / 2, y: 27, 'text-anchor': 'middle', text: String(s.v) }); tv.style.fill = s.ink; g.appendChild(tv); } svg.appendChild(g); x += ww; });
    box.appendChild(h('div', { class: 'chart-wrap' }, [svg]));
    box.appendChild(h('div', { class: 'legend' }, segs.map(function (s) { var sw = h('span', { class: 'sw' }); sw.style.background = s.color; return h('span', {}, [sw, s.v + ' ' + s.label]); })));
    box.appendChild(h('p', { class: 'small', text: 'Of the ' + w.witnesses + ' proposed witnesses, separately written checkers confirmed ' + w.checker_confirmed + ' and rejected ' + w.checker_rejected + '; all ' + w.programs_replayed + ' search and checker programs passed exact-arithmetic inspection and deterministic replay. A separate stage checked ' + w.selected_algorithmic_failures_checked + ' selected algorithmic failures and confirmed all ' + w.selected_algorithmic_failures_confirmed + '.' }));
  }

  function tiers() {
    var box = document.getElementById('tiers'); if (!box) return;
    var items = [
      { count: 'BugBank collection', what: 'BugBank: every dossier the workflow produced, with whatever reviews it received. Membership is not human approval. The public release holds 284 screened dossiers, each with its source passage, counterexample and Lean certificate.' },
      { count: '147', what: 'Human-approved core, from 137 distinct sources: dossiers with all-YES human judgments on the three questions (source interpretation, counterexample validity, correspondence with the Lean statement), with recorded version continuity.' },
      { count: '100', what: 'Primary benchmark inputs, from 92 problem clusters: core dossiers whose texts have at least ten nonblank lines; 31 shorter texts form a supplementary evaluation set.' }];
    items.forEach(function (it, i) { var ring = h('div', { class: 'ring' }, [h('div', { class: 'count', text: it.count }), h('div', { class: 'what', text: it.what })]); ring.style.marginLeft = (i * 1.5) + 'rem'; box.appendChild(ring); });
  }

  function composition() {
    var cc = D.core_composition, box = document.getElementById('composition'); if (!cc || !box) return;
    function table(title, rows, key) {
      var t = h('table', { class: 'data' }, [h('thead', {}, [h('tr', {}, [h('th', { text: title }), h('th', { class: 'num', text: 'Dossiers' }), h('th', { class: 'num', text: 'Inputs' })])]), h('tbody', {}, rows.map(function (r) { return h('tr', { class: /^Total/.test(r[key]) ? 'is-highlight' : '' }, [h('td', { text: r[key] }), h('td', { class: 'num', text: String(r.dossiers) }), h('td', { class: 'num', text: String(r.inputs) })]); }))]);
      return h('div', { class: 'table-wrap' }, [t]);
    }
    box.appendChild(table('Source collection', cc.by_source_collection, 'source_collection'));
    box.appendChild(table('Error mechanism', cc.by_error_mechanism, 'error_mechanism'));
  }

  function reviewRounds() {
    var rv = D.review_rounds, an = D.audit_nonapprovals, box = document.getElementById('review-rounds'); if (!rv || !box) return;
    var t = h('table', { class: 'data' }, [h('caption', { class: 'sr-only', text: 'Human-review rounds' }), h('thead', {}, [h('tr', {}, ['Round', 'Frame and selection', 'Purpose', 'Outcome'].map(function (x) { return h('th', { text: x }); }))]), h('tbody', {}, rv.rows.map(function (r) { var tr = h('tr', {}); ['round', 'frame_and_selection', 'purpose', 'outcome'].forEach(function (k) { var td = h('td', { class: 'text' }); td.innerHTML = C.texToHtml(r[k]); tr.appendChild(td); }); return tr; }))]);
    box.appendChild(h('div', { class: 'table-wrap' }, [t]));
    if (an) {
      var t2 = h('table', { class: 'data' }, [h('thead', {}, [h('tr', {}, ['Packet', 'Earlier set', 'Negative checks', 'Recorded concern', 'Certificate version'].map(function (x) { return h('th', { text: x }); }))]), h('tbody', {}, an.rows.map(function (r) { var tr = h('tr', {}); tr.appendChild(h('td', { text: r.packet })); tr.appendChild(h('td', { text: r.earlier_set })); tr.appendChild(h('td', { text: r.negative_checks })); var td = h('td', { class: 'text' }); td.innerHTML = C.texToHtml(r.recorded_concern); tr.appendChild(td); tr.appendChild(h('td', {}, [h('code', { text: r.certificate_version })])); return tr; }))]);
      var det = h('details', {}, [h('summary', { text: 'The nine nonapprovals in the final random audit (all excluded from the core)' }), h('div', { class: 'table-wrap' }, [t2]), h('p', { class: 'small', text: an.source.caption.replace(/\[ref:[^\]]+\]/g, '') })]);
      box.appendChild(det);
    }
  }

  document.addEventListener('copeer:ready', function () { outcomesBar(); tiers(); composition(); reviewRounds(); C.renderMath(document.getElementById('bugbank')); });
})();
