r"""Let X be a finite generalized simplicial complex on a vertex set V: thus X is a family of subsets of V closed under inclusion. Define its actual vertices by vert(X):={x∈V:{x}∈X}; elements of V\vert(X) are ghost vertices. For an actual vertex u, define del(X;u):={S∈X:u∉S} and lk(X;u):={T∈X:u∉T and T∪{u}∈X}. For a ghost vertex u, set lk(X;u)=del(X;u)={∅}. Call u∈V a cone vertex when lk(X;u)=del(X;u), and let V°(X) be the set of non-cone vertices. Define θ on finite simplicial complexes recursively by θ(X)=0 if V°(X)=∅, and otherwise by θ(X)=min_{u∈V°(X)} max{θ(del(X;u)), θ(lk(X;u))+1}. Here a “vertex of X” means an actual vertex. Then, for every finite generalized simplicial complex X and every actual vertex v∈vert(X), θ(lk(X;v))≤θ(del(X;v))."""

import json
from functools import lru_cache

REPORT = {
    "record_id": "arxiv_2201.13046v3__source_enriched_codex",
    "verdict": "CONFIRMED",
    "notes": "Independent exact set-based recursion gives θ(lk(X;0))=1 and θ(del(X;0))=0, so the claimed inequality fails. The refuted statement is substantive, not plainly a typo: the source quote states the same inequality and the witness satisfies all supplied definitions.",
}

EMPTY_FACE = frozenset()
GHOST_COMPLEX = frozenset((EMPTY_FACE,))


def actual_vertices(faces, ambient):
    return frozenset(
        vertex
        for vertex in ambient
        if frozenset((vertex,)) in faces
    )


def deletion(faces, vertex):
    if frozenset((vertex,)) not in faces:
        return GHOST_COMPLEX
    return frozenset(face for face in faces if vertex not in face)


def link(faces, vertex):
    singleton = frozenset((vertex,))
    if singleton not in faces:
        return GHOST_COMPLEX
    return frozenset(
        face
        for face in faces
        if vertex not in face and face.union(singleton) in faces
    )


@lru_cache(maxsize=None)
def theta(faces, ambient):
    choices = []
    for vertex in sorted(ambient):
        deleted = deletion(faces, vertex)
        linked = link(faces, vertex)
        if linked != deleted:
            deletion_value = theta(deleted, ambient)
            link_value = theta(linked, ambient) + 1
            choices.append(
                deletion_value
                if deletion_value >= link_value
                else link_value
            )
    return min(choices) if choices else 0


V = frozenset((0, 1, 2))
X = frozenset((
    EMPTY_FACE,
    frozenset((0,)),
    frozenset((1,)),
    frozenset((2,)),
    frozenset((0, 1)),
    frozenset((0, 2)),
    frozenset((1, 2)),
))

assert EMPTY_FACE in X
assert all(
    face.difference((vertex,)) in X
    for face in X
    for vertex in face
)
assert actual_vertices(X, V) == V
assert frozenset((0, 1, 2)) not in X

expected_link = frozenset((
    EMPTY_FACE,
    frozenset((1,)),
    frozenset((2,)),
))
expected_deletion = frozenset((
    EMPTY_FACE,
    frozenset((1,)),
    frozenset((2,)),
    frozenset((1, 2)),
))

computed_link = link(X, 0)
computed_deletion = deletion(X, 0)
assert computed_link == expected_link
assert computed_deletion == expected_deletion

left = theta(computed_link, V)
right = theta(computed_deletion, V)
assert left == 1
assert right == 0
assert left > right
assert not left <= right
assert REPORT["verdict"] == "CONFIRMED"

print(json.dumps(REPORT, ensure_ascii=True, separators=(",", ":")))
