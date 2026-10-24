"""The proof uses the false general claim that G/G' is isomorphic to Z(G)."""

import json

REPORT = {
    "record_id": "reddit_learnmath_bwiq68",
    "verdict": "CONFIRMED",
    "notes": "Independent exact enumeration of S_3 gives derived subgroup A_3 of order 3, two quotient cosets, and a center of order 1, so G/G' cannot be isomorphic to Z(G). The refuted general statement is substantive, not plainly a typo.",
}


def compose(first, second):
    return tuple(first[second[position]] for position in range(3))


def invert(permutation):
    return tuple(permutation.index(value) for value in range(3))


def product(factors, identity):
    result = identity
    for factor in factors:
        result = compose(result, factor)
    return result


identity = (0, 1, 2)
group = {
    identity,
    (1, 0, 2),
    (2, 1, 0),
    (0, 2, 1),
    (1, 2, 0),
    (2, 0, 1),
}

assert len(group) == 6
assert all(compose(a, b) in group for a in group for b in group)
assert all(
    compose(compose(a, b), c) == compose(a, compose(b, c))
    for a in group
    for b in group
    for c in group
)
assert all(compose(identity, a) == a == compose(a, identity) for a in group)
assert all(
    compose(a, invert(a)) == identity == compose(invert(a), a)
    for a in group
)

center = {
    candidate
    for candidate in group
    if all(compose(candidate, other) == compose(other, candidate) for other in group)
}
assert center == {identity}

commutators = {
    product((a, b, invert(a), invert(b)), identity)
    for a in group
    for b in group
}
derived = {identity}
derived.update(commutators)
while True:
    enlarged = derived | {compose(a, b) for a in derived for b in derived}
    if enlarged == derived:
        break
    derived = enlarged

alternating = {identity, (1, 2, 0), (2, 0, 1)}
assert derived == alternating
assert all(invert(a) in derived for a in derived)

cosets = {
    frozenset(compose(representative, member) for member in derived)
    for representative in group
}
assert len(cosets) == 2
assert all(len(coset) == 3 for coset in cosets)
assert set().union(*cosets) == group
assert len(cosets) != len(center)

print(json.dumps(REPORT, sort_keys=True, separators=(",", ":")))
