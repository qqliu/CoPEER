#!/usr/bin/env python3
"""
BLIND counterexample search for record Algorithms_11__sol5.

TARGET CLAIM (quoted verbatim from the proof):

    "The ferry capacity k = c+1 implies at most c passengers can be
     transported at a time (excluding Charon). - Thus, the passengers can
     be partitioned into at most c independent sets, corresponding to a
     c-coloring of G."

INTERPRETATION (standard ferry / Charon puzzle model, which the quote
presupposes):

  * There is a conflict graph G on the set of passengers.  An edge {u, v}
    means u and v may never be left together on a bank unless Charon
    (the ferryman) is present on that bank.
  * The ferry (boat) holds Charon plus at most c passengers per crossing
    (capacity k = c+1 including Charon).
  * A schedule is FEASIBLE if, starting from all passengers and Charon on
    the left bank, a sequence of crossings (Charon plus any subset of at
    most c passengers from his current bank, possibly empty) moves
    everyone to the right bank, such that after every crossing the bank
    NOT containing Charon holds an independent set of G.

  The quoted sentence infers, from the fact that at most c passengers are
  transported at a time, that the passengers CAN be partitioned into at
  most c independent sets, i.e. that G is c-colorable.  Read as a logical
  implication it says:

      (the ferry instance (G, capacity c) is feasible)
          ==>  chi(G) <= c.

  A COUNTEREXAMPLE is therefore a concrete graph G and integer c >= 1
  such that the ferry instance with per-trip passenger capacity c is
  feasible, yet G is NOT c-colorable.

SEARCH SPACE (exhaustive, deterministic, exact arithmetic only):

  * number of passengers n = 1, 2, 3, 4  (in this order);
  * every labeled graph G on vertex set {0, ..., n-1}: all 2^C(n,2)
    edge subsets, enumerated in a fixed lexicographic order;
  * every capacity c = 1, ..., n-1  (for c >= n the coloring side is
    trivially true, so no counterexample is possible there);
  * feasibility decided EXACTLY by breadth-first search over the finite
    configuration space (subset of passengers on the left bank, side of
    Charon): at most 2^n * 2 states;
  * c-colorability decided EXACTLY by enumerating all c^n color
    assignments (itertools.product, fixed order).

  Everything is integer / frozenset combinatorics; no floats anywhere.

VERDICT: printed at the end; the first witness found (in the fixed
enumeration order) is named explicitly and re-verified.
"""

import itertools
from collections import deque


def is_independent(vertex_set, edges):
    """True iff vertex_set (an iterable of vertices) is independent in G."""
    vs = frozenset(vertex_set)
    return not any(u in vs and v in vs for (u, v) in edges)


def ferry_feasible(n, edges, c):
    """
    Exact decision: can Charon move all n passengers from the left bank to
    the right bank, carrying at most c passengers per crossing, such that
    after every crossing the bank without Charon is an independent set of
    the graph (vertices 0..n-1, edge list `edges`)?

    State = (frozenset of passengers on LEFT bank, charon_side) with
    charon_side in {'L', 'R'}.  BFS with fixed, deterministic expansion
    order.
    """
    all_pass = frozenset(range(n))
    start = (all_pass, 'L')
    goal = (frozenset(), 'R')
    if start == goal:
        return True
    seen = {start}
    queue = deque([start])
    verts_sorted = sorted(range(n))
    while queue:
        left, side = queue.popleft()
        here = left if side == 'L' else (all_pass - left)
        here_sorted = [v for v in verts_sorted if v in here]
        # Charon crosses with any subset S of his bank, |S| <= c
        # (S may be empty), in fixed lexicographic order.
        for r in range(0, c + 1):
            for S in itertools.combinations(here_sorted, r):
                S = frozenset(S)
                if side == 'L':
                    new_left = left - S
                    new_side = 'R'
                    unattended = new_left          # bank without Charon
                else:
                    new_left = left | S
                    new_side = 'L'
                    unattended = all_pass - new_left
                if not is_independent(unattended, edges):
                    continue
                state = (new_left, new_side)
                if state == goal:
                    return True
                if state not in seen:
                    seen.add(state)
                    queue.append(state)
    return False


