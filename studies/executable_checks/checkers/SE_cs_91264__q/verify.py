r'''Suppose we have a graph G with |V| vertices that has a minimum spanning tree.  Suppose we also have a set of |V| - 1 edges = <$e_1$, $e_2$, ..., $e_n$>, such that each edge is a light edge for some cut C, and these edges do not form a cycle.  This set of edges must form a minimum spanning tree.'''

import itertools
import json

RECORD_ID = "SE_cs_91264__q"
CONFIRMED_NOTES = "The refuted statement is substantive, not plainly a typo: tied light edges can each be light for the same cut yet collectively form a spanning tree heavier than an MST."
INVALID_NOTES = "The reported witness could not be validated; the statement would therefore not be refuted by this witness."

vertices = (0, 1, 2)
weighted_edges = (
    ((0, 1), 1),
    ((0, 2), 2),
    ((1, 2), 2),
)
selected = ((0, 2), (1, 2))

weight_by_edge = {edge: weight for edge, weight in weighted_edges}
all_edges = tuple(weight_by_edge)


def acyclic(edges):
    representative = {vertex: vertex for vertex in vertices}

    def root(vertex):
        while representative[vertex] != vertex:
            vertex = representative[vertex]
        return vertex

    for u, v in edges:
        root_u = root(u)
        root_v = root(v)
        if root_u == root_v:
            return False
        representative[root_v] = root_u
    return True


def spanning_tree(edges):
    if len(edges) != len(vertices) - 1 or not acyclic(edges):
        return False
    reached = {vertices[0]}
    frontier = [vertices[0]]
    while frontier:
        current = frontier.pop()
        for u, v in edges:
            if u == current and v not in reached:
                reached.add(v)
                frontier.append(v)
            elif v == current and u not in reached:
                reached.add(u)
                frontier.append(u)
    return reached == set(vertices)


def crosses(edge, side):
    u, v = edge
    return (u in side) != (v in side)


def all_cut_sides():
    for size in range(1, len(vertices)):
        for members in itertools.combinations(vertices, size):
            yield frozenset(members)


def light_for_a_cut(edge):
    for side in all_cut_sides():
        if not crosses(edge, side):
            continue
        crossing = tuple(candidate for candidate in all_edges if crosses(candidate, side))
        least = min(weight_by_edge[candidate] for candidate in crossing)
        if weight_by_edge[edge] == least:
            return True
    return False


def total_weight(edges):
    return sum(weight_by_edge[edge] for edge in edges)


trees = tuple(
    candidate
    for candidate in itertools.combinations(all_edges, len(vertices) - 1)
    if spanning_tree(candidate)
)
optimum = min(total_weight(tree) for tree in trees)
selected_total = total_weight(selected)
reported_cut = frozenset((0, 1))
reported_crossing = tuple(edge for edge in all_edges if crosses(edge, reported_cut))
reported_cut_check = (
    set(reported_crossing) == set(selected)
    and all(
        weight_by_edge[edge] == min(weight_by_edge[item] for item in reported_crossing)
        for edge in selected
    )
)
valid_refutation = (
    len(selected) == len(vertices) - 1
    and acyclic(selected)
    and spanning_tree(selected)
    and all(light_for_a_cut(edge) for edge in selected)
    and reported_cut_check
    and selected_total == 4
    and optimum == 3
    and selected_total > optimum
)

if valid_refutation:
    verdict = "CONFIRMED"
    notes = CONFIRMED_NOTES
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = INVALID_NOTES

print(json.dumps({"record_id": RECORD_ID, "verdict": verdict, "notes": notes}))
