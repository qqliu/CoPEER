"""The rewrite x=b(a/b+√2) is valid for arbitrary rational coefficients a and b."""

import json
from fractions import Fraction
from itertools import product


def search():
    values = (Fraction(-1, 1), Fraction(0, 1), Fraction(1, 1))
    violations = []

    for a, b in product(values, repeat=2):
        if b == 0:
            violations.append((a, b, "a/b is undefined"))
            continue

        quotient = a * Fraction(b.denominator, b.numerator)
        rhs_rational_coefficient = b * quotient
        rhs_sqrt2_coefficient = b
        if (rhs_rational_coefficient, rhs_sqrt2_coefficient) != (a, b):
            violations.append((a, b, "symbolic coefficients differ"))

    return violations


def main():
    violations = search()
    assert violations
    assert violations[0] == (Fraction(-1, 1), Fraction(0, 1), "a/b is undefined")

    result = {
        "record_id": "reddit_learnmath_o5qbvs",
        "outcome": "WITNESS_FOUND",
        "witness_description": "Take a=-1 and b=0, both rational. The subexpression a/b is division by zero, so b(a/b+√2) is undefined.",
        "refutation_explanation": "The claim quantifies over arbitrary rational b, which includes b=0. Multiplication by b outside the parentheses does not make the undefined quotient a/b meaningful. Thus the proposed rewrite is not valid for all rational coefficients.",
        "search_space": "All 9 ordered pairs (a,b) in {Fraction(-1,1), Fraction(0,1), Fraction(1,1)}^2, traversed in lexicographic product order; every pair was checked symbolically with exact Fraction arithmetic."
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
