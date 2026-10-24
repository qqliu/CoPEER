#!/usr/bin/env python3
"""
Blind TEST-SEARCH for record Algorithms_43__sol5.

TARGET CLAIM (solution line 0047, verbatim):

    S° = {y in R^n | y^T a_i <= b_i for all i with b_i > 0}
         inter {y in R^n | y = lambda a_i, lambda >= 0 for all i with b_i = 0}.

for S = {x in R^n | A x <= b}, with rows a_i^T of A.

Secondary claim (lines 0033-0040):

    "If b_i > 0, the maximum of y^T x subject to a_i^T x <= b_i is y^T a_i / b_i
     (achieved at x = a_i / b_i)"

Both are *directly implementable* membership / value predicates, so this file:

  1. IMPLEMENTATION (faithful): turns line 0047 into a membership predicate
     member_solution(A, b, y) exactly as written -- including its bugs, and
     including the fact that rows with b_i < 0 are simply not mentioned by the
     formula (so they impose nothing).

  2. ORACLE (exact, complete, reference computation): y in S° iff
     sup_{x in S} y^T x <= 1 iff the linear system
         { a_i^T x <= b_i for all i } U { y^T x > 1 }
     is INFEASIBLE.  Feasibility of a mixed strict/non-strict rational linear
     system is decided *exactly and completely* by Fourier-Motzkin elimination
     over Fraction arithmetic (no floats anywhere, no sampling).  Independent
     cross-checks are run against (a) a hand-derived interval oracle for n = 1
     and (b) explicit integer witnesses x in S with y^T x > 1.

  3. SEARCH: exhaustive over a bounded family of tiny instances
     (n in {1,2}, m <= 3, integer entries in [-2,2] / [-1,1]) crossed with a
     rational grid of candidate y, plus the adversarial constructions named in
     the triage sketches.  Deterministic: no randomness, fixed enumeration
     order, first failure in lexicographic enumeration order is reported.

No floating point value is ever used to decide anything.
"""

from fractions import Fraction as F
from itertools import product

# --------------------------------------------------------------------------
# 0. Exact linear-arithmetic core: Fourier-Motzkin with strict inequalities
# --------------------------------------------------------------------------
# A constraint is (coeffs, rhs, strict) meaning  sum_j coeffs[j]*x_j  <= rhs
# (or < rhs when strict is True).  All entries are Fraction.


def _combine(u, l, k):
    """Eliminate variable k from upper-bound constraint u (coeff>0) and
    lower-bound constraint l (coeff<0) by a positive combination."""
    cu, ru, su = u
    cl, rl, sl = l
    mu = -cl[k]          # > 0
    ml = cu[k]           # > 0
    coeffs = [mu * a + ml * b for a, b in zip(cu, cl)]
    coeffs[k] = F(0)     # exact cancellation by construction
    rhs = mu * ru + ml * rl
    return (coeffs, rhs, su or sl)


def _normalize(c):
    coeffs, rhs, strict = c
    g = 0
    for a in coeffs:
        g = g if a == 0 else g  # placeholder; scaling not needed for exactness
    return (coeffs, rhs, strict)


def feasible(constraints, nvars):
    """Exact, complete decision: does there exist a real x satisfying all
    constraints?  Fourier-Motzkin elimination (sound and complete for mixed
    strict / non-strict linear inequalities over an ordered field)."""
    cons = [([F(a) for a in c], F(r), bool(s)) for (c, r, s) in constraints]
    for k in range(nvars):
        upper, lower, keep = [], [], []
        for c in cons:
            if c[0][k] > 0:
                upper.append(c)
            elif c[0][k] < 0:
                lower.append(c)
            else:
                keep.append(c)
        new = list(keep)
        for u in upper:
            for l in lower:
                new.append(_combine(u, l, k))
        # prune trivially-true rows (0 <= r with r >= 0) to keep growth in check
        pruned = []
        for c in new:
            if all(a == 0 for a in c[0]):
                if c[1] > 0 or (c[1] == 0 and not c[2]):
                    continue  # 0 <= r, satisfied -> drop
                return False  # 0 <= negative, or 0 < 0 -> infeasible
            pruned.append(c)
        cons = pruned
    for c in cons:
        if c[1] < 0 or (c[1] == 0 and c[2]):
            return False
    return True


