#!/usr/bin/env python3
"""
Blind TEST-SEARCH for record Algorithms_36__sol5.

PROBLEM (Algorithms_36):
  (V,T1) and (V,T2) are two trees on a common vertex set V.  Prove that for
  every e in T1 there exists f in T2 such that BOTH (V,(T1\\{e}) u {f}) and
  (V,(T2\\{f}) u {e}) are trees.

TARGET CLAIM under test (solution 5, lines 0009-0011 and 0019-0027):
  "Since T2 is connected, there must exist at least one edge f in T2 that
   connects a vertex in A to a vertex in B.  Choose any such edge f."
  ... "Therefore (V,(T2 \\ {f}) u {e}) is a tree."

  i.e. the solution's *selection rule* for f is "any edge of T2 crossing the
  cut (A,B) induced by deleting e from T1", and it then asserts that this f
  makes BOTH exchanged graphs trees.  (The correct rule requires f to lie on
  the unique u-v path in T2, which is strictly stronger than crossing the cut
  when the path crosses the cut more than once.)

WHAT THIS FILE DOES
  1. FAITHFUL IMPLEMENTATION of the solution's procedure, exactly as written,
     including its bug: `solution_select_f` computes the components A,B of
     T1\\{e} by BFS, collects every edge of T2 crossing (A,B), and returns one
     of them chosen by the caller's `choice` policy.  The solution says
     "choose any such edge", so the faithful implementation is parameterised by
     the choice; the solution's assertion is a universally-quantified claim
     over that choice, and we test BOTH
        (a) the deterministic reading  "first crossing edge in sorted order",
        (b) the universal reading      "every crossing edge works".
  2. BRUTE-FORCE ORACLE `is_tree` : exact integer/set computation only
     (|E| = n-1, no self-loops/parallel edges, connected by BFS, acyclic by
     union-find).  No floating point anywhere in this file.
  3. SEARCH: exhaustive over all ordered pairs of labelled trees on n = 2..5
     vertices (Prufer enumeration, n^(n-2) trees each) x every e in T1 x every
     crossing f; deterministic seeded random sweep for n = 6..12; plus the
     adversarial construction from the triage sketch.

Deterministic: fixed seeds, no wall-clock, no sampling that affects the verdict
for the exhaustive range.
"""

import itertools
import random
from collections import deque

# ----------------------------------------------------------------------------
# Edge / graph helpers (exact, hashable, order-canonical)
# ----------------------------------------------------------------------------

def E(u, v):
    """Canonical undirected edge as a sorted 2-tuple of ints."""
    return (u, v) if u < v else (v, u)


def neighbors(n, edges):
    adj = {i: [] for i in range(n)}
    for (u, v) in edges:
        adj[u].append(v)
        adj[v].append(u)
    return adj


# ----------------------------------------------------------------------------
# 2. BRUTE-FORCE ORACLE
# ----------------------------------------------------------------------------

def is_tree(n, edges):
    """Reference checker: is (V,edges) a tree on n labelled vertices 0..n-1?

    Exact combinatorial checks only:
      - edges is a set of well-formed distinct undirected edges, no self-loops
      - |edges| == n - 1
      - graph is connected (BFS reaches all n vertices)
      - graph is acyclic (union-find never merges an already-merged pair)
    """
    edges = list(edges)
    seen = set()
    for (u, v) in edges:
        if u == v:
            return False                      # self-loop
        if not (0 <= u < n and 0 <= v < n):
            return False
        c = E(u, v)
        if c in seen:
            return False                      # parallel edge
        seen.add(c)
    if len(seen) != n - 1:
        return False

    # acyclicity via union-find
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for (u, v) in seen:
        ru, rv = find(u), find(v)
        if ru == rv:
            return False                      # cycle
        parent[ru] = rv

    # connectivity via BFS
    adj = neighbors(n, seen)
    seenv = {0}
    dq = deque([0])
    while dq:
        x = dq.popleft()
        for y in adj[x]:
            if y not in seenv:
                seenv.add(y)
                dq.append(y)
    return len(seenv) == n


# ----------------------------------------------------------------------------
# 1. FAITHFUL IMPLEMENTATION OF THE SOLUTION'S ALGORITHM
# ----------------------------------------------------------------------------

def components_after_removing(n, T1, e):
    """Step 1 of the solution: 'removing edge e from T1 disconnects the graph
    into exactly two connected components.  Let these components be A and B.'
    Implemented literally by BFS on T1 \\ {e}."""
    rest = [x for x in T1 if x != e]
    adj = neighbors(n, rest)
    A = set()
    dq = deque([e[0]])
    A.add(e[0])
    while dq:
        x = dq.popleft()
        for y in adj[x]:
            if y not in A:
                A.add(y)
                dq.append(y)
    B = set(range(n)) - A
    return A, B


