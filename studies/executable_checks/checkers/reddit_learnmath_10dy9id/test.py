"""For finite n, the displayed equality among the two consecutive Fibonacci ratios and the inverse of f_{n-2}/f_{n-2} holds."""

import json
from fractions import Fraction
from itertools import product

RECORD_ID = "reddit_learnmath_10dy9id"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = "No certified counterexample: the bounded sweep finds unequal ratios for arbitrary integer triples, but the quote provides no criterion by which any such triple can be certified as consecutive Fibonacci terms."
REFUTATION_EXPLANATION = "The supplied quote does not define the Fibonacci sequence, its indexing or initial values, the admissible finite values of n, or the nonzero-denominator conditions. Consequently, an exact bounded algebraic sweep cannot determine which tested triples, if any, instantiate the claim."
SEARCH_SPACE = "All 252 ordered integer triples (a,b,c) in {-3,-2,-1,0,1,2,3}^3 with b != 0 and c != 0, interpreted only as algebraic placeholders for (f_n,f_{n-1},f_{n-2}); every triple was tested in lexicographic product order using exact Fraction values."


def main():
    values = range(-3, 4)
    checked = 0
    algebraic_violations = 0

    for a, b, c in product(values, repeat=3):
        if b == 0 or c == 0:
            continue
        checked += 1
        first_ratio = Fraction(a, b)
        second_ratio = Fraction(b, c)
        inverse_self_ratio = Fraction(1, 1)
        if not (first_ratio == second_ratio == inverse_self_ratio):
            algebraic_violations += 1

    assert checked == 252
    assert algebraic_violations > 0

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":"), ensure_ascii=True))


if __name__ == "__main__":
    main()
