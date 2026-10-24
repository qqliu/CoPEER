"""For V^k=((x^2+y^2)^2+z^2)^k, the displayed formula for the partial derivative V_y is correct."""

import json

RECORD_ID = "arxiv_1406.1756v4__source_enriched_codex"
CONFIRMED_NOTES = "Exact formal-polynomial differentiation gives -80, while the displayed expression gives -64 at (k,x,y,z)=(2,-1,-1,-1), so the claim fails on the witness. The omitted y^4 term is plainly a typographical/algebraic omission, not a substantive mathematical phenomenon."


def polynomial_product(left, right):
    result = [0] * (len(left) + len(right) - 1)
    for left_degree, left_coefficient in enumerate(left):
        for right_degree, right_coefficient in enumerate(right):
            result[left_degree + right_degree] += left_coefficient * right_coefficient
    return result


def polynomial_value(coefficients, argument):
    value = 0
    for coefficient in reversed(coefficients):
        value = value * argument + coefficient
    return value


def integer_power(base, exponent):
    value = 1
    for _ in range(exponent):
        value *= base
    return value


def main():
    k, x, y, z = 2, -1, -1, -1

    x_squared_plus_y_squared = [x * x, 0, 1]
    inner = polynomial_product(x_squared_plus_y_squared, x_squared_plus_y_squared)
    inner[0] += z * z

    complete_polynomial = [1]
    for _ in range(k):
        complete_polynomial = polynomial_product(complete_polynomial, inner)

    derivative_coefficients = [
        degree * complete_polynomial[degree]
        for degree in range(1, len(complete_polynomial))
    ]
    actual = polynomial_value(derivative_coefficients, y)

    displayed_base = x * x * x * x + 2 * x * x * y * y + z * z
    displayed_factor = 4 * y * y * y + 4 * x * x * y
    displayed = k * integer_power(displayed_base, k - 1) * displayed_factor

    if actual == -80 and displayed == -64 and actual != displayed:
        verdict = "CONFIRMED"
        notes = CONFIRMED_NOTES
    else:
        verdict = "REFUTED_WITNESS_INVALID"
        notes = "The exact recomputation did not produce the reported unequal values; the alleged omission would be a plain typo if present."

    print(json.dumps({
        "record_id": RECORD_ID,
        "verdict": verdict,
        "notes": notes,
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
