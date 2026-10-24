"""The explicitly reconstructed points form a valid folded configuration with A=C while preserving the specified edge lengths."""

import json

RECORD_ID = "reddit_askmath_1ileqom"
WITNESS = (
    "The quoted reconstruction itself: A=C=(0,0), "
    "B=(223/100 cos(300/223), 223/100 sin(300/223)), and "
    "D=(223/100 cos(-300/223), 223/100 sin(-300/223))."
)
EXPLANATION = (
    "Because A=C, the segments AB and CB have identical endpoints and therefore "
    "equal lengths. The specified requirements instead assign |AB|=3 and |BC|=4, "
    "which is impossible. Likewise, CD and AD have identical endpoints but are "
    "assigned 3 and 4. Thus the reconstructed points cannot preserve the four "
    "specified edge lengths."
)
SEARCH_SPACE = (
    "The singleton space containing the quoted reconstruction's endpoint "
    "identification A=C and its four specified edge constraints: |AB|=3, |BC|=4, "
    "|CD|=3, and |DA|=4. The program exhaustively checks all four constraints "
    "after identifying coincident endpoints."
)

configurations = (
    (
        (("A", "C"),),
        (("A", "B", 3), ("B", "C", 4), ("C", "D", 3), ("D", "A", 4)),
    ),
)

conflict_found = False
for identifications, constraints in configurations:
    vertices = ("A", "B", "C", "D")
    parent = {vertex: vertex for vertex in vertices}

    def find(vertex):
        while parent[vertex] != vertex:
            vertex = parent[vertex]
        return vertex

    for left, right in identifications:
        left_root = find(left)
        right_root = find(right)
        if left_root != right_root:
            smaller, larger = sorted((left_root, right_root))
            parent[larger] = smaller

    assigned_lengths = {}
    for left, right, length in constraints:
        edge = tuple(sorted((find(left), find(right))))
        if edge in assigned_lengths and assigned_lengths[edge] != length:
            conflict_found = True
        else:
            assigned_lengths[edge] = length

assert conflict_found

result = {
    "record_id": RECORD_ID,
    "outcome": "WITNESS_FOUND",
    "witness_description": WITNESS,
    "refutation_explanation": EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, sort_keys=True, separators=(",", ":")))
