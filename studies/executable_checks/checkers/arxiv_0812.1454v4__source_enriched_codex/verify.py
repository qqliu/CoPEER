r'''Let \(A\subset\mathbb C\) be finite with \(0\notin A\), and let \(A_2=A\times A\). Let \(T\) be the finite set of complex lines through the origin that support points of \(A_2\), and let \(\nu(t)\) be the number of points of \(A_2\) on the line indexed by \(t\). Thus the multiplicative energy is \(E(A)=\sum_{t\in T}\nu(t)^2\). Dyadically decompose the range \(\nu(t)\in\{1,\ldots,|A|\}\), and let \(T'\subseteq T\) be a dyadic class whose contribution \(\sum_{t\in T'}\nu(t)^2\) is maximal; in particular, the values \(\nu(t)\) for \(t\in T'\) differ by at most a factor of two. Under the standard embedding \(\mathbb C^2\cong\mathbb R^4\), let \(X\) be the image of \(A_2\), and let \(\pi_t\) be the real two-plane corresponding to the complex line indexed by \(t\). Suppose there is a subset \(T''\subseteq T'\) with \(|T''|\ge |T'|/2\) such that, for each \(t\in T''\), one can assign another \(t_1\in T''\) and retain at least half of the points of \(X\cap\pi_t\) and at least half of the points of \(X\cap\pi_{t_1}\), with every resulting vector sum \(x+x_1\) pairwise distinct across the construction. Then \[\sum_{t\in T'}\nu(t)^2\le \frac{1}{32}|X+X|.\] Here \(|\cdot|\) denotes finite-set cardinality, \(X+X=\{x+x_1:x,x_1\in X\}\), \(|X|=|A|^2\), and \(|X+X|=|A+A|^2\).'''

import json
from math import gcd

REPORT = {
    "record_id": "arxiv_0812.1454v4__source_enriched_codex",
    "verdict": "CONFIRMED",
    "notes": "The witness independently checks out exactly. The refuted statement is plainly a typo: the factor 1/32 reverses the direction of the intended counting constant, rather than exposing a substantive failure of the argument.",
}


def slope_of(point):
    x, y = point
    divisor = gcd(abs(x), abs(y))
    numerator = y // divisor
    denominator = x // divisor
    if denominator < 0:
        numerator = -numerator
        denominator = -denominator
    return numerator, denominator


def embed(point):
    return point[0], 0, point[1], 0


A = (1, 2, 4)
assert len(set(A)) == len(A)
assert all(value != 0 for value in A)

A2 = tuple((x, y) for x in A for y in A)
lines = dict()
for point in A2:
    slope = slope_of(point)
    lines.setdefault(slope, []).append(point)
for slope in lines:
    lines[slope] = tuple(lines[slope])

occupancies = dict((slope, len(points)) for slope, points in lines.items())
assert sum(occupancies.values()) == len(A2) == 9
assert all(1 <= count <= len(A) for count in occupancies.values())

classes = dict()
for slope, count in occupancies.items():
    class_index = count.bit_length() - 1
    lower = 1 << class_index
    upper = 1 << (class_index + 1)
    assert lower <= count < upper
    classes.setdefault(class_index, set()).add(slope)

contributions = dict()
for class_index, slopes in classes.items():
    contributions[class_index] = sum(
        occupancies[slope] * occupancies[slope] for slope in slopes
    )

T_prime = frozenset(((1, 2), (1, 1), (2, 1)))
assert T_prime == frozenset(classes[1])
assert contributions[1] == 17
assert contributions[0] == 2
assert contributions[1] == max(contributions.values())
prime_counts = tuple(occupancies[slope] for slope in T_prime)
assert max(prime_counts) <= 2 * min(prime_counts)

T_double = T_prime
assignment = dict()
assignment[(1, 2)] = (1, 1)
assignment[(1, 1)] = (2, 1)
assignment[(2, 1)] = (1, 2)

retained = dict()
retained[(1, 2)] = ((2, 1),)
retained[(1, 1)] = ((1, 1), (2, 2))
retained[(2, 1)] = ((1, 2),)

assert 2 * len(T_double) >= len(T_prime)
for slope in T_double:
    other = assignment[slope]
    assert other in T_double
    assert other != slope
    assert set(retained[slope]).issubset(lines[slope])
    assert set(retained[other]).issubset(lines[other])
    assert 2 * len(retained[slope]) >= occupancies[slope]
    assert 2 * len(retained[other]) >= occupancies[other]

constructed_sums = []
for slope in sorted(T_double):
    other = assignment[slope]
    for first in retained[slope]:
        for second in retained[other]:
            first4 = embed(first)
            second4 = embed(second)
            constructed_sums.append(tuple(
                first4[index] + second4[index] for index in range(4)
            ))

expected_sums = {
    (3, 0, 2, 0),
    (4, 0, 3, 0),
    (2, 0, 3, 0),
    (3, 0, 4, 0),
    (3, 0, 3, 0),
}
assert set(constructed_sums) == expected_sums
assert len(constructed_sums) == len(set(constructed_sums)) == 5

X = tuple(embed(point) for point in A2)
X_plus_X = set()
for first in X:
    for second in X:
        X_plus_X.add(tuple(
            first[index] + second[index] for index in range(4)
        ))
assert set(constructed_sums).issubset(X_plus_X)

A_plus_A = set(x + y for x in A for y in A)
assert A_plus_A == {2, 3, 4, 5, 6, 8}
assert len(X) == len(A) * len(A) == 9
assert len(X_plus_X) == len(A_plus_A) * len(A_plus_A) == 36

prime_energy = sum(
    occupancies[slope] * occupancies[slope] for slope in T_prime
)
assert prime_energy == 17
assert 32 * prime_energy > len(X_plus_X)

print(json.dumps(REPORT, separators=(",", ":")))
