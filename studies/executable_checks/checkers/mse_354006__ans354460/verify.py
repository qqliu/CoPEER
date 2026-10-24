r"""Induction hypothesis: Suppose any bipartite graph $G$ with bipartition $A,B$, satisfying Hall's condition for $A$, and such that $\deg(v)\geq m$ for all $v\in A$ admits $m!$ matchings saturating all of $A$."""

import json

record_id = "mse_354006__ans354460"
m = 3
left = ("a0",)
right = ("b0", "b1", "b2")
edges = frozenset({
    ("a0", "b0"),
    ("a0", "b1"),
    ("a0", "b2"),
})


def all_subsets(items):
    subsets = [()]
    for item in items:
        subsets += [subset + (item,) for subset in subsets]
    return subsets


def hall_holds():
    for subset in all_subsets(left):
        neighbors = set()
        for vertex in subset:
            for candidate in right:
                if (vertex, candidate) in edges:
                    neighbors.add(candidate)
        if len(neighbors) < len(subset):
            return False
    return True


def enumerate_saturating_matchings(position, occupied):
    if position == len(left):
        return (frozenset(),)
    vertex = left[position]
    results = []
    for candidate in right:
        if candidate not in occupied and (vertex, candidate) in edges:
            tails = enumerate_saturating_matchings(
                position + 1, occupied | frozenset({candidate})
            )
            for tail in tails:
                results.append(tail | frozenset({(vertex, candidate)}))
    return tuple(results)


def factorial(number):
    value = 1
    factor = 2
    while factor <= number:
        value *= factor
        factor += 1
    return value


valid_bipartite_edges = all(a in left and b in right for a, b in edges)
degrees_sufficient = all(
    sum(1 for b in right if (a, b) in edges) >= m for a in left
)
matchings = set(enumerate_saturating_matchings(0, frozenset()))
verified = (
    valid_bipartite_edges
    and hall_holds()
    and degrees_sufficient
    and len(matchings) == 3
    and factorial(m) == 6
    and len(matchings) < factorial(m)
)

if verified:
    verdict = "CONFIRMED"
    notes = "Independently verified the stated witness: Hall's condition holds, the sole A-vertex has degree 3, and exactly 3 distinct A-saturating matchings exist, while 3! = 6. The refuted statement is substantive, not plainly a typo."
else:
    verdict = "CANNOT_REPRODUCE"
    notes = "The independent exact-arithmetic verification did not establish the reported counterexample. The alleged refutation would be substantive, not plainly a typo."

print(json.dumps({
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}))
