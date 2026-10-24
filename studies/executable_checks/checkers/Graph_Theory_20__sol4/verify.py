r'''since x in B because R contains v and R is connected by red edges, v and x are connected by a red path, implying x is reachable by a blue path from v as well; thus x in B'''

import json

REPORT = {
    "record_id": "Graph Theory_20__sol4",
    "verdict": "CONFIRMED",
    "notes": "Independent finite-graph reachability confirms the witness: the red edge connects v to x, while the empty blue edge set does not. The refuted red-path-to-blue-path implication is substantive, not plainly a typo.",
}


def component(origin, permitted_vertices, undirected_edges):
    reached = {origin}
    while True:
        expanded = set(reached)
        for left, right in undirected_edges:
            if left in reached:
                expanded.add(right)
            if right in reached:
                expanded.add(left)
        expanded.intersection_update(permitted_vertices)
        if expanded == reached:
            return frozenset(reached)
        reached = expanded


vertices = frozenset((0, 1))
region = frozenset((0, 1))
v = 0
x = 1
red_edges = ((0, 1),)
blue_edges = ()

assert v != x
assert region.issubset(vertices)
assert all(left in vertices and right in vertices and left != right for left, right in red_edges)
assert all(left in vertices and right in vertices and left != right for left, right in blue_edges)

red_component_in_region = component(v, region, red_edges)
blue_component_in_graph = component(v, vertices, blue_edges)
premises_hold = v in region and x in region and red_component_in_region == region
claimed_conclusion = x in blue_component_in_graph
claimed_implication = (not premises_hold) or claimed_conclusion

assert premises_hold
assert red_component_in_region == frozenset((v, x))
assert blue_component_in_graph == frozenset((v,))
assert claimed_conclusion is False
assert claimed_implication is False
assert REPORT["verdict"] == "CONFIRMED"

print(json.dumps(REPORT, separators=(",", ":")))
