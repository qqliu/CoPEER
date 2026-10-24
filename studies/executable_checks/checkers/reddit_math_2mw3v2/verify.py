r"""The rank of a graph's cycle space is always exactly two less than its number of edges."""

import json

REPORT = {
    "record_id": "reddit_math_2mw3v2",
    "verdict": "CONFIRMED",
    "notes": "The three-edge star has cycle-space rank 0, whereas the claim predicts 1. This is a substantive false statement, not plainly a typo.",
}

vertices = (0, 1, 2, 3)
edges = ((0, 1), (0, 2), (0, 3))

kernel = []
for selection in range(1 << len(edges)):
    boundary = [0 for _ in vertices]
    for edge_index in range(len(edges)):
        if selection & (1 << edge_index):
            left, right = edges[edge_index]
            boundary[left] ^= 1
            boundary[right] ^= 1
    if not any(boundary):
        kernel.append(selection)

assert len(edges) == 3
assert kernel == [0]
cycle_space_size = len(kernel)
cycle_space_rank = cycle_space_size.bit_length() - 1
assert (1 << cycle_space_rank) == cycle_space_size
assert cycle_space_rank == 0
claimed_rank = len(edges) - 2
assert claimed_rank == 1
assert cycle_space_rank != claimed_rank
assert REPORT["verdict"] == "CONFIRMED"

print(json.dumps(REPORT, separators=(",", ":")))
