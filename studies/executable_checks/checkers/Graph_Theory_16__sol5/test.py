r"""Extend this orientation to all of G by orienting any additional edges arbitrarily (these cannot create longer paths since H already contains a k-vertex path and no longer path exists in H)."""

import itertools
import json

REPORT = {
    "record_id": "Graph Theory_16__sol5",
    "outcome": "WITNESS_FOUND",
    "witness_description": "Let H have labeled vertices {0,1,2}, sole directed edge 0->1, and k=2. Add the edge {0,2} and orient it 2->0. The resulting G has the 3-vertex directed path 2->0->1.",
    "refutation_explanation": "H has a 2-vertex directed path and no longer directed path, but one permitted orientation of an additional edge creates a 3-vertex directed path. Thus additional edges oriented arbitrarily can create a path longer than the longest path in H.",
    "search_space": "Both orientations, in fixed order 0->2 then 2->0, of the sole additional edge {0,2}, extending the fixed H on vertices {0,1,2} whose sole directed edge is 0->1."
}


def longest_simple_directed_path(vertices, arcs):
    arc_set = set(arcs)
    longest = 0
    for length in range(1, len(vertices) + 1):
        for path in itertools.permutations(vertices, length):
            if all((path[index], path[index + 1]) in arc_set
                   for index in range(length - 1)):
                longest = length
    return longest


vertices = (0, 1, 2)
h_arcs = ((0, 1),)
h_longest = longest_simple_directed_path(vertices, h_arcs)
assert h_longest == 2
assert (0, 1) in h_arcs

orientation_cases = ((0, 2), (2, 0))
violations = []
for added_arc in orientation_cases:
    g_arcs = h_arcs + (added_arc,)
    g_longest = longest_simple_directed_path(vertices, g_arcs)
    if g_longest > h_longest:
        violations.append((added_arc, g_longest, g_arcs))

if not violations:
    raise AssertionError("The exhaustive bounded search found no violation")

first_arc, first_length, first_g_arcs = violations[0]
assert first_arc == (2, 0)
assert first_length == 3
assert all((2, 0, 1)[index:index + 2] in first_g_arcs
           for index in range(2))

print(json.dumps(REPORT, separators=(",", ":")))
