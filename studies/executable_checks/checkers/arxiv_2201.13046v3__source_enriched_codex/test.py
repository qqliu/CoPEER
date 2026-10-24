r"""Let X be a finite generalized simplicial complex on a vertex set V: thus X is a family of subsets of V closed under inclusion. Define its actual vertices by vert(X):={x∈V:{x}∈X}; elements of V\vert(X) are ghost vertices. For an actual vertex u, define del(X;u):={S∈X:u∉S} and lk(X;u):={T∈X:u∉T and T∪{u}∈X}. For a ghost vertex u, set lk(X;u)=del(X;u)={∅}. Call u∈V a cone vertex when lk(X;u)=del(X;u), and let V°(X) be the set of non-cone vertices. Define θ on finite simplicial complexes recursively by θ(X)=0 if V°(X)=∅, and otherwise by θ(X)=min_{u∈V°(X)} max{θ(del(X;u)), θ(lk(X;u))+1}. Here a “vertex of X” means an actual vertex. Then, for every finite generalized simplicial complex X and every actual vertex v∈vert(X), θ(lk(X;v))≤θ(del(X;v))."""

import json
from functools import lru_cache

REPORT = {
    "record_id": "arxiv_2201.13046v3__source_enriched_codex",
    "outcome": "WITNESS_FOUND",
    "witness_description": "V={0,1,2}, X={∅,{0},{1},{2},{0,1},{0,2},{1,2}}, and v=0; the exhaustive sweep computes θ(lk(X;0))=1 and θ(del(X;0))=0.",
    "refutation_explanation": "For this X, lk(X;0)={∅,{1},{2}}. At either non-cone vertex its deletion is a one-vertex simplex of θ=0 and its link is {∅} of θ=0, so θ(lk(X;0))=1. Meanwhile del(X;0)={∅,{1},{2},{1,2}} is a simplex, all its vertices are cone vertices, and its θ is 0; hence 1≤0 is false.",
    "search_space": "All downward-closed families X⊆𝒫(V_n) for V_n={0,...,n−1} and n∈{0,1,2,3}, including the empty family, with every actual vertex tested; family codes and vertices were visited in increasing integer-mask order.",
}


def is_downward_closed(family_code, subset_count):
    for face in range(subset_count):
        if family_code & (1 << face):
            subface = face
            while True:
                if not (family_code & (1 << subface)):
                    return False
                if subface == 0:
                    break
                subface = (subface - 1) & face
    return True


def deletion(faces, vertex):
    singleton = 1 << vertex
    if singleton not in faces:
        return frozenset((0,))
    return frozenset(
        face for face in sorted(faces) if (face & singleton) == 0
    )


def link(faces, vertex):
    singleton = 1 << vertex
    if singleton not in faces:
        return frozenset((0,))
    return frozenset(
        face
        for face in sorted(faces)
        if (face & singleton) == 0 and (face | singleton) in faces
    )


@lru_cache(maxsize=None)
def theta(faces, ambient_size):
    branch_values = []
    for vertex in range(ambient_size):
        deleted = deletion(faces, vertex)
        linked = link(faces, vertex)
        if linked != deleted:
            branch_values.append(
                max(theta(deleted, ambient_size), theta(linked, ambient_size) + 1)
            )
    if not branch_values:
        return 0
    return min(branch_values)


first_violation = None
for ambient_size in range(4):
    subset_count = 1 << ambient_size
    family_code_limit = 1 << subset_count
    for family_code in range(family_code_limit):
        if not is_downward_closed(family_code, subset_count):
            continue
        faces = frozenset(
            face
            for face in range(subset_count)
            if family_code & (1 << face)
        )
        for vertex in range(ambient_size):
            if (1 << vertex) not in faces:
                continue
            linked = link(faces, vertex)
            deleted = deletion(faces, vertex)
            left = theta(linked, ambient_size)
            right = theta(deleted, ambient_size)
            if left > right and first_violation is None:
                first_violation = (
                    ambient_size,
                    family_code,
                    vertex,
                    left,
                    right,
                    faces,
                    linked,
                    deleted,
                )

expected_faces = frozenset((0, 1, 2, 3, 4, 5, 6))
expected_link = frozenset((0, 2, 4))
expected_deletion = frozenset((0, 2, 4, 6))
expected_violation = (
    3,
    127,
    0,
    1,
    0,
    expected_faces,
    expected_link,
    expected_deletion,
)

assert first_violation == expected_violation
assert theta(expected_link, 3) == 1
assert theta(expected_deletion, 3) == 0
assert REPORT["outcome"] == "WITNESS_FOUND"

print(json.dumps(REPORT, ensure_ascii=True, separators=(",", ":")))
