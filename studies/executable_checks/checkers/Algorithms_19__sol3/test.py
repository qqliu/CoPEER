#!/usr/bin/env python3
"""
Blind counterexample search for record Algorithms_19__sol3.

TARGET CLAIM (quoted verbatim from the proof):

    "Since T is a tree, e1 is a bridge in T, meaning that removing e1
     disconnects T into exactly two components. These components must be
     precisely S and V \\ S (as e1 connects these two sets)."

Formalization used here (taking the claim at face value, with only the
hypotheses the quoted text itself supplies):

  Hypotheses:
    - T is a (spanning) tree on a finite vertex set V.
    - S is a nonempty proper subset of V (so that "S and V \\ S" is a
      genuine two-sided cut).
    - e1 is an edge of T that "connects these two sets", i.e. e1 has one
      endpoint in S and the other in V \\ S.

  Claimed conclusions:
    (a) Removing e1 from T disconnects T into exactly two components.
    (b) These two components are PRECISELY S and V \\ S.

Part (a) is a standard fact (every tree edge is a bridge and its removal
yields exactly two components).  Part (b) is the load-bearing assertion:
it claims that merely because e1 crosses the cut (S, V\\S), the two
components of T - e1 must equal S and V \\ S.  That is only guaranteed
when e1 is the UNIQUE tree edge crossing the cut; the quoted text asserts
it from the crossing property alone.  We search exhaustively for a
counterexample: a tree T on V = {0,...,n-1}, a nonempty proper subset S,
and a tree edge e1 crossing the cut, such that the two components of
T - e1 are NOT {S, V \\ S} (or such that (a) fails, which it never does).

SEARCH SPACE (swept exhaustively, in a fixed deterministic order):
  for n = 2, 3, 4, 5:
    for every subset of the C(n,2) possible edges of size n-1 that forms
        a tree on V = {0,...,n-1} (edges in lexicographic order):
      for every nonempty proper subset S of V (by increasing bitmask):
        for every edge e1 of T with exactly one endpoint in S
            (in lexicographic order):
          check conclusions (a) and (b) by exact integer/set computation.

All arithmetic is exact (ints, frozensets); no floats, no randomness.
The first violating triple (T, S, e1) encountered is printed as the
witness and the program stops.  If none is found the sweep is exhaustive
over the space above.
"""

from itertools import combinations


def components_after_removal(n, edges, removed):
    """Exact connected components of graph ({0..n-1}, edges - {removed})."""
    adj = {v: [] for v in range(n)}
    for e in edges:
        if e == removed:
            continue
        a, b = e
        adj[a].append(b)
        adj[b].append(a)
    seen = [False] * n
    comps = []
    for start in range(n):
        if seen[start]:
            continue
        stack = [start]
        seen[start] = True
        comp = []
        while stack:
            v = stack.pop()
            comp.append(v)
            for w in adj[v]:
                if not seen[w]:
                    seen[w] = True
                    stack.append(w)
        comps.append(frozenset(comp))
    return comps


def is_tree(n, edges):
    """edges is a tuple of n-1 distinct edges on {0..n-1}: tree iff connected."""
    comps = components_after_removal(n, edges, None)
    return len(comps) == 1


def main():
    for n in range(2, 6):
        V = frozenset(range(n))
        all_edges = list(combinations(range(n), 2))  # lexicographic
        for edges in combinations(all_edges, n - 1):
            if not is_tree(n, edges):
                continue
            # nonempty proper subsets S of V, by increasing bitmask
            for mask in range(1, (1 << n) - 1):
                S = frozenset(v for v in range(n) if (mask >> v) & 1)
                Sc = V - S
                for e1 in edges:  # lexicographic within the tree
                    a, b = e1
                    crosses = (a in S) != (b in S)
                    if not crosses:
                        continue
                    comps = components_after_removal(n, edges, e1)
                    # Claim (a): exactly two components.
                    if len(comps) != 2:
                        print("WITNESS_FOUND (claim (a) fails)")
                        print("n =", n, "tree edges =", edges,
                              "S =", sorted(S), "e1 =", e1,
                              "components =", [sorted(c) for c in comps])
                        return
                    # Claim (b): components are precisely {S, V \ S}.
                    if {comps[0], comps[1]} != {S, Sc}:
                        print("WITNESS_FOUND (claim (b) fails)")
                        print("  n  =", n, " V =", sorted(V))
                        print("  tree edges T =", list(edges))
                        print("  S            =", sorted(S))
                        print("  V \\ S        =", sorted(Sc))
                        print("  e1           =", e1,
                              "(one endpoint in S, one in V \\ S)")
                        print("  components of T - e1 =",
                              sorted([sorted(c) for c in comps]))
                        print("  These are NOT {S, V \\ S}: removing the")
                        print("  crossing edge e1 does not split T into S")
                        print("  and its complement, contradicting the claim.")
                        return
    print("NO_WITNESS_EXHAUSTIVE: swept all trees on n=2..5 labeled")
    print("vertices, all nonempty proper subsets S, all crossing tree")
    print("edges e1; claims (a) and (b) held everywhere.")


if __name__ == "__main__":
    main()