def crossing_edges(T2, A, B):
    """Step 2 of the solution: 'there must exist at least one edge f in T2 that
    connects a vertex in A to a vertex in B.  Choose any such edge f.'
    Returns ALL such candidates, in canonical sorted order, so that a caller
    can realise 'choose any'."""
    return sorted(f for f in T2
                  if (f[0] in A and f[1] in B) or (f[0] in B and f[1] in A))


def solution_exchange(n, T1, T2, e, choice="first"):
    """The solution's full procedure for a fixed e in T1.

    choice = "first" : deterministic reading of 'choose any such edge f'
                       (first candidate in canonical sorted order)
    choice = int k   : the k-th candidate in canonical sorted order

    Returns (f, T1_new, T2_new) which the solution ASSERTS are both trees.
    """
    A, B = components_after_removing(n, T1, e)
    cands = crossing_edges(T2, A, B)
    if not cands:
        raise RuntimeError("solution's step 2 found no crossing edge")
    f = cands[0] if choice == "first" else cands[choice]
    return f, exch(T1, e, f), exch(T2, f, e)


def exch(T, drop, add):
    """(T \\ {drop}) u {add}, as a SET of edges (the problem writes \\ and u,
    so the result is a simple graph, not a multigraph)."""
    return sorted(set(x for x in T if x != drop) | {add})


# ----------------------------------------------------------------------------
# Tree generation (Prufer) for the search space
# ----------------------------------------------------------------------------

def _prufer_simple(n, seq):
    """Unambiguous O(n^2) Prufer decoder."""
    degree = [1] * n
    for x in seq:
        degree[x] += 1
    edges = []
    for x in seq:
        for i in range(n):
            if degree[i] == 1:
                edges.append(E(i, x))
                degree[i] -= 1
                degree[x] -= 1
                break
    rem = [i for i in range(n) if degree[i] == 1]
    edges.append(E(rem[0], rem[1]))
    return sorted(edges)


def all_labelled_trees(n):
    """All n^(n-2) labelled trees on vertices 0..n-1."""
    if n == 1:
        yield []
        return
    if n == 2:
        yield [E(0, 1)]
        return
    for seq in itertools.product(range(n), repeat=n - 2):
        yield _prufer_simple(n, seq)


def random_labelled_tree(n, rng):
    if n <= 2:
        return [E(0, 1)] if n == 2 else []
    seq = [rng.randrange(n) for _ in range(n - 2)]
    return _prufer_simple(n, seq)


# ----------------------------------------------------------------------------
# The CORRECT construction (used only for reporting, never for the verdict):
# f must lie on the unique u-v path in T2.
# ----------------------------------------------------------------------------

def path_edges_in_tree(n, T, u, v):
    adj = {i: [] for i in range(n)}
    for (a, b) in T:
        adj[a].append(b)
        adj[b].append(a)
    prev = {u: None}
    dq = deque([u])
    while dq:
        x = dq.popleft()
        if x == v:
            break
        for y in adj[x]:
            if y not in prev:
                prev[y] = x
                dq.append(y)
    out = []
    x = v
    while prev[x] is not None:
        out.append(E(prev[x], x))
        x = prev[x]
    return out


def a_correct_f_exists(n, T1, T2, e):
    """Does SOME f in T2 satisfy the theorem?  (sanity check that the theorem
    itself is true and only the solution's selection rule is broken.)"""
    A, B = components_after_removing(n, T1, e)
    for f in crossing_edges(T2, A, B):
        if is_tree(n, exch(T1, e, f)) and is_tree(n, exch(T2, f, e)):
            return f
    return None


# ----------------------------------------------------------------------------
# 3. SEARCH
# ----------------------------------------------------------------------------

def check_instance(n, T1, T2):
    """Return a list of failures for this (T1,T2) pair.

    A failure record is a dict describing an (e,f) where the solution's
    selection rule produced a graph the ORACLE says is not a tree.
    """
    fails = []
    for e in T1:
        A, B = components_after_removing(n, T1, e)
        cands = crossing_edges(T2, A, B)
        if not cands:
            fails.append(dict(kind="no_crossing_edge", e=e, f=None,
                              A=sorted(A), B=sorted(B)))
            continue
        for k, f in enumerate(cands):
            T1n = exch(T1, e, f)
            T2n = exch(T2, f, e)
            ok1 = is_tree(n, T1n)
            ok2 = is_tree(n, T2n)
            if not (ok1 and ok2):
                fails.append(dict(kind="exchange_not_tree", e=e, f=f,
                                  choice_index=k, is_first_choice=(k == 0),
                                  # "clean" = non-degenerate: e is not already an
                                  # edge of T2, so no set-union collapse.
                                  clean=(e not in T2 and f != e),
                                  A=sorted(A), B=sorted(B),
                                  T1_new_is_tree=ok1, T2_new_is_tree=ok2,
                                  T1_new=sorted(T1n), T2_new=sorted(T2n)))
    return fails


