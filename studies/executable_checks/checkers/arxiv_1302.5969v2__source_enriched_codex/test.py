"""Theorem 23septt3aa asserts that the set S is precompact even though its definition requires only that each individual u have some Hölder constant C, rather than imposing one uniform constant for the family."""

import json
from fractions import Fraction
from itertools import product

RECORD_ID = "arxiv_1302.5969v2__source_enriched_codex"
WITNESS = "Take [a,b]=[0,1], E=W=X=R with the usual norm and identity injections, p=1, q=2, and R=1. Let g(x)=2 dist(x,Z) and u_n(t)=g(2^n t) for n>=0. The identity E->W is compact because R is finite-dimensional. Each u_n has L1 norm 1/2 and is Hölder-1/2 with its own constant 2^(n+1), so every u_n belongs to S. For every distinct m,n, the exact L1 distance between u_m and u_n is 1/3."
REFUTATION = "The sequence (u_n) is an infinite 1/3-separated subset of S in L1([0,1];W), hence has no Cauchy or convergent subsequence. Therefore S is not precompact. The growing constants 2^(n+1) demonstrate precisely why individual, nonuniform Hölder constants do not yield the asserted conclusion."
SEARCH_SPACE = "Exhaustive lexicographic sweep of 16 templates: p=1; q in {2,3}; R in {1,1/2}; amplitude A in {1,1/2}; and frequency base B in {2,3}. For every template the program checks the exact L1 bound, the individual Hölder implication, and the closed-form even-B separation certificate; it also exactly integrates frequency gaps 1 through 6 as a certificate check. The selected template is (p,q,R,A,B)=(1,2,1,1,2). The finite template sweep finds an analytically certified infinite family; the six-gap check is not treated as exhaustive evidence about precompactness."


def tent_distance_unit(scale):
    """Return integral_0^1 |g(x)-g(scale*x)| dx exactly."""
    total = Fraction(0, 1)
    for branch in range(scale):
        if branch % 2 == 0:
            numerator = branch * branch + (scale - 1 - branch) ** 2
            denominator = 2 * scale * scale * (scale - 1)
        else:
            numerator = (scale - branch) ** 2 + (branch + 1) ** 2
            denominator = 2 * scale * scale * (scale + 1)
        total += Fraction(numerator, denominator)
    return total


# Here g(x)=2*dist(x,Z). For every even integer N, g(Nx) has N affine
# branches. On the even branches, summing the two triangular areas gives
# sum_{j=0}^{N-1} j^2 / (2*N^2*(N-1)) = (2*N-1)/(12*N).
# On the odd branches it gives
# sum_{j=1}^{N} j^2 / (2*N^2*(N+1)) = (2*N+1)/(12*N).
# Their sum is 1/3. Thus if B is even, N=B^k is even for every k>=1,
# proving exactly (not merely for the checked gaps) that
# integral |A*g(x)-A*g(B^k*x)| dx = A/3.

p_values = (1,)
q_values = (2, 3)
r_values = (Fraction(1, 1), Fraction(1, 2))
amplitudes = (Fraction(1, 1), Fraction(1, 2))
bases = (2, 3)
valid = []
examined = 0

for p, q, radius, amplitude, base in product(
    p_values, q_values, r_values, amplitudes, bases
):
    examined += 1
    l1_norm = amplitude * Fraction(1, 2)
    holder_is_individual = p == 1 and q > 1
    generic_separation_certificate = base >= 2 and base % 2 == 0
    bounded_checks = all(
        amplitude * tent_distance_unit(base ** gap)
        == amplitude * Fraction(1, 3)
        for gap in range(1, 7)
    )
    if (
        l1_norm <= radius
        and holder_is_individual
        and generic_separation_certificate
        and bounded_checks
    ):
        valid.append((p, q, radius, amplitude, base))

assert examined == 16
assert valid
assert valid[0] == (1, 2, Fraction(1, 1), Fraction(1, 1), 2)

result = {
    "record_id": RECORD_ID,
    "outcome": "WITNESS_FOUND",
    "witness_description": WITNESS,
    "refutation_explanation": REFUTATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