# --------------------------------------------------------------------------
# 1. FAITHFUL IMPLEMENTATION of the solution's explicit formula (line 0047)
# --------------------------------------------------------------------------

def member_solution(A, b, y):
    """Membership predicate for the set the solution CLAIMS equals S°.

    Literal transcription of line 0047:
      * for every row i with b_i > 0 : require y^T a_i <= b_i
      * for every row i with b_i = 0 : require y = lambda * a_i for some
        lambda >= 0
      * rows with b_i < 0 are not mentioned by the formula at all, so they
        impose nothing.  (Recorded verbatim in faithfulness notes.)
    """
    n = len(y)
    for a, bi in zip(A, b):
        if bi > 0:
            if sum(yj * aj for yj, aj in zip(y, a)) > bi:
                return False
        elif bi == 0:
            # y must be a nonnegative multiple of a_i
            if all(aj == 0 for aj in a):
                # a_i = 0: nonneg multiples of 0 is just {0}
                if any(yj != 0 for yj in y):
                    return False
                continue
            # find lambda from a nonzero coordinate, then verify all coords
            lam = None
            for j in range(n):
                if a[j] != 0:
                    lam = F(y[j], 1) / F(a[j], 1)
                    break
            if lam < 0:
                return False
            if any(F(y[j]) != lam * a[j] for j in range(n)):
                return False
    return True


def claimed_max_single(a, bi, y):
    """Lines 0033-0040: claimed value of max{ y^T x : a^T x <= b } when b > 0."""
    return F(sum(yj * aj for yj, aj in zip(y, a))) / F(bi)


# --------------------------------------------------------------------------
# 2. ORACLE
# --------------------------------------------------------------------------

def in_polar_oracle(A, b, y):
    """TRUE membership: y in S° iff y^T x <= 1 for every x with A x <= b,
    iff { A x <= b } U { y^T x > 1 } is infeasible."""
    n = len(y)
    cons = []
    for a, bi in zip(A, b):
        cons.append(([F(v) for v in a], F(bi), False))
    # y^T x > 1   <=>   -y^T x < -1
    cons.append(([F(-v) for v in y], F(-1), True))
    return not feasible(cons, n)


def in_polar_oracle_interval_n1(A, b, y):
    """Independent hand-derived oracle for n = 1 (cross-check only).
    S = {x : a_i x <= b_i}.  Build the interval, then sup y*x."""
    lo, hi = None, None  # None = unbounded on that side
    for (a,), bi in zip(A, b):
        a = F(a); bi = F(bi)
        if a > 0:
            v = bi / a
            hi = v if hi is None else min(hi, v)
        elif a < 0:
            v = bi / a
            lo = v if lo is None else max(lo, v)
        else:
            if bi < 0:
                return True  # S empty -> sup = -inf <= 1 -> every y in S°
    if lo is not None and hi is not None and lo > hi:
        return True  # empty
    y0 = F(y[0])
    if y0 > 0:
        if hi is None:
            return False  # sup = +inf
        return y0 * hi <= 1
    if y0 < 0:
        if lo is None:
            return False
        return y0 * lo <= 1
    return True  # y = 0 -> sup = 0 (S nonempty) <= 1


def integer_witness(A, b, y, rng=14):
    """Try to exhibit an explicit integer x in S with y^T x > 1 (certifies
    NON-membership without relying on Fourier-Motzkin).  Returns x or None."""
    n = len(y)
    for x in product(range(-rng, rng + 1), repeat=n):
        if all(sum(F(ai) * xi for ai, xi in zip(a, x)) <= F(bi)
               for a, bi in zip(A, b)):
            if sum(F(yj) * xj for yj, xj in zip(y, x)) > 1:
                return x
    return None


# --------------------------------------------------------------------------
# 3. Self-test of the exact core
# --------------------------------------------------------------------------

