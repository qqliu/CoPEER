r'''By partitioning any even cycle within the graph by their subscripts such that all even subscripted vertex are separated from the odd subscripted vertex, we have created a bipartite graph.'''

import json

record_id = "SE_math_2233469__q"
vertices = (0, 1, 2, 3)
reported_edges = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3))
edges = frozenset(frozenset(edge) for edge in reported_edges)
cycle = (0, 2, 1, 3)

simple_graph = (
    len(edges) == len(reported_edges)
    and all(len(edge) == 2 and edge <= frozenset(vertices) for edge in edges)
)
cycle_distinct = len(frozenset(cycle)) == 4
cycle_edges = tuple(
    frozenset((cycle[index], cycle[(index + 1) % len(cycle)]))
    for index in range(len(cycle))
)
cycle_present = cycle_distinct and all(edge in edges for edge in cycle_edges)
cycle_even = len(cycle) % 2 == 0

even_part = frozenset(cycle[index] for index in range(0, len(cycle), 2))
odd_part = frozenset(cycle[index] for index in range(1, len(cycle), 2))
parts_match_report = (
    even_part == frozenset((0, 1))
    and odd_part == frozenset((2, 3))
    and even_part.isdisjoint(odd_part)
    and even_part | odd_part == frozenset(vertices)
)

same_class_edges = tuple(
    edge for edge in edges
    if edge <= even_part or edge <= odd_part
)
reported_obstruction = frozenset((0, 1)) in same_class_edges
triangle_present = all(
    frozenset(edge) in edges
    for edge in ((0, 1), (1, 2), (2, 0))
)

def coloring_is_proper(bits):
    for edge in edges:
        left, right = tuple(edge)
        if ((bits >> left) & 1) == ((bits >> right) & 1):
            return False
    return True

has_two_coloring = any(coloring_is_proper(bits) for bits in range(1 << len(vertices)))
confirmed = (
    simple_graph
    and cycle_present
    and cycle_even
    and parts_match_report
    and reported_obstruction
    and triangle_present
    and not has_two_coloring
)

if confirmed:
    verdict = "CONFIRMED"
    notes = (
        "Exact recomputation verifies the reported 4-cycle and its parity classes. "
        "The ambient graph has the same-class edge {0,1}, and exhaustive exact "
        "two-color checking also shows that the graph is not bipartite (it contains "
        "the triangle 0-1-2-0). The refuted statement is substantive, not plainly a typo."
    )
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "Independent exact checks did not validate the reported witness; the statement is substantive, not plainly a typo."

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, separators=(",", ":")))
