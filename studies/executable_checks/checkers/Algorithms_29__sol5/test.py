"""If G has a simple path visiting exactly n vertices, then none of the additional 17 isolated vertices can be on this path (as they have no edges)."""

import json
from itertools import permutations

REPORT = {
    "record_id": "Algorithms_29__sol5",
    "outcome": "WITNESS_FOUND",
    "witness_description": "n=1; G has vertices ordinary_00 and isolated_00 through isolated_16, no edges, and the simple path is (isolated_00).",
    "refutation_explanation": "A one-vertex path needs no edge. Thus (isolated_00) is a simple path in G, visits exactly n=1 vertex, and includes one of the 17 designated additional isolated vertices, so the claimed conclusion is false without an assumption such as n at least 2.",
    "search_space": "Exhaustively swept all 18 ordered one-vertex sequences in the unique edgeless graph on ordinary_00 plus the 17 designated vertices isolated_00 through isolated_16, with n fixed to 1.",
}

ADDITIONAL_ISOLATED = tuple(
    "isolated_" + str(index).zfill(2) for index in range(17)
)
VERTICES = ("ordinary_00",) + ADDITIONAL_ISOLATED
EDGES = frozenset()


def is_simple_path(path):
    return len(path) == len(set(path)) and all(
        frozenset((path[index], path[index + 1])) in EDGES
        for index in range(len(path) - 1)
    )


first_violation = None
candidate_count = 0
for n in (1,):
    for path in permutations(VERTICES, n):
        candidate_count += 1
        if (
            is_simple_path(path)
            and len(path) == n
            and any(vertex in ADDITIONAL_ISOLATED for vertex in path)
            and first_violation is None
        ):
            first_violation = (n, path)

assert candidate_count == 18
assert first_violation == (1, ("isolated_00",))
assert is_simple_path(first_violation[1])
assert len(first_violation[1]) == first_violation[0]
assert first_violation[1][0] in ADDITIONAL_ISOLATED
assert REPORT["outcome"] == "WITNESS_FOUND"

print(json.dumps(REPORT, sort_keys=True, separators=(",", ":")))