def selftest():
    ok = True
    # x <= 1 and -x <= -2  ->  infeasible
    ok &= not feasible([([F(1)], F(1), False), ([F(-1)], F(-2), False)], 1)
    # x <= 1 and -x <= -1  ->  feasible (x = 1)
    ok &= feasible([([F(1)], F(1), False), ([F(-1)], F(-1), False)], 1)
    # x < 1 and -x <= -1 -> infeasible (strictness matters)
    ok &= not feasible([([F(1)], F(1), True), ([F(-1)], F(-1), False)], 1)
    # 2D: x+y<=1, -x<=0, -y<=0, and x+y>1 -> infeasible
    ok &= not feasible([([F(1), F(1)], F(1), False), ([F(-1), F(0)], F(0), False),
                        ([F(0), F(-1)], F(0), False), ([F(-1), F(-1)], F(-1), True)], 2)
    # 2D unbounded: x1<=1, and x2>0 -> feasible
    ok &= feasible([([F(1), F(0)], F(1), False), ([F(0), F(-1)], F(0), True)], 2)
    return bool(ok)


def crosscheck_n1():
    """Fourier-Motzkin oracle vs. hand-derived interval oracle, n = 1."""
    bad = []
    rows = [(a, b) for a in (-2, -1, 0, 1, 2) for b in (-2, -1, 0, 1, 2)]
    ys = [F(p, q) for q in (1, 2, 3) for p in range(-6, 7)]
    ys = sorted(set(ys))
    for m in (1, 2):
        for combo in product(rows, repeat=m):
            A = [[r[0]] for r in combo]
            b = [r[1] for r in combo]
            for y in ys:
                o1 = in_polar_oracle(A, b, [y])
                o2 = in_polar_oracle_interval_n1(A, b, [y])
                if o1 != o2:
                    bad.append((A, b, y, o1, o2))
    return bad


# --------------------------------------------------------------------------
# 4. Exhaustive search for a disagreement
# --------------------------------------------------------------------------

def y_grid(n, dens=(1, 2, 5), nums=range(-5, 6)):
    vals = sorted(set(F(p, q) for q in dens for p in nums))
    return list(product(vals, repeat=n))


def search(n, m_max, coef_range, rhs_range, ylist, limit_report=400):
    """Exhaustive sweep. At most ONE mismatch is recorded per (A,b) instance so
    that the reported findings span many distinct instances rather than many
    candidate y for the same one."""
    rows = [(a, bi) for a in product(coef_range, repeat=n) for bi in rhs_range]
    findings = []
    checked = 0
    instances = 0
    for m in range(1, m_max + 1):
        for combo in product(rows, repeat=m):
            A = [list(r[0]) for r in combo]
            b = [r[1] for r in combo]
            instances += 1
            for y in ylist:
                checked += 1
                got = member_solution(A, b, list(y))
                exp = in_polar_oracle(A, b, list(y))
                if got != exp:
                    findings.append((A, b, list(y), got, exp))
                    break  # one witness per instance
            if len(findings) >= limit_report:
                return findings, checked, instances
    return findings, checked, instances


def show(A, b, y):
    cons = ", ".join(
        "%s.x <= %s" % (tuple(a), b[i]) for i, a in enumerate(A))
    return "S = {x : %s},  y = (%s)" % (cons, ", ".join(str(v) for v in y))


# --------------------------------------------------------------------------
# 5. Secondary claim: max{ y^T x : a^T x <= b } == y^T a / b   (lines 0033-40)
# --------------------------------------------------------------------------

