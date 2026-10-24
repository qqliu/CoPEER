"""The proposed choice m=(1-3𝜀)/(9𝜀) supplies the natural number required by the sequence-limit definition for every 𝜀>0."""

import json
from fractions import Fraction


def is_natural(value):
    return value.denominator == 1 and value.numerator >= 0


def main():
    epsilon_space = (Fraction(1, 1),)
    witness = None

    for epsilon in epsilon_space:
        m = Fraction(1 - 3 * epsilon, 9 * epsilon)
        if epsilon > 0 and not is_natural(m):
            witness = (epsilon, m)
            break

    if witness != (Fraction(1, 1), Fraction(-2, 9)):
        raise AssertionError("Expected counterexample was not found")

    result = {
        "record_id": "reddit_learnmath_9a9ohb",
        "outcome": "WITNESS_FOUND",
        "witness_description": "ε=1 gives m=(1-3·1)/(9·1)=-2/9.",
        "refutation_explanation": "The value -2/9 is negative and not an integer, so it is not a natural number. Thus the proposed formula fails for the positive value ε=1, refuting the universal claim.",
        "search_space": "Exhaustively searched the explicitly bounded singleton space ε ∈ {1}, using exact rational arithmetic."
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
