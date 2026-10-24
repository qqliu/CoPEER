"""The displayed integral defines the Petersson inner product on the space of weight-2 cusp forms, as required by the self-adjointness claim for D_N."""

import json
from fractions import Fraction
from itertools import product


record_id = "reddit_mathematics_1m1oif2"
outcome = "NO_WITNESS_INCONCLUSIVE"
witness_description = (
    "No concrete witness: the quote supplies no specific N, nonzero cusp "
    "forms f and g, their values, or definition of D_N."
)
refutation_explanation = (
    "The finite sweep detects nonunit weight-2 transformation factors for "
    "the displayed unweighted density, but this alone is not a concrete "
    "counterexample inside S_2(Gamma_0(N)). Without a specified N, actual "
    "nonzero forms, and a definition of D_N, neither the asserted "
    "inner-product identity nor the referenced self-adjointness claim can "
    "be conclusively tested."
)
search_space = (
    "Exhaustive illustrative sweep of N in {1,2,3,4}; every integer tuple "
    "(a,b,c,d) in {-2,-1,0,1,2}^4 satisfying ad-bc=1 and c congruent to 0 "
    "modulo N; and every z=x+iy with x in {-1,0,1} and y in {1,2}. For "
    "each case, |cz+d|^4 was computed exactly. This is not an exhaustive "
    "search over N or cusp forms."
)

entries = tuple(range(-2, 3))
xs = (Fraction(-1, 1), Fraction(0, 1), Fraction(1, 1))
ys = (Fraction(1, 1), Fraction(2, 1))
checked = 0
nonunit_factors = 0

for level in range(1, 5):
    for a, b, c, d in product(entries, repeat=4):
        if a * d - b * c != 1 or c % level != 0:
            continue
        for x, y in product(xs, ys):
            absolute_square = (c * x + d) ** 2 + (c * y) ** 2
            weight_two_factor = absolute_square ** 2
            checked += 1
            if weight_two_factor != Fraction(1, 1):
                nonunit_factors += 1

assert checked > 0
assert nonunit_factors > 0

result = {
    "record_id": record_id,
    "outcome": outcome,
    "witness_description": witness_description,
    "refutation_explanation": refutation_explanation,
    "search_space": search_space,
}
print(json.dumps(result, sort_keys=True, separators=(",", ":")))
