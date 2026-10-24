r"""If the length of P is odd, the other endpoint would receive the same color as the starting point, leading to a monochromatic edge when P is added."""

import itertools
import json

REPORT = {
    "record_id": "Graph Theory_12__sol5",
    "outcome": "WITNESS_FOUND",
    "witness_description": "Start with two isolated labeled vertices v0 and v1, colored 0 and 1 respectively, and add the path P=v0--v1. P has edge-length 1; its other endpoint differs in color from the start, and its sole edge is not monochromatic.",
    "refutation_explanation": "The premise holds because P has one edge, hence odd length. The search's first violating coloring has endpoint colors 0 and 1, so the endpoints are unequal and the only added edge is bichromatic; therefore the claimed consequences both fail.",
    "search_space": "Exhaustive sweep for two initially isolated labeled vertices v0,v1 and the added one-edge path P=v0--v1, over all four binary vertex-colorings (0,0), (0,1), (1,0), and (1,1) in lexicographic order.",
}

path_vertices = (0, 1)
path_edges = ((0, 1),)
edge_length = len(path_edges)
colorings = tuple(itertools.product((0, 1), repeat=len(path_vertices)))
violations = []

for colors in colorings:
    endpoints_same = colors[path_vertices[0]] == colors[path_vertices[-1]]
    monochromatic_after_addition = any(
        colors[left] == colors[right] for left, right in path_edges
    )
    if (
        edge_length % 2 == 1
        and not endpoints_same
        and not monochromatic_after_addition
    ):
        violations.append(
            (colors, endpoints_same, monochromatic_after_addition)
        )

assert colorings == ((0, 0), (0, 1), (1, 0), (1, 1))
assert violations
first_witness = violations[0]
assert first_witness == ((0, 1), False, False)

print(json.dumps(REPORT, separators=(",", ":")))
