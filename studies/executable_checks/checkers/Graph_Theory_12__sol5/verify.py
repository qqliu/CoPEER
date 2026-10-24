r"""If the length of P is odd, the other endpoint would receive the same color as the starting point, leading to a monochromatic edge when P is added."""

import json

REPORT = {
    "record_id": "Graph Theory_12__sol5",
    "verdict": "CONFIRMED",
    "notes": "The one-edge path has odd edge-length, independently generated alternating colors 0 and 1, and no monochromatic edge. The refuted statement is plainly a parity-reversal typo: odd path length gives opposite endpoint colors.",
}

vertices = ("v0", "v1")
initial_edges = ()
added_path_edges = tuple(
    (index, index + 1) for index in range(len(vertices) - 1)
)
path_length = len(added_path_edges)

colors = [0]
for edge in added_path_edges:
    assert edge[0] == len(colors) - 1
    colors.append(1 - colors[-1])

after_addition_edges = initial_edges + added_path_edges
monochromatic_edges = tuple(
    edge
    for edge in after_addition_edges
    if colors[edge[0]] == colors[edge[1]]
)

premise_is_true = path_length % 2 == 1
endpoints_same = colors[0] == colors[-1]
has_monochromatic_edge = len(monochromatic_edges) != 0

assert vertices == ("v0", "v1")
assert initial_edges == ()
assert added_path_edges == ((0, 1),)
assert path_length == 1
assert tuple(colors) == (0, 1)
assert premise_is_true
assert not endpoints_same
assert not has_monochromatic_edge
assert monochromatic_edges == ()

print(json.dumps(REPORT, separators=(",", ":")))
