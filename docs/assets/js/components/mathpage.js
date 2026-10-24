/* Mathematics page extras: the statements, the rook-board viewer, the thirteen explanation packages. */
(function () {
  'use strict';
  var C = window.COPEER, D = window.COPEER_DATA || {}, h = C.h;

  function rookBoard() {
    var R = D.rook_board, root = document.getElementById('rook'); if (!R || !root) return;
    var n = R.board_size, black = {}; R.black_cells.forEach(function (c) { black[c] = true; });
    var sel = h('select', { 'aria-label': 'placement number' }); for (var i = 0; i < R.placements.length; i++) sel.appendChild(h('option', { value: String(i), text: 'placement ' + (i + 1) + ' of ' + R.placements.length }));
    var rnd = h('button', { class: 'btn btn-small', type: 'button', text: 'Random placement' });
    var fig = h('div', { class: 'diagram-wrap' }), readout = h('div', { class: 'readout', 'aria-live': 'polite' }), caveat = h('p', { class: 'small' });
    root.appendChild(h('div', { class: 'controls' }, [h('label', {}, ['Show ', sel]), rnd, h('span', { class: 'small', text: 'Click a white cell to see the two words (segments) through it.' })]));
    root.appendChild(h('div', { class: 'grid-2 split-5-7' }, [fig, h('div', {}, [readout, caveat])]));
    var always = {}; R.cells_occupied_in_every_placement.forEach(function (c) { always[c] = true; });
    function wordsThrough(cell) { return R.words.filter(function (w) { return w.cells.indexOf(cell) >= 0; }); }
    function draw() {
      var k = parseInt(sel.value, 10), pl = R.placements[k], rooks = {}; pl.forEach(function (c) { rooks[c] = true; });
      var S = 40, W = n * S + 2, svg = C.svg('svg', { class: 'chart diagram', viewBox: '0 0 ' + W + ' ' + W, role: 'group', 'aria-label': 'Permutation crossword grid with rook placement ' + (k + 1) });
      for (var r = 0; r < n; r++) for (var c = 0; c < n; c++) (function (r, c) {
        var id = r * n + c, rect = C.svg('rect', { x: 1 + c * S, y: 1 + r * S, width: S, height: S, 'data-cell': String(id), class: 'hot' });
        rect.style.fill = black[id] ? 'var(--ink)' : (always[id] ? 'var(--amber-soft)' : 'var(--elevated)'); rect.style.stroke = 'var(--line-strong)';
        if (!black[id]) { rect.setAttribute('tabindex', '0'); rect.setAttribute('role', 'button'); rect.setAttribute('aria-label', 'row ' + (r + 1) + ' column ' + (c + 1) + (rooks[id] ? ', rook' : '')); var show = function () { svg.querySelectorAll('rect[data-cell]').forEach(function (x) { x.style.strokeWidth = '1'; x.style.stroke = 'var(--line-strong)'; }); var ws = wordsThrough(id); ws.forEach(function (w) { w.cells.forEach(function (cc) { var el = svg.querySelector('rect[data-cell="' + cc + '"]'); if (el) { el.style.stroke = 'var(--crimson)'; el.style.strokeWidth = '3'; } }); }); readout.innerHTML = ''; readout.appendChild(h('p', {}, ['Cell (row ' + (r + 1) + ', column ' + (c + 1) + ')' + (rooks[id] ? ' holds a rook in this placement. ' : ' is empty in this placement. ') + 'It lies on ' + ws.length + ' word' + (ws.length === 1 ? '' : 's') + ': ' + ws.map(function (w) { return (w.down ? 'down' : 'across') + ' word of length ' + w.cells.length + ' on ' + (w.down ? 'column ' : 'row ') + w.line + ' (' + w.start + '–' + w.end + ')'; }).join('; ') + '. Each word holds exactly one rook; the rook' + (ws.length === 1 ? '' : 's') + ' on ' + (ws.length === 1 ? 'this word is' : 'these words are') + ' at ' + ws.map(function (w) { var rk = w.cells.filter(function (cc) { return rooks[cc]; })[0]; return '(row ' + (Math.floor(rk / n) + 1) + ', column ' + (rk % n + 1) + ')'; }).join(' and ') + '.'])); }; rect.addEventListener('click', show); rect.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); show(); } }); }
        svg.appendChild(rect);
        if (rooks[id]) { var t = C.svg('text', { x: 1 + c * S + S / 2, y: 1 + r * S + S / 2 + 1, 'text-anchor': 'middle', 'dominant-baseline': 'central', 'pointer-events': 'none', 'aria-hidden': 'true', text: '♜' }); t.style.fontSize = '24px'; t.style.fill = 'var(--indigo)'; svg.appendChild(t); }
      })(r, c);
      fig.innerHTML = ''; fig.appendChild(svg);
      readout.innerHTML = '';
      readout.appendChild(h('p', {}, ['Placement ' + (k + 1) + ' of ' + R.placement_count + ': ' + pl.length + ' rooks, one in each of the ' + R.words.length + ' maximal white segments (words), so no two rooks attack each other through white cells; black cells block attacks. ' + R.cells_occupied_in_every_placement.length + ' cells (shaded) hold a rook in every placement.']));
      caveat.textContent = 'The grid is the permutation crossword grid of w = (' + R.permutation.join(', ') + '): black cells at (row i, column w(i)). The Lean kernel counts ' + R.placement_count + ' complete placements, and ' + R.placement_count + ' ≡ ' + R.count_mod_4 + ' (mod 4), which refutes the necessity direction of the source\'s Conjecture 3.10. The placements shown were enumerated independently by a reviewer from the certificate\'s word list and are an illustration; the count lies beyond the source\'s summarised range r ≤ 108, as the paper notes, and no minimality or complete spectrum is claimed.';
    }
    sel.addEventListener('change', draw); rnd.addEventListener('click', function () { sel.value = String(Math.floor(Math.random() * R.placements.length)); draw(); });
    draw();
  }

  function packages() {
    var ep = D.explanation_packages, root = document.getElementById('packages'); if (!ep || !root) return;
    var grid = h('div', { class: 'grid-3' });
    ep.rows.forEach(function (r) {
      var parts = r.record_topic.split(' / ');
      var card = h('div', { class: 'card' });
      card.appendChild(h('h3', { text: parts[1] || parts[0] }));
      card.appendChild(h('p', { class: 'small' }, [h('code', { text: parts[0] })]));
      var p1 = h('p', { class: 'small' }); p1.innerHTML = '<strong>Formal result.</strong> ' + C.texToHtml(r.formal_result); card.appendChild(p1);
      var p2 = h('p', { class: 'small' }); p2.innerHTML = '<strong>Assumptions and scope.</strong> ' + C.texToHtml(r.assumptions_scope); card.appendChild(p2);
      grid.appendChild(card);
    });
    root.appendChild(grid);
    root.appendChild(h('p', { class: 'small', text: 'All thirteen mathematical follow-ups in the selected explanation study (Table 21 of the paper), each stating the formal result and the assumptions needed to apply it. The Lean sources are under mathematics/explanations/ for the twelve later packages and mathematics/extensions/sqrt_boundary/ and sqrt_repair/ for the square root; the artifact index maps each abbreviated source identifier to its full record id and selected declarations.' }));
  }

  document.addEventListener('copeer:ready', function () { rookBoard(); packages(); C.renderMath(document.body); });
})();
