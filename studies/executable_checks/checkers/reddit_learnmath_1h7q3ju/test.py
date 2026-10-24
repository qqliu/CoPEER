"""After setting δ = min{1, ε / K}, the proof claims δ·K = (ε/K)·K = ε, including when the minimum selects 1."""

import json
from fractions import Fraction
from itertools import product


RECORD_ID = "reddit_learnmath_1h7q3ju"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "ε = 2 and K = 1, so min{1, ε/K} selects 1 and δ = 1."
REFUTATION_EXPLANATION = (
    "For ε = 2 and K = 1, δ·K = 1·1 = 1, whereas "
    "(ε/K)·K = (2/1)·1 = 2 = ε. Thus δ·K is not ε "
    "when the minimum selects 1."
)
SEARCH_SPACE = (
    "All 16 ordered pairs (ε, K) of positive integers with 1 ≤ ε ≤ 4 "
    "and 1 ≤ K ≤ 4, iterated in lexicographic order with ε first."
)


def main():
    witnesses = []
    for epsilon, k_value in product(range(1, 5), range(1, 5)):
        quotient = Fraction(epsilon, k_value)
        delta = min(Fraction(1, 1), quotient)
        delta_times_k = delta * k_value
        quotient_times_k = quotient * k_value
        if delta == Fraction(1, 1) and delta_times_k != epsilon:
            witnesses.append(
                (epsilon, k_value, delta, delta_times_k, quotient_times_k)
            )

    first = witnesses[0]
    assert first == (
        2,
        1,
        Fraction(1, 1),
        Fraction(1, 1),
        Fraction(2, 1),
    )

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=False))


if __name__ == "__main__":
    main()