def check_single_constraint_max():
    """Refute by exhibiting a feasible x with y^T x > claimed max."""
    out = []
    cases = [
        ([1, 0], 1, [0, 1]),   # triage p1's construction: sup is +inf
        ([1, 0], 1, [1, 1]),
        ([1], 2, [1]),         # n = 1, y not "parallel-scaled" properly
        ([2], 2, [1]),
    ]
    for a, bi, y in cases:
        n = len(a)
        c = claimed_max_single(a, bi, y)
        cons = [([F(v) for v in a], F(bi), False),
                ([F(-v) for v in y], -c, True)]   # y^T x > c
        beats = feasible(cons, n)
        w = None
        if beats:
            for x in product(range(-12, 13), repeat=n):
                if sum(F(ai) * xi for ai, xi in zip(a, x)) <= F(bi) and \
                   sum(F(yj) * xj for yj, xj in zip(y, x)) > c:
                    w = x
                    break
        out.append((a, bi, y, c, beats, w))
    return out


# --------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------

def main():
    print("=" * 78)
    print("TEST-SEARCH  Algorithms_43__sol5   (claim kind: CORRECTNESS)")
    print("=" * 78)
    print("Target claim (solution line 0047):")
    print("  S-polar = {y : y^T a_i <= b_i for all i with b_i > 0}")
    print("            inter {y : y = lambda a_i, lambda >= 0 for all i with b_i = 0}")
    print()

    print("[0] exact-core self-test (Fourier-Motzkin, Fraction arithmetic):",
          "PASS" if selftest() else "FAIL")
    bad = crosscheck_n1()
    print("[0] oracle cross-check n=1 (Fourier-Motzkin vs. interval oracle):",
          "AGREE on all %s" % "instances" if not bad else "DISAGREE %r" % (bad[:3],))
    if bad:
        print("    ORACLE SELF-CONSISTENCY FAILED -- aborting")
        return
    print()

    # ---- adversarial constructions named by the triage sketches -----------
    print("-" * 78)
    print("[1] adversarial constructions from the triage sketches")
    print("-" * 78)
    adv = [
        # triage p0: S = [0,2] via rows (1,2) and (-1,0); y = 2/5
        ([[1], [-1]], [2, 0], [F(2, 5)]),
        ([[1], [-1]], [2, 0], [F(1, 2)]),
        # triage p1: S = (-inf, 1] via row (1,1); y = -5
        ([[1]], [1], [F(-5)]),
    ]
    for A, b, y in adv:
        got = member_solution(A, b, y)
        exp = in_polar_oracle(A, b, y)
        w = None if exp else integer_witness(A, b, y)
        print("  %s" % show(A, b, y))
        print("    solution formula says y in S-polar : %s" % got)
        print("    oracle (exact)         y in S-polar : %s%s"
              % (exp, "" if w is None else
                 "   [witness x=%s in S with y.x=%s > 1]"
                 % (w, sum(F(a) * c for a, c in zip(y, w)))))
        print("    ==> %s" % ("MISMATCH" if got != exp else "agree"))
    print()

    # ---- exhaustive bounded search --------------------------------------
    print("-" * 78)
    print("[2] exhaustive search, n = 1, m <= 3, a in [-2,2], b in [-2,2],")
    print("    y over the rational grid {p/q : q in {1,2,5}, -5 <= p <= 5}")
    print("-" * 78)
    f1, n1, i1 = search(1, 3, range(-2, 3), range(-2, 3), y_grid(1))
    print("  (%d (instance, y) pairs examined over %d instances)" % (n1, i1))
    for A, b, y, got, exp in f1[:5]:
        w = None if exp else integer_witness(A, b, y)
        print("  MISMATCH: %s" % show(A, b, y))
        print("            formula=%s  oracle=%s%s" % (got, exp,
              "" if w is None else "  [witness x=%s, y.x=%s]"
              % (w, sum(F(a) * c for a, c in zip(y, w)))))
    print("  distinct (A,b) instances with a mismatch, n=1 sweep: %d / %d"
          % (len(f1), i1))
    print("  ... of which have every b_i > 0 (formula's stated branch): %d"
          % sum(1 for t in f1 if all(bi > 0 for bi in t[1])))
    print()

    print("-" * 78)
    print("[3] exhaustive search, n = 2, m <= 2, a in [-1,1]^2, b in [-1,1],")
    print("    y over {p/q : q in {1,2}, -2 <= p <= 2}^2")
    print("-" * 78)
    y2 = list(product(sorted(set(F(p, q) for q in (1, 2) for p in range(-2, 3))),
                      repeat=2))
    f2, n2, i2 = search(2, 2, range(-1, 2), range(-1, 2), y2)
    print("  (%d (instance, y) pairs examined over %d instances)" % (n2, i2))
    for A, b, y, got, exp in f2[:5]:
        w = None if exp else integer_witness(A, b, y, rng=8)
        print("  MISMATCH: %s" % show(A, b, y))
        print("            formula=%s  oracle=%s%s" % (got, exp,
              "" if w is None else "  [witness x=%s, y.x=%s]"
              % (w, sum(F(a) * c for a, c in zip(y, w)))))
    print("  distinct (A,b) instances with a mismatch, n=2 sweep: %d / %d"
          % (len(f2), i2))
    print("  ... of which have every b_i > 0 (formula's stated branch): %d"
          % sum(1 for t in f2 if all(bi > 0 for bi in t[1])))
    print()

    # ---- secondary claim -------------------------------------------------
    print("-" * 78)
    print("[4] secondary claim, lines 0033-0040:")
    print("    max{ y^T x : a^T x <= b } == y^T a / b   for b > 0")
    print("-" * 78)
    sec = check_single_constraint_max()
    for a, bi, y, c, beats, w in sec:
        print("  a=%s b=%s y=%s : claimed max = %s ; exists feasible x with "
              "y.x > claimed max ? %s%s"
              % (a, bi, y, c, beats,
                 "" if w is None else "  [x=%s, y.x=%s]"
                 % (list(w), sum(F(u) * v for u, v in zip(y, w)))))
    print()

    # ---- verdict ---------------------------------------------------------
    print("=" * 78)
    any_mismatch = bool(f1) or bool(f2) or any(
        member_solution(A, b, y) != in_polar_oracle(A, b, y) for A, b, y in adv)
    if any_mismatch:
        # Prefer a failure that lies ENTIRELY inside the formula's explicitly
        # stated branches (all b_i >= 0), so the refutation does not depend on
        # how rows with b_i < 0 -- which line 0047 never mentions -- are read.
        strict_pos = [t for t in (f1 + f2) if all(bi > 0 for bi in t[1])]
        pool = strict_pos or [t for t in (f1 + f2) if all(bi >= 0 for bi in t[1])] \
            or (f1 + f2)
        A, b, y, got, exp = pool[0]
        print("VERDICT: BUG_FOUND")
        print("The explicit polar formula on line 0047 is FALSE.")
        print("Headline failing input (all b_i > 0, i.e. squarely inside the")
        print("branch the formula explicitly states):")
        print("  %s" % show(A, b, y))
        print("  solution formula: y in S-polar = %s" % got)
        print("  exact oracle    : y in S-polar = %s" % exp)
        wit = None if exp else integer_witness(A, b, y, rng=14)
        if wit is not None:
            print("  certificate: x = %s satisfies A x <= b and y.x = %s > 1"
                  % (list(wit), sum(F(u) * v for u, v in zip(y, wit))))
        print("Canonical human-readable counterexample (triage p0 construction):")
        A0, b0, y0 = [[1], [-1]], [2, 0], [F(2, 5)]
        print("  S = {x in R : x <= 2, -x <= 0} = [0,2];  y = 2/5")
        print("  true polar of [0,2] = (-inf, 1/2];  sup_{x in [0,2]} (2/5)x = 4/5 <= 1")
        print("    -> oracle: y = 2/5 IS in S-polar  (%s)"
              % in_polar_oracle(A0, b0, y0))
        print("  formula: row 2 has b_2 = 0, so it demands y = lambda*(-1), lambda>=0,")
        print("           i.e. y <= 0 and y a nonpositive multiple of 1; 2/5 fails")
        print("    -> formula: y = 2/5 is NOT in S-polar (%s)"
              % member_solution(A0, b0, y0))
        print("  The two sets differ, so line 0047 does not describe S-polar.")
    else:
        print("VERDICT: NO_BUG_FOUND")
    print("=" * 78)


if __name__ == "__main__":
    main()
