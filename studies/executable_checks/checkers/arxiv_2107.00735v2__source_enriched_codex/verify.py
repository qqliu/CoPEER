r'''After choosing merely another subgroup H of order p, the proof may treat G/H as a quotient group and apply the induction hypothesis to it.'''

import json

RECORD_ID = "arxiv_2107.00735v2__source_enriched_codex"
NOTES = "Exact permutation arithmetic confirms that in D8, N=<r^2> is normal and H=<s> has order 2 with N intersection H={e}, but r s r^{-1}=r^2 s is not in H. The same input left cosets represented by e,s and r,r yield distinct output cosets, so multiplication on G/H is not well-defined. This refutes the stated claim and exposes a substantive logical gap, not a typo."

# Permutations act on four vertices. Multiplication is function composition.
def multiply(a, b):
    return tuple(a[b[index]] for index in range(4))


def inverse(a, universe):
    matches = []
    for candidate in universe:
        if multiply(a, candidate) == identity and multiply(candidate, a) == identity:
            matches.append(candidate)
    assert len(matches) == 1
    return matches[0]


def left_coset(g, subgroup):
    return frozenset(multiply(g, h) for h in subgroup)


identity = (0, 1, 2, 3)
r = (1, 2, 3, 0)
s = (0, 3, 2, 1)

rotations = [identity]
for unused in range(3):
    rotations.append(multiply(rotations[-1], r))

elements = tuple(rotations + [multiply(rotation, s) for rotation in rotations])
assert len(elements) == 8
assert len(frozenset(elements)) == 8

# Independently certify the finite group laws for the displayed witness.
for a in elements:
    assert multiply(identity, a) == a
    assert multiply(a, identity) == a
    inverse(a, elements)
    for b in elements:
        assert multiply(a, b) in elements
        for c in elements:
            assert multiply(multiply(a, b), c) == multiply(a, multiply(b, c))

r_squared = rotations[2]
r_cubed = rotations[3]
N = frozenset((identity, r_squared))
H = frozenset((identity, s))
p = 2

assert len(N) == p
assert len(H) == p
assert N.intersection(H) == frozenset((identity,))

for subgroup in (N, H):
    assert identity in subgroup
    for a in subgroup:
        assert inverse(a, elements) in subgroup
        for b in subgroup:
            assert multiply(a, b) in subgroup

# N is normal.
for g in elements:
    g_inverse = inverse(g, elements)
    assert frozenset(multiply(multiply(g, n), g_inverse) for n in N) == N

# H is not normal: conjugating s by r produces r^2 s outside H.
r_inverse = inverse(r, elements)
r_squared_s = multiply(r_squared, s)
conjugate = multiply(multiply(r, s), r_inverse)
assert conjugate == r_squared_s
assert conjugate not in H

# Representatives e and s determine the same first left coset. Using r for
# the second coset nevertheless produces different candidate product cosets.
assert left_coset(identity, H) == left_coset(s, H)
output_from_identity = left_coset(multiply(identity, r), H)
output_from_s = left_coset(multiply(s, r), H)
assert multiply(s, r) == multiply(r_cubed, s)
assert output_from_identity == frozenset((r, multiply(r, s)))
assert output_from_s == frozenset((multiply(r_cubed, s), r_cubed))
assert output_from_identity != output_from_s

result = {
    "record_id": RECORD_ID,
    "verdict": "CONFIRMED",
    "notes": NOTES,
}
print(json.dumps(result, separators=(",", ":")))
