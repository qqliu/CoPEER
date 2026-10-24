"""For every odd n, the binomial expansion of (x+y)^n contains a term of the form (xy)^n."""

import json
from math import comb


def contains_claimed_term(n):
    terms = [(comb(n, k), n - k, k) for k in range(n + 1)]
    return any(coefficient != 0 and x_power == n and y_power == n
               for coefficient, x_power, y_power in terms)


def main():
    odd_values = (1, 3, 5, 7, 9)
    counterexamples = []
    for n in odd_values:
        if not contains_claimed_term(n):
            counterexamples.append(n)

    if counterexamples:
        first = counterexamples[0]
        if first != 1:
            raise AssertionError("unexpected first counterexample")
        payload = {
            "record_id": "reddit_askmath_17lqiae",
            "outcome": "WITNESS_FOUND",
            "witness_description": "n=1: the expansion is x+y, whose exponent pairs are (1,0) and (0,1), so it contains no xy term.",
            "refutation_explanation": "The claimed term (xy)^1=xy would have exponent pair (1,1). Neither term of (x+y)^1 has that exponent pair, so the universal claim fails at the odd integer n=1.",
            "search_space": "All binomial terms indexed by k=0,...,n for every odd n in {1,3,5,7,9}; each term was checked by exact integer coefficient and exponent pair."
        }
    else:
        payload = {
            "record_id": "reddit_askmath_17lqiae",
            "outcome": "NO_WITNESS_EXHAUSTIVE",
            "witness_description": "No counterexample was found in the bounded search.",
            "refutation_explanation": "The bounded search found no violating odd exponent.",
            "search_space": "All binomial terms indexed by k=0,...,n for every odd n in {1,3,5,7,9}; each term was checked by exact integer coefficient and exponent pair."
        }

    print(json.dumps(payload, separators=(",", ":")))


if __name__ == "__main__":
    main()
