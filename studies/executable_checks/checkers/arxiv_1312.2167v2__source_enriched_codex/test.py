"""If φ is an automorphism of a finitely generated group Γ and a nonzero character χ satisfies χ∘φ=rχ for some r≠0, then r=±1."""

import json
from fractions import Fraction
from itertools import product

RECORD_ID = "arxiv_1312.2167v2__source_enriched_codex"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "Take Γ = Z^2, φ(x,y) = (2x+y,x+y), χ(x,y) = x + ((sqrt(5)-1)/2)y, and r = (3+sqrt(5))/2."
REFUTATION_EXPLANATION = "The integer matrix of φ has determinant 1, so φ is an automorphism of the finitely generated group Z^2. Also χ(1,0)=1, so χ is nonzero. Exact arithmetic in Q(sqrt(5)) gives χ∘φ=rχ. The rate r has a nonzero sqrt(5) coefficient, so it is nonzero and is neither 1 nor -1, contradicting the conclusion."
SEARCH_SPACE = "All 531,441 tuples consisting of a 2x2 matrix with entries in {0,1,2} and parameters a,b,c,d independently in {n/2 : n=-4,...,4}, interpreted as χ(x,y)=x+(a+b√5)y and r=c+d√5, are visited in fixed lexicographic order; tuples whose matrix determinant is not ±1 are rejected."


def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def scale(x, n):
    return (x[0] * n, x[1] * n)


def multiply(x, y):
    return (x[0] * y[0] + Fraction(5) * x[1] * y[1],
            x[0] * y[1] + x[1] * y[0])


zero = (Fraction(0), Fraction(0))
one = (Fraction(1), Fraction(0))
minus_one = (Fraction(-1), Fraction(0))
found_expected = False
visited = 0

for p, q, s, t in product(range(3), repeat=4):
    determinant = p * t - q * s
    for an, bn, cn, dn in product(range(-4, 5), repeat=4):
        visited += 1
        if determinant not in (-1, 1):
            continue

        alpha = (Fraction(an, 2), Fraction(bn, 2))
        rate = (Fraction(cn, 2), Fraction(dn, 2))
        if rate == zero or rate == one or rate == minus_one:
            continue

        composed_on_first_generator = add(scale(one, p), scale(alpha, s))
        composed_on_second_generator = add(scale(one, q), scale(alpha, t))
        scaled_on_first_generator = multiply(rate, one)
        scaled_on_second_generator = multiply(rate, alpha)

        if (composed_on_first_generator == scaled_on_first_generator and
                composed_on_second_generator == scaled_on_second_generator):
            if ((p, q, s, t) == (2, 1, 1, 1) and
                    (an, bn, cn, dn) == (-1, 1, 3, 1)):
                found_expected = True

assert visited == 531441
assert found_expected

print(json.dumps({
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE
}, separators=(",", ":")))
