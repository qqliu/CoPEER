"""In every acyclic graph, after choosing one vertex v, there is a unique path from v to every other vertex, so a single breadth-first search colors the whole graph."""

import json
from itertools import combinations


def is_acyclic(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in edges:
        root_a = find(a)
        root_b = find(b)
        if root_a == root_b:
            return False
        parent[root_b] = root_a
    return True


def bfs_reaches_all(n, edges, root):
    adjacency = [[] for _ in range(n)]
    for a, b in edges:
        adjacency[a].append(b)
        adjacency[b].append(a)
    seen = {root}
    queue = [root]
    index = 0
    while index < len(queue):
        current = queue[index]
        index += 1
        for neighbor in adjacency[current]:
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return len(seen) == n


def search():
    first_witness = None
    checked_pairs = 0
    for n in range(1, 5):
        possible_edges = tuple(combinations(range(n), 2))
        for mask in range(1 << len(possible_edges)):
            edges = tuple(
                edge
                for bit, edge in enumerate(possible_edges)
                if mask & (1 << bit)
            )
            acyclic = is_acyclic(n, edges)
            for root in range(n):
                checked_pairs += 1
                if acyclic and not bfs_reaches_all(n, edges, root):
                    if first_witness is None:
                        first_witness = (n, edges, root)
    return checked_pairs, first_witness


checked_pairs, first_witness = search()
assert checked_pairs == 285
assert first_witness == (2, (), 0)

result = {
    "record_id": "reddit_learnmath_3e6sra",
    "outcome": "WITNESS_FOUND",
    "witness_description": "Take the labeled simple undirected graph with vertices {0, 1}, no edges, and choose v = 0.",
    "refutation_explanation": "This graph is acyclic, but there is no path from 0 to 1. Breadth-first search starting at 0 visits only vertex 0, so it does not color the whole graph.",
    "search_space": "All 285 graph-root pairs consisting of every labeled simple undirected graph on vertex set {0, ..., n-1} for n = 1, 2, 3, 4 and every choice of root v, enumerated in increasing n, edge-mask, and v order; every pair was checked, with counterexamples restricted to acyclic graphs."
}
print(json.dumps(result, separators=(",", ":")))
