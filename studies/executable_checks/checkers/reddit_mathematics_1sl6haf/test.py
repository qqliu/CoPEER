"""The axis Re(s) = 1/2 is the only axis on which zeros of the Riemann zeta function are possible."""

import json
from fractions import Fraction
from math import comb

RECORD_ID = "reddit_mathematics_1sl6haf"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "s = -2; the exact special-value identity zeta(-n) = (-1)^n B_(n+1) times 1/(n+1) gives zeta(-2) = B_3 times 1/3 = 0, while Re(-2) = -2, not 1/2."
REFUTATION_EXPLANATION = "The claim excludes every zeta zero whose real part is not 1/2. The exact Bernoulli-number computation gives B_3 = 0 and hence zeta(-2) = 0, so this zero lies on Re(s) = -2 and directly contradicts the claim."
SEARCH_SPACE = "All 12 negative integers s = -n for integers n from 1 through 12, swept in increasing n order; zeta(-n) is evaluated exactly using Bernoulli numbers B_0 through B_13 and fractions.Fraction."


def bernoulli_numbers(maximum_index):
    numbers = [Fraction(1, 1)]
    for m in range(1, maximum_index + 1):
        total = Fraction(0, 1)
        for k in range(m):
            total += comb(m + 1, k) * numbers[k]
        numbers.append(-total * Fraction(1, m + 1))
    return tuple(numbers)


def zeta_at_negative_integer(n, numbers):
    sign = -1 if n % 2 else 1
    return sign * numbers[n + 1] * Fraction(1, n + 1)


def main():
    candidates = tuple(range(1, 13))
    numbers = bernoulli_numbers(13)
    witnesses = []
    for n in candidates:
        s = -n
        zeta_value = zeta_at_negative_integer(n, numbers)
        if zeta_value == 0 and Fraction(s, 1) != Fraction(1, 2):
            witnesses.append(s)

    if -2 not in witnesses:
        raise AssertionError("the exact bounded sweep did not recover s = -2")

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
