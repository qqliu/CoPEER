r"""Extend this orientation to all of G by orienting any additional edges arbitrarily (these cannot create longer paths since H already contains a k-vertex path and no longer path exists in H)."""

import json

REPORT = {
    "record_id": "Graph Theory_16__sol5",
    "verdict": "CONFIRMED",
    "notes": "Independent exact enumeration confirms that H has longest simple directed path length 2, while orienting the additional edge as 2->0 creates the 3-vertex path 2->0->1. The refuted statement is substantive, not plainly a typo."
}


def enumerate_simple_directed_paths(vertices, arcs):
    vertex_tuple = tuple(vertices)
    arc_set = set(arcs)
    paths = []

    def extend(path):
        paths.append(tuple(path))
        last = path[-1]
        for candidate in vertex_tuple:
            if candidate not in path and (last, candidate) in arc_set:
                path.append(candidate)
                extend(path)
                path.pop()

    for start in vertex_tuple:
        extend([start])
    return tuple(paths)


vertices = (0, 1, 2)
assert len(set(vertices)) == len(vertices)

h_arcs = frozenset({(0, 1)})
extra_edge = frozenset({0, 2})
added_arc = (2, 0)

assert len(extra_edge) == 2
assert frozenset(added_arc) == extra_edge
assert added_arc[0] != added_arc[1]
assert (0, 2) not in h_arcs
assert (2, 0) not in h_arcs

g_arcs = h_arcs | {added_arc}
assert h_arcs < g_arcs

h_paths = enumerate_simple_directed_paths(vertices, h_arcs)
g_paths = enumerate_simple_directed_paths(vertices, g_arcs)
h_longest = max((len(path) for path in h_paths), default=0)
g_longest = max((len(path) for path in g_paths), default=0)

assert (0, 1) in h_paths
assert h_longest == 2
assert (2, 0, 1) in g_paths
assert (2, 0) in g_arcs and (0, 1) in g_arcs
assert g_longest == 3
assert g_longest > h_longest
assert REPORT["verdict"] == "CONFIRMED"

print(json.dumps(REPORT, separators=(",", ":")))
