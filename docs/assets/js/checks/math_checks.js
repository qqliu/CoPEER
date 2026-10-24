/* Checks of the demonstration mathematics (assets/js/math/labs.js) against the paper's statements and against
   Codex's independently generated fixtures. Runs in the browser (docs/tests.html) and in node (tests/run_checks.mjs). */
(function (root) {
  'use strict';
  function runMathChecks(M, F) {
    var out = [];
    function check(name, cond, detail) { out.push({ name: name, pass: !!cond, detail: detail || '' }); }
    var Q = M.Q;

    /* even/odd */
    var w = M.evenOdd.savedWitness, c1 = M.evenOdd.check('const1', 1);
    check('Even/odd: the saved witness f = 1 at x = 1 gives 1 on the left and 0 on the right', w.lhs === 1 && w.rhs === 0 && c1.lhs === 1 && c1.rhs === 0 && c1.fails);
    check('Even/odd: the constant function fails the identity at every sampled x', [-2, -0.5, 0, 0.3, 2].every(function (x) { return M.evenOdd.check('const1', x).fails; }));
    var xe = -Math.log(2) / 2, ce = M.evenOdd.check('exp', xe);
    check('Even/odd: e^x satisfies the challenged identity at x = -ln(2)/2 (so the readout must not call every x a counterexample)', !ce.fails, 'lhs ' + ce.lhs.toFixed(6) + ' rhs ' + ce.rhs.toFixed(6));
    check('Even/odd: the decomposition recovers f for several functions and x', ['const1', 'square1', 'exp', 'cube'].every(function (k) { return [-1.5, 0.7].every(function (x) { var d = M.evenOdd.decomposition(k, x); return Math.abs(d.even + d.odd - M.evenOdd.functions[k].f(x)) < 1e-9; }); }));
    if (F && F.even_odd_witness) check('Even/odd: fixture agrees on record, line, domain and values', F.even_odd_witness.record_id === 'reddit_learnmath_dm6itc' && F.even_odd_witness.reference_line === 5 && F.even_odd_witness.lhs === 1 && F.even_odd_witness.rhs === 0);

    /* shellsort */
    var o = M.shellsort.analyse(M.shellsort.original, 2), r = M.shellsort.analyse(M.shellsort.replacement, 2);
    check('Shellsort: original witness violates the endpoint assumption and ends with 1 first', !o.endpointAssumptionHolds && o.firstExchangedIntoZero === 2 && o.finalFirst === 1 && o.challengedClaimFails);
    check('Shellsort: replacement satisfies 3 < 4, exchanges 2 into front, final array (1,5,2,6,3,7,4)', r.endpointAssumptionHolds && r.firstExchangedIntoZero === 2 && r.final.join(',') === '1,5,2,6,3,7,4' && r.challengedClaimFails);
    if (F && F.shellsort_cases) check('Shellsort: both fixture cases reproduced exactly', F.shellsort_cases.every(function (c) { var a = M.shellsort.analyse(c.input, 2); return a.endpointAssumptionHolds === c.endpoint_assumption_holds && a.firstExchangedIntoZero === c.first_exchanged_into_zero && a.final.join(',') === c.final.join(',') && a.challengedClaimFails === c.challenged_claim_fails; }));

    /* square root */
    var t = M.sqrt.table(144);
    check('Square root: the printed recurrence returns 0 at 0 and fails exactly at the positive perfect squares up to 144', t.every(function (row) { return row.fails === row.isSquare; }) && t[0].printed === 0 && t[1].fails && t[4].fails && t[9].fails && !t[2].fails);
    check('Square root: the strict guard returns floor(sqrt(x)) for every x up to 144', t.every(function (row) { return row.repaired === row.truth; }));
    check('Square root: the printed value equals floor(sqrt(x-1)) for every positive x', t.slice(1).every(function (row) { return row.printed === M.sqrt.isqrt(row.x - 1); }));
    if (F && F.square_root_cases) check('Square root: all ' + F.square_root_cases.length + ' fixture inputs agree', F.square_root_cases.every(function (c) { return M.sqrt.run(c.x, false)[c.x] === c.original && M.sqrt.run(c.x, true)[c.x] === c.repaired && M.sqrt.isqrt(c.x) === c.integer_square_root; }));

    /* cycles */
    check('Cycles: exact bag-level enumeration equals 90 * 2^n when 3 | n and 0 otherwise, for odd n from 5 to 21', [5, 7, 9, 11, 13, 15, 17, 19, 21].every(function (n) { return M.cycles.countFrozenExact(n) === M.cycles.labelledCount(n); }));
    check('Cycles: vertex-level brute force agrees with the enumeration at n = 3 (720) and n = 5 (0)', BigInt(M.cycles.bruteForceFrozenCount(3)) === M.cycles.countFrozenExact(3) && M.cycles.countFrozenExact(3) === 720n && M.cycles.bruteForceFrozenCount(5) === 0);
    check('Cycles: the period-three colouring is proper for every odd n and frozen exactly when 3 | n', [5, 7, 9, 11, 13, 15, 21].every(function (n) { var col = M.cycles.periodThree(n); return M.cycles.isProper(n, col) && (M.cycles.isFrozen(n, col, 6) === (n % 3 === 0)); }));
    check('Cycles: every vertex of C_n[K_2] has five neighbours', [5, 9].every(function (n) { for (var v = 0; v < 2 * n; v++) if (M.cycles.neighbours(n, v).length !== 5) return false; return true; }));
    if (F && F.doubled_cycle_cases) check('Cycles: fixture constructions reproduce properness, frozenness and available recolourings', F.doubled_cycle_cases.every(function (c) { var n = c.cycle_length, col = c.colors.map(function (x) { return x + 1; }); if (M.cycles.isProper(n, col) !== c.period_three_construction_is_proper || M.cycles.isFrozen(n, col, 6) !== c.period_three_construction_is_frozen) return false; return c.available_single_vertex_recolors.every(function (av, v) { return M.cycles.freeColours(n, col, v, 6).map(function (x) { return x - 1; }).join(',') === av.join(','); }); }));

    /* Schur */
    check('Schur: 99 m^2 + 3 m rainbow ordered triples at n = 22m for m = 1..4 (102 of 231 at n = 22)', [1, 2, 3, 4].every(function (m) { var c = M.schur.count(22 * m, Q(4, 11), Q(10, 11)); return c.rainbow === M.schur.paperCount(m) && c.denominator === 22 * m * (22 * m - 1) / 2; }) && M.schur.count(22, Q(4, 11), Q(10, 11)).rainbow === 102);
    check('Schur: the limiting density has value 9/22 at (4/11, 10/11)', Q.str(M.schur.density([4, 11], [10, 11])) === '9/22');
    check('Schur: 9/22 is the maximum over a fine rational grid of the triangle 0 <= a <= b <= 1 and is attained only at (4/11, 10/11) on the grid containing it', (function () { var best = Q(0), where = []; for (var i = 0; i <= 44; i++) for (var j = i; j <= 44; j++) { var d = M.schur.density(Q(i, 44), Q(j, 44)); var c = Q.cmp(d, best); if (c > 0) { best = d; where = [[i, j]]; } else if (c === 0) where.push([i, j]); } return Q.str(best) === '9/22' && where.length === 1 && where[0][0] === 16 && where[0][1] === 40; })());
    check('Schur: rules with a = 0 or b = 1 reach at most 2/5 on the grid, with 2/5 attained', (function () { var best = Q(0); for (var k = 0; k <= 60; k++) { [M.schur.density(Q(0), Q(k, 60)), M.schur.density(Q(k, 60), Q(1))].forEach(function (d) { if (Q.cmp(d, best) > 0) best = d; }); } return Q.str(best) === '2/5'; })());
    check('Schur: the finite fraction (99m^2+3m)/C(22m,2) decreases towards 9/22 (m = 1, 5, 20, 50)', (function () { var prev = Infinity; return [1, 5, 20, 50].every(function (m) { var c = M.schur.count(22 * m, Q(4, 11), Q(10, 11)); var f = c.rainbow / c.denominator; var ok = f < prev && f > 9 / 22; prev = f; return ok; }) && Math.abs(prev - 9 / 22) < 0.001; })());
    if (F && F.schur_cases) check('Schur: all ' + F.schur_cases.length + ' finite fixture cases agree (counts, denominators, colourings)', F.schur_cases.every(function (c) { var r = M.schur.count(c.n, Q(c.a[0], c.a[1]), Q(c.b[0], c.b[1])); return r.rainbow === c.rainbow_ordered_triples && r.denominator === c.all_ordered_triples && r.colouring.join(',') === c.colors.join(','); }));
    if (F && F.schur_limiting_cases) check('Schur: all ' + F.schur_limiting_cases.length + ' limiting-density fixture cases agree exactly', F.schur_limiting_cases.every(function (c) { return Q.str(M.schur.density(c.a, c.b)) === c.density; }));

    /* projective cubes */
    var tbl = M.cubes.table(32);
    check('Cubes: density exceeds (d-1)/d exactly outside {2^l-2, 2^l-1, 2^l}, equality exactly at powers of two (d = 2..32)', tbl.every(function (r) { var pow2 = (r.d & (r.d - 1)) === 0; return (r.comparison === 'exceeds') === !r.exceptional && (r.comparison === 'equals') === pow2; }));
    check('Cubes: g(1) = 1 and g(2) = 1/2, g(3) = 3/8', Q.str(M.cubes.g(1)) === '1' && Q.str(M.cubes.g(2)) === '1/2' && Q.str(M.cubes.g(3)) === '3/8');
    if (F && F.layered_boundary_cases) check('Cubes: all ' + F.layered_boundary_cases.length + ' fixture dimensions agree on g(d), density, comparison and exceptionality', F.layered_boundary_cases.every(function (c) { var r = tbl.filter(function (x) { return x.d === c.d; })[0]; return r && r.g === c.g && r.density === c.density && r.comparison === c.comparison && r.exceptional === c.exceptional; }));
    check('Cubes: the three certified families have densities 13/16, 7/8, 8/9 above 4/5, 6/7, 7/8', M.cubes.families.every(function (f) { return Q.cmp(Q(f.density[0], f.density[1]), Q(f.bound[0], f.bound[1])) > 0; }));

    return out;
  }
  root.COPEER_CHECKS = root.COPEER_CHECKS || {};
  root.COPEER_CHECKS.runMathChecks = function () {
    var M = root.COPEER_MATH || (typeof require === 'function' ? require('../math/labs.js') : null);
    var F = root.COPEER_FIXTURES || null;
    return runMathChecks(M, F);
  };
})(typeof window !== 'undefined' ? window : globalThis);
