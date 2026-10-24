r"""Every nonconstant real polynomial has leading coefficient 1 and therefore has the displayed monic form."""

import json


def main():
    coefficients = (0, 2)
    degree = -1
    for exponent, coefficient in enumerate(coefficients):
        if coefficient != 0:
            degree = exponent

    coefficients_are_real = all(isinstance(value, int) for value in coefficients)
    is_nonconstant = degree >= 1
    leading_coefficient = coefficients[degree]
    is_monic = leading_coefficient == 1

    verified = coefficients_are_real and is_nonconstant and leading_coefficient == 2 and not is_monic
    verdict = "CONFIRMED" if verified else "REFUTED_WITNESS_INVALID"
    notes = (
        "Exact integer arithmetic verifies that f(x) = 2x has degree 1 and leading coefficient 2, "
        "so it is a nonconstant real polynomial that is not monic. The refuted statement is "
        "substantive, not plainly a typo."
    )
    result = {
        "record_id": "reddit_learnmath_1ufl3wv",
        "verdict": verdict,
        "notes": notes,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