def fmt_edges(es):
    return "{" + ",".join("%d-%d" % (u + 1, v + 1) for (u, v) in sorted(es)) + "}"


def fmt_e(e):
    return "%d-%d" % (e[0] + 1, e[1] + 1)


def fmt_set(S):
    return "{" + ",".join(str(x + 1) for x in sorted(S)) + "}"


def main():
    print("=" * 78)
    print("TEST-SEARCH  record_id = Algorithms_36__sol5")
    print("claim_kind  = CORRECTNESS")
    print("target      = 'Choose ANY edge f of T2 crossing the cut (A,B) of T1\\\\{e};")
    print("               then (T2\\\\{f}) u {e} is a tree.'  (lines 0009-0011, 0027)")
    print("Vertices printed 1-indexed; oracle = is_tree (|E|=n-1 + BFS connected")
    print("+ union-find acyclic), exact integer/set arithmetic only.")
    print("=" * 78)

    # ---- 0. self-test of the oracle -------------------------------------
    assert is_tree(4, [E(0, 1), E(1, 2), E(2, 3)])
    assert not is_tree(4, [E(0, 1), E(0, 2), E(1, 2)])          # triangle + isolated
    assert not is_tree(4, [E(0, 1), E(1, 2)])                   # too few edges
    assert not is_tree(3, [E(0, 1), E(0, 1)])                   # parallel
    assert is_tree(2, [E(0, 1)])
    print("[oracle self-test] passed")

    # ---- A. adversarial construction from the triage sketch -------------
    print()
    print("--- A. adversarial construction from triage sketch (n=4) ---")
    n = 4
    T1 = [E(0, 1), E(1, 2), E(2, 3)]          # path 1-2-3-4
    T2 = [E(0, 1), E(0, 2), E(0, 3)]          # star at 1
    e = E(1, 2)                                # e = {2,3}
    assert is_tree(n, T1) and is_tree(n, T2)
    A, B = components_after_removing(n, T1, e)
    cands = crossing_edges(T2, A, B)
    print("T1 = %s   T2 = %s   e = %s" % (fmt_edges(T1), fmt_edges(T2), fmt_e(e)))
    print("A = %s  B = %s   crossing edges of T2 = %s"
          % (fmt_set(A), fmt_set(B), fmt_edges(cands)))
    adv_fail = None
    for k, f in enumerate(cands):
        T1n, T2n = exch(T1, e, f), exch(T2, f, e)
        ok1, ok2 = is_tree(n, T1n), is_tree(n, T2n)
        print("   f = %s (choice #%d): (T1\\e)+f = %s -> tree=%s ; "
              "(T2\\f)+e = %s -> tree=%s"
              % (fmt_e(f), k, fmt_edges(T1n), ok1, fmt_edges(T2n), ok2))
        if not (ok1 and ok2) and adv_fail is None:
            adv_fail = (f, k, ok1, ok2, T2n)
    if adv_fail:
        f, k, ok1, ok2, T2n = adv_fail
        print("   => solution's rule admits f = %s, but oracle says (T2\\f)+e = %s"
              " is NOT a tree (cycle 1-2-3, vertex 4 isolated)."
              % (fmt_e(f), fmt_edges(T2n)))
    good = a_correct_f_exists(n, T1, T2, e)
    print("   (theorem itself is fine: f = %s does satisfy both.)"
          % (fmt_e(good) if good else "NONE"))

    # ---- B. exhaustive over all labelled tree pairs, n = 2..5 -----------
    print()
    print("--- B. exhaustive: ALL ordered pairs of labelled trees, n = 2..5 ---")
    # smallest counterexample under the deterministic 'first crossing edge' rule,
    # restricted to non-degenerate instances (e not already in T2)
    first_choice_ce = None
    # smallest non-degenerate counterexample under 'some crossing f' ("any")
    any_choice_ce = None
    totals = []
    for n in range(2, 6):
        trees = list(all_labelled_trees(n))
        pairs = 0
        bad_pairs = 0
        bad_any = 0
        bad_first = 0
        theorem_ok = True
        for T1 in trees:
            for T2 in trees:
                pairs += 1
                fails = check_instance(n, T1, T2)
                if fails:
                    bad_pairs += 1
                    bad_any += len(fails)
                    for fl in fails:
                        if fl.get("is_first_choice"):
                            bad_first += 1
                            if first_choice_ce is None and fl.get("clean"):
                                first_choice_ce = (n, list(T1), list(T2), fl)
                        if any_choice_ce is None and fl.get("clean"):
                            any_choice_ce = (n, list(T1), list(T2), fl)
                # the THEOREM (some f works) must always hold
                for e in T1:
                    if a_correct_f_exists(n, T1, T2, e) is None:
                        theorem_ok = False
        totals.append((n, len(trees), pairs, bad_pairs, bad_any, bad_first))
        print("  n=%2d  trees=%5d  ordered pairs=%8d  pairs with a bad (e,f)=%7d"
              "  bad (e,f) choices=%8d  of which first-in-order=%6d  "
              "theorem-holds-for-some-f=%s"
              % (n, len(trees), pairs, bad_pairs, bad_any, bad_first, theorem_ok))
        assert theorem_ok, "the theorem itself failed -- oracle/impl bug"

    # ---- C. seeded random sweep, n = 6..12 ------------------------------
    print()
    print("--- C. seeded random sweep (seed=20260820), n = 6..12, 400 pairs each ---")
    rng = random.Random(20260820)
    for n in range(6, 13):
        bad_pairs = 0
        bad_first = 0
        bad_any = 0
        for _ in range(400):
            T1 = random_labelled_tree(n, rng)
            T2 = random_labelled_tree(n, rng)
            fails = check_instance(n, T1, T2)
            if fails:
                bad_pairs += 1
                bad_any += len(fails)
                bad_first += sum(1 for fl in fails if fl.get("is_first_choice"))
                if first_choice_ce is None:
                    for fl in fails:
                        if fl.get("is_first_choice") and fl.get("clean"):
                            first_choice_ce = (n, list(T1), list(T2), fl)
                            break
        print("  n=%2d  pairs=400  pairs with a bad (e,f)=%3d  bad (e,f) choices=%5d"
              "  of which first-in-order=%4d" % (n, bad_pairs, bad_any, bad_first))

    # ---- D. verdict ------------------------------------------------------
    print()
    print("=" * 78)
    if any_choice_ce is None:
        print("VERDICT: NO_BUG_FOUND")
    else:
        n, T1, T2, fl = any_choice_ce
        print("VERDICT: BUG_FOUND")
        print("Smallest NON-DEGENERATE counterexample (e not already in T2) to the")
        print("solution's selection rule ('choose ANY crossing edge f'):")
        print("  n  = %d   V = {1..%d}" % (n, n))
        print("  T1 = %s" % fmt_edges(T1))
        print("  T2 = %s" % fmt_edges(T2))
        print("  e  = %s   ->  A = %s, B = %s"
              % (fmt_e(fl["e"]), fmt_set(fl["A"]), fmt_set(fl["B"])))
        print("  f  = %s  (a T2-edge crossing the cut, choice #%d of the "
              "candidate list -- exactly what step 2 permits)"
              % (fmt_e(fl["f"]), fl["choice_index"]))
        print("  (T1\\e)+f = %s  -> oracle is_tree = %s"
              % (fmt_edges(fl["T1_new"]), fl["T1_new_is_tree"]))
        print("  (T2\\f)+e = %s  -> oracle is_tree = %s   <== solution asserts True"
              % (fmt_edges(fl["T2_new"]), fl["T2_new_is_tree"]))
        print("  solution's claimed output at line 0027: '(V,(T2\\{f}) u {e}) is a "
              "tree' = True")
        print("  oracle output                          = %s"
              % fl["T2_new_is_tree"])
        if first_choice_ce is not None:
            n2, U1, U2, g = first_choice_ce
            print()
            print("Also fails under the DETERMINISTIC reading (f := first crossing "
                  "edge in canonical sorted order):")
            print("  n=%d  T1=%s  T2=%s  e=%s  f=%s  ->  (T2\\f)+e = %s  is_tree=%s"
                  % (n2, fmt_edges(U1), fmt_edges(U2), fmt_e(g["e"]),
                     fmt_e(g["f"]), fmt_edges(g["T2_new"]), g["T2_new_is_tree"]))
        print()
        print("ROOT CAUSE (line 0026): 'e was the unique edge in T1 connecting A "
              "and B' is true, but the solution needs f to lie on the unique u-v "
              "PATH in T2, not merely to cross the cut (A,B).  When that path "
              "crosses the cut more than once, a crossing f off the path leaves "
              "(T2\\{f})+e disconnected and cyclic.  The THEOREM is still true "
              "(verified above: some valid f always exists); the solution's "
              "selection rule is what is unsound.")
    print("=" * 78)


if __name__ == "__main__":
    main()
