"""Moreover, f cannot belong to T1 (otherwise T1 would contain an edge directly connecting VA and VB other than e, which contradicts the fact that removing e disconnects T1)."""

import json
from itertools import combinations

REPORT = {
    "record_id": "Algorithms_36__sol4",
    "outcome": "NO_WITNESS_EXHAUSTIVE",
    "witness_description": "No counterexample exists in the bounded sweep: whenever removing e disconnects T1 into the endpoint components VA and VB, every distinct edge f directly joining VA to VB is absent from T1.",
    "refutation_explanation": "The search found no refutation in its explicitly bounded simple-graph model. If such an f were present, it would remain after e was removed and would connect VA to VB, contradicting their being distinct components. This bounded result does not establish the claim for graph interpretations not specified by the quote.",
    "search_space": "For each n in {2, 3, 4, 5}: every labeled simple undirected graph T1 on vertices 0 through n-1, every possible edge e, and every distinct possible edge f, filtered to cases where T1 is connected, e belongs to T1, removing e disconnects its endpoints, and f directly joins the resulting endpoint components.",
}


def component(start, vertices, edge_set):
    reached = {start}
    frontier = [start]
    while frontier:
        vertex = frontier.pop()
        for other in vertices:
            edge = (vertex, other) if vertex < other else (other, vertex)
            if other not in reached and other != vertex and edge in edge_set:
                reached.add(other)
                frontier.append(other)
    return reached


witness = None
for n in range(2, 6):
    vertices = tuple(range(n))
    possible_edges = tuple(combinations(vertices, 2))
    for mask in range(1 << len(possible_edges)):
        t1 = {
            edge
            for index, edge in enumerate(possible_edges)
            if mask & (1 << index)
        }
        if component(0, vertices, t1) != set(vertices):
            continue
        for e in possible_edges:
            if e not in t1:
                continue
            without_e = t1 - {e}
            va = component(e[0], vertices, without_e)
            if e[1] in va:
                continue
            vb = component(e[1], vertices, without_e)
            for f in possible_edges:
                if f == e:
                    continue
                crosses = ((f[0] in va and f[1] in vb) or
                           (f[1] in va and f[0] in vb))
                if crosses and f in t1:
                    witness = (n, tuple(sorted(t1)), e, f)
                    break
            if witness is not None:
                break
        if witness is not None:
            break
    if witness is not None:
        break

assert (witness is None) == (REPORT["outcome"] == "NO_WITNESS_EXHAUSTIVE")
print(json.dumps(REPORT, separators=(",", ":")))
