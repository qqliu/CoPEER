r"""The propagated relative uncertainty of the total mass is dM = sqrt(sum (dm_i)^2), the unweighted root-sum-square of the constituents' relative uncertainties."""

import json
from fractions import Fraction
from itertools import product

RECORD_ID = "reddit_mathematics_t3jogf"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = "No counterexample is certified."
REFUTATION_EXPLANATION = (
    "The quote supplies only the proposed right-hand side and gives no definition "
    "or independent criterion for the propagated total relative uncertainty dM. "
    "Exact values of dm_i therefore determine the claimed expression but cannot "
    "establish that it is wrong."
)
SEARCH_SPACE = (
    "All 22,620 ordered tuples of lengths 1 through 4 over the 12 distinct "
    "Fractions a/b with 0 <= a <= 4 and 1 <= b <= 4, in increasing Fraction "
    "order; for each tuple, sum(dm_i ** 2) was computed exactly. This bounded "
    "sweep cannot test the claim because the quote supplies no independent "
    "criterion for dM."
)


def main():
    values = tuple(sorted({
        Fraction(numerator, denominator)
        for numerator in range(5)
        for denominator in range(1, 5)
    }))
    checked = 0
    for length in range(1, 5):
        for uncertainties in product(values, repeat=length):
            claimed_square = sum((item ** 2 for item in uncertainties), Fraction(0, 1))
            if claimed_square < 0:
                raise AssertionError("A sum of exact squares cannot be negative")
            checked += 1

    if len(values) != 12 or checked != 22620:
        raise AssertionError("The declared finite search space was not swept")

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
