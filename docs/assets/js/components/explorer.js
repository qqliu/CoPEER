/* BugBank explorer: filter and search the released dossiers; load a record's detail on demand (classic script). */
(function () {
  'use strict';
  var C = window.COPEER, D = window.COPEER_DATA || {}, h = C.h;
  var loaded = {};

  function loadRecord(id) {
    return new Promise(function (resolve, reject) {
      if (window.COPEER_RECORDS && window.COPEER_RECORDS[id]) return resolve(window.COPEER_RECORDS[id]);
      if (loaded[id]) return loaded[id].then(resolve, reject);
      loaded[id] = new Promise(function (res, rej) {
        var s = document.createElement('script'); s.src = 'data/records/' + encodeURIComponent(id) + '.js';
        s.onload = function () { res(window.COPEER_RECORDS[id]); }; s.onerror = function () { rej(new Error('record not found: ' + id)); };
        document.head.appendChild(s);
      });
      loaded[id].then(resolve, reject);
    });
  }

  function ranges(nums) { var a = nums.slice().sort(function (x, y) { return x - y; }), out = [], i = 0; while (i < a.length) { var j = i; while (j + 1 < a.length && a[j + 1] === a[j] + 1) j++; out.push(j - i >= 2 ? a[i] + '–' + a[j] : a.slice(i, j + 1).join(', ')); i = j + 1; } return out.join(', '); }
  function badge(text, kind) { return h('span', { class: 'badge badge-' + kind, text: text }); }
  function popBadges(r) {
    var out = [];
    if (r.primary) out.push(badge('primary benchmark input', 'indigo'));
    else if (r.scorable) out.push(badge('supplementary input', 'indigo'));
    if (r.core) out.push(badge('human-approved core', 'teal')); else out.push(badge('not in the core', 'muted'));
    if (r.benchmark_excluded) out.push(badge('benchmark-excluded', 'amber'));
    return out;
  }
  function reviewText(r) { if (!r.review || !r.review.length) return 'no recorded human review in the current layer'; return r.review.map(function (e) { return e.cohort + ' ' + e.locator + ': ' + (e.answers || []).join('/'); }).join('; '); }

  function build() {
    var idx = D.dossiers_index, views = D.views; if (!idx) return;
    var rows = idx.rows, counts = idx.counts;
    document.getElementById('x-counts').innerHTML = '';
    document.getElementById('x-counts').appendChild(h('div', { class: 'tier' }, [
      h('div', { class: 'ring' }, [h('div', { class: 'count', text: 'BugBank collection' }), h('div', { class: 'what', text: 'Every dossier the workflow produced. The public release holds ' + counts.released + ' screened dossiers, each with its source passage, counterexample and Lean certificate; ' + counts.with_any_all_yes_review + ' of them have at least one recorded all-YES human review.' })]),
      h('div', { class: 'ring' }, [h('div', { class: 'count', text: String(counts.core) }), h('div', { class: 'what', text: 'Human-approved core from 137 distinct sources: all-YES human judgments on the three questions with recorded version continuity (113 with exact current scientific content, 34 with continuity confirmed by the authors).' })]),
      h('div', { class: 'ring' }, [h('div', { class: 'count', text: counts.primary + ' + 31' }), h('div', { class: 'what', text: 'Current benchmark inputs: ' + counts.primary + ' primary texts (at least ten nonblank lines, 92 problem clusters) and 31 supplementary shorter texts, ' + counts.scorable + ' scorable in all.' })])]));

    var q = document.getElementById('x-q'), pop = document.getElementById('x-pop'), grp = document.getElementById('x-group'), rev = document.getElementById('x-review'), list = document.getElementById('x-rows'), summary = document.getElementById('x-summary');
    var groups = []; rows.forEach(function (r) { if (groups.indexOf(r.group_name) < 0) groups.push(r.group_name); });
    groups.sort().forEach(function (g) { grp.appendChild(h('option', { value: g, text: g })); });
    var mech = document.getElementById('x-mech'), mechs = []; rows.forEach(function (r) { if (r.mechanism_name && mechs.indexOf(r.mechanism_name) < 0) mechs.push(r.mechanism_name); });
    mechs.sort().forEach(function (g) { mech.appendChild(h('option', { value: g, text: g })); });
    function matches(r) {
      var s = q.value.trim().toLowerCase();
      if (s && (r.id + ' ' + r.claim_quote + ' ' + r.flaw + ' ' + r.group_name).toLowerCase().indexOf(s) < 0) return false;
      var p = pop.value;
      if (p === 'core' && !r.core) return false; if (p === 'primary' && !r.primary) return false; if (p === 'scorable' && !r.scorable) return false; if (p === 'notcore' && r.core) return false; if (p === 'excluded' && !r.benchmark_excluded) return false;
      if (grp.value && r.group_name !== grp.value) return false;
      if (mech.value && r.mechanism_name !== mech.value) return false;
      var rv = rev.value;
      if (rv === 'allyes' && !r.any_all_yes) return false; if (rv === 'none' && r.review.length) return false; if (rv === 'noallyes' && (r.any_all_yes || !r.review.length)) return false; if (rv === 'adverse' && !r.any_adverse) return false;
      return true;
    }
    function render() {
      var sel = rows.filter(matches);
      if (pop.value === 'all') sel = sel.slice().sort(function (a, b) { return (b.primary - a.primary) || (b.core - a.core) || a.id.localeCompare(b.id); });
      list.innerHTML = '';
      sel.forEach(function (r) {
        var tr = h('tr', { 'data-id': r.id });
        tr.appendChild(h('td', {}, [h('a', { href: '#record=' + encodeURIComponent(r.id), onclick: function (e) { e.preventDefault(); open(r.id); } }, [h('code', { class: 'id', text: r.id })])]));
        tr.appendChild(h('td', { text: r.group_name }));
        tr.appendChild(h('td', {}, popBadges(r)));
        tr.appendChild(h('td', { class: 'num', text: r.current_gold ? ranges(r.current_gold) : '—' }));
        tr.appendChild(h('td', { class: 'text small', text: r.claim_quote.length > 140 ? r.claim_quote.slice(0, 140) + '…' : r.claim_quote }));
        tr.addEventListener('click', function (e) { if (e.target.tagName !== 'A') open(r.id); });
        list.appendChild(tr);
      });
      summary.textContent = sel.length + ' of ' + rows.length + ' released dossiers shown (' + sel.filter(function (r) { return r.core; }).length + ' in the core, ' + sel.filter(function (r) { return r.primary; }).length + ' primary inputs).';
    }
    [q, pop, grp, mech, rev].forEach(function (el) { el.addEventListener('input', render); el.addEventListener('change', render); });
    render();

    var detail = document.getElementById('x-detail'), wanted = null;
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    function open(id) {
      wanted = id;
      history.replaceState(null, '', '#record=' + encodeURIComponent(id));
      detail.innerHTML = ''; detail.appendChild(h('p', { class: 'small', text: 'Loading ' + id + '…' }));
      loadRecord(id).then(function (rec) { if (wanted !== id) return; detail.innerHTML = ''; var box = renderRecord(rec, views); detail.appendChild(box); C.renderMath(detail); detail.scrollIntoView({ block: 'start', behavior: reduce ? 'auto' : 'smooth' }); var hd = box.querySelector('h3'); if (hd) { hd.setAttribute('tabindex', '-1'); hd.focus({ preventScroll: true }); } }, function (err) { if (wanted !== id) return; detail.innerHTML = ''; detail.appendChild(h('p', { class: 'note fails', text: err.message })); });
    }
    var m = /record=([^&]+)/.exec(location.hash);
    if (m) open(decodeURIComponent(m[1]));
    else { wanted = 'reddit_learnmath_dm6itc'; loadRecord('reddit_learnmath_dm6itc').then(function (rec) { if (wanted !== 'reddit_learnmath_dm6itc') return; detail.innerHTML = ''; detail.appendChild(h('p', { class: 'small', text: 'Starter record (the front page\'s example); select any row above to replace it.' })); detail.appendChild(renderRecord(rec, views)); C.renderMath(detail); }); }
  }

  function linesList(rec, gold) {
    var ol = h('ol', { class: 'proof-lines' });
    rec.source_lines.forEach(function (l) {
      if (!l.text.trim()) return;
      var isGold = gold && gold.map(String).indexOf(String(l.label)) >= 0;
      var li = h('li', { class: isGold ? 'is-flagged' : '' }, [h('span', { class: 'n', text: /^\d+$/.test(l.label) ? '[' + l.label + ']' : l.label }), h('span', { text: l.text })]);
      if (isGold) li.appendChild(badge('reference line', 'crimson'));
      ol.appendChild(li);
    });
    return ol;
  }

  function renderRecord(rec, views) {
    var r = rec.index, m = rec.membership, box = h('div', { class: 'panel elevated' });
    box.appendChild(h('div', { class: 'panel-head' }, [h('h3', {}, [h('code', { text: rec.id })]), h('div', {}, popBadges(r))]));
    box.appendChild(h('p', { class: 'small' }, ['Source collection: ' + r.group_name + (r.mechanism_name ? '. Error mechanism (saved primary annotation): ' + r.mechanism_name + (r.mechanism_uncertain ? ' (annotation uncertainty flag)' : '') : '') + '. ', C.repoLink(rec.bindings ? rec.bindings.dossier : 'bugbank/dossiers/' + rec.id + '.json', 'dossier'), ' · ', C.repoLink(rec.bindings ? rec.bindings.source : 'bugbank/sources/' + rec.id + '.json', 'source'), ' · ', C.repoLink(rec.certificate.path, 'certificate'), ' (SHA-256 ' + rec.certificate.sha256.slice(0, 12) + '…)']));
    /* current review layer */
    var kv = h('dl', { class: 'kv' });
    kv.appendChild(h('dt', { text: 'Current review layer' }));
    kv.appendChild(h('dd', {}, m ? [m.eligible ? badge('eligible for the core', 'teal') : badge('not eligible', 'muted'), ' ' + (m.eligibility_reasons || []).join('; ').toLowerCase().replace(/_/g, ' ') + '. Continuity: ' + String(m.continuity).toLowerCase().replace(/_/g, ' ') + '.'] : ['no membership record']));
    kv.appendChild(h('dt', { text: 'Human reviews' })); kv.appendChild(h('dd', { text: reviewText(r) + (m && m.current_source_scope_flags && m.current_source_scope_flags.length ? '; source-scope flags: ' + m.current_source_scope_flags.join(', ') : '') }));
    kv.appendChild(h('dt', { text: 'Reference lines' })); kv.appendChild(h('dd', { text: r.current_gold ? 'current: ' + r.current_gold.join(', ') + (r.exact_gold ? ' (exact current human review of the line label)' : '') + (r.scorable ? '' : ' (preserved labels; this record is outside the current benchmark inputs)') : 'none in the current layer' + (rec.gold_source_file ? '; the release source file preserves ' + JSON.stringify(rec.gold_source_file) + ' (outside the current benchmark)' : '') }));
    kv.appendChild(h('dt', { text: 'Formal statement' })); kv.appendChild(h('dd', {}, rec.declarations && rec.declarations.length ? [h('code', { text: rec.declarations[0].name }), ' · axioms: ' + ((rec.declarations[0].axioms || []).join(', ') || 'none') + (rec.declarations[0].uses_native_reduction ? ' · uses native reduction' : '') + (rec.declarations[0].unsafe ? ' · unsafe' : '')] : ['—']));
    kv.appendChild(h('dt', { text: 'Recorded automated checks' })); kv.appendChild(h('dd', { class: 'small', text: 'evidence tier ' + rec.historical_export_fields.evidence_tier + '; human approval at export: ' + String(rec.historical_export_fields.human_approval_of_current_artifact).toLowerCase().replace(/_/g, ' ') + '. These fields were recorded when the dossier was exported, before the human reviews; the current verdict is the review entry above.' }));
    box.appendChild(kv);
    /* fields */
    var f = rec.fields || {};
    ['problem', 'claim_quote', 'flaw', 'witness', 'explanation'].forEach(function (k) { if (!f[k]) return; var d = h('details', { open: k === 'claim_quote' || k === 'witness' ? '' : null }, [h('summary', { text: { problem: 'Problem statement', claim_quote: 'Quoted challenged claim', flaw: 'Recorded flaw', witness: 'Counterexample (witness)', explanation: 'Explanation' }[k] }), h('pre', { class: 'wrap no-math', text: f[k] })]); box.appendChild(d); });
    box.appendChild(h('details', {}, [h('summary', { text: 'Numbered source text (' + rec.source_lines.filter(function (l) { return l.text.trim(); }).length + ' lines; reference lines highlighted)' }), linesList(rec, r.current_gold), h('p', { class: 'small', text: 'Line numbers are those the critics saw. Contact strings, if any, are omitted in this display only.' })]));
    if (rec.declarations && rec.declarations.length) box.appendChild(h('details', {}, [h('summary', { text: 'Selected Lean declaration' }), h('pre', { class: 'lean no-math', text: rec.declarations.map(function (d) { return d.kind + ' ' + d.name + ' :\n  ' + d.type; }).join('\n\n') })]));
    box.appendChild(h('details', {}, [h('summary', { text: 'Lean certificate file (' + rec.certificate.text.length + ' bytes)' }), h('pre', { class: 'lean no-math', text: rec.certificate.text.trim() })]));
    /* selections */
    if (r.scorable && views) {
      var t = h('table', { class: 'data' }, [h('thead', {}, [h('tr', {}, ['Configuration (reporting view)', 'Recorded candidates', 'Hit@1', 'Hit@3', 'Attempt class'].map(function (x, i) { return h('th', { class: i >= 2 && i < 4 ? 'num' : '', text: x }); }))]), h('tbody', {}, views.views.map(function (vw) {
        var sv = rec.selections[vw.view_id] || {}, o = sv.outcome || {};
        return h('tr', {}, [h('td', { text: vw.name }), h('td', { class: 'num', text: sv.candidates ? '[' + sv.candidates.join(', ') + ']' : '—' }), h('td', { class: 'num', text: o.hit1 === undefined || o.hit1 === null ? '—' : String(o.hit1) }), h('td', { class: 'num', text: o.hit3 === undefined || o.hit3 === null ? '—' : String(o.hit3) }), h('td', { class: 'small', text: (o.attempt_class || sv.attempt_class || '—') + (o.cause && o.cause !== 'None' ? ' (' + o.cause + ')' : '') })]);
      }))]);
      box.appendChild(h('details', {}, [h('summary', { text: 'Recorded critic selections on this input (' + (r.primary ? 'primary' : 'supplementary') + ' evaluation)' }), h('div', { class: 'table-wrap' }, [t]), h('p', { class: 'small', text: 'Candidates are the parsed ranked line numbers of the saved answer; Hit@1/Hit@3 are the derived outcomes against the current reference lines; responses that broke the rules count as misses. The two Haiku rows are reporting views of one configuration.' })]));
    }
    box.appendChild(h('p', { class: 'small' }, [h('a', { href: '#record=' + encodeURIComponent(rec.id), text: 'Link to this record' })].concat(r.scorable ? [' · ', h('a', { href: 'benchmark.html#input=' + encodeURIComponent(rec.id), text: 'Try the localization exercise on this input' })] : [])));
    return box;
  }

  document.addEventListener('copeer:ready', build);
})();
