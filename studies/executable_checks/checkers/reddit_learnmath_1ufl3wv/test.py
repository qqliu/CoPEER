"""Every nonconstant real polynomial has leading coefficient 1 and therefore has the displayed monic form."""

import json


def main():
    leading_coefficients = (2, -2, -1, 1)
    constant_coefficients = (0, -2, -1, 1, 2)
    violations = []

    for leading in leading_coefficients:
        for constant in constant_coefficients:
            is_nonconstant = leading != 0
            has_required_leading_coefficient = leading == 1
            if is_nonconstant and not has_required_leading_coefficient:
                violations.append((leading, constant))

    assert len(leading_coefficients) * len(constant_coefficients) == 20
    assert violations
    assert violations[0] == (2, 0)

    result = {
        "record_id": "reddit_learnmath_1ufl3wv",
        "outcome": "WITNESS_FOUND",
        "witness_description": "f(x) = 2x is a nonconstant real polynomial whose leading coefficient is 2.",
        "refutation_explanation": "The claim requires every nonconstant real polynomial to have leading coefficient 1. The polynomial f(x) = 2x has real coefficients and is nonconstant, but its leading coefficient is 2, not 1, so it is not of the displayed monic form.",
        "search_space": "All 20 linear polynomials f(x) = ax + b with a in the fixed ordered set (2, -2, -1, 1) and b in the fixed ordered set (0, -2, -1, 1, 2); every candidate was checked."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
