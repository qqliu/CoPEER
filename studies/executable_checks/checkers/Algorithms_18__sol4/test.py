#!/usr/bin/env python3
"""
Blind counterexample search for record Algorithms_18__sol4.

TARGET CLAIM (quoted verbatim from the proof):

    "In all cases, we conclude that our assumption was wrong: the edge emax
    (the heaviest edge of cycle C) cannot be part of any minimum spanning tree."

Formalization of the literal claim being tested:

    For every connected undirected weighted graph G, every cycle C in G, and
    every edge emax of C whose weight is maximal among the edges of C
    ("the heaviest edge of cycle C"), emax belongs to NO minimum spanning
    tree of G.

Note the claim as quoted contains NO hypothesis that emax is *strictly*
heavier than the other edges of C (no distinct-weights assumption appears in
the quoted text). The correct "cycle property" requires strict maximality;
without it, the statement is refutable. This program searches exhaustively,
with exact integer arithmetic, for a concrete witness:

    (graph G with integer weights, cycle C, edge emax maximal in C,
     spanning tree T of G with minimum total weight, emax in T).

It ALSO separately checks the strict variant (emax strictly heavier than
every other edge of C) as a sanity control; no witness is expected there.

SEARCH SPACE (exhaustive, deterministic, fixed iteration order):
  - vertex counts n in {3, 4}
  - all edge subsets of the complete graph K_n that yield a connected graph
    containing at least one cycle
  - all weight assignments with each edge weight in {1, 2, 3}
  - all simple cycles C of the graph, all maximal-weight edges of each C
  - all spanning trees (all (n-1)-edge acyclic connected subsets), exact
    integer total weights, minimum taken exactly

Stdlib only. No floats. No randomness.
"""

import itertools
from typing import List, Tuple, Dict, FrozenSet

Edge = Tuple[int, int]  # (u, v) with u < v


def connected(vertices: List[int], edges: List[Edge]) -> bool:
    if not vertices:
        return True
    adj: Dict[int, List[int]] = {v: [] for v in vertices}
    for (u, v) in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen = {vertices[0]}
    stack = [vertices[0]]
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                stack.append(y)
    return len(seen) == len(vertices)


def is_forest(n_vertices: int, edges: List[Edge]) -> bool:
    # union-find, deterministic
    parent = list(range(n_vertices))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for (u, v) in edges:
        ru, rv = find(u), find(v)
        if ru == rv:
            return False
        parent[ru] = rv
    return True


def all_simple_cycles(vertices: List[int], edges: List[Edge]) -> List[List[Edge]]:
    """All simple cycles, each returned as a sorted list of its edges.

    Enumerated by taking every subset of vertices of size >= 3 and every
    cyclic ordering of that subset (fixed lexicographic order), keeping
    orderings whose consecutive pairs are all edges. Deduplicated by edge set.
    """
    edge_set = set(edges)
    found = {}
    for k in range(3, len(vertices) + 1):
        for subset in itertools.combinations(vertices, k):
            first = subset[0]
            rest = subset[1:]
            for perm in itertools.permutations(rest):
                order = (first,) + perm
                cyc_edges = []
                ok = True
                for i in range(k):
                    a, b = order[i], order[(i + 1) % k]
                    e = (min(a, b), max(a, b))
                    if e not in edge_set:
                        ok = False
                        break
                    cyc_edges.append(e)
                if ok:
                    key = frozenset(cyc_edges)
                    if key not in found:
                        found[key] = sorted(cyc_edges)
    return [found[k] for k in sorted(found.keys(), key=lambda s: sorted(s))]


def all_spanning_trees(vertices: List[int], edges: List[Edge]) -> List[Tuple[Edge, ...]]:
    n = len(vertices)
    trees = []
    for cand in itertools.combinations(edges, n - 1):
        if is_forest(n, list(cand)) and connected(vertices, list(cand)):
            trees.append(cand)
    return trees


def main() -> None:
    WEIGHTS = (1, 2, 3)
    witness = None            # literal claim (maximal, ties allowed)
    strict_witness = None     # strict variant (control; expected None)
    graphs_checked = 0

    for n in (3, 4):
        vertices = list(range(n))
        all_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        m = len(all_edges)
        for edge_mask in range(1, 1 << m):
            edges = [all_edges[i] for i in range(m) if (edge_mask >> i) & 1]
            if len(edges) < n:          # need a cycle: at least n edges
                continue
            if not connected(vertices, edges):
                continue
            cycles = all_simple_cycles(vertices, edges)
            if not cycles:
                continue
            for wvec in itertools.product(WEIGHTS, repeat=len(edges)):
                graphs_checked += 1
                w = dict(zip(edges, wvec))
                trees = all_spanning_trees(vertices, edges)
                tree_weights = [sum(w[e] for e in t) for t in trees]
                min_w = min(tree_weights)
                msts = [t for t, tw in zip(trees, tree_weights) if tw == min_w]
                mst_edges = set()
                for t in msts:
                    mst_edges.update(t)
                for C in cycles:
                    cmax = max(w[e] for e in C)
                    heavy = [e for e in C if w[e] == cmax]
                    for emax in heavy:
                        if emax in mst_edges:
                            if witness is None:
                                # find one MST containing emax, deterministically first
                                t_hit = next(t for t in msts if emax in t)
                                witness = (n, list(edges), dict(w), list(C), emax,
                                           cmax, t_hit, min_w, len(heavy))
                            if len(heavy) == 1 and strict_witness is None:
                                strict_witness = (n, list(edges), dict(w),
                                                  list(C), emax, cmax)
                if witness is not None and strict_witness is None:
                    # keep scanning the whole space for the strict control,
                    # but we already have the literal witness
                    pass
    print("Search space: n in {3,4}; all connected graphs with a cycle on n "
          "labeled vertices; all edge weights in {1,2,3}; all simple cycles; "
          "all spanning trees enumerated exactly.")
    print("Weighted graphs examined: %d" % graphs_checked)
    print()
    if witness is None:
        print("VERDICT: NO WITNESS FOUND in the swept space (literal claim).")
    else:
        n, edges, w, C, emax, cmax, t_hit, min_w, n_heavy = witness
        print("VERDICT: WITNESS FOUND — the literal claim is FALSE.")
        print("  Vertices: %s" % list(range(n)))
        print("  Edges with weights: %s" % {e: w[e] for e in edges})
        print("  Cycle C (edge list): %s" % C)
        print("  Edge emax = %s with weight %d, maximal in C "
              "(%d edge(s) of C attain the maximum)" % (emax, cmax, n_heavy))
        print("  A minimum spanning tree containing emax: %s (total weight %d)"
              % (list(t_hit), min_w))
        print("  Hence 'the heaviest edge of cycle C cannot be part of any "
              "minimum spanning tree' fails: emax is a heaviest edge of C and "
              "lies in an MST. The claim as quoted lacks the required "
              "strict-maximality (distinct weights) hypothesis.")
    print()
    if strict_witness is None:
        print("Control (strict variant): NO witness where emax is STRICTLY "
              "heavier than every other edge of its cycle — consistent with "
              "the correct cycle property.")
    else:
        n, edges, w, C, emax, cmax = strict_witness
        print("Control (strict variant): unexpected witness! %s" %
              ((n, edges, w, C, emax, cmax),))


if __name__ == "__main__":
    main()
