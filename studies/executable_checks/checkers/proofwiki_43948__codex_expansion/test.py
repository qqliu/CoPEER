"""If an edge belongs to every minimum spanning tree of the graph, then it is a minimum-weight bridge of the graph."""

import json
from itertools import combinations, product

RECORD_ID = "proofwiki_43948__codex_expansion"
OUTCOME = "WITNESS_FOUND"
WITNESS = "On vertices {0,1,2}, take the triangle with weights w(0,1)=1, w(0,2)=1, and w(1,2)=2. Its unique minimum spanning tree is {{0,1},{0,2}}, so edge {0,1} belongs to every minimum spanning tree. Removing {0,1} leaves the path 0-2-1 connected, so {0,1} is not a bridge."
EXPLANATION = "The conclusion requires the edge to be a bridge (in particular, before it can be a minimum-weight bridge). The exhibited edge belongs to every minimum spanning tree but is not a bridge, so it violates the implication."
SEARCH_SPACE = "All 68 encodings of labeled simple undirected graphs on n in {2,3}, where every possible edge is independently absent or has integer weight in {1,2,3}; every encoding was visited in fixed lexicographic product order, and minimum spanning trees were exhaustively enumerated for each connected encoding."


def is_connected(n, edges, excluded=None):
    adjacency = {vertex: [] for vertex in range(n)}
    for u, v, weight in edges:
        if excluded == (u, v):
            continue
        adjacency[u].append(v)
        adjacency[v].append(u)
    seen = {0}
    stack = [0]
    while stack:
        vertex = stack.pop()
        for neighbor in adjacency[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return len(seen) == n


def minimum_spanning_trees(n, edges):
    weights = {(u, v): weight for u, v, weight in edges}
    edge_keys = tuple(weights)
    trees = []
    for chosen in combinations(edge_keys, n - 1):
        chosen_edges = tuple((u, v, weights[(u, v)]) for u, v in chosen)
        if is_connected(n, chosen_edges):
            total = sum(weights[edge] for edge in chosen)
            trees.append((total, chosen))
    minimum = min(total for total, chosen in trees)
    return tuple(chosen for total, chosen in trees if total == minimum)


def search():
    first_witness = None
    encodings_visited = 0
    for n in (2, 3):
        possible_edges = tuple(combinations(range(n), 2))
        for states in product(range(4), repeat=len(possible_edges)):
            encodings_visited += 1
            edges = tuple(
                (u, v, state)
                for (u, v), state in zip(possible_edges, states)
                if state != 0
            )
            if not is_connected(n, edges):
                continue
            minimum_trees = minimum_spanning_trees(n, edges)
            for u, v, weight in edges:
                edge = (u, v)
                belongs_to_every_mst = all(
                    edge in tree for tree in minimum_trees
                )
                is_not_a_bridge = is_connected(n, edges, excluded=edge)
                if belongs_to_every_mst and is_not_a_bridge:
                    if first_witness is None:
                        first_witness = (n, edges, edge, minimum_trees)
    return encodings_visited, first_witness


visited, found = search()
expected = (
    3,
    ((0, 1, 1), (0, 2, 1), (1, 2, 2)),
    (0, 1),
    (((0, 1), (0, 2)),),
)
if visited != 68 or found != expected:
    raise RuntimeError("exhaustive search did not produce the expected witness")

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS,
    "refutation_explanation": EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
