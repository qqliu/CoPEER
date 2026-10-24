r"""Let F be a field of characteristic p>2, let A⊂F be finite, and put n=|A|≤p^(2/3). Let F̄ be an algebraic closure of F and define Q=(AA−AA)/(A+A−A−A)={ (a1a2−a3a4)/(a5+a6−a7−a8) : a1,…,a8∈A and a5+a6−a7−a8≠0 }. For any ξ∈F̄\Q, replace A by the shifted set A+ξ. Equivalently, retaining a,b,c∈A as the unshifted variables, associate to every ordered triple (a,b,c)∈A³ the homogeneous point-coordinate quadruple (a−c:a+ξ:b+ξ:c+ξ) and the dual homogeneous plane-coordinate quadruple (b+ξ:−(c+ξ):c−a:a+ξ), regarded over F̄. A homogeneous quadruple must be nonzero; two point-coordinate quadruples, or two dual plane-coordinate quadruples, define the same projective point or plane exactly when one is a nonzero scalar multiple of the other. The claim is that, for every such permitted ξ, all these quadruples are nonzero and each of the two maps from A³ is injective. Thus the construction gives exactly n³ distinct projective points and exactly n³ distinct projective planes."""

import json
import itertools

RECORD_ID = "arxiv_1508.05142v6__source_enriched_codex"
VERDICT = "CONFIRMED"
NOTES = "Independent exact arithmetic confirms that Q(A)=GF(3), ξ=t is permitted, and the distinct triples (0,0,0) and (1,1,1) yield nonzero proportional point and plane quadruples. The refuted injectivity statement is substantive, not plainly a typo."

p = 3
A = (0, 1)
zero = (0, 0)
one = (1, 0)
t = (0, 1)


def mod3(value):
    return value % p


def ext(value):
    return (mod3(value), 0)


def add(left, right):
    return (mod3(left[0] + right[0]), mod3(left[1] + right[1]))


def neg(value):
    return (mod3(-value[0]), mod3(-value[1]))


def sub(left, right):
    return add(left, neg(right))


def mul(left, right):
    # Exact arithmetic in GF(3)[t]/(t*t+1), where t*t=2.
    return (
        mod3(left[0] * right[0] + 2 * left[1] * right[1]),
        mod3(left[0] * right[1] + left[1] * right[0]),
    )


def inv3(value):
    value = mod3(value)
    assert value != 0
    for candidate in (1, 2):
        if mod3(value * candidate) == 1:
            return candidate
    raise AssertionError("inverse missing")


def scale(scalar, vector):
    return tuple(mul(scalar, entry) for entry in vector)


def nonzero(vector):
    return any(entry != zero for entry in vector)


def point(triple, xi):
    a, b, c = triple
    return (
        ext(a - c),
        add(ext(a), xi),
        add(ext(b), xi),
        add(ext(c), xi),
    )


def plane(triple, xi):
    a, b, c = triple
    return (
        add(ext(b), xi),
        neg(add(ext(c), xi)),
        ext(c - a),
        add(ext(a), xi),
    )


# The modulus X*X+1 has no root in GF(3), and every nonzero residue has an
# inverse, so these pairs form the field GF(9), embedded in an algebraic closure.
assert all(mod3(x * x + 1) != 0 for x in range(p))
elements = tuple((a, b) for a in range(p) for b in range(p))
for value in elements:
    if value != zero:
        assert any(mul(value, candidate) == one for candidate in elements)
assert mul(t, t) == ext(2)

# Verify the characteristic and the size hypothesis without approximation.
assert p > 2
assert add(add(one, one), one) == zero
n = len(A)
assert n * n * n <= p * p

# Recompute Q directly from its eight quantified variables.
q_values = set()
for values in itertools.product(A, repeat=8):
    numerator = mod3(values[0] * values[1] - values[2] * values[3])
    denominator = mod3(values[4] + values[5] - values[6] - values[7])
    if denominator != 0:
        quotient = mod3(numerator * inv3(denominator))
        q_values.add(ext(quotient))
assert q_values == {ext(0), ext(1), ext(2)}
xi = t
assert xi not in q_values

first = (0, 0, 0)
second = (1, 1, 1)
assert first != second

first_point = point(first, xi)
second_point = point(second, xi)
first_plane = plane(first, xi)
second_plane = plane(second, xi)
assert nonzero(first_point) and nonzero(second_point)
assert nonzero(first_plane) and nonzero(second_plane)

# Compute 1+2t exactly; it is the reported nonzero projective scalar.
scalar = add(one, mul(ext(2), t))
assert scalar != zero
assert mul(scalar, t) == add(one, t)
assert scale(scalar, first_point) == second_point
assert scale(scalar, first_plane) == second_plane

print(json.dumps({
    "record_id": RECORD_ID,
    "verdict": VERDICT,
    "notes": NOTES,
}, ensure_ascii=False))
