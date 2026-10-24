r"""The proposed condition δ < min(1,(√3+√2)ε) guarantees |√x−√2| < ε whenever |x−2| < δ."""

import json
from fractions import Fraction

ONE = Fraction(1, 1)
TWO = Fraction(2, 1)
EIGHT = Fraction(8, 1)


def ratio_less_than_sqrt3_plus_sqrt2(delta, epsilon):
    ratio = Fraction(
        delta.numerator * epsilon.denominator,
        delta.denominator * epsilon.numerator,
    )
    ratio_squared = ratio * ratio
    if ratio_squared < Fraction(5, 1):
        return True
    excess = ratio_squared - Fraction(5, 1)
    return excess * excess < Fraction(24, 1)


def radical_distance_at_least_epsilon(x, epsilon):
    epsilon_squared = epsilon * epsilon
    bound_squared = EIGHT * epsilon_squared
    if x <= TWO:
        term = TWO + epsilon_squared - x
        return term >= 0 and term * term >= bound_squared
    term = x - TWO - epsilon_squared
    return term >= 0 and term * term >= bound_squared


first_witness = None
for a in range(1, 11):
    epsilon = Fraction(a, 100)
    for b in range(1, 101):
        delta = Fraction(b, 100)
        condition_on_delta = (
            delta < ONE
            and ratio_less_than_sqrt3_plus_sqrt2(delta, epsilon)
        )
        for c in range(0, 401):
            x = Fraction(c, 100)
            if (
                condition_on_delta
                and abs(x - TWO) < delta
                and radical_distance_at_least_epsilon(x, epsilon)
                and first_witness is None
            ):
                first_witness = (epsilon, delta, x)

expected = (Fraction(1, 20), Fraction(3, 20), Fraction(93, 50))
assert first_witness == expected

result = {
    "record_id": "reddit_learnmath_1bbke99",
    "outcome": "WITNESS_FOUND",
    "witness_description": "ε=1/20, δ=3/20, x=93/50.",
    "refutation_explanation": "The exact checks give |x−2|=7/50<3/20, δ<1, and δ/ε=3<√3+√2 (since 16<24 after exact squaring). Also √2−√(93/50)>1/20 because (57/400)^2=3249/160000>3200/160000=8(1/20)^2. Thus the antecedent holds while the asserted conclusion fails.",
    "search_space": "All 401,000 triples ε=a/100, δ=b/100, x=c/100 with integers 1≤a≤10, 1≤b≤100, 0≤c≤400, in lexicographic (a,b,c) order.",
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
