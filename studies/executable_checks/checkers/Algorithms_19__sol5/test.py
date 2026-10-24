#!/usr/bin/env python3
"""
BLIND counterexample search for record Algorithms_19__sol5.

TARGET CLAIM (quoted verbatim from the proof under test):

    **Cut Property**: For any partition of the vertex set V into two subsets
    S and V \\ S, the edge of minimum weight crossing the partition belongs
    to every MST.

Interpretation tested
---------------------
The claim, as written, carries NO hypothesis of distinct edge weights and no
tie-breaking caveat.  We read "the edge of minimum weight crossing the
partition" in the only way that makes the universally quantified statement
checkable: an edge e crossing the cut whose weight equals the minimum weight
among all crossing edges.  The claim then asserts:

    For every connected weighted graph G = (V, E, w),
    for every partition (S, V\\S) with S nonempty and proper,
    every crossing edge of minimum crossing weight belongs to EVERY
    minimum spanning tree of G.

(The textbook-correct cut property either assumes the minimum crossing edge
is UNIQUE, or concludes membership in SOME MST.  The quoted claim assumes
neither, so weight ties are fair game.)

Search space (exhaustive, deterministic, exact integer arithmetic)
------------------------------------------------------------------
- Vertex counts n in {2, 3, 4} (vertices 0..n-1).
- Edge sets: every subset of the n*(n-1)/2 possible undirected edges such
  that the graph is connected (spanning, simple, no self-loops).
- Weights: every assignment of integer weights from {1, 2} to the chosen
  edges.
- Partitions: every nonempty proper subset S of V containing vertex 0
  (S vs V\\S is unordered, so fixing 0 in S loses nothing).
- MSTs: ALL minimum spanning trees, found by brute force over all spanning
  subsets of E of size n-1, keeping exactly those that are spanning trees of
  minimum total weight.  Pure int comparisons; no floats anywhere.

Verdict: prints WITNESS_FOUND with the first witness in the fixed iteration
order, or NO_WITNESS_EXHAUSTIVE if the whole space is swept clean.
"""

from itertools import combinations, product


def connected(n, edges):
    """Exact connectivity check on vertices 0..n-1 via DFS over edge list."""
    adj = {v: [] for v in range(n)}
    for (u, v) in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen = {0}
    stack = [0]
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                stack.append(y)
    return len(seen) == n


def all_msts(n, edges, w):
    """Return (min_weight, list of all MSTs) by brute force over
    all (n-1)-subsets of edges. Deterministic order."""
    best = None
    trees = []
    for sub in combinations(edges, n - 1):
        if not connected(n, sub):
            continue  # n-1 edges + connected == spanning tree
        total = sum(w[e] for e in sub)
        if best is None or total < best:
            best = total
            trees = [sub]
        elif total == best:
            trees.append(sub)
    return best, trees


def main():
    checked_graphs = 0
    for n in (2, 3, 4):
        verts = list(range(n))
        all_edges = list(combinations(verts, 2))
        # every connected edge set
        for r in range(n - 1, len(all_edges) + 1):
            for eset in combinations(all_edges, r):
                if not connected(n, eset):
                    continue
                # every weight assignment from {1,2}
                for wtuple in product((1, 2), repeat=r):
                    w = dict(zip(eset, wtuple))
                    checked_graphs += 1
                    mst_weight, msts = all_msts(n, eset, w)
                    # every partition S (fix vertex 0 in S), S proper nonempty
                    others = verts[1:]
                    for k in range(0, n - 1):
                        for extra in combinations(others, k):
                            S = frozenset((0,) + extra)
                            crossing = [e for e in eset
                                        if (e[0] in S) != (e[1] in S)]
                            if not crossing:
                                continue  # cannot happen (graph connected)
                            mcross = min(w[e] for e in crossing)
                            for e in crossing:
                                if w[e] != mcross:
                                    continue
                                # claim: e belongs to EVERY MST
                                for T in msts:
                                    if e not in T:
                                        report_witness(
                                            n, eset, w, S, e, mcross,
                                            mst_weight, msts, T)
                                        return
    print("NO_WITNESS_EXHAUSTIVE")
    print(f"Swept {checked_graphs} weighted connected graphs "
          f"(n in {{2,3,4}}, weights in {{1,2}}), all partitions, "
          f"all minimum crossing edges, all MSTs. No counterexample.")


def report_witness(n, eset, w, S, e, mcross, mst_weight, msts, T):
    print("WITNESS_FOUND")
    print(f"Graph: n = {n}, vertices = {list(range(n))}")
    print(f"Edges with weights: "
          + ", ".join(f"{u}-{v}:w={w[(u, v)]}" for (u, v) in eset))
    print(f"Partition: S = {sorted(S)}, V \\ S = "
          f"{sorted(set(range(n)) - S)}")
    print(f"Minimum crossing weight = {mcross}")
    print(f"Minimum-weight crossing edge e = {e} (weight {w[e]})")
    print(f"MST total weight = {mst_weight}; ALL MSTs:")
    for i, t in enumerate(msts):
        mark = "  <-- omits e" if e not in t else ""
        print(f"  MST #{i}: {list(t)}{mark}")
    print(f"Violation: edge {e} has minimum weight {w[e]} among edges "
          f"crossing the partition (S={sorted(S)}), yet the minimum "
          f"spanning tree {list(T)} (an MST, total weight {mst_weight}) "
          f"does not contain {e}.  Hence the minimum-weight crossing edge "
          f"does NOT belong to every MST, contradicting the claim.")


if __name__ == "__main__":
    main()
