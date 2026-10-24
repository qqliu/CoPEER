/* Mathematics section: live laboratories for doubled odd cycles, rainbow Schur triples and projective cubes,
   plus the further certified families. All computations come from assets/js/math/labs.js. */
(function () {
  'use strict';
  var C = window.COPEER, M = window.COPEER_MATH, D = window.COPEER_DATA || {}, h = C.h, Q = M.Q;
  var palette = ['var(--c1)', 'var(--c2)', 'var(--c3)', 'var(--c4)', 'var(--c5)', 'var(--c6)'];
  var paletteInk = ['var(--c1-ink)', 'var(--c2-ink)', 'var(--c3-ink)', 'var(--c4-ink)', 'var(--c5-ink)', 'var(--c6-ink)'];
  function tex(s) { var sp = h('span'); sp.innerHTML = C.texToHtml(s); return sp; }
  function bigFmt(b) { return b.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ','); }

  /* ---------- Lab A: doubled odd cycles ---------- */
  function cycles(root) {
    var nSel = h('select', {}, [5, 7, 9, 11, 13, 15, 21].map(function (n) { return h('option', { value: String(n), text: 'n = ' + n + (n % 3 === 0 ? ' (3 divides n)' : ''), selected: n === 9 ? 'selected' : null }); }));
    var fig = h('div', { class: 'diagram-wrap' }), readout = h('div', { class: 'readout', 'aria-live': 'polite' }), vertexOut = h('div', { class: 'readout', 'aria-live': 'polite' });
    var vSel = h('select', { id: 'cycle-vertex', 'aria-label': 'Vertex to inspect' }); var pickers = {};
    root.appendChild(h('div', { class: 'controls' }, [h('label', {}, ['Cycle length ', nSel]), h('label', {}, ['Inspect vertex ', vSel]), h('span', { class: 'small', text: 'or click a vertex in the drawing.' })]));
    vSel.addEventListener('change', function () { if (pickers[vSel.value]) pickers[vSel.value](); });
    root.appendChild(h('div', { class: 'grid-2 split-7-5' }, [h('div', {}, [fig]), h('div', {}, [readout, h('div', { style: 'height:.75rem' }), vertexOut])]));
    function draw() {
      var n = parseInt(nSel.value, 10), col = M.cycles.periodThree(n), W = 560, cx = W / 2, cy = 250, R = 165, dr = 22;
      var svg = C.svg('svg', { class: 'chart diagram', viewBox: '0 0 ' + W + ' 500', role: 'group', 'aria-label': 'Doubled ' + n + '-cycle with a six-colouring; each vertex is a button' });
      function pos(v) { var i = Math.floor(v / 2), ang = -Math.PI / 2 + 2 * Math.PI * i / n, r = R + (v % 2 ? dr : -dr); return [cx + r * Math.cos(ang), cy + r * Math.sin(ang)]; }
      /* window arcs when 3 | n */
      if (n % 3 === 0) for (var w = 0; w < n; w += 3) { var a0 = -Math.PI / 2 + 2 * Math.PI * (w - 0.35) / n, a1 = -Math.PI / 2 + 2 * Math.PI * (w + 2.35) / n, rr = R + dr + 24; svg.appendChild(C.svg('path', { d: 'M ' + (cx + rr * Math.cos(a0)) + ' ' + (cy + rr * Math.sin(a0)) + ' A ' + rr + ' ' + rr + ' 0 0 1 ' + (cx + rr * Math.cos(a1)) + ' ' + (cy + rr * Math.sin(a1)), fill: 'none', stroke: 'var(--line-strong)', 'stroke-width': 6, 'stroke-linecap': 'round', opacity: 0.6 })); }
      var seam = M.cycles.seam(n);
      /* edges */
      var edges = C.svg('g', { stroke: 'var(--line-strong)', 'stroke-width': 1 });
      for (var v = 0; v < 2 * n; v++) M.cycles.neighbours(n, v).forEach(function (u) { if (u > v) { var p = pos(v), q = pos(u); edges.appendChild(C.svg('line', { x1: p[0], y1: p[1], x2: q[0], y2: q[1] })); } });
      svg.appendChild(edges);
      /* seam highlight */
      if (seam) seam.bags.forEach(function (b) { var ang = -Math.PI / 2 + 2 * Math.PI * b / n; svg.appendChild(C.svg('circle', { cx: cx + R * Math.cos(ang), cy: cy + R * Math.sin(ang), r: dr + 16, fill: 'none', stroke: 'var(--crimson)', 'stroke-dasharray': '4 3', 'stroke-width': 1.5 })); });
      /* vertices */
      for (var v2 = 0; v2 < 2 * n; v2++) (function (v) {
        var p = pos(v), c = col[v];
        var g = C.svg('g', { class: 'hot', tabindex: '0', role: 'button', 'aria-label': 'vertex ' + v + ' in bag ' + Math.floor(v / 2) + ', colour ' + c });
        var circ = C.svg('circle', { class: 'vertex', 'data-v': String(v), cx: p[0], cy: p[1], r: 12 }); circ.style.fill = palette[c - 1]; g.appendChild(circ);
        var t = C.svg('text', { class: 'vertex-label', x: p[0], y: p[1], text: String(c) }); t.style.fill = paletteInk[c - 1]; g.appendChild(t);
        function pick() { svg.querySelectorAll('.vertex').forEach(function (c) { c.classList.remove('is-picked', 'is-nb'); }); circ.classList.add('is-picked'); M.cycles.neighbours(n, v).forEach(function (u) { var el = svg.querySelector('[data-v="' + u + '"]'); if (el) el.classList.add('is-nb'); }); var seen = M.cycles.neighbours(n, v).map(function (u) { return col[u]; }).sort(); var free = M.cycles.freeColours(n, col, v, 6); vertexOut.className = 'readout ' + (free.length ? 'ok' : 'fail'); vertexOut.innerHTML = ''; vertexOut.appendChild(h('p', {}, ['Vertex ' + v + ' (bag ' + Math.floor(v / 2) + ') has colour ' + c + '. Its five neighbours carry colours ' + seen.join(', ') + '. ', free.length ? h('strong', { class: 'ok', text: 'It could change to colour ' + free.join(' or ') + ': not frozen here.' }) : h('strong', { class: 'fail', text: 'Every other colour is taken: this vertex cannot change colour.' })])); }
        g.addEventListener('click', pick); g.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pick(); } });
        pickers[String(v)] = pick;
        svg.appendChild(g);
      })(v2);
      /* bag labels */
      for (var i = 0; i < n; i++) { var ang = -Math.PI / 2 + 2 * Math.PI * i / n; svg.appendChild(C.svg('text', { x: cx + (R - dr - 26) * Math.cos(ang), y: cy + (R - dr - 26) * Math.sin(ang), 'text-anchor': 'middle', 'dominant-baseline': 'central', text: String(i) })); }
      fig.innerHTML = ''; fig.appendChild(svg);
      vSel.innerHTML = ''; vSel.appendChild(h('option', { value: '', text: '—' })); for (var vv = 0; vv < 2 * n; vv++) vSel.appendChild(h('option', { value: String(vv), text: 'vertex ' + vv + ' (bag ' + Math.floor(vv / 2) + ', colour ' + col[vv] + ')' }));
      var frozen = M.cycles.isFrozen(n, col, 6), exact = M.cycles.countFrozenExact(n), formula = M.cycles.labelledCount(n);
      readout.className = 'readout ' + (frozen ? 'fail' : 'ok'); readout.innerHTML = '';
      readout.appendChild(h('p', {}, [tex('$C_{' + n + '}[K_2]$'), ' has ' + (2 * n) + ' vertices; each bag is a pair of adjacent vertices joined to both vertices of the neighbouring bags, so every vertex has five neighbours. Shown: the period-three colouring, pairs {1,2}, {3,4}, {5,6} repeating around the cycle' + (n % 3 === 0 ? '.' : ', with the last bag given the pair disjoint from both of its neighbours.')]));
      readout.appendChild(h('p', {}, [frozen ? h('strong', { class: 'fail', text: 'Frozen: every vertex already sees all five other colours, so no single vertex can change colour.' }) : h('strong', { class: 'ok', text: 'Not frozen: ' + (seam ? 'the pattern cannot close around the cycle (dashed bags), and vertices there can change colour.' : '') })]));
      readout.appendChild(h('p', { class: 'small' }, ['Labelled frozen six-colourings for n = ' + n + ': ', formula ? tex('$90\\cdot 2^{' + n + '} = ' + bigFmt(formula).replace(/,/g, '{,}') + '$') : '0', ' by the proposition (frozen six-colourings exist exactly when 3 divides n); exact enumeration over bag colourings in the page: ' + bigFmt(exact) + '.']));
      vertexOut.className = 'readout'; vertexOut.textContent = 'Select a vertex.';
    }
    nSel.addEventListener('change', draw); draw();
    root.appendChild(h('div', { class: 'note scope' }, [h('p', { text: 'Let n ≥ 5 be odd. The doubled n-cycle has a frozen six-colouring exactly when n is a multiple of three; for each such n there are exactly 90·2ⁿ such colourings with labelled vertices and colours (90 ways to assign disjoint colour pairs to the first three bags, two orders inside each of the n bags). The existence construction was known (Shaebani, 2009); the necessity and the count are the paper\'s contribution. The picture illustrates the theorem; the proof is in the appendix. The initial frozen colouring of the 18-vertex doubled 9-cycle, refuting a conjecture on recolourability of clique blowups, came from a model run without access to BugBank.' })]));
  }

  /* ---------- Lab B: rainbow Schur triples ---------- */
  function schur(root) {
    var DEN = 220, aIn = h('input', { type: 'range', id: 'schur-a', min: '0', max: String(DEN), step: '1', value: '80', 'aria-valuetext': '4/11' }), bIn = h('input', { type: 'range', id: 'schur-b', min: '0', max: String(DEN), step: '1', value: '200', 'aria-valuetext': '10/11' });
    var aOut = h('span', { class: 'mono', text: '4/11' }), bOut = h('span', { class: 'mono', text: '10/11' });
    var mSel = h('select', {}, [1, 2, 3, 5].map(function (m) { return h('option', { value: String(m), text: 'n = ' + (22 * m) + ' (m = ' + m + ')' }); }));
    var presets = h('div', { class: 'controls' }, [
      h('span', { class: 'small', text: 'Presets:' }),
      h('button', { class: 'btn btn-small', type: 'button', text: 'optimum (4/11, 10/11)', onclick: function () { set(80, 200); } }),
      h('button', { class: 'btn btn-small', type: 'button', text: 'a = 0, b = 2/5', onclick: function () { set(0, 88); } }),
      h('button', { class: 'btn btn-small', type: 'button', text: 'a = 3/5, b = 1', onclick: function () { set(132, 220); } }),
      h('button', { class: 'btn btn-small', type: 'button', text: 'a = b = 1/2 (no green)', onclick: function () { set(110, 110); } })]);
    var strip = h('div', { class: 'strip', 'aria-label': 'colouring of 1..n' }), readout = h('div', { class: 'readout', 'aria-live': 'polite' }), heat = h('div', { class: 'diagram-wrap' }), samples = h('p', { class: 'small' });
    root.appendChild(h('div', { class: 'controls' }, [h('label', { for: 'schur-a' }, ['a = ', aOut]), aIn, h('label', { for: 'schur-b' }, ['b = ', bOut]), bIn, h('label', {}, ['Finite check at ', mSel])]));
    root.appendChild(presets);
    root.appendChild(h('div', { class: 'grid-2 split-7-5' }, [h('div', {}, [heat]), h('div', {}, [readout, h('div', { style: 'height:.75rem' }), h('p', { class: 'small', text: 'Colouring of 1..n: even numbers red; odd numbers blue when k/n ≤ a or k/n > b, green otherwise.' }), strip, samples])]));
    function frac(i) { return Q(i, DEN); }
    function set(i, j) { aIn.value = String(i); bIn.value = String(j); update(); }
    var cell = {};
    function drawHeat() {
      var N = 44, W = 560, pad = 36, size = (W - 2 * pad) / N, Hh = pad * 2 + N * size;
      var svg = C.svg('svg', { class: 'chart diagram', viewBox: '0 0 ' + W + ' ' + Hh, role: 'img', 'aria-label': 'Limiting rainbow density over the thresholds a and b' });
      var maxD = 9 / 22;
      for (var i = 0; i <= N; i++) for (var j = i; j <= N; j++) (function (i, j) {
        var d = Q.num(M.schur.density(Q(i, N), Q(j, N)));
        var t = d / maxD, r = C.svg('rect', { x: pad + i * size, y: pad + (N - j) * size, width: size + 0.4, height: size + 0.4, class: 'hot' });
        r.style.fill = 'color-mix(in srgb, var(--indigo) ' + Math.round(8 + 92 * t) + '%, var(--paper))';
        r.appendChild(C.svg('title', { text: 'a = ' + i + '/' + N + ', b = ' + j + '/' + N + ': D = ' + Q.str(M.schur.density(Q(i, N), Q(j, N))) + ' ≈ ' + (100 * d).toFixed(2) + '%' }));
        r.addEventListener('click', function () { set(i * 5, j * 5); });
        svg.appendChild(r); cell[i + ',' + j] = r;
      })(i, j);
      svg.appendChild(C.svg('text', { x: pad + N * size / 2, y: Hh - 8, 'text-anchor': 'middle', text: 'a (first threshold)' }));
      svg.appendChild(C.svg('text', { x: 12, y: pad + N * size / 2, 'text-anchor': 'middle', transform: 'rotate(-90 12 ' + (pad + N * size / 2) + ')', text: 'b (second threshold)' }));
      var oi = 16, oj = 40; svg.appendChild(C.svg('circle', { cx: pad + (oi + 0.5) * size, cy: pad + (N - oj + 0.5) * size, r: size * 0.9, fill: 'none', stroke: 'var(--crimson)', 'stroke-width': 2 }));
      var lx = pad + 24 * size, ly = pad + 30 * size; svg.appendChild(C.svg('line', { x1: pad + (oi + 0.5) * size + size * 0.9, y1: pad + (N - oj + 0.5) * size + size * 0.9, x2: lx - 4, y2: ly - 14, stroke: 'var(--crimson)', 'stroke-dasharray': '3 3', 'stroke-width': 1.5 })); var lab = C.svg('text', { x: lx, y: ly, text: '9/22 at (4/11, 10/11)' }); lab.style.fill = 'var(--crimson)'; lab.style.fontWeight = '700'; svg.appendChild(lab);
      var marker = C.svg('rect', { id: 'schur-marker', width: size + 0.4, height: size + 0.4, fill: 'none', stroke: 'var(--teal)', 'stroke-width': 2.5 });
      svg.appendChild(marker);
      heat.innerHTML = ''; heat.appendChild(svg);
      heat.appendChild(h('p', { class: 'caption', text: 'Limiting fraction D(a, b) of rainbow ordered Schur triples under the two-threshold rule, on a 1/44 grid of the triangle 0 ≤ a ≤ b ≤ 1 (darker is larger; click a cell to select it). The ring marks the unique maximum 9/22 at (4/11, 10/11); the square marks the current thresholds.' }));
      return { pad: pad, size: size, N: N, marker: marker };
    }
    var geo = drawHeat();
    function update() {
      var i = parseInt(aIn.value, 10), j = parseInt(bIn.value, 10); if (i > j) { if (document.activeElement === aIn) { j = i; bIn.value = String(j); } else { i = j; aIn.value = String(i); } }
      var a = frac(i), b = frac(j), m = parseInt(mSel.value, 10), n = 22 * m;
      aOut.textContent = Q.str(a); bOut.textContent = Q.str(b); aIn.setAttribute('aria-valuetext', Q.str(a)); bIn.setAttribute('aria-valuetext', Q.str(b));
      var d = M.schur.density(a, b), c = M.schur.count(n, a, b);
      readout.className = 'readout'; readout.innerHTML = '';
      readout.appendChild(h('p', {}, ['Limiting density ', h('strong', { text: 'D(' + Q.str(a) + ', ' + Q.str(b) + ') = ' + Q.str(d) + ' ≈ ' + (100 * Q.num(d)).toFixed(2) + '%' }), Q.str(d) === '9/22' ? h('span', { class: 'badge badge-crimson', text: ' unique maximum of the family' }) : (Q.num(d) > 0.4 ? h('span', { class: 'badge badge-teal', text: ' above 2/5' }) : null)]));
      readout.appendChild(h('p', {}, ['At n = ' + n + ': ' + bigFmt(BigInt(c.rainbow)) + ' rainbow ordered Schur triples (x, y, x + y) out of n(n − 1)/2 = ' + bigFmt(BigInt(c.denominator)) + ', a fraction of ' + (100 * c.rainbow / c.denominator).toFixed(2) + '%' + (Q.str(a) === '4/11' && Q.str(b) === '10/11' ? ' (99m² + 3m = ' + M.schur.paperCount(m) + ' as the paper states)' : '') + '.']));
      strip.innerHTML = ''; c.colouring.forEach(function (col, k) { strip.appendChild(h('span', { class: ['red', 'blue', 'green'][col], text: String(k + 1), title: (k + 1) + ': ' + ['red', 'blue', 'green'][col] })); });
      samples.textContent = c.samples.length ? 'First rainbow triples: ' + c.samples.map(function (t) { return '(' + t.join(', ') + ')'; }).join(' ') + (c.rainbow > 24 ? ' …' : '') : 'No rainbow triple at this n.';
      var ga = i / 220 * geo.N, gb = j / 220 * geo.N;
      geo.marker.setAttribute('x', geo.pad + ga * geo.size); geo.marker.setAttribute('y', geo.pad + (geo.N - gb) * geo.size);
    }
    aIn.addEventListener('input', update); bIn.addEventListener('input', update); mSel.addEventListener('change', update); update();
    root.appendChild(h('div', { class: 'note scope' }, [h('p', { text: 'Consider the two-threshold rule that colours every even integer red and colours an odd integer k blue if k/n ≤ a or k/n > b, and green if a < k/n ≤ b. With a = 4/11 and b = 10/11 the colouring at n = 22m has 99m² + 3m rainbow ordered Schur triples out of n(n − 1)/2, a fraction converging to 9/22 ≈ 40.9% > 2/5. Over the whole family the limiting fraction D(a, b) has its unique maximum 9/22 at (4/11, 10/11); on the region a ≤ 1/2 ≤ b, a + b ≥ 1 the loss 9/22 − D(a, b) is the quadratic (5/2)u² − 2uv + (3/2)v² in the displacements u = a − 4/11, v = b − 10/11, at least ((4 − √5)/2)(u² + v²); the simpler rules with a = 0 or b = 1 reach at most 2/5. This optimum applies to the two-threshold family; a higher limiting fraction requires a rule outside it. Independent work by Hegde, Kumar and Pratibha (arXiv:2609.18474, submitted 16 September 2026) obtained the same construction and 9/22 lower bound together with a global upper bound of 8/15; the saved model run is dated 4 September 2026, and the paper leaves mathematical priority unassigned.' }), h('p', { class: 'small' }, [h('a', { href: 'https://arxiv.org/abs/2609.18474', rel: 'noopener', text: 'Hegde, Kumar and Pratibha (2026), A somewhat sure note on an un-Schur problem' })])]));
  }

  /* ---------- Lab C: projective cubes ---------- */
  function cubes(root) {
    root.appendChild(h('p', {}, ['In the cyclic group ', tex('$\\mathbb{Z}_N$'), ', the nonempty subset sums of ', tex('$d$'), ' generators form a projective ', tex('$d$'), '-cube; repeated and zero generators are allowed. A cube-free set contains no such cube. The source conjectures that when ', tex('$d$'), ' divides ', tex('$N$'), ', the density of a cube-free set is at most ', tex('$(d-1)/d$'), '. Three Lean-verified families beat that bound; the curve below shows exactly when one particular construction, the layered one, exceeds it.']));
    var rows = M.cubes.table(32), W = 560, Hh = 310, left = 44, right = 16, top = 16, bottom = 46;
    var svg = C.svg('svg', { class: 'chart diagram', viewBox: '0 0 ' + W + ' ' + Hh, role: 'img', 'aria-label': 'Density of the layered construction against the conjectured bound' });
    var x = function (d) { return left + (d - 2) / 30 * (W - left - right); }, y = function (v) { return top + (1 - (v - 0.45) / 0.55) * (Hh - top - bottom); };
    [0.5, 0.6, 0.7, 0.8, 0.9, 1.0].forEach(function (t) { svg.appendChild(C.svg('line', { class: 'grid', x1: left, x2: W - right, y1: y(t), y2: y(t), stroke: 'var(--line)' })); svg.appendChild(C.svg('text', { x: left - 6, y: y(t), 'text-anchor': 'end', 'dominant-baseline': 'central', text: t.toFixed(1) })); });
    var pathB = 'M' + rows.map(function (r) { return x(r.d) + ' ' + y(r.boundNum); }).join(' L');
    var pathD = 'M' + rows.map(function (r) { return x(r.d) + ' ' + y(r.densityNum); }).join(' L');
    svg.appendChild(C.svg('path', { d: pathB, fill: 'none', stroke: 'var(--crimson)', 'stroke-width': 1.5, 'stroke-dasharray': '4 3' }));
    svg.appendChild(C.svg('path', { d: pathD, fill: 'none', stroke: 'var(--indigo)', 'stroke-width': 1.5 }));
    rows.forEach(function (r) { var c = C.svg('circle', { cx: x(r.d), cy: y(r.densityNum), r: r.exceptional ? 5 : 3.5, class: 'hot' }); c.style.fill = r.exceptional ? 'var(--c4)' : 'var(--indigo)'; c.appendChild(C.svg('title', { text: 'd = ' + r.d + ': density ' + r.density + ' ' + (r.comparison === 'exceeds' ? '>' : r.comparison === 'equals' ? '=' : '<') + ' bound ' + r.bound })); svg.appendChild(c); if (r.d % 4 === 0 || r.d === 2) svg.appendChild(C.svg('text', { x: x(r.d), y: Hh - 24, 'text-anchor': 'middle', text: String(r.d) })); });
    svg.appendChild(C.svg('text', { x: W / 2, y: Hh - 4, 'text-anchor': 'middle', text: 'dimension d' }));
    var wrap = h('div', { class: 'diagram-wrap' }, [svg]);
    root.appendChild(h('div', { class: 'grid-2 split-7-5' }, [h('div', {}, [wrap, h('div', { class: 'legend' }, [h('span', {}, [(function () { var s = h('span', { class: 'sw' }); s.style.background = 'var(--indigo)'; return s; })(), 'layered construction density ', tex('$1-g(d)$')]), h('span', {}, [(function () { var s = h('span', { class: 'sw' }); s.style.background = 'var(--crimson)'; return s; })(), 'conjectured bound (d − 1)/d']), h('span', {}, [(function () { var s = h('span', { class: 'sw' }); s.style.background = 'var(--c4)'; return s; })(), 'exceptional dimensions ', tex('$2^{\\ell}-2,\\ 2^{\\ell}-1,\\ 2^{\\ell}$')])])]),
      h('div', {}, [h('div', { class: 'table-wrap', style: 'max-height:20rem;overflow:auto' }, [h('table', { class: 'data' }, [h('thead', {}, [h('tr', {}, ['d', 'density', 'bound', 'comparison'].map(function (t, i) { return h('th', { class: i && i < 3 ? 'num' : '', text: t }); }))]), h('tbody', {}, rows.map(function (r) { return h('tr', { class: r.exceptional ? 'is-highlight' : '' }, [h('td', { text: String(r.d) }), h('td', { class: 'num', text: r.density }), h('td', { class: 'num', text: r.bound }), h('td', {}, [h('span', { class: 'badge ' + (r.comparison === 'exceeds' ? 'badge-teal' : r.comparison === 'equals' ? 'badge-amber' : 'badge-crimson'), text: r.comparison })])]); }))])])])]));
    var fam = D.projective_cube_families;
    if (fam) root.appendChild(h('div', { class: 'table-wrap' }, [h('table', { class: 'data' }, [h('thead', {}, [h('tr', {}, fam.header.map(function (t) { var th = h('th'); th.innerHTML = C.texToHtml(t === '|A_N|' ? '$|A_N|$' : t === 'M' ? '$M$' : t === 'N' ? '$N$' : t === 'd' ? '$d$' : t); return th; }))]), h('tbody', {}, fam.rows.map(function (r) { var tr = h('tr', {}); ['d', 'M', 'excluded_residues', 'N', 'size', 'density'].forEach(function (k) { var td = h('td', {}); td.innerHTML = C.texToHtml(String(r[k])); tr.appendChild(td); }); return tr; }))])]));
    root.appendChild(h('div', { class: 'note scope' }, [h('p', { text: 'Three families of cube-free sets in cyclic groups exceed the conjectured density (d − 1)/d for d = 5, 7, 8 and every integer k ≥ 1 (Lean-verified). The curve shows the recursively defined layered construction of Long and Wagner in the group of order 2ⁿ (it fits whenever d ≤ n), with g(1) = 1 and g(P + m − 1) = (1 + g(m))/(2P) for P a power of two and 1 ≤ m ≤ P: for every d ≥ 2 its density 1 − g(d) exceeds (d − 1)/d exactly when d is not of the form 2ˡ − 2, 2ˡ − 1 or 2ˡ; equality holds exactly at powers of two, and at the other exceptional dimensions the density is strictly below the bound. Cube-freeness of the general construction is a result of Long and Wagner and enters the conditional Lean theorems as an explicit premise; the three families are checked directly. The d = 5 set was found in the model runs of 10 September 2026, first with BugBank and then with plain prompting; it is the pullback of the published layered set, so the search rediscovered that construction. We found the d = 7 and d = 8 sets by computer search, with AI tools, on 19 September 2026, and then formalized them; their construction priority is not established.' })]));
  }

  /* ---------- Lab D: further certified families ---------- */
  function families(root) {
    var cf = D.certified_families; if (!cf) return;
    var grid = h('div', { class: 'grid-3' });
    cf.rows.forEach(function (r) {
      var card = h('div', { class: 'card' });
      card.appendChild(h('h3', { text: r.case }));
      var p1 = h('p', { class: 'small' }); p1.innerHTML = '<strong>Refuted statement.</strong> ' + C.texToHtml(r.refuted_statement); card.appendChild(p1);
      var p2 = h('p', { class: 'small' }); p2.innerHTML = '<strong>Lean establishes.</strong> ' + C.texToHtml(r.lean_establishes); card.appendChild(p2);
      card.appendChild(h('p', { class: 'small', text: 'Toolchain: ' + r.toolchain + '.' }));
      grid.appendChild(card);
    });
    root.appendChild(grid);
    root.appendChild(h('p', { class: 'small', text: 'Citations in the refuted statements refer to the sources listed in the paper\'s bibliography; each row\'s scope, certificate file, provenance and the human judgments on its dossier are given in the paper. The permutation-grid count (155 placements for w = (2, 7, 4, 8, 1, 6, 3, 5), 155 ≡ 3 mod 4) and the other finite objects are shown on the mathematics page.' }));
  }

  document.addEventListener('copeer:ready', function () {
    var root = document.getElementById('math-labs'); if (!root) return;
    root.innerHTML = '';
    var tabs = h('div', { class: 'tabs', role: 'tablist', 'aria-label': 'Laboratories', 'data-tabs': '' }, [
      h('button', { role: 'tab', id: 'tab-cycles', 'aria-controls': 'panel-cycles', 'aria-selected': 'true', type: 'button', text: 'Doubled odd cycles' }),
      h('button', { role: 'tab', id: 'tab-schur', 'aria-controls': 'panel-schur', 'aria-selected': 'false', type: 'button', text: 'Rainbow Schur triples' }),
      h('button', { role: 'tab', id: 'tab-cubes', 'aria-controls': 'panel-cubes', 'aria-selected': 'false', type: 'button', text: 'Projective cubes' }),
      h('button', { role: 'tab', id: 'tab-families', 'aria-controls': 'panel-families', 'aria-selected': 'false', type: 'button', text: 'Further certified families' })]);
    var p1 = h('div', { role: 'tabpanel', id: 'panel-cycles', 'aria-labelledby': 'tab-cycles' }), p2 = h('div', { role: 'tabpanel', id: 'panel-schur', 'aria-labelledby': 'tab-schur', hidden: '' }), p3 = h('div', { role: 'tabpanel', id: 'panel-cubes', 'aria-labelledby': 'tab-cubes', hidden: '' }), p4 = h('div', { role: 'tabpanel', id: 'panel-families', 'aria-labelledby': 'tab-families', hidden: '' });
    root.appendChild(tabs); [p1, p2, p3, p4].forEach(function (p) { root.appendChild(p); });
    cycles(p1); schur(p2); cubes(p3); families(p4);
    C.initTabs(root); C.renderMath(root);
  });
})();
