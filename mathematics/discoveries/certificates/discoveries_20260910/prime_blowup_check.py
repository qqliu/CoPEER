#!/usr/bin/env python3
"""Exact finite checks for the prime C9 / C9[K2] counterexample.

Run with Python 3 (standard library only). No network or repository writes.
The all-k recolorability assertion uses the induction proved in the entry;
this program checks all 512 induced graphs at k = chi + 1, not infinitely
many k. This is an executable certificate, not a proof-assistant certificate.
"""

from collections import Counter, deque
import json


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def adjacency(n, edges):
    result = [set() for _ in range(n)]
    for u, v in edges:
        check(0 <= u < v < n, "invalid simple graph edge")
        result[u].add(v)
        result[v].add(u)
    return result


def colorings(adj, k):
    colors = [-1] * len(adj)

    def visit(v):
        if v == len(adj):
            yield tuple(colors)
            return
        forbidden = {colors[w] for w in adj[v] if w < v}
        for color in range(k):
            if color not in forbidden:
                colors[v] = color
                yield from visit(v + 1)
        colors[v] = -1

    return visit(0)


def exact_chi(adj):
    for k in range(len(adj) + 1):
        if next(colorings(adj, k), None) is not None:
            return k
    raise AssertionError("chromatic number absent")


def exact_degeneracy(adj):
    remaining = set(range(len(adj)))
    answer = 0
    while remaining:
        v = min(remaining, key=lambda w: len(adj[w] & remaining))
        answer = max(answer, len(adj[v] & remaining))
        remaining.remove(v)
    return answer


def boundary_connected(adj, k):
    unseen = set(colorings(adj, k))
    total = len(unseen)
    check(total > 0, "no boundary colorings")
    queue = deque([unseen.pop()])
    while queue:
        colors = queue.popleft()
        for v in range(len(adj)):
            for color in range(k):
                changed = colors[:v] + (color,) + colors[v + 1:]
                if changed in unseen:
                    unseen.remove(changed)
                    queue.append(changed)
    check(not unseen, "disconnected induced-graph boundary")
    return total


def exact_alpha(adj):
    # Dynamic enumeration visits every subset. Removing its lowest vertex
    # leaves an independent set iff the residual set has no neighbor of it.
    independent = bytearray(1 << len(adj))
    independent[0] = 1
    masks = [sum(1 << w for w in neighbors) for neighbors in adj]
    answer = 0
    for subset in range(1, 1 << len(adj)):
        bit = subset & -subset
        v = bit.bit_length() - 1
        rest = subset ^ bit
        independent[subset] = independent[rest] and not (rest & masks[v])
        if independent[subset]:
            answer = max(answer, bin(subset).count("1"))
    return answer


def main():
    cycle_edges = {tuple(sorted((v, (v + 1) % 9))) for v in range(9)}
    cycle = adjacency(9, cycle_edges)
    candidate_count = 0
    for mask in range(1 << 9):
        module = {v for v in range(9) if mask & (1 << v)}
        if 2 <= len(module) < 9:
            candidate_count += 1
            check(any(cycle[v] & module not in (set(), module)
                      for v in set(range(9)) - module), "nontrivial module")
    check(candidate_count == 501, "module coverage")
    classes = Counter()
    boundary_counts = []
    for mask in range(1 << 9):
        vertices = [v for v in range(9) if mask & (1 << v)]
        adj = [{j for j, w in enumerate(vertices) if w in cycle[v]}
               for v in vertices]
        chi, d = exact_chi(adj), exact_degeneracy(adj)
        if len(vertices) == 9:
            kind, expected = "whole_cycle", (3, 2)
        elif not vertices:
            kind, expected = "empty", (0, 0)
        elif not any(adj):
            kind, expected = "nonempty_edgeless", (1, 0)
        else:
            kind, expected = "proper_with_edge", (2, 1)
        check((chi, d) == expected, "induced chromatic/degeneracy classification")
        classes[kind] += 1
        boundary_counts.append(boundary_connected(adj, chi + 1))
    check(dict(classes) == {"empty": 1, "nonempty_edgeless": 75,
                            "proper_with_edge": 435, "whole_cycle": 1},
          "induced coverage")
    check(exact_alpha(cycle) == 4, "cycle independence number")

    edges = {(u, v) for u in range(18) for v in range(u + 1, 18)
             if u // 2 == v // 2 or (u // 2 - v // 2) % 9 in (1, 8)}
    blowup = adjacency(18, edges)
    check(len(edges) == 45 and all(len(a) == 5 for a in blowup), "blowup model")
    alpha = exact_alpha(blowup)
    check(alpha == 4 and 4 * alpha < 18, "chromatic lower bound")
    five = (1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4, 1, 5, 2, 3, 4, 5)
    six = (1, 2, 3, 4, 5, 6) * 3
    for colors, k in ((five, 5), (six, 6)):
        check(len(colors) == 18 and set(colors) <= set(range(1, k + 1)),
              "coloring domain")
        check(all(colors[u] != colors[v] for u, v in edges), "improper coloring")
    for v in range(18):
        check({six[w] for w in blowup[v]} == set(range(1, 7)) - {six[v]},
              "unfrozen vertex")
    check(five != six, "second R6 vertex absent")
    print(json.dumps({
        "status": "PASS", "module_candidates": candidate_count,
        "induced_subgraphs": 512, "induced_classification": dict(classes),
        "all_induced_boundary_reconfiguration_graphs_connected": True,
        "boundary_coloring_count_range": [min(boundary_counts), max(boundary_counts)],
        "blowup_vertices": 18, "blowup_edges": len(edges),
        "independence_subsets_checked": 1 << 18, "alpha": alpha, "chi": 5,
        "frozen_vertices_in_proper_6_coloring": 18,
        "distinct_proper_6_coloring_exists": True,
        "all_k_argument": "hand-proved degeneracy recoloring lemma in entry",
        "formalized": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
