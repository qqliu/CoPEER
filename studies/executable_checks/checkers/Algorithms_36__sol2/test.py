"""Consider the graph T2 union {e}. This graph contains n edges and n vertices. Since T2 is a tree, adding the edge e = {u, v} creates exactly one cycle"""

import json
from itertools import combinations, permutations


REPORT = {
    "record_id": "Algorithms_36__sol2",
    "outcome": "NO_WITNESS_EXHAUSTIVE",
    "witness_description": "No counterexample exists in the stated finite search space.",
    "refutation_explanation": "For every enumerated labeled tree and every missing edge, exhaustive enumeration of undirected simple cycles in the augmented graph found exactly one cycle. This is a bounded result and does not prove the unrestricted claim.",
    "search_space": "For each n in {1,2,3,4,5}, all simple undirected graphs on the labeled vertex set {0,...,n-1} having n-1 edges were enumerated and filtered to trees T2; for every such tree, every unordered pair e={u,v} of distinct vertices not already in T2 was tested. All undirected simple cycles in T2 union {e} were enumerated exactly.",
}


def is_tree(n, edges):
    if len(edges) != n - 1:
        return False
    adjacency = [set() for _ in range(n)]
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    seen = {0}
    stack = [0]
    while stack:
        vertex = stack.pop()
        for neighbor in sorted(adjacency[vertex]):
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return len(seen) == n


def canonical_edge(a, b):
    if a < b:
        return (a, b)
    return (b, a)


def count_simple_cycles(n, edges):
    edge_set = set(edges)
    count = 0
    vertices = tuple(range(n))
    for length in range(3, n + 1):
        for chosen in combinations(vertices, length):
            start = chosen[0]
            for ordering in permutations(chosen[1:]):
                route = (start,) + ordering
                if route[1] >= route[-1]:
                    continue
                cycle_present = True
                for index in range(length):
                    edge = canonical_edge(route[index], route[(index + 1) % length])
                    if edge not in edge_set:
                        cycle_present = False
                        break
                if cycle_present:
                    count += 1
    return count


first_violation = None
examined_cases = 0

for n in (1, 2, 3, 4, 5):
    possible_edges = tuple(combinations(range(n), 2))
    for tree_edges in combinations(possible_edges, n - 1):
        if not is_tree(n, tree_edges):
            continue
        tree_edge_set = set(tree_edges)
        for extra_edge in possible_edges:
            if extra_edge in tree_edge_set:
                continue
            examined_cases += 1
            augmented_edges = tree_edges + (extra_edge,)
            assert len(augmented_edges) == n
            cycle_count = count_simple_cycles(n, augmented_edges)
            if cycle_count != 1 and first_violation is None:
                first_violation = (n, tree_edges, extra_edge, cycle_count)

assert examined_cases > 0
computed_outcome = (
    "NO_WITNESS_EXHAUSTIVE"
    if first_violation is None
    else "WITNESS_FOUND"
)
assert computed_outcome == REPORT["outcome"]

print(json.dumps(REPORT, separators=(",", ":"), ensure_ascii=True))
