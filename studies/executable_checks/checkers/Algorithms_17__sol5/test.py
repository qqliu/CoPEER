#!/usr/bin/env python3
"""
Blind counterexample search for record Algorithms_17__sol5.

TARGET CLAIM (quoted verbatim from the proof):
    "However, any subset of k-1 edges from C forms a spanning tree of C
     and suffices to maintain the reachability."

INTERPRETATION (the only one the quote supports without inventing data):
  - "C" with the parameter k, whose edge subsets of size k-1 are claimed to be
    spanning trees, is read in its standard graph-theoretic sense: C is the
    (undirected, simple) cycle graph C_k on vertex set {0,...,k-1} with the
    k edges {i, (i+1) mod k}.  A cycle is the canonical object named "C" for
    which "k-1 edges" and "spanning tree" fit dimensionally (a spanning tree
    of a k-vertex graph has exactly k-1 edges, and C_k has exactly k edges).
  - "forms a spanning tree of C" := the chosen edge subset, together with all
    k vertices of C, is connected and acyclic and touches every vertex.
  - "suffices to maintain the reachability" := every ordered pair of vertices
    of C is connected by a path inside the chosen edge subset (undirected
    reachability), i.e. the subgraph is connected on all k vertices.

SEARCH SPACE (exhaustive, deterministic, exact integer arithmetic only):
  For every k in 3..16 (simple cycles require k >= 3), enumerate EVERY subset
  S of size k-1 of the k edges of C_k via itertools.combinations in a fixed
  lexicographic order (there are exactly k such subsets per k).  For each S,
  check with exact integer union-find / BFS:
      (a) S spans all k vertices,
      (b) the subgraph (V(C_k), S) is connected,
      (c) S is acyclic (|S| = k-1 and connected => tree; acyclicity is also
          checked independently via union-find),
      (d) all ordered pairs (u,v) are mutually reachable in (V(C_k), S).
  A witness is any (k, S) violating (a), (b), (c) or (d).

No floats are used anywhere; all decisions are made on Python ints.
"""

import itertools
import sys


def cycle_edges(k):
    """Edges of the undirected cycle C_k on vertices 0..k-1, fixed order."""
    return [(i, (i + 1) % k) for i in range(k)]


class DSU:
    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        """Return False if a,b already in same component (edge closes a cycle)."""
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        self.parent[rb] = ra
        return True


def is_spanning_tree_and_reachable(k, subset):
    """Return (ok, reason). ok=True iff subset is a spanning tree of C_k and
    every ordered vertex pair is reachable within subset. Exact int arithmetic."""
    touched = set()
    for (u, v) in subset:
        touched.add(u)
        touched.add(v)
    if touched != set(range(k)):
        return False, "does not span all %d vertices (misses %s)" % (
            k, sorted(set(range(k)) - touched))

    dsu = DSU(k)
    for (u, v) in subset:
        if not dsu.union(u, v):
            return False, "contains a cycle (edge (%d,%d) closes it)" % (u, v)

    root = dsu.find(0)
    for v in range(1, k):
        if dsu.find(v) != root:
            return False, "not connected (vertex %d unreachable from 0)" % v

    # Independent all-pairs reachability check via BFS from every vertex.
    adj = {i: [] for i in range(k)}
    for (u, v) in subset:
        adj[u].append(v)
        adj[v].append(u)
    for s in range(k):
        seen = {s}
        frontier = [s]
        while frontier:
            nxt = []
            for x in frontier:
                for y in adj[x]:
                    if y not in seen:
                        seen.add(y)
                        nxt.append(y)
            frontier = nxt
        if len(seen) != k:
            return False, "reachability fails from vertex %d" % s

    return True, "spanning tree; all ordered pairs reachable"


def main():
    K_MIN, K_MAX = 3, 16
    total_checked = 0
    for k in range(K_MIN, K_MAX + 1):
        edges = cycle_edges(k)
        for subset in itertools.combinations(edges, k - 1):
            total_checked += 1
            ok, reason = is_spanning_tree_and_reachable(k, subset)
            if not ok:
                print("WITNESS_FOUND")
                print("k =", k)
                print("edge subset =", list(subset))
                print("violation:", reason)
                return 1
    print("NO_WITNESS_EXHAUSTIVE")
    print("Swept: for every k in %d..%d, ALL C(k, k-1) = k subsets of size k-1"
          % (K_MIN, K_MAX))
    print("of the k edges of the undirected cycle C_k; %d subsets checked in"
          % total_checked)
    print("total.  Every subset was verified (exact integer union-find + BFS)")
    print("to be a spanning tree of C_k with all ordered vertex pairs mutually")
    print("reachable.  No counterexample to the claim exists in this space.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
