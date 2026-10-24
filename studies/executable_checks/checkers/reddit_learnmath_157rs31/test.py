"""Drawing an interior diagonal in a (k+1)-sided polygon produces two polygons whose side counts are both between 4 and k."""

import itertools
import json

RECORD_ID = "reddit_learnmath_157rs31"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "For k=4, use the strictly convex pentagon with vertices (0,0), (2,0), "
    "(3,1), (2,3), (0,2) in cyclic order. Its diagonal joining vertices 0 "
    "and 2 produces polygons with 3 and 4 sides."
)
REFUTATION_EXPLANATION = (
    "The required range is 4 through k=4. The polygon on the boundary path "
    "0-1-2 plus diagonal 2-0 has 3 sides, so its side count is not at least "
    "4. Thus this interior diagonal violates the claim."
)
SEARCH_SPACE = (
    "The single labeled strictly convex pentagon with vertices "
    "((0,0),(2,0),(3,1),(2,3),(0,2)), with k=4, and all 5 of its "
    "nonadjacent vertex pairs (all diagonals), swept in lexicographic order. "
    "Exact integer cross products verify strict convexity."
)


def cross(a, b, c):
    return ((b[0] - a[0]) * (c[1] - b[1])
            - (b[1] - a[1]) * (c[0] - b[0]))


def main():
    k = 4
    vertices = ((0, 0), (2, 0), (3, 1), (2, 3), (0, 2))
    n = len(vertices)

    assert n == k + 1
    assert all(
        cross(vertices[i], vertices[(i + 1) % n], vertices[(i + 2) % n]) > 0
        for i in range(n)
    )

    diagonals = []
    violations = []
    for a, b in itertools.combinations(range(n), 2):
        separation = b - a
        if separation == 1 or separation == n - 1:
            continue
        diagonals.append((a, b))
        side_counts = (separation + 1, n - separation + 1)
        if not all(4 <= count <= k for count in side_counts):
            violations.append((a, b, side_counts))

    assert len(diagonals) == 5
    assert len(violations) == 5
    assert violations[0] == (0, 2, (3, 4))

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
