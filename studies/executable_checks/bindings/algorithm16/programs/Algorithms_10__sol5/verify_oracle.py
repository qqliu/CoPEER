#!/usr/bin/env python3
"""
INDEPENDENT VERIFIER for Algorithms_10__sol5.

Written from scratch.  No import from, and no copy of, test.py.
Deliberately different internal representations and different algorithms:

  * graph stored as a set of frozenset({u,v}) EDGES; neighbourhoods are computed
    by scanning the edge set (test.py used precomputed adjacency lists);
  * the walk oracle is a LAYERED-REACHABILITY + PARENT-POINTER backtrack
    (test.py used an exhaustive itertools.product over W_1 x ... x W_k);
    a separate independent brute force is used only to cross-validate MY oracle;
  * the solution's construction is explored over ALL admissible choice
    sequences (a DFS over every vertex the proof licenses), not one
    deterministic tie-break, so the verdict cannot hinge on a tie-break rule.

Everything is exact: ints and fractions.Fraction.  No floating point.

WHAT IS BEING CHECKED
---------------------
Problem hypothesis (H):  n even, and for EVERY S subset V with |S| = n/2,
        |N(S)| >= n/2 + alpha*n,      N(S) = {w : exists v in S, {v,w} in E}.
Given W_1..W_k with |W_i| >= (1-alpha)n, a walk (v_1..v_k), v_i in W_i,
{v_i,v_{i+1}} in E, must exist.

Solution 5's claimed step (lines 0007-0022): with S = {v_m} a SINGLETON,
        |N(S)| >= n/2 + alpha*n   and hence   N(S) cap W_{m+1} != empty.
"""

from fractions import Fraction
from itertools import combinations, product
import sys

# ---------------------------------------------------------------- graph model


def E(*pairs):
    """Edge set as a set of frozensets."""
    s = set()
    for (u, v) in pairs:
        if u == v:
            raise ValueError("self loop")
        s.add(frozenset((u, v)))
    return s


def nbrs_of_vertex(edges, v, closed=False):
    out = set()
    for e in edges:
        if v in e:
            for w in e:
                if w != v:
                    out.add(w)
    if closed:
        out.add(v)
    return out


def N(edges, S, closed=False):
    """Neighbourhood of a SET, computed by scanning edges (open by default)."""
    out = set()
    for e in edges:
        a, b = tuple(e)
        if a in S:
            out.add(b)
        if b in S:
            out.add(a)
    if closed:
        out |= set(S)
    return out


# ------------------------------------------------------- hypothesis checking


