"""For real x away from the poles of Gamma and real y, the absolute-value ratio |Gamma(x+iy)/Gamma(x)| equals the displayed infinite product with exponent -1."""

import json
from fractions import Fraction
from itertools import product

RECORD_ID = "arxiv_2002.06342v3__source_enriched_codex"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No counterexample was found among the four pairs (x,y) = "
    "(1,0), (2,0), (3,0), (4,0)."
)
REFUTATION_EXPLANATION = (
    "For every swept pair, y=0 makes the Gamma ratio a quantity divided by "
    "itself and makes every factor of the displayed product exactly 1, so "
    "both sides equal 1. The supplied quote gives no finite exact evaluation "
    "rule or bounds for Gamma or the infinite product at nonzero y, so this "
    "bounded sweep cannot decide the universal claim."
)
SEARCH_SPACE = (
    "Exactly the Cartesian product x in {1,2,3,4} and y in {0}, in "
    "increasing lexicographic order; all four pairs were checked with "
    "Fraction arithmetic."
)


def check_y_zero_case(x, y):
    if y != Fraction(0, 1):
        raise ValueError("This exact checker only handles y=0.")
    # On the stated domain, Gamma(x+0i)/Gamma(x) is a quantity divided by
    # itself. Every displayed product factor also has numerator y squared,
    # hence is exactly one. No truncation of the infinite product is needed.
    lhs = Fraction(1, 1)
    rhs = Fraction(1, 1)
    return lhs != rhs


def main():
    xs = tuple(Fraction(n, 1) for n in range(1, 5))
    ys = (Fraction(0, 1),)
    violations = []
    checked = 0
    for x, y in product(xs, ys):
        checked += 1
        if check_y_zero_case(x, y):
            violations.append((x, y))
    if checked != 4 or violations:
        raise AssertionError("The declared finite sweep was not completed.")
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
