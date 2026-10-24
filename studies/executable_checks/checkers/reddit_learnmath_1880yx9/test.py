"""From a_n > k and b_n > k, it follows that a_n + b_n > k for every real k."""

import json
from fractions import Fraction
from itertools import product


def main():
    k_values = (Fraction(-1), Fraction(0), Fraction(1))
    term_values = (Fraction(-3, 4), Fraction(0), Fraction(2))

    witnesses = []
    tested = 0
    for k, a_n, b_n in product(k_values, term_values, term_values):
        tested += 1
        if a_n > k and b_n > k and not (a_n + b_n > k):
            witnesses.append((k, a_n, b_n))

    expected = (Fraction(-1), Fraction(-3, 4), Fraction(-3, 4))
    assert tested == 27
    assert witnesses
    assert witnesses[0] == expected

    result = {
        "record_id": "reddit_learnmath_1880yx9",
        "outcome": "WITNESS_FOUND",
        "witness_description": "At a fixed index n, take k = -1 and a_n = b_n = -3/4.",
        "refutation_explanation": "Both -3/4 > -1, but a_n + b_n = -3/2, and -3/2 is not greater than -1. These rational numbers are real, so this refutes the universal claim.",
        "search_space": "All 27 triples in K x V x V, in fixed product order, where K = {-1, 0, 1} and V = {-3/4, 0, 2}; every triple was tested exactly using Fraction arithmetic."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
