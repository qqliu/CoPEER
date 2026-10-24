"""The conditions b^n ≥ M and x ≥ b suffice to invoke the asymptotic bound x^n/2 ≤ f(x) and conclude f(x) ≥ f(0)."""

import itertools
import json
from fractions import Fraction

RECORD_ID = "reddit_learnmath_1u24yp4"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "n=1, b=1, M=1, x=1, f(0)=1, and f(x)=1/2."
REFUTATION_EXPLANATION = (
    "The claimed conditions hold: b^n=1≥M=1 and x=1≥b=1. "
    "The asymptotic bound also holds with equality, since x^n/2=1/2=f(x). "
    "Nevertheless f(x)=1/2<1=f(0). The source's additional requirement "
    "b^n≥2f(0) fails here (1 is not at least 2), showing why the two "
    "conditions named in the target claim do not suffice."
)
SEARCH_SPACE = (
    "All 32,000 tuples (n,b,M,x,f(0),f(x)) with n,b,M,x in {1,2,3,4}, "
    "f(0) in {0,1,2,3,4}, and f(x)=k/2 for every integer k from -8 "
    "through 16, tested in that fixed lexicographic order. Every tuple was "
    "tested; the reported witness is the first tuple satisfying b^n≥M, "
    "x≥b, and x^n/2≤f(x), while violating f(x)≥f(0)."
)

first_witness = None
for n, b, m, x, f_zero, numerator in itertools.product(
    range(1, 5),
    range(1, 5),
    range(1, 5),
    range(1, 5),
    range(0, 5),
    range(-8, 17),
):
    f_at_x = Fraction(numerator, 2)
    lower_bound = Fraction(x ** n, 2)
    violates = (
        b ** n >= m
        and x >= b
        and lower_bound <= f_at_x
        and f_at_x < f_zero
    )
    if violates and first_witness is None:
        first_witness = (n, b, m, x, f_zero, f_at_x)

assert first_witness == (1, 1, 1, 1, 1, Fraction(1, 2))

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
