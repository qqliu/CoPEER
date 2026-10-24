"""Applying the displayed argument to √16 establishes a common factor of p and q and concludes that √16 is irrational."""

import json
from fractions import Fraction
from math import gcd


def main():
    witness = None
    for q in range(1, 17):
        for p in range(0, 65):
            value = Fraction(p, q)
            if value * value == 16 and gcd(p, q) == 1:
                witness = (p, q)
                break
        if witness is not None:
            break

    assert witness == (4, 1)
    result = {
        "record_id": "reddit_mathematics_1j7062e",
        "outcome": "WITNESS_FOUND",
        "witness_description": "p = 4, q = 1: Fraction(4, 1)^2 = 16 and gcd(4, 1) = 1.",
        "refutation_explanation": "The exact rational number 4/1 is the nonnegative square root of 16, since 4^2 = 16. Its numerator and denominator have no common factor greater than 1, so the asserted irrational conclusion is false.",
        "search_space": "All integer pairs (p, q) with 0 <= p <= 64 and 1 <= q <= 16, in increasing q then increasing p, testing p^2 = 16q^2 and gcd(p, q) = 1."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
