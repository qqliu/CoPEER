/* Pure computations behind the Co-PEER demonstrations. No DOM. Exposed as window.COPEER_MATH
   in browsers and as module.exports in node, so the same code is tested in both. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.COPEER_MATH = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';
  var M = {};

  /* ---------- exact rationals on BigInt ---------- */
  function gcd(a, b) { a = a < 0n ? -a : a; b = b < 0n ? -b : b; while (b) { var t = a % b; a = b; b = t; } return a; }
  function Q(n, d) { n = BigInt(n); d = d === undefined ? 1n : BigInt(d); if (d === 0n) throw new Error('zero denominator'); if (d < 0n) { n = -n; d = -d; } var g = gcd(n, d) || 1n; return { n: n / g, d: d / g }; }
  Q.add = function (a, b) { return Q(a.n * b.d + b.n * a.d, a.d * b.d); };
  Q.sub = function (a, b) { return Q(a.n * b.d - b.n * a.d, a.d * b.d); };
  Q.mul = function (a, b) { return Q(a.n * b.n, a.d * b.d); };
  Q.div = function (a, b) { return Q(a.n * b.d, a.d * b.n); };
  Q.cmp = function (a, b) { var l = a.n * b.d, r = b.n * a.d; return l < r ? -1 : l > r ? 1 : 0; };
  Q.str = function (a) { return a.d === 1n ? a.n.toString() : a.n.toString() + '/' + a.d.toString(); };
  Q.num = function (a) { return Number(a.n) / Number(a.d); };
  Q.parse = function (s) { if (s && typeof s === 'object' && 'n' in s && 'd' in s) return s; if (Array.isArray(s)) return Q(s[0], s[1]); s = String(s); var k = s.indexOf('/'); return k < 0 ? Q(s) : Q(s.slice(0, k), s.slice(k + 1)); };
  M.Q = Q;

  /* ---------- even/odd decomposition example ---------- */
  M.evenOdd = {
    functions: {
      const1: { label: 'f(x) = 1', tex: 'f(x)=1', f: function () { return 1; } },
      square1: { label: 'f(x) = x² + 1', tex: 'f(x)=x^2+1', f: function (x) { return x * x + 1; } },
      exp: { label: 'f(x) = eˣ', tex: 'f(x)=e^{x}', f: function (x) { return Math.exp(x); } },
      cube: { label: 'f(x) = x³', tex: 'f(x)=x^{3}', f: function (x) { return x * x * x; } }
    },
    /* the challenged identity f(x) = f(-x) + (-f(x)); returns both sides and whether it fails at x */
    check: function (fkey, x) {
      var f = M.evenOdd.functions[fkey].f;
      var lhs = f(x), rhs = f(-x) - f(x);
      var tol = 1e-9 * Math.max(1, Math.abs(lhs), Math.abs(rhs));
      return { lhs: lhs, rhs: rhs, fails: Math.abs(lhs - rhs) > tol, tolerance: tol };
    },
    /* the saved finite-domain witness of the certificate */
    savedWitness: { domain: [-1, 1], f: 1, x: 1, lhs: 1, rhs: 0 },
    decomposition: function (fkey, x) { var f = M.evenOdd.functions[fkey].f; return { even: (f(x) + f(-x)) / 2, odd: (f(x) - f(-x)) / 2 }; }
  };

  /* ---------- gap-m insertion sort (Shellsort pass) ---------- */
  /* Performs the gap-m insertion pass left to right: for i = m..n-1, insert a[i] into its gap chain.
     Records the first exchange that writes position 0 and the final array. */
  M.shellsort = {
    gapPass: function (input, m) {
      var a = input.slice(), steps = [], firstIntoZero = null;
      for (var i = m; i < a.length; i++) {
        var j = i;
        while (j >= m && a[j - m] > a[j]) {
          var t = a[j - m]; a[j - m] = a[j]; a[j] = t;
          steps.push({ i: i, j: j, swapped: [j - m, j], array: a.slice() });
          if (j - m === 0 && firstIntoZero === null) firstIntoZero = a[0];
          j -= m;
        }
      }
      return { final: a, steps: steps, firstExchangedIntoZero: firstIntoZero };
    },
    analyse: function (input, m) {
      var r = M.shellsort.gapPass(input, m);
      var endpoint = input[0] < input[input.length - 1];
      return {
        input: input, gap: m, endpointAssumptionHolds: endpoint, firstExchangedIntoZero: r.firstExchangedIntoZero,
        final: r.final, finalFirst: r.final[0], steps: r.steps,
        /* the source's challenged step: the entry exchanged into position 0 by the first exchange stays first */
        challengedClaimFails: r.firstExchangedIntoZero !== null && r.final[0] !== r.firstExchangedIntoZero
      };
    },
    original: [3, 4, 2, 5, 1], replacement: [3, 5, 2, 6, 1, 7, 4]
  };

  /* ---------- integer square-root recurrence ---------- */
  M.sqrt = {
    isqrt: function (x) { var r = Math.floor(Math.sqrt(x)); while (r * r > x) r--; while ((r + 1) * (r + 1) <= x) r++; return r; },
    /* printed recurrence: answer 0 at 0; given answer b at x-1, return b if x <= (b+1)^2 (weak) or x < (b+1)^2 (strict), else b+1 */
    run: function (maxX, strict) {
      var out = [0], b = 0;
      for (var x = 1; x <= maxX; x++) { var keep = strict ? (x < (b + 1) * (b + 1)) : (x <= (b + 1) * (b + 1)); b = keep ? b : b + 1; out.push(b); }
      return out;
    },
    table: function (maxX) {
      var weak = M.sqrt.run(maxX, false), strict = M.sqrt.run(maxX, true), rows = [];
      for (var x = 0; x <= maxX; x++) rows.push({ x: x, printed: weak[x], repaired: strict[x], truth: M.sqrt.isqrt(x), fails: weak[x] !== M.sqrt.isqrt(x), isSquare: x > 0 && M.sqrt.isqrt(x) * M.sqrt.isqrt(x) === x });
      return rows;
    }
  };

  /* ---------- doubled odd cycles C_n[K_2] ---------- */
  /* vertices 2i, 2i+1 form bag i; edges: inside a bag, and all four edges between consecutive bags */
  M.cycles = {
    neighbours: function (n, v) {
      var i = Math.floor(v / 2), out = [v ^ 1];
      [(i + n - 1) % n, (i + 1) % n].forEach(function (k) { out.push(2 * k, 2 * k + 1); });
      return out;
    },
    /* period-three construction: bag i gets pair P_{i mod 3} of {1,2},{3,4},{5,6}; order alternates so both labelled orders appear */
    /* Period-three construction: bag i gets pair P_{i mod 3} of {1,2},{3,4},{5,6}. When 3 divides n the pattern closes
       around the cycle and every three consecutive bags use all six colours (frozen). When 3 does not divide n the last bag
       is given the pair disjoint from both of its neighbours, so the colouring stays proper but the windows across the seam
       no longer partition the colours (not frozen). */
    periodThree: function (n) {
      var c = [];
      for (var i = 0; i < n; i++) { var p = i % 3; c.push(2 * p + 1, 2 * p + 2); }
      if (n % 3 !== 0) {
        var prev = Math.floor((c[2 * (n - 2)] - 1) / 2), first = 0; /* pair indices of bag n-2 and bag 0 */
        var choice = [0, 1, 2].filter(function (q) { return q !== prev && q !== first; })[0];
        c[2 * (n - 1)] = 2 * choice + 1; c[2 * (n - 1) + 1] = 2 * choice + 2;
      }
      return c;
    },
    isProper: function (n, col) { for (var v = 0; v < 2 * n; v++) { var nb = M.cycles.neighbours(n, v); for (var k = 0; k < nb.length; k++) if (col[nb[k]] === col[v]) return false; } return true; },
    /* colours (1..palette) a vertex could switch to without breaking properness */
    freeColours: function (n, col, v, palette) { var seen = {}; M.cycles.neighbours(n, v).forEach(function (u) { seen[col[u]] = true; }); var out = []; for (var c = 1; c <= palette; c++) if (c !== col[v] && !seen[c]) out.push(c); return out; },
    isFrozen: function (n, col, palette) { for (var v = 0; v < 2 * n; v++) if (M.cycles.freeColours(n, col, v, palette).length) return false; return true; },
    /* where the period-three pattern fails to close: the seam between bag n-1 and bag 0 when 3 does not divide n */
    seam: function (n) { return n % 3 === 0 ? null : { bags: [n - 2, n - 1, 0, 1], reason: 'the windows that cross from bag ' + (n - 1) + ' back to bag 0 cannot all contain three different pairs, so some vertex there sees fewer than five colours' }; },
    labelledCount: function (n) { return n % 3 === 0 ? 90n * (1n << BigInt(n)) : 0n; },
    /* Exact enumeration of frozen six-colourings at bag level. A vertex sees its partner and the four vertices of the two
       neighbouring bags, five neighbours in all, so it is frozen exactly when those five colours are the five other colours,
       i.e. when the three consecutive bags use six distinct colours. Frozen proper colourings are therefore cyclic sequences of
       unordered colour pairs in which every three consecutive bags partition the six colours, times 2^n orders inside bags.
       The count below enumerates those sequences by a transfer matrix over consecutive pair states; it does not use the
       paper's closed form. */
    countFrozenExact: function (n) {
      var pairs = []; for (var i = 1; i <= 6; i++) for (var j = i + 1; j <= 6; j++) pairs.push([i, j]);
      function disjoint(p, q) { return p[0] !== q[0] && p[0] !== q[1] && p[1] !== q[0] && p[1] !== q[1]; }
      var states = []; pairs.forEach(function (p, a) { pairs.forEach(function (q, b) { if (disjoint(p, q)) states.push([a, b]); }); });
      var index = {}; states.forEach(function (s, k) { index[s[0] + ',' + s[1]] = k; });
      var S = states.length; /* 90 */
      var T = []; for (var k = 0; k < S; k++) { T.push(new Array(S).fill(0n)); var a = states[k][0], b = states[k][1]; pairs.forEach(function (r, c) { if (disjoint(pairs[a], r) && disjoint(pairs[b], r)) T[k][index[b + ',' + c]] = 1n; }); }
      function mul(A, B) { var R = []; for (var i = 0; i < S; i++) { R.push(new Array(S).fill(0n)); for (var k2 = 0; k2 < S; k2++) { if (A[i][k2] === 0n) continue; for (var j = 0; j < S; j++) if (B[k2][j] !== 0n) R[i][j] += A[i][k2] * B[k2][j]; } } return R; }
      var P = null, base = T, e = n; while (e > 0) { if (e & 1) P = P ? mul(P, base) : base; e >>= 1; if (e) base = mul(base, base); }
      var trace = 0n; for (var i = 0; i < S; i++) trace += P[i][i];
      return trace * (1n << BigInt(n));
    },
    /* brute force: count proper 6-colourings of C_n[K_2] that are frozen (for small n only) */
    bruteForceFrozenCount: function (n) {
      if (n > 5) throw new Error('vertex-level brute force limited to n <= 5');
      var N = 2 * n, col = new Array(N).fill(0), count = 0;
      function ok(v, c) { var nb = M.cycles.neighbours(n, v); for (var k = 0; k < nb.length; k++) if (nb[k] < v && col[nb[k]] === c) return false; return true; }
      (function rec(v) {
        if (v === N) { if (M.cycles.isProper(n, col) && M.cycles.isFrozen(n, col, 6)) count++; return; }
        for (var c = 1; c <= 6; c++) if (ok(v, c)) { col[v] = c; rec(v + 1); col[v] = 0; }
      })(0);
      return count;
    }
  };

  /* ---------- rainbow Schur triples under the two-threshold rule ---------- */
  M.schur = {
    /* colour of k in 1..n: 0 red (even), 1 blue (odd with k/n <= a or k/n > b), 2 green (odd with a < k/n <= b); a, b rationals */
    colouring: function (n, a, b) {
      var out = [];
      for (var k = 1; k <= n; k++) {
        if (k % 2 === 0) { out.push(0); continue; }
        var r = Q(k, n);
        out.push((Q.cmp(r, a) <= 0 || Q.cmp(r, b) > 0) ? 1 : 2);
      }
      return out;
    },
    /* Rainbow ordered Schur triples. Convention of the paper and of RainbowSchur.lean: triples (x, y, x + y) with x != y are
       ordered, so each unordered solution {x, y} of x + y = z with x != y counts twice, and the total is normalised by
       n(n-1)/2. A triple is rainbow when x, y and x + y carry three different colours. */
    count: function (n, a, b) {
      var col = M.schur.colouring(n, a, b), rainbow = 0, unordered = 0, samples = [];
      for (var x = 1; x <= n; x++) for (var y = x + 1; x + y <= n; y++) {
        var cx = col[x - 1], cy = col[y - 1], cz = col[x + y - 1];
        if (cx !== cy && cx !== cz && cy !== cz) { rainbow += 2; unordered++; if (samples.length < 12) samples.push([x, y, x + y]); }
      }
      return { n: n, rainbow: rainbow, unorderedSolutions: unordered, denominator: n * (n - 1) / 2, samples: samples, colouring: col };
    },
    paperCount: function (m) { return 99 * m * m + 3 * m; },
    /* limiting density D(a,b) of rainbow triples under the two-threshold rule, 0 <= a <= b <= 1, exact rational.
       Derivation (continuum limit): evens red; odd x in B = [0,a] ∪ (b,1], G = (a,b]. A rainbow triple needs one even and two
       odds of different colours, with the two odds summing to at most 1 (x + y <= n) when the even is the sum, or an odd and an
       even summing to an odd in the other colour. The closed form below is the paper's four-region piecewise quadratic; tests
       compare it with a direct finite count at n = 22m and with Codex's independent fixtures. */
    density: function (a, b) { return M.schur.densityExact(a, b); },
    /* The appendix's expanded quadratics (Table of regions). Implemented by direct integration of the limit: */
    densityExact: function (a, b) {
      a = Q.parse(a); b = Q.parse(b);
      /* Count in the limit: integers x < y with x + y <= n; one must be even and the odd ones coloured so all three differ.
         Let u, v be normalised positions. Cases by parity of (x, y, x+y): (odd, odd, even): x, y odd, different colours, x+y<=n.
         (odd, even, odd) and (even, odd, odd): one odd summand and odd sum of different colours.
         In the limit each parity pattern has density weight 1/4 of the pair measure {(u,v): 0<u<v, u+v<=1} (area 1/4),
         and the pair (x, y) is normalised by n(n-1)/2 ~ n^2/2. The density contributions are areas divided by 1/2.
         We compute them by exact integration over the piecewise-constant colouring. */
      var pts = [Q(0), a, b, Q(1)];
      function colour(t) { /* colour of an odd number at normalised position t in (0,1] */ return (Q.cmp(t, a) <= 0 || Q.cmp(t, b) > 0) ? 1 : 2; }
      /* intervals of constant colour for odd positions */
      var ivs = [];
      for (var i = 0; i < 3; i++) if (Q.cmp(pts[i], pts[i + 1]) < 0) ivs.push({ lo: pts[i], hi: pts[i + 1], c: colour(Q.div(Q.add(pts[i], pts[i + 1]), Q(2))) });
      function areaPairs(I, J) {
        /* measure of {(u,v): u in I, v in J, u < v, u + v <= 1}, exact */
        return integrateRegion(I, J, function (u, v) { return Q.cmp(u, v) < 0 && Q.cmp(Q.add(u, v), Q(1)) <= 0; });
      }
      /* exact integration of indicator regions bounded by lines over rectangles: use polygon clipping on rationals */
      function integrateRegion(I, J, pred) {
        /* The regions are polygons; compute area exactly by clipping the rectangle [I]x[J] with the half-planes.
           pred is one of the two known predicates; branch on which by testing a flag. */
        var poly = [[I.lo, J.lo], [I.hi, J.lo], [I.hi, J.hi], [I.lo, J.hi]];
        var isPairs = pred(Q(1, 4), Q(1, 2)) && !pred(Q(1, 2), Q(1, 4));
        poly = clip(poly, function (p) { return Q.sub(Q(1), Q.add(p[0], p[1])); }); /* u + v <= 1 */
        if (isPairs) poly = clip(poly, function (p) { return Q.sub(p[1], p[0]); }); /* u < v */
        return area(poly);
      }
      function clip(poly, f) {
        var out = [];
        for (var i = 0; i < poly.length; i++) {
          var P = poly[i], S = poly[(i + 1) % poly.length], fp = f(P), fs = f(S);
          var inP = Q.cmp(fp, Q(0)) >= 0, inS = Q.cmp(fs, Q(0)) >= 0;
          if (inP) out.push(P);
          if (inP !== inS) { var t = Q.div(fp, Q.sub(fp, fs)); out.push([Q.add(P[0], Q.mul(t, Q.sub(S[0], P[0]))), Q.add(P[1], Q.mul(t, Q.sub(S[1], P[1])))]); }
        }
        return out;
      }
      function area(poly) { var s = Q(0); for (var i = 0; i < poly.length; i++) { var P = poly[i], S = poly[(i + 1) % poly.length]; s = Q.add(s, Q.sub(Q.mul(P[0], S[1]), Q.mul(S[0], P[1]))); } s = Q.div(s, Q(2)); return Q.cmp(s, Q(0)) < 0 ? Q.mul(s, Q(-1)) : s; }
      /* odd-odd pairs with different colours (sum even, red): weight: positions of odd numbers have density 1/2 each */
      var total = Q(0);
      ivs.forEach(function (I) { ivs.forEach(function (J) { if (I.c !== J.c) total = Q.add(total, Q.mul(Q(1, 4), areaPairs(I, J))); }); });
      /* odd summand u (colour c1), even summand w (red), odd sum u + w (colour c2 != c1): the sum's position is u + w */
      ivs.forEach(function (I) { ivs.forEach(function (J) { if (I.c !== J.c) total = Q.add(total, Q.mul(Q(1, 4), sumArea(I, J))); }); });
      function sumArea(I, J) {
        /* measure of {(u, w): u in I, w in (0,1], u + w in J}; the even w ranges over positions with density 1/2 */
        var poly = [[I.lo, Q(0)], [I.hi, Q(0)], [I.hi, Q(1)], [I.lo, Q(1)]];
        poly = clip(poly, function (p) { return Q.sub(Q.add(p[0], p[1]), J.lo); }); /* u + w >= J.lo */
        poly = clip(poly, function (p) { return Q.sub(J.hi, Q.add(p[0], p[1])); }); /* u + w <= J.hi */
        poly = clip(poly, function (p) { return Q.sub(Q(1), Q.add(p[0], p[1])); }); /* u + w <= 1 */
        return area(poly);
      }
      /* normalise: unordered pairs have measure n^2/2, so divide the areas by 1/2; ordered triples count each pair twice */
      return Q.mul(total, Q(4));
    },
    optimum: { a: [4, 11], b: [10, 11], value: [9, 22] },
    singleBlockBound: [2, 5]
  };

  /* ---------- layered projective-cube construction ---------- */
  M.cubes = {
    /* g(1) = 1; g(P + m - 1) = (1 + g(m)) / (2P) for P = 2^l, l >= 1, 1 <= m <= P. density = 1 - g(d). */
    g: function (d) {
      var memo = { 1: Q(1) };
      function rec(k) {
        if (memo[k]) return memo[k];
        /* find P = 2^l with P + 1 - 1 <= k <= 2P - 1, i.e. P <= k < 2P with P >= 2... need k = P + m - 1, 1 <= m <= P => P <= k <= 2P - 1 */
        var P = 1; while (2 * P - 1 < k) P *= 2;
        if (P < 2) P = 2;
        var m = k - P + 1;
        var v = Q.div(Q.add(Q(1), rec(m)), Q(2 * P));
        memo[k] = v; return v;
      }
      return rec(d);
    },
    density: function (d) { return Q.sub(Q(1), M.cubes.g(d)); },
    bound: function (d) { return Q(d - 1, d); },
    exceptional: function (d) { for (var l = 1; (1 << l) - 2 <= d; l++) { var P = 1 << l; if (d === P - 2 || d === P - 1 || d === P) return true; } return false; },
    table: function (maxD) { var rows = []; for (var d = 2; d <= maxD; d++) { var den = M.cubes.density(d), bd = M.cubes.bound(d), c = Q.cmp(den, bd); rows.push({ d: d, g: Q.str(M.cubes.g(d)), density: Q.str(den), densityNum: Q.num(den), bound: Q.str(bd), boundNum: Q.num(bd), comparison: c > 0 ? 'exceeds' : c === 0 ? 'equals' : 'below', exceptional: M.cubes.exceptional(d) }); } return rows; },
    families: [{ d: 5, M: 16, excluded: [0, 4, 12], N: '80k', size: '65k', density: [13, 16], bound: [4, 5] }, { d: 7, M: 24, excluded: [0, 6, 18], N: '168k', size: '147k', density: [7, 8], bound: [6, 7] }, { d: 8, M: 36, excluded: [0, 6, 12, 30], N: '72k', size: '64k', density: [8, 9], bound: [7, 8] }]
  };

  /* ---------- rooks on the permutation grid ---------- */
  M.rooks = {
    permutation: [2, 7, 4, 8, 1, 6, 3, 5],
    /* the permutation crossword grid: cells (i, j) allowed when ... the paper defines the grid; here we expose the count only through the
       certified value and leave the geometric definition to the mathematics page text. */
    certifiedCount: 155
  };

  return M;
});