def min_expansion(n, edges, closed=False):
    """min_{|S| = n/2} |N(S)|.  Requires n even."""
    if n % 2:
        raise ValueError("hypothesis speaks of |S| = n/2; n must be even")
    return min(len(N(edges, set(S), closed))
               for S in combinations(range(n), n // 2))


def hypothesis_holds(n, edges, alpha, closed=False):
    """Exact check of (H).  alpha is a Fraction."""
    thr = Fraction(n, 2) + Fraction(alpha) * n
    for S in combinations(range(n), n // 2):
        if Fraction(len(N(edges, set(S), closed))) < thr:
            return False, set(S)
    return True, None


def Ws_admissible(n, alpha, Ws):
    need = (1 - Fraction(alpha)) * n
    bad = [i for i, W in enumerate(Ws) if Fraction(len(W)) < need]
    return (not bad), need, bad


# --------------------------------------------- MY oracle: layered reachability


def oracle_walk(n, edges, Ws):
    """Return a valid walk or None.

    R_1 = W_1 ; R_{i+1} = N(R_i) cap W_{i+1}.  R_i is exactly the set of
    endpoints of valid length-(i-1) constrained walks, so a walk exists iff
    R_k is non-empty; parent pointers rebuild one.  This is a genuinely
    different algorithm from an exhaustive product enumeration.
    """
    k = len(Ws)
    layers = [set(Ws[0])]
    parents = [dict()]
    for i in range(1, k):
        prev = layers[-1]
        cur, par = set(), {}
        for v in prev:
            for w in nbrs_of_vertex(edges, v):
                if w in Ws[i] and w not in par:
                    par[w] = v
                    cur.add(w)
        layers.append(cur)
        parents.append(par)
        if not cur:
            return None
    if not layers[-1]:
        return None
    v = min(layers[-1])
    walk = [v]
    for i in range(k - 1, 0, -1):
        v = parents[i][v]
        walk.append(v)
    walk.reverse()
    return walk


def brute_force_walk(n, edges, Ws):
    """Independent cross-check of MY oracle: raw enumeration."""
    for cand in product(*[sorted(W) for W in Ws]):
        if all(frozenset((cand[i], cand[i + 1])) in edges
               for i in range(len(cand) - 1)):
            return list(cand)
    return None


def check_walk(edges, Ws, walk):
    """Independently validate a claimed walk."""
    if walk is None:
        return False
    if len(walk) != len(Ws):
        return False
    if any(walk[i] not in Ws[i] for i in range(len(Ws))):
        return False
    return all(frozenset((walk[i], walk[i + 1])) in edges
               for i in range(len(walk) - 1))


# ------------------------------- the solution's construction, ALL choices open


def stuck_prefixes(n, edges, Ws, closed=False):
    """DFS over EVERY choice sequence the solution's proof licenses.

    Base case: v_1 may be ANY vertex of W_1 ("any single vertex forms a path").
    Step: v_{m+1} may be ANY vertex of N({v_m}) cap W_{m+1} ("we can choose").
    Returns (list_of_stuck_prefixes, list_of_complete_walks).
    A stuck prefix is a sequence the proof asserts is always extendable but
    which has N({last}) cap W_{next} = empty.
    """
    k = len(Ws)
    stuck, done = [], []

    def rec(pref):
        m = len(pref)
        if m == k:
            done.append(list(pref))
            return
        cand = N(edges, {pref[-1]}, closed) & set(Ws[m])
        if not cand:
            stuck.append(list(pref))
            return
        for w in sorted(cand):
            rec(pref + [w])

    for v in sorted(Ws[0]):
        rec([v])
    return stuck, done


# ------------------------------------------------------------------- headline


def headline():
    print("=" * 74)
    print("PART 1 -- independent recheck of the reported failing input")
    print("=" * 74)
    n = 6
    edges = E(*([tuple(p) for p in combinations([1, 2, 3, 4, 5], 2)] + [(0, 1)]))
    alpha = Fraction(1, 3)
    Ws = [{0, 2, 3, 4}, {2, 3, 4, 5}]

    print("V = {0..5}, E = K5 on {1..5} + edge (0,1); |E| = %d" % len(edges))
    print("degrees: " + ", ".join("d(%d)=%d" % (v, len(nbrs_of_vertex(edges, v)))
                                  for v in range(n)))

    me = min_expansion(n, edges)
    thr = Fraction(n, 2) + alpha * n
    print("min_{|S|=3} |N(S)| = %d ; threshold n/2 + alpha*n = %s (alpha=%s)"
          % (me, thr, alpha))
    ok, badS = hypothesis_holds(n, edges, alpha)
    print("HYPOTHESIS (H) over all %d subsets of size 3: %s"
          % (len(list(combinations(range(n), 3))), "HOLDS" if ok else
             "FAILS at %s" % sorted(badS)))
    adm, need, bad = Ws_admissible(n, alpha, Ws)
    print("|W_1|=%d, |W_2|=%d ; need >= (1-alpha)n = %s -> %s"
          % (len(Ws[0]), len(Ws[1]), need, "ADMISSIBLE" if adm else "BAD %s" % bad))

    print()
    print("(a) is the quoted singleton inequality |N({v})| >= %s true?" % thr)
    for v in range(n):
        d = len(nbrs_of_vertex(edges, v))
        print("      v=%d: |N({%d})| = %d  %s %s" %
              (v, v, d, ">=" if Fraction(d) >= thr else "<  *** FALSE ***", thr))

    print()
    print("(b) the solution's construction, over ALL licensed choices:")
    stuck, done = stuck_prefixes(n, edges, Ws)
    for p in stuck:
        last = p[-1]
        print("      STUCK prefix %s : N({%d}) = %s, W_%d = %s, cap = {}"
              % (p, last, sorted(nbrs_of_vertex(edges, last)),
                 len(p) + 1, sorted(Ws[len(p)])))
    print("      complete walks the construction can also reach: %s" % done)

    print()
    ow = oracle_walk(n, edges, Ws)
    bf = brute_force_walk(n, edges, Ws)
    print("(c) MY layered oracle    : %s   (valid: %s)"
          % (ow, check_walk(edges, Ws, ow)))
    print("    independent brute fce: %s   (valid: %s)"
          % (bf, check_walk(edges, Ws, bf)))
    assert (ow is None) == (bf is None), "my two oracles disagree!"

    print()
    print("(d) closed-neighbourhood reading N[S] = S u N(S):")
    me_c = min_expansion(n, edges, closed=True)
    ok_c, _ = hypothesis_holds(n, edges, alpha, closed=True)
    st_c, _ = stuck_prefixes(n, edges, Ws, closed=True)
    print("      min_{|S|=3}|N[S]| = %d, (H): %s ; |N[{0}]| = %d ; stuck: %s"
          % (me_c, "HOLDS" if ok_c else "FAILS", len(nbrs_of_vertex(edges, 0, True)),
             st_c))

    print()
    print("(e) k = 3, W_3 = {2,3,4,5}:")
    Ws3 = [{0, 2, 3, 4}, {2, 3, 4, 5}, {2, 3, 4, 5}]
    st3, _ = stuck_prefixes(n, edges, Ws3)
    o3 = oracle_walk(n, edges, Ws3)
    print("      stuck prefixes: %s ; oracle walk: %s (valid: %s)"
          % (st3, o3, check_walk(edges, Ws3, o3)))

    verdict = (ok and adm and len(stuck) > 0 and ow is not None
               and check_walk(edges, Ws, ow))
    print()
    print("PART 1 RESULT: hypothesis holds, W's admissible, the proof's own "
          "construction\n  has a licensed prefix it cannot extend, and a valid "
          "walk demonstrably exists -> %s" % ("CONFIRMED" if verdict else "NOT confirmed"))
    return verdict


# ---------------------------------------------------------- exhaustive n = 6


def exhaustive():
    print()
    print("=" * 74)
    print("PART 2 -- my own exhaustive sweep over all labelled graphs on n = 6")
    print("=" * 74)
    n = 6
    pairs = [tuple(p) for p in combinations(range(n), 2)]
    subsets = [frozenset(c) for size in range(1, n + 1)
               for c in combinations(range(n), size)]

    n_graphs = 0
    n_hyp = 0
    n_inst = 0
    ces = []
    for mask in range(1 << len(pairs)):
        edges = E(*[pairs[i] for i in range(len(pairs)) if mask >> i & 1])
        n_graphs += 1
        me = min_expansion(n, edges)
        alpha = Fraction(me, n) - Fraction(1, 2)     # largest valid alpha
        if alpha <= 0:
            continue
        n_hyp += 1
        need = (1 - alpha) * n
        good = [W for W in subsets if Fraction(len(W)) >= need]
        for W1 in good:
            for W2 in good:
                n_inst += 1
                Ws = [set(W1), set(W2)]
                stuck, _ = stuck_prefixes(n, edges, Ws)
                if not stuck:
                    continue
                ow = oracle_walk(n, edges, Ws)
                if ow is not None:
                    assert check_walk(edges, Ws, ow)
                    ces.append((len(edges), sorted(tuple(sorted(e)) for e in edges),
                                alpha, sorted(W1), sorted(W2), stuck[0], ow))
    print("graphs enumerated ................. %d" % n_graphs)
    print("graphs satisfying (H) for some a>0  %d" % n_hyp)
    print("admissible (G,W1,W2) instances .... %d" % n_inst)
    print("instances where the proof's step has a stuck licensed prefix")
    print("  while a constrained walk provably exists: %d" % len(ces))
    if ces:
        m = min(ces, key=lambda t: (t[0], t[1], t[3], t[4]))
        print("fewest-edge such instance:")
        print("   E      = %s" % (m[1],))
        print("   alpha  = %s  ((1-alpha)n = %s)" % (m[2], (1 - m[2]) * n))
        print("   W1 = %s , W2 = %s" % (m[3], m[4]))
        print("   stuck licensed prefix = %s ; oracle walk = %s" % (m[5], m[6]))
    return len(ces)


# ------------------------------------------- sanity: the THEOREM itself is true


def theorem_sanity():
    """The statement to be proved is TRUE; only solution 5's argument is broken.

    Verify on the same exhaustive family: whenever (H) holds and the W_i are
    admissible, my layered oracle always finds a walk.  If this ever failed,
    the 'counterexamples' above would be counterexamples to the problem, not
    to the solution -- which would mean the harness had mis-set up the test.
    """
    print()
    print("=" * 74)
    print("PART 3 -- control: is the THEOREM true on every admissible n=6 "
          "instance?")
    print("=" * 74)
    n = 6
    pairs = [tuple(p) for p in combinations(range(n), 2)]
    subsets = [frozenset(c) for size in range(1, n + 1)
               for c in combinations(range(n), size)]
    checked = 0
    failures = 0
    for mask in range(1 << len(pairs)):
        edges = E(*[pairs[i] for i in range(len(pairs)) if mask >> i & 1])
        me = min_expansion(n, edges)
        alpha = Fraction(me, n) - Fraction(1, 2)
        if alpha <= 0:
            continue
        need = (1 - alpha) * n
        good = [W for W in subsets if Fraction(len(W)) >= need]
        for W1 in good:
            for W2 in good:
                checked += 1
                if oracle_walk(n, edges, [set(W1), set(W2)]) is None:
                    failures += 1
    print("admissible instances checked: %d ; instances with NO walk: %d"
          % (checked, failures))
    print("=> the theorem holds on every one of them, so the failures found in "
          "PART 2\n   are failures of solution 5's argument, not of the problem "
          "statement.")
    return failures


def main():
    v1 = headline()
    nce = exhaustive()
    fails = theorem_sanity()
    print()
    print("=" * 74)
    if v1 and nce > 0 and fails == 0:
        print("INDEPENDENT VERDICT: CONFIRMED")
        print(" - the quoted inequality |N({v_m})| >= n/2 + alpha*n is FALSE on a")
        print("   legal instance (|N({0})| = 1 vs threshold 5);")
        print(" - the construction the proof defines has a prefix the proof "
              "itself\n   licenses and cannot extend, on an instance where (H) "
              "holds and the\n   W_i are admissible;")
        print(" - a constrained walk does exist there, so the gap is real, not "
              "vacuous;")
        print(" - the theorem itself is true, so this refutes solution 5's "
              "inductive\n   step (the substantive load-bearing step), not the "
              "problem.")
    else:
        print("INDEPENDENT VERDICT: NOT CONFIRMED")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
