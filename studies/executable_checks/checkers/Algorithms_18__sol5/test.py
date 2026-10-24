#!/usr/bin/env python3
"""
Counterexample search for the claim (Algorithms_18__sol5):

    "we conclude that no maximum-weight edge of any cycle in G can belong
     to the MST."

Interpretation
--------------
G is a connected, undirected, weighted graph.  The claim asserts: for every
cycle C in G and every edge e of C whose weight equals the maximum edge
weight on C, e does not belong to the MST.  (This is the "cycle property"
stated WITHOUT the uniqueness hypothesis on the maximum-weight edge.)

Because a graph with weight ties may have several minimum spanning trees,
we test the claim in its STRONGEST-for-the-claim / weakest-for-us form:
we look for a graph in which EVERY minimum spanning tree contains an edge
that is a maximum-weight edge of some cycle.  Such a graph refutes the
claim under any reading of "the MST" (whichever MST one takes, it contains
a forbidden edge).  We also record the weaker "some MST violates" form.

Search space (exhaustive, deterministic, exact integer arithmetic)
------------------------------------------------------------------
All simple undirected graphs on n in {3, 4} labeled vertices, over every
subset of the possible edges that yields a connected graph with at least
one cycle, with every assignment of integer weights from {1, 2} to the
chosen edges.  For each graph:
  * all spanning trees are enumerated by brute force over edge subsets,
  * the exact minimum total weight and the full set of MSTs are computed,
  * all simple cycles are enumerated by brute force over edge subsets
    (a cycle = connected edge subset in which every vertex has degree 2),
  * an edge e is a "cycle-max edge" iff there is a simple cycle C with
    e in C and weight(e) == max(weight(f) for f in C).
Verdict: witness found iff every MST of some graph contains a cycle-max
edge.  Iteration order is fixed (sorted/lexicographic); no randomness,
no floats.
"""

import itertools
from collections import deque


def connected(vertices, edges):
    """Exact connectivity check on the given vertex set via the edge list."""
    vertices = list(vertices)
    if not vertices:
        return True
    adj = {v: [] for v in vertices}
    for (u, v) in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen = {vertices[0]}
    q = deque([vertices[0]])
    while q:
        x = q.popleft()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                q.append(y)
    return len(seen) == len(vertices)


def spanning_trees(n, edges):
    """All spanning trees (as frozensets of edges) of graph on vertices 0..n-1."""
    trees = []
    for subset in itertools.combinations(edges, n - 1):
        verts_covered = set()
        for (u, v) in subset:
            verts_covered.add(u)
            verts_covered.add(v)
        if len(verts_covered) != n:
            continue
        if connected(range(n), subset):
            trees.append(frozenset(subset))
    return trees


def simple_cycles(edges):
    """All simple cycles as frozensets of edges: connected, all degrees == 2."""
    cycles = []
    for r in range(3, len(edges) + 1):
        for subset in itertools.combinations(edges, r):
            deg = {}
            for (u, v) in subset:
                deg[u] = deg.get(u, 0) + 1
                deg[v] = deg.get(v, 0) + 1
            if any(d != 2 for d in deg.values()):
                continue
            if connected(deg.keys(), subset):
                cycles.append(frozenset(subset))
    return cycles


def search():
    for n in (3, 4):
        all_edges = list(itertools.combinations(range(n), 2))
        # every edge subset of size >= n (guarantees a cycle if connected)
        for k in range(n, len(all_edges) + 1):
            for edge_set in itertools.combinations(all_edges, k):
                if not connected(range(n), edge_set):
                    continue
                cycles = simple_cycles(edge_set)
                if not cycles:
                    continue
                for weights in itertools.product((1, 2), repeat=k):
                    w = dict(zip(edge_set, weights))
                    # cycle-max edges: e s.t. exists cycle C, e in C,
                    # w[e] == max weight on C
                    cycle_max = set()
                    for C in cycles:
                        m = max(w[e] for e in C)
                        for e in C:
                            if w[e] == m:
                                cycle_max.add(e)
                    if not cycle_max:
                        continue
                    trees = spanning_trees(n, edge_set)
                    min_w = min(sum(w[e] for e in T) for T in trees)
                    msts = [T for T in trees
                            if sum(w[e] for e in T) == min_w]
                    # strong violation: EVERY MST contains a cycle-max edge
                    if all(any(e in cycle_max for e in T) for T in msts):
                        return n, edge_set, w, cycles, msts, cycle_max, min_w
    return None


def main():
    result = search()
    if result is None:
        print("NO_WITNESS_EXHAUSTIVE: no counterexample among all connected "
              "graphs on 3-4 vertices with weights in {1,2}.")
        return
    n, edge_set, w, cycles, msts, cycle_max, min_w = result
    print("WITNESS_FOUND")
    print(f"  vertices : 0..{n - 1}")
    print(f"  edges    : " + ", ".join(f"{e}:w={w[e]}" for e in edge_set))
    print(f"  simple cycles: {[sorted(C) for C in cycles]}")
    print(f"  MST weight = {min_w}; all MSTs: {[sorted(T) for T in msts]}")
    print(f"  cycle-max edges (max-weight edge of some cycle): "
          f"{sorted(cycle_max)}")
    for T in msts:
        bad = sorted(e for e in T if e in cycle_max)
        print(f"  MST {sorted(T)} contains cycle-max edge(s) {bad}")
    print()
    print("  VERDICT: the claim 'no maximum-weight edge of any cycle in G")
    print("  can belong to the MST' is FALSE: in this graph EVERY minimum")
    print("  spanning tree contains an edge of maximum weight on a cycle.")
    print("  (The cycle property requires the maximum to be UNIQUE on the")
    print("  cycle; with weight ties the claim fails.)")


if __name__ == "__main__":
    main()
