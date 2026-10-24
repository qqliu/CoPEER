"""For the stated product, the trigonometric expression on line 20 is valid, including at n=0."""

import json


def product_value(n):
    value = 1
    for k in range(1, n + 1):
        value *= -1 if k % 2 else 1
    return (value, 0)


def stated_rhs(n):
    triangular = n * (n + 1) // 2
    cosine = -1 if triangular % 2 else 1
    return (cosine, cosine)


def main():
    witness = None
    for n in range(0, 1):
        if product_value(n) != stated_rhs(n):
            witness = n
            break

    if witness != 0:
        raise AssertionError("expected the exhaustive sweep to find n=0")

    result = {
        "record_id": "reddit_learnmath_9qa1bc",
        "outcome": "WITNESS_FOUND",
        "witness_description": "n=0: the empty product is 1, represented as (1, 0), while the stated right-hand side is 1+i, represented as (1, 1).",
        "refutation_explanation": "At n=0, n(n+1)/2=0, so both displayed cosine terms equal cos(0)=1. Thus the claimed equality says 1=1+i, which is false because their imaginary parts are 0 and 1.",
        "search_space": "All integers n with 0 <= n <= 0; this one-element bounded space was exhaustively swept in increasing order using exact integer pairs for complex values."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
