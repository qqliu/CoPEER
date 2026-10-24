r"""Let F be a field of characteristic p>2, let A⊂F be finite, and put n=|A|≤p^(2/3). Let F̄ be an algebraic closure of F and define Q=(AA−AA)/(A+A−A−A)={ (a1a2−a3a4)/(a5+a6−a7−a8) : a1,…,a8∈A and a5+a6−a7−a8≠0 }. For any ξ∈F̄\Q, replace A by the shifted set A+ξ. Equivalently, retaining a,b,c∈A as the unshifted variables, associate to every ordered triple (a,b,c)∈A³ the homogeneous point-coordinate quadruple (a−c:a+ξ:b+ξ:c+ξ) and the dual homogeneous plane-coordinate quadruple (b+ξ:−(c+ξ):c−a:a+ξ), regarded over F̄. A homogeneous quadruple must be nonzero; two point-coordinate quadruples, or two dual plane-coordinate quadruples, define the same projective point or plane exactly when one is a nonzero scalar multiple of the other. The claim is that, for every such permitted ξ, all these quadruples are nonzero and each of the two maps from A³ is injective. Thus the construction gives exactly n³ distinct projective points and exactly n³ distinct projective planes."""

import json
from itertools import combinations, product

P = 3
A = (0, 1)
ZERO = (0, 0)


def f3_add(x, y):
    return (x + y) % P


def f3_sub(x, y):
    return (x - y) % P


def f3_mul(x, y):
    return (x * y) % P


def f3_inv(x):
    assert x % P != 0
    for candidate in range(1, P):
        if f3_mul(x, candidate) == 1:
            return candidate
    raise AssertionError("nonzero GF(3) element lacked an inverse")


def embed(x):
    return (x % P, 0)


def add(x, y):
    return (f3_add(x[0], y[0]), f3_add(x[1], y[1]))


def neg(x):
    return ((-x[0]) % P, (-x[1]) % P)


def sub(x, y):
    return add(x, neg(y))


def mul(x, y):
    # Pairs denote a+b*t, with t^2=-1=2 in GF(3).
    constant = x[0] * y[0] + 2 * x[1] * y[1]
    linear = x[0] * y[1] + x[1] * y[0]
    return (constant % P, linear % P)


def nonzero_vector(vector):
    return any(entry != ZERO for entry in vector)


def proportional(left, right):
    if not nonzero_vector(left) or not nonzero_vector(right):
        return False
    for i in range(4):
        for j in range(i + 1, 4):
            if mul(left[i], right[j]) != mul(left[j], right[i]):
                return False
    return True


def point_coordinates(triple, xi):
    a, b, c = triple
    return (
        embed(f3_sub(a, c)),
        add(embed(a), xi),
        add(embed(b), xi),
        add(embed(c), xi),
    )


def plane_coordinates(triple, xi):
    a, b, c = triple
    return (
        add(embed(b), xi),
        neg(add(embed(c), xi)),
        embed(f3_sub(c, a)),
        add(embed(a), xi),
    )


assert len(A) ** 3 <= P ** 2

q_values = set()
for values in product(A, repeat=8):
    numerator = f3_sub(f3_mul(values[0], values[1]),
                       f3_mul(values[2], values[3]))
    denominator = (
        values[4] + values[5] - values[6] - values[7]
    ) % P
    if denominator != 0:
        q_values.add(embed(f3_mul(numerator, f3_inv(denominator))))

base_field = {(x, 0) for x in range(P)}
assert q_values == base_field

extension_elements = tuple(product(range(P), repeat=2))
permitted_xis = tuple(xi for xi in extension_elements if xi not in q_values)
assert len(permitted_xis) == 6

triples = tuple(product(A, repeat=3))
assert len(triples) == 8
violations = []

# Complete the whole bounded sweep even after finding a violation.
for xi in permitted_xis:
    points = tuple(point_coordinates(triple, xi) for triple in triples)
    planes = tuple(plane_coordinates(triple, xi) for triple in triples)

    for index in range(len(triples)):
        if not nonzero_vector(points[index]):
            violations.append(("zero_point", xi, index, index))
        if not nonzero_vector(planes[index]):
            violations.append(("zero_plane", xi, index, index))

    for left, right in combinations(range(len(triples)), 2):
        if proportional(points[left], points[right]):
            violations.append(("point_collision", xi, left, right))
        if proportional(planes[left], planes[right]):
            violations.append(("plane_collision", xi, left, right))

witness_xi = (0, 1)
first_triple = triples.index((0, 0, 0))
second_triple = triples.index((1, 1, 1))
assert ("point_collision", witness_xi, first_triple, second_triple) in violations
assert ("plane_collision", witness_xi, first_triple, second_triple) in violations

witness_description = (
    "In F=GF(3), take A={0,1} and ξ=t in GF(9)=GF(3)[t]/(t^2+1). "
    "The distinct triples (0,0,0) and (1,1,1) give point quadruples "
    "(0:t:t:t) and (0:1+t:1+t:1+t), and plane quadruples "
    "(t:−t:0:t) and (1+t:−(1+t):0:1+t)."
)
refutation_explanation = (
    "Here Q(A)=GF(3), so t∉Q(A), and |A|^3=8≤9=3^2, equivalently "
    "|A|≤3^(2/3). Multiplication by the nonzero scalar (1+t)/t=1+2t "
    "sends each quadruple for (0,0,0) to the corresponding quadruple for "
    "(1,1,1). Thus both projective maps identify two distinct triples and "
    "are not injective."
)
search_space = (
    "Exhaustive sweep for F=GF(3), A={0,1}, and "
    "GF(9)=GF(3)[t]/(t^2+1): all 6 elements ξ in GF(9)\\Q(A), all 8 "
    "ordered triples in A^3, all 48 nonzero-quadruple checks for each map, "
    "and all 168 distinct-triple pair comparisons for each of the point and "
    "plane maps."
)

result = {
    "record_id": "arxiv_1508.05142v6__source_enriched_codex",
    "outcome": "WITNESS_FOUND",
    "witness_description": witness_description,
    "refutation_explanation": refutation_explanation,
    "search_space": search_space,
}
print(json.dumps(result, ensure_ascii=False))
