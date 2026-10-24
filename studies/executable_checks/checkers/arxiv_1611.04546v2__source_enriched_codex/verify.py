"""Every triangle-free planar graph of n vertices contains an induced forest of size at least 5n/9 + 20/27."""

import json
from fractions import Fraction

RECORD_ID = "arxiv_1611.04546v2__source_enriched_codex"
VERDICT = "CONFIRMED"
NOTES = (
    "Exact recomputation confirms that the one-vertex edgeless graph is planar "
    "and triangle-free, its maximum induced-forest size is 1, and 1 < 35/27. "
    "This is a substantive failure of the statement as written, not a plainly "
    "identifiable typo; no stated restriction excludes n = 1."
)


def induced_subgraph_is_acyclic(vertex_count, edges, mask):
    parent = list(range(vertex_count))

    def root(vertex):
        while parent[vertex] != vertex:
            vertex = parent[vertex]
        return vertex

    for left, right in edges:
        if not (mask & (1 << left)) or not (mask & (1 << right)):
            continue
        left_root = root(left)
        right_root = root(right)
        if left_root == right_root:
            return False
        parent[left_root] = right_root
    return True


def main():
    vertices = (0,)
    edges = frozenset()
    vertex_count = len(vertices)

    simple = all(
        0 <= left < right < vertex_count
        for left, right in edges
    )

    triangle_free = True
    for first in range(vertex_count):
        for second in range(first + 1, vertex_count):
            for third in range(second + 1, vertex_count):
                if {(first, second), (first, third), (second, third)} <= edges:
                    triangle_free = False

    # One isolated point is itself a crossing-free plane drawing.
    planar = vertex_count == 1 and len(edges) == 0

    largest_forest = 0
    for mask in range(1 << vertex_count):
        if induced_subgraph_is_acyclic(vertex_count, edges, mask):
            size = mask.bit_count()
            if size > largest_forest:
                largest_forest = size

    claimed_bound = Fraction(5 * vertex_count, 9) + Fraction(20, 27)
    refutes_claim = (
        simple
        and triangle_free
        and planar
        and largest_forest == 1
        and claimed_bound == Fraction(35, 27)
        and Fraction(largest_forest, 1) < claimed_bound
    )
    if not refutes_claim:
        raise AssertionError("independent exact verification failed")

    print(json.dumps({
        "record_id": RECORD_ID,
        "verdict": VERDICT,
        "notes": NOTES,
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
