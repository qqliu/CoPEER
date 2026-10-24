r"""() If G is not acyclic, then G has multiple transitive reductions."""

import json

VERTICES = (0, 1)
POSSIBLE_EDGES = ((0, 1), (1, 0))

REPORT = {
    "record_id": "Algorithms_17__sol3",
    "outcome": "WITNESS_FOUND",
    "witness_description": "The directed graph on vertices {0,1} with edges 0->1 and 1->0 is cyclic and has exactly one transitive reduction: itself.",
    "refutation_explanation": "Both edges are necessary to preserve mutual reachability, so no proper spanning subgraph has the same transitive closure. Thus this non-acyclic graph does not have multiple transitive reductions.",
    "search_space": "All 4 loopless directed graphs on the labeled vertex set {0,1}; for each graph, every spanning edge subset was checked in increasing bit-mask order for minimum-size preservation of transitive closure.",
}


def edges_selected(edge_universe, mask):
    return tuple(
        edge
        for index, edge in enumerate(edge_universe)
        if mask & (1 << index)
    )


def transitive_closure(edges):
    reachable = set(edges)
    for intermediate in VERTICES:
        for start in VERTICES:
            if (start, intermediate) not in reachable:
                continue
            for end in VERTICES:
                if (intermediate, end) in reachable:
                    reachable.add((start, end))
    return frozenset(reachable)


def is_acyclic(edges):
    reachable = transitive_closure(edges)
    return all((vertex, vertex) not in reachable for vertex in VERTICES)


def minimum_transitive_reductions(graph_edges):
    target_closure = transitive_closure(graph_edges)
    minimum_size = None
    reductions = []
    for subset_mask in range(1 << len(graph_edges)):
        subset = edges_selected(graph_edges, subset_mask)
        if transitive_closure(subset) != target_closure:
            continue
        subset_size = len(subset)
        if minimum_size is None or subset_size < minimum_size:
            minimum_size = subset_size
            reductions = [subset]
        elif subset_size == minimum_size:
            reductions.append(subset)
    return tuple(reductions)


violations = []
for graph_mask in range(1 << len(POSSIBLE_EDGES)):
    graph_edges = edges_selected(POSSIBLE_EDGES, graph_mask)
    reductions = minimum_transitive_reductions(graph_edges)
    if not is_acyclic(graph_edges) and len(reductions) < 2:
        violations.append((graph_edges, reductions))

if not violations:
    raise AssertionError("The bounded search found no counterexample")

first_graph, first_reductions = violations[0]
assert first_graph == POSSIBLE_EDGES
assert not is_acyclic(first_graph)
assert len(first_reductions) == 1
assert first_reductions[0] == first_graph
assert transitive_closure(first_reductions[0]) == transitive_closure(first_graph)

print(json.dumps(REPORT, separators=(",", ":")))
