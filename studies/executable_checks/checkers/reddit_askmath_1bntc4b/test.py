"""The multiplicativity formula for Euler's phi function can be applied to the factorization 16 = 2^2 · 2^2."""

import json
from math import gcd


def phi_by_exhaustion(n):
    return sum(1 for k in range(1, n + 1) if gcd(k, n) == 1)


def main():
    factorizations = ((4, 4),)
    witness = None
    for left, right in factorizations:
        if left * right != 16:
            continue
        phi_product = phi_by_exhaustion(left) * phi_by_exhaustion(right)
        phi_whole = phi_by_exhaustion(16)
        if phi_whole != phi_product:
            witness = (left, right, gcd(left, right), phi_whole, phi_product)
            break

    if witness is None:
        raise AssertionError("Expected the supplied factorization to be a counterexample")

    result = {
        "record_id": "reddit_askmath_1bntc4b",
        "outcome": "WITNESS_FOUND",
        "witness_description": "The supplied factorization itself is a witness: 16 = 4 · 4, with gcd(4, 4) = 4, φ(16) = 8, and φ(4)φ(4) = 2 · 2 = 4.",
        "refutation_explanation": "Exact enumeration shows that φ(16) is not equal to φ(4)φ(4). Therefore Euler's phi multiplicativity formula cannot be applied to this non-coprime factorization.",
        "search_space": "The single supplied ordered factorization (4, 4) of 16, with φ(16) exhaustively computed over k = 1,...,16 and φ(4) exhaustively computed over k = 1,...,4 using exact integer gcd."
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