def is_c_colorable(n, edges, c):
    """Exact decision by exhaustive enumeration of all c^n assignments."""
    if not edges:
        return True
    if c <= 0:
        return n == 0
    for coloring in itertools.product(range(c), repeat=n):
        if all(coloring[u] != coloring[v] for (u, v) in edges):
            return True
    return False


def recover_schedule(n, edges, c):
    """Reconstruct one feasible schedule (for witness display), or None."""
    all_pass = frozenset(range(n))
    start = (all_pass, 'L')
    goal = (frozenset(), 'R')
    parent = {start: None}
    queue = deque([start])
    verts_sorted = sorted(range(n))
    while queue:
        state = queue.popleft()
        left, side = state
        here = left if side == 'L' else (all_pass - left)
        here_sorted = [v for v in verts_sorted if v in here]
        for r in range(0, c + 1):
            for S in itertools.combinations(here_sorted, r):
                Sf = frozenset(S)
                if side == 'L':
                    new_left, new_side = left - Sf, 'R'
                    unattended = new_left
                else:
                    new_left, new_side = left | Sf, 'L'
                    unattended = all_pass - new_left
                if not is_independent(unattended, edges):
                    continue
                ns = (new_left, new_side)
                if ns not in parent:
                    parent[ns] = (state, tuple(S))
                    if ns == goal:
                        moves = []
                        cur = ns
                        while parent[cur] is not None:
                            prev, carried = parent[cur]
                            moves.append((prev[1], cur[1], carried))
                            cur = prev
                        moves.reverse()
                        return moves
                    queue.append(ns)
    return None


def main():
    witness = None
    for n in range(1, 5):                              # n = 1, 2, 3, 4
        possible_edges = list(itertools.combinations(range(n), 2))
        m = len(possible_edges)
        for mask in range(2 ** m):                     # fixed lexicographic order
            edges = tuple(e for i, e in enumerate(possible_edges)
                          if (mask >> i) & 1)
            for c in range(1, n):                      # c = 1, ..., n-1
                if ferry_feasible(n, edges, c) and not is_c_colorable(n, edges, c):
                    witness = (n, edges, c)
                    break
            if witness:
                break
        if witness:
            break

    print("Claim under test: feasibility of the ferry instance with per-trip")
    print("passenger capacity c (boat capacity k = c+1 incl. Charon) implies")
    print("the conflict graph G is c-colorable (partition into <= c")
    print("independent sets).")
    print()
    print("Search space: all labeled graphs on n = 1..4 vertices")
    print("(every edge subset), all capacities c = 1..n-1;")
    print("feasibility by exact BFS, colorability by exact enumeration.")
    print()

    if witness is None:
        print("VERDICT: NO COUNTEREXAMPLE FOUND in the swept space.")
        return

    n, edges, c = witness
    print("VERDICT: WITNESS FOUND (first in fixed enumeration order)")
    print(f"  n = {n} passengers, vertices {{0..{n-1}}}")
    print(f"  conflict graph edges E = {sorted(edges)}")
    print(f"  capacity c = {c} passengers per trip (boat k = c+1 = {c+1})")
    print()
    # Re-verify both sides explicitly.
    assert ferry_feasible(n, edges, c) is True
    assert is_c_colorable(n, edges, c) is False
    print(f"  CHECK 1 (feasible): ferry instance IS solvable with capacity {c}.")
    sched = recover_schedule(n, edges, c)
    print("  Feasible schedule (Charon's crossings, carried passengers):")
    for i, (frm, to, carried) in enumerate(sched, 1):
        load = list(carried) if carried else "(nobody)"
        print(f"    step {i}: {frm} -> {to}, carrying {load}")
    print(f"  CHECK 2 (not colorable): G has NO proper {c}-coloring")
    print(f"    (all {c}**{n} = {c ** n} assignments enumerated; each hits an edge),")
    print(f"    so the passengers CANNOT be partitioned into <= {c} independent sets.")
    print()
    print("  Hence the quoted implication is FALSE: at most c passengers per")
    print("  trip does NOT imply a partition into at most c independent sets.")


if __name__ == "__main__":
    main()
