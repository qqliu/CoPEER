"""The final parametric-polar expression equals the Whewell curvature for every regular polar-parametric curve."""

import itertools
import json

RECORD_ID = "proofwiki_99460__codex_expansion"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No witness: none can be certified from the supplied data because the "
    "comparison quantity, Whewell curvature, is undefined."
)
REFUTATION_EXPLANATION = (
    "The quote supplies only one expression and gives no definition or "
    "independently computable formula for \"Whewell curvature,\" so equality "
    "cannot be tested. The finite sweep therefore neither refutes nor verifies "
    "the universal claim."
)
SEARCH_SPACE = (
    "Exhaustively enumerated all 5^5 = 3,125 integer substitutions "
    "(r,r',r'',theta',theta'') in {-2,-1,0,1,2}^5; the displayed numerator "
    "and squared denominator were evaluated for all 2,900 substitutions with "
    "r'^2+(r theta')^2>0. This is only a bounded jet sweep, not all regular "
    "curves."
)


def main():
    values = (-2, -1, 0, 1, 2)
    total = 0
    denominator_defined = 0

    for r, r_prime, r_second, theta_prime, theta_second in itertools.product(
        values, repeat=5
    ):
        total += 1
        squared_denominator = (
            r_prime * r_prime + (r * theta_prime) * (r * theta_prime)
        )
        if squared_denominator == 0:
            continue

        denominator_defined += 1
        numerator = (
            2 * r_prime * r_prime * theta_prime
            + r * r_second * theta_prime
            + r * r_prime * theta_second
            + r * r * theta_prime * theta_prime * theta_prime
        )

        # This pair exactly represents the supplied expression's numerator and
        # squared denominator without introducing an inexact square root.
        displayed_expression_data = (numerator, squared_denominator)
        assert isinstance(displayed_expression_data[0], int)
        assert displayed_expression_data[1] > 0

    assert total == 3125
    assert denominator_defined == 2900

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
