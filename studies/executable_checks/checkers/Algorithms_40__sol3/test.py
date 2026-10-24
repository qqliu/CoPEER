"""Let M1 = {v1v2, v3v4} and M2 = {v2v3}. Both are maximal matchings with |M1| = 2 = 2|M2|."""

import itertools
import json

VERTICES = ("v1", "v2", "v3", "v4")
M1 = (("v1", "v2"), ("v3", "v4"))
M2 = (("v2", "v3"),)
REQUIRED = frozenset(M1 + M2)
ALL_EDGES = tuple(itertools.combinations(VERTICES, 2))
OPTIONAL = tuple(edge for edge in ALL_EDGES if edge not in REQUIRED)


def is_matching(graph, matching):
    used = set()
    for edge in matching:
        if edge not in graph:
            return False
        a, b = edge
        if a in used or b in used:
            return False
        used.add(a)
        used.add(b)
    return True


def is_maximal_matching(graph, matching):
    if not is_matching(graph, matching):
        return False
    used = {vertex for edge in matching for vertex in edge}
    return not any(a not in used and b not in used for a, b in graph)


m2_maximal_count = 0
m2_nonmaximal_count = 0
for mask in range(1 << len(OPTIONAL)):
    graph = set(REQUIRED)
    for index, edge in enumerate(OPTIONAL):
        if mask & (1 << index):
            graph.add(edge)
    graph = frozenset(graph)
    assert is_maximal_matching(graph, M1)
    assert len(M1) == 2 * len(M2)
    if is_maximal_matching(graph, M2):
        m2_maximal_count += 1
    else:
        m2_nonmaximal_count += 1

assert len(OPTIONAL) == 3
assert m2_maximal_count == 4
assert m2_nonmaximal_count == 4
assert is_maximal_matching(REQUIRED, M2)
assert not is_maximal_matching(REQUIRED | frozenset({("v1", "v4")}), M2)

result = {
    "record_id": "Algorithms_40__sol3",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No claim-level witness can be certified from the quote alone. Among the bounded completions, the graph containing only v1v2, v2v3, and v3v4 makes M2 maximal, while adding v1v4 makes M2 non-maximal.",
    "refutation_explanation": "The ambient graph and its vertex set are not specified. Maximality depends on that missing data: if v1v4 is an edge, it can be added disjointly to M2, but if it is absent in the four-vertex path completion, M2 is maximal. The cardinality equation itself holds.",
    "search_space": "All 8 simple undirected graphs on exactly {v1,v2,v3,v4} containing v1v2, v2v3, and v3v4, with the other 3 possible edges independently absent or present, enumerated by masks 0 through 7. Exactly 4 make M2 maximal and 4 do not; this bounded completion sweep is illustrative because the quote does not specify the ambient graph or vertex set."
}
print(json.dumps(result, separators=(",", ":")))
