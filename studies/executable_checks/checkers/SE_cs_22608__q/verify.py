r"""If $X$ is the maximum weight independent set of the circular-arc graph $A$, then for any clique $Z$ of $A$, we have that $\| X \cap Z\| = 1$."""

import json

record_id = "SE_cs_22608__q"
confirmed_notes = (
    "The witness is valid. The refuted statement is plainly a typo: an "
    "independent set meets any clique in at most one vertex, not necessarily "
    "exactly one."
)

vertices = (0, 1, 2)
weights = {0: 1, 1: 1, 2: 2}
edges = frozenset({(0, 1), (0, 2), (1, 2)})

# Each pair (start, end) denotes a closed, non-wrapping arc on a circle
# parametrized from 0 through 3. Identical proper arcs certify K_3.
circumference = 4
arcs = {vertex: (0, 1) for vertex in vertices}


def arcs_intersect(first, second):
    first_start, first_end = first
    second_start, second_end = second
    return max(first_start, second_start) <= min(first_end, second_end)


def adjacent(left, right):
    pair = (left, right) if left < right else (right, left)
    return left != right and pair in edges


def independent(candidate):
    return all(
        not adjacent(candidate[i], candidate[j])
        for i in range(len(candidate))
        for j in range(i + 1, len(candidate))
    )


def clique(candidate):
    return all(
        adjacent(candidate[i], candidate[j])
        for i in range(len(candidate))
        for j in range(i + 1, len(candidate))
    )


arc_certificate_valid = all(
    0 <= arcs[vertex][0] < arcs[vertex][1] < circumference
    for vertex in vertices
) and all(
    adjacent(vertices[i], vertices[j])
    == arcs_intersect(arcs[vertices[i]], arcs[vertices[j]])
    for i in range(len(vertices))
    for j in range(i + 1, len(vertices))
)

subsets = tuple(
    tuple(vertex for position, vertex in enumerate(vertices) if mask & (1 << position))
    for mask in range(1 << len(vertices))
)
independent_sets = tuple(candidate for candidate in subsets if independent(candidate))
weight_by_set = {
    candidate: sum(weights[vertex] for vertex in candidate)
    for candidate in independent_sets
}
best_weight = max(weight_by_set.values())
best_sets = tuple(
    candidate for candidate in independent_sets
    if weight_by_set[candidate] == best_weight
)

x = (2,)
z = (0, 1)
witness_established = (
    arc_certificate_valid
    and best_weight == 2
    and best_sets == (x,)
    and clique(z)
    and len(set(x).intersection(z)) == 0
    and len(set(x).intersection(z)) != 1
)

if witness_established:
    verdict = "CONFIRMED"
    notes = confirmed_notes
else:
    verdict = "CANNOT_REPRODUCE"
    notes = "The independent exact recomputation did not establish the reported witness."

print(json.dumps({
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}, separators=(",", ":")))
