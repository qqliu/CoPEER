"""PG visits n distinct vertices of G. There are only n original vertices in VH, so any set of n distinct vertices of G must include all the original vertices VH"""

import json
from itertools import combinations

REPORT = {
    "record_id": "Algorithms_29__sol4",
    "outcome": "WITNESS_FOUND",
    "witness_description": "n=1; G has vertex set {0,1}; VH={0} is the sole original vertex; PG visits the one-element set {1}.",
    "refutation_explanation": "The visited set has n=1 distinct vertex of G but does not contain 0, so it does not include all original vertices VH; therefore the asserted 'any set' conclusion is false.",
    "search_space": "For each n in {1,2,3} and each m in {n,n+1,n+2}, the full Cartesian product of all n-element VH subsets and all n-element visited subsets of the labeled vertex set {0,...,m-1} was exhaustively swept in lexicographic combination order."
}

first_violation = None
violation_count = 0
examined_count = 0

for n in range(1, 4):
    for vertex_count in range(n, n + 3):
        vertices = tuple(range(vertex_count))
        for original_vertices in combinations(vertices, n):
            for visited_vertices in combinations(vertices, n):
                examined_count += 1
                misses_original = any(
                    vertex not in visited_vertices
                    for vertex in original_vertices
                )
                if misses_original:
                    violation_count += 1
                    if first_violation is None:
                        first_violation = (
                            n,
                            vertices,
                            original_vertices,
                            visited_vertices,
                        )

assert examined_count > 0
assert violation_count > 0
assert first_violation == (1, (0, 1), (0,), (1,))

witness_n, witness_g, witness_vh, witness_visits = first_violation
assert len(witness_vh) == witness_n
assert len(set(witness_vh)) == witness_n
assert all(vertex in witness_g for vertex in witness_vh)
assert len(witness_visits) == witness_n
assert len(set(witness_visits)) == witness_n
assert all(vertex in witness_g for vertex in witness_visits)
assert any(vertex not in witness_visits for vertex in witness_vh)

print(json.dumps(REPORT, separators=(",", ":")))
