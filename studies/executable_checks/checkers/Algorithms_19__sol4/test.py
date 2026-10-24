#!/usr/bin/env python3
"""
Blind counterexample search for record Algorithms_19__sol4.

TARGET CLAIM (quoted verbatim from the source proof):

    "spanning tree T ' by removing e1 from T and adding the other edge e2."

This is a sentence FRAGMENT.  It asserts (implicitly) that some object T'
obtained from a spanning tree T by removing an edge e1 and adding an edge e2
is again a spanning tree.  The fragment does NOT define:
  * the graph G,
  * how e1 is chosen,
  * what "the other edge e2" refers to (other than WHAT? -- the antecedent
    is missing from the quoted text).

Because the relation between e1 and e2 is not supplied by the claim text,
the claim admits (at least) two finitely checkable readings.  This program
exhaustively sweeps small graphs under BOTH readings, using exact integer
arithmetic only:

  Reading A (unconstrained / strawman):
      For every connected graph G, every spanning tree T of G, every
      e1 in T and every e2 in E(G) minus T, T' = T - e1 + e2 is a spanning tree.
      (If the fragment meant an arbitrary pair, this is the claim.)

  Reading B (standard tree-exchange, the usual context of such sentences):
      For every connected graph G, every spanning tree T, every non-tree
      edge e2, and every tree edge e1 lying on the unique cycle of T + e2
      ("the other edge" of that cycle),  T' = T - e1 + e2 is a spanning tree.

Search space: ALL labeled simple graphs on n = 3, 4, 5 vertices (every
subset of the C(n,2) possible edges), restricted to connected graphs;
for each, ALL spanning trees (enumerated as all (n-1)-subsets of edges
that are acyclic and spanning); for each, ALL admissible pairs (e1, e2)
under each reading.  Everything is enumerated in a fixed deterministic
order (lexicographic over frozen edge lists).  No floats, no randomness.

Verdict logic:
  * If Reading B (the standard interpretation) yields a violation, that is
    a genuine WITNESS against every reasonable reading -> WITNESS_FOUND.
  * If only Reading A fails, that refutes merely the strawman reading the
    fragment does not clearly assert -> the run is INCONCLUSIVE for the
    claim as written (the text under-determines the e1/e2 relationship).
"""

from itertools import combinations


class DSU:
    """Deterministic union-find over vertices 0..n-1 (exact int arithmetic)."""

    def __init__(self, n):
        self.p = list(range(n))

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if ra > rb:
            ra, rb = rb, ra
        self.p[rb] = ra
        return True


def is_spanning_tree(n, edges):
    """edges: iterable of (u,v). True iff exactly n-1 edges, acyclic, spanning."""
    es = list(edges)
    if len(es) != n - 1:
        return False
    d = DSU(n)
    for (u, v) in es:
        if not d.union(u, v):
            return False  # cycle
    root = d.find(0)
    return all(d.find(v) == root for v in range(n))


def is_connected(n, edges):
    d = DSU(n)
    for (u, v) in edges:
        d.union(u, v)
    root = d.find(0)
    return all(d.find(v) == root for v in range(n))


def cycle_edges_of(n, tree_edges, e2):
    """Unique cycle of T + e2: the tree path between endpoints of e2, as edges."""
    adj = {v: [] for v in range(n)}
    for (u, v) in tree_edges:
        adj[u].append(v)
        adj[v].append(u)
    a, b = e2
    # deterministic DFS from a to b along the tree
    parent = {a: None}
    stack = [a]
    while stack:
        x = stack.pop()
        for y in sorted(adj[x]):
            if y not in parent:
                parent[y] = x
                stack.append(y)
    path = []
    x = b
    while parent[x] is not None:
        px = parent[x]
        path.append((min(px, x), max(px, x)))
        x = px
    return path  # edges of the tree path a..b (the cycle minus e2)


def main():
    strawman_witness = None      # Reading A violation (first found)
    standard_witness = None      # Reading B violation (first found)
    graphs_checked = 0
    trees_checked = 0
    pairs_A = 0
    pairs_B = 0

    for n in (3, 4, 5):
        all_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        m = len(all_edges)
        for k in range(n - 1, m + 1):          # need >= n-1 edges to connect
            for E in combinations(all_edges, k):
                if not is_connected(n, E):
                    continue
                graphs_checked += 1
                Eset = set(E)
                for T in combinations(E, n - 1):
                    if not is_spanning_tree(n, T):
                        continue
                    trees_checked += 1
                    Tset = set(T)
                    nontree = [e for e in E if e not in Tset]
                    for e2 in nontree:
                        cyc = cycle_edges_of(n, T, e2)
                        cycset = set(cyc)
                        for e1 in T:
                            # Reading A: any tree edge e1, any non-tree e2
                            pairs_A += 1
                            Tp = [e for e in T if e != e1] + [e2]
                            ok = is_spanning_tree(n, Tp)
                            if not ok and strawman_witness is None:
                                strawman_witness = (n, E, T, e1, e2, tuple(sorted(Tp)))
                            # Reading B: e1 must lie on the cycle of T + e2
                            if e1 in cycset:
                                pairs_B += 1
                                if not ok and standard_witness is None:
                                    standard_witness = (n, E, T, e1, e2, tuple(sorted(Tp)))

    print("Search space swept (deterministic, exhaustive):")
    print("  all connected labeled simple graphs on n in {3,4,5} vertices:",
          graphs_checked, "graphs")
    print("  all spanning trees of each:", trees_checked, "trees")
    print("  Reading A pairs (any e1 in T, any e2 not in T):", pairs_A)
    print("  Reading B pairs (e1 on the unique cycle of T+e2):", pairs_B)
    print()

    if standard_witness is not None:
        n, E, T, e1, e2, Tp = standard_witness
        print("VERDICT: WITNESS_FOUND (violates even the standard exchange reading)")
        print("  n =", n, " G edges =", E)
        print("  T =", T, " e1 =", e1, " e2 =", e2, " T' =", Tp)
        return

    print("Reading B (standard tree-exchange, e1 on cycle of T+e2):")
    print("  NO violation found anywhere in the swept space -- consistent with")
    print("  the classical exchange lemma, which is a theorem.")
    print()
    if strawman_witness is not None:
        n, E, T, e1, e2, Tp = strawman_witness
        print("Reading A (unconstrained e1,e2) fails, e.g. first violation found:")
        print("  n =", n, " G edges =", list(E))
        print("  T  =", list(T))
        print("  e1 =", e1, " e2 =", e2)
        print("  T' = T - e1 + e2 =", list(Tp), " -- NOT a spanning tree")
        print("  (removing e1 disconnects T and e2 does not reconnect the parts)")
        print()
    print("VERDICT: NO_WITNESS_INCONCLUSIVE")
    print("  The quoted claim is a sentence fragment: it never defines how e1")
    print("  and e2 are related ('the other edge' has no antecedent in the")
    print("  quoted text).  Under the standard exchange reading the swept")
    print("  space contains no counterexample; the unconstrained reading is")
    print("  refutable but is not clearly what the text asserts.  The claim")
    print("  text does not supply enough to decide which reading is meant,")
    print("  so no genuine counterexample to the claim can be certified.")


if __name__ == "__main__":
    main()
