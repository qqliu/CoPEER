"""If K'=Q(u) is totally real, u is an algebraic integer with 2<u<14, and every embedding of K' that is nonidentity on K=Q(u^2) sends u into (-2,2), then [K:Q]≤6."""

import json
from fractions import Fraction
from itertools import product

RECORD_ID = "arxiv_math_0407313v2__source_enriched_codex"
NEGATIVE_WITNESS = (
    "No polynomial in the stated 1,458-polynomial space had exactly six "
    "roots in (-2,2) and one root in (2,14)."
)
NEGATIVE_EXPLANATION = (
    "The exact bounded sweep found no counterexample. This is exhaustive only "
    "for the stated Eisenstein family and does not establish the claim for "
    "algebraic integers outside that family."
)
SEARCH_SPACE = (
    "All 1,458 monic degree-7 polynomials x^7+a6*x^6+...+a1*x+a0 with "
    "a0 in {-2,2} and each of a1,...,a6 in {-2,0,2}; every polynomial is "
    "Eisenstein at 2. Exact Sturm sequences counted roots in (-2,2) and "
    "(2,14)."
)


def trim(poly):
    result = list(poly)
    while result and result[-1] == 0:
        result.pop()
    return result


def derivative(poly):
    return trim([poly[index] * index for index in range(1, len(poly))])


def reciprocal(value):
    return Fraction(value.denominator, value.numerator)


def polynomial_remainder(dividend, divisor):
    remainder = list(dividend)
    divisor = trim(divisor)
    while remainder and len(remainder) >= len(divisor):
        shift = len(remainder) - len(divisor)
        factor = remainder[-1] * reciprocal(divisor[-1])
        for index in range(len(divisor)):
            remainder[index + shift] -= factor * divisor[index]
        remainder = trim(remainder)
    return remainder


def sturm_sequence(integer_coefficients):
    first = [Fraction(coefficient, 1) for coefficient in integer_coefficients]
    sequence = [first, derivative(first)]
    while sequence[-1]:
        remainder = polynomial_remainder(sequence[-2], sequence[-1])
        if not remainder:
            break
        sequence.append([-coefficient for coefficient in remainder])
    return sequence


def evaluate(poly, point):
    value = Fraction(0, 1)
    for coefficient in reversed(poly):
        value = value * point + coefficient
    return value


def variations(sequence, point):
    signs = []
    for poly in sequence:
        value = evaluate(poly, point)
        if value > 0:
            signs.append(1)
        elif value < 0:
            signs.append(-1)
    return sum(signs[index] != signs[index - 1] for index in range(1, len(signs)))


def roots_between(sequence, left, right):
    return variations(sequence, Fraction(left, 1)) - variations(
        sequence, Fraction(right, 1)
    )


def polynomial_text(coefficients):
    pieces = ["x^7"]
    for power in range(6, -1, -1):
        coefficient = coefficients[power]
        if coefficient == 0:
            continue
        magnitude = abs(coefficient)
        if power == 0:
            term = str(magnitude)
        elif power == 1:
            term = ("" if magnitude == 1 else str(magnitude) + "*") + "x"
        else:
            term = ("" if magnitude == 1 else str(magnitude) + "*") + "x^" + str(power)
        pieces.append((" + " if coefficient > 0 else " - ") + term)
    return "".join(pieces)


def main():
    values = (-2, 0, 2)
    result = {
        "record_id": RECORD_ID,
        "outcome": "NO_WITNESS_EXHAUSTIVE",
        "witness_description": NEGATIVE_WITNESS,
        "refutation_explanation": NEGATIVE_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }

    for constant in (-2, 2):
        for remaining in product(values, repeat=6):
            coefficients = [constant] + list(remaining) + [1]
            sequence = sturm_sequence(coefficients)
            if roots_between(sequence, -2, 2) == 6 and roots_between(sequence, 2, 14) == 1:
                displayed = polynomial_text(coefficients)
                result = {
                    "record_id": RECORD_ID,
                    "outcome": "WITNESS_FOUND",
                    "witness_description": (
                        "Let u be the unique root in (2,14) of p(x)=" + displayed
                        + "; the other six roots of p lie in (-2,2)."
                    ),
                    "refutation_explanation": (
                        "The polynomial is monic and Eisenstein at 2, so u is an "
                        "algebraic integer of degree 7. Exact Sturm counts give seven "
                        "real roots, six in (-2,2) and u in (2,14). Since "
                        "[Q(u):Q(u^2)] divides 2 while [Q(u):Q]=7 is odd, "
                        "Q(u^2)=Q(u), so [K:Q]=7>6 and every nonidentity embedding "
                        "sends u to one of the six roots in (-2,2)."
                    ),
                    "search_space": SEARCH_SPACE,
                }
                print(json.dumps(result, separators=(",", ":"), ensure_ascii=False))
                return

    print(json.dumps(result, separators=(",", ":"), ensure_ascii=False))


if __name__ == "__main__":
    main()
