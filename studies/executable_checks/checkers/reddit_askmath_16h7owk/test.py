"""For arbitrary a=L+M, the map ε ↦ ε²+aε is an automorphism of the positive reals."""

import json
from fractions import Fraction
from itertools import product


RECORD_ID = "reddit_askmath_16h7owk"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No certified witness: the quote gives no domain for L and M "
    "(and hence no admissible range for a=L+M)."
)
REFUTATION_EXPLANATION = (
    "The bounded sweep's first conditional closure failure is L=-2, M=-2, "
    "ε=1, for which a=-4 and ε²+aε=-3, not a positive real. This refutes "
    "the claim only if those values of L and M are admissible; the supplied "
    "quote does not say that they are, so the result is inconclusive."
)
SEARCH_SPACE = (
    "Exhaustively swept all 400 ordered tuples (L,M,p,q) with "
    "L,M∈{-2,-1,0,1,2} and p,q∈{1,2,3,4}, taking ε=p/q exactly "
    "(including duplicate rational values), and tested whether "
    "ε²+(L+M)ε is nonpositive. This grid is illustrative, not an asserted "
    "admissible domain."
)


def search():
    first_failure = None
    checked = 0
    for l_value, m_value in product(range(-2, 3), repeat=2):
        parameter = l_value + m_value
        for numerator, denominator in product(range(1, 5), repeat=2):
            epsilon = Fraction(numerator, denominator)
            image = epsilon * epsilon + parameter * epsilon
            checked += 1
            if image <= 0 and first_failure is None:
                first_failure = (l_value, m_value, epsilon, image)
    return checked, first_failure


def main():
    checked, first_failure = search()
    assert checked == 400
    assert first_failure == (-2, -2, Fraction(1, 1), Fraction(-3, 1))
    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
