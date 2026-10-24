/* Shared behaviour for the Co-PEER site: theme, navigation, tabs, tables, KaTeX, copy buttons, charts.
   Classic script; exposes window.COPEER. Works from file:// and from a subpath. */
(function () {
  'use strict';
  var C = window.COPEER = window.COPEER || {};

  /* ---------- small helpers ---------- */
  C.h = function (tag, attrs, children) {
    var el = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      if (k === 'class') el.className = attrs[k];
      else if (k === 'text') el.textContent = attrs[k];
      else if (k === 'html') el.innerHTML = attrs[k];
      else if (k.slice(0, 2) === 'on') el.addEventListener(k.slice(2), attrs[k]);
      else if (attrs[k] !== null && attrs[k] !== undefined) el.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) { if (c === null || c === undefined) return; el.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); });
    return el;
  };
  C.svg = function (tag, attrs, children) {
    var el = document.createElementNS('http://www.w3.org/2000/svg', tag);
    if (attrs) Object.keys(attrs).forEach(function (k) { if (k === 'text') el.textContent = attrs[k]; else el.setAttribute(k, attrs[k]); });
    (children || []).forEach(function (c) { if (c) el.appendChild(c); });
    return el;
  };
  C.fmt = function (n, digits) { if (n === null || n === undefined) return '—'; if (typeof n === 'object') n = n.value; if (n === null || n === undefined) return '—'; return Number(n).toLocaleString('en-US', { minimumFractionDigits: digits || 0, maximumFractionDigits: digits === undefined ? 3 : digits }); };
  C.val = function (x) { return (x && typeof x === 'object' && 'value' in x) ? x.value : x; };
  C.ci = function (x) { return (x && typeof x === 'object' && x.ci95) ? x.ci95 : null; };
  C.maskEmails = function (text) { return String(text).replace(/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g, '[contact omitted in display]'); };
  C.escape = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };
  C.texToHtml = function (tex) {
    /* render $...$ fragments with KaTeX when available; otherwise leave the text */
    var parts = String(tex).split('$');
    return parts.map(function (p, i) {
      if (i % 2 === 1 && window.katex) { try { return window.katex.renderToString(p, { throwOnError: false }); } catch (e) { return C.escape(p); } }
      if (i % 2 === 1) return '<code>' + C.escape(p) + '</code>';
      return C.escape(p).replace(/(\b(?:of|by)\s+)?\[cite:([^\]]+)\]/g, function (m, lead, keys) { var labels = keys.split(',').map(function (k) { return C.citeLabel(k.trim(), !!lead); }).join('; '); return lead ? lead + labels : '(' + labels + ')'; }).replace(/\[ref:([^\]]+)\]/g, '');
    }).join('');
  };

  /* ---------- citations: author-year labels from the extracted bibliography ---------- */
  C.citeLabel = function (key, narrative) {
    var D = window.COPEER_DATA || {}, bib = (D.related_resources && D.related_resources.bibliography) || {};
    var e = bib[key];
    if (!e || !e.author) return '<cite class="cite" title="' + C.escape(key) + '">[' + C.escape(key) + ']</cite>';
    var authors = e.author.split(/\s+and\s+/).map(function (a) { a = a.trim(); return a.indexOf(',') >= 0 ? a.split(',')[0].trim() : a.split(' ').pop(); });
    var label = authors.length > 2 ? authors[0] + ' et al.' : authors.join(' and ');
    var title = (e.title || '') + (e.year ? ' (' + e.year + ')' : '');
    var inner = C.escape(narrative ? label + (e.year ? ' (' + e.year + ')' : '') : label + (e.year ? ', ' + e.year : ''));
    return e.url ? '<cite class="cite"><a href="' + C.escape(e.url) + '" title="' + C.escape(title) + '" rel="noopener">' + inner + '</a></cite>' : '<cite class="cite" title="' + C.escape(title) + '">' + inner + '</cite>';
  };

  /* ---------- links into the evidence release (known only after publication) ---------- */
  C.repoLink = function (path, label) {
    var cfg = window.COPEER_CONFIG || {};
    if (cfg.repoUrl) return C.h('a', { href: cfg.repoUrl.replace(/\/$/, '') + '/blob/' + (cfg.repoBranch || 'main') + '/' + path, rel: 'noopener' }, [label || path]);
    var el = C.h('code', { class: 'repo-path', title: 'Path inside the public repository; the link is added when the repository URL is published' }, [label || path]);
    return el;
  };

  /* ---------- theme ---------- */
  C.initTheme = function () {
    var root = document.documentElement, key = 'copeer-theme', stored = null;
    try { stored = localStorage.getItem(key); } catch (e) { }
    if (stored === 'dark' || stored === 'light') root.setAttribute('data-theme', stored);
    var qs = /[?&]theme=(dark|light)/.exec(location.search); if (qs) root.setAttribute('data-theme', qs[1]);
    document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
      function label() { var dark = root.getAttribute('data-theme') === 'dark' || (!root.getAttribute('data-theme') && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches); btn.textContent = dark ? 'Light theme' : 'Dark theme'; btn.setAttribute('aria-pressed', dark ? 'true' : 'false'); }
      label();
      btn.addEventListener('click', function () {
        var dark = root.getAttribute('data-theme') === 'dark' || (!root.getAttribute('data-theme') && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
        var next = dark ? 'light' : 'dark';
        root.setAttribute('data-theme', next);
        try { localStorage.setItem(key, next); } catch (e) { }
        label();
      });
    });
  };

  /* ---------- navigation: highlight the section in view ---------- */
  C.initNav = function () {
    var links = Array.prototype.slice.call(document.querySelectorAll('.navlinks a[href^="#"]'));
    if (!links.length || !('IntersectionObserver' in window)) return;
    var map = {};
    links.forEach(function (a) { var id = a.getAttribute('href').slice(1); var sec = document.getElementById(id); if (sec) map[id] = a; });
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { links.forEach(function (a) { a.classList.remove('is-active'); }); var a = map[e.target.id]; if (a) a.classList.add('is-active'); } });
    }, { rootMargin: '-40% 0px -55% 0px' });
    Object.keys(map).forEach(function (id) { obs.observe(document.getElementById(id)); });
  };

  /* ---------- tabs (WAI-ARIA tabs pattern) ---------- */
  C.initTabs = function (root) {
    (root || document).querySelectorAll('[data-tabs]').forEach(function (group) {
      var tabs = Array.prototype.slice.call(group.querySelectorAll('[role="tab"]'));
      var panels = tabs.map(function (t) { return document.getElementById(t.getAttribute('aria-controls')); });
      function select(i, focus) {
        tabs.forEach(function (t, j) { var on = i === j; t.setAttribute('aria-selected', on ? 'true' : 'false'); t.tabIndex = on ? 0 : -1; if (panels[j]) panels[j].hidden = !on; });
        if (focus) tabs[i].focus();
        group.dispatchEvent(new CustomEvent('tabchange', { detail: { index: i, id: tabs[i].id } }));
      }
      tabs.forEach(function (t, i) {
        t.addEventListener('click', function () { select(i, false); });
        t.addEventListener('keydown', function (ev) {
          var k = ev.key, n = tabs.length;
          if (k === 'ArrowRight') { ev.preventDefault(); select((i + 1) % n, true); }
          else if (k === 'ArrowLeft') { ev.preventDefault(); select((i - 1 + n) % n, true); }
          else if (k === 'Home') { ev.preventDefault(); select(0, true); }
          else if (k === 'End') { ev.preventDefault(); select(n - 1, true); }
        });
      });
      var initial = tabs.findIndex(function (t) { return t.getAttribute('aria-selected') === 'true'; });
      select(initial < 0 ? 0 : initial, false);
      if (location.hash) { var idx = tabs.findIndex(function (t) { return '#' + t.id === location.hash || '#' + t.getAttribute('aria-controls') === location.hash; }); if (idx >= 0) select(idx, false); }
    });
  };

  /* ---------- segmented controls ---------- */
  C.initSegmented = function (root) {
    (root || document).querySelectorAll('.segmented').forEach(function (seg) {
      var btns = Array.prototype.slice.call(seg.querySelectorAll('button'));
      btns.forEach(function (b) { b.addEventListener('click', function () { btns.forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); }); seg.dispatchEvent(new CustomEvent('change', { detail: { value: b.getAttribute('data-value') } })); }); });
    });
  };
  C.segValue = function (seg) { var b = seg.querySelector('button[aria-pressed="true"]'); return b ? b.getAttribute('data-value') : null; };

  /* ---------- sortable tables ---------- */
  C.makeSortable = function (table) {
    var ths = table.querySelectorAll('thead th[data-sort]');
    ths.forEach(function (th, idx) {
      var btn = C.h('button', { class: 'sort', type: 'button', html: th.innerHTML });
      th.innerHTML = ''; th.appendChild(btn);
      btn.addEventListener('click', function () {
        var kind = th.getAttribute('data-sort');
        var current = th.getAttribute('aria-sort');
        var dir = current === 'ascending' ? 'descending' : 'ascending';
        ths.forEach(function (x) { x.removeAttribute('aria-sort'); });
        th.setAttribute('aria-sort', dir);
        var tbody = table.tBodies[0];
        var rows = Array.prototype.slice.call(tbody.rows).filter(function (r) { return !r.classList.contains('no-sort'); });
        var col = Array.prototype.indexOf.call(th.parentNode.children, th);
        rows.sort(function (a, b) {
          var av = a.cells[col].getAttribute('data-value') || a.cells[col].textContent.trim();
          var bv = b.cells[col].getAttribute('data-value') || b.cells[col].textContent.trim();
          if (kind === 'num') { av = av === '—' || av === '' ? -Infinity : parseFloat(av.replace(/,/g, '')); bv = bv === '—' || bv === '' ? -Infinity : parseFloat(bv.replace(/,/g, '')); return av - bv; }
          return av.localeCompare(bv, undefined, { numeric: true, sensitivity: 'base' });
        });
        if (dir === 'descending') rows.reverse();
        rows.forEach(function (r) { tbody.appendChild(r); });
      });
    });
  };

  /* ---------- copy to clipboard with fallback ---------- */
  C.initCopy = function () {
    document.querySelectorAll('[data-copy-target]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var src = document.querySelector(btn.getAttribute('data-copy-target'));
        var text = src ? src.textContent : '';
        function done(ok) { var old = btn.textContent; btn.textContent = ok ? 'Copied' : 'Select the text and copy it'; setTimeout(function () { btn.textContent = old; }, 1800); }
        if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(text).then(function () { done(true); }, function () { done(false); });
        else { try { var r = document.createRange(); r.selectNodeContents(src); var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(r); done(document.execCommand('copy')); } catch (e) { done(false); } }
      });
    });
  };

  /* ---------- KaTeX ---------- */
  C.renderMath = function (root) {
    if (!window.renderMathInElement) return;
    try {
      window.renderMathInElement(root || document.body, {
        delimiters: [{ left: '$$', right: '$$', display: true }, { left: '\\[', right: '\\]', display: true }, { left: '\\(', right: '\\)', display: false }, { left: '$', right: '$', display: false }],
        ignoredTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code', 'option'],
        ignoredClasses: ['no-math', 'lean'],
        throwOnError: false
      });
    } catch (e) { }
  };

  /* ---------- charts (SVG, no dependencies) ---------- */
  /* dot plot with interval: rows [{label, value, lo, hi, cls}], range [0,100] */
  C._charts = [];
  C.chartWidth = function (container, opts) { var w = (container.clientWidth || container.parentNode && container.parentNode.clientWidth || 720); return Math.max(560, Math.min(opts && opts.maxWidth || 900, w)); };
  C.registerChart = function (container, redraw) { C._charts = C._charts.filter(function (c) { return c.container !== container; }); C._charts.push({ container: container, redraw: redraw }); };
  window.addEventListener('resize', (function () { var t; return function () { clearTimeout(t); t = setTimeout(function () { C._charts.forEach(function (c) { c.redraw(); }); }, 150); }; })());
  C.dotPlot = function (container, rows, opts) {
    opts = opts || {};
    C.registerChart(container, function () { C.dotPlot(container, rows, opts); });
    var width = opts.width || C.chartWidth(container, opts), rowH = opts.rowH || 26, left = opts.left || 190, right = 70, top = 28, bottom = 26;
    var height = top + rows.length * rowH + bottom;
    var min = opts.min !== undefined ? opts.min : 0, max = opts.max !== undefined ? opts.max : 100;
    var x = function (v) { return left + (v - min) / (max - min) * (width - left - right); };
    var svg = C.svg('svg', { class: 'chart', viewBox: '0 0 ' + width + ' ' + height, role: 'img', 'aria-label': opts.ariaLabel || 'Dot plot' });
    var grid = C.svg('g', { class: 'grid' });
    var ticks = opts.ticks || [0, 20, 40, 60, 80, 100];
    ticks.forEach(function (t) { grid.appendChild(C.svg('line', { x1: x(t), x2: x(t), y1: top - 8, y2: height - bottom + 4 })); svg.appendChild(C.svg('text', { x: x(t), y: height - 6, 'text-anchor': 'middle', text: String(t) + (opts.unit || '') })); });
    svg.appendChild(grid);
    if (opts.refLine !== undefined && opts.refLine !== null) { svg.appendChild(C.svg('line', { class: 'ref-line', x1: x(opts.refLine), x2: x(opts.refLine), y1: top - 8, y2: height - bottom + 4 })); svg.appendChild(C.svg('text', { x: x(opts.refLine) + 4, y: top - 12, text: opts.refLabel || '' })); }
    rows.forEach(function (r, i) {
      var cy = top + i * rowH + rowH / 2;
      var g = C.svg('g', { class: 'hot', tabindex: '0' });
      g.appendChild(C.svg('title', { text: r.label + ': ' + C.fmt(r.value, 1) + (opts.unit || '') + (r.lo !== undefined && r.lo !== null ? ' [' + C.fmt(r.lo, 1) + ', ' + C.fmt(r.hi, 1) + ']' : '') }));
      g.appendChild(C.svg('text', { class: 'label', x: left - 10, y: cy, 'text-anchor': 'end', 'dominant-baseline': 'central', text: r.label }));
      if (r.lo !== undefined && r.lo !== null) g.appendChild(C.svg('line', { class: 'ci-line', x1: x(r.lo), x2: x(r.hi), y1: cy, y2: cy }));
      g.appendChild(C.svg('circle', { class: 'dot' + (r.cls ? ' ' + r.cls : ''), cx: x(r.value), cy: cy, r: 5.5 }));
      g.appendChild(C.svg('text', { class: 'value', x: width - right + 8, y: cy, 'dominant-baseline': 'central', text: C.fmt(r.value, 1) + (opts.unit || '') }));
      svg.appendChild(g);
    });
    container.innerHTML = '';
    container.classList.add('chart-wrap');
    container.appendChild(svg);
    return svg;
  };
  /* grouped horizontal bars: rows [{label, values:[...]}], series [{name, cls}] */
  C.barGroups = function (container, rows, series, opts) {
    opts = opts || {};
    C.registerChart(container, function () { C.barGroups(container, rows, series, opts); });
    var maxLabel = rows.reduce(function (m, r) { return Math.max(m, String(r.label).length); }, 0);
    var width = opts.width || C.chartWidth(container, opts), left = opts.left || Math.min(300, Math.max(120, Math.round(maxLabel * 6.9) + 16)), right = 80, top = 20, bottom = 26, barH = opts.barH || 12, gap = 3;
    var groupH = series.length * (barH + gap) + 12;
    var height = top + rows.length * groupH + bottom;
    var max = opts.max || Math.max.apply(null, rows.map(function (r) { return Math.max.apply(null, r.values.map(function (v) { return v || 0; })); })) * 1.08;
    var x = function (v) { return left + v / max * (width - left - right); };
    var svg = C.svg('svg', { class: 'chart', viewBox: '0 0 ' + width + ' ' + height, role: 'img', 'aria-label': opts.ariaLabel || 'Bar chart' });
    rows.forEach(function (r, i) {
      var y0 = top + i * groupH;
      svg.appendChild(C.svg('text', { class: 'label', x: left - 10, y: y0 + groupH / 2 - 4, 'text-anchor': 'end', 'dominant-baseline': 'central', text: r.label }));
      series.forEach(function (s, j) {
        var v = r.values[j]; if (v === null || v === undefined) return;
        var y = y0 + j * (barH + gap);
        var g = C.svg('g', { class: 'hot' });
        g.appendChild(C.svg('title', { text: r.label + ' — ' + s.name + ': ' + C.fmt(v, opts.digits) }));
        var rect = C.svg('rect', { class: 'bar ' + (s.cls || ''), x: left, y: y, width: Math.max(0, x(v) - left), height: barH, rx: 2 });
        if (s.color) rect.style.fill = s.color;
        g.appendChild(rect);
        g.appendChild(C.svg('text', { class: 'value', x: x(v) + 6, y: y + barH / 2, 'dominant-baseline': 'central', text: C.fmt(v, opts.digits) }));
        svg.appendChild(g);
      });
    });
    container.innerHTML = '';
    container.classList.add('chart-wrap');
    container.appendChild(svg);
    var legend = C.h('div', { class: 'legend' }, series.map(function (s) { var sw = C.h('span', { class: 'sw' }); sw.style.background = s.color || 'var(--indigo)'; return C.h('span', {}, [sw, s.name]); }));
    container.appendChild(legend);
    return svg;
  };

  /* ---------- runtime error banner (also captured by headless renders) ---------- */
  C._errors = [];
  window.addEventListener('error', function (ev) {
    var msg = (ev.message || 'error') + (ev.filename ? ' (' + ev.filename.split('/').pop() + ':' + ev.lineno + ')' : '');
    C._errors.push(msg);
    var box = document.getElementById('js-errors');
    if (!box) { box = document.createElement('div'); box.id = 'js-errors'; box.className = 'js-errors'; box.setAttribute('role', 'alert'); document.body.appendChild(box); }
    box.textContent = 'A script on this page failed (' + C._errors.length + '): ' + C._errors.join(' | ');
  });

  /* ---------- boot ---------- */
  document.addEventListener('DOMContentLoaded', function () {
    C.initTheme(); C.initTabs(); C.initSegmented(); C.initCopy(); C.initNav();
    document.querySelectorAll('table.data[data-sortable]').forEach(C.makeSortable);
    C.renderMath(document.body);
    document.dispatchEvent(new CustomEvent('copeer:ready'));
  });
})();
